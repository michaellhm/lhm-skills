import json
import os
import subprocess
from pathlib import Path

import pytest

from lhm_workflow.seo_envelope_runtime import ACTION, DISPATCH, PARENT, RegisteredAdapter, run

ROOT = Path(__file__).parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "registered_seo_adapter.py"


def request(root: Path):
    return {"schema_version": 1, "parent_run_id": PARENT, "action_id": ACTION, "action_version": 1, "envelope_sha256": "a" * 64, "site": "https://localhealthmarketing.com/", "urls": ["https://localhealthmarketing.com/"], "client": "local-health-marketing", "artifact_path": str(root / "seo-keywords.md"), "file_name": "seo-keywords.md", "discussion": "SEO-01 accepted", "tracker_expected_sha256": "b" * 64}


class RecordingAdapter(RegisteredAdapter):
    def __init__(self):
        super().__init__(str(FIXTURE), test_mode=True); self.calls = []
    def invoke(self, operation, argv, binding):
        self.calls.append((operation, argv, binding)); return super().invoke(operation, argv, binding)


def test_exact_callable_sequence_lineage_and_one_drive_create(tmp_path, monkeypatch):
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE", "1"); monkeypatch.setenv("LHM_SEO_ARTIFACT_ROOT", str(tmp_path))
    adapter = RecordingAdapter(); result = run(request(tmp_path), adapter)
    assert [argv[1] for operation, argv, _ in adapter.calls if operation == "claude_dispatch"] == ["submit-seo-gsc-readonly", "submit-specialist-readonly", "submit-google-drive-client-file-create", "submit-specialist-readonly", "submit-basicops-task-discussion-update"]
    assert [call[0] for call in adapter.calls] == ["claude_dispatch", "claude_dispatch", "claude_dispatch", "claude_dispatch", "department_lead_accept", "tracker_cas_readback", "claude_dispatch"]
    assert result["drive_create_count"] == 1 and result["stop_after_basicops_readback"] is True
    assert result["artifact_sha256"] == result["drive_receipt"]["readback_sha256"] == result["qa_receipt"]["artifact_sha256"]
    assert result["lead_acceptance"]["qa_receipt_sha256"]


def test_fail_closed_request_and_unregistered_adapter(tmp_path, monkeypatch):
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE", "1"); monkeypatch.setenv("LHM_SEO_ARTIFACT_ROOT", str(tmp_path))
    bad = request(tmp_path); bad["parent_run_id"] = "other"
    with pytest.raises(ValueError): run(bad, RegisteredAdapter(str(FIXTURE), test_mode=True))
    with pytest.raises(ValueError): RegisteredAdapter("relative-adapter")


def test_real_entry_isolated_rehearsal_without_credentials(tmp_path):
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(ROOT / "src"), "LHM_WORKFLOW_ADAPTER": str(FIXTURE), "LHM_WORKFLOW_TEST_MODE": "1", "LHM_SEO_ARTIFACT_ROOT": str(tmp_path), "LHM_SEO_FAILURE_ROOT": str(tmp_path / "failures")}
    done = subprocess.run([str(ROOT / "integration" / "lhm-seo-envelope-runtime")], input=json.dumps(request(tmp_path)), text=True, capture_output=True, env=env, check=False)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["status"] == "completed"
    assert not any(key in env for key in ("GOOGLE_APPLICATION_CREDENTIALS", "BASICOPS_TOKEN", "CLAUDE_API_KEY"))


def test_one_retry_then_immutable_linked_waiting_receipt(tmp_path, monkeypatch):
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE", "1"); monkeypatch.setenv("LHM_SEO_ARTIFACT_ROOT", str(tmp_path)); monkeypatch.setenv("LHM_SEO_FAILURE_ROOT", str(tmp_path / "failures"))
    fake = tmp_path / "failing-adapter"; fake.write_text("#!/bin/sh\nexit 9\n"); fake.chmod(0o755)
    result = run(request(tmp_path), RegisteredAdapter(str(fake), test_mode=True))
    assert result["status"] == "waiting_on_capability" and result["retry_count"] == 1
    files = sorted((tmp_path / "failures").glob("*.json")); assert len(files) == 2
    incident = json.loads(next(p for p in files if ".incident." in p.name).read_text())
    assert incident["attempts"] == 2 and result["incident_sha256"]
    assert run(request(tmp_path), RegisteredAdapter(str(fake), test_mode=True)) == result


def test_receipt_tamper_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE", "1"); monkeypatch.setenv("LHM_SEO_ARTIFACT_ROOT", str(tmp_path)); monkeypatch.setenv("LHM_SEO_FAILURE_ROOT", str(tmp_path / "failures"))
    fake = tmp_path / "bad-adapter"; fake.write_text("#!/bin/sh\nprintf '%s\\n' '{\"schema_version\":1}'\n"); fake.chmod(0o755)
    result = run(request(tmp_path), RegisteredAdapter(str(fake), test_mode=True))
    assert result["status"] == "waiting_on_capability"


def test_native_tracker_cli_schema_cas_and_exact_readback(tmp_path):
    value = "d" * 64
    summary = {"parent_run_id": PARENT, "workflow_id": "seo-envelope-v1", "accepted_receipts": [{"stage_id": "seo-delivery-qa", "contract_sha256": value, "artifact_sha256s": [value]}], "run_result": "succeeded", "work_state": "complete", "completed_at": "2026-08-24T12:00:00Z"}
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "LHM_WORKFLOW_ROOT": str(tmp_path / "state"), "LHM_WORKFLOW_TEST_MODE": "1", "LHM_TRACKER_VAULT": str(tmp_path / "vault")}
    empty = __import__("hashlib").sha256(b"").hexdigest()
    done = subprocess.run([str(ROOT / "lhm-workflow"), "tracker-cas-readback", empty], input=json.dumps(summary), text=True, capture_output=True, env=env, check=False)
    assert done.returncode == 0, done.stderr
    receipt = json.loads(done.stdout)
    assert receipt["path"] == "30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md"
    assert receipt["sha256"] == receipt["readback_sha256"]


def test_packaged_adapter_and_disabled_service_are_installable():
    adapter = ROOT / "integration" / "lhm-workflow-registered-adapter"
    service = (ROOT / "packaging" / "lhm-seo-envelope-runtime.service").read_text()
    installer = (ROOT / "packaging" / "install.sh").read_text()
    assert adapter.is_file() and os.access(adapter, os.X_OK)
    assert "WantedBy=" not in service and "LHM_WORKFLOW_ADAPTER=/usr/local/libexec/lhm-workflow-registered-adapter" in service
    assert 'integration/lhm-workflow-registered-adapter /usr/local/libexec/lhm-workflow-registered-adapter' in installer
