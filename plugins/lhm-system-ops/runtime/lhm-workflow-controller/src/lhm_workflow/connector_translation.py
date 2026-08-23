"""Compatibility boundary for closed, authenticated connector metadata only."""
from __future__ import annotations
import argparse,json,os,tempfile
from pathlib import Path
from .departmental_state import DepartmentalStateStore,authenticated,digest,seal_ed25519
from .secureio import read_trusted,UnsafeFile
FIELDS={"role","target_role","parent_run_id","action_id","action_version","source_run_id","skill_id","contract_sha256","result_sha256","artifact_sha256","artifact_id","delivery_parent_id","observed_at","attestation"}
def translate(request:dict,state:dict,source:dict,adapter_public,private_key)->dict:
 if set(request)!={"schema_version","parent_run_id","action_id","action_version","source_run_id","target_role"}:raise ValueError("invalid closed translation request")
 action=next((a for a in state["action_register"] if a["action_id"]==request["action_id"]),None)
 if action is None or (request["parent_run_id"],request["action_version"])!=(state["parent_run_id"],action["version"]):raise ValueError("translation binding mismatch")
 if set(source)!=FIELDS or not authenticated(source,adapter_public,"claude_connector_evidence"):raise ValueError("authenticated closed connector evidence required")
 checks=("target_role","parent_run_id","action_id","action_version","source_run_id")
 if any(source[k]!=request[k] for k in checks) or source["contract_sha256"]!=digest(action["contract"]):raise ValueError("closed connector binding mismatch")
 body={k:source[k] for k in FIELDS if k not in {"role","attestation"}};body.update({"schema_version":1,"role":"connector_metadata_translator","source_receipt_sha256":digest(source),"state_sha256":digest(state)})
 return seal_ed25519(body,private_key)
def _atomic(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=f".{path.name}.")
 try:
  with os.fdopen(fd,"w") as h:json.dump(value,h,sort_keys=True,separators=(",",":"));h.write("\n");h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o440);os.replace(tmp,path)
 finally:Path(tmp).unlink(missing_ok=True)
def main():
 p=argparse.ArgumentParser();p.add_argument("request",type=Path);p.add_argument("source",type=Path);p.add_argument("output",type=Path);p.add_argument("--request-root",type=Path,default=Path("/var/lib/lhm-workflow/department-connector-requests"));p.add_argument("--source-root",type=Path,default=Path("/var/lib/lhm-workflow/department-connector-results"));p.add_argument("--state-root",type=Path,default=Path("/var/lib/lhm-workflow/departmental-parents"));p.add_argument("--adapter-public",type=Path,default=Path("/var/lib/lhm-workflow/public/adapter.public.pem"));p.add_argument("--private-key",type=Path,default=Path("/var/lib/lhm-workflow/secrets/adapter.private.pem"));a=p.parse_args()
 try:request=json.loads(read_trusted(a.request,root=a.request_root,uid=os.stat(a.request_root).st_uid));source=json.loads(read_trusted(a.source,root=a.source_root,uid=os.stat(a.source_root).st_uid))
 except (UnsafeFile,json.JSONDecodeError) as exc:raise SystemExit(f"unsafe closed metadata: {exc}")
 state=DepartmentalStateStore(a.state_root).load(request.get("parent_run_id",""));_atomic(a.output,translate(request,state,source,a.adapter_public,a.private_key))
if __name__=="__main__":main()
