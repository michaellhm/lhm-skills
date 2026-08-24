import pytest
from lhm_workflow.seo_capability_envelope import BASICOPS,DRIVE,GSC,MARKETING_HUB,TRACKER_PATH,UNAVAILABLE,accept_keyword,accept_lead,accept_projection,accept_qa,digest,dispatch,envelope,fail_fast,new_state,validate
PARENT="lhm-seo-dept-pilot-2192596-20260824"
def bound(**extra):
 value={"parent_run_id":PARENT,"action_id":"SEO-01","action_version":1,"envelope_sha256":envelope(PARENT)["envelope_sha256"]};value.update(extra);return value
def keyword_receipt(**extra):
 value=bound(skill="keyword-research",artifact_id="seo-01-keywords",sha256="a"*64,drive_folder_id=DRIVE["folder_id"],relative_path="seo/keyword-research-local-health-marketing.md",media_type="text/markdown",readback_sha256="a"*64,degraded_evidence=True,unavailable_evidence=UNAVAILABLE);value.update(extra);return value
def progressed():
 e=envelope(PARENT);s=accept_keyword(new_state(e),keyword_receipt());qa=bound(skill="seo-delivery-qa",decision="pass",artifact_sha256=digest(s["keyword_artifact"]),readback_sha256="b"*64,degraded_evidence_verified=True,extra_authority=[]);s=accept_qa(s,qa);return e,accept_lead(s,bound(decision="accepted",qa_receipt_sha256=digest(s["qa_receipt"])))
def projection(state,kind,destination,operation):return bound(projection=kind,destination=destination,source_sha256=digest(state["lead_receipt"]),readback_sha256="c"*64,operation=operation)
def test_exact_authority_envelope_is_closed_and_disabled():
 e=validate(envelope(PARENT));assert e["tracker"]["path"]==TRACKER_PATH=="30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md";assert e["marketing_hub"]==MARKETING_HUB and [x["id"] for x in MARKETING_HUB["skills"]]==["keyword-research","seo-delivery-qa"];assert e["gsc"]==GSC and GSC["property"]=="https://localhealthmarketing.com/" and GSC["mode"]=="read_only";assert e["drive"]==DRIVE and e["basicops"]==BASICOPS and e["services_enabled"] is False;assert e["unavailable_evidence"]=={"keywords_everywhere":"unavailable","google_ads":"unavailable"}
@pytest.mark.parametrize("mutator",[lambda e:e["tracker"].update(path="wrong"),lambda e:e["marketing_hub"]["skills"].append({"id":"seo-page-brief","sha256":"0"*64}),lambda e:e["gsc"].update(property="sc-domain:localhealthmarketing.com"),lambda e:e["drive"].update(folder_id="wrong"),lambda e:e["basicops"].update(task_id="wrong"),lambda e:e.update(action_version=2),lambda e:e.update(permission_ceiling="network")])
def test_wrong_binding_and_extra_authority_fail_closed(mutator):
 e=envelope(PARENT);mutator(e)
 with pytest.raises(ValueError):validate(e)
def test_sequential_dispatch_and_three_readback_projections():
 e=envelope(PARENT);s=new_state(e);assert dispatch(s,e)["skill"]=="keyword-research"
 with pytest.raises(ValueError):accept_qa(s,{})
 s=accept_keyword(s,keyword_receipt());assert dispatch(s,e)["skill"]=="seo-delivery-qa" and dispatch(s,e)["accepted_input"]==s["keyword_artifact"]
 qa=bound(skill="seo-delivery-qa",decision="pass",artifact_sha256=digest(s["keyword_artifact"]),readback_sha256="b"*64,degraded_evidence_verified=True,extra_authority=[]);s=accept_qa(s,qa);s=accept_lead(s,bound(decision="accepted",qa_receipt_sha256=digest(s["qa_receipt"])))
 s=accept_projection(s,projection(s,"canonical",TRACKER_PATH,"cas_write_exact_readback"));s=accept_projection(s,projection(s,"drive",DRIVE["folder_id"],"create_md_exact_readback"));s=accept_projection(s,projection(s,"basicops",BASICOPS["task_id"],"discussion_create_exact_readback"));assert s["stage"]=="stopped" and list(s["projections"])==["canonical","drive","basicops"]
 with pytest.raises(ValueError):dispatch(s,e)
@pytest.mark.parametrize("change",[{"drive_folder_id":"wrong"},{"relative_path":"seo/report.txt"},{"relative_path":"other/report.md"},{"readback_sha256":"d"*64},{"degraded_evidence":False},{"unavailable_evidence":{"keywords_everywhere":"inferred","google_ads":"unavailable"}}])
def test_destination_type_readback_and_degraded_evidence_fail_closed(change):
 with pytest.raises(ValueError):accept_keyword(new_state(envelope(PARENT)),keyword_receipt(**change))
def test_projection_parent_version_destination_and_readback_fail_closed():
 _,s=progressed();receipt=projection(s,"canonical",TRACKER_PATH,"cas_write_exact_readback")
 for field,value in [("parent_run_id","wrong"),("action_version",2),("destination","wrong"),("readback_sha256","bad")]:
  with pytest.raises(ValueError):accept_projection(s,{**receipt,field:value})
def test_one_retry_one_incident_immediate_receipt_no_exploratory_loop():
 s=fail_fast(new_state(envelope(PARENT)),"transient",same_key_safe=True);assert s["retry_count"]==1 and s["incident"] is None and s["failure_receipt"]["persist_immediately"] is True;s=fail_fast(s,"repeat",same_key_safe=True);first=s["incident"];assert first["immutable"] is True and first["diagnostic_redispatch"] is False and first["search_loop"] is False;s=fail_fast(s,"again",same_key_safe=False);assert s["retry_count"]==1 and s["incident"]==first
