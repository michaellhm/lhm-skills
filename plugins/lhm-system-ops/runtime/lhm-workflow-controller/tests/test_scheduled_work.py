import json
import importlib.util
from importlib.machinery import SourceFileLoader
import subprocess
from pathlib import Path

import pytest

from lhm_workflow.scheduled_work import business_status, create_parent, load_definition, normalise_urls, persist_parent

ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "integration" / "scheduled-workflows.json"


def runtime_module():
    path = ROOT / "integration" / "lhm-scheduled-work-runtime"
    spec = importlib.util.spec_from_loader("scheduled_runtime", SourceFileLoader("scheduled_runtime", str(path)))
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(**overrides):
    value = {
        "source": "hermes-cron-alternate",
        "source_cron_id": "3994012c42ba",
        "job_name": "LHM weekly SEO rollout",
        "prompt": "Run the governed weekly SEO rollout.",
        "delivery": "none",
        "triggered_at": "2026-08-25T00:00:00Z",
    }
    value.update(overrides)
    return value


def test_registered_cron_creates_governed_parent_with_shared_contract(tmp_path):
    definition = load_definition(REGISTRY, "local-health-marketing-seo", test_mode=True)
    parent = create_parent(definition, event(), "seo-weekly-20260825")
    assert parent["stage_order"][:3] == ["chief_intake", "production_plan", "seo_plan"]
    assert parent["scheduled_contract"]["department"] == "seo"
    assert parent["scheduled_contract"]["destinations"]["basicops_task_id"] == "2192596"
    first = persist_parent(tmp_path, parent, test_mode=True)
    second = persist_parent(tmp_path, parent, test_mode=True)
    assert first["replayed"] is False and second["replayed"] is True
    assert first["parent_sha256"] == second["parent_sha256"]


def test_mismatched_cron_and_conflicting_replay_fail_closed(tmp_path):
    definition = load_definition(REGISTRY, "local-health-marketing-seo", test_mode=True)
    with pytest.raises(ValueError, match="does not match"):
        create_parent(definition, event(source_cron_id="other"), "seo-weekly-20260825")
    parent = create_parent(definition, event(), "seo-weekly-20260825")
    persist_parent(tmp_path, parent, test_mode=True)
    changed = dict(parent); changed["objective"] = "different"
    with pytest.raises(ValueError, match="conflicting"):
        persist_parent(tmp_path, changed, test_mode=True)


def test_url_normalisation_uses_exact_registered_property_and_rejects_escape():
    assert normalise_urls("https://localhealthmarketing.com/", ["/ahpra-compliance", "https://localhealthmarketing.com/blog/x"]) == [
        "https://localhealthmarketing.com/ahpra-compliance",
        "https://localhealthmarketing.com/blog/x",
    ]
    with pytest.raises(ValueError, match="outside"):
        normalise_urls("https://localhealthmarketing.com/", ["https://example.com/x"])


def test_scheduler_and_business_state_are_separate():
    assert business_status({"state": "running"}) == {"run_result": "accepted", "work_state": "running"}
    assert business_status({"state": "needs_repair"}) == {"run_result": "failed", "work_state": "waiting_on_capability"}
    assert business_status({"state": "closed"}) == {"run_result": "succeeded", "work_state": "completed"}


def test_real_entrypoint_is_idempotent_without_external_calls(tmp_path):
    event_path = tmp_path / "event.json"; event_path.write_text(json.dumps(event()))
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT / "src"), "LHM_WORKFLOW_TEST_MODE": "1"}
    command = ["python3", "-m", "lhm_workflow.scheduled_work", "local-health-marketing-seo", str(event_path), "seo-weekly-20260825", "--registry", str(REGISTRY), "--outbox", str(tmp_path / "outbox")]
    first = subprocess.run(command, env=env, text=True, capture_output=True, check=False)
    second = subprocess.run(command, env=env, text=True, capture_output=True, check=False)
    assert first.returncode == second.returncode == 0
    assert json.loads(first.stdout)["replayed"] is False
    assert json.loads(second.stdout)["replayed"] is True


def test_host_runtime_validates_closed_request_and_writes_final_receipt(tmp_path, monkeypatch):
    runtime = runtime_module()
    runtime.BASE = tmp_path
    runtime.INCOMING, runtime.PROCESSED, runtime.FAILED, runtime.RUNS = (tmp_path / name for name in ("incoming", "processed", "failed", "runs"))
    for directory in (runtime.INCOMING, runtime.PROCESSED, runtime.FAILED, runtime.RUNS):
        directory.mkdir()
    request = {
        "schema_version": 1,
        "workflow_key": "local-health-marketing-seo",
        "parent_run_id": "local-health-marketing-seo-20260825t0000z",
        "event": event(),
    }
    source = runtime.INCOMING / f"{request['parent_run_id']}.json"
    source.write_text(json.dumps(request))

    class Done:
        returncode = 0
        stdout = json.dumps({"status": "accepted", "work_state": "running"})
        stderr = ""

    observed = {}
    def runner(argv, **kwargs):
        observed["argv"] = argv
        return Done()

    runtime.process(source, runner=runner)
    assert observed["argv"][1] == "local-health-marketing-seo"
    final = json.loads((runtime.RUNS / request["parent_run_id"] / "final.json").read_text())
    assert final["scheduler"] == "accepted"
    assert final["receipt"]["work_state"] == "running"
    assert not source.exists()


def test_host_runtime_rejects_identity_mismatch():
    runtime = runtime_module()
    request = {"schema_version": 1, "workflow_key": "local-health-marketing-seo", "parent_run_id": "right", "event": event()}
    with pytest.raises(ValueError, match="identity"):
        runtime.validate(request, "wrong.json")


def test_cron_candidate_uses_only_container_visible_thin_trigger():
    candidate = json.loads((ROOT / "integration" / "cron-3994012c42ba.alternate.disabled.json").read_text())
    wrapper = (ROOT / "integration" / "lhm-seo-org-cron-alternate").read_text()
    assert candidate["script"].startswith("/opt/data/profiles/lhm_brain/bin/")
    assert "lhm-scheduled-work-dispatch" in wrapper
    assert "lhm-scheduled-work-ingress" not in wrapper
