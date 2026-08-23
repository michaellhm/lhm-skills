import hashlib,json,os
from pathlib import Path
from lhm_workflow.org_canary import Canary,KEY_NAMES,load_keys
from test_org_routing import cron

def make_canary(tmp_path,monkeypatch):
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE","1")
    key=os.urandom(32); keys={role:key for role in KEY_NAMES}
    return Canary(tmp_path,keys,research=research(tmp_path),trusted_internal=True)
def research(canary_root):
    def call(parent,contract,config):
        path=canary_root/"real-research.md"; path.write_text("verified GSC research\n"); path.chmod(0o600)
        artifact={"artifact_id":f"{parent}:research","sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"media_type":"text/markdown"}
        return artifact,path
    return call

def config(): return {"objective":"Governed weekly SEO research","site_property":"https://localhealthmarketing.com/","urls":["https://localhealthmarketing.com/seo/"],"completed_at":"2026-08-23T18:00:00Z","content_required":False}

def test_manual_step_restart_no_website_no_delivery_and_complete_bundle(tmp_path,monkeypatch):
    c=make_canary(tmp_path,monkeypatch); c.initialise(cron(),"canary-1")
    state=c.run("canary-1",config(),step=True); assert state["cursor"]==1
    # Restart from disk through a new orchestrator instance.
    c2=Canary(tmp_path,c.keys,research=research(tmp_path),trusted_internal=True); state=c2.run("canary-1",config())
    assert state["state"]=="closed" and "website" not in state["stage_order"]
    assert state["delivery"]=={"channel":"suppressed_canary","status":"suppressed"}
    bundle=json.loads((tmp_path/"evidence/canary-1.json").read_text()); assert bundle["parent_sha256"] and bundle["artifact_hashes"]
    assert (tmp_path/"vault/30 Projects/LHM Website SEO Growth Rollout/rollout-state.md").is_file()

def test_pause_after_and_content_fails_closed_without_adapter(tmp_path,monkeypatch):
    c=make_canary(tmp_path,monkeypatch); c.initialise(cron(),"canary-2")
    state=c.run("canary-2",config(),pause_after="research"); assert state["stages"][-1]["stage_id"]=="research"
    cfg={**config(),"content_required":True}
    # Advance through research verification/SEO acceptance, then stop at missing governed Content adapter.
    try: c.run("canary-2",cfg)
    except ValueError as exc: assert "content required" in str(exc)
    else: raise AssertionError("missing Content adapter must fail closed")

def test_research_checkpoint_prevents_reinvoke_after_crash(tmp_path,monkeypatch):
    c=make_canary(tmp_path,monkeypatch); calls={"count":0}; base_research=research(tmp_path)
    def counted(*args): calls["count"]+=1; return base_research(*args)
    c.research=counted; c.initialise(cron(),"canary-crash")
    monkeypatch.setenv("LHM_CANARY_FAULT","after_external_before_accept")
    try: c.run("canary-crash",config())
    except RuntimeError: pass
    monkeypatch.delenv("LHM_CANARY_FAULT")
    c.run("canary-crash",config()); assert calls["count"]==1

def test_tracker_reconciles_crash_without_duplicate_append(tmp_path,monkeypatch):
    c=make_canary(tmp_path,monkeypatch); c.initialise(cron(),"canary-tracker-crash")
    monkeypatch.setenv("LHM_CANARY_FAULT","after_tracker_before_checkpoint")
    try: c.run("canary-tracker-crash",config())
    except RuntimeError: pass
    monkeypatch.delenv("LHM_CANARY_FAULT")
    state=c.run("canary-tracker-crash",config()); assert state["state"]=="closed"
    raw=c.tracker.path.read_text(); assert raw.count("## Governed run canary-tracker-crash")==1

def test_evidence_bundle_is_strictly_parent_scoped(tmp_path,monkeypatch):
    c=make_canary(tmp_path,monkeypatch)
    c.initialise(cron(),"parent-one"); c.run("parent-one",config())
    c.initialise(cron(),"parent-two"); c.run("parent-two",config())
    # Rebuild the first bundle after the shared stores contain the second run.
    c._bundle("parent-one")
    bundle=json.loads((tmp_path/"evidence/parent-one.json").read_text())
    encoded=json.dumps(bundle,sort_keys=True)
    assert "parent-two" not in encoded
    assert bundle["operations"] and bundle["role-receipts"]
    assert all(key.startswith("parent-one:") for key in bundle["artifact_registry"]["value"])
    tracker=bytes.fromhex(bundle["tracker"]["bytes_hex"]).decode()
    assert "## Governed run parent-one" in tracker and "parent-two" not in tracker
