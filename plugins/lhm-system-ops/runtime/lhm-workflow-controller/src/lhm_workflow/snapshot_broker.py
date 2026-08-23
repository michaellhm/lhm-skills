"""Root boundary from controller outgoing snapshots to isolated role inboxes."""
from __future__ import annotations
import hashlib,json,os,tempfile
from pathlib import Path
from .departmental_state import DepartmentalStateStore,authenticated,digest
from .secureio import read_trusted
ROLE_DIR={"projection":"projection-requests","hop":"hop-requests"}
def atomic(path,value,mode=0o440):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=f".{path.name}.")
 try:
  with os.fdopen(fd,"w") as h:json.dump(value,h,sort_keys=True,separators=(",",":"));h.write("\n");h.flush();os.fsync(h.fileno())
  os.chmod(tmp,mode);os.replace(tmp,path);d=os.open(path.parent,os.O_RDONLY);os.fsync(d);os.close(d)
 finally:Path(tmp).unlink(missing_ok=True)
def process(path:Path,root:Path,dispatch_public:Path)->str:
 outgoing=root/"controller-outgoing";quarantine=root/"snapshot-quarantine";consumed=root/"snapshot-consumed"
 if path.is_symlink() or path.parent.resolve()!=outgoing.resolve() or not path.is_file():raise ValueError("unsafe snapshot source")
 value=json.loads(read_trusted(path,root=outgoing,uid=os.stat(outgoing).st_uid));role=value.get("target_role")
 if role not in ROLE_DIR or not authenticated(value,dispatch_public,"controller_dispatch"):raise ValueError("invalid snapshot dispatch")
 state=DepartmentalStateStore(root/"departmental-parents").load(value["parent_run_id"])
 if (value.get("generation"),value.get("state_sha256"),value.get("snapshot_sha256"))!=(state["generation"],digest(state),digest(value.get("snapshot"))):raise ValueError("stale or tampered snapshot")
 name=f'{value["parent_run_id"]}-{role}-{value["snapshot_sha256"]}.json';target=root/ROLE_DIR[role]/name;marker=consumed/name
 if marker.exists():
  if json.loads(read_trusted(marker,root=consumed,uid=os.stat(consumed).st_uid))!=value:raise ValueError("conflicting snapshot replay")
  path.unlink(missing_ok=True);return "replayed"
 if target.exists():
  if target.is_symlink() or json.loads(read_trusted(target,root=target.parent,uid=os.stat(target.parent).st_uid))!=value:raise ValueError("role inbox collision")
  atomic(marker,value);path.unlink();return "recovered"
 atomic(target,value)
 if os.environ.get("LHM_SNAPSHOT_BROKER_FAULT")=="after_delivery":raise RuntimeError("injected broker failure")
 atomic(marker,value);path.unlink();return "delivered"
def quarantine(path:Path,root:Path,reason:str):
 q=root/"snapshot-quarantine"/path.name;atomic(q,{"source":path.name,"reason":reason});path.unlink(missing_ok=True)
