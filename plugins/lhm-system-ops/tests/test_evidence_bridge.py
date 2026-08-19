import hashlib, importlib.util, json, os
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location("evidence_bridge",ROOT/"scripts/evidence_bridge.py")
bridge=importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)

class Drive:
    def __init__(self): self.files={}; self.created=0; self.folders=[]
    def get_file_metadata(self,i):
        if i in self.files: return {"id":i,"name":self.files[i][0],"parent_id":self.files[i][1]}
        return {"id":i,"name":"Client","mime_type":"application/vnd.google-apps.folder"}
    def search_folders_exact(self,name): return self.folders
    def read_exact_file(self,i,t): return b"drive source","text/plain"
    def search_exact_name(self,folder,name): return [{"id":i} for i,v in self.files.items() if v[:2]==(name,folder)]
    def create_file(self,folder,name,content):
        self.created+=1; self.files["new"]=(name,folder,content); return "new"
    def read_file_content(self,i): return self.files[i][2]

class Fathom:
    def get_meeting_transcript(self,recording_id,timeout): return "transcript"

class Producer:
    def produce_campaign_playbook(self,drive,fathom,name,timeout): return b"# Complete playbook\n"+drive+b"\n"+fathom

def req(profile,**extra):
    base={"schema_version":1,"run_id":"run-1","profile":profile,"agent_id":"lhm-connector-repair","client":"Client","timeout_seconds":30}
    return {**base,**extra}

def test_canonical_overview_is_checked_before_search(tmp_path):
    p=tmp_path/"Client.md"; p.write_text("## Systems and files\n- Drive: https://drive.google.com/drive/folders/folder_1\n")
    d=Drive(); assert bridge.discover_client_folder(p,"Client",d)==("folder_1",False)

def test_missing_folder_unique_discovery_writes_only_verified_link(tmp_path):
    p=tmp_path/"Client.md"; p.write_text("# Client\n")
    d=Drive(); d.folders=[{"id":"folder_2"}]
    assert bridge.discover_client_folder(p,"Client",d)==("folder_2",True)
    assert p.read_text().endswith("- Google Drive folder: https://drive.google.com/drive/folders/folder_2\n")

@pytest.mark.parametrize("folders",[[],[{"id":"a"},{"id":"b"}]])
def test_missing_or_ambiguous_folder_uses_resumable_incident(tmp_path,folders):
    p=tmp_path/"Client.md"; p.write_text("# Client\n"); d=Drive(); d.folders=folders
    with pytest.raises(bridge.CapabilityUnavailable) as error: bridge.discover_client_folder(p,"Client",d)
    assert error.value.result["status"]=="waiting_on_capability"
    assert error.value.result["resume_token"]=="campaign-playbook-flow-20260818-resume-01"

def test_drive_read_is_exact_registered_id_and_mode_0640(tmp_path):
    r=req("google_drive_exact_file_read",file_id="file_1")
    out=bridge.drive_exact_read(r,{"drive_source_file_id":"file_1"},Drive(),tmp_path)
    assert out["file_id"]=="file_1" and out["sha256"]==hashlib.sha256(b"drive source").hexdigest()
    assert os.stat(out["content_file"]).st_mode & 0o777==0o640

def test_drive_read_refuses_unregistered_id(tmp_path):
    with pytest.raises(bridge.CapabilityUnavailable): bridge.drive_exact_read(req("google_drive_exact_file_read",file_id="wrong"),{"drive_source_file_id":"right"},Drive(),tmp_path)

def test_fathom_uses_exact_numeric_recording(tmp_path):
    out=bridge.fathom_exact_read(req("fathom_exact_recording_read",recording_id=123),{"fathom_recording_id":123},Fathom(),tmp_path)
    assert out["recording_id"]==123 and out["byte_count"]==10

def test_production_hash_binds_both_sources(tmp_path):
    d=bridge.bounded_artifact(tmp_path,"run-1","d",b"D"); f=bridge.bounded_artifact(tmp_path,"run-1","f",b"F")
    request={**req("campaign_playbook_production",agent_id="lhm-marketing-hub:content"),"drive_source_file":str(d),"drive_source_sha256":bridge.sha256_bytes(b"D"),"fathom_source_file":str(f),"fathom_source_sha256":bridge.sha256_bytes(b"F"),"output_file_name":"playbook.md"}
    result=bridge.produce(request,Producer(),tmp_path); assert result["byte_count"]>len(b"D\nF")
    request["drive_source_sha256"]="0"*64
    with pytest.raises(ValueError): bridge.produce(request,Producer(),tmp_path)

