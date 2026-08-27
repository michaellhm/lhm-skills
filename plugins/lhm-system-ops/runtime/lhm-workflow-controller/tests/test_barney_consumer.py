import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import lhm_workflow.barney_consumer as consumer_module
from lhm_workflow.barney_consumer import BarneyConsumer, _message
from lhm_workflow.barney_monitor import evaluate
from lhm_workflow.controller import WorkflowController
from lhm_workflow.delegated_task import canonical, heartbeat
from test_delegated_task import CHIEF, approved_execution, event, project


def dispatch(root, state, route, action, identifier="barney-action-1"):
    request = {
        "schema_version": 1,
        "action_id": identifier,
        "parent_run_id": state["parent_run_id"],
        "state_generation": state["generation"],
        "action": action,
    }
    target = root / "barney-dispatch" / route / f"{identifier}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"schema_version": 1, "route": route, "request": request}))
    return target


def successful_adapter(calls):
    def run(argv, **kwargs):
        envelope = json.loads(kwargs["input"])
        calls.append(envelope)
        operation = envelope["argv"][1]
        verification = {
            "verification": "passed",
            "task_id": "2199999",
            "discussion_message_id": "msg-barney",
            "readback_observed_at": "2026-08-27T10:00:00+00:00",
        }
        if operation == "submit-basicops-task-baton-transition":
            verification.update(assignee_user_id=envelope["argv"][4], native_status=envelope["argv"][5], review_type=envelope["argv"][6])
        result = {"verification": verification}
        receipt = {
            "schema_version": 1,
            "operation": "claude_dispatch",
            "binding": envelope["binding"],
            "result": result,
            "receipt_sha256": hashlib.sha256(canonical(result)).hexdigest(),
        }
        return SimpleNamespace(returncode=0, stdout=json.dumps(receipt), stderr="")
    return run


def executing(ctl):
    state, _ = approved_execution()
    return ctl.delegated.checkpoint(state, expected_generation=None)


def test_notification_tone_is_playful_only_before_overdue(tmp_path):
    ctl = WorkflowController(tmp_path, test_mode=True)
    state = executing(ctl)
    approaching = _message(state, {"action": "notify_internal_owner", "level": "approaching"})
    overdue = _message(state, {"action": "notify_internal_owner", "level": "overdue"})
    assert "Suit up" in approaching and "Challenge accepted" in approaching
    assert "Funny bit over" in overdue and "Suit up" not in overdue and "Challenge accepted" not in overdue


def test_retry_wakes_chief_with_idempotent_baton_without_lifecycle_change(tmp_path, monkeypatch):
    ctl = WorkflowController(tmp_path, test_mode=True)
    state = executing(ctl)
    now = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    state = heartbeat(state, event("chief_of_staff", "beat-retry", 82491, observed_at=now.isoformat(), expected_next_event="worker result", next_check_at=(now + timedelta(minutes=15)).isoformat(), deadline_at=(now + timedelta(hours=1)).isoformat()), CHIEF)
    state = ctl.delegated.checkpoint(state, expected_generation=ctl.delegated.load(state["parent_run_id"])["generation"])
    before = copy.deepcopy(state)
    source = dispatch(tmp_path, state, "chief-of-staff", {"action": "retry_silently", "idempotent": True})
    calls = []
    monkeypatch.setattr(consumer_module.subprocess, "run", successful_adapter(calls))
    receipts = BarneyConsumer(tmp_path).consume(ctl.delegated)
    assert len(calls) == len(receipts) == 1
    argv = calls[0]["argv"]
    assert argv[1] == "submit-basicops-task-baton-transition"
    assert argv[4:7] == [state["next_action_owner"]["user_id"], "In Progress", state["review_type"]]
    assert ctl.delegated.load(state["parent_run_id"]) == before
    assert not source.exists()
    # A recovered duplicate is suppressed by the immutable downstream receipt.
    dispatch(tmp_path, state, "chief-of-staff", {"action": "retry_silently", "idempotent": True})
    BarneyConsumer(tmp_path).consume(ctl.delegated)
    assert len(calls) == 1


def test_cto_waits_for_verified_projection_then_adds_incident_discussion(tmp_path, monkeypatch):
    ctl = WorkflowController(tmp_path, test_mode=True)
    state = executing(ctl)
    now = datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc)
    state = heartbeat(state, event("chief_of_staff", "beat-cto", 82491, observed_at=now.isoformat(), expected_next_event="worker result", next_check_at=now.isoformat(), deadline_at=(now + timedelta(hours=1)).isoformat()), CHIEF)
    state, _ = evaluate(state, now=(now + timedelta(minutes=1)).isoformat())
    state, actions = evaluate(state, now=(now + timedelta(minutes=17)).isoformat())
    assert actions[0]["action"] == "route_cto" and state["projection_pending"] is not None
    state = ctl.delegated.checkpoint(state, expected_generation=ctl.delegated.load(state["parent_run_id"])["generation"])
    source = dispatch(tmp_path, state, "cto", actions[0])
    calls = []
    monkeypatch.setattr(consumer_module.subprocess, "run", successful_adapter(calls))
    assert BarneyConsumer(tmp_path).consume(ctl.delegated) == [] and source.exists() and calls == []
    projected, _ = project(state, "cto-projection")
    ctl.delegated.checkpoint(projected, expected_generation=state["generation"])
    receipts = BarneyConsumer(tmp_path).consume(ctl.delegated)
    assert len(receipts) == len(calls) == 1
    assert calls[0]["argv"][1] == "submit-basicops-task-discussion-update"
    assert "CTO owns capability diagnosis" in calls[0]["argv"][-1]


def test_adapter_crash_reconciles_inflight_with_idempotent_replay(tmp_path, monkeypatch):
    ctl = WorkflowController(tmp_path, test_mode=True)
    state = executing(ctl)
    source = dispatch(tmp_path, state, "basicops-notifications", {"action": "notify_internal_owner", "level": "approaching", "target_user_id": state["next_action_owner"]["user_id"]})
    calls = []
    def crash(*args, **kwargs):
        calls.append(json.loads(kwargs["input"]))
        raise RuntimeError("adapter crashed after an unknown external outcome")
    monkeypatch.setattr(consumer_module.subprocess, "run", crash)
    with pytest.raises(RuntimeError, match="unknown external outcome"):
        BarneyConsumer(tmp_path).consume(ctl.delegated)
    assert not source.exists() and (tmp_path / "barney-dispatch/inflight/barney-action-1.json").exists()
    assert not list((tmp_path / "barney-downstream-receipts").glob("*.json"))
    monkeypatch.setattr(consumer_module.subprocess, "run", successful_adapter(calls))
    receipts = BarneyConsumer(tmp_path).consume(ctl.delegated)
    assert len(calls) == 2 and len(receipts) == 1
    assert not (tmp_path / "barney-dispatch/inflight/barney-action-1.json").exists()
    assert (tmp_path / "barney-downstream-receipts/barney-action-1.json").exists()
