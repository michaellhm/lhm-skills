"""Controller-owned projection and HOP joins; no worker claims are accepted."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from .departmental_state import authenticated,digest,seal,seal_ed25519,validate_state
def _seal(value,key):return seal_ed25519(value,key) if isinstance(key,(str,Path)) else seal(value,key)
def projection(state:dict,basicops:dict,tracker:dict,adapter_key:bytes,projection_key:bytes)->dict:
 validate_state(state);action=next(a for a in state["action_register"] if a["status"]=="lead_accepted");c=action["contract"];e=c["dispatch_envelope"]
 if not authenticated(basicops,adapter_key,"basicops_connector") or (basicops["parent_run_id"],basicops["action_id"],basicops["action_version"])!=(state["parent_run_id"],action["action_id"],action["version"]):raise ValueError("BasicOps observation binding mismatch")
 if basicops["task_id"]!=e["basicops_task_id"] or basicops["discussion_sha256"]!=digest(e["discussion_payload"]):raise ValueError("BasicOps observation mismatch")
 if set(tracker)!={"tracker_path","previous_sha256","intended_post_sha256","observed_post_sha256","changed"}:raise ValueError("invalid tracker observation")
 path=Path(tracker["tracker_path"])
 if path.is_symlink() or not path.is_file():raise ValueError("unsafe tracker")
 observed=hashlib.sha256(path.read_bytes()).hexdigest()
 if not tracker["changed"] or tracker["previous_sha256"]==tracker["intended_post_sha256"]:raise ValueError("tracker write did not change content")
 if observed!=tracker["intended_post_sha256"] or observed!=tracker["observed_post_sha256"]:raise ValueError("tracker exact readback mismatch")
 return _seal({"schema_version":1,"role":"projection_writer","parent_run_id":state["parent_run_id"],"action_id":action["action_id"],"action_version":action["version"],"state_readback_sha256":digest(state),"tracker_path":str(path),"tracker_sha256":observed,"tracker_readback_sha256":observed,"basicops_task_id":basicops["task_id"],"basicops_dedupe_key":e["basicops_dedupe_key"],"basicops_comment_id":basicops["message_id"],"discussion_payload_sha256":basicops["discussion_sha256"],"no_subtasks":True,"basicops_readback_sha256":basicops["readback_sha256"]},projection_key)
def hop_dossier(state:dict,astro:dict,verifier_key:bytes,hop_key:bytes)->dict:
 validate_state(state)
 if state["state"]!="department_accepted" or not authenticated(astro,verifier_key,"astro_verifier"):raise ValueError("authenticated Astro return required")
 last=state["action_register"][-1]["dispatch_envelope"]
 if astro.get("seo_state_sha256")!=digest(state) or astro.get("return_role")!=last["return_role"] or astro.get("return_point")!=last["return_point"] or not isinstance(astro.get("receipt_sha256"),str) or len(astro["receipt_sha256"])!=64:raise ValueError("Astro return binding mismatch")
 body={"schema_version":1,"role":"head_of_production","parent_run_id":state["parent_run_id"],"department_state_sha256":digest(state),"seo_action_receipts":[digest(a["projection_receipt"]) for a in state["action_register"]],"astro_return_evidence":{"required":True,"receipt_sha256":astro["receipt_sha256"],"return_role":astro["return_role"],"return_point":astro["return_point"],"seo_state_sha256":astro["seo_state_sha256"]},"completion_checks":["all_seo_projections_accepted","authenticated_astro_return"],"decision":"accepted"}
 return _seal(body,hop_key)
