"""Reusable, fail-closed ingress for thin Hermes scheduled-work triggers."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

from .org_routing import intake as seo_intake

DEFAULT_REGISTRY = Path("/etc/lhm-workflow/scheduled-workflows.json")
DEFAULT_OUTBOX = Path("/var/lib/lhm-workflow/scheduled-intake")
SAFE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _trusted_file(path: Path, *, test_mode: bool) -> bytes:
    stat = os.stat(path, follow_symlinks=False)
    if path.is_symlink() or not path.is_file():
        raise ValueError("scheduled-work registry must be a regular file")
    if not test_mode and (stat.st_uid != 0 or stat.st_mode & 0o022):
        raise ValueError("scheduled-work registry ownership or mode is unsafe")
    return path.read_bytes()


def load_definition(path: Path, workflow_key: str, *, test_mode: bool = False) -> dict:
    if not SAFE.fullmatch(workflow_key):
        raise ValueError("invalid scheduled workflow key")
    value = json.loads(_trusted_file(path, test_mode=test_mode))
    if set(value) != {"schema_version", "workflows"} or value["schema_version"] != 1:
        raise ValueError("invalid scheduled-work registry")
    definition = value["workflows"].get(workflow_key)
    required = {
        "source_cron_id", "job_name", "handler", "department", "client_id",
        "permission_ceiling", "reviewer", "delivery", "destinations", "completion_test",
        "profile_aliases", "canonical_sources", "gsc", "work_control",
    }
    if not isinstance(definition, dict) or set(definition) != required:
        raise ValueError("unknown or invalid scheduled workflow")
    for key in ("department", "client_id", "reviewer"):
        if not SAFE.fullmatch(str(definition[key])):
            raise ValueError(f"invalid scheduled workflow {key}")
    if definition["handler"] != "seo-org-v1" or definition["delivery"] != "none":
        raise ValueError("unsupported scheduled workflow handler or delivery")
    if not isinstance(definition["destinations"], dict) or not definition["destinations"]:
        raise ValueError("scheduled workflow requires authoritative destinations")
    if not isinstance(definition["completion_test"], str) or not definition["completion_test"].strip():
        raise ValueError("scheduled workflow requires a completion test")
    aliases = definition["profile_aliases"]
    required_aliases = {"lhm_chief_of_staff", "lhm_head_of_production", "lhm_seo_lead", "lhm_researcher", "lhm_content", "lhm_website", "lhm_verifier", "lhm_learning_steward"}
    if not isinstance(aliases, dict) or set(aliases) != required_aliases or any(not str(value).startswith("/home/hermes/.hermes/.local/bin/") for value in aliases.values()):
        raise ValueError("invalid Hermes profile alias registry")
    sources = definition["canonical_sources"]
    if not isinstance(sources, list) or len(sources) != 4 or any(not str(value).startswith("/home/hermes/.hermes/profiles/lhm_brain/vault/") for value in sources):
        raise ValueError("invalid canonical source registry")
    gsc = definition["gsc"]
    if set(gsc) != {"property", "route", "allowed_actions", "evidence_path", "evidence_sha256"} or gsc["property"] != "https://localhealthmarketing.com/" or gsc["route"] != "seo_gsc_readonly":
        raise ValueError("invalid registered GSC property")
    if set(gsc["allowed_actions"]) != {"list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"}:
        raise ValueError("invalid GSC permission ceiling")
    work_control = definition["work_control"]
    if set(work_control) != {"path", "sha256", "return_role", "return_point"} or work_control["return_role"] != "head_of_production":
        raise ValueError("invalid work-control registry")
    return definition


def normalise_urls(site: str, urls: list[str]) -> list[str]:
    parsed = urlparse(site)
    if parsed.scheme != "https" or not parsed.netloc or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("invalid registered site URL")
    root = f"{parsed.scheme}://{parsed.netloc}/"
    result = []
    for value in urls:
        if not isinstance(value, str) or not value.strip() or "," in value:
            raise ValueError("invalid scheduled URL")
        absolute = urljoin(root, value.strip())
        observed = urlparse(absolute)
        if observed.scheme != "https" or observed.netloc != parsed.netloc or observed.params or observed.query or observed.fragment:
            raise ValueError("URL is outside the registered site")
        if absolute not in result:
            result.append(absolute)
    return result


def create_parent(definition: dict, event: dict, parent_run_id: str) -> dict:
    if event.get("source_cron_id") != definition["source_cron_id"] or event.get("job_name") != definition["job_name"]:
        raise ValueError("cron event does not match registered workflow")
    parent = seo_intake(event, parent_run_id)
    contract = {
        "schema_version": 1,
        "source_cron_id": definition["source_cron_id"],
        "department": definition["department"],
        "client_id": definition["client_id"],
        "permission_ceiling": definition["permission_ceiling"],
        "reviewer": definition["reviewer"],
        "destinations": definition["destinations"],
        "completion_test": definition["completion_test"],
        "profile_aliases": definition["profile_aliases"],
        "canonical_sources": definition["canonical_sources"],
        "gsc": definition["gsc"],
        "work_control": definition["work_control"],
    }
    parent["scheduled_contract"] = contract
    parent["scheduled_contract_sha256"] = _digest(contract)
    parent["stage_order"] = ["chief_intake", "context", "context_verify", "research", "research_verify", "production_plan", "seo_plan", "seo_plan_verify", "seo_accept"]
    return parent


def persist_parent(outbox: Path, parent: dict, *, test_mode: bool = False) -> dict:
    if not test_mode and outbox != DEFAULT_OUTBOX:
        raise ValueError("scheduled-work outbox override requires test mode")
    outbox.mkdir(parents=True, exist_ok=True, mode=0o750)
    target = outbox / f"{parent['parent_run_id']}.json"
    if target.exists():
        observed = json.loads(target.read_text())
        if observed != parent:
            raise ValueError("conflicting scheduled parent replay")
        return {"status": "accepted", "replayed": True, "parent_run_id": parent["parent_run_id"], "parent_sha256": _digest(parent)}
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=outbox)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(_canonical(parent) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    if json.loads(target.read_text()) != parent:
        raise ValueError("scheduled parent readback mismatch")
    return {"status": "accepted", "replayed": False, "parent_run_id": parent["parent_run_id"], "parent_sha256": _digest(parent)}


def business_status(parent: dict) -> dict:
    state = parent.get("state")
    if state == "closed":
        return {"run_result": "succeeded", "work_state": "completed"}
    if state in {"incident", "needs_repair"}:
        return {"run_result": "failed", "work_state": "waiting_on_capability"}
    if state == "needs_consequential_approval":
        return {"run_result": "blocked", "work_state": "waiting_on_approval"}
    if state in {"ready", "running"}:
        return {"run_result": "accepted", "work_state": "running"}
    raise ValueError("unknown scheduled parent state")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow_key")
    parser.add_argument("event", type=Path)
    parser.add_argument("parent_run_id")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX)
    args = parser.parse_args(argv)
    test_mode = os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1"
    definition = load_definition(args.registry, args.workflow_key, test_mode=test_mode)
    event = json.loads(_trusted_file(args.event, test_mode=test_mode))
    parent = create_parent(definition, event, args.parent_run_id)
    receipt = persist_parent(args.outbox, parent, test_mode=test_mode)
    print(json.dumps({**receipt, **business_status(parent)}, sort_keys=True))


if __name__ == "__main__":
    main()
