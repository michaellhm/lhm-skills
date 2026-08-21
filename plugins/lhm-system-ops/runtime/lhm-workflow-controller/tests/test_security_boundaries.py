from __future__ import annotations

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from adversarial_helpers import (
    Controller, canonical_digest, contract, file_digest, initialise,
    stage_receipt, verifier_receipt, write_json, write_sealed_json,
)


@pytest.fixture
def ctl(tmp_path: Path) -> Controller:
    return Controller.from_environment(tmp_path / "state")


@pytest.fixture
def issued(ctl: Controller, tmp_path: Path):
    c = contract()
    initialise(ctl, c)
    artifact = tmp_path / "worker" / "content.md"
    artifact.parent.mkdir(); artifact.write_text("bounded content\n")
    artifact.chmod(0o600)
    return c, artifact


def assert_not_advanced(ctl: Controller):
    state = ctl.state()
    assert state["state"] != "review_ready"
    assert state["stages"][0]["status"] != "accepted"


def test_worker_cannot_forge_verifier_receipt(ctl, issued, tmp_path):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    accepted = ctl.ingest_stage(event)
    forged = verifier_receipt(c, canonical_digest(event))
    worker_file = write_json(tmp_path / "worker" / "forged-verifier.json", forged)
    ctl.run("ingest-verification", str(worker_file), ok=False)
    assert_not_advanced(ctl)


def test_worker_cannot_forge_host_provenance(ctl, issued):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    event["host_provenance"]["observer"] = "worker"
    unsealed = write_json(ctl.root.parent / "worker" / "forged-stage.json", event)
    ctl.run("ingest-stage", str(unsealed), ok=False)
    assert_not_advanced(ctl)


def test_worker_text_cannot_impersonate_host_dispatcher(ctl, issued):
    """The word host-dispatcher in worker JSON is not authentication."""
    c, artifact = issued
    forged = stage_receipt(c, artifact)
    forged["host_provenance"]["observer"] = "host-dispatcher"
    forged["host_provenance"]["attested_by_service"] = False
    unsealed = write_json(ctl.root.parent / "worker" / "host-lookalike.json", forged)
    ctl.run("ingest-stage", str(unsealed), ok=False)
    assert_not_advanced(ctl)


def test_missing_observed_skill_rejected(ctl, issued):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    event["host_provenance"]["observed_skill_calls"] = []
    ctl.assert_stage_rejected(event, "missing-skill.json")
    assert_not_advanced(ctl)


def test_wrong_worker_rejected(ctl, issued):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    event["worker"]["identity"] = "lhm-marketing-hub:seo"
    ctl.assert_stage_rejected(event, "wrong-worker.json")
    assert_not_advanced(ctl)


def test_hash_tamper_rejected(ctl, issued):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    artifact.write_text("tampered after receipt\n")
    ctl.assert_stage_rejected(event, "hash-tamper.json")
    assert_not_advanced(ctl)


@pytest.mark.parametrize("mode", [0o622, 0o666, 0o777])
def test_group_or_world_writable_evidence_rejected(ctl, issued, mode):
    c, artifact = issued
    artifact.chmod(mode)
    ctl.assert_stage_rejected(stage_receipt(c, artifact), f"unsafe-mode-{mode:o}.json")
    assert_not_advanced(ctl)


@pytest.mark.skipif(os.geteuid() != 0, reason="ownership boundary requires Linux root staging")
def test_wrong_uid_evidence_rejected(ctl, issued):
    c, artifact = issued
    os.chown(artifact, 65534, 65534)
    ctl.assert_stage_rejected(stage_receipt(c, artifact), "wrong-uid.json")
    assert_not_advanced(ctl)


def test_symlink_and_path_escape_rejected(ctl, issued, tmp_path):
    c, artifact = issued
    link = tmp_path / "worker" / "link.md"
    link.symlink_to(artifact)
    ctl.assert_stage_rejected(stage_receipt(c, link), "symlink.json")
    escaped = tmp_path / "outside.md"; escaped.write_text("outside")
    ctl.assert_stage_rejected(stage_receipt(c, escaped), "escape.json")
    assert_not_advanced(ctl)


@pytest.mark.parametrize("mode", [0o620, 0o660, 0o606, 0o666])
def test_adapter_rejects_group_or_world_writable_source_record(ctl, issued, mode):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    source = write_json(ctl.root.parent / "adapter-source" / f"source-{mode:o}.json", event, mode)
    output = ctl.root.parent / "adapter" / f"source-{mode:o}.json"
    proc = subprocess.run(
        [os.environ.get("LHM_WORKFLOW_PYTHON", "/tmp/lhm-workflow-pytest/bin/python"),
         "-m", "lhm_workflow.adapter", str(source), str(output), "--key",
         str(ctl.root / "secrets" / "adapter.key"), "--artifact-root",
         str(ctl.root.parent / "adapter" / "artifacts")],
        text=True, capture_output=True, env=ctl.env,
    )
    assert proc.returncode != 0
    assert not output.exists()
    assert_not_advanced(ctl)


@pytest.mark.parametrize("field", ["checks", "evidence_ids"])
def test_empty_verifier_assurance_rejected(ctl, issued, tmp_path, field):
    c, artifact = issued
    event = stage_receipt(c, artifact)
    accepted = ctl.ingest_stage(event)
    receipt = verifier_receipt(c, accepted["stage_event_sha256"])
    receipt[field] = []
    trusted = write_sealed_json(
        tmp_path / "verifier" / "final.json", receipt,
        ctl.root / "secrets" / "verifier.key", "verifier_attestation",
    )
    ctl.run("ingest-verification", str(trusted), ok=False)
    assert_not_advanced(ctl)


