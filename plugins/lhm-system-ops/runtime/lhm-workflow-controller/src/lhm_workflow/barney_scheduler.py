"""Durable scheduling and execution-receipt boundary for Barney actions."""
from __future__ import annotations
import hashlib, hmac, json, os, tempfile
from pathlib import Path
from .delegated_task import canonical

def _atomic(path, value, mode=0o600):
    path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as handle:handle.write(canonical(value)+b"\n");handle.flush();os.fsync(handle.fileno())
        os.chmod(tmp,mode);os.replace(tmp,path);directory=os.open(path.parent,os.O_RDONLY);os.fsync(directory);os.close(directory)
    finally:Path(tmp).unlink(missing_ok=True)

def action_id(parent_run_id,generation,action):
    return hashlib.sha256(canonical({"parent_run_id":parent_run_id,"state_generation":generation,"action":action})).hexdigest()

class BarneyScheduler:
    """Evaluate all parents and persist actions for a separately privileged executor."""
    def __init__(self,controller,root):
        self.controller=controller;self.root=Path(root);self.pending=self.root/"barney-actions/pending";self.receipts=self.root/"barney-actions/receipts";self.runs=self.root/"barney-actions/runs"
        for path in (self.pending,self.receipts,self.runs):path.mkdir(parents=True,exist_ok=True)
    def run(self,*,now,approaching_minutes=60):
        issued=[];checked=[]
        for parent_path in sorted(self.controller.delegated.root.glob("*.json")):
            parent_id=parent_path.stem;result=self.controller.delegated_transition(parent_id,"monitor",{"now":now,"approaching_minutes":approaching_minutes});state=result["state"]
            checked.append({"parent_run_id":parent_id,"generation":state["generation"],"state":state["state"]})
            for action in result["actions"]:
                identifier=action_id(parent_id,state["generation"],action);envelope={"schema_version":1,"action_id":identifier,"parent_run_id":parent_id,"basicops_task_id":state["basicops_task_id"],"state_generation":state["generation"],"issued_at":now,"action":action};target=self.pending/f"{identifier}.json"
                if (self.receipts/f"{identifier}.json").exists():continue
                if target.exists() and json.loads(target.read_text())!=envelope:raise ValueError("conflicting Barney action replay")
                if not target.exists():_atomic(target,envelope)
                issued.append(envelope)
        run_id=hashlib.sha256(canonical({"now":now,"checked":checked,"issued":[x["action_id"] for x in issued]})).hexdigest();run={"schema_version":1,"run_id":run_id,"observed_at":now,"checked":checked,"issued_action_ids":[x["action_id"] for x in issued]};path=self.runs/f"{run_id}.json"
        if not path.exists():_atomic(path,run,0o440)
        return run
    def record_receipt(self,receipt,key):
        required={"schema_version","role","action_id","parent_run_id","state_generation","disposition","evidence","executed_at","attestation"}
        if not isinstance(receipt,dict) or set(receipt)!=required or receipt.get("schema_version")!=1 or receipt.get("role")!="barney_action_executor":raise ValueError("invalid Barney action receipt")
        identifier=str(receipt.get("action_id",""));unsigned=dict(receipt);unsigned.pop("attestation");expected=hmac.new(key,canonical(unsigned),hashlib.sha256).hexdigest()
        if len(identifier)!=64 or not hmac.compare_digest(str(receipt.get("attestation")),expected):raise ValueError("invalid Barney action attestation")
        if receipt["disposition"] not in {"executed","failed","not_required"} or not isinstance(receipt["evidence"],list) or not receipt["evidence"]:raise ValueError("Barney execution requires evidence")
        target=self.receipts/f"{identifier}.json"
        if target.exists():
            existing=json.loads(target.read_text())
            if existing!=receipt:raise ValueError("conflicting Barney action receipt replay")
            return existing
        request_path=self.pending/f"{identifier}.json"
        if not request_path.is_file() or request_path.is_symlink():raise ValueError("unknown Barney action")
        request=json.loads(request_path.read_text())
        if (receipt["parent_run_id"],receipt["state_generation"])!=(request["parent_run_id"],request["state_generation"]):raise ValueError("stale Barney action receipt")
        _atomic(target,receipt,0o440);request_path.unlink();return json.loads(target.read_text())
