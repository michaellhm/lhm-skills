import copy
from datetime import datetime, timedelta, timezone

import pytest

from lhm_workflow.barney_monitor import evaluate, render_notification
from lhm_workflow.delegated_task import (
    DelegatedTaskStore, capability_restored, chief_complete, chief_start, correction_fixed, delivery_decision, digest,
    heartbeat, new_state, plan_decision, post_plan, record_projection,
    review_ready, seal, steward_disposition, validate_state,
)

PM = b"project-manager"
HUMAN = b"human"
CHIEF = b"chief"
BASICOPS = b"basicops"
STEWARD = b"steward"


def actor(user_id, name):
    return {"user_id": str(user_id), "canonical_name": name, "workspace_id": "lhm", "verified_at": "2026-08-27T00:00:00+10:00"}


ACTORS = {
    "human": actor(100, "Aiya"),
    "project_manager": {"user_id": "82484", "canonical_name": "Monica AI", "workspace_id": "481630853364967730", "verified_at": "2026-08-27T00:00:00+10:00"},
    "chief_of_staff": {"user_id": "82491", "canonical_name": "Waylon", "workspace_id": "481630853364967730", "verified_at": "2026-08-27T00:00:00+10:00"},
    "cto": actor(400, "CTO"),
    "learning_steward": actor(500, "Learning Steward"),
}


def handoff(state, owner, review="none", *, calls=None, decisions=None, completed=None, evidence=None):
    return {
        "state": state,
        "outcome_owner": "chief_of_staff",
        "next_action_owner": owner,
        "review_type": review,
        "completed": completed or [],
        "evidence": evidence or [],
        "remaining": ["Finish the delegated outcome"],
        "next_action": "Take the next bounded action.",
        "resume_trigger": "The recorded next action is verified.",
        "completion_condition": "Approved page exists in staging",
        "calls_made": calls or [],
        "decision_required": decisions or [],
        "notification_receipt": None,
    }


def initial():
    return new_state(
        parent_run_id="delegated-1", basicops_task_id="2199999",
        basicops_target={"client_slug": "local-health-marketing", "handback_task_id": "2199999"},
        basicops_dedupe_key="delegated:aiya:page-1", objective="Create a service page",
        completion_condition="Approved page exists in staging", permission_ceiling="green",
        actors=ACTORS, initial_handoff=handoff("planning", "Monica AI"),
    )


def project(state, event_id):
    expected = copy.deepcopy(state["projection_pending"])
    receipt = seal({
        "schema_version": 1, "role": "basicops_connector", "event_id": event_id,
        "parent_run_id": state["parent_run_id"], "projection": expected, "readback": expected,
        "mutation": {"task_revision_before": "1", "task_revision_after": "2", "discussion_message_id": f"msg-{event_id}", "task_url": "https://basicops.example/task/2199999", "readback_observed_at": "2026-08-27T00:00:00+10:00"},
    }, BASICOPS)
    return record_projection(state, receipt, BASICOPS), receipt


def event(role, event_id, actor_id, **values):
    body = {
        "role": role, "event_id": event_id, "actor_user_id": str(actor_id),
        "parent_run_id": "delegated-1", "task_id": "2199999", **values,
    }
    if role in {"human_approver", "human_reviewer"}:
        body["basicops_observation"] = {"message_id": f"human-{event_id}", "author_user_id": str(actor_id), "task_id": "2199999", "task_revision": "7", "observed_at": "2026-08-27T00:00:00+10:00", "body_sha256": digest({"event_id": event_id})}
    key = {"project_manager": PM, "human_approver": HUMAN, "human_reviewer": HUMAN, "chief_of_staff": CHIEF, "learning_steward": STEWARD}[role]
    return seal(body, key)


