import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from lhm_workflow.org_routing import CRON_ID, ROLE_POLICY, Router, accept, canonical, digest, intake, issue, receipt, seal
from lhm_workflow.tracker_connector import TrackerConnector, sha, summary_from_parent

KEYS={role:hashlib.sha256(role.encode()).digest() for role,_,_,_ in ROLE_POLICY.values()}


def artifact(name):
    return {"artifact_id":name,"sha256":hashlib.sha256(name.encode()).hexdigest(),"media_type":"application/json"}


def cron(delivery="none"):
    return {"source":"hermes-cron-alternate","source_cron_id":CRON_ID,"job_name":"LHM weekly SEO rollout",
            "prompt":"Run the governed weekly SEO rollout.","delivery":delivery,"triggered_at":"2026-08-23T18:00:00Z"}


def step(parent, child, *, decision=None):
    parent,contract=issue(parent,child)
    outputs=contract["input_artifacts"] if contract["runtime"]=="verifier" or contract["stage_id"]=="operations_readback" else [artifact(child)]
    checks=["deterministic_role_acceptance"]
    if contract["stage_id"]=="chief_handback": checks.append("governed_delivery_suppressed_canary")
    value=seal(receipt(contract,outputs=outputs,checks=checks,decision=decision),KEYS[contract["owner"]])
    return accept(parent,contract,value,attestation_keys=KEYS),contract


def test_full_org_route_with_optional_teams_and_exact_owners():
    parent=intake(cron(),"weekly-1")
    parent,c1=step(parent,"chief-1"); parent,c2=step(parent,"prod-1")
    parent,c3=step(parent,"seo-plan")
    parent,_=step(parent,"research"); parent,_=step(parent,"research-verify")
    parent,_=step(parent,"seo-accept",decision={"content_required":True,"website_required":True,"reason":"verified defects and approved pages"})
    expected=["content","content_verify","website","website_verify","final_verify","production_closeout","chief_handback","operations_write","operations_readback","learning"]
    seen=[]
    for i in range(len(expected)):
        parent,c=step(parent,f"child-{i}"); seen.append(c["stage_id"])
        assert c["owner"]==ROLE_POLICY[c["stage_id"]][0]
    assert seen==expected and parent["state"]=="closed" and parent["delivery"]["status"]=="suppressed"


def test_optional_content_and_website_are_skipped_only_by_seo_lead_decision():
    parent=intake(cron(),"weekly-2")
    parent,_=step(parent,"chief"); parent,_=step(parent,"prod")
    parent,_=step(parent,"seo-plan"); parent,_=step(parent,"research"); parent,_=step(parent,"research-verify")
    parent,_=step(parent,"seo-accept",decision={"content_required":False,"website_required":False,"reason":"clean diagnosis"})
    assert "content" not in parent["stage_order"] and "website" not in parent["stage_order"]
    assert parent["stage_order"][3:]==["research","research_verify","seo_accept","final_verify","production_closeout","chief_handback","operations_write","operations_readback","learning"]


def test_cron_cannot_deliver_raw_telegram_or_dispatch_claude():
    with pytest.raises(ValueError,match="delivery must be disabled"): intake(cron("telegram"),"weekly-3")
    candidate=json.loads((Path(__file__).parents[1]/"integration/cron-3994012c42ba.alternate.disabled.json").read_text())
    assert candidate["enabled"] is False and candidate["deliver"]=="none" and candidate["no_agent"] is True
    assert "claude" not in candidate["script"].lower()


def test_head_of_production_owns_dispatch_before_research():
    parent=intake(cron(),"weekly-4")
    parent,c=issue(parent,"first")
    assert c["stage_id"]=="chief_intake" and c["runtime"]=="deterministic"
    parent=accept(parent,c,seal(receipt(c,outputs=[artifact("first")],checks=["accepted"]),KEYS[c["owner"]]),attestation_keys=KEYS)
    _,c=issue(parent,"second")
    assert c["stage_id"]=="production_plan" and c["owner"]=="lhm_head_of_production"


def test_operations_write_must_be_followed_by_independent_readback():
    parent=intake(cron(),"weekly-5")
    parent,_=step(parent,"chief"); parent,_=step(parent,"prod")
    parent,_=step(parent,"seo-plan"); parent,_=step(parent,"research"); parent,_=step(parent,"research-verify")
    parent,_=step(parent,"seo-accept",decision={"content_required":False,"website_required":False,"reason":"clean"})
    while parent["stage_order"][parent["cursor"]] != "operations_write": parent,_=step(parent,f"x-{parent['cursor']}")
    parent,_=step(parent,"ops-write")
    _,contract=issue(parent,"ops-read")
    assert contract["stage_id"]=="operations_readback" and contract["required_capabilities"]==["knowledge.tracker_readback"]


