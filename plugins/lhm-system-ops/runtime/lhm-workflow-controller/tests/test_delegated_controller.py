import copy

from lhm_workflow.controller import WorkflowController
from lhm_workflow.delegated_task import digest, seal


def actor(user_id, name):
    return {"user_id": str(user_id), "canonical_name": name, "workspace_id": "481630853364967730", "verified_at": "2026-08-27T00:00:00+10:00"}


ACTORS = {
    "human": actor(100, "Aiya"), "project_manager": actor(82484, "Lily"),
    "chief_of_staff": actor(82491, "Ted"), "cto": actor(900, "CTO"),
    "learning_steward": actor(901, "Learning Steward"),
}


def handoff(state, owner, review="none"):
    return {
        "state": state, "outcome_owner": "chief_of_staff", "next_action_owner": owner,
        "review_type": review, "completed": [], "evidence": [], "remaining": ["Finish"],
        "next_action": "Take the next action.", "resume_trigger": "The action is verified.",
        "completion_condition": "Staging page passes QA", "calls_made": [],
        "decision_required": [], "notification_receipt": None,
    }


def sign(controller, key_name, body):
    return seal(body, (controller.secrets / key_name).read_bytes())


def project(controller, state, event_id):
    expected = copy.deepcopy(state["projection_pending"])
    receipt = sign(controller, "basicops.key", {
        "schema_version": 1, "role": "basicops_connector", "event_id": event_id,
        "parent_run_id": "delegated-cli-1", "projection": expected, "readback": expected,
        "mutation": {"task_revision_before": "1", "task_revision_after": "2", "discussion_message_id": f"msg-{event_id}", "task_url": "https://basicops.example/task/2199999", "readback_observed_at": "2026-08-27T00:00:00+10:00"},
    })
    return controller.delegated_transition("delegated-cli-1", "project", receipt)


def test_controller_persists_version_bound_plan_and_exact_basicops_baton(tmp_path):
    controller = WorkflowController(tmp_path / "runtime", test_mode=True)
    state = controller.delegated_init({
        "parent_run_id": "delegated-cli-1", "basicops_task_id": "2199999",
        "basicops_target": {"client_slug": "local-health-marketing", "handback_task_id": "2199999"},
        "basicops_dedupe_key": "delegated:aiya:page-1", "objective": "Create page",
        "completion_condition": "Staging page passes QA", "permission_ceiling": "green",
        "actors": ACTORS, "initial_handoff": handoff("planning", "Lily"),
    })
    state = project(controller, state, "project-0")
    plan = {"steps": [{"role": "Content", "skill": "copywriting"}]}
    posted = sign(controller, "project-manager.key", {
        "role": "project_manager", "event_id": "plan-1", "actor_user_id": "82484",
        "parent_run_id": "delegated-cli-1", "task_id": "2199999", "plan": plan,
        "handoff": handoff("awaiting_plan_approval", "Aiya", "plan_approval"),
    })
    state = controller.delegated_transition("delegated-cli-1", "post-plan", posted)
    assert state["projection_pending"]["native_status"] == "Under Review"
    assert state["projection_pending"]["assignee_user_id"] == "100"
    state = project(controller, state, "project-1")
    approval = sign(controller, "human-approval.key", {
        "role": "human_approver", "event_id": "approve-1", "actor_user_id": "100",
        "parent_run_id": "delegated-cli-1", "task_id": "2199999", "decision": "approved",
        "plan_version": 1, "plan_sha256": digest(plan), "handoff": handoff("approved", "Ted"),
        "basicops_observation": {"message_id": "human-approve-1", "author_user_id": "100", "task_id": "2199999", "task_revision": "7", "observed_at": "2026-08-27T00:00:00+10:00", "body_sha256": digest({"decision": "approved"})},
    })
    state = controller.delegated_transition("delegated-cli-1", "plan-decision", approval)
    assert state["projection_pending"]["native_status"] == "In Progress"
    assert state["projection_pending"]["assignee_user_id"] == "82491"
    assert controller.delegated.load("delegated-cli-1")["plan"]["approval_receipt"]["event_id"] == "approve-1"
