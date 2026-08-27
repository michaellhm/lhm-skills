"""Fail-closed queue contracts for delegated BasicOps projection and human observations."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .delegated_connector import human_decision_event, projection_receipt
from .departmental_state import seal_ed25519
from .delegated_task import _iso, canonical, digest, validate_state


def projection_dispatch_id(state: dict) -> str:
    current = validate_state(state)
    pending = current["projection_pending"]
    if pending is None:
        raise ValueError("no delegated projection pending")
    material = f"{current['parent_run_id']}:{pending['state_generation']}:{pending['discussion_sha256']}"
    return "delegated-projection-" + hashlib.sha256(material.encode()).hexdigest()[:32]


def validate_basicops_target(state: dict, registry: dict) -> dict:
    current = validate_state(state)
    target = current["basicops_target"]
    clients = registry.get("clients") if isinstance(registry, dict) else None
    entry = clients.get(target["client_slug"]) if isinstance(clients, dict) else None
    task_ids = entry.get("basicops_task_ids") if isinstance(entry, dict) else None
    if (not isinstance(task_ids, list)
            or target["handback_task_id"] not in {str(value) for value in task_ids}):
        raise ValueError("BasicOps target is not present in governed handback registry")
    return target


def projection_request(state: dict, registry: dict) -> dict:
    current = validate_state(state)
    target = validate_basicops_target(current, registry)
    expected = current["projection_pending"]
    if expected is None:
        raise ValueError("no delegated projection pending")
    return {
        "schema_version": 1,
        "dispatch_id": projection_dispatch_id(current),
        "parent_run_id": current["parent_run_id"],
        "client_slug": target["client_slug"],
        "task_id": target["handback_task_id"],
        "assignee_user_id": expected["assignee_user_id"],
        "native_status": expected["native_status"],
        "review_type": expected["review_type"],
        "discussion": canonical(current["handoff"]).decode(),
        "discussion_sha256": expected["discussion_sha256"],
        "state_generation": expected["state_generation"],
    }


def durable_put(directory: Path, name: str, value: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    payload = canonical(value) + b"\n"
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError("queue id already exists with different content")
        return path
    fd, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=directory)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        Path(temporary).unlink(missing_ok=True)
    if path.read_bytes() != payload:
        raise IOError("queue readback mismatch")
    return path


def signed_projection_import(state: dict, worker_result: dict, private_key: Path) -> dict:
    """Sign only the exact closed verification object returned by the readback worker."""
    if not isinstance(worker_result, dict) or set(worker_result) != {
        "verification", "event_id", "task_id", "assignee_user_id", "native_status",
        "review_type", "discussion_message_id", "discussion_body_sha256",
        "task_revision_before", "task_revision_after", "task_url",
        "readback_observed_at", "checks", "error",
    } or worker_result["verification"] != "passed" or not worker_result["checks"]:
        raise ValueError("invalid delegated BasicOps worker observation")
    observation = {key: value for key, value in worker_result.items() if key not in {"checks", "error"}}
    return projection_receipt(state, observation, private_key)


DECISION_PREFIX = "LHM decision:"
WORKFLOW_PREFIX = "LHM workflow event:"


def closed_decision_observation(state: dict, observed_message: dict, private_key: Path) -> dict:
    """Accept only an exact JSON marker; never infer a decision from prose."""
    required = {"message_id", "author_user_id", "task_id", "task_revision", "observed_at", "body"}
    if not isinstance(observed_message, dict) or set(observed_message) != required:
        raise ValueError("invalid BasicOps message observation")
    body = observed_message["body"]
    if not isinstance(body, str) or not body.startswith(DECISION_PREFIX):
        raise ValueError("message is not a closed LHM decision marker")
    try:
        marker = json.loads(body[len(DECISION_PREFIX):].strip())
    except json.JSONDecodeError as exc:
        raise ValueError("invalid LHM decision JSON") from exc
    marker_required = {"event_id", "decision", "plan_version", "plan_sha256", "correction", "handoff"}
    if not isinstance(marker, dict) or set(marker) != marker_required:
        raise ValueError("invalid LHM decision marker fields")
    observation = {
        **{key: observed_message[key] for key in required if key != "body"},
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        **marker,
        "verification": "passed",
    }
    return human_decision_event(state, observation, private_key)


WORKFLOW_OPERATIONS = {
    "post-plan": ("project_manager", {"event_id", "operation", "plan", "handoff"}),
    "chief-start": ("chief_of_staff", {"event_id", "operation", "handoff"}),
    "heartbeat": ("chief_of_staff", {"event_id", "operation", "observed_at", "expected_next_event", "next_check_at", "deadline_at"}),
    "review-ready": ("chief_of_staff", {"event_id", "operation", "completion_evidence", "handoff"}),
    "correction-fixed": ("chief_of_staff", {"event_id", "operation", "correction_event_id", "fix_evidence"}),
    "chief-complete": ("chief_of_staff", {"event_id", "operation", "decision", "completion_checks", "handoff"}),
    "steward-disposition": ("learning_steward", {"event_id", "operation", "correction_event_id", "disposition", "promotion_status"}),
    "capability-restored": ("cto", {"event_id", "operation", "result", "verification_evidence", "handoff"}),
}


def closed_workflow_observation(state: dict, observed_message: dict, private_key: Path) -> tuple[str, dict]:
    """Translate one exact AI workflow marker into an allowlisted signed controller event."""
    current = validate_state(state)
    required = {"message_id", "author_user_id", "task_id", "task_revision", "observed_at", "body"}
    if not isinstance(observed_message, dict) or set(observed_message) != required:
        raise ValueError("invalid BasicOps workflow observation")
    body = observed_message["body"]
    if not isinstance(body, str) or not body.startswith(WORKFLOW_PREFIX):
        raise ValueError("message is not a closed LHM workflow marker")
    try:
        marker = json.loads(body[len(WORKFLOW_PREFIX):].strip())
    except json.JSONDecodeError as exc:
        raise ValueError("invalid LHM workflow JSON") from exc
    operation = marker.get("operation") if isinstance(marker, dict) else None
    contract = WORKFLOW_OPERATIONS.get(operation)
    if contract is None or set(marker) != contract[1]:
        raise ValueError("invalid LHM workflow marker fields")
    actor_name = contract[0]
    actor = current["actors"][actor_name]
    if (str(observed_message["task_id"]) != current["basicops_task_id"]
            or str(observed_message["author_user_id"]) != actor["user_id"]):
        raise ValueError("workflow marker author or task mismatch")
    _iso(observed_message["observed_at"], "observed_at")
    observation = {
        "message_id": str(observed_message["message_id"]),
        "author_user_id": actor["user_id"],
        "task_id": current["basicops_task_id"],
        "task_revision": str(observed_message["task_revision"]),
        "observed_at": observed_message["observed_at"],
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
    }
    event = {key: value for key, value in marker.items() if key != "operation"}
    event.update({
        "role": actor_name, "actor_user_id": actor["user_id"],
        "parent_run_id": current["parent_run_id"], "task_id": current["basicops_task_id"],
        "basicops_observation": observation,
    })
    return operation, seal_ed25519(event, private_key)
