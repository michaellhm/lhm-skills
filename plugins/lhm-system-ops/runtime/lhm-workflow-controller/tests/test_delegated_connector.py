import copy
import subprocess

from lhm_workflow.delegated_connector import human_decision_event, projection_receipt
from lhm_workflow.delegated_task import authenticated, digest, record_projection
from test_delegated_task import BASICOPS, HUMAN, approved_execution, event, handoff, initial, project


def keys(tmp_path):
    private = tmp_path / "adapter.private.pem"
    public = tmp_path / "adapter.public.pem"
    subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)], check=True)
    subprocess.run(["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True)
    return private, public


def test_projection_adapter_requires_exact_independent_readback(tmp_path):
    private, public = keys(tmp_path)
    state = initial()
    expected = state["projection_pending"]
    observation = {
        "event_id": "basicops-readback-1", "task_id": "2199999",
        "assignee_user_id": "82484", "native_status": "In Progress", "review_type": "none",
        "discussion_message_id": "message-1", "discussion_body_sha256": digest(state["handoff"]),
        "task_revision_before": "11", "task_revision_after": "12",
        "task_url": "https://basicops.example/task/2199999",
        "readback_observed_at": "2026-08-27T10:00:00+10:00", "verification": "passed",
    }
    receipt = projection_receipt(state, observation, private)
    assert authenticated(receipt, public, "basicops_connector")
    assert record_projection(state, receipt, public)["projection_pending"] is None
    bad = copy.deepcopy(observation); bad["assignee_user_id"] = "82491"
    try:
        projection_receipt(state, bad, private)
        assert False, "mismatched assignment must fail"
    except ValueError:
        pass


def test_human_adapter_binds_real_message_author_revision_and_current_plan(tmp_path):
    private, public = keys(tmp_path)
    state, _ = project(initial(), "p0")
    plan = {"steps": ["Discussion canary"]}
    state = __import__("lhm_workflow.delegated_task", fromlist=["post_plan"]).post_plan(
        state, event("project_manager", "plan-observed", 82484, plan=plan,
                     handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), b"project-manager")
    state, _ = project(state, "p1")
    observation = {
        "event_id": "human-observed-1", "message_id": "human-message-1", "author_user_id": "100",
        "task_id": "2199999", "task_revision": "15", "observed_at": "2026-08-27T10:05:00+10:00",
        "body_sha256": digest({"body": "Approve plan v1"}), "decision": "approved",
        "plan_version": 1, "plan_sha256": digest(plan), "correction": None,
        "handoff": handoff("approved", "Waylon"), "verification": "passed",
    }
    signed = human_decision_event(state, observation, private)
    assert authenticated(signed, public, "human_approver")
    bad = copy.deepcopy(observation); bad["author_user_id"] = "999"
    try:
        human_decision_event(state, bad, private)
        assert False, "wrong author must fail"
    except ValueError:
        pass
