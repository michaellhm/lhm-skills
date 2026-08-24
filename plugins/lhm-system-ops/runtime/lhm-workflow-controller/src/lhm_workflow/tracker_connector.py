"""CAS write and exact readback boundary for the canonical SEO tracker."""
from __future__ import annotations
import hashlib
import os
import tempfile
import json
import re
from pathlib import Path

TRACKER_RELATIVE=Path("30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md")


def sha(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()


HEX=re.compile(r"^[0-9a-f]{64}$")
SAFE=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
RFC3339=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
class TrackerConnector:
    def __init__(self,vault:Path): self.vault=vault.absolute()
    @property
    def path(self): return self.vault/TRACKER_RELATIVE
    def _current(self):
        path=self.path
        current=Path(path.anchor)
        for part in path.parts[1:]:
            current=current/part
            if current.exists() and current.is_symlink(): raise ValueError("tracker ancestor cannot be linked")
        try: path.absolute().relative_to(self.vault)
        except ValueError as exc: raise ValueError("tracker escapes fixed vault") from exc
        return path.read_bytes() if path.exists() else b""
    def write(self,content:bytes,expected_previous_sha256:str):
        self._current()
        raise ValueError("arbitrary tracker narrative forbidden; structured accepted evidence required")
    def _write(self,content:bytes,expected_previous_sha256:str):
        old=self._current()
        if sha(old)!=expected_previous_sha256: raise ValueError("tracker CAS mismatch")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=self.path.parent,prefix=".rollout-state.")
        try:
            with os.fdopen(fd,"wb") as f: f.write(content); f.flush(); os.fsync(f.fileno())
            os.chmod(tmp,0o600); os.replace(tmp,self.path)
        finally: Path(tmp).unlink(missing_ok=True)
        return self.readback(sha(content))
    def readback(self,expected_sha256:str):
        raw=self._current(); observed=sha(raw)
        if observed!=expected_sha256: raise ValueError("tracker exact readback mismatch")
        return {"artifact_id":"seo-rollout-tracker","sha256":observed,"media_type":"text/markdown"},raw
    def append_structured(self,summary:dict,expected_previous_sha256:str):
        required={"parent_run_id","workflow_id","accepted_receipts","run_result","work_state","completed_at"}
        if not isinstance(summary,dict) or set(summary)!=required or summary["run_result"] not in {"succeeded","failed","needs_context"} or summary["work_state"] not in {"complete","needs_context","blocked"}:
            raise ValueError("invalid structured tracker summary")
        if (not SAFE.fullmatch(str(summary["parent_run_id"])) or not SAFE.fullmatch(str(summary["workflow_id"]))
                or not RFC3339.fullmatch(str(summary["completed_at"]))): raise ValueError("invalid structured tracker identifiers")
        receipts=summary["accepted_receipts"]
        if not isinstance(receipts,list) or not receipts: raise ValueError("accepted receipts required")
        rendered=self._render(summary)
        old=self._current(); body=old+(b"\n" if old and not old.endswith(b"\n") else b"")+rendered
        return self._write(body,expected_previous_sha256)
    def _render(self,summary:dict):
        required={"parent_run_id","workflow_id","accepted_receipts","run_result","work_state","completed_at"}
        if not isinstance(summary,dict) or set(summary)!=required or summary["run_result"] not in {"succeeded","failed","needs_context"} or summary["work_state"] not in {"complete","needs_context","blocked"}: raise ValueError("invalid structured tracker summary")
        if not SAFE.fullmatch(str(summary["parent_run_id"])) or not SAFE.fullmatch(str(summary["workflow_id"])) or not RFC3339.fullmatch(str(summary["completed_at"])): raise ValueError("invalid structured tracker identifiers")
        receipts=summary["accepted_receipts"]
        if not isinstance(receipts,list) or not receipts: raise ValueError("accepted receipts required")
        lines=[f"## Governed run {summary['parent_run_id']}",f"- Workflow: `{summary['workflow_id']}`",f"- Completed: `{summary['completed_at']}`",f"- Run result: `{summary['run_result']}`",f"- Work state: `{summary['work_state']}`","- Accepted receipts:"]
        for item in receipts:
            if (not isinstance(item,dict) or set(item)!={"stage_id","contract_sha256","artifact_sha256s"}
                    or not SAFE.fullmatch(str(item["stage_id"]))
                    or not HEX.fullmatch(str(item["contract_sha256"])) or not isinstance(item["artifact_sha256s"],list)
                    or not all(HEX.fullmatch(str(value)) for value in item["artifact_sha256s"])):
                raise ValueError("invalid accepted receipt summary")
            lines.append(f"  - `{item['stage_id']}` contract `{item['contract_sha256']}` artifacts `{','.join(item['artifact_sha256s'])}`")
        return ('\n'.join(lines)+'\n').encode()


def summary_from_parent(parent:dict,request:dict)->dict:
    """Derive receipt hashes from persisted Router state; stdin cannot supply them."""
    if set(request)!={"parent_run_id","run_result","work_state","completed_at"} or request["parent_run_id"]!=parent.get("parent_run_id"):
        raise ValueError("tracker request does not bind persisted parent")
    accepted=[]
    for stage in parent.get("stages",[]):
        if stage.get("status")!="accepted": continue
        outputs=stage.get("outputs")
        if not isinstance(outputs,list) or not all(isinstance(item,dict) and HEX.fullmatch(str(item.get("sha256",""))) for item in outputs):
            raise ValueError("persisted accepted output invalid")
        if not HEX.fullmatch(str(stage.get("contract_sha256",""))): raise ValueError("persisted accepted contract invalid")
        accepted.append({"stage_id":stage["stage_id"],"contract_sha256":stage["contract_sha256"],"artifact_sha256s":[item["sha256"] for item in outputs]})
    if not accepted: raise ValueError("persisted parent has no accepted receipts")
    return {**request,"workflow_id":parent["workflow_id"],"accepted_receipts":accepted}
