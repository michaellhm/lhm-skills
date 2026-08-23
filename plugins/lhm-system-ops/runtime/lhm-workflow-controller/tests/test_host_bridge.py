from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from lhm_workflow.host_bridge import BridgeRoots, build_receipt, digest, process_manifest


def write(path: Path, value, *, jsonl=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if jsonl:
        path.write_text("\n".join(json.dumps(item) for item in value) + "\n")
    else:
        path.write_text(json.dumps(value))
    path.chmod(0o600)
    return path


def fixture(tmp_path: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    roots = BridgeRoots(*(tmp_path / name for name in ("contracts", "host-events", "worker-results", "adapter-source", "processed", "quarantine")))
    contract = {
        "parent_run_id": "p1", "child_run_id": "c1", "workflow_id": "seo-content-astro-v1",
        "stage_id": "seo_evidence", "idempotency_key": "a" * 64,
        "worker": {"runtime": "claude", "identity": "lhm-marketing-hub:seo", "run_id": "r1"},
        "required_skills": ["lhm-marketing-hub:seo-audit"],
        "required_capabilities": ["google_search_console.property_read"], "expected_mutation_state": "none",
    }
    binding = digest(contract)
    events = [
        {"source": "host-dispatcher", "seq": 1, "event": "dispatch_admitted", "child_run_id": "c1", "contract_sha256": binding, "worker": contract["worker"]},
        {"source": "host-dispatcher", "seq": 2, "event": "skill_invoked", "child_run_id": "c1", "contract_sha256": binding, "skill": contract["required_skills"][0]},
        {"source": "host-dispatcher", "seq": 3, "event": "capability_observed", "child_run_id": "c1", "contract_sha256": binding, "capability": contract["required_capabilities"][0]},
        {"source": "host-dispatcher", "seq": 4, "event": "terminal", "child_run_id": "c1", "contract_sha256": binding, "status": "completed"},
    ]
    artifact = tmp_path / "artifact.md"; artifact.write_text("evidence\n"); artifact.chmod(0o600)
    result = {"child_run_id": "c1", "status": "candidate", "evidence": [{"kind": "artifact", "path": str(artifact), "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}], "checks": ["artifact_hash"], "mutation_audit": {"mutation_state": "none"}}
    write(roots.contracts / "c1.json", contract)
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    write(roots.worker_results / "c1.json", result)
    manifest = write(tmp_path / "incoming" / "c1.json", {"contract": "c1.json", "host_events": "c1.jsonl", "worker_result": "c1.json"})
    return roots, contract, events, result, manifest


def test_bridge_builds_root_derived_receipt_and_is_idempotent(tmp_path):
    roots, contract, events, result, manifest = fixture(tmp_path)
    output = process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}, adapter_gid=os.getgid())
    receipt = json.loads(output.read_text())
    assert receipt["host_provenance"]["observed_skill_calls"] == contract["required_skills"]
    assert receipt["bridge_input_sha256"]
    replay = write(tmp_path / "incoming" / "replay.json", {"contract": "c1.json", "host_events": "c1.jsonl", "worker_result": "c1.json"})
    assert process_manifest(replay, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}, adapter_gid=os.getgid()) == output
    assert output.stat().st_mode & 0o777 == 0o640
    assert output.stat().st_gid == os.getgid()
    assert not list(roots.quarantine.glob("*.json"))


def test_worker_cannot_claim_skill_in_result(tmp_path):
    roots, contract, events, result, manifest = fixture(tmp_path)
    events.pop(1)
    for seq, event in enumerate(events, 1): event["seq"] = seq
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    result["observed_skill_calls"] = contract["required_skills"]
    write(roots.worker_results / "c1.json", result)
    assert process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}) is None
    assert "incomplete" in (roots.quarantine / "c1.json.reason").read_text()


def test_symlink_and_path_escape_are_quarantined(tmp_path):
    roots, _, _, _, manifest = fixture(tmp_path)
    target = roots.contracts / "c1.json"
    real = roots.contracts / "real.json"; target.rename(real); target.symlink_to(real)
    assert process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}) is None
    roots, _, _, _, manifest = fixture(tmp_path / "second")
    write(manifest, {"contract": "../outside.json", "host_events": "c1.jsonl", "worker_result": "c1.json"})
    assert process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}) is None


