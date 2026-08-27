"""Durable human → PM → Chief of Staff delegated-task lifecycle."""
from __future__ import annotations

import copy
import fcntl
import hashlib
import hmac
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .departmental_state import authenticated as authenticated_attestation

SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
HEX = re.compile(r"^[0-9a-f]{64}$")
STATES = {
    "planning", "awaiting_plan_approval", "approved", "executing",
    "awaiting_delivery_review", "correction_requested", "completion_pending",
    "waiting_on_capability", "blocked", "on_hold", "completed",
}
NATIVE_STATUS = {
    "planning": "In Progress",
    "awaiting_plan_approval": "Under Review",
    "approved": "In Progress",
    "executing": "In Progress",
    "awaiting_delivery_review": "Under Review",
    "correction_requested": "In Progress",
    "completion_pending": "In Progress",
    "waiting_on_capability": "Blocked",
    "blocked": "Blocked",
    "on_hold": "On Hold",
    "completed": "Complete",
}
VERIFIED_BASICOPS_AI = {
    "project_manager": {"user_id": "82484", "canonical_name": "Monica AI", "workspace_id": "481630853364967730"},
    "chief_of_staff": {"user_id": "82491", "canonical_name": "Waylon", "workspace_id": "481630853364967730"},
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def seal(value: dict, key: bytes) -> dict:
    result = copy.deepcopy(value)
    result.pop("attestation", None)
    result["attestation"] = hmac.new(key, canonical(result), hashlib.sha256).hexdigest()
    return result


def authenticated(value: dict, key: bytes | Path, role: str) -> bool:
    return authenticated_attestation(value, key, role)


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not SAFE.fullmatch(value):
        raise ValueError(f"invalid {name}")
    return value


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {name}")
    return value.strip()


def _actor(value: object, name: str) -> dict:
    required = {"user_id", "canonical_name", "workspace_id", "verified_at"}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError(f"invalid {name} actor")
    _identifier(str(value["user_id"]), f"{name}.user_id")
    _text(value["canonical_name"], f"{name}.canonical_name")
    _identifier(str(value["workspace_id"]), f"{name}.workspace_id")
    _iso(value["verified_at"], f"{name}.verified_at")
    return copy.deepcopy(value)


def _iso(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"invalid {name}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid {name}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"invalid {name}")
    return value


def _handoff(value: object) -> dict:
    required = {
        "state", "outcome_owner", "next_action_owner", "review_type",
        "completed", "evidence", "remaining", "next_action", "resume_trigger",
        "completion_condition", "calls_made", "decision_required",
        "notification_receipt",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("invalid handoff")
    if value["review_type"] not in {"none", "plan_approval", "delivery_review"}:
        raise ValueError("invalid review type")
    for field in ("completed", "evidence", "remaining", "calls_made", "decision_required"):
        if not isinstance(value[field], list):
            raise ValueError(f"invalid handoff {field}")
    for field in ("state", "outcome_owner", "next_action_owner", "next_action", "resume_trigger", "completion_condition"):
        _text(value[field], f"handoff.{field}")
    # Calls made are disclosures. Ordinary reversible choices may not create a decision gate.
    for decision in value["decision_required"]:
        if not isinstance(decision, dict) or set(decision) != {"question", "reason", "consequence", "authority_required"}:
            raise ValueError("invalid decision required")
        if decision["authority_required"] not in {"consequential", "material_judgment", "protected_access", "conflict"}:
            raise ValueError("ordinary assumption cannot require a decision")
    receipt = value["notification_receipt"]
    if receipt is not None and (not isinstance(receipt, dict) or set(receipt) != {"channel", "message_id", "verified_at"}):
        raise ValueError("invalid notification receipt")
    return copy.deepcopy(value)


def _expected_projection(state: dict, *, discussion: dict) -> dict:
    review_type = state["review_type"]
    owner = state["next_action_owner"]
    return {
        "task_id": state["basicops_task_id"],
        "assignee_user_id": owner["user_id"],
        "native_status": NATIVE_STATUS[state["state"]],
        "review_type": review_type,
        "discussion_sha256": digest(discussion),
        "state_generation": state["generation"] + 1,
    }


def _set_projection(state: dict, handoff: dict) -> None:
    state["handoff"] = _handoff(handoff)
    state["projection_pending"] = _expected_projection(state, discussion=handoff)


def _require_projected(state: dict) -> None:
    if state["projection_pending"] is not None:
        raise ValueError("BasicOps projection must be verified before the next transition")


def validate_state(state: dict) -> dict:
    required = {
        "schema_version", "generation", "parent_run_id", "basicops_task_id", "basicops_target",
        "basicops_dedupe_key", "objective", "completion_condition", "permission_ceiling",
        "outcome_owner", "actors", "state", "next_action_owner", "review_type",
        "plan", "handoff", "projection_pending", "processed_event_ids", "processed_observation_ids",
        "projection_receipts", "correction_events", "heartbeat", "monitor", "completion_receipt",
    }
    if not isinstance(state, dict) or set(state) != required or state.get("schema_version") != 1:
        raise ValueError("invalid delegated task state")
    if not isinstance(state["generation"], int) or state["generation"] < 0:
        raise ValueError("invalid generation")
    _identifier(state["parent_run_id"], "parent_run_id")
    _identifier(str(state["basicops_task_id"]), "basicops_task_id")
    target = state["basicops_target"]
    if (not isinstance(target, dict) or set(target) != {"client_slug", "handback_task_id"}
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", target.get("client_slug", ""))
            or str(target.get("handback_task_id")) != state["basicops_task_id"]):
        raise ValueError("invalid BasicOps target binding")
    _identifier(state["basicops_dedupe_key"], "basicops_dedupe_key")
    _text(state["objective"], "objective")
    _text(state["completion_condition"], "completion_condition")
    if state["permission_ceiling"] not in {"green", "amber"}:
        raise ValueError("invalid permission ceiling")
    if state["outcome_owner"] != "chief_of_staff":
        raise ValueError("Chief of Staff must own the delegated outcome")
    if not isinstance(state["actors"], dict) or set(state["actors"]) != {"human", "project_manager", "chief_of_staff", "cto", "learning_steward"}:
        raise ValueError("invalid actor registry")
    actors = {name: _actor(actor, name) for name, actor in state["actors"].items()}
    for role, expected in VERIFIED_BASICOPS_AI.items():
        observed = actors[role]
        if any(str(observed[field]) != value for field, value in expected.items()):
            raise ValueError(f"{role} does not match verified BasicOps AI registry")
    if state["state"] not in STATES or state["review_type"] not in {"none", "plan_approval", "delivery_review"}:
        raise ValueError("invalid delegated state")
    expected_owner = {
        "planning": "project_manager", "awaiting_plan_approval": "human",
        "approved": "chief_of_staff", "executing": "chief_of_staff",
        "awaiting_delivery_review": "human", "correction_requested": "chief_of_staff",
        "completion_pending": "chief_of_staff", "waiting_on_capability": "cto",
        "blocked": "human", "on_hold": "human", "completed": "chief_of_staff",
    }[state["state"]]
    if state["next_action_owner"] != actors[expected_owner]:
        raise ValueError("next-action owner does not match state")
    expected_review = "plan_approval" if state["state"] == "awaiting_plan_approval" else "delivery_review" if state["state"] == "awaiting_delivery_review" else "none"
    if state["review_type"] != expected_review:
        raise ValueError("review type does not match state")
    plan = state["plan"]
    if not isinstance(plan, dict) or set(plan) != {"version", "material", "material_sha256", "approval_receipt", "superseded_versions"}:
        raise ValueError("invalid plan")
    if not isinstance(plan["version"], int) or plan["version"] < 0 or plan["material_sha256"] != digest(plan["material"]):
        raise ValueError("invalid plan binding")
    if not isinstance(plan["superseded_versions"], list):
        raise ValueError("invalid plan history")
    if plan["version"] == 0 and state["state"] != "planning":
        raise ValueError("plan required before baton can advance")
    if state["handoff"] is not None:
        handoff = _handoff(state["handoff"])
        if handoff["state"] != state["state"] or handoff["outcome_owner"] != "chief_of_staff":
            raise ValueError("handoff does not match delegated state")
        if handoff["next_action_owner"] != state["next_action_owner"]["canonical_name"]:
            raise ValueError("handoff next owner mismatch")
    pending = state["projection_pending"]
    if pending is not None:
        keys = {"task_id", "assignee_user_id", "native_status", "review_type", "discussion_sha256", "state_generation"}
        if not isinstance(pending, dict) or set(pending) != keys or pending["task_id"] != state["basicops_task_id"]:
            raise ValueError("invalid projection expectation")
        if pending["assignee_user_id"] != state["next_action_owner"]["user_id"] or pending["native_status"] != NATIVE_STATUS[state["state"]] or pending["review_type"] != state["review_type"]:
            raise ValueError("projection does not match baton state")
    if len(state["processed_event_ids"]) != len(set(state["processed_event_ids"])):
        raise ValueError("duplicate processed event")
    if (not isinstance(state["processed_observation_ids"], list)
            or len(state["processed_observation_ids"]) != len(set(state["processed_observation_ids"]))):
        raise ValueError("duplicate processed BasicOps observation")
    if not isinstance(state["projection_receipts"], list):
        raise ValueError("invalid projection receipts")
    if not isinstance(state["correction_events"], list):
        raise ValueError("invalid corrections")
    correction_required = {"event_id", "actor_user_id", "task_id", "parent_run_id", "old_value", "new_value", "source", "authority_scope", "affected_locations", "fix_receipt", "steward_status"}
    allowed_steward = {"waiting_for_fix", "pending", "client_memory", "related_artifacts", "project_evidence", "sop_proposal", "skill_proposal", "cto_improvement", "observe_again"}
    for correction in state["correction_events"]:
        if not isinstance(correction, dict) or not correction_required.issubset(correction) or correction["steward_status"] not in allowed_steward:
            raise ValueError("invalid correction state")
        if correction["steward_status"] != "waiting_for_fix" and correction["fix_receipt"] is None:
            raise ValueError("learning cannot precede correction fix")
    heartbeat = state["heartbeat"]
    if heartbeat is not None:
        if not isinstance(heartbeat, dict) or set(heartbeat) != {"observed_at", "expected_next_event", "next_check_at", "deadline_at"}:
            raise ValueError("invalid heartbeat")
        for key in ("observed_at", "next_check_at", "deadline_at"):
            if heartbeat[key] is not None:
                _iso(heartbeat[key], f"heartbeat.{key}")
    monitor = state["monitor"]
    if not isinstance(monitor, dict) or set(monitor) != {"retry_count", "last_alert_fingerprint", "reminder_ledger", "overdue_escalated_at"} or not isinstance(monitor["retry_count"], int) or not isinstance(monitor["reminder_ledger"], list):
        raise ValueError("invalid monitor state")
    if monitor["overdue_escalated_at"] is not None:
        _iso(monitor["overdue_escalated_at"], "monitor.overdue_escalated_at")
    if state["state"] == "completed" and state["completion_receipt"] is None:
        raise ValueError("completion requires Chief of Staff receipt")
    return state


def new_state(*, parent_run_id: str, basicops_task_id: str, basicops_dedupe_key: str,
              objective: str, completion_condition: str, permission_ceiling: str,
              actors: dict, initial_handoff: dict, basicops_target: dict) -> dict:
    actor_registry = {name: _actor(value, name) for name, value in actors.items()}
    for role, expected in VERIFIED_BASICOPS_AI.items():
        observed = actor_registry.get(role, {})
        if any(str(observed.get(field)) != value for field, value in expected.items()):
            raise ValueError(f"{role} does not match verified BasicOps AI registry")
    state = {
        "schema_version": 1,
        "generation": 0,
        "parent_run_id": _identifier(parent_run_id, "parent_run_id"),
        "basicops_task_id": _identifier(str(basicops_task_id), "basicops_task_id"),
        "basicops_target": copy.deepcopy(basicops_target),
        "basicops_dedupe_key": _identifier(basicops_dedupe_key, "basicops_dedupe_key"),
        "objective": _text(objective, "objective"),
        "completion_condition": _text(completion_condition, "completion_condition"),
        "permission_ceiling": permission_ceiling,
        "outcome_owner": "chief_of_staff",
        "actors": actor_registry,
        "state": "planning",
        "next_action_owner": actor_registry["project_manager"],
        "review_type": "none",
        "plan": {"version": 0, "material": {}, "material_sha256": digest({}), "approval_receipt": None, "superseded_versions": []},
        "handoff": None,
        "projection_pending": None,
        "processed_event_ids": [],
        "processed_observation_ids": [],
        "projection_receipts": [],
        "correction_events": [],
        "heartbeat": None,
        "monitor": {"retry_count": 0, "last_alert_fingerprint": None, "reminder_ledger": [], "overdue_escalated_at": None},
        "completion_receipt": None,
    }
    _set_projection(state, initial_handoff)
    return validate_state(state)


def _consume(state: dict, event: dict, key: bytes, role: str) -> tuple[dict, bool]:
    updated = copy.deepcopy(validate_state(state))
    event_id = _identifier(event.get("event_id"), "event_id")
    if event_id in updated["processed_event_ids"]:
        return updated, True
    if not authenticated(event, key, role):
        raise ValueError(f"invalid {role} event")
    if event.get("parent_run_id") != updated["parent_run_id"] or str(event.get("task_id")) != updated["basicops_task_id"]:
        raise ValueError("event binding mismatch")
    actor_name = {
        "project_manager": "project_manager", "chief_of_staff": "chief_of_staff",
        "human_approver": "human", "human_reviewer": "human",
        "learning_steward": "learning_steward", "cto": "cto",
    }.get(role)
    if actor_name and str(event.get("actor_user_id")) != str(updated["actors"][actor_name]["user_id"]):
        raise ValueError("event actor does not match verified registry")
    observation = event.get("basicops_observation")
    if role in {"human_approver", "human_reviewer"} or observation is not None:
        required = {"message_id", "author_user_id", "task_id", "task_revision", "observed_at", "body_sha256"}
        if not isinstance(observation, dict) or set(observation) != required:
            raise ValueError("human decision requires exact BasicOps observation")
        _identifier(str(observation["message_id"]), "basicops_observation.message_id")
        _identifier(str(observation["task_revision"]), "basicops_observation.task_revision")
        _iso(observation["observed_at"], "basicops_observation.observed_at")
        if (str(observation["author_user_id"]) != str(event["actor_user_id"])
                or str(observation["task_id"]) != updated["basicops_task_id"]
                or not isinstance(observation["body_sha256"], str)
                or not HEX.fullmatch(observation["body_sha256"])):
            raise ValueError("BasicOps observation binding mismatch")
        observation_id = digest({key: str(observation[key]) for key in
            ("task_id", "message_id", "task_revision", "body_sha256")})
        if observation_id in updated["processed_observation_ids"]:
            raise ValueError("BasicOps observation already consumed")
        updated["processed_observation_ids"].append(observation_id)
    updated["processed_event_ids"].append(event_id)
    return updated, False


def post_plan(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "project_manager")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] not in {"planning"}:
        raise ValueError("plan cannot be posted in current state")
    material = event.get("plan")
    if not isinstance(material, dict) or not material:
        raise ValueError("invalid plan material")
    if event.get("handoff", {}).get("next_action_owner") != updated["actors"]["human"]["canonical_name"]:
        raise ValueError("plan handoff must name the verified human approver")
    previous = updated["plan"]
    if previous["version"]:
        previous_record = {"version": previous["version"], "material_sha256": previous["material_sha256"], "approval_receipt": previous["approval_receipt"]}
        previous["superseded_versions"].append(previous_record)
    previous.update(version=previous["version"] + 1, material=copy.deepcopy(material), material_sha256=digest(material), approval_receipt=None)
    updated.update(state="awaiting_plan_approval", next_action_owner=updated["actors"]["human"], review_type="plan_approval")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def plan_decision(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "human_approver")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "awaiting_plan_approval":
        raise ValueError("plan is not awaiting approval")
    plan = updated["plan"]
    if (event.get("plan_version"), event.get("plan_sha256")) != (plan["version"], plan["material_sha256"]):
        raise ValueError("stale or mismatched plan decision")
    decision = event.get("decision")
    if decision == "approved":
        plan["approval_receipt"] = copy.deepcopy(event)
        updated.update(state="approved", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none")
    elif decision == "changes_requested":
        updated.update(state="planning", next_action_owner=updated["actors"]["project_manager"], review_type="none")
    else:
        raise ValueError("invalid plan decision")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def chief_start(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "chief_of_staff")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] not in {"approved", "correction_requested"} or updated["plan"]["approval_receipt"] is None:
        raise ValueError("approved plan required before execution")
    updated.update(state="executing", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def review_ready(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "chief_of_staff")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "executing":
        raise ValueError("delivery is not executing")
    evidence = event.get("completion_evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("delivery review requires evidence")
    pending_corrections = [item for item in updated["correction_events"] if item["fix_receipt"] is None]
    if pending_corrections:
        raise ValueError("correction fix must be verified before delivery review")
    updated.update(state="awaiting_delivery_review", next_action_owner=updated["actors"]["human"], review_type="delivery_review")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def delivery_decision(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "human_reviewer")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "awaiting_delivery_review":
        raise ValueError("delivery is not awaiting review")
    decision = event.get("decision")
    if decision == "accepted":
        updated.update(state="completion_pending", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none")
    elif decision == "correction_requested":
        correction = event.get("correction")
        required = {"old_value", "new_value", "source", "authority_scope", "affected_locations"}
        if not isinstance(correction, dict) or set(correction) != required or not isinstance(correction["affected_locations"], list) or not correction["affected_locations"]:
            raise ValueError("invalid correction event")
        for field in ("old_value", "new_value", "source", "authority_scope"):
            _text(correction[field], f"correction.{field}")
        if correction["old_value"] == correction["new_value"] or any(not isinstance(item, str) or not item.strip() for item in correction["affected_locations"]):
            raise ValueError("invalid correction event")
        updated["correction_events"].append({
            "event_id": event["event_id"], "actor_user_id": event["actor_user_id"],
            "task_id": updated["basicops_task_id"], "parent_run_id": updated["parent_run_id"],
            **copy.deepcopy(correction), "fix_receipt": None, "steward_status": "waiting_for_fix",
        })
        updated.update(state="correction_requested", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none")
    else:
        raise ValueError("invalid delivery decision")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def chief_complete(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "chief_of_staff")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "completion_pending" or event.get("decision") != "completed":
        raise ValueError("human acceptance and Chief of Staff completion required")
    checks = event.get("completion_checks")
    if not isinstance(checks, list) or updated["completion_condition"] not in checks:
        raise ValueError("completion condition not verified")
    updated["completion_receipt"] = copy.deepcopy(event)
    updated.update(state="completed", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none")
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def steward_disposition(state: dict, event: dict, key: bytes) -> dict:
    """Route a correction after the bounded current-work fix; never delays that fix."""
    updated, replay = _consume(state, event, key, "learning_steward")
    if replay:
        return updated
    _require_projected(updated)
    correction_id = event.get("correction_event_id")
    correction = next((item for item in updated["correction_events"] if item["event_id"] == correction_id), None)
    if correction is None or correction["steward_status"] != "pending" or correction["fix_receipt"] is None:
        raise ValueError("unknown or already-routed correction")
    disposition = event.get("disposition")
    allowed = {"client_memory", "related_artifacts", "project_evidence", "sop_proposal", "skill_proposal", "cto_improvement", "observe_again"}
    if disposition not in allowed:
        raise ValueError("invalid learning disposition")
    if disposition in {"sop_proposal", "skill_proposal"} and event.get("promotion_status") != "proposed_for_review":
        raise ValueError("general rule changes require review")
    correction["steward_status"] = disposition
    correction["steward_receipt"] = copy.deepcopy(event)
    return validate_state(updated)


def heartbeat(state: dict, event: dict, key: bytes) -> dict:
    updated, replay = _consume(state, event, key, "chief_of_staff")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] not in {"executing", "correction_requested"}:
        raise ValueError("heartbeat only valid during active execution")
    updated["heartbeat"] = {
        "observed_at": _iso(event.get("observed_at"), "observed_at"),
        "expected_next_event": _text(event.get("expected_next_event"), "expected_next_event"),
        "next_check_at": _iso(event.get("next_check_at"), "next_check_at"),
        "deadline_at": _iso(event.get("deadline_at"), "deadline_at") if event.get("deadline_at") else None,
    }
    updated["monitor"]["retry_count"] = 0
    return validate_state(updated)


def correction_fixed(state: dict, event: dict, key: bytes) -> dict:
    """Prove the current delivery was fixed before Learning Steward may generalise it."""
    updated, replay = _consume(state, event, key, "chief_of_staff")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "executing":
        raise ValueError("correction fix is only valid during resumed execution")
    correction = next((item for item in updated["correction_events"] if item["event_id"] == event.get("correction_event_id")), None)
    evidence = event.get("fix_evidence")
    if correction is None or correction["fix_receipt"] is not None or not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("invalid correction fix receipt")
    correction["fix_receipt"] = copy.deepcopy(event)
    correction["steward_status"] = "pending"
    return validate_state(updated)


def capability_restored(state: dict, event: dict, key: bytes) -> dict:
    """Resume the same parent only after CTO provides verified repair evidence."""
    updated, replay = _consume(state, event, key, "cto")
    if replay:
        return updated
    _require_projected(updated)
    if updated["state"] != "waiting_on_capability":
        raise ValueError("task is not waiting on capability")
    evidence = event.get("verification_evidence")
    if event.get("result") != "capability_restored" or not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise ValueError("verified capability restoration required")
    updated.update(state="executing", next_action_owner=updated["actors"]["chief_of_staff"], review_type="none", heartbeat=None)
    updated["monitor"]["retry_count"] = 0
    _set_projection(updated, event["handoff"])
    return validate_state(updated)


def record_projection(state: dict, receipt: dict, key: bytes) -> dict:
    updated = copy.deepcopy(validate_state(state))
    expected = updated["projection_pending"]
    if expected is None:
        if any(item.get("event_id") == receipt.get("event_id") and item == receipt for item in updated["projection_receipts"]):
            return updated
        raise ValueError("no BasicOps projection pending")
    if not authenticated(receipt, key, "basicops_connector"):
        raise ValueError("invalid BasicOps projection receipt")
    required = {"schema_version", "role", "event_id", "parent_run_id", "projection", "readback", "mutation", "attestation"}
    if set(receipt) != required or receipt["parent_run_id"] != updated["parent_run_id"]:
        raise ValueError("invalid BasicOps receipt fields")
    if receipt["projection"] != expected or receipt["readback"] != expected:
        raise ValueError("BasicOps assignment/status/discussion readback mismatch")
    mutation = receipt["mutation"]
    mutation_required = {"task_revision_before", "task_revision_after", "discussion_message_id", "task_url", "readback_observed_at"}
    if not isinstance(mutation, dict) or set(mutation) != mutation_required:
        raise ValueError("invalid BasicOps mutation evidence")
    for field in mutation_required:
        _text(str(mutation[field]), f"projection.mutation.{field}")
    _iso(mutation["readback_observed_at"], "projection.mutation.readback_observed_at")
    event_id = _identifier(receipt["event_id"], "projection.event_id")
    marker = f"projection:{event_id}"
    if marker in updated["processed_event_ids"]:
        return updated
    updated["processed_event_ids"].append(marker)
    updated["projection_receipts"].append(copy.deepcopy(receipt))
    updated["projection_pending"] = None
    return validate_state(updated)


class DelegatedTaskStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, parent_run_id: str) -> Path:
        return self.root / f"{_identifier(parent_run_id, 'parent_run_id')}.json"

    @contextmanager
    def global_lock(self):
        handle = (self.root / ".global.lock").open("a+b")
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
            handle.close()

    @contextmanager
    def lock(self, parent_run_id: str):
        handle = (self.root / f".{_identifier(parent_run_id, 'parent_run_id')}.lock").open("a+b")
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
            handle.close()

    def load(self, parent_run_id: str) -> dict:
        return validate_state(json.loads(self.path(parent_run_id).read_text()))

    def checkpoint(self, state: dict, *, expected_generation: int | None) -> dict:
        value = copy.deepcopy(state)
        validate_state(value)
        path = self.path(value["parent_run_id"])
        with self.global_lock(), self.lock(value["parent_run_id"]):
            old = self.load(value["parent_run_id"]) if path.exists() else None
            observed = None if old is None else old["generation"]
            if observed != expected_generation:
                raise ValueError("stale delegated-task checkpoint")
            if old is None:
                for candidate in self.root.glob("*.json"):
                    existing = self.load(candidate.stem)
                    if existing["parent_run_id"] != value["parent_run_id"] and (
                        existing["basicops_dedupe_key"] == value["basicops_dedupe_key"]
                        or existing["basicops_task_id"] == value["basicops_task_id"]
                    ):
                        raise ValueError("delegated task or dedupe key already bound to another parent")
            value["generation"] = 1 if observed is None else observed + 1
            existing_stat = path.stat() if path.exists() else None
            fd, temporary = tempfile.mkstemp(dir=self.root, prefix=f".{path.name}.")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(canonical(value) + b"\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                    if existing_stat is not None:
                        temporary_stat = os.fstat(handle.fileno())
                        if (temporary_stat.st_uid, temporary_stat.st_gid) != (existing_stat.st_uid, existing_stat.st_gid):
                            os.fchown(handle.fileno(), existing_stat.st_uid, existing_stat.st_gid)
                os.chmod(temporary, (existing_stat.st_mode & 0o777) if existing_stat is not None else 0o600)
                os.replace(temporary, path)
                directory = os.open(self.root, os.O_RDONLY)
                os.fsync(directory)
                os.close(directory)
            finally:
                Path(temporary).unlink(missing_ok=True)
            observed_value = self.load(value["parent_run_id"])
            if digest(observed_value) != digest(value):
                raise IOError("delegated-task state readback mismatch")
            return observed_value
