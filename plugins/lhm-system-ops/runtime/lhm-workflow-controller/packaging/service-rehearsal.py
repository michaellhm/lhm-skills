#!/usr/bin/env python3
"""Root-only, watchers-disabled systemd rehearsal for the installed release."""
from __future__ import annotations

import hashlib
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/var/lib/lhm-workflow")
CLI = "/opt/lhm-workflow/current/venv/bin/lhm-workflow"
PATH_UNITS = (
    "lhm-workflow-bridge.path",
    "lhm-workflow-adapter.path", "lhm-workflow-stage.path",
    "lhm-workflow-verifier.path", "lhm-workflow-verification.path",
)
SERVICES = (
    "lhm-workflow-bridge.service",
    "lhm-workflow-adapter.service", "lhm-workflow-stage.service",
    "lhm-workflow-verifier.service", "lhm-workflow-verification.service",
)
FAULTS = {"wal_prepared", "receipt_sealed", "parent_applied", "wal_committed", "verifier_enqueued", "processed_marker", "source_cleanup"}


def run(*args: str, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, input=input_text, text=True, capture_output=True)
    if check and result.returncode:
        raise SystemExit(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stdout}{result.stderr}")
    return result


def controller(*args: str, payload: dict | None = None) -> dict:
    result = run("runuser", "-u", "lhmworkflow", "--", CLI, *args,
                 input_text=None if payload is None else json.dumps(payload))
    return json.loads(result.stdout)


def contract(parent: str, stage: str, index: int) -> dict:
    definitions = {
        "seo_evidence": ("claude", "lhm-marketing-hub:seo", "lhm-marketing-hub:seo-audit", ["google_search_console.property_read"], "none"),
        "content_production": ("claude", "lhm-marketing-hub:content", "lhm-marketing-hub:seo-content-writer", [], "none"),
        "site_implementation": ("codex", "codexworker", "lhm-wordpress-hub:astro-build", ["repo.branch_write", "preview.create"], "branch_only"),
        "verification": ("lhm_host_verifier", "lhmworkflowverify", "lhm-system:workflow-verification", ["artifact.read", "repo.read", "preview.read"], "none"),
    }
    runtime, identity, skill, capabilities, mutation = definitions[stage]
    child = f"{parent}-s{index}"
    return {
        "schema_version": 1, "parent_run_id": parent, "child_run_id": child,
        "workflow_id": "seo-content-astro-v1", "stage_id": stage,
        "idempotency_key": hashlib.sha256(f"{parent}:{stage}".encode()).hexdigest(),
        "worker": {"runtime": runtime, "identity": identity, "run_id": f"rehearsal-{child}"},
        "required_skills": [skill], "required_capabilities": capabilities,
        "expected_mutation_state": mutation,
    }


def assert_watchers_off() -> None:
    for unit in PATH_UNITS:
        enabled = run("systemctl", "is-enabled", unit, check=False).stdout.strip()
        active = run("systemctl", "is-active", unit, check=False).stdout.strip()
        if enabled not in {"disabled", "masked"} or active != "inactive":
            raise SystemExit(f"refusing rehearsal: watcher {unit} is {enabled}/{active}")


def assert_spools_empty() -> None:
    for name in ("bridge-incoming", "adapter-source", "adapter-incoming", "verifier-requests", "verifier-results"):
        if any((ROOT / name).glob("*.json")):
            raise SystemExit(f"refusing rehearsal: queued JSON exists in {ROOT / name}")


def start(unit: str) -> None:
    run("systemctl", "start", unit)
    state = run("systemctl", "is-failed", unit, check=False).stdout.strip()
    if state == "failed":
        run("journalctl", "-u", unit, "-n", "80", "--no-pager")
        raise SystemExit(f"{unit} failed")


