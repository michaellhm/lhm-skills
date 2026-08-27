"""Policy-only business outcome watchdog for delegated tasks."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone

from .delegated_task import _set_projection, validate_state


def render_notification(*, task: str, consequence: str, owner: str, exact_next_action: str,
                        native_link: str, level: str) -> str:
    """Render an internal-only Barney Stinson reminder without hiding the operational facts."""
    fields = (task, consequence, owner, exact_next_action, native_link)
    if any(not isinstance(value, str) or not value.strip() for value in fields):
        raise ValueError("Barney reminder requires every operational field")
    if level == "approaching":
        opener = "Suit up — this task is about to become overdue. Challenge accepted?"
    elif level == "overdue":
        opener = "This task is overdue. Funny bit over; let’s get it moving."
    else:
        raise ValueError("invalid Barney reminder level")
    return "\n".join((
        opener,
        f"Task: {task}",
        f"Consequence: {consequence}",
        f"Owner: {owner}",
        f"Do this now: {exact_next_action}",
        f"BasicOps: {native_link}",
    ))


def _time(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value.replace("Z", "+00:00"))


def _handoff(state: dict, *, next_owner: str, action: str, trigger: str, remaining: list[str]) -> dict:
    return {
        "state": state["state"],
        "outcome_owner": "chief_of_staff",
        "next_action_owner": next_owner,
        "review_type": state["review_type"],
        "completed": [],
        "evidence": [],
        "remaining": remaining,
        "next_action": action,
        "resume_trigger": trigger,
        "completion_condition": state["completion_condition"],
        "calls_made": [],
        "decision_required": [],
        "notification_receipt": None,
    }


def evaluate(state: dict, *, now: str, approaching_minutes: int = 60, escalate_after_minutes: int = 30) -> tuple[dict, list[dict]]:
    """Return a new state and bounded actions; unchanged state yields no repeat alert."""
    updated = copy.deepcopy(validate_state(state))
    current = _time(now)
    if current is None or current.tzinfo is None:
        raise ValueError("monitor now must include timezone")
    if updated["projection_pending"] is not None or updated["state"] == "completed":
        return updated, []
    actions: list[dict] = []
    heartbeat = updated["heartbeat"]

    if updated["state"] in {"executing", "correction_requested"} and heartbeat:
        next_check = _time(heartbeat["next_check_at"])
        if next_check and current <= next_check:
            return updated, []
        if updated["monitor"]["retry_count"] == 0:
            updated["monitor"]["retry_count"] = 1
            heartbeat["next_check_at"] = (current + timedelta(minutes=15)).isoformat()
            actions.append({"action": "retry_silently", "idempotent": True, "human_notification": False})
            return validate_state(updated), actions
        updated.update(state="waiting_on_capability", next_action_owner=updated["actors"]["cto"], review_type="none")
        handoff = _handoff(
            updated,
            next_owner=updated["actors"]["cto"]["canonical_name"],
            action="Diagnose the persistent stall and return capability_restored evidence.",
            trigger="Verified capability_restored event resumes the saved parent.",
            remaining=[heartbeat["expected_next_event"]],
        )
        _set_projection(updated, handoff)
        actions.append({"action": "route_cto", "human_notification": False, "retry_count": 1})
        return validate_state(updated), actions

    if updated["state"] not in {"awaiting_plan_approval", "awaiting_delivery_review", "blocked"} or not heartbeat:
        return updated, []
    deadline = _time(heartbeat["deadline_at"])
    if deadline is None:
        return updated, []
    minutes = int((deadline - current).total_seconds() // 60)
    level = "overdue" if minutes < 0 else "approaching" if minutes <= approaching_minutes else None
    if level is None:
        return updated, []
    fingerprint = f"{updated['state']}:{level}:{deadline.isoformat()}:{updated['next_action_owner']['user_id']}"
    if updated["monitor"]["last_alert_fingerprint"] == fingerprint:
        if level == "overdue" and updated["monitor"]["overdue_escalated_at"] is None:
            first = next((item for item in reversed(updated["monitor"]["reminder_ledger"]) if item["fingerprint"] == fingerprint), None)
            if first and current >= _time(first["sent_at"]) + timedelta(minutes=escalate_after_minutes):
                updated["monitor"]["overdue_escalated_at"] = current.isoformat()
                actions.append({
                    "action": "escalate_internal_project_manager", "target_user_id": updated["actors"]["project_manager"]["user_id"],
                    "level": "persistent_overdue", "playful": False, "client_facing": False,
                    "required_content": ["task", "consequence", "owner", "exact_next_action", "native_link"],
                })
                return validate_state(updated), actions
        return updated, []
    updated["monitor"]["last_alert_fingerprint"] = fingerprint
    updated["monitor"]["reminder_ledger"].append({"fingerprint": fingerprint, "sent_at": current.isoformat(), "level": level})
    playful = level == "approaching"
    actions.append({
        "action": "notify_internal_owner",
        "target_user_id": updated["next_action_owner"]["user_id"],
        "level": level,
        "playful": playful,
        "client_facing": False,
        "required_content": ["task", "consequence", "owner", "exact_next_action", "native_link"],
    })
    return validate_state(updated), actions