def approved_execution():
    state, _ = project(initial(), "p0")
    plan = {"steps": ["Content", "Website", "QA"], "skills": ["copywriting", "wp-page-builder"]}
    posted = event("project_manager", "plan-1", 82484, plan=plan, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval"))
    state = post_plan(state, posted, PM)
    state, _ = project(state, "p1")
    approved = event("human_approver", "approve-1", 100, decision="approved", plan_version=1, plan_sha256=digest(plan), handoff=handoff("approved", "Waylon"))
    state = plan_decision(state, approved, HUMAN)
    state, _ = project(state, "p2")
    started = event("chief_of_staff", "start-1", 82491, handoff=handoff("executing", "Waylon"))
    state = chief_start(state, started, CHIEF)
    state, _ = project(state, "p3")
    return state, plan


def test_complete_baton_preserves_one_task_and_requires_human_plan_approval():
    state, plan = approved_execution()
    assert state["basicops_task_id"] == "2199999" and state["state"] == "executing"
    calls = [{"choice": "Used the Hawthorn address from the client profile", "location": "CTA", "release_state": "staging"}]
    ready = event("chief_of_staff", "ready-1", 82491, completion_evidence=["staging-url", "qa-pass"], handoff=handoff("awaiting_delivery_review", "Aiya", "delivery_review", calls=calls, completed=["Page built"], evidence=["staging-url", "qa-pass"]))
    state = review_ready(state, ready, CHIEF)
    assert state["projection_pending"]["native_status"] == "Under Review"
    state, _ = project(state, "p4")
    accepted = event("human_reviewer", "accept-1", 100, decision="accepted", handoff=handoff("completion_pending", "Waylon", completed=["Delivery accepted"], evidence=["review-message-1"]))
    state = delivery_decision(state, accepted, HUMAN)
    state, _ = project(state, "p5")
    completed = event("chief_of_staff", "complete-1", 82491, decision="completed", completion_checks=["Approved page exists in staging"], handoff=handoff("completed", "Waylon", completed=["Outcome verified"], evidence=["staging-url", "qa-pass", "human-acceptance"]))
    state = chief_complete(state, completed, CHIEF)
    assert state["state"] == "completed" and state["projection_pending"]["native_status"] == "Complete"
    assert state["plan"]["version"] == 1 and state["plan"]["material_sha256"] == digest(plan)


def test_stale_plan_approval_rejected_and_changes_resume_same_task():
    state, _ = project(initial(), "p0")
    first = {"steps": ["Draft"]}
    state = post_plan(state, event("project_manager", "plan-1", 82484, plan=first, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), PM)
    state, _ = project(state, "p1")
    changes = event("human_approver", "changes-1", 100, decision="changes_requested", plan_version=1, plan_sha256=digest(first), handoff=handoff("planning", "Monica AI"))
    state = plan_decision(state, changes, HUMAN)
    state, _ = project(state, "p2")
    second = {"steps": ["Draft", "Mobile QA"]}
    state = post_plan(state, event("project_manager", "plan-2", 82484, plan=second, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), PM)
    state, _ = project(state, "p3")
    stale = event("human_approver", "stale", 100, decision="approved", plan_version=1, plan_sha256=digest(first), handoff=handoff("approved", "Waylon"))
    with pytest.raises(ValueError, match="stale"):
        plan_decision(state, stale, HUMAN)
    assert state["basicops_task_id"] == "2199999" and state["plan"]["version"] == 2


def test_projection_requires_exact_assignment_status_discussion_readback_and_replay_is_safe():
    state = initial()
    expected = copy.deepcopy(state["projection_pending"])
    bad = seal({"schema_version": 1, "role": "basicops_connector", "event_id": "bad", "parent_run_id": "delegated-1", "projection": expected, "readback": {**expected, "native_status": "Complete"}, "mutation": {"task_revision_before": "1", "task_revision_after": "2", "discussion_message_id": "msg-bad", "task_url": "https://basicops.example/task/2199999", "readback_observed_at": "2026-08-27T00:00:00+10:00"}}, BASICOPS)
    with pytest.raises(ValueError, match="readback mismatch"):
        record_projection(state, bad, BASICOPS)
    projected, receipt = project(state, "good")
    assert record_projection(projected, receipt, BASICOPS) == projected
    with pytest.raises(ValueError, match="projection must be verified"):
        post_plan(state, event("project_manager", "early", 82484, plan={"steps": ["x"]}, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), PM)


def test_ai_identity_cannot_be_supplied_by_display_name_or_unverified_id():
    actors = copy.deepcopy(ACTORS)
    actors["project_manager"]["user_id"] = "99999"
    with pytest.raises(ValueError, match="verified BasicOps AI registry"):
        new_state(
            parent_run_id="spoofed", basicops_task_id="2199999",
            basicops_target={"client_slug": "local-health-marketing", "handback_task_id": "2199999"},
            basicops_dedupe_key="delegated:spoofed", objective="Create a page",
            completion_condition="Page exists", permission_ceiling="green", actors=actors,
            initial_handoff={**handoff("planning", "Monica AI"), "completion_condition": "Page exists"},
        )


def test_correction_resumes_same_parent_and_steward_routes_without_promoting_one_off():
    state, _ = approved_execution()
    state = review_ready(state, event("chief_of_staff", "ready", 82491, completion_evidence=["preview"], handoff=handoff("awaiting_delivery_review", "Aiya", "delivery_review", calls=[{"choice": "Used 123 Smith St", "location": "CTA", "release_state": "staging"}])), CHIEF)
    state, _ = project(state, "p4")
    correction = {"old_value": "123 Smith St", "new_value": "125 Smith St", "source": "Aiya review", "authority_scope": "website domain owner", "affected_locations": ["page:cta", "client-profile:address"]}
    request = event("human_reviewer", "correct-1", 100, decision="correction_requested", correction=correction, handoff=handoff("correction_requested", "Waylon"))
    state = delivery_decision(state, request, HUMAN)
    assert state["parent_run_id"] == "delegated-1" and state["basicops_task_id"] == "2199999"
    state, _ = project(state, "p5")
    state = chief_start(state, event("chief_of_staff", "restart-fix", 82491, handoff=handoff("executing", "Waylon")), CHIEF)
    state, _ = project(state, "p6")
    fixed = event("chief_of_staff", "fixed-1", 82491, correction_event_id="correct-1", fix_evidence=["basicops-message:green-readback"])
    state = correction_fixed(state, fixed, CHIEF)
    routed = event("learning_steward", "steward-1", 500, correction_event_id="correct-1", disposition="client_memory", promotion_status="not_applicable")
    state = steward_disposition(state, routed, STEWARD)
    assert state["correction_events"][0]["steward_status"] == "client_memory"


def test_replayed_lifecycle_event_is_safe_while_projection_is_pending():
    state, _ = project(initial(), "p0")
    posted = event("project_manager", "plan-replay", 82484, plan={"steps": ["Draft"]}, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval"))
    pending = post_plan(state, posted, PM)
    assert post_plan(pending, posted, PM) == pending


def test_capability_restored_resumes_same_parent_after_verified_cto_evidence():
    state, _ = approved_execution()
    base = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    state = heartbeat(state, event("chief_of_staff", "beat-cap", 82491, observed_at=base.isoformat(), expected_next_event="worker", next_check_at=base.isoformat(), deadline_at=(base + timedelta(hours=1)).isoformat()), CHIEF)
    state, _ = evaluate(state, now=(base + timedelta(minutes=1)).isoformat())
    state, _ = evaluate(state, now=(base + timedelta(minutes=17)).isoformat())
    state, _ = project(state, "cap-projection")
    restored = seal({"role": "cto", "event_id": "restore-1", "actor_user_id": "400", "parent_run_id": "delegated-1", "task_id": "2199999", "result": "capability_restored", "verification_evidence": ["incident:CII-1:passed"], "handoff": handoff("executing", "Waylon")}, b"cto")
    state = capability_restored(state, restored, b"cto")
    assert state["state"] == "executing" and state["basicops_task_id"] == "2199999"


def test_calls_made_are_disclosures_and_ordinary_choice_cannot_require_decision():
    state, _ = approved_execution()
    ordinary = {"question": "Which address?", "reason": "Footer differs", "consequence": "Draft CTA", "authority_required": "reversible_default"}
    with pytest.raises(ValueError, match="ordinary assumption"):
        review_ready(state, event("chief_of_staff", "ready", 82491, completion_evidence=["preview"], handoff=handoff("awaiting_delivery_review", "Aiya", "delivery_review", decisions=[ordinary])), CHIEF)
    consequential = {"question": "Publish now?", "reason": "Live mutation", "consequence": "Public release", "authority_required": "consequential"}
    state = review_ready(state, event("chief_of_staff", "ready-2", 82491, completion_evidence=["preview"], handoff=handoff("awaiting_delivery_review", "Aiya", "delivery_review", calls=[{"choice": "Used 123 Smith St", "location": "CTA", "release_state": "staging"}], decisions=[consequential])), CHIEF)
    assert state["handoff"]["calls_made"] and state["handoff"]["decision_required"]


def test_barney_is_silent_when_healthy_retries_once_then_routes_cto_without_human():
    state, _ = approved_execution()
    base = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    beat = event("chief_of_staff", "beat-1", 82491, observed_at=base.isoformat(), expected_next_event="worker result", next_check_at=(base + timedelta(minutes=5)).isoformat(), deadline_at=(base + timedelta(hours=1)).isoformat())
    state = heartbeat(state, beat, CHIEF)
    healthy, actions = evaluate(state, now=(base + timedelta(minutes=4)).isoformat())
    assert actions == [] and healthy["state"] == "executing"
    retried, actions = evaluate(healthy, now=(base + timedelta(minutes=6)).isoformat())
    assert actions == [{"action": "retry_silently", "idempotent": True, "human_notification": False}]
    routed, actions = evaluate(retried, now=(base + timedelta(minutes=22)).isoformat())
    assert routed["state"] == "waiting_on_capability" and routed["next_action_owner"] == ACTORS["cto"]
    assert actions[0]["action"] == "route_cto" and actions[0]["human_notification"] is False


def test_barney_deadline_alert_is_internal_clear_and_suppressed_until_material_change():
    state, _ = project(initial(), "p0")
    plan = {"steps": ["Draft"]}
    state = post_plan(state, event("project_manager", "plan", 82484, plan=plan, handoff=handoff("awaiting_plan_approval", "Aiya", "plan_approval")), PM)
    state, _ = project(state, "p1")
    base = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    state["heartbeat"] = {"observed_at": base.isoformat(), "expected_next_event": "plan approval", "next_check_at": base.isoformat(), "deadline_at": (base + timedelta(minutes=30)).isoformat()}
    alerted, actions = evaluate(state, now=base.isoformat())
    assert actions[0]["playful"] is True and actions[0]["client_facing"] is False
    assert set(actions[0]["required_content"]) == {"task", "consequence", "owner", "exact_next_action", "native_link"}
    unchanged, repeated = evaluate(alerted, now=(base + timedelta(minutes=1)).isoformat())
    assert repeated == [] and unchanged["monitor"]["reminder_ledger"] == alerted["monitor"]["reminder_ledger"]
    overdue, actions = evaluate(alerted, now=(base + timedelta(minutes=31)).isoformat())
    assert actions[0]["level"] == "overdue" and actions[0]["playful"] is False
    escalated, actions = evaluate(overdue, now=(base + timedelta(minutes=62)).isoformat())
    assert actions[0]["action"] == "escalate_internal_project_manager" and actions[0]["target_user_id"] == "82484"


def test_barney_voice_is_funny_before_deadline_and_plain_when_overdue():
    approaching = render_notification(task="Approve plan", consequence="Production cannot start", owner="Aiya", exact_next_action="Review plan v2", native_link="https://basicops.com/task/1", level="approaching")
    overdue = render_notification(task="Approve plan", consequence="Production is blocked", owner="Aiya", exact_next_action="Review plan v2", native_link="https://basicops.com/task/1", level="overdue")
    assert "Suit up" in approaching and "Challenge accepted" in approaching
    assert "Funny bit over" in overdue
    for message in (approaching, overdue):
        assert all(label in message for label in ("Task:", "Consequence:", "Owner:", "Do this now:", "BasicOps:"))


def test_new_progress_heartbeat_restores_one_safe_retry_budget():
    state, _ = approved_execution()
    base = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    state = heartbeat(state, event("chief_of_staff", "beat-reset-1", 82491, observed_at=base.isoformat(), expected_next_event="worker", next_check_at=base.isoformat(), deadline_at=(base + timedelta(hours=1)).isoformat()), CHIEF)
    state, actions = evaluate(state, now=(base + timedelta(minutes=1)).isoformat())
    assert state["monitor"]["retry_count"] == 1
    progressed = heartbeat(state, event("chief_of_staff", "beat-reset-2", 82491, observed_at=(base + timedelta(minutes=2)).isoformat(), expected_next_event="qa", next_check_at=(base + timedelta(minutes=3)).isoformat(), deadline_at=(base + timedelta(hours=1)).isoformat()), CHIEF)
    assert progressed["monitor"]["retry_count"] == 0


def test_store_cas_rejects_stale_checkpoint_and_survives_reload(tmp_path):
    store = DelegatedTaskStore(tmp_path)
    one = store.checkpoint(initial(), expected_generation=None)
    store.path("delegated-1").chmod(0o640)
    projected, _ = project(one, "p0")
    two = store.checkpoint(projected, expected_generation=1)
    assert store.path("delegated-1").stat().st_mode & 0o777 == 0o640
    with pytest.raises(ValueError, match="stale"):
        store.checkpoint(one, expected_generation=1)
    assert store.load("delegated-1") == two


def test_store_globally_rejects_duplicate_task_or_dedupe_key(tmp_path):
    store = DelegatedTaskStore(tmp_path)
    store.checkpoint(initial(), expected_generation=None)
    duplicate = copy.deepcopy(initial())
    duplicate["parent_run_id"] = "delegated-2"
    with pytest.raises(ValueError, match="already bound"):
        store.checkpoint(duplicate, expected_generation=None)


def test_plan_handoff_must_name_verified_human_approver():
    state, _ = project(initial(), "p0")
    plan = {"steps": ["Draft"]}
    wrong = event("project_manager", "wrong-plan-owner", 82484, plan=plan,
        handoff=handoff("awaiting_plan_approval", "Waylon", "plan_approval"))
    with pytest.raises(ValueError, match="verified human approver"):
        post_plan(state, wrong, PM)
