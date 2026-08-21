import hashlib, hmac, json
import pytest
from lhm_workflow.controller import ControllerError, WorkflowController
from lhm_workflow.storage import digest

def contract(parent="p-recovery", stage="seo_evidence", mutation="none"):
    return {"schema_version":1,"parent_run_id":parent,"child_run_id":"child-1","workflow_id":"seo-content-astro-v1","stage_id":stage,"idempotency_key":"a"*64,"worker":{"runtime":"claude","identity":"seo"},"required_skills":["lhm-marketing-hub:seo-audit"],"required_capabilities":[],"expected_mutation_state":mutation}

def failure(c, kind="needs_more_research", fid="failure-1", observer="lhmworkflowverify"):
    value={"schema_version":1,"failure_id":fid,"parent_run_id":"p-recovery","child_run_id":"child-1","stage_id":"seo_evidence","classification":kind,"reason":"Bounded evidence is incomplete.","evidence_sha256":["b"*64],"observer":observer}
    raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode()
    return {**value,"failure_attestation":hmac.new((c.secrets/"verifier.key").read_bytes(),raw,hashlib.sha256).hexdigest()}

def seal(c, value):
    unsigned=dict(value); raw=json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode()
    return {**unsigned,"production_attestation":hmac.new((c.secrets/"production.key").read_bytes(),raw,hashlib.sha256).hexdigest()}

def test_research_failure_requires_production_resume_and_is_idempotent(tmp_path):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract())
    f=failure(c); assert c.record_failure(f)==f; assert c.record_failure(f)==f
    receipt=c.failure_receipts/"failure-1.json"; assert receipt.stat().st_mode & 0o777 == 0o440
    auth=seal(c,{"schema_version":1,"mode":"Production","actor":"lhm_production_manager","decision":"resume","failure_id":"failure-1","failure_receipt_sha256":hashlib.sha256(receipt.read_bytes()).hexdigest()})
    with pytest.raises(ControllerError): c.production_resume("p-recovery","seo_evidence",{**auth,"mode":"worker"})
    resumed=c.production_resume("p-recovery","seo_evidence",auth)
    assert resumed["stages"][0]["retry_attempt"]==1 and resumed["stages"][0]["status"]=="issued"
    assert c.production_resume("p-recovery","seo_evidence",auth)==resumed

def test_conflicting_receipt_and_worker_self_certification_denied(tmp_path):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract())
    with pytest.raises(ControllerError,match="self-certification"): c.record_failure(failure(c,observer="claudeworker"))
    c.record_failure(failure(c))
    changed=failure(c); changed["reason"]="rewritten evidence"; changed.pop("failure_attestation")
    raw=json.dumps(changed,sort_keys=True,separators=(",",":")).encode(); changed["failure_attestation"]=hmac.new((c.secrets/"verifier.key").read_bytes(),raw,hashlib.sha256).hexdigest()
    with pytest.raises(ControllerError,match="conflicting"): c.record_failure(changed)

def test_capability_incident_creates_non_mutating_repair_and_diagnostic_queues(tmp_path):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract())
    c.record_failure(failure(c,"capability_incident"))
    assert json.loads((c.repair_queue/"failure-1.json").read_text())["status"]=="awaiting_repair"
    diagnostic=json.loads((c.diagnostic_queue/"failure-1.json").read_text())
    assert diagnostic["may_mutate"] is False and diagnostic["may_resume"] is False

def test_no_consequential_retry(tmp_path):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract(mutation="branch_only"))
    c.record_failure(failure(c))
    state=c.status("p-recovery"); assert state["stages"][0]["recovery_disposition"]=="no_automatic_retry"

def test_crash_after_immutable_receipt_reconciles_on_replay(tmp_path, monkeypatch):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract()); f=failure(c)
    monkeypatch.setattr(c,"_fault",lambda point: (_ for _ in ()).throw(RuntimeError("crash")) if point=="failure_receipt_sealed" else None)
    with pytest.raises(RuntimeError): c.record_failure(f)
    assert (c.failure_receipts/"failure-1.json").exists() and c.status("p-recovery")["stages"][0]["status"]=="issued"
    monkeypatch.setattr(c,"_fault",lambda point: None); c.record_failure(f)
    assert c.status("p-recovery")["stages"][0]["status"]=="failed"

def test_only_one_retry_and_accepted_stage_cannot_be_rewound(tmp_path):
    c=WorkflowController(tmp_path,test_mode=True); c.initialise(contract()); f1=failure(c)
    c.record_failure(f1); receipt=c.failure_receipts/"failure-1.json"
    auth=seal(c,{"schema_version":1,"mode":"Production","actor":"lhm_production_manager","decision":"resume","failure_id":"failure-1","failure_receipt_sha256":hashlib.sha256(receipt.read_bytes()).hexdigest()})
    c.production_resume("p-recovery","seo_evidence",auth)
    c.record_failure(failure(c,fid="failure-2"))
    assert c.status("p-recovery")["stages"][0]["recovery_disposition"]=="no_automatic_retry"
    other=WorkflowController(tmp_path/"accepted",test_mode=True); parent=other.initialise(contract(parent="p-accepted"))
    old=other.storage.read_parent("p-accepted"); parent["stages"][0]["status"]="accepted"; other.storage.transact("p-accepted",parent,expected_hash=digest(old),tx_id="accept-test")
    denied=failure(other); denied["parent_run_id"]="p-accepted"; denied.pop("failure_attestation")
    raw=json.dumps(denied,sort_keys=True,separators=(",",":")).encode(); denied["failure_attestation"]=hmac.new((other.secrets/"verifier.key").read_bytes(),raw,hashlib.sha256).hexdigest()
    with pytest.raises(ControllerError,match="cannot be rewound"): other.record_failure(denied)
