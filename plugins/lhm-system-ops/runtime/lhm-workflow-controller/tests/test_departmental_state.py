import copy,json,os,subprocess
from pathlib import Path
import pytest
from lhm_workflow.departmental_state import *
ADAPTER=b"adapter"; QA=b"qa"; PROD=b"production"; APPROVAL=b"approval"; HOP=b"hop"
def envelope():return {"delivery_parent_id":"folder-1","permission_ceiling":"green","completion_test":["objective_met"],"basicops_task_id":"task-1","basicops_dedupe_key":"seo:wave-1","discussion_payload":{"Goal":"Grow visibility","Outcome":"Accepted package","Milestones":["Research"],"Actions":["Run research"],"Artefacts":["Drive file"],"Dependencies":["Context"],"Completion":"Checks pass","Next handoff":"SEO Lead"},"no_subtasks":True,"constraints":["one_action"],"return_role":"seo_lead","return_point":"accept_action","approval":{"required":False,"receipt":None,"superseded_by_version":None}}
def art(i="research"):
 return seal({"artifact_id":i,"sha256":"a"*64,"media_type":"text/markdown","drive_file_id":"drive-1","drive_url":"https://drive.google.com/file/d/drive-1","drive_parent_id":"folder-1","readback_sha256":"a"*64,"role":"drive_connector"},ADAPTER)
def state(kind="durable"):
 return new_departmental_state(parent_run_id="wave-1",department="seo",parent_goal="Grow visibility",department_goal="Deliver package",actions=[{"action_id":"SEO-01","dependencies":[],"objective":"Research","required_skills":["keyword-research"],"accepted_inputs":[],"required_output":kind,"dispatch_envelope":envelope()},{"action_id":"SEO-02","dependencies":["SEO-01"],"objective":"Brief","required_skills":["seo-page-brief"],"accepted_inputs":[],"required_output":"durable","dispatch_envelope":envelope()}])
def candidate(c,items=None,disposition=None):return {"candidate_id":"candidate-1","contract_sha256":digest(c),"artifacts":[art()] if items is None else items,"completion_evidence":["objective_met"],"permission_evidence":["green"],"output_disposition":{"status":"delivered"} if disposition is None else disposition}
def qa(c,v):return seal({"schema_version":1,"role":"qa_verifier","disposition":"accepted","contract_sha256":digest(c),"candidate_sha256":digest(v),"artifact_receipt_sha256":digest(v["artifacts"]),"readback_checks":["drive_readback"],"permission_checks":["green"],"completion_checks":["objective_met"]},QA)
def lead(q):return seal({"schema_version":1,"role":"department_lead","decision":"accepted","qa_receipt_sha256":digest(q),"goal_checks":["department_goal"]},PROD)
def projection(s,c):return seal({"schema_version":1,"role":"projection_writer","parent_run_id":s["parent_run_id"],"action_id":c["action_id"],"action_version":c["action_version"],"state_readback_sha256":digest(s),"tracker_path":"rollout-state.md","tracker_sha256":"c"*64,"tracker_readback_sha256":"c"*64,"basicops_task_id":"task-1","basicops_dedupe_key":"seo:wave-1","basicops_comment_id":"comment-1","discussion_payload_sha256":digest(envelope()["discussion_payload"]),"no_subtasks":True,"basicops_readback_sha256":"d"*64},PROD)
def test_separate_gates_materialise_dependency_and_replays_are_idempotent():
 s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);assert record_candidate(s,c,v,ADAPTER)==s
 q=qa(c,v);s=record_qa_acceptance(s,c,q,QA);assert record_qa_acceptance(s,c,q,QA)==s
 l=lead(q);s=record_lead_acceptance(s,c,l,PROD);assert record_lead_acceptance(s,c,l,PROD)==s
 p=projection(s,c);done=record_projection(s,c,p,PROD);assert done["action_register"][1]["version"]==2 and done["action_register"][1]["accepted_inputs"]==[art()]
def test_forged_roles_and_false_projection_rejected():
 s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);q=qa(c,v)
 with pytest.raises(ValueError):record_qa_acceptance(s,c,q,b"wrong")
 s=record_qa_acceptance(s,c,q,QA);l=lead(q)
 with pytest.raises(ValueError):record_lead_acceptance(s,c,l,b"wrong")
 s=record_lead_acceptance(s,c,l,PROD);p=projection(s,c);p["tracker_readback_sha256"]="e"*64;p=seal(p,PROD)
 with pytest.raises(ValueError,match="false projection"):record_projection(s,c,p,PROD)
 p=projection(s,c);p["basicops_dedupe_key"]="wrong";p=seal(p,PROD)
 with pytest.raises(ValueError,match="BasicOps binding"):record_projection(s,c,p,PROD)
def test_sealed_drive_receipt_with_wrong_parent_is_rejected():
 s,c=issue_next_action(state(),"child-1");wrong=art();wrong["drive_parent_id"]="other-folder";wrong=seal(wrong,ADAPTER)
 with pytest.raises(ValueError,match="wrong Drive parent"):record_candidate(s,c,candidate(c,[wrong]),ADAPTER)
def test_durable_and_explicit_non_durable_output():
 s,c=issue_next_action(state(),"child-1")
 with pytest.raises(ValueError,match="durable"):record_candidate(s,c,candidate(c,[]),ADAPTER)
 s,c=issue_next_action(state("non_durable"),"child-1")
 with pytest.raises(ValueError,match="not_required"):record_candidate(s,c,candidate(c,[],{"status":"done"}),ADAPTER)
 assert record_candidate(s,c,candidate(c,[],{"status":"not_required","reason":"No file-producing output in this action"}),ADAPTER)["action_register"][0]["candidate"]
