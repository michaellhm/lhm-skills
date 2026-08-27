import copy
import json
import subprocess

from lhm_workflow.delegated_basicops_runtime import closed_workflow_observation
from lhm_workflow.delegated_connector import human_decision_event, projection_receipt
from lhm_workflow.delegated_task import (
    DelegatedTaskStore,
    authenticated,
    chief_complete,
    chief_start,
    correction_fixed,
    delivery_decision,
    digest,
    plan_decision,
    post_plan,
    record_projection,
    review_ready,
    seal,
    steward_disposition,
)
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


def test_workflow_marker_rejects_wrong_ai_author_and_non_allowlisted_fields(tmp_path):
    private, _ = keys(tmp_path)
    state, _ = project(initial(), "p0")
    marker = {
        "event_id":"pm-marker-1", "operation":"post-plan", "plan":{"steps":["Draft"]},
        "handoff":handoff("awaiting_plan_approval", "Aiya", "plan_approval"),
    }
    body = "LHM workflow event: " + json.dumps(marker, separators=(",", ":"))
    observed = {"message_id":"msg-pm-1", "author_user_id":"82484", "task_id":"2199999",
        "task_revision":"12", "observed_at":"2026-08-27T10:00:00+10:00", "body":body}
    operation, signed = closed_workflow_observation(state, observed, private)
    assert operation == "post-plan" and signed["actor_user_id"] == "82484"
    bad_author = {**observed, "message_id":"msg-pm-2", "author_user_id":"82491"}
    try:
        closed_workflow_observation(state, bad_author, private)
        assert False, "Waylon must not submit Monica's plan marker"
    except ValueError:
        pass
    expanded = dict(marker, command="run arbitrary code")
    bad_fields = {**observed, "message_id":"msg-pm-3",
        "body":"LHM workflow event: " + json.dumps(expanded, separators=(",", ":"))}
    try:
        closed_workflow_observation(state, bad_fields, private)
        assert False, "extra workflow marker fields must fail closed"
    except ValueError:
        pass


def test_steward_and_cto_markers_are_bound_to_parent_actor_ids(tmp_path):
    private, _ = keys(tmp_path)
    state = initial()
    cases = [
        ("steward-disposition", "500", {
            "event_id":"steward-marker", "correction_event_id":"correction-1",
            "disposition":"observe_again", "promotion_status":"not_applicable"}),
        ("capability-restored", "400", {
            "event_id":"cto-marker", "result":"capability_restored",
            "verification_evidence":["incident:CII-1:passed"],
            "handoff":handoff("executing", "Waylon")}),
    ]
    for operation, author, payload in cases:
        body="LHM workflow event: "+json.dumps(
            {"operation":operation, **payload}, separators=(",", ":"))
        observed={"message_id":f"message-{operation}", "author_user_id":author,
            "task_id":"2199999", "task_revision":"20",
            "observed_at":"2026-08-27T10:00:00+10:00", "body":body}
        observed_operation,event=closed_workflow_observation(state, observed, private)
        assert observed_operation == operation and event["actor_user_id"] == author
        try:
            closed_workflow_observation(state, {**observed,"author_user_id":"82491"}, private)
            assert False, "marker must remain bound to the parent actor registry"
        except ValueError:
            pass