def test_same_uid_file_in_verifier_directory_is_not_authenticity(ctl, issued):
    """Path, UID and mode alone cannot distinguish a forged verifier result."""
    c, artifact = issued
    accepted = ctl.ingest_stage(stage_receipt(c, artifact))
    forged = verifier_receipt(c, accepted["stage_event_sha256"])
    forged["verifier_identity"] = "lhmworkflowverify"
    verifier_root = ctl.root.parent / "verifier"
    forged_path = write_json(verifier_root / "forged-by-controller-caller.json", forged, 0o600)
    ctl.run("ingest-verification", str(forged_path), ok=False)
    assert_not_advanced(ctl)


def test_root_override_requires_explicit_test_mode(tmp_path):
    configured = os.environ.get("LHM_WORKFLOW_CLI")
    assert configured, "LHM_WORKFLOW_CLI must name installed CLI"
    env = dict(os.environ)
    env["LHM_WORKFLOW_ROOT"] = str(tmp_path / "attacker-selected-root")
    env.pop("LHM_WORKFLOW_TEST_MODE", None)
    proc = subprocess.run(
        [configured, "init-parent"], input=json.dumps(contract()), text=True,
        capture_output=True, env=env,
    )
    assert proc.returncode != 0, "environment root override silently enabled test trust rules"


def test_duplicate_delivery_is_exact_once(ctl, issued):
    c, artifact = issued; event = stage_receipt(c, artifact)
    sealed = ctl.adapter_record(event, "duplicate.json")
    first = ctl.json("ingest-stage", str(sealed))
    second = ctl.json("ingest-stage", str(sealed))
    assert second["event_id"] == first["event_id"]
    assert second["stage_event_sha256"] == first["stage_event_sha256"]
    assert ctl.state()["event_counts"][event["event_id"]] == 1


def test_concurrent_duplicate_events_are_exact_once(ctl, issued):
    c, artifact = issued; event = stage_receipt(c, artifact)
    sealed = ctl.adapter_record(event, "concurrent.json")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: ctl.run("ingest-stage", str(sealed)), range(16)))
    assert all(p.returncode == 0 for p in results)
    assert ctl.state()["event_counts"][event["event_id"]] == 1


@pytest.mark.parametrize("boundary", [
    "wal_prepared", "receipt_sealed", "parent_applied", "verifier_enqueued",
    "processed_marker", "wal_committed", "source_cleanup",
])
def test_sigkill_recovery_at_every_durable_boundary(ctl, issued, boundary):
    c, artifact = issued; event = stage_receipt(c, artifact)
    sealed = ctl.adapter_record(event, f"fault-{boundary}.json")
    proc = ctl.run(
        "ingest-stage", str(sealed), ok=False,
        extra_env={"LHM_FAULT_INJECT": f"sigkill_after:{boundary}"},
    )
    assert proc.returncode < 0, f"fault hook must deliver SIGKILL at {boundary}"
    ctl.run("recover")
    state = ctl.state()
    assert state["event_counts"].get(event["event_id"], 0) == 1
    assert state["stages"][0]["status"] == "verifying"
    assert state["pending_verifications"] == [f"verify:{c['child_run_id']}"]
    ctl.run("recover")
    assert ctl.state() == state


def test_verifier_receipt_bound_to_exact_stage_hash(ctl, issued, tmp_path):
    c, artifact = issued; event = stage_receipt(c, artifact)
    accepted = ctl.ingest_stage(event)
    receipt = verifier_receipt(c, "0" * 64)
    trusted = write_json(tmp_path / "verifier" / "wrong-hash.json", receipt)
    ctl.run("ingest-verification", str(trusted), ok=False)
    assert accepted["stage_event_sha256"] != receipt["stage_event_sha256"]
    assert_not_advanced(ctl)


def test_full_workflow_does_not_finish_after_first_stage(ctl):
    """Review-ready requires SEO, content, site and independent verification."""
    stages = [
        contract("seo_evidence"),
        contract("content_production"),
        contract("site_implementation"),
        contract("verification"),
    ]
    workflow = {
        "schema_version": 1,
        "parent_run_id": "p-security",
        "workflow_id": "seo-content-astro-v1",
        "stages": stages,
    }
    state = ctl.json("init-workflow", payload=workflow)
    assert len(state["stages"]) == 4
    assert state["state"] != "review_ready"
    assert [s["status"] for s in state["stages"]] == ["issued", "pending", "pending", "pending"]


def test_full_four_stage_progression_requires_each_independent_verification(ctl, tmp_path):
    stages = [contract(name) for name in (
        "seo_evidence", "content_production", "site_implementation", "verification",
    )]
    ctl.json("init-workflow", payload={
        "schema_version": 1, "parent_run_id": "p-security",
        "workflow_id": "seo-content-astro-v1", "stages": stages,
    })
    for index, c in enumerate(stages):
        artifact = tmp_path / "worker" / f"{c['stage_id']}.txt"
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_text(f"evidence for {c['stage_id']}\n")
        artifact.chmod(0o600)
        ctl.ingest_stage(stage_receipt(c, artifact), f"{index}-{c['stage_id']}.json")
        before = ctl.state()
        assert before["state"] == "verifying"
        assert before["stages"][index]["status"] == "verifying"
        ctl.verify_stage(c["child_run_id"], f"{index}-{c['stage_id']}.json")
        after = ctl.state()
        assert after["stages"][index]["status"] == "accepted"
        if index < len(stages) - 1:
            assert after["state"] == "worker_running"
            assert after["stages"][index + 1]["status"] == "issued"
            assert after["state"] != "review_ready"
        else:
            assert after["state"] == "review_ready"
    assert [s["status"] for s in ctl.state()["stages"]] == ["accepted"] * 4
