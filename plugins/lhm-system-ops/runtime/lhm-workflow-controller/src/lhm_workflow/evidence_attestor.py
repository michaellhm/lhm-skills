"""Attest closed connector metadata without copying captured content."""
from __future__ import annotations
import argparse,json,os,re,tempfile
from datetime import datetime,timezone
from pathlib import Path
from .departmental_state import DepartmentalStateStore,authenticated,digest,seal_ed25519
from .secureio import read_trusted,UnsafeFile

RUN=re.compile(r"^claude-(?:gdrive|basicops|skill)-[0-9]{8}-[0-9]{2}$")
IDENT=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ROLES={"qa":"qa_verifier","lead":"department_lead"}
SOURCE_FIELDS={"role","target_role","parent_run_id","action_id","action_version","source_run_id","skill_id","contract_sha256","result_sha256","artifact_sha256","artifact_id","delivery_parent_id","observed_at","attestation"}

def attest(request:dict,state:dict,source:dict,adapter_public,attestor_private,now:str|None=None)->dict:
 if set(request)!={"schema_version","target_role","parent_run_id","action_id","action_version","source_run_id"}:raise ValueError("invalid evidence attestation request")
 if request["target_role"] not in ROLES or not RUN.fullmatch(str(request["source_run_id"])):raise ValueError("invalid evidence target or run")
 action=next((a for a in state["action_register"] if a["action_id"]==request["action_id"]),None)
 if action is None or (request["parent_run_id"],request["action_version"])!=(state["parent_run_id"],action["version"]):raise ValueError("stale evidence request")
 if set(source)!=SOURCE_FIELDS or not authenticated(source,adapter_public,"claude_connector_evidence"):raise ValueError("authenticated connector evidence required")
 expected=(request["target_role"],request["parent_run_id"],request["action_id"],request["action_version"],request["source_run_id"],digest(action["contract"]))
 observed=(source["target_role"],source["parent_run_id"],source["action_id"],source["action_version"],source["source_run_id"],source["contract_sha256"])
 if observed!=expected:raise ValueError("connector evidence binding mismatch")
 if not IDENT.fullmatch(str(source["skill_id"])) or not IDENT.fullmatch(str(source["artifact_id"])) or not IDENT.fullmatch(str(source["delivery_parent_id"])):raise ValueError("invalid closed evidence identifier")
 for field in ("result_sha256","artifact_sha256"):
  if not re.fullmatch(r"[0-9a-f]{64}",str(source[field])):raise ValueError("invalid evidence hash")
 body={"schema_version":1,"role":"evidence_attestor","decision_role":ROLES[request["target_role"]],"parent_run_id":state["parent_run_id"],"action_id":action["action_id"],"action_version":action["version"],"state_sha256":digest(state),"contract_sha256":digest(action["contract"]),"source_run_id":source["source_run_id"],"skill_id":source["skill_id"],"result_sha256":source["result_sha256"],"artifact_sha256":source["artifact_sha256"],"artifact_id":source["artifact_id"],"delivery_parent_id":source["delivery_parent_id"],"source_receipt_sha256":digest(source),"observed_at":source["observed_at"],"attested_at":now or datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
 return seal_ed25519(body,attestor_private)

def _atomic(path:Path,value:dict):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=f".{path.name}.")
 try:
  with os.fdopen(fd,"w") as h:json.dump(value,h,sort_keys=True,separators=(",",":"));h.write("\n");h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o440);os.replace(tmp,path);d=os.open(path.parent,os.O_RDONLY);os.fsync(d);os.close(d)
 finally:Path(tmp).unlink(missing_ok=True)

def main():
 if os.geteuid()!=0:raise SystemExit("evidence attestor must run as root")
 p=argparse.ArgumentParser();p.add_argument("request",type=Path);p.add_argument("source",type=Path);p.add_argument("--request-root",type=Path,default=Path("/var/lib/lhm-workflow/evidence-attestor-requests"));p.add_argument("--source-root",type=Path,default=Path("/var/lib/lhm-workflow/department-connector-results"));p.add_argument("--state-root",type=Path,default=Path("/var/lib/lhm-workflow/departmental-parents"));p.add_argument("--adapter-public",type=Path,default=Path("/var/lib/lhm-workflow/public/adapter.public.pem"));p.add_argument("--private-key",type=Path,default=Path("/var/lib/lhm-workflow/secrets/evidence-attestor.private.pem"));p.add_argument("--qa-output",type=Path,default=Path("/var/lib/lhm-workflow/qa-requests/evidence.json"));p.add_argument("--lead-output",type=Path,default=Path("/var/lib/lhm-workflow/lead-requests/evidence.json"));a=p.parse_args()
 try:request=json.loads(read_trusted(a.request,root=a.request_root,uid=0));source=json.loads(read_trusted(a.source,root=a.source_root,uid=os.stat(a.source_root).st_uid))
 except (UnsafeFile,json.JSONDecodeError) as exc:raise SystemExit(f"unsafe evidence metadata: {exc}")
 state=DepartmentalStateStore(a.state_root).load(request.get("parent_run_id",""));receipt=attest(request,state,source,a.adapter_public,a.private_key);_atomic(a.qa_output if request["target_role"]=="qa" else a.lead_output,receipt);a.request.unlink()
if __name__=="__main__":main()
