"""Independent adapter translation for delegated BasicOps projections and human decisions."""
from __future__ import annotations

import copy
from pathlib import Path

from .departmental_state import seal_ed25519
from .delegated_task import HEX, _identifier, _iso, digest, validate_state


def projection_receipt(state: dict, observation: dict, private_key: Path) -> dict:
    """Translate an independently read BasicOps task/message observation into a signed receipt."""
    current = validate_state(copy.deepcopy(state))
    expected = current["projection_pending"]
    if expected is None:
        raise ValueError("no delegated projection pending")
    required = {
        "event_id", "task_id", "assignee_user_id", "native_status", "review_type",
        "discussion_message_id", "discussion_body_sha256", "task_revision_before",
        "task_revision_after", "task_url", "readback_observed_at", "verification",
    }
    if not isinstance(observation, dict) or set(observation) != required or observation["verification"] != "passed":
        raise ValueError("invalid BasicOps projection observation")
    observed_projection = {
        "task_id": str(observation["task_id"]),
        "assignee_user_id": str(observation["assignee_user_id"]),
        "native_status": observation["native_status"],
        "review_type": observation["review_type"],
        "discussion_sha256": observation["discussion_body_sha256"],
        "state_generation": expected["state_generation"],
    }
    if observed_projection != expected or observation["discussion_body_sha256"] != digest(current["handoff"]):
        raise ValueError("BasicOps observation does not match pending projection")
    _iso(observation["readback_observed_at"], "readback_observed_at")
    body = {
        "schema_version": 1, "role": "basicops_connector",
        "event_id": _identifier(observation["event_id"], "event_id"),
        "parent_run_id": current["parent_run_id"], "projection": expected,
        "readback": observed_projection,
        "mutation": {
            "task_revision_before": str(observation["task_revision_before"]),
            "task_revision_after": str(observation["task_revision_after"]),
            "discussion_message_id": str(observation["discussion_message_id"]),
            "task_url": observation["task_url"],
            "readback_observed_at": observation["readback_observed_at"],
        },
    }
    return seal_ed25519(body, private_key)


def human_decision_event(state: dict, observation: dict, private_key: Path) -> dict:
    """Bind one real BasicOps message author/revision/body to the current approval or review gate."""
    current = validate_state(copy.deepcopy(state))
    required = {
        "event_id", "message_id", "author_user_id", "task_id", "task_revision",
        "observed_at", "body_sha256", "decision", "plan_version", "plan_sha256",
        "correction", "handoff", "verification",
    }
    if not isinstance(observation, dict) or set(observation) != required or observation["verification"] != "passed":
        raise ValueError("invalid BasicOps human observation")
    if (str(observation["task_id"]) != current["basicops_task_id"]
            or str(observation["author_user_id"]) != current["actors"]["human"]["user_id"]
            or not isinstance(observation["body_sha256"], str)
            or not HEX.fullmatch(observation["body_sha256"])):
        raise ValueError("human observation binding mismatch")
    role = "human_approver" if current["state"] == "awaiting_plan_approval" else "human_reviewer" if current["state"] == "awaiting_delivery_review" else None
    if role is None:
        raise ValueError("delegated task is not at a human decision gate")
    if role == "human_approver" and (observation["plan_version"], observation["plan_sha256"]) != (current["plan"]["version"], current["plan"]["material_sha256"]):
        raise ValueError("stale BasicOps plan decision")
    allowed = {"approved", "changes_requested"} if role == "human_approver" else {"accepted", "correction_requested"}
    if observation["decision"] not in allowed:
        raise ValueError("invalid observed human decision")
    body = {
        "role": role, "event_id": _identifier(observation["event_id"], "event_id"),
        "actor_user_id": str(observation["author_user_id"]),
        "parent_run_id": current["parent_run_id"], "task_id": current["basicops_task_id"],
        "decision": observation["decision"], "handoff": copy.deepcopy(observation["handoff"]),
        "basicops_observation": {
            "message_id": str(observation["message_id"]),
            "author_user_id": str(observation["author_user_id"]),
            "task_id": current["basicops_task_id"],
            "task_revision": str(observation["task_revision"]),
            "observed_at": _iso(observation["observed_at"], "observed_at"),
            "body_sha256": observation["body_sha256"],
        },
    }
    if role == "human_approver":
        body.update(plan_version=observation["plan_version"], plan_sha256=observation["plan_sha256"])
    elif observation["decision"] == "correction_requested":
        body["correction"] = copy.deepcopy(observation["correction"])
    return seal_ed25519(body, private_key)
