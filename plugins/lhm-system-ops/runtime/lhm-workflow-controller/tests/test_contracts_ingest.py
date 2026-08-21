import hashlib,json
from pathlib import Path
import pytest
from lhm_workflow.contracts import *
from lhm_workflow.ingest import Ingestor
def contract(): return {"workflow_id":"lhm-seo-001","workflow_type":WORKFLOW_TYPE,"stage_id":"seo_evidence","child_run_id":"child:1","worker":"claude","required_skills":["lhm-marketing-hub:seo-audit"],"required_capabilities":["google_search_console.property_read"]}
def test_fixed_contract_rejects_worker():
 c=contract();c["worker"]="root"
 with pytest.raises(ContractError): validate_contract(c)
def test_artifact_and_envelopes(tmp_path):
 p=tmp_path/"a";p.write_text("x"); a={"artifact_id":"a","logical_name":"a","media_type":"text/plain","size_bytes":1,"sha256":hashlib.sha256(b"x").hexdigest(),"purpose":"t","path":str(p)}; validate_artifact(a,tmp_path)
 validate_connector({"observer":"host-connector-adapter","mutation":True,"readback":True,"remote_id":"1"})
 validate_site({"observer":"host-site-adapter","commit":"a"*40,"preview_url":"https://x","preview_noindex":True,"configured_checks":True})
def test_host_events_and_replay_quarantine(tmp_path):
 q=tmp_path/"q";p=tmp_path/"p"; ing=Ingestor(q,p); f=tmp_path/"e.jsonl"; c=contract()
 ev=[{"source":"host-dispatcher","child_run_id":"child:1","event":"skill_tool_call","skill":c["required_skills"][0]},{"source":"host-dispatcher","child_run_id":"child:1","event":"capability_observed","capability":c["required_capabilities"][0]},{"source":"host-dispatcher","child_run_id":"child:1","event":"terminal","status":"completed"}]
 f.write_text("\n".join(map(json.dumps,ev))); assert ing.ingest_events(f,c)["status"]=="completed"
 f=tmp_path/"again";f.write_text("{}"); assert ing.ingest_events(f,c) is None; assert (q/"again").exists()
def test_worker_summary_is_quarantined(tmp_path):
 ing=Ingestor(tmp_path/"q",tmp_path/"p"); f=tmp_path/"bad";f.write_text(json.dumps({"source":"worker-summary","child_run_id":"child:1"})); assert ing.ingest_events(f,contract()) is None