def publish_req(tmp_path,content=b"artifact"):
    path=bridge.bounded_artifact(tmp_path,"run-1","artifact.md",content)
    return {**req("google_drive_exact_folder_publish",folder_id="folder",file_name="Playbook.md",content_file=str(path),content_sha256=bridge.sha256_bytes(content))}

def test_publish_create_and_full_readback(tmp_path):
    d=Drive(); result=bridge.publish(publish_req(tmp_path),{"destination_drive_folder_id":"folder"},d,tmp_path)
    assert result["status"]=="created" and d.created==1

def test_publish_identical_is_idempotent(tmp_path):
    d=Drive(); d.files["same"]=("Playbook.md","folder",b"artifact")
    result=bridge.publish(publish_req(tmp_path),{"destination_drive_folder_id":"folder"},d,tmp_path)
    assert result["status"]=="already_existed" and d.created==0

def test_publish_differing_content_refuses_without_mutation(tmp_path):
    d=Drive(); d.files["same"]=("Playbook.md","folder",b"different")
    result=bridge.publish(publish_req(tmp_path),{"destination_drive_folder_id":"folder"},d,tmp_path)
    assert result["status"]=="refused"
    assert d.created==0

def test_logs_exclude_content_and_paths():
    logged=bridge.safe_log({"status":"created","byte_count":3,"sha256":"a"*64,"content_file":"secret","full_content":"secret"})
    assert logged=={"status":"created","byte_count":3,"sha256":"a"*64}

def test_contracts_are_strict_and_secret_free():
    paths=list((ROOT/"references/evidence-bridge").glob("*.schema.json")); assert len(paths)==8
    for path in paths:
        data=json.loads(path.read_text()); assert data["additionalProperties"] is False
        text=path.read_text().lower(); assert not any(word in text for word in ("password","oauth_token","api_key","secret"))

def test_gateway_assets_pin_verified_paths_and_tools():
    dispatcher=(ROOT/"assets/gateways/lhm-evidence-claude-dispatcher").read_text()
    worker=(ROOT/"assets/gateways/lhm-evidence-claude-worker").read_text()
    fathom=(ROOT/"assets/gateways/lhm-evidence-fathom-backend").read_text()
    assert "/usr/local/libexec/lhm-evidence-claude-worker" in dispatcher
    assert "/home/claudeworker/.local/bin/claude" in worker
    assert 'invoke(prompt, "content"' in worker and 'payload.get("result")' in worker
    assert '"HOME": HOME' in worker and "/home/claudeworker-repair" in worker
    assert "mcp__fathom__get_meeting_transcript" in fathom and '"exec", "-i", "-u", "hermes", "hermes"' in fathom
    assert '"-p", "lhm_brain", "-z"' in fathom and '"--skills", "fathom-meeting-lookup"' in fathom

def test_installer_fails_closed_and_does_not_enable_service():
    text=(ROOT/"assets/install/install-source-production.sh").read_text()
    assert "lhm-evidence-bridge-preflight" in text and "evidence-routes.json" in text
    assert "systemctl enable" not in text
    assert "install -D -m 0755 assets/gateways/lhm-claude-dispatcher" not in text
    assert "install -D -m 0755 assets/gateways/lhm-claude-worker" not in text
    assert text.count("verify_shared") >= 3 and "systemctl is-enabled lhm-source-production.path" in text
    assert "dbcb320cbb0b3f6fd036e7129c2cc4d37b688ac4d4af50bae5470e497d487f95" in text
    assert "ec28d515a37bd3f10e2a2dedf5080a3eb3529065da4b4bc0445ce080a705a531" in text

def test_rollback_preserves_registrations_and_evidence():
    text=(ROOT/"references/source-production-release.md").read_text()
    assert "Exact rollback inventory" in text
    assert "Never restore, remove, or otherwise mutate `/usr/local/libexec/lhm-claude-dispatcher`" in text
    assert "remove each path recorded absent" in text and "Reject an inventory with any other path" in text

def test_host_and_container_preflights_are_separate():
    preflight=(ROOT/"assets/install/preflight-evidence-bridge.py").read_text()
    release=(ROOT/"references/source-production-release.md").read_text()
    assert "/home/hermes/.hermes/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md" in preflight
    assert "/opt/data/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md" not in preflight
    assert "docker exec -i -u hermes hermes test -r /opt/data/profiles" in release
