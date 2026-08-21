from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path


def load_candidate():
    loader = importlib.machinery.SourceFileLoader("site_dispatcher_candidate", "/tmp/lhm-site-dispatcher.live")
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def request(request_id="astro-child-1", mode="branch", governed=True):
    return {
        "schema_version": 2 if governed else 1,
        "request_id": request_id,
        "site_id": "lhm-main",
        "objective": "Create the governed Astro staging change.",
        "mode": mode,
        "success_test": ["Preview passes verification"],
        "timeout_seconds": 900,
        "handback_note": "25 Marketing/Website/handback.md",
        **({"input_artifacts": [{
            "artifact_id": "content-1", "logical_name": "content.md",
            "media_type": "text/markdown", "size_bytes": 10,
            "sha256": "b" * 64, "purpose": "source_copy",
        }]} if governed else {}),
    }


def contract():
    return {
        "schema_version": 1,
        "parent_run_id": "parent-1",
        "child_run_id": "astro-child-1",
        "workflow_id": "seo-content-astro-v1",
        "stage_id": "astro",
        "idempotency_key": "a" * 64,
        "worker": {"runtime": "codex", "identity": "codexworker"},
        "required_skills": ["lhm-wordpress-hub:start-astro", "lhm-wordpress-hub:astro-build"],
        "required_capabilities": ["git.feature_branch_write", "cloudflare.preview_readback"],
        "permission_ceiling": "amber",
        "input_artifacts": [{"artifact_id": "content-1", "sha256": "b" * 64, "media_type": "text/markdown"}],
        "expected_mutation_state": "feature_branch",
    }


def test_legacy_request_schemas_are_unchanged():
    site = load_candidate()
    assert site.FIELDS_V1 == {
        "schema_version", "request_id", "site_id", "objective", "mode",
        "success_test", "timeout_seconds", "handback_note",
    }
    assert site.FIELDS_V2 == site.FIELDS_V1 | {"input_artifacts"}
    assert site.FIELDS_V3 == site.FIELDS_V2 | {"create_manifest"}


def test_standalone_legacy_request_does_not_emit_workflow_hooks(tmp_path, monkeypatch):
    site = load_candidate()
    monkeypatch.setattr(site, "WORKFLOW_CONTRACTS", tmp_path)
    assert site.governed_contract(request(governed=False)) is None


def test_governed_route_writes_common_envelope_then_calls_root_admit(tmp_path, monkeypatch):
    site = load_candidate()
    contracts = tmp_path / "contracts"; contracts.mkdir()
    contract_path = contracts / "astro-child-1.json"; contract_path.write_text("{}")
    run_dir = tmp_path / "run"; run_dir.mkdir()
    calls = []
    monkeypatch.setattr(site, "WORKFLOW_CONTRACTS", contracts)
    monkeypatch.setattr(site, "WORKFLOW_HOOK", Path("/trusted/root-hook"))
    monkeypatch.setattr(site, "read_root_json", lambda path, root: contract())
    monkeypatch.setattr(site, "atomic_text", lambda path, content, **kwargs: path.write_text(content))
    monkeypatch.setattr(site.subprocess, "run", lambda command, check: calls.append((command, check)))
    envelope = site.admit_governed_route(
        request(), {"permission_profile_id": "lhm-main-astro-v1"}, run_dir,
    )
    assert envelope["kind"] == "lhm_governed_dispatch"
    assert envelope["legacy_request"]["request_id"] == "astro-child-1"
    assert envelope["required_skills"] == contract()["required_skills"]
    assert json.loads((run_dir / "governed-envelope.json").read_text()) == envelope
    assert calls == [(["/trusted/root-hook", "admit", str(contract_path), "astro-child-1"], True)]


def test_governed_route_fails_closed_on_skill_or_mode_mismatch(tmp_path, monkeypatch):
    site = load_candidate()
    contracts = tmp_path / "contracts"; contracts.mkdir()
    (contracts / "astro-child-1.json").write_text("{}")
    monkeypatch.setattr(site, "WORKFLOW_CONTRACTS", contracts)
    bad = contract(); bad["required_skills"] = ["invented-skill"]
    monkeypatch.setattr(site, "read_root_json", lambda path, root: bad)
    try:
        site.governed_contract(request())
    except ValueError as exc:
        assert "skill contract mismatch" in str(exc)
    else:
        raise AssertionError("unsafe skill mismatch was accepted")
    monkeypatch.setattr(site, "read_root_json", lambda path, root: contract())
    try:
        site.governed_contract(request(mode="research"))
    except ValueError as exc:
        assert "amber branch mode" in str(exc)
    else:
        raise AssertionError("unsafe mode mismatch was accepted")


def test_governed_route_fails_closed_on_dependency_hash_mismatch(tmp_path, monkeypatch):
    site = load_candidate()
    contracts = tmp_path / "contracts"; contracts.mkdir()
    (contracts / "astro-child-1.json").write_text("{}")
    monkeypatch.setattr(site, "WORKFLOW_CONTRACTS", contracts)
    monkeypatch.setattr(site, "read_root_json", lambda path, root: contract())
    value = request(); value["input_artifacts"][0]["sha256"] = "c" * 64
    try:
        site.governed_contract(value)
    except ValueError as exc:
        assert "artifact binding mismatch" in str(exc)
    else:
        raise AssertionError("dependency hash mismatch was accepted")


def test_admit_failure_prevents_worker_launch(monkeypatch):
    site = load_candidate()
    launches = []
    def fail(*args, **kwargs):
        raise RuntimeError("admit failed")
    monkeypatch.setattr(site, "admit_governed_route", fail)
    monkeypatch.setattr(site.subprocess, "run", lambda *args, **kwargs: launches.append(args))
    try:
        site.launch_change(["systemd-run", "worker"], request(), {}, Path("/run"))
    except RuntimeError as exc:
        assert str(exc) == "admit failed"
    else:
        raise AssertionError("admit failure did not fail closed")
    assert launches == []