def test_observed_human_lifecycle_survives_restart_and_replay(tmp_path):
    """Exercise the whole reversible canary using only observed BasicOps decisions.

    Re-opening the store before every operation models a fresh controller process. Replaying
    an already-consumed human observation must be a no-op and must not duplicate corrections.
    """
    adapter_private, adapter_public = keys(tmp_path)
    state_root = tmp_path / "delegated-parents"
    store = DelegatedTaskStore(state_root)
    state = store.checkpoint(initial(), expected_generation=None)
    revision = 10

    def restart():
        return DelegatedTaskStore(state_root).load("delegated-1")

    def checkpoint(updated, previous):
        return DelegatedTaskStore(state_root).checkpoint(
            updated, expected_generation=previous["generation"]
        )

    def observe_projection(current, event_id):
        nonlocal revision
        expected = current["projection_pending"]
        observation = {
            "event_id": event_id,
            "task_id": current["basicops_task_id"],
            "assignee_user_id": expected["assignee_user_id"],
            "native_status": expected["native_status"],
            "review_type": expected["review_type"],
            "discussion_message_id": f"discussion-{event_id}",
            "discussion_body_sha256": expected["discussion_sha256"],
            "task_revision_before": str(revision),
            "task_revision_after": str(revision + 1),
            "task_url": "https://basicops.example/task/2199999",
            "readback_observed_at": "2026-08-27T10:00:00+10:00",
            "verification": "passed",
        }
        revision += 1
        receipt = projection_receipt(current, observation, adapter_private)
        return checkpoint(record_projection(current, receipt, adapter_public), current), receipt

    def observe_human(current, event_id, decision, handoff_value, *, correction=None):
        observation = {
            "event_id": event_id,
            "message_id": f"message-{event_id}",
            "author_user_id": "100",
            "task_id": "2199999",
            "task_revision": str(revision),
            "observed_at": "2026-08-27T10:05:00+10:00",
            "body_sha256": digest({"message_id": f"message-{event_id}", "decision": decision}),
            "decision": decision,
            "plan_version": current["plan"]["version"] if current["state"] == "awaiting_plan_approval" else None,
            "plan_sha256": current["plan"]["material_sha256"] if current["state"] == "awaiting_plan_approval" else None,
            "correction": correction,
            "handoff": handoff_value,
            "verification": "passed",
        }
        return human_decision_event(current, observation, adapter_private)

    def observe_ai(current, operation, author_user_id, marker):
        body = "LHM workflow event: " + json.dumps(
            {"operation": operation, **marker}, sort_keys=True, separators=(",", ":")
        )
        observed = {
            "message_id": f"message-{marker['event_id']}",
            "author_user_id": str(author_user_id), "task_id": "2199999",
            "task_revision": str(revision), "observed_at": "2026-08-27T10:04:00+10:00",
            "body": body,
        }
        observed_operation, signed = closed_workflow_observation(
            current, observed, adapter_private
        )
        assert observed_operation == operation
        return signed

    state, _ = observe_projection(restart(), "projection-initial")
    plan = {"steps": ["Post an internal Discussion-only colour token"]}
    current = restart()
    posted = observe_ai(current, "post-plan", 82484, {
        "event_id":"plan-canary", "plan":plan,
        "handoff":handoff("awaiting_plan_approval", "Aiya", "plan_approval")})
    state = checkpoint(post_plan(current, posted, adapter_public), current)
    state, _ = observe_projection(restart(), "projection-plan-review")

    current = restart()
    approval = observe_human(
        current, "observed-plan-approval", "approved", handoff("approved", "Waylon")
    )
    state = checkpoint(plan_decision(current, approval, adapter_public), current)
    replayed = plan_decision(restart(), approval, adapter_public)
    assert replayed == restart()
    assert replayed["plan"]["approval_receipt"]["basicops_observation"]["message_id"] == "message-observed-plan-approval"
    state, _ = observe_projection(restart(), "projection-approved")

    current = restart()
    started = observe_ai(current, "chief-start", 82491, {
        "event_id":"chief-start", "handoff":handoff("executing", "Waylon")})
    state = checkpoint(chief_start(current, started, adapter_public), current)
    state, _ = observe_projection(restart(), "projection-executing")

    current = restart()
    first_review = observe_ai(current, "review-ready", 82491, {
        "event_id":"review-blue", "completion_evidence":["basicops:discussion:colour-blue"],
        "handoff":handoff("awaiting_delivery_review", "Aiya", "delivery_review")})
    state = checkpoint(review_ready(current, first_review, adapter_public), current)
    state, _ = observe_projection(restart(), "projection-review-blue")

    correction = {
        "old_value": "blue", "new_value": "green", "source": "Aiya BasicOps review",
        "authority_scope": "canary wording", "affected_locations": ["basicops:discussion:colour-token"],
    }
    current = restart()
    correction_observation = observe_human(
        current, "observed-correction", "correction_requested",
        handoff("correction_requested", "Waylon"), correction=correction,
    )
    state = checkpoint(delivery_decision(current, correction_observation, adapter_public), current)
    assert len(state["correction_events"]) == 1
    assert delivery_decision(restart(), correction_observation, adapter_public) == restart()
    assert len(restart()["correction_events"]) == 1
    state, _ = observe_projection(restart(), "projection-correction")

    current = restart()
    resumed = observe_ai(current, "chief-start", 82491, {
        "event_id":"resume-correction", "handoff":handoff("executing", "Waylon")})
    state = checkpoint(chief_start(current, resumed, adapter_public), current)
    state, _ = observe_projection(restart(), "projection-correction-executing")

    current = restart()
    fixed = observe_ai(current, "correction-fixed", 82491, {
        "event_id":"correction-fixed", "correction_event_id":"observed-correction",
        "fix_evidence":["basicops:discussion:colour-green:readback"]})
    state = checkpoint(correction_fixed(current, fixed, adapter_public), current)
    current = restart()
    steward = observe_ai(current, "steward-disposition", 500, {
        "event_id":"steward-canary", "correction_event_id":"observed-correction",
        "disposition":"project_evidence", "promotion_status":"not_applicable"})
    state = checkpoint(steward_disposition(current, steward, adapter_public), current)

    current = restart()
    corrected_review = observe_ai(current, "review-ready", 82491, {
        "event_id":"review-green", "completion_evidence":["basicops:discussion:colour-green:readback"],
        "handoff":handoff("awaiting_delivery_review", "Aiya", "delivery_review")})
    state = checkpoint(review_ready(current, corrected_review, adapter_public), current)
    state, _ = observe_projection(restart(), "projection-review-green")

    current = restart()
    acceptance = observe_human(
        current, "observed-delivery-acceptance", "accepted",
        handoff("completion_pending", "Waylon"),
    )
    state = checkpoint(delivery_decision(current, acceptance, adapter_public), current)
    assert delivery_decision(restart(), acceptance, adapter_public) == restart()
    state, _ = observe_projection(restart(), "projection-completion-pending")

    current = restart()
    completed = observe_ai(current, "chief-complete", 82491, {
        "event_id":"chief-complete", "decision":"completed",
        "completion_checks":["Approved page exists in staging"],
        "handoff":handoff("completed", "Waylon")})
    state = checkpoint(chief_complete(current, completed, adapter_public), current)
    state, final_projection = observe_projection(restart(), "projection-complete")

    assert state["state"] == "completed"
    assert state["basicops_task_id"] == "2199999"
    assert state["parent_run_id"] == "delegated-1"
    assert state["correction_events"][0]["old_value"] == "blue"
    assert state["correction_events"][0]["new_value"] == "green"
    assert state["correction_events"][0]["steward_status"] == "project_evidence"
    assert final_projection["readback"]["native_status"] == "Complete"
