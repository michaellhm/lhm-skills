import json
import subprocess

import pytest

from lhm_workflow.delegated_basicops_runtime import (
    closed_decision_observation, durable_put, projection_dispatch_id,
    projection_request, signed_projection_import,
)
from lhm_workflow.delegated_task import _consume, authenticated, digest, seal
from test_delegated_task import HUMAN, event, handoff, initial, project


def keypair(tmp_path):
    private = tmp_path / "private.pem"; public = tmp_path / "public.pem"
    subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)], check=True)
    subprocess.run(["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True)
    return private, public


def registry(task="2199999"):
    return {"clients": {"local-health-marketing": {"basicops_task_ids": [task]}}}


def approval_state():
    state, _ = project(initial(), "p0")
    plan = {"steps": ["Draft"]}
    module = __import__("lhm_workflow.delegated_task", fromlist=["post_plan"])
    state = module.post_plan(state, event("project_manager", "plan", 82484, plan=plan,
        handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), b"project-manager")
    state, _ = project(state, "p1")
    return state, plan


def test_projection_request_is_deterministic_and_registry_bound(tmp_path):
    state = initial()
    one = projection_request(state, registry()); two = projection_request(state, registry())
    assert one == two and one["dispatch_id"] == projection_dispatch_id(state)
    assert one["discussion_sha256"] == digest(state["handoff"])
    first = durable_put(tmp_path, one["dispatch_id"], one)
    assert durable_put(tmp_path, one["dispatch_id"], one) == first
    with pytest.raises(ValueError, match="governed handback"):
        projection_request(state, registry("999"))


def test_projection_worker_observation_is_signed_only_after_exact_validation(tmp_path):
    private, public = keypair(tmp_path); state = initial(); expected = state["projection_pending"]
    result = {"verification": "passed", "event_id": "readback-1", "task_id": "2199999",
        "assignee_user_id": expected["assignee_user_id"], "native_status": expected["native_status"],
        "review_type": expected["review_type"], "discussion_message_id": "m1",
        "discussion_body_sha256": expected["discussion_sha256"], "task_revision_before": "1",
        "task_revision_after": "2", "task_url": "https://basicops.example/task/2199999",
        "readback_observed_at": "2026-08-27T10:00:00+10:00", "checks": ["readback"], "error": None}
    receipt = signed_projection_import(state, result, private)
    assert authenticated(receipt, public, "basicops_connector")
    assert receipt["mutation"]["readback_observed_at"] != result["readback_observed_at"]
    assert receipt["mutation"]["readback_observed_at"].endswith("+00:00")
    receipt_from_date_only_worker = signed_projection_import(
        state, {**result, "readback_observed_at": "2026-08-27"}, private)
    assert authenticated(receipt_from_date_only_worker, public, "basicops_connector")
    assert receipt_from_date_only_worker["mutation"]["readback_observed_at"].endswith("+00:00")
    with pytest.raises(ValueError):
        signed_projection_import(state, {**result, "task_id": "999"}, private)


def test_human_observer_accepts_only_closed_exact_marker(tmp_path):
    private, public = keypair(tmp_path); state, plan = approval_state()
    marker = {"event_id": "approve-1", "decision": "approved", "plan_version": 1,
        "plan_sha256": digest(plan), "correction": None, "handoff": handoff("approved", "Ted")}
    observed = {"message_id": "m2", "author_user_id": "100", "task_id": "2199999",
        "task_revision": "3", "observed_at": "2026-08-27T10:05:00+10:00",
        "body": "LHM decision: " + json.dumps(marker)}
    signed = closed_decision_observation(state, observed, private)
    assert authenticated(signed, public, "human_approver")
    with pytest.raises(ValueError, match="closed LHM decision"):
        closed_decision_observation(state, {**observed, "body": "looks good"}, private)


def test_same_basicops_observation_cannot_be_reattested_with_new_event_id():
    state, plan = approval_state()
    observation = {"message_id": "m2", "author_user_id": "100", "task_id": "2199999",
        "task_revision": "3", "observed_at": "2026-08-27T10:05:00+10:00",
        "body_sha256": digest({"body": "marker"})}
    base = {"role": "human_approver", "actor_user_id": "100", "parent_run_id": "delegated-1",
        "task_id": "2199999", "decision": "approved", "plan_version": 1,
        "plan_sha256": digest(plan), "handoff": handoff("approved", "Ted"),
        "basicops_observation": observation}
    consumed, replay = _consume(state, seal({**base, "event_id": "first"}, HUMAN), HUMAN, "human_approver")
    assert replay is False and consumed["processed_observation_ids"]
    with pytest.raises(ValueError, match="observation already consumed"):
        _consume(consumed, seal({**base, "event_id": "second"}, HUMAN), HUMAN, "human_approver")
