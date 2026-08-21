#!/usr/bin/env python3
"""Create, validate, and render Hermes client capability preflight records."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAPABILITIES = (
    "google_search_console",
    "google_analytics",
    "google_ads",
    "website",
    "google_drive",
    "basicops",
    "knowledge",
)
STATUSES = {"unconfigured", "configured", "verified", "failed", "blocked", "not_applicable"}
SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SECRET_KEY = re.compile(r"(?:password|secret|token|api[_-]?key|private[_-]?key|cookie)", re.I)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def template(client_id: str, client_name: str) -> dict[str, Any]:
    if not SAFE_ID.fullmatch(client_id):
        raise ValueError("client_id must be lowercase letters, numbers, and single hyphens")
    return {
        "schema_version": 1,
        "client": {"id": client_id, "name": client_name, "type": "client"},
        "onboarding": {
            "status": "incomplete",
            "owner": "lhm_client_onboarding",
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        "capabilities": {
            name: {
                "required": False,
                "status": "unconfigured",
                "route": None,
                "identifiers": {},
                "allowed_operations": [],
                "owner": None,
                "last_test": None,
            }
            for name in CAPABILITIES
        },
    }


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("root JSON value must be an object")
    return value


def find_secret_keys(value: Any, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{prefix}.{key}"
            if SECRET_KEY.search(str(key)):
                found.append(location)
            found.extend(find_secret_keys(child, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_secret_keys(child, f"{prefix}[{index}]"))
    return found


def validate(record: dict[str, Any], required: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    blockers: list[str] = []
    client = record.get("client")
    if not isinstance(client, dict) or not SAFE_ID.fullmatch(str(client.get("id", ""))):
        errors.append("client.id is missing or unsafe")
    secret_keys = find_secret_keys(record)
    if secret_keys:
        errors.append("secret-like fields are forbidden: " + ", ".join(secret_keys))
    capabilities = record.get("capabilities")
    if not isinstance(capabilities, dict):
        return errors + ["capabilities must be an object"], blockers
    unknown_required = sorted(set(required) - set(CAPABILITIES))
    if unknown_required:
        errors.append("unknown required capabilities: " + ", ".join(unknown_required))
    effective_required = set(required)
    for name, capability in capabilities.items():
        if name not in CAPABILITIES:
            errors.append(f"unknown capability: {name}")
            continue
        if not isinstance(capability, dict):
            errors.append(f"{name} must be an object")
            continue
        status = capability.get("status")
        if status not in STATUSES:
            errors.append(f"{name}.status is invalid")
        if capability.get("required") is True:
            effective_required.add(name)
        if status == "verified":
            test = capability.get("last_test")
            if not capability.get("route"):
                errors.append(f"{name} verified without route")
            if not capability.get("identifiers"):
                errors.append(f"{name} verified without identifiers")
            if not capability.get("allowed_operations"):
                errors.append(f"{name} verified without allowed_operations")
            if not isinstance(test, dict) or test.get("result") != "passed" or not test.get("evidence_ref"):
                errors.append(f"{name} verified without passing evidence")
            elif not SHA256.fullmatch(str(test.get("evidence_sha256", ""))):
                errors.append(f"{name} verified without evidence_sha256")
            if name == "google_search_console" and isinstance(test, dict):
                expected_binding = {
                    "client_id": client.get("id") if isinstance(client, dict) else None,
                    "property": capability.get("identifiers", {}).get("property"),
                    "capability": "google_search_console.property_read",
                    "allowed_operations": capability.get("allowed_operations"),
                }
                if test.get("binding") != expected_binding:
                    errors.append("google_search_console verified without exact evidence binding")
    for name in sorted(effective_required):
        capability = capabilities.get(name)
        if not isinstance(capability, dict) or capability.get("status") != "verified":
            blockers.append(f"{name} is missing or not verified")
    return errors, blockers


def render(record: dict[str, Any]) -> str:
    client = record["client"]
    rows = []
    for name in CAPABILITIES:
        cap = record["capabilities"].get(name, {})
        test = cap.get("last_test") or {}
        rows.append(
            f"| `{name}` | {'yes' if cap.get('required') else 'no'} | "
            f"{cap.get('status', 'missing')} | {cap.get('route') or '—'} | {test.get('at') or '—'} |"
        )
    table = "\n".join([
        "| Capability | Required | Status | Route | Last tested |",
        "|---|---:|---|---|---|",
        *rows,
    ])
    return (
        f"# {client['name']} — Hermes onboarding\n\n"
        "Canonical machine record: `capabilities.json`\n\n"
        "## Readiness\n\n"
        f"{table}\n\n"
        "## Rule\n\n"
        "Hermes must stop with `client_onboarding_required` when a workflow needs a capability "
        "that is missing or not verified. Credentials are never stored in this folder.\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("path", type=Path)
    init_parser.add_argument("--client-id", required=True)
    init_parser.add_argument("--client-name", required=True)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("path", type=Path)
    check_parser.add_argument("--require", action="append", default=[])
    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("path", type=Path)
    render_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            if args.path.exists():
                raise ValueError(f"refusing to overwrite {args.path}")
            atomic_write(args.path, json.dumps(template(args.client_id, args.client_name), indent=2) + "\n")
            return 0
        record = load(args.path)
        errors, blockers = validate(record, getattr(args, "require", []))
        if errors:
            print(json.dumps({"status": "invalid", "errors": errors}, indent=2))
            return 1
        if args.command == "check":
            if blockers:
                print(json.dumps({"status": "client_onboarding_required", "blockers": blockers}, indent=2))
                return 2
            print(json.dumps({"status": "ready", "client_id": record["client"]["id"]}, indent=2))
            return 0
        atomic_write(args.output, render(record))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
