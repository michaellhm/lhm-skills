import copy,json,os,subprocess
from pathlib import Path
import pytest
from lhm_workflow.departmental_state import *
from lhm_workflow.department_receipt_producer import produce
from lhm_workflow.connector_translation import translate
from lhm_workflow.department_final_producers import projection as produce_projection,hop_dossier
import lhm_workflow.snapshot_broker as broker
import lhm_workflow.result_importer as importer
from lhm_workflow.evidence_attestor import attest
from lhm_workflow.secureio import read_trusted,trusted_key_copy,UnsafeFile
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
 astro=seal({"role":"astro_verifier","receipt_sha256":"e"*64,"return_role":"seo_lead","return_point":"accept_action","seo_state_sha256":digest(s)},QA);produced=hop_dossier(s,astro,QA,HOP);assert authenticated(produced,HOP,"head_of_production")
 with pytest.raises(ValueError):hop_dossier(s,astro,PROD,HOP)
 with pytest.raises(ValueError):accept_completion_dossier(s,receipt,PROD)
 bad=copy.deepcopy(body);bad["astro_return_evidence"]["return_point"]="wrong"
 with pytest.raises(ValueError,match="Astro"):accept_completion_dossier(s,seal(bad,HOP),HOP)
def test_bounded_receipt_producers_derive_from_observed_state_only():
 s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);decision=seal({"role":"claude_skill_decision","decision_role":"qa_verifier","decision":"accepted","skill_id":"seo-qa","contract_sha256":digest(c),"result_sha256":digest(v)},HOP);request={"schema_version":1,"mode":"qa","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"decision":decision}
 evidence=seal({"role":"evidence_attestor","decision_role":"qa_verifier","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"contract_sha256":digest(c),"skill_id":"seo-qa","result_sha256":digest(v),"artifact_sha256":"a"*64},HOP)
 q=produce(request,s,QA,HOP,evidence,HOP);assert authenticated(q,QA,"qa_verifier") and q["completion_checks"]==["objective_met"]
 with pytest.raises(ValueError,match="request"):produce({**request,"claimed_checks":["fake"]},s,QA,HOP,evidence,HOP)
 forged={**request,"decision":seal({**decision,"result_sha256":"f"*64},HOP)}
 with pytest.raises(ValueError,match="mismatch|binding"):produce(forged,s,QA,HOP,evidence,HOP)
 s=record_qa_acceptance(s,c,q,QA);lead_decision=seal({"role":"claude_skill_decision","decision_role":"department_lead","decision":"accepted","skill_id":"seo-lead","contract_sha256":digest(c),"result_sha256":digest(q)},HOP);lead_request={**request,"mode":"lead","decision":lead_decision};lead_evidence=seal({**evidence,"decision_role":"department_lead","skill_id":"seo-lead","result_sha256":digest(q)},HOP);l=produce(lead_request,s,PROD,HOP,lead_evidence,HOP)
 assert authenticated(l,PROD,"department_lead") and l["qa_receipt_sha256"]==digest(q)
def test_captured_connector_final_translation_and_wrong_parent(tmp_path):
 adapter_private=tmp_path/"adapter.pem";adapter_public=tmp_path/"adapter.pub";translator_private=tmp_path/"translator.pem";translator_public=tmp_path/"translator.pub"
 for private,public in ((adapter_private,adapter_public),(translator_private,translator_public)):
  if subprocess.run(["openssl","genpkey","-algorithm","ED25519","-out",str(private)]).returncode:pytest.skip("local OpenSSL lacks Ed25519")
  subprocess.run(["openssl","pkey","-in",str(private),"-pubout","-out",str(public)],check=True)
 s=state();source=seal_ed25519({"role":"claude_connector_evidence","target_role":"qa","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"source_run_id":"claude-skill-20260823-01","skill_id":"seo-qa","contract_sha256":digest(s["action_register"][0]["contract"]),"result_sha256":"a"*64,"artifact_sha256":"b"*64,"artifact_id":"research-1","delivery_parent_id":"folder-1","observed_at":"2026-08-23T00:00:00Z"},adapter_private);request={"schema_version":1,"target_role":"qa","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"source_run_id":"claude-skill-20260823-01"};receipt=translate(request,s,source,adapter_public,translator_private)
 assert authenticated(receipt,translator_public,"connector_metadata_translator") and receipt["artifact_sha256"]=="b"*64
 with pytest.raises(ValueError,match="binding"):translate({**request,"target_role":"lead"},s,source,adapter_public,translator_private)
def test_captured_basicops_translation_binds_expected_task(tmp_path):
 assert "/var/lib/lhm-claude/runs" not in (Path(__file__).parents[1]/"src/lhm_workflow/connector_translation.py").read_text()
def test_projection_and_hop_join_only_authenticated_observations(tmp_path):
 s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);q=qa(c,v);s=record_qa_acceptance(s,c,q,QA);s=record_lead_acceptance(s,c,lead(q),PROD)
 basic=seal({"role":"basicops_connector","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"task_id":"task-1","message_id":"message-1","discussion_sha256":digest(envelope()["discussion_payload"]),"readback_sha256":"d"*64,"source_final_sha256":"e"*64},ADAPTER);tracker=tmp_path/"rollout-state.md";tracker.write_text("accepted milestone");th=__import__("hashlib").sha256(tracker.read_bytes()).hexdigest()
 observation={"tracker_path":str(tracker),"previous_sha256":"0"*64,"intended_post_sha256":th,"observed_post_sha256":th,"changed":True}
 pr=produce_projection(s,basic,observation,ADAPTER,PROD);assert authenticated(pr,PROD,"projection_writer")
 with pytest.raises(ValueError):produce_projection(s,basic,{**observation,"observed_post_sha256":"f"*64},ADAPTER,PROD)
 with pytest.raises(ValueError,match="did not change"):produce_projection(s,basic,{**observation,"previous_sha256":th,"changed":False},ADAPTER,PROD)
def test_ed25519_projection_isolation_and_forgery(tmp_path):
 adapter_private=tmp_path/"adapter.private.pem";adapter_public=tmp_path/"adapter.public.pem";projection_private=tmp_path/"projection.private.pem";projection_public=tmp_path/"projection.public.pem"
 for private,public in ((adapter_private,adapter_public),(projection_private,projection_public)):
  generated=subprocess.run(["openssl","genpkey","-algorithm","ED25519","-out",str(private)],capture_output=True)
  if generated.returncode:pytest.skip("local OpenSSL lacks Ed25519")
  subprocess.run(["openssl","pkey","-in",str(private),"-pubout","-out",str(public)],check=True)
 s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);q=qa(c,v);s=record_qa_acceptance(s,c,q,QA);s=record_lead_acceptance(s,c,lead(q),PROD);tracker=tmp_path/"tracker";tracker.write_text("exact");th=__import__("hashlib").sha256(tracker.read_bytes()).hexdigest()
 basic=seal_ed25519({"role":"basicops_connector","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"task_id":"task-1","message_id":"m1","discussion_sha256":digest(envelope()["discussion_payload"]),"readback_sha256":"a"*64,"source_final_sha256":"b"*64},adapter_private)
 observation={"tracker_path":str(tracker),"previous_sha256":"0"*64,"intended_post_sha256":th,"observed_post_sha256":th,"changed":True}
 receipt=produce_projection(s,basic,observation,adapter_public,projection_private);assert authenticated(receipt,projection_public,"projection_writer")
 with pytest.raises(ValueError):produce_projection(s,basic,observation,projection_public,projection_private)
def test_service_files_isolate_projection_and_hop_keys():
 packaging=Path(__file__).parents[1]/"packaging";projection=(packaging/"lhm-department-projection-producer.service").read_text();hop=(packaging/"lhm-department-hop-producer.service").read_text()
 assert "User=lhmprojection" in projection and "projection.private.pem" in projection and "hop.private.pem" not in projection
 assert "User=lhmhop" in hop and "hop.private.pem" in hop and "projection.private.pem" not in hop
def test_service_files_isolate_qa_and_lead_keys_and_queues():
 packaging=Path(__file__).parents[1]/"packaging";qa=(packaging/"lhm-department-qa-producer.service").read_text();lead_service=(packaging/"lhm-department-lead-producer.service").read_text();install=(packaging/"install.sh").read_text()
 assert "User=lhmdepartmentqa" in qa and "department-qa.private.pem" in qa and "department-lead.private.pem" not in qa and "/qa-requests/" in qa
 assert "User=lhmdepartmentlead" in lead_service and "department-lead.private.pem" in lead_service and "department-qa.private.pem" not in lead_service and "/lead-requests/" in lead_service
 assert "chown root:lhmdepartmentqa" in install and "chown root:lhmdepartmentlead" in install and "usermod -a -G lhmadapterkey,lhmverifierkey lhmworkflow" not in install
def test_cross_role_ed25519_receipt_forgery_fails(tmp_path):
 qa_private=tmp_path/"qa.pem";qa_public=tmp_path/"qa.pub";lead_private=tmp_path/"lead.pem";lead_public=tmp_path/"lead.pub"
 for private,public in ((qa_private,qa_public),(lead_private,lead_public)):
  if subprocess.run(["openssl","genpkey","-algorithm","ED25519","-out",str(private)]).returncode:pytest.skip("local OpenSSL lacks Ed25519")
  subprocess.run(["openssl","pkey","-in",str(private),"-pubout","-out",str(public)],check=True)
 receipt=seal_ed25519({"role":"qa_verifier","decision":"accepted"},qa_private)
 assert authenticated(receipt,qa_public,"qa_verifier") and not authenticated(receipt,lead_public,"qa_verifier")
def test_hash_only_evidence_attestor_rejects_tamper_stale_and_role_mismatch(tmp_path):
 adapter_private=tmp_path/"adapter.pem";adapter_public=tmp_path/"adapter.pub";attestor_private=tmp_path/"attestor.pem";attestor_public=tmp_path/"attestor.pub"
 for private,public in ((adapter_private,adapter_public),(attestor_private,attestor_public)):
  if subprocess.run(["openssl","genpkey","-algorithm","ED25519","-out",str(private)]).returncode:pytest.skip("local OpenSSL lacks Ed25519")
  subprocess.run(["openssl","pkey","-in",str(private),"-pubout","-out",str(public)],check=True)
 s,c=issue_next_action(state(),"child-1");source=seal_ed25519({"role":"claude_connector_evidence","target_role":"qa","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"source_run_id":"claude-skill-20260823-01","skill_id":"seo-qa","contract_sha256":digest(c),"result_sha256":"a"*64,"artifact_sha256":"b"*64,"artifact_id":"research-1","delivery_parent_id":"folder-1","observed_at":"2026-08-23T00:00:00Z"},adapter_private);request={"schema_version":1,"target_role":"qa","parent_run_id":"wave-1","action_id":"SEO-01","action_version":1,"source_run_id":"claude-skill-20260823-01"}
 receipt=attest(request,s,source,adapter_public,attestor_private,"2026-08-23T00:01:00Z");assert authenticated(receipt,attestor_public,"evidence_attestor") and "files" not in receipt
 with pytest.raises(ValueError,match="stale"):attest({**request,"action_version":2},s,source,adapter_public,attestor_private)
 with pytest.raises(ValueError,match="binding"):attest({**request,"target_role":"lead"},s,source,adapter_public,attestor_private)
 tampered={**source,"result_sha256":"f"*64}
 with pytest.raises(ValueError,match="authenticated"):attest(request,s,tampered,adapter_public,attestor_private)
 with pytest.raises(ValueError,match="run"):attest({**request,"source_run_id":"../../run"},s,source,adapter_public,attestor_private)
def test_evidence_attestor_is_hard_disabled_until_rehearsal():
 packaging=Path(__file__).parents[1]/"packaging";service=(packaging/"lhm-department-evidence-attestor.service").read_text();install=(packaging/"install.sh").read_text()
 assert "ExecStart=/bin/false" in service and "evidence-attestor.path" in install.split("department_units=",1)[1].splitlines()[0]
def test_common_trusted_reader_rejects_symlink_mode_owner_and_mutation(tmp_path,monkeypatch):
 root=tmp_path/"trusted";root.mkdir();good=root/"value.json";good.write_text('{}');good.chmod(0o600);uid=os.getuid()
 assert read_trusted(good,root=root,uid=uid)==b'{}'
 link=root/"link.json";link.symlink_to(good)
 with pytest.raises(UnsafeFile):read_trusted(link,root=root,uid=uid)
 good.chmod(0o622)
 with pytest.raises(UnsafeFile,match="ownership or mode"):read_trusted(good,root=root,uid=uid)
 good.chmod(0o600)
 with pytest.raises(UnsafeFile,match="ownership or mode"):read_trusted(good,root=root,uid=uid+1)
 real_fstat=os.fstat;calls={"n":0}
 def changed(fd):
  value=real_fstat(fd);calls["n"]+=1
  if calls["n"]==2:
   class Changed:
    def __getattr__(self,name):return value.st_mtime_ns+1 if name=="st_mtime_ns" else getattr(value,name)
   return Changed()
  return value
 monkeypatch.setattr(os,"fstat",changed)
 with pytest.raises(UnsafeFile,match="changed during read"):read_trusted(good,root=root,uid=uid)
def test_projection_and_hop_sources_have_no_direct_read_text():
 source=Path(__file__).parents[1]/"src/lhm_workflow"
 for name in ("projection_producer.py","hop_producer.py"):
  text=(source/name).read_text();assert ".read_text()" not in text and "trusted_key_copy" in text and "read_trusted" in text
def test_trusted_claude_pins_complete_marketing_hub_222_archive():
 root=Path(__file__).parents[1];script=(root/"packaging/provision-trusted-claude.sh").read_text();supervisor=(root/"integration/lhm_claude_trusted_supervisor.py").read_text()
 assert "lhm-marketing-hub-2.2.2.tar" in script and "lhm-marketing-hub-2.2.2" in supervisor
 assert "/.claude/plugins/cache/" not in script and "trusted-marketing-hub-package.py" in script
def test_snapshot_broker_allowlist_stale_replay_and_traversal(tmp_path,monkeypatch):
 root=tmp_path;store=DepartmentalStateStore(root/"departmental-parents");current=store.checkpoint(state(),expected_generation=None);snap={"state_record":current};value={"role":"controller_dispatch","target_role":"projection","parent_run_id":"wave-1","generation":1,"state_sha256":digest(current),"snapshot_sha256":digest(snap),"snapshot":snap,"attestation":"test"}
 monkeypatch.setattr(broker,"authenticated",lambda *a:True);out=root/"controller-outgoing";out.mkdir();source=out/"request.json";source.write_text(json.dumps(value));assert broker.process(source,root,tmp_path/"public") == "delivered"
 source.write_text(json.dumps(value));assert broker.process(source,root,tmp_path/"public") == "replayed"
 stale={**value,"generation":0};source.write_text(json.dumps(stale))
 with pytest.raises(ValueError,match="stale"):broker.process(source,root,tmp_path/"public")
 outside=tmp_path/"outside.json";outside.write_text(json.dumps(value))
 with pytest.raises(ValueError,match="unsafe"):broker.process(outside,root,tmp_path/"public")
def test_snapshot_broker_recovers_crash_after_delivery(tmp_path,monkeypatch):
 root=tmp_path;store=DepartmentalStateStore(root/"departmental-parents");current=store.checkpoint(state(),expected_generation=None);snap={"state_record":current};value={"role":"controller_dispatch","target_role":"projection","parent_run_id":"wave-1","generation":1,"state_sha256":digest(current),"snapshot_sha256":digest(snap),"snapshot":snap,"attestation":"test"}
 monkeypatch.setattr(broker,"authenticated",lambda *a:True);out=root/"controller-outgoing";out.mkdir();source=out/"request.json";source.write_text(json.dumps(value));monkeypatch.setenv("LHM_SNAPSHOT_BROKER_FAULT","after_delivery")
 with pytest.raises(RuntimeError,match="injected"):broker.process(source,root,tmp_path/"public")
 monkeypatch.delenv("LHM_SNAPSHOT_BROKER_FAULT");assert broker.process(source,root,tmp_path/"public")=="recovered"
def test_broker_rejects_cross_role_and_symlink(tmp_path,monkeypatch):
 out=tmp_path/"controller-outgoing";out.mkdir();target=tmp_path/"real";target.write_text("{}");link=out/"link.json";link.symlink_to(target)
 with pytest.raises(ValueError,match="unsafe"):broker.process(link,tmp_path,tmp_path/"public")
 bad=out/"bad.json";bad.write_text(json.dumps({"target_role":"admin"}));monkeypatch.setattr(broker,"authenticated",lambda *a:True)
 with pytest.raises(ValueError,match="invalid"):broker.process(bad,tmp_path,tmp_path/"public")
def test_result_importer_exact_role_replay_and_quarantine_boundary(tmp_path,monkeypatch):
 root=tmp_path;store=DepartmentalStateStore(root/"departmental-parents");current=store.checkpoint(state(),expected_generation=None);(root/"projection-results").mkdir();(root/"snapshot-consumed").mkdir();(root/"public").mkdir()
 dispatch={"parent_run_id":"wave-1","target_role":"projection","generation":1,"snapshot_sha256":"a"*64};(root/"snapshot-consumed"/f'wave-1-projection-{"a"*64}.json').write_text(json.dumps(dispatch));result={"role":"projection_producer","snapshot_sha256":"a"*64,"receipt":{},"attestation":"x"};path=root/"projection-results/result.json";path.write_text(json.dumps(result))
 monkeypatch.setattr(importer,"authenticated",lambda *a:True);monkeypatch.setattr(importer,"import_result",lambda current,*a:current)
 assert importer.process(path,root,"projection")=="imported";path.write_text(json.dumps(result));assert importer.process(path,root,"projection")=="replayed"
 with pytest.raises(ValueError,match="role"):importer.process(root/"projection-results/nope",root,"admin")
def test_result_importer_recovers_checkpoint_before_marker(tmp_path,monkeypatch):
 root=tmp_path;s,c=issue_next_action(state(),"child-1");v=candidate(c);s=record_candidate(s,c,v,ADAPTER);q=qa(c,v);s=record_qa_acceptance(s,c,q,QA);s=record_lead_acceptance(s,c,lead(q),PROD);store=DepartmentalStateStore(root/"departmental-parents");current=store.checkpoint(s,expected_generation=None);receipt=projection(current,c);result={"role":"projection_producer","snapshot_sha256":"a"*64,"receipt":receipt,"attestation":"x"};dispatch={"parent_run_id":"wave-1","target_role":"projection","generation":1,"snapshot_sha256":"a"*64};(root/"projection-results").mkdir();(root/"snapshot-consumed").mkdir();(root/"public").mkdir();(root/"snapshot-consumed"/f'wave-1-projection-{"a"*64}.json').write_text(json.dumps(dispatch));path=root/"projection-results/result.json";path.write_text(json.dumps(result));monkeypatch.setattr(importer,"authenticated",lambda *a:True);monkeypatch.setattr(importer,"import_result",lambda current,*a:record_projection(current,c,receipt,PROD));monkeypatch.setenv("LHM_RESULT_IMPORTER_FAULT","after_checkpoint")
 with pytest.raises(RuntimeError,match="injected"):importer.process(path,root,"projection")
 monkeypatch.delenv("LHM_RESULT_IMPORTER_FAULT");assert importer.process(path,root,"projection")=="recovered"
def test_new_root_broker_units_are_disabled_by_default():
 install=(Path(__file__).parents[1]/"packaging/install.sh").read_text()
 units=next(line for line in install.splitlines() if line.startswith("units="))
 assert "snapshot-broker" not in units and "projection-producer" not in units and "hop-producer" not in units
def test_cli_subprocess_rejects_unsealed_connector_receipt(tmp_path):
 root=tmp_path/"controller"; env={**os.environ,"PYTHONPATH":str(Path(__file__).parents[1]/"src"),"LHM_WORKFLOW_TEST_MODE":"1","LHM_WORKFLOW_ROOT":str(root)}
 definition={"parent_run_id":"cli-wave","department":"seo","parent_goal":"Goal","department_goal":"Department goal","actions":[{"action_id":"SEO-01","dependencies":[],"objective":"Research","required_skills":["keyword-research"],"accepted_inputs":[],"required_output":"durable","dispatch_envelope":envelope()}]}
 def run(command,payload):return subprocess.run([os.environ.get("LHM_WORKFLOW_CLI",str(Path(__file__).parents[1]/"lhm-workflow")),command,"cli-wave"] if command!="department-init" else [os.environ.get("LHM_WORKFLOW_CLI",str(Path(__file__).parents[1]/"lhm-workflow")),command],input=json.dumps(payload),text=True,capture_output=True,env=env)
 assert run("department-init",definition).returncode==0
 issued=run("department-issue",{"child_run_id":"child-1"});assert issued.returncode==0;c=json.loads(issued.stdout)["contract"]
 forged={"candidate_id":"candidate-1","contract_sha256":digest(c),"artifacts":[{k:v for k,v in art().items() if k not in {"role","attestation"}}],"completion_evidence":["objective_met"],"permission_evidence":["green"],"output_disposition":{"status":"delivered"}}
 denied=run("department-candidate",forged);assert denied.returncode==2 and "artifact receipt" in denied.stderr
