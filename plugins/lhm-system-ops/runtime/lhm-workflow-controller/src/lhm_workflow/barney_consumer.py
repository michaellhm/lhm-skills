"""Crash-safe downstream consumer for durably dispatched Barney actions."""
from __future__ import annotations
import hashlib, hmac, json, os, subprocess
from pathlib import Path
from .barney_monitor import render_notification
from .barney_scheduler import _atomic
from .delegated_task import NATIVE_STATUS, canonical, validate_state

ROUTES={"chief-of-staff","cto","basicops-notifications"}

def _task_url(state):
    for receipt in reversed(state["projection_receipts"]):
        value=receipt.get("mutation",{}).get("task_url")
        if isinstance(value,str) and value.startswith("https://"):return value
    raise ValueError("verified BasicOps task URL is unavailable")

def _message(state,action):
    kind=action["action"];owner=state["next_action_owner"]["canonical_name"];link=_task_url(state);task=state["objective"];next_action=state["handoff"]["next_action"]
    consequence=state["handoff"]["resume_trigger"]
    if kind=="notify_internal_owner":return render_notification(task=task,consequence=consequence,owner=owner,exact_next_action=next_action,native_link=link,level=action["level"])
    if kind=="escalate_internal_project_manager":return "\n".join(("Persistent overdue task — escalation required.",f"Task: {task}",f"Consequence: {consequence}",f"Owner: {owner}",f"Do this now: {next_action}",f"BasicOps: {link}"))
    if kind=="retry_silently":return f"Barney monitor: the expected event did not arrive. Re-waking {owner} once at the saved resume point. Expected next event: {state['heartbeat']['expected_next_event']}."
    if kind=="route_cto":return f"Barney monitor: one safe retry did not restore progress. CTO owns capability diagnosis; Chief of Staff retains the outcome. Resume trigger: {state['handoff']['resume_trigger']}"
    raise ValueError("unregistered Barney action")

def _verified_result(receipt,request,operation,state):
    if not isinstance(receipt,dict) or receipt.get("operation")!="claude_dispatch" or receipt.get("binding")!={"action_id":request["action_id"],"parent_run_id":request["parent_run_id"],"state_generation":request["state_generation"]}:raise ValueError("registered adapter binding mismatch")
    result=receipt.get("result");verification=result.get("verification") if isinstance(result,dict) else None
    if not isinstance(result,dict) or receipt.get("receipt_sha256") != hashlib.sha256(canonical(result)).hexdigest():raise ValueError("registered adapter receipt digest mismatch")
    if not isinstance(verification,dict) or verification.get("verification")!="passed" or str(verification.get("task_id"))!=state["basicops_task_id"] or not verification.get("discussion_message_id") or not verification.get("readback_observed_at"):raise ValueError("BasicOps discussion readback missing")
    if operation=="submit-basicops-task-baton-transition" and (str(verification.get("assignee_user_id")),verification.get("native_status"),verification.get("review_type"))!=(state["next_action_owner"]["user_id"],NATIVE_STATUS[state["state"]],state["review_type"]):raise ValueError("BasicOps baton readback mismatch")
    return verification

def _cto_assignment_verified(state):
    if state["state"]!="waiting_on_capability" or state["projection_pending"] is not None:return False
    return bool(state["projection_receipts"] and state["projection_receipts"][-1]["readback"]["assignee_user_id"]==state["actors"]["cto"]["user_id"] and state["projection_receipts"][-1]["readback"]["native_status"]=="Blocked")

def _route_is_current(route,state,action):
    if route=="chief-of-staff":
        return action["action"]=="retry_silently" and state["state"] in {"executing","correction_requested"} and state["next_action_owner"]["user_id"]==state["actors"]["chief_of_staff"]["user_id"] and state["heartbeat"] is not None
    if route=="cto":return action["action"]=="route_cto" and _cto_assignment_verified(state)
    if action["action"]=="notify_internal_owner":return action.get("target_user_id")==state["next_action_owner"]["user_id"]
    return action["action"]=="escalate_internal_project_manager" and action.get("target_user_id")==state["actors"]["project_manager"]["user_id"]

