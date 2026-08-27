import hashlib, hmac, json, os, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from lhm_workflow.barney_scheduler import BarneyScheduler
from lhm_workflow.controller import WorkflowController
from lhm_workflow.delegated_task import canonical, heartbeat, seal
from test_delegated_task import ACTORS, CHIEF, PM, approved_execution, event, handoff, initial, post_plan, project


def waiting_for_plan(ctl):
    return ctl.delegated.checkpoint(initial(),expected_generation=None)


def test_scheduler_persists_idempotent_monitor_action_and_run_receipt(tmp_path):
    ctl=WorkflowController(tmp_path,test_mode=True);state,_=approved_execution();state=ctl.delegated.checkpoint(state,expected_generation=None)
    now=datetime(2026,8,27,10,0,tzinfo=timezone.utc)
    # Exercise an executing parent because its first stale check yields a silent retry.
    state=heartbeat(state,event("chief_of_staff","beat",82491,observed_at=now.isoformat(),expected_next_event="worker result",next_check_at=now.isoformat(),deadline_at=(now+timedelta(hours=1)).isoformat()),CHIEF)
    ctl.delegated.checkpoint(state,expected_generation=1)
    result=ctl.barney.run(now=(now+timedelta(minutes=1)).isoformat())
    assert len(result["issued_action_ids"])==1
    action_id=result["issued_action_ids"][0];request=json.loads((ctl.barney.pending/f"{action_id}.json").read_text())
    assert request["action"]["action"]=="retry_silently" and request["parent_run_id"]=="delegated-1"
    replay=ctl.barney.run(now=(now+timedelta(minutes=1)).isoformat())
    assert replay["issued_action_ids"]==[] and len(list(ctl.barney.pending.glob("*.json")))==1


def test_executor_receipt_is_authenticated_bound_and_replay_safe(tmp_path):
    ctl=WorkflowController(tmp_path,test_mode=True);state,_=project(initial(),"p0");state=post_plan(state,event("project_manager","plan",82484,plan={"steps":["Draft"]},handoff=handoff("awaiting_plan_approval","Aiya","plan_approval")),PM);state,_=project(state,"p1");ctl.delegated.checkpoint(state,expected_generation=None)
    now="2026-08-27T10:00:00+00:00";state=ctl.delegated.load("delegated-1")
    state["heartbeat"]={"observed_at":now,"expected_next_event":"plan approval","next_check_at":now,"deadline_at":"2026-08-27T10:30:00+00:00"}
    ctl.delegated.checkpoint(state,expected_generation=1)
    run=ctl.barney.run(now=now);identifier=run["issued_action_ids"][0];request=json.loads((ctl.barney.pending/f"{identifier}.json").read_text());key=(ctl.secrets/"barney-executor.key").read_bytes()
    unsigned={"schema_version":1,"role":"barney_action_executor","action_id":identifier,"parent_run_id":"delegated-1","state_generation":request["state_generation"],"disposition":"executed","evidence":["basicops-message:123"],"executed_at":now}
    receipt={**unsigned,"attestation":hmac.new(key,canonical(unsigned),hashlib.sha256).hexdigest()}
    assert ctl.barney.record_receipt(receipt,key)==receipt
    assert ctl.barney.record_receipt(receipt,key)==receipt
    assert not (ctl.barney.pending/f"{identifier}.json").exists()
    forged={**receipt,"evidence":["forged"]}
    with pytest.raises(ValueError,match="attestation"):ctl.barney.record_receipt(forged,key)


def test_timer_replay_and_executor_restart_do_not_duplicate_dispatch(tmp_path):
    ctl=WorkflowController(tmp_path,test_mode=True);state,_=approved_execution();state=ctl.delegated.checkpoint(state,expected_generation=None);now=datetime(2026,8,27,10,0,tzinfo=timezone.utc)
    state=heartbeat(state,event("chief_of_staff","beat-restart",82491,observed_at=now.isoformat(),expected_next_event="worker",next_check_at=now.isoformat(),deadline_at=(now+timedelta(hours=1)).isoformat()),CHIEF);ctl.delegated.checkpoint(state,expected_generation=1)
    run=ctl.barney.run(now=(now+timedelta(minutes=1)).isoformat());identifier=run["issued_action_ids"][0];request=(ctl.barney.pending/f"{identifier}.json").read_bytes()
    script=Path(__file__).parents[1]/"integration/lhm-barney-action-executor";env={**os.environ,"LHM_WORKFLOW_ROOT":str(tmp_path)}
    subprocess.run([sys.executable,str(script)],env=env,check=True)
    dispatches=list((tmp_path/"barney-dispatch/chief-of-staff").glob("*.json"));assert len(dispatches)==1
    (ctl.barney.pending/f"{identifier}.json").write_bytes(request)  # crash/restart replay after receipt commit
    subprocess.run([sys.executable,str(script)],env=env,check=True)
    assert len(list((tmp_path/"barney-dispatch/chief-of-staff").glob("*.json")))==1
    assert len(list(ctl.barney.receipts.glob("*.json")))==1 and not list(ctl.barney.pending.glob("*.json"))