def rehearse_crash(boundary: str) -> None:
    dropin = Path("/run/systemd/system/lhm-workflow-stage.service.d/90-rehearsal-fault.conf")
    dropin.parent.mkdir(parents=True, exist_ok=True)
    dropin.write_text(f"[Service]\nEnvironment=LHM_FAULT_INJECT=sigkill_after:{boundary}\n")
    try:
        run("systemctl", "daemon-reload")
        crashed = run("systemctl", "start", "lhm-workflow-stage.service", check=False)
        if crashed.returncode == 0:
            raise SystemExit(f"fault injection at {boundary} did not crash stage service")
    finally:
        dropin.unlink(missing_ok=True)
        try:
            dropin.parent.rmdir()
        except OSError:
            pass
        run("systemctl", "daemon-reload")
        run("systemctl", "reset-failed", "lhm-workflow-stage.service", check=False)
    start("lhm-workflow-recover.service")
    start("lhm-workflow-stage.service")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fault-boundary", choices=sorted(FAULTS))
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit("must run as root")
    assert_watchers_off()
    assert_spools_empty()
    parent = f"rehearsal-{int(time.time())}-{os.getpid()}"
    stage_names = ("seo_evidence", "content_production", "site_implementation", "verification")
    contracts = [contract(parent, name, index) for index, name in enumerate(stage_names)]
    controller("init-workflow", payload={
        "schema_version": 1, "parent_run_id": parent,
        "workflow_id": "seo-content-astro-v1", "stages": contracts,
    })
    for index, item in enumerate(contracts):
        runtime = item["worker"]["runtime"]
        uid = {"claude": 10002, "codex": 10001, "lhm_host_verifier": 10006}[runtime]
        artifact = ROOT / "worker" / f"{parent}-{item['stage_id']}.txt"
        artifact.write_text(f"systemd rehearsal evidence for {item['stage_id']}\n")
        os.chown(artifact, uid, 10004)
        os.chmod(artifact, 0o640)
        artifact_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        contract_name = f"{index}-{parent}.json"
        events_name = f"{index}-{parent}.jsonl"
        result_name = f"{index}-{parent}.json"
        contract_path = ROOT / "issued-contracts" / contract_name
        events_path = ROOT / "host-events" / events_name
        result_path = ROOT / "worker-results" / result_name
        contract_path.write_text(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n")
        contract_digest = hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        events = [{
            "source": "host-dispatcher", "seq": 1, "event": "dispatch_admitted",
            "child_run_id": item["child_run_id"], "contract_sha256": contract_digest,
            "worker": item["worker"],
        }]
        for skill in item["required_skills"]:
            events.append({"source": "host-dispatcher", "seq": len(events) + 1, "event": "skill_invoked", "child_run_id": item["child_run_id"], "contract_sha256": contract_digest, "skill": skill})
        for capability in item["required_capabilities"]:
            events.append({"source": "host-dispatcher", "seq": len(events) + 1, "event": "capability_observed", "child_run_id": item["child_run_id"], "contract_sha256": contract_digest, "capability": capability})
        events.append({"source": "host-dispatcher", "seq": len(events) + 1, "event": "terminal", "child_run_id": item["child_run_id"], "contract_sha256": contract_digest, "status": "completed"})
        events_path.write_text("".join(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n" for event in events))
        result_path.write_text(json.dumps({
            "child_run_id": item["child_run_id"], "status": "candidate",
            "evidence": [{"kind": "artifact", "path": str(artifact), "sha256": artifact_digest}],
            "checks": ["artifact_hash"],
            "mutation_audit": {"mutation_state": item["expected_mutation_state"]},
        }, sort_keys=True, separators=(",", ":")) + "\n")
        for trusted in (contract_path, events_path):
            os.chown(trusted, 0, 0)
            os.chmod(trusted, 0o600)
        os.chown(result_path, uid, 10004)
        os.chmod(result_path, 0o640)
        manifest = ROOT / "bridge-incoming" / f"{index}-{parent}.json"
        manifest.write_text(json.dumps({"contract": contract_name, "host_events": events_name, "worker_result": result_name}, sort_keys=True, separators=(",", ":")) + "\n")
        os.chown(manifest, 0, 0)
        os.chmod(manifest, 0o600)
        for service in SERVICES:
            if index == 0 and service == "lhm-workflow-stage.service" and args.fault_boundary:
                rehearse_crash(args.fault_boundary)
            else:
                start(service)
        state = controller("status", parent)
        expected = ["accepted"] * (index + 1) + ["issued"] * (1 if index < 3 else 0) + ["pending"] * max(0, 2 - index)
        if [stage["status"] for stage in state["stages"]] != expected:
            raise SystemExit(f"unexpected stage state after {item['stage_id']}: {state}")
    final = controller("status", parent)
    if final["state"] != "review_ready":
        raise SystemExit(f"workflow did not become review_ready: {final}")
    print(json.dumps({"status": "ok", "parent_run_id": parent, "state": final["state"]}, sort_keys=True))


if __name__ == "__main__":
    main()
