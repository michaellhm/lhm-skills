#!/usr/bin/env python3
"""Apply an explicitly approved, hash-bound meeting bundle to the registered vault root."""

import fcntl
import hashlib
import json
import os
import re
import secrets
import shutil
from pathlib import Path

BASE = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch")
INCOMING = BASE / "vault-apply-incoming"
PROCESSED = BASE / "vault-apply-processed"
FAILED = BASE / "vault-apply-failed"
RUNS = BASE / "meeting-runs"
REGISTRY = Path("/etc/lhm-codex/clients")
VAULT = Path("/home/hermes/.hermes/profiles/lhm_brain/vault")
LOCK = BASE / "vault-apply.lock"
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
HASH = re.compile(r"^[0-9a-f]{64}$")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_json(path, payload, mode=0o640):
    temp = path.with_name(f".{path.name}.{secrets.token_hex(4)}")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.chmod(temp, mode)
    os.replace(temp, path)


def fail(path, approval_id, reason):
    FAILED.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.move(path, FAILED / path.name)
    atomic_json(FAILED / f"{approval_id}.result.json", {
        "approval_id": approval_id, "status": "failed", "reason": str(reason)[:1000]
    })


def verified_bundle(data):
    expected = {"schema_version", "approval_id", "source_run_id", "content_hash", "operation", "approved_by", "approval_text"}
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError("approval request does not match closed schema")
    approval_id, run_id = data["approval_id"], data["source_run_id"]
    if not SAFE_ID.fullmatch(approval_id) or not SAFE_ID.fullmatch(run_id):
        raise ValueError("invalid approval or run ID")
    if data["schema_version"] != 1 or data["operation"] != "apply_vault":
        raise ValueError("unsupported approval operation")
    if data["approved_by"] != "Michael":
        raise ValueError("Michael approval is required")
    approval = data["approval_text"]
    if not isinstance(approval, str) or "approve" not in approval.lower() or "vault" not in approval.lower() or len(approval) > 1000:
        raise ValueError("explicit vault approval text is required")
    content_hash = data["content_hash"]
    if not isinstance(content_hash, str) or not HASH.fullmatch(content_hash):
        raise ValueError("invalid content hash")
    final_path = RUNS / run_id / "final.json"
    request_path = RUNS / run_id / "request.json"
    if not final_path.is_file() or not request_path.is_file():
        raise ValueError("source meeting run is unavailable")
    final = json.loads(final_path.read_text(encoding="utf-8"))
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if final.get("status") != "needs_review" or final.get("content_hash") != content_hash:
        raise ValueError("source run status or content hash mismatch")
    result = final.get("result")
    canonical = json.dumps({k: result[k] for k in ("email_draft", "meeting_record", "proposed_mutations")}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if digest(canonical) != content_hash:
        raise ValueError("review bundle content no longer matches its hash")
    return approval_id, run_id, content_hash, request, result


def apply(path):
    approval_id = path.stem
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        approval_id, run_id, content_hash, request, result = verified_bundle(data)
        profile_path = REGISTRY / f"{request['client_id']}.json"
        if not profile_path.is_file() or profile_path.is_symlink():
            raise ValueError("registered client profile is unavailable")
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        root = (VAULT / profile["vault_relative_root"]).resolve()
        if VAULT.resolve() not in root.parents or not root.is_dir() or root.is_symlink():
            raise ValueError("invalid registered client root")
        mutations = result["proposed_mutations"]
        if not isinstance(mutations, list) or not mutations:
            raise ValueError("no proposed vault mutations")
        plans = []
        for item in mutations:
            relative = Path(item["path"])
            target = (VAULT / relative).resolve()
            if root != target and root not in target.parents:
                raise ValueError("mutation escaped the registered client root")
            if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent != VAULT.parent):
                raise ValueError("symlinked vault target is not allowed")
            operation, expected = item["operation"], item["expected_sha256"]
            if operation == "create":
                if expected is not None or target.exists():
                    raise ValueError(f"create precondition failed: {relative}")
                meeting_parent = root / "project-management" / "meetings"
                if target.parent != meeting_parent:
                    raise ValueError("new meeting files are allowed only in the registered meetings directory")
            elif operation == "replace":
                if not target.is_file() or not isinstance(expected, str) or digest(target.read_text(encoding="utf-8")) != expected:
                    raise ValueError(f"replace version check failed: {relative}")
            else:
                raise ValueError("unsupported mutation operation")
            plans.append((target, item["content"], operation))
        with LOCK.open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            staged = []
            for target, content, operation in plans:
                target.parent.mkdir(parents=True, exist_ok=True)
                temp = target.with_name(f".{target.name}.{approval_id}.{secrets.token_hex(3)}")
                temp.write_text(content, encoding="utf-8")
                os.chmod(temp, 0o640)
                staged.append((temp, target, operation))
            for temp, target, _ in staged:
                os.replace(temp, target)
        receipt = {"approval_id": approval_id, "source_run_id": run_id, "content_hash": content_hash,
                   "status": "vault_applied", "files": [str(target.relative_to(VAULT)) for target, _, _ in plans]}
        atomic_json(PROCESSED / f"{approval_id}.result.json", receipt)
        shutil.move(path, PROCESSED / path.name)
    except Exception as exc:
        fail(path, approval_id, exc)


def main():
    for directory in (INCOMING, PROCESSED, FAILED):
        if not directory.exists():
            raise SystemExit(f"missing vault apply directory: {directory}")
    for path in sorted(INCOMING.glob("*.json")):
        apply(path)


if __name__ == "__main__":
    main()
