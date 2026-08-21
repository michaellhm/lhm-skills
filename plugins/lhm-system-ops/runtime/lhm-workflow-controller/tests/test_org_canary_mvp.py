import hashlib,json,os,subprocess
from pathlib import Path
from lhm_workflow.org_canary import Canary,KEY_NAMES
from test_org_routing import cron

def research(root,calls):
    def run(parent,contract,config):
        calls["count"]+=1; path=root/"gsc-readback.md"
        path.write_text("host GSC readback evidence\n"); path.chmod(0o600)
        return {"artifact_id":f"{parent}:research","sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"media_type":"text/markdown"},path
    return run

def cfg(): return {"client_id":"example-client","objective":"SEO read-only audit","site_property":"sc-domain:example.test","urls":["https://example.test/"],"completed_at":"2026-08-23T18:00:00Z","content_required":False,"website_required":False}

def client_record(tmp_path,status="verified",property="sc-domain:example.test"):
    vault=tmp_path/"vault"; path=vault/"_System/Hermes/clients/example-client/capabilities.json"
    operations=["list_sites","batch_url_inspection","search_analytics","list_sitemaps"]
    evidence=tmp_path/"gsc-evidence.json"; evidence.write_text(json.dumps({"requests":{"research.json":{"value":{"profile":"seo_gsc_readonly","required_capabilities":["google_search_console.property_read"],"site_property":property}}}})); evidence.chmod(0o600)
    path.parent.mkdir(parents=True); path.write_text(json.dumps({"client":{"id":"example-client"},"capabilities":{"google_search_console":{"status":status,"route":"seo_gsc_readonly","identifiers":{"property":property},"allowed_operations":operations,"last_test":{"result":"passed","evidence_ref":str(evidence),"evidence_sha256":hashlib.sha256(evidence.read_bytes()).hexdigest(),"binding":{"client_id":"example-client","property":property,"capability":"google_search_console.property_read","allowed_operations":operations}}}}})); path.chmod(0o600)
    return vault

def test_trusted_internal_manual_canary_exact_once_and_readback(tmp_path,monkeypatch):
    key=os.urandom(32); calls={"count":0}; keys={role:key for role in KEY_NAMES}
    canary=Canary(tmp_path,keys,research=research(tmp_path,calls),trusted_internal=True)
    canary.initialise(cron(),"mvp-canary-1")
    monkeypatch.setenv("LHM_CANARY_FAULT","after_external_before_accept")
    try: canary.run("mvp-canary-1",cfg())
    except RuntimeError: pass
    monkeypatch.delenv("LHM_CANARY_FAULT")
    state=Canary(tmp_path,keys,research=research(tmp_path,calls),trusted_internal=True).run("mvp-canary-1",cfg())
    assert calls["count"]==1 and state["state"]=="closed"
    assert "website" not in state["stage_order"]
    assert state["delivery"]=={"channel":"suppressed_canary","status":"suppressed"}
    assert (tmp_path/"evidence/mvp-canary-1.json").is_file()
    tracker=(tmp_path/"vault/30 Projects/LHM Website SEO Growth Rollout/rollout-state.md").read_text()
    assert tracker.count("## Governed run mvp-canary-1")==1

def test_mvp_executable_rejects_website(tmp_path,monkeypatch):
    (tmp_path/"controller.key").write_bytes(os.urandom(32)); (tmp_path/"controller.key").chmod(0o600)
    event=tmp_path/"event.json"; event.write_text(json.dumps(cron()))
    config=tmp_path/"config.json"; config.write_text(json.dumps({**cfg(),"website_required":True}))
    script=Path(__file__).parents[1]/"integration/lhm-seo-org-canary-mvp"
    env={**os.environ,"LHM_WORKFLOW_TEST_MODE":"1","PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    done=subprocess.run([str(script),str(event),"mvp-web",str(config),"--root",str(tmp_path),"--vault-root",str(client_record(tmp_path))],env=env,text=True,capture_output=True)
    assert done.returncode!=0 and "consequential approval" in done.stderr

def test_mvp_executable_rejects_content(tmp_path):
    (tmp_path/"controller.key").write_bytes(os.urandom(32)); (tmp_path/"controller.key").chmod(0o600)
    event=tmp_path/"event.json"; event.write_text(json.dumps(cron()))
    config=tmp_path/"config.json"; config.write_text(json.dumps({**cfg(),"content_required":True}))
    script=Path(__file__).parents[1]/"integration/lhm-seo-org-canary-mvp"
    env={**os.environ,"LHM_WORKFLOW_TEST_MODE":"1","PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    done=subprocess.run([str(script),str(event),"mvp-content",str(config),"--root",str(tmp_path),"--vault-root",str(client_record(tmp_path))],env=env,text=True,capture_output=True)
    assert done.returncode!=0 and "Content is disabled" in done.stderr

def test_mvp_executable_resumes_progressed_parent_without_reinitialising(tmp_path,monkeypatch):
    key=os.urandom(32)
    (tmp_path/"controller.key").write_bytes(key); (tmp_path/"controller.key").chmod(0o600)
    event=tmp_path/"event.json"; event.write_text(json.dumps(cron()))
    config=tmp_path/"config.json"; config.write_text(json.dumps(cfg()))
    keys={role:key for role in KEY_NAMES}; canary=Canary(tmp_path,keys,research=research(tmp_path,{"count":0}),trusted_internal=True)
    canary.initialise(cron(),"mvp-resume")
    contract=canary.router.issue("mvp-resume","mvp-resume:chief_intake")
    assert contract["stage_id"]=="chief_intake"
    script=Path(__file__).parents[1]/"integration/lhm-seo-org-canary-mvp"
    env={**os.environ,"LHM_WORKFLOW_TEST_MODE":"1","PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    done=subprocess.run([str(script),str(event),"mvp-resume",str(config),"--root",str(tmp_path),"--vault-root",str(client_record(tmp_path)),"--step"],env=env,text=True,capture_output=True)
    assert done.returncode==0,done.stderr
    assert json.loads(done.stdout)["cursor"]==1

def test_mvp_preflight_stops_when_client_capability_is_unverified(tmp_path):
    (tmp_path/"controller.key").write_bytes(os.urandom(32)); (tmp_path/"controller.key").chmod(0o600)
    event=tmp_path/"event.json"; event.write_text(json.dumps(cron()))
    config=tmp_path/"config.json"; config.write_text(json.dumps(cfg()))
    script=Path(__file__).parents[1]/"integration/lhm-seo-org-canary-mvp"
    env={**os.environ,"LHM_WORKFLOW_TEST_MODE":"1","PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    done=subprocess.run([str(script),str(event),"mvp-blocked",str(config),"--root",str(tmp_path),"--vault-root",str(client_record(tmp_path,"configured"))],env=env,text=True,capture_output=True)
    assert done.returncode!=0 and "client_onboarding_required" in done.stderr

def test_mvp_preflight_rejects_tampered_evidence(tmp_path):
    (tmp_path/"controller.key").write_bytes(os.urandom(32)); (tmp_path/"controller.key").chmod(0o600)
    event=tmp_path/"event.json"; event.write_text(json.dumps(cron()))
    config=tmp_path/"config.json"; config.write_text(json.dumps(cfg()))
    vault=client_record(tmp_path); (tmp_path/"gsc-evidence.json").write_text('{"tampered":true}')
    script=Path(__file__).parents[1]/"integration/lhm-seo-org-canary-mvp"
    env={**os.environ,"LHM_WORKFLOW_TEST_MODE":"1","PYTHONPATH":str(Path(__file__).parents[1]/"src")}
    done=subprocess.run([str(script),str(event),"mvp-tamper",str(config),"--root",str(tmp_path),"--vault-root",str(vault)],env=env,text=True,capture_output=True)
    assert done.returncode!=0 and "hash mismatch" in done.stderr