class BarneyConsumer:
    def __init__(self,root,adapter="/usr/local/libexec/lhm-workflow-registered-adapter",key_path=None):
        self.root=Path(root);self.adapter=adapter;self.key_path=Path(key_path or self.root/"secrets/barney-executor.key");self.inflight=self.root/"barney-dispatch/inflight";self.consumed=self.root/"barney-dispatch/consumed";self.receipts=self.root/"barney-downstream-receipts"
        for path in (self.inflight,self.consumed,self.receipts):path.mkdir(parents=True,exist_ok=True)
    def consume(self,state_store):
        done=[]
        # Inflight calls are deliberately replayed first. Both registered BasicOps
        # operations are closed and idempotent: the exact Discussion is created at
        # most once and the baton writes the same assignee/status values. This lets
        # an unknown post-call crash reconcile itself without duplicate user-visible
        # effects or a manual operator intervention.
        candidates=[]
        for claimed in sorted(self.inflight.glob("*.json")):
            dispatch=json.loads(claimed.read_text());candidates.append((dispatch["route"],claimed,True))
        for route in sorted(ROUTES):
            for source in sorted((self.root/"barney-dispatch"/route).glob("*.json")):
                candidates.append((route,source,False))
        for route,source,already_claimed in candidates:
            dispatch=json.loads(source.read_text());request=dispatch["request"];identifier=request["action_id"];receipt_path=self.receipts/f"{identifier}.json"
            if receipt_path.exists():source.unlink();done.append(json.loads(receipt_path.read_text()));continue
            state=validate_state(state_store.load(request["parent_run_id"]));action=request["action"]
            if request["state_generation"]>state["generation"]:raise ValueError("Barney action is ahead of governed state")
            if route=="cto" and not _cto_assignment_verified(state):continue
            if not _route_is_current(route,state,action):raise ValueError("Barney downstream route no longer matches governed state")
            message=_message(state,action);operation="submit-basicops-task-baton-transition" if route=="chief-of-staff" else "submit-basicops-task-discussion-update"
            claude="/opt/data/profiles/lhm_brain/bin/claude-dispatch";target=state["basicops_target"]
            argv=[claude,operation,target["client_slug"],target["handback_task_id"]]
            if operation.endswith("baton-transition"):argv += [state["next_action_owner"]["user_id"],NATIVE_STATUS[state["state"]],state["review_type"],message]
            else:argv += [message]
            envelope={"schema_version":1,"operation":"claude_dispatch","argv":argv,"binding":{"action_id":identifier,"parent_run_id":state["parent_run_id"],"state_generation":request["state_generation"]}}
            claimed=self.inflight/f"{identifier}.json"
            if not already_claimed:os.replace(source,claimed)
            result=subprocess.run([self.adapter],input=json.dumps(envelope),text=True,capture_output=True,timeout=620,check=False)
            if result.returncode:raise RuntimeError(result.stderr or result.stdout or "Barney BasicOps dispatch failed")
            adapter_receipt=json.loads(result.stdout);verification=_verified_result(adapter_receipt,request,operation,state)
            unsigned={"schema_version":1,"role":"barney_downstream_consumer","action_id":identifier,"parent_run_id":state["parent_run_id"],"state_generation":request["state_generation"],"route":route,"operation":operation,"message_sha256":hashlib.sha256(message.encode()).hexdigest(),"adapter_receipt_sha256":hashlib.sha256(canonical(adapter_receipt)).hexdigest(),"basicops_readback":verification}
            receipt={**unsigned,"attestation":hmac.new(self.key_path.read_bytes(),canonical(unsigned),hashlib.sha256).hexdigest()}
            _atomic(receipt_path,receipt,0o440);os.replace(claimed,self.consumed/claimed.name);done.append(receipt)
        return done