def test_changed_input_v2_store_cas_and_corruption(tmp_path):
 s,c=issue_next_action(state(),"child-1");s=record_candidate(s,c,candidate(c),ADAPTER);s=revise_action_inputs(s,"SEO-01",[art("context")]);assert s["action_register"][0]["version"]==2
 store=DepartmentalStateStore(tmp_path);one=store.checkpoint(state(),expected_generation=None);stale=copy.deepcopy(one);new=store.checkpoint(one,expected_generation=1)
 with pytest.raises(ValueError,match="stale"):store.checkpoint(stale,expected_generation=1)
 raw=copy.deepcopy(new);raw["state"]="department_accepted";store.path("wave-1").write_text(json.dumps(raw))
 with pytest.raises(ValueError,match="top state"):store.load("wave-1")
def test_unrelated_completion_or_permission_evidence_rejected():
 s,c=issue_next_action(state(),"child-1");v=candidate(c);v["completion_evidence"]=["unrelated"]
 with pytest.raises(ValueError,match="does not satisfy"):record_candidate(s,c,v,ADAPTER)
 v=candidate(c);v["permission_evidence"]=["amber"]
 with pytest.raises(ValueError,match="does not satisfy"):record_candidate(s,c,v,ADAPTER)
def test_material_change_supersedes_machine_approval():
 s=state();a=s["action_register"][0];a["dispatch_envelope"]["approval"]["required"]=True
 material=digest({"objective":a["objective"],"inputs":a["accepted_inputs"],"envelope":{k:v for k,v in a["dispatch_envelope"].items() if k!="approval"}})
 a["dispatch_envelope"]["approval"]["receipt"]=seal({"schema_version":1,"role":"approval_authority","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"material_sha256":material,"decision":"approved"},APPROVAL)
 assert validate_approval(s,APPROVAL);changed=revise_action_inputs(s,"SEO-01",[art("new")])
 assert changed["action_register"][0]["dispatch_envelope"]["approval"]["receipt"] is None
 with pytest.raises(ValueError,match="approval"):validate_approval(changed,APPROVAL)
def test_completion_dossier_binds_astro_return_and_separate_hop_key():
 s=new_departmental_state(parent_run_id="one",department="seo",parent_goal="Goal",department_goal="Package",actions=[{"action_id":"SEO-01","dependencies":[],"objective":"Research","required_skills":["keyword-research"],"accepted_inputs":[],"required_output":"durable","dispatch_envelope":envelope()}])
 s,c=issue_next_action(s,"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);q=qa(c,v);s=record_qa_acceptance(s,c,q,QA);s=record_lead_acceptance(s,c,lead(q),PROD);s=record_projection(s,c,projection(s,c),PROD)
 body={"schema_version":1,"role":"head_of_production","parent_run_id":"one","department_state_sha256":digest(s),"seo_action_receipts":[digest(s["action_register"][0]["projection_receipt"])],"astro_return_evidence":{"required":True,"receipt_sha256":"e"*64,"return_role":"seo_lead","return_point":"accept_action","seo_state_sha256":digest(s)},"completion_checks":["dossier_complete"],"decision":"accepted"}
 receipt=seal(body,HOP);assert accept_completion_dossier(s,receipt,HOP)==receipt
 with pytest.raises(ValueError):accept_completion_dossier(s,receipt,PROD)
 bad=copy.deepcopy(body);bad["astro_return_evidence"]["return_point"]="wrong"
 with pytest.raises(ValueError,match="Astro"):accept_completion_dossier(s,seal(bad,HOP),HOP)
def test_cli_subprocess_rejects_unsealed_connector_receipt(tmp_path):
 root=tmp_path/"controller"; env={**os.environ,"PYTHONPATH":str(Path(__file__).parents[1]/"src"),"LHM_WORKFLOW_TEST_MODE":"1","LHM_WORKFLOW_ROOT":str(root)}
 definition={"parent_run_id":"cli-wave","department":"seo","parent_goal":"Goal","department_goal":"Department goal","actions":[{"action_id":"SEO-01","dependencies":[],"objective":"Research","required_skills":["keyword-research"],"accepted_inputs":[],"required_output":"durable","dispatch_envelope":envelope()}]}
 def run(command,payload):return subprocess.run([os.environ.get("LHM_WORKFLOW_CLI",str(Path(__file__).parents[1]/"lhm-workflow")),command,"cli-wave"] if command!="department-init" else [os.environ.get("LHM_WORKFLOW_CLI",str(Path(__file__).parents[1]/"lhm-workflow")),command],input=json.dumps(payload),text=True,capture_output=True,env=env)
 assert run("department-init",definition).returncode==0
 issued=run("department-issue",{"child_run_id":"child-1"});assert issued.returncode==0;c=json.loads(issued.stdout)["contract"]
 forged={"candidate_id":"candidate-1","contract_sha256":digest(c),"artifacts":[{k:v for k,v in art().items() if k not in {"role","attestation"}}],"completion_evidence":["objective_met"],"permission_evidence":["green"],"output_disposition":{"status":"delivered"}}
 denied=run("department-candidate",forged);assert denied.returncode==2 and "artifact receipt" in denied.stderr
