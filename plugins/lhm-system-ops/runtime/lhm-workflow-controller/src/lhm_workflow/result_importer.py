"""Root boundary importing isolated role results through current-state CAS."""
from __future__ import annotations
import json,os
from pathlib import Path
from .departmental_state import DepartmentalStateStore,authenticated,digest
from .department_snapshot import import_result
from .secureio import read_trusted
ROLE={"projection":("projection-results","projection.public.pem"),"hop":("hop-results","hop.public.pem")}
def process(path:Path,root:Path,role:str)->str:
 if role not in ROLE:raise ValueError("invalid result role")
 inbox=root/ROLE[role][0]
 if path.is_symlink() or path.parent.resolve()!=inbox.resolve() or not path.is_file():raise ValueError("unsafe result source")
 result=json.loads(read_trusted(path,root=inbox,uid=os.stat(inbox).st_uid));snapshot_hash=result.get("snapshot_sha256")
 matches=list((root/"snapshot-consumed").glob(f"*-{role}-{snapshot_hash}.json"))
 if len(matches)!=1:raise ValueError("result has no unique dispatch")
 dispatch=json.loads(read_trusted(matches[0],root=root/"snapshot-consumed",uid=os.stat(root/"snapshot-consumed").st_uid));parent=dispatch["parent_run_id"];store=DepartmentalStateStore(root/"departmental-parents");current=store.load(parent);public=root/"public"/ROLE[role][1]
 if not authenticated(result,public,f"{role}_producer"):raise ValueError("invalid role result signature")
 receipt_marker=root/"result-consumed"/f"{digest(result)}.json"
 if receipt_marker.exists():path.unlink(missing_ok=True);return "replayed"
 if current.get("generation")!=dispatch.get("generation"):
  applied=role=="projection" and any(a.get("projection_receipt") and digest(a["projection_receipt"])==digest(result.get("receipt")) for a in current["action_register"])
  if not applied:raise ValueError("stale result after checkpoint")
  from .snapshot_broker import atomic
  atomic(receipt_marker,{"parent_run_id":parent,"role":role,"result_sha256":digest(result)});path.unlink(missing_ok=True);return "recovered"
 updated=import_result(current,dispatch,result,root/"public"/"controller-dispatch.public.pem",public)
 store.checkpoint(updated,expected_generation=current["generation"])
 if os.environ.get("LHM_RESULT_IMPORTER_FAULT")=="after_checkpoint":raise RuntimeError("injected importer failure")
 from .snapshot_broker import atomic
 atomic(receipt_marker,{"parent_run_id":parent,"role":role,"result_sha256":digest(result)});path.unlink();return "imported"
def quarantine(path:Path,root:Path,reason:str):
 from .snapshot_broker import atomic
 atomic(root/"result-quarantine"/path.name,{"source":path.name,"reason":reason});path.unlink(missing_ok=True)
