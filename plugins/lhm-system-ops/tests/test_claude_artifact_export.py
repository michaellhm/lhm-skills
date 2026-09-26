import hashlib
import importlib.util
import json
import os
import stat
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

PLUGIN=Path(__file__).resolve().parents[1]


def load(name,path):
    spec=importlib.util.spec_from_loader(name,SourceFileLoader(name,str(path)))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


EXPORTER=load('artifact_exporter',PLUGIN/'assets/gateways/lhm-claude-artifact-exporter')
SUBMITTER=load('artifact_submitter',PLUGIN/'assets/gateways/lhm-claude-artifact-submit')


def request():
    return {'schema_version':1,'kind':'claude_specialist_artifact_export','request_id':'a'*32,
            'run_id':'claude-delegate-20260824-01','parent_run_id':'parent-1','action_id':'seo-1',
            'action_version':1,'predecessor_sha256':'b'*64}


def terminal(runs,result=b'exact specialist result\n'):
    run=runs/request()['run_id'];run.mkdir(parents=True)
    contract={'workflow_id':'seo-lead-review','required_skills':['lhm-marketing-hub:start-seo'],
              'required_capabilities':[],'skill_provenance':'observed'}
    final={'run_id':request()['run_id'],'status':'needs_review','profile':'specialist_readonly',
           'agent_id':'lhm-marketing-hub:seo','completed_at':'2026-08-24T00:00:00+00:00',
           'result_file':'result.md','workflow_contract':contract,
           'skill_provenance_file':'skill-provenance.json'}
    provenance={'verification':'passed','workflow_id':'seo-lead-review','entrypoint':'lhm-marketing-hub:seo',
                'required_skills':['lhm-marketing-hub:start-seo'],
                'observed_skill_calls':['lhm-marketing-hub:start-seo']}
    (run/'final.json').write_text(json.dumps(final));(run/'skill-provenance.json').write_text(json.dumps(provenance));(run/'result.md').write_bytes(result)
    return run


def roots(tmp_path):
    root=tmp_path/'export';runs=tmp_path/'protected-runs';handback=tmp_path/'adapter-incoming'
    for child in ('artifacts','operations','incidents','accepted','locks'): (root/child).mkdir(parents=True,exist_ok=True)
    runs.mkdir();handback.mkdir();(root/'locks/exporter.key').write_bytes(b'k'*32)
    return root,runs,handback


def test_submitter_accepts_no_source_path_and_uses_write_only_create(tmp_path):
    incoming=tmp_path/'incoming';incoming.mkdir();os.chmod(incoming,0o300)
    built=SUBMITTER.build_request(request()['run_id'],'parent-1','seo-1',1,'b'*64)
    assert 'source_path' not in built and set(built)==EXPORTER.REQUEST_KEYS
    SUBMITTER.submit(built,incoming)
    os.chmod(incoming,0o700)
    assert len(list(incoming.iterdir()))==1


def test_descriptor_safe_export_preserves_exact_bytes_and_is_idempotent(tmp_path):
    root,runs,handback=roots(tmp_path);result=b'exact specialist result\n';terminal(runs,result)
    receipt=EXPORTER.export(request(),root,runs,handback,b'k'*32)
    assert receipt['source_disclosure']=='none' and receipt['drive_published'] is False
    assert receipt['predecessor_sha256']=='b'*64 and receipt['result_sha256']==hashlib.sha256(result).hexdigest()
    artifact=root/'artifacts/sha256'/receipt['result_sha256'][:2]/receipt['result_sha256']
    assert artifact.read_bytes()==result
    assert EXPORTER.export(request(),root,runs,handback,b'k'*32)==receipt


@pytest.mark.parametrize('target',('final.json','skill-provenance.json','result.md'))
def test_symlink_terminal_artifacts_fail_closed(tmp_path,target):
    root,runs,handback=roots(tmp_path);run=terminal(runs);outside=tmp_path/'outside';outside.write_text('stolen')
    (run/target).unlink();(run/target).symlink_to(outside)
    with pytest.raises(OSError): EXPORTER.export(request(),root,runs,handback,b'k'*32)


def test_real_current_specialist_schema_rejects_fabricated_worker_fields(tmp_path):
    root,runs,handback=roots(tmp_path);run=terminal(runs)
    final=json.loads((run/'final.json').read_text());final['artifacts']=[];(run/'final.json').write_text(json.dumps(final))
    with pytest.raises(EXPORTER.PermanentError,match='current specialist terminal schema'):
        EXPORTER.export(request(),root,runs,handback,b'k'*32)


def test_permanent_failure_incidents_immediately_and_transient_retries_once(tmp_path):
    root,runs,handback=roots(tmp_path);incoming=tmp_path/'incoming';incoming.mkdir()
    bad=request();bad['source_path']='/home/hermes/secret';path=incoming/'bad.json';path.write_text(json.dumps(bad))
    assert EXPORTER.process(path,root,runs,handback) is True
    assert (root/'incidents'/f"{bad['request_id']}.json").is_file()
    missing=request();missing['request_id']='c'*32;retry=incoming/'retry.json';retry.write_text(json.dumps(missing))
    assert EXPORTER.process(retry,root,runs,handback) is False
    assert not (root/'incidents'/f"{missing['request_id']}.json").exists()
    assert EXPORTER.process(retry,root,runs,handback) is True
    assert (root/'incidents'/f"{missing['request_id']}.json").is_file()
    lines=(root/'operations'/f"{missing['request_id']}.jsonl").read_text().splitlines()
    assert len(lines)==2 and '"type":"retry"' in lines[0] and '"type":"incident"' in lines[1]


def test_packaging_boundaries_and_600_610_630_lease_order():
    service=(PLUGIN/'assets/systemd/lhm-claude-artifact-export.service').read_text()
    worker=(PLUGIN/'assets/gateways/lhm-shared-claude-worker').read_text()
    installer=(PLUGIN/'assets/install/install-shared-claude-gateway.py').read_text()
    assert "'timeout_seconds': 600" in (PLUGIN/'assets/container/claude-dispatch').read_text()
    assert 'TimeoutStartSec=610' in service and SUBMITTER.CALLER_LEASE_SECONDS==630
    assert 'ReadOnlyPaths=/home/hermes/.hermes/profiles/lhm_brain/dispatch/claude/runs' in service
    assert "('incoming', 0o730, workflow_gid)" in installer
    assert "('artifacts', 0o2750, adapter_gid)" in installer
    assert "systemctl', 'enable'" not in installer and "systemctl', 'start'" not in installer
    assert "parse stdout" not in EXPORTER.__doc__.lower()
