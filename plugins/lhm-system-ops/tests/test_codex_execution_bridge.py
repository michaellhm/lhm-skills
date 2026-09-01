import importlib.util, io, json, subprocess, sys, tempfile
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_loader(name,SourceFileLoader(name,str(path))); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
worker=load('codex_execution_worker',ROOT/'assets/host/lhm-codex-execution-worker')
client=load('codex_execution_client',ROOT/'assets/container/lhm-codex-dispatch')

def request(**overrides):
    value={'schema_version':1,'request_id':'synthetic-1','parent_run_id':'telegram-parent-1','task_class':'generic_non_mutating','objective':'Summarise this bounded synthetic request.','permission_profile':'default-review-only','timeout_seconds':60,'created_at':'2026-09-01T00:00:00Z'}
    value.update(overrides); return value

def test_protected_client_accepts_exact_generic_contract(capsys):
    with tempfile.TemporaryDirectory() as temporary:
        client.BASE=Path(temporary)
        with mock.patch.object(sys,'argv',['lhm-codex-dispatch','submit']), mock.patch.object(sys,'stdin',io.StringIO(json.dumps(request()))): client.main()
        accepted=json.loads(capsys.readouterr().out)
        assert accepted['selected_worker']=='codex' and accepted['authentication_class']=='subscription-backed'
        assert (client.BASE/'incoming/synthetic-1.json').is_file()

def test_protected_client_rejects_duplicate_id():
    with tempfile.TemporaryDirectory() as temporary:
        client.BASE=Path(temporary)
        for _ in range(2):
            try:
                with mock.patch.object(sys,'argv',['lhm-codex-dispatch','submit']), mock.patch.object(sys,'stdin',io.StringIO(json.dumps(request()))): client.main()
            except SystemExit as exc:
                assert 'duplicate request_id' in str(exc); break
        else: raise AssertionError('duplicate accepted')

def test_generic_request_launches_subscription_codex_and_persists_receipt():
    with tempfile.TemporaryDirectory() as temporary:
        worker.BASE=Path(temporary); [ (worker.BASE/n).mkdir() for n in ('incoming','processing','receipts','incidents','failed','worker-runs') ]
        path=worker.BASE/'incoming/synthetic-1.json'; path.write_text(json.dumps(request()))
        def fake(args,**kwargs):
            if 'status' in args: return subprocess.CompletedProcess(args,0,'Logged in using ChatGPT\n','')
            out=Path(args[args.index('--output-last-message')+1]); out.write_text(json.dumps({'status':'completed','summary':'Synthetic result','worker':'codex'}))
            return subprocess.CompletedProcess(args,0,'{"type":"turn.completed"}\n','')
        with mock.patch.object(worker,'run_codex',side_effect=fake) as run: worker.process(path)
        receipt=json.loads((worker.BASE/'receipts/synthetic-1.json').read_text())
        assert receipt['selected_worker']=='codex' and receipt['selected_provider']=='openai-codex'
        assert receipt['authentication_class']=='subscription-backed' and receipt['permission_ceiling']=='review-only'
        command=run.call_args_list[1].args[0]
        assert '--ignore-user-config' in command and command[command.index('--sandbox')+1]=='read-only'

def test_marketing_and_knowledge_work_keep_codex_default():
    with tempfile.TemporaryDirectory() as temporary:
        for task in ('marketing','knowledge_work'):
            path=Path(temporary)/f'{task}.json'; value=request(request_id=task,task_class=task); path.write_text(json.dumps(value)); worker.validate(value,path)

def test_unregistered_write_profile_fails_closed():
    with tempfile.TemporaryDirectory() as temporary:
        path=Path(temporary)/'synthetic-1.json'; value=request(permission_profile='write-anywhere'); path.write_text(json.dumps(value))
        try: worker.validate(value,path)
        except ValueError as exc: assert 'unregistered permission profile' in str(exc)
        else: raise AssertionError('write profile accepted')

def test_stale_or_api_auth_is_rejected_without_worker_fallback():
    with mock.patch.object(worker,'run_codex',return_value=subprocess.CompletedProcess([],0,'Logged in with API key','')):
        try: worker.auth_status()
        except RuntimeError as exc: assert 'subscription authentication unavailable' in str(exc)
        else: raise AssertionError('metered auth accepted')

def test_environment_is_allowlisted_and_contains_no_metered_keys():
    assert set(worker.ENV)=={'HOME','CODEX_HOME','PATH'}
    source=(ROOT/'assets/host/lhm-codex-execution-worker').read_text()
    assert all(value not in source for value in ('OPENROUTER_API_KEY','ANTHROPIC_API_KEY','OPENAI_API_KEY','hermes-2'))

def test_service_has_no_docker_vault_root_or_host_shell_exposure():
    unit=(ROOT/'assets/systemd/lhm-codex-execution.service').read_text()
    assert 'InaccessiblePaths=' in unit and '/var/run/docker.sock' in unit and '/run/docker.sock' in unit and '/root' in unit
    assert '/profiles/lhm_brain/vault' in unit and 'ProtectSystem=strict' in unit
    assert 'ExecStart=/usr/local/libexec/lhm-codex-execution-worker' in unit
    assert 'User=codexworker' in unit
    assert '/home/codexworker/.codex' not in next(line for line in unit.splitlines() if line.startswith('ReadWritePaths='))

def test_root_owned_launch_repairs_only_codexworker_traversal_before_worker():
    unit=(ROOT/'assets/systemd/lhm-codex-execution.service').read_text()
    lines=unit.splitlines()
    acl_lines=[line for line in lines if line.startswith('ExecStartPre=')]
    assert acl_lines == [
        'ExecStartPre=+/usr/bin/setfacl -n -m m::--x,u:codexworker:--x /home/hermes/.hermes',
        'ExecStartPre=+/usr/bin/setfacl -n -m m::--x,u:codexworker:--x /home/hermes/.hermes/profiles/lhm_brain',
        'ExecStartPre=+/usr/bin/setfacl -n -m m::--x,u:codexworker:--x /home/hermes/.hermes/profiles/lhm_brain/dispatch/codex-execution',
    ]
    assert max(lines.index(line) for line in acl_lines) < lines.index('ExecStart=/usr/local/libexec/lhm-codex-execution-worker')
    assert all(line.startswith('ExecStartPre=+/usr/bin/setfacl -n -m ') for line in acl_lines)
    assert all('m::--x,u:codexworker:--x' in line for line in acl_lines)
    assert all('-R' not in line and 'vault' not in line and 'rwx' not in line for line in acl_lines)
    assert not any(entry in '\n'.join(acl_lines) for entry in ('u:claudeworker:','u:hermes:','u:root:'))
