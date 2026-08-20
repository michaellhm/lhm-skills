import importlib.util, json, subprocess
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock
import pytest

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'assets/host/lhm-source-production-runtime'
spec=importlib.util.spec_from_loader('source_runtime',SourceFileLoader('source_runtime',str(HELPER)))
runtime=importlib.util.module_from_spec(spec); spec.loader.exec_module(runtime)

def manifest(run='wellness-run'):
    return {'schema_version':1,'run_id':run,'parent_run_id':'campaign-playbook-flow-20260818-01','saved_role':'Context and Research','return_point':'context_research.acquire_required_sources','source_policy':'all_required','sources':[{'source_id':'wellness-drive','kind':'google_drive_file','allowlisted_identifier':'drive-wellness-exact','required':True},{'source_id':'strategy-call','kind':'fathom_transcript','allowlisted_identifier':12345,'required':True}],'production':{'packaged_worker':'campaign_playbook_production','publisher':'registered_google_drive_publisher','destination_allowlisted_identifier':'drive-output-exact'}}

def setup(tmp_path,m):
    base=tmp_path/'dispatch'; incoming=base/'incoming'; incoming.mkdir(parents=True)
    for name in ('processed','failed','runs','events','consumed'): (base/name).mkdir()
    registry=tmp_path/'registry'; registry.mkdir()
    (registry/(m['run_id']+'.json')).write_text(json.dumps({'schema_version':1,'run_id':m['run_id'],'sources':[{'kind':'google_drive_file','identifier':'drive-wellness-exact'},{'kind':'fathom_transcript','identifier':12345}],'destination_identifier':'drive-output-exact'}))
    path=incoming/(m['run_id']+'.json'); path.write_text(json.dumps(m))
    values={'BASE':base,'INCOMING':incoming,'PROCESSED':base/'processed','FAILED':base/'failed','RUNS':base/'runs','EVENTS':base/'events'}
    return registry,path,values

class Result:
    def __init__(self,code=0,out=b'',err=b''): self.returncode=code; self.stdout=out; self.stderr=err

def test_healthy_fake_connectors_receipts_child_and_full_readback(tmp_path):
    m=manifest(); registry,path,values=setup(tmp_path,m); calls=[]
    def runner(argv,**kwargs):
        command=argv[-1]; calls.append(command)
        if command==runtime.PREFLIGHT: return Result(out=b'{"preflight":"ok"}')
        if command==runtime.CONNECTORS['google_drive_file']: return Result(out=b'Wellness file complete')
        if command==runtime.CONNECTORS['fathom_transcript']: return Result(out=b'Fathom transcript complete')
        if command==runtime.PACKAGED_WORKER:
            package=json.loads(kwargs['input'])
            assert [x['content'] for x in package['sources']]==['Wellness file complete','Fathom transcript complete']
            return Result(out=b'Complete production playbook')
        if command==runtime.PUBLISHER: return Result(out=json.dumps({'full_content':'Complete production playbook'}).encode())
        raise AssertionError(argv)
    with mock.patch.multiple(runtime,**values):
        assert runtime.process(path,runner,registry)=='delivered'
        run=values['RUNS']/m['run_id']
        assert len(list(run.glob('*.receipt.json')))==2
        assert (run/'production-child.json').is_file()
        delivery=json.loads((run/'delivery-receipt.json').read_text())
        assert delivery['full_content_read_back'] and delivery['published_content_sha256']==delivery['read_back_content_sha256']

def test_drive_failure_persists_one_parent_one_incident_and_no_completion(tmp_path):
    m=manifest('failed-run'); registry,path,values=setup(tmp_path,m); work=[]
    def runner(argv,**kwargs):
        command=argv[-1]
        if command==runtime.PREFLIGHT: return Result(out=b'{"preflight":"ok"}')
        if command==runtime.CONNECTORS['google_drive_file']: return Result(1,err=b'controlled unavailable')
        if command==runtime.WORK_CONTROL: work.append(json.loads(kwargs['input'])); return Result(out=b'{}')
        raise AssertionError(argv)
    with mock.patch.multiple(runtime,**values):
        assert runtime.process(path,runner,registry)=='blocked'
        run=values['RUNS']/m['run_id']
        assert json.loads((run/'blocker.json').read_text())['blocker_kind']=='google_drive_read_unavailable'
        assert len(work)==1 and not (run/'production-child.json').exists() and not (run/'delivery-receipt.json').exists()
        assert len(list(values['RUNS'].iterdir()))==1

def test_registration_rejects_arbitrary_identifier(tmp_path):
    m=manifest('reject-run'); registry,path,values=setup(tmp_path,m)
    m['sources'][0]['allowlisted_identifier']='arbitrary-drive-id'
    with pytest.raises(ValueError,match='not registered'):
        runtime.validate_manifest(m,path.name,registry)

