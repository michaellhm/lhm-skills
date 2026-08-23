"""Controller-signed snapshot dispatch and role-signed CAS result import."""
from __future__ import annotations
import copy,hashlib,json,os,tempfile
from pathlib import Path
from .departmental_state import authenticated,digest,seal_ed25519,validate_state,record_projection,accept_completion_dossier
ROLES={"projection","hop"}
def snapshot(state:dict,role:str)->dict:
 validate_state(state)
 if role not in ROLES:raise ValueError("invalid snapshot role")
 return {"schema_version":1,"role":role,"parent_run_id":state["parent_run_id"],"generation":state["generation"],"state_sha256":digest(state),"state_record":copy.deepcopy(state)}
def issue(state:dict,role:str,private_key:Path)->dict:
 snap=snapshot(state,role);body={"schema_version":1,"role":"controller_dispatch","target_role":role,"parent_run_id":state["parent_run_id"],"generation":state["generation"],"state_sha256":digest(state),"snapshot_sha256":digest(snap),"snapshot":snap};return seal_ed25519(body,private_key)
def verify_dispatch(value:dict,role:str,public_key:Path)->dict:
 keys={"schema_version","role","target_role","parent_run_id","generation","state_sha256","snapshot_sha256","snapshot","attestation"}
 if not isinstance(value,dict) or set(value)!=keys or value["target_role"]!=role or not authenticated(value,public_key,"controller_dispatch") or value["snapshot_sha256"]!=digest(value["snapshot"]):raise ValueError("invalid controller snapshot")
 return copy.deepcopy(value["snapshot"])
def import_result(current:dict,dispatch:dict,result:dict,controller_public:Path,role_public:Path,projection_key=None,hop_key=None):
 validate_state(current);role=dispatch.get("target_role")
 if not authenticated(dispatch,controller_public,"controller_dispatch"):raise ValueError("untrusted dispatch")
 if (dispatch["parent_run_id"],dispatch["generation"],dispatch["state_sha256"])!=(current["parent_run_id"],current["generation"],digest(current)):raise ValueError("stale snapshot result")
 if result.get("snapshot_sha256")!=dispatch["snapshot_sha256"] or not authenticated(result,role_public,f"{role}_producer"):raise ValueError("invalid producer result")
 payload=result.get("receipt")
 if role=="projection":
  action=next(a for a in current["action_register"] if a["status"]=="lead_accepted");return record_projection(current,action["contract"],payload,projection_key or role_public)
 if role=="hop":return accept_completion_dossier(current,payload,hop_key or role_public)
 raise ValueError("invalid result role")
def atomic_dispatch(value:dict,queue:Path)->Path:
 name=f'{value["parent_run_id"]}-{value["target_role"]}-{value["snapshot_sha256"]}.json';path=queue/name;queue.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=queue,prefix=f".{name}.")
 try:
  with os.fdopen(fd,"wb") as h:h.write(json.dumps(value,sort_keys=True,separators=(",",":")).encode()+b"\n");h.flush();os.fsync(h.fileno())
  os.chmod(tmp,0o440);os.replace(tmp,path);d=os.open(queue,os.O_RDONLY);os.fsync(d);os.close(d)
 finally:Path(tmp).unlink(missing_ok=True)
 return path