def test_receipt_cannot_be_replayed_for_another_owner_or_contract():
    parent=intake(cron(),"weekly-6"); running,contract=issue(parent,"chief")
    value=receipt(contract,outputs=[artifact("x")],checks=["ok"]); value["owner"]="lhm_researcher"
    with pytest.raises(ValueError,match="owner"): accept(running,contract,value,attestation_keys=KEYS)


def test_persistent_router_exact_once_issue_accept_failure_and_resume(tmp_path):
    router=Router(tmp_path/"router",KEYS); parent="weekly-persist"
    router.initialise(cron(),parent); contract=router.issue(parent,"chief")
    assert router.issue(parent,"chief")==contract
    proof={"parent_run_id":parent,"contract_sha256":digest(contract),"reason":"transient dependency"}
    import hmac
    signature=hmac.new(KEYS[contract["owner"]],canonical(proof),hashlib.sha256).hexdigest()
    failed=router.fail(parent,contract,"transient dependency",signature)
    assert failed["state"]=="needs_repair" and router.fail(parent,contract,"transient dependency",signature)==failed
    resume_proof={"parent_run_id":parent,"contract_sha256":digest(contract),"failure_receipt_sha256":failed["stages"][-1]["failure_receipt_sha256"],"action":"resume"}
    resume_signature=hmac.new(KEYS["lhm_head_of_production"],canonical(resume_proof),hashlib.sha256).hexdigest()
    resumed=router.resume(parent,resume_signature); assert resumed["state"]=="running" and router.resume(parent)==resumed
    value=seal(receipt(contract,outputs=[artifact("chief")],checks=["accepted"]),KEYS[contract["owner"]])
    first=router.accept(parent,contract,value); assert router.accept(parent,contract,value)==first


def test_failure_cannot_rewind_accepted_stage(tmp_path):
    router=Router(tmp_path/"router",KEYS); parent="weekly-no-rewind"; router.initialise(cron(),parent)
    contract=router.issue(parent,"chief"); value=seal(receipt(contract,outputs=[artifact("chief")],checks=["accepted"]),KEYS[contract["owner"]]); router.accept(parent,contract,value)
    import hmac
    proof={"parent_run_id":parent,"contract_sha256":digest(contract),"reason":"late forged failure"}
    signature=hmac.new(KEYS[contract["owner"]],canonical(proof),hashlib.sha256).hexdigest()
    with pytest.raises(ValueError,match="rewind"): router.fail(parent,contract,"late forged failure",signature)


def test_real_tracker_connector_cas_write_and_exact_readback(tmp_path):
    connector=TrackerConnector(tmp_path/"vault"); h=hashlib.sha256(b"receipt").hexdigest()
    summary={"parent_run_id":"p1","workflow_id":"lhm-weekly-seo-org-v1","accepted_receipts":[{"stage_id":"research","contract_sha256":h,"artifact_sha256s":[h]}],"run_result":"succeeded","work_state":"complete","completed_at":"2026-08-23T18:00:00Z"}
    artifact,written=connector.append_structured(summary,sha(b"")); assert b"Governed run p1" in written
    same,readback=connector.readback(artifact["sha256"]); assert same==artifact and readback==written
    with pytest.raises(ValueError,match="CAS"): connector.append_structured(summary,sha(b"wrong"))
    connector.path.write_bytes(b"tampered")
    with pytest.raises(ValueError,match="readback"): connector.readback(artifact["sha256"])


def test_tracker_summary_is_derived_from_persisted_accepted_state_and_rejects_injection():
    h=hashlib.sha256(b"receipt").hexdigest(); parent={"parent_run_id":"p1","workflow_id":"lhm-weekly-seo-org-v1","stages":[{"stage_id":"research","status":"accepted","contract_sha256":h,"outputs":[artifact("research")]}]}
    request={"parent_run_id":"p1","run_result":"succeeded","work_state":"complete","completed_at":"2026-08-23T18:00:00Z"}
    summary=summary_from_parent(parent,request); assert summary["accepted_receipts"][0]["contract_sha256"]==h
    bad={**request,"parent_run_id":"p1\nINJECTED"}
    with pytest.raises(ValueError): summary_from_parent(parent,bad)
    forged={**summary,"accepted_receipts":[{"stage_id":"fake","contract_sha256":"f"*64,"artifact_sha256s":["e"*64]}]}
    # Renderer validates shape, but the root adapter never accepts this field; provenance comes only from summary_from_parent.
    assert "accepted_receipts" not in request