def test_partial_or_conflicting_replay_quarantined(tmp_path):
    roots, _, _, _, manifest = fixture(tmp_path)
    (roots.host_events / "c1.jsonl").write_text('{"source":"host-dispatcher"')
    assert process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}) is None
    roots, _, _, _, manifest = fixture(tmp_path / "second")
    output = process_manifest(manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()})
    output.write_text("{}\n"); output.chmod(0o600)
    replay = write(tmp_path / "second" / "incoming" / "replay.json", {"contract": "c1.json", "host_events": "c1.jsonl", "worker_result": "c1.json"})
    assert process_manifest(replay, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}) is None


def test_parent_stage_and_idempotency_are_derived_only_from_issued_contract(tmp_path):
    """A worker may echo bindings, but cannot replace the root-issued values."""
    roots, contract, _, result, manifest = fixture(tmp_path)
    result.update({
        "parent_run_id": "attacker-parent",
        "workflow_id": "attacker-workflow",
        "stage_id": "verification",
        "idempotency_key": "b" * 64,
        "worker": {"runtime": "codex", "identity": "attacker", "run_id": "evil"},
    })
    write(roots.worker_results / "c1.json", result)
    output = process_manifest(
        manifest, roots, root_uid=os.getuid(),
        worker_uids={"claude": os.getuid(), "codex": os.getuid()},
    )
    receipt = json.loads(output.read_text())
    for field in ("parent_run_id", "workflow_id", "stage_id", "idempotency_key", "worker"):
        assert receipt[field] == contract[field]


def test_cross_child_event_stream_cannot_be_substituted(tmp_path):
    roots, contract, events, _, manifest = fixture(tmp_path)
    events[1]["child_run_id"] = "c2"
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    assert process_manifest(
        manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}
    ) is None
    assert "binding" in (roots.quarantine / "c1.json.reason").read_text()


@pytest.mark.parametrize("mutation", [
    lambda contract, result: contract.update(worker="claude"),
    lambda contract, result: contract.update(required_capabilities=None),
    lambda contract, result: contract.update(required_skills={"skill": "seo"}),
    lambda contract, result: result.update(checks=[{"forged": True}]),
    lambda contract, result: result.update(evidence="not-a-list"),
])
def test_malformed_protected_inputs_are_quarantined_not_crash(tmp_path, mutation):
    roots, contract, events, result, manifest = fixture(tmp_path)
    mutation(contract, result)
    binding = digest(contract)
    for event in events:
        event["contract_sha256"] = binding
        if event["event"] == "dispatch_admitted":
            event["worker"] = contract["worker"]
    write(roots.contracts / "c1.json", contract)
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    write(roots.worker_results / "c1.json", result)
    assert process_manifest(
        manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}
    ) is None
    assert (roots.quarantine / "c1.json.reason").is_file()


def test_terminal_must_follow_all_observations_and_replay_cannot_extend_stream(tmp_path):
    roots, _, events, _, manifest = fixture(tmp_path)
    events[2], events[3] = events[3], events[2]
    for seq, event in enumerate(events, 1):
        event["seq"] = seq
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    assert process_manifest(
        manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}
    ) is None
    assert "terminal" in (roots.quarantine / "c1.json.reason").read_text()


def test_capability_must_be_observed_even_if_worker_claims_it(tmp_path):
    roots, contract, events, result, manifest = fixture(tmp_path)
    events.pop(2)
    for seq, event in enumerate(events, 1):
        event["seq"] = seq
    result["observed_capabilities"] = contract["required_capabilities"]
    write(roots.host_events / "c1.jsonl", events, jsonl=True)
    write(roots.worker_results / "c1.json", result)
    assert process_manifest(
        manifest, roots, root_uid=os.getuid(), worker_uids={"claude": os.getuid()}
    ) is None
    assert "incomplete" in (roots.quarantine / "c1.json.reason").read_text()
