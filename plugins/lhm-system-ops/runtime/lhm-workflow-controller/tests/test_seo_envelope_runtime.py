import json
import os
import subprocess
from pathlib import Path

import pytest

from lhm_workflow.seo_envelope_runtime import ACTION, DISPATCH, PARENT, RegisteredAdapter, run

ROOT = Path(__file__).parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "registered_seo_adapter.py"


def request():
    return {"schema_version": 1, "parent_run_id": PARENT, "action_id": ACTION, "action_version": 1, "envelope_sha256": "a" * 64, "site": "https://localhealthmarketing.com/", "urls": ["https://localhealthmarketing.com/"], "client": "local-health-marketing", "artifact_path": "/var/lib/lhm-workflow/artifacts/seo-keywords.md", "file_name": "seo-keywords.md", "discussion": "SEO-01 accepted", "tracker_expected_sha256": "b" * 64}


class RecordingAdapter(RegisteredAdapter):
    def __init__(self):
        super().__init__(str(FIXTURE), test_mode=True); self.calls = []
    def invoke(self, operation, argv, binding):
        self.calls.append((operation, argv, binding)); return super().invoke(operation, argv, binding)


def test_exact_callable_sequence_receipts_and_one_drive_create():
    adapter = RecordingAdapter(); result = run(request(), adapter)
    commands = [argv[1] for operation, argv, _ in adapter.calls if operation == "claude_dispatch"]
    assert commands == ["submit-seo-gsc-readonly", "submit-specialist-readonly", "submit-specialist-readonly", "submit-google-drive-client-file-create", "submit-basicops-task-discussion-update"]
    assert [call[1][2] for call in adapter.calls if len(call[1]) > 2 and call[1][1] == "submit-specialist-readonly"] == ["keyword-research", "seo-delivery-qa"]
    assert all(call[1][0] == DISPATCH for call in adapter.calls if call[0] == "claude_dispatch")
    assert [call[0] for call in adapter.calls] == ["claude_dispatch", "claude_dispatch", "claude_dispatch", "department_lead_accept", "tracker_cas_readback", "claude_dispatch", "claude_dispatch"]
    assert result["drive_create_count"] == 1 and result["lead_acceptance"]["immutable_readback"] is True and result["tracker_receipt"]["cas"] is True


def test_fail_closed_request_and_unregistered_adapter():
    bad = request(); bad["parent_run_id"] = "other"
    with pytest.raises(ValueError): run(bad, RegisteredAdapter(str(FIXTURE), test_mode=True))
    with pytest.raises(ValueError): RegisteredAdapter("relative-adapter")


def test_real_entry_isolated_rehearsal_without_credentials(tmp_path):
    env = {"PATH": os.environ["PATH"], "PYTHONPATH": str(ROOT / "src"), "LHM_WORKFLOW_ADAPTER": str(FIXTURE), "LHM_WORKFLOW_TEST_MODE": "1"}
    done = subprocess.run([str(ROOT / "integration" / "lhm-seo-envelope-runtime")], input=json.dumps(request()), text=True, capture_output=True, env=env, check=False)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout)["status"] == "completed"
    assert not any(key in env for key in ("GOOGLE_APPLICATION_CREDENTIALS", "BASICOPS_TOKEN", "CLAUDE_API_KEY"))


def test_receipt_tamper_fails(tmp_path):
    fake = tmp_path / "bad-adapter"
    fake.write_text("#!/bin/sh\nprintf '%s\\n' '{\"schema_version\":1}'\n")
    fake.chmod(0o755)
    with pytest.raises(ValueError): run(request(), RegisteredAdapter(str(fake), test_mode=True))
