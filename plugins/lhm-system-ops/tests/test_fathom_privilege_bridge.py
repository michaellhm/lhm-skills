import importlib.util, importlib.machinery, io, json, subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'assets/host/lhm-evidence-fathom-backend'

def load_helper():
    loader=importlib.machinery.SourceFileLoader('fathom_privilege_bridge',str(HELPER))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def request(**changes):
    return {"action":"read","identifier":123,"run_id":"run-one",**changes}

def registered_helper(tmp_path, monkeypatch, registration=None):
    helper=load_helper(); helper.REGISTRY=tmp_path
    value=registration or {"run_id":"run-one","sources":[{"kind":"fathom_transcript","identifier":123}]}
    (tmp_path/'run-one.json').write_text(json.dumps(value))
    original=Path.stat
    monkeypatch.setattr(Path,'stat',lambda self,*a,**k: SimpleNamespace(st_uid=0,st_mode=0o100640) if self.name=='run-one.json' else original(self,*a,**k))
    return helper

def test_registered_request_builds_only_fixed_docker_argv(tmp_path,monkeypatch):
    helper=registered_helper(tmp_path,monkeypatch); value=helper.load_request(io.StringIO(json.dumps(request())))
    helper.registered(value); argv=helper.command(value)
    assert argv[:7]==['/usr/bin/docker','exec','-i','-u','hermes','hermes','/opt/hermes/.venv/bin/hermes']
    assert argv[-2:]==['--skills','fathom-meeting-lookup'] and '123' in argv[-3]
    assert 'sh' not in argv and 'bash' not in argv and 'ps' not in argv

def test_unprivileged_fixture_probe_and_read_cross_only_the_bridge(tmp_path,monkeypatch):
    helper=registered_helper(tmp_path,monkeypatch); calls=[]
    payload=json.dumps({"recording_id":123,"transcript":"transcript"}).encode()
    monkeypatch.setattr(helper.subprocess,'run',lambda argv,**kwargs: calls.append(argv) or SimpleNamespace(returncode=0,stdout=payload))
    for action in ('probe','read'):
        value=request(action=action); helper.registered(helper.load_request(io.StringIO(json.dumps(value))))
        done=helper.subprocess.run(helper.command(value))
        assert json.loads(done.stdout)=={"recording_id":123,"transcript":"transcript"} and calls[-1][0]=='/usr/bin/docker'
    profile=json.loads((ROOT/'assets/worker/source-production-worker-profile.json').read_text())
    assert 'docker' in profile['denied'] and all('docker' not in command for command in profile['commands'])

@pytest.mark.parametrize('stdout',[b'transcript',b'{}',b'{"recording_id":124,"transcript":"transcript"}',b'{"recording_id":123,"transcript":""}'])
def test_backend_rejects_unbound_or_empty_hermes_output(tmp_path,monkeypatch,stdout):
    helper=registered_helper(tmp_path,monkeypatch)
    monkeypatch.setattr(helper.subprocess,'run',lambda *a,**k: SimpleNamespace(returncode=0,stdout=stdout))
    monkeypatch.setattr(helper.sys,'stdin',io.StringIO(json.dumps(request())))
    monkeypatch.setattr(helper.sys,'argv',[str(HELPER)])
    with pytest.raises(SystemExit): helper.main()

@pytest.mark.parametrize('value',[request(extra=True),request(identifier='123'),request(identifier=True),request(identifier=0),request(run_id='../x'),request(run_id='bad/run')])
def test_bad_schema_ids_and_run_ids_fail_closed(value):
    helper=load_helper()
    with pytest.raises(SystemExit): helper.load_request(io.StringIO(json.dumps(value)))

def test_unregistered_and_mismatched_registration_fail_before_docker(tmp_path,monkeypatch):
    for registration in ({"run_id":"run-one","sources":[]},{"run_id":"other","sources":[{"kind":"fathom_transcript","identifier":123}]}):
        helper=registered_helper(tmp_path,monkeypatch,registration)
        with pytest.raises(SystemExit): helper.registered(request())

def test_helper_arguments_fail_before_docker(monkeypatch):
    helper=load_helper(); called=[]; monkeypatch.setattr(helper.subprocess,'run',lambda *a,**k: called.append(a))
    monkeypatch.setattr(helper.sys,'argv',[str(HELPER),'docker','ps'])
    with pytest.raises(SystemExit): helper.main()
    assert called==[]

def test_policy_and_adapter_are_exact_and_non_recursive():
    sudoers=(ROOT/'assets/sudoers/lhm-evidence-fathom-backend').read_text()
    adapter=(ROOT/'assets/host/lhm-source-adapter').read_text()
    assert '/usr/local/libexec/lhm-evidence-fathom-backend ""' in sudoers
    assert 'NOPASSWD: LHM_FATHOM_BACKEND' in sudoers and '/usr/bin/docker' not in sudoers
    assert '["/usr/bin/sudo", "-n", "/usr/local/libexec/lhm-evidence-fathom-backend"]' in adapter
    assert 'lhm-fathom-transcript-read' not in sudoers

def test_installer_validates_policy_and_never_enables_path():
    installer=(ROOT/'assets/install/install-source-production.sh').read_text()
    assert '-m 0440 assets/sudoers/lhm-evidence-fathom-backend' in installer
    assert "root:root 440" in installer
    assert '/usr/sbin/visudo -cf' in installer
    assert 'systemctl enable' not in installer and 'systemctl start' not in installer
    assert 'usermod' not in installer and 'docker group' not in installer
    assert 'sourceworker must not have docker-group membership' in installer
    release=(ROOT/'references/source-production-release.md').read_text()
    assert '/etc/sudoers.d/lhm-evidence-fathom-backend' in release