def test_matching_restoration_resumes_exactly_once(tmp_path):
    m=manifest('resume-run'); registry,path,values=setup(tmp_path,m)
    run=values['RUNS']/m['run_id']; run.mkdir()
    blocker={'schema_version':1,'type':'capability_blocker','blocker_kind':'google_drive_read_unavailable','capability_incident_id':'resume-run:wellness-drive','parent_run_id':m['parent_run_id'],'saved_role':m['saved_role'],'return_point':m['return_point'],'source_id':'wellness-drive','route':'lhm-cto','reason':'x','created_at':'now'}
    (run/'blocker.json').write_text(json.dumps(blocker))
    event={k:blocker[k] for k in ('capability_incident_id','parent_run_id','saved_role','return_point')}
    event.update(schema_version=1,event='capability_restored',event_id='restore-one',created_at='now')
    ep=tmp_path/'event.json'; ep.write_text(json.dumps(event)); calls=[]
    def runner(argv,**kwargs): calls.append(json.loads(kwargs['input'])); return Result(out=b'{}')
    with mock.patch.multiple(runtime,**values):
        assert runtime.consume_restored(ep,runner)=='resumed'
        assert runtime.consume_restored(ep,runner)=='duplicate'
    assert len(calls)==1 and calls[0]['role']==m['saved_role'] and calls[0]['return_point']==m['return_point']

def test_capability_restored_producer_consumer_and_parent_transition_e2e(tmp_path):
    m=manifest('contract-e2e'); registry,path,values=setup(tmp_path,m)
    run=values['RUNS']/m['run_id']; run.mkdir()
    blocker={'schema_version':1,'type':'capability_blocker','blocker_kind':'google_drive_read_unavailable','capability_incident_id':'contract-e2e:wellness-drive','parent_run_id':m['parent_run_id'],'saved_role':m['saved_role'],'return_point':m['return_point'],'source_id':'wellness-drive','route':'lhm-cto','reason':'x','created_at':'now'}
    (run/'blocker.json').write_text(json.dumps(blocker))
    emitted=runtime.capability_restored_event(blocker,'restore-contract-e2e','2026-08-20T00:00:00+00:00')
    schema=json.loads((ROOT/'references/capability-restored.schema.json').read_text())
    assert set(emitted)==set(schema['required'])
    event_path=tmp_path/'emitted-capability-restored.json'; event_path.write_text(json.dumps(emitted)); transitions=[]
    def runner(argv,**kwargs): transitions.append(json.loads(kwargs['input'])); return Result(out=b'{}')
    with mock.patch.multiple(runtime,**values):
        assert runtime.consume_restored(event_path,runner)=='resumed'
    assert transitions==[{'schema_version':1,'event':'resume_saved_role','parent_run_id':m['parent_run_id'],'role':m['saved_role'],'return_point':m['return_point'],'capability_incident_id':blocker['capability_incident_id']}]

def test_security_profile_and_role_skills_fail_closed():
    profile=json.loads((ROOT/'assets/worker/source-production-worker-profile.json').read_text())
    assert all(command.startswith('/usr/local/libexec/') for command in profile['commands'])
    assert {'credential_files','raw_tokens','ssh','docker','host_shell','unrestricted_filesystem','basicops_mutation'} <= set(profile['denied'])
    for role in ('lhm-chief-of-staff-source-handoff','lhm-context-research-source-handoff','lhm-cto-source-handoff','lhm-head-of-production-source-handoff'):
        text=(ROOT/'skills'/role/'SKILL.md').read_text()
        assert 'source-dispatch' in text or 'host runtime' in text
    assert 'missing or mismatched receipt is a hard stop' in (ROOT/'skills/lhm-context-research-source-handoff/SKILL.md').read_text()

def test_outage_regressions_are_encoded():
    import shlex
    unit=(ROOT/'assets/systemd/lhm-source-production.service').read_text()
    assert '"/home/hermes/.hermes/profiles/lhm_brain/vault/01 Inbox/Hermes Reviews"' in unit
    line=next(x for x in unit.splitlines() if x.startswith('ReadWritePaths='))
    assert shlex.split(line.split('=',1)[1])[-1]=='/home/hermes/.hermes/profiles/lhm_brain/vault/01 Inbox/Hermes Reviews'
    dispatcher=(ROOT/'assets/host/lhm-cto-plugin-dispatcher').read_text()
    publisher=(ROOT/'assets/host/lhm-cto-branch-publisher').read_text()
    assert "--untracked-files=all" in dispatcher and "--untracked-files=all" in publisher
