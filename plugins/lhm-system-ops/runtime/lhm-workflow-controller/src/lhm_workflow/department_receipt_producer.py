"""Produce bounded departmental receipts from controller-observed state only."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from .departmental_state import DepartmentalStateStore,authenticated,digest,seal,seal_ed25519
from .secureio import read_trusted,UnsafeFile

def produce(request:dict,state:dict,key,claude_public,evidence:dict,attestor_public)->dict:
 if set(request)!={"schema_version","mode","parent_run_id","action_id","action_version","decision"}:raise ValueError("invalid signer request")
 action=next((a for a in state["action_register"] if a["action_id"]==request["action_id"]),None)
 if action is None or request["parent_run_id"]!=state["parent_run_id"] or request["action_version"]!=action["version"]:raise ValueError("signer request binding mismatch")
 contract=action["contract"];candidate=action["candidate"];decision=request["decision"]
 if not authenticated(decision,claude_public,"claude_skill_decision") or decision.get("decision")!="accepted":raise ValueError("authenticated Claude skill decision required")
 expected_role="qa_verifier" if request["mode"]=="qa" else "department_lead"
 if not authenticated(evidence,attestor_public,"evidence_attestor") or evidence.get("decision_role")!=expected_role or (evidence.get("parent_run_id"),evidence.get("action_id"),evidence.get("action_version"),evidence.get("contract_sha256"))!=(state["parent_run_id"],action["action_id"],action["version"],digest(contract)):raise ValueError("attested evidence binding mismatch")
 if evidence.get("skill_id")!=decision.get("skill_id") or evidence.get("result_sha256")!=decision.get("result_sha256") or not evidence.get("artifact_sha256"):raise ValueError("attested skill result mismatch")
 if request["mode"]=="qa":
  if action["status"]!="running" or not candidate:raise ValueError("recorded candidate required")
  if decision.get("decision_role")!="qa_verifier" or decision.get("contract_sha256")!=digest(contract) or decision.get("result_sha256")!=digest(candidate) or not decision.get("skill_id"):raise ValueError("Claude QA decision binding mismatch")
  receipt={"schema_version":1,"role":"qa_verifier","disposition":"accepted","contract_sha256":digest(contract),"candidate_sha256":digest(candidate),"artifact_receipt_sha256":digest(candidate["artifacts"]),"readback_checks":["sealed_connector_receipts"],"permission_checks":[contract["dispatch_envelope"]["permission_ceiling"]],"completion_checks":contract["dispatch_envelope"]["completion_test"]}
 elif request["mode"]=="lead":
  if action["status"]!="qa_accepted" or not action["qa_receipt"]:raise ValueError("QA acceptance required")
  if decision.get("decision_role")!="department_lead" or decision.get("contract_sha256")!=digest(contract) or decision.get("result_sha256")!=digest(action["qa_receipt"]) or not decision.get("skill_id"):raise ValueError("Claude Lead decision binding mismatch")
  receipt={"schema_version":1,"role":"department_lead","decision":"accepted","qa_receipt_sha256":digest(action["qa_receipt"]),"goal_checks":["parent_goal","department_goal","action_objective"]}
 else:raise ValueError("unsupported signer mode")
 return seal_ed25519(receipt,key) if isinstance(key,(str,Path)) else seal(receipt,key)

def main():
 p=argparse.ArgumentParser();p.add_argument("request",type=Path);p.add_argument("evidence",type=Path);p.add_argument("output",type=Path);p.add_argument("--state-root",type=Path,default=Path("/var/lib/lhm-workflow/departmental-parents"));p.add_argument("--key",type=Path,required=True);p.add_argument("--claude-public",type=Path,required=True);p.add_argument("--attestor-public",type=Path,default=Path("/var/lib/lhm-workflow/public/evidence-attestor.public.pem"));p.add_argument("--request-root",type=Path,default=Path("/var/lib/lhm-workflow/department-signer-requests"));a=p.parse_args()
 try: request=json.loads(read_trusted(a.request,root=a.request_root,uid=os.getuid()))
 except (UnsafeFile,json.JSONDecodeError) as e:raise SystemExit(f"unsafe signer request: {e}")
 evidence=json.loads(read_trusted(a.evidence,root=a.request_root,uid=os.getuid()));state=DepartmentalStateStore(a.state_root).load(request.get("parent_run_id",""));receipt=produce(request,state,a.key,a.claude_public,evidence,a.attestor_public)
 a.output.parent.mkdir(parents=True,exist_ok=True);tmp=a.output.with_name(f".{a.output.name}.{os.getpid()}.tmp");tmp.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"))+"\n");os.chmod(tmp,0o640);os.replace(tmp,a.output)
 a.request.unlink()
if __name__=="__main__":main()
