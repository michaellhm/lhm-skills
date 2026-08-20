import hashlib, importlib.util, json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock
import pytest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_loader(name,SourceFileLoader(name,str(path))); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
dispatch=load('prototype_dispatch',ROOT/'assets/container/prototype-dispatch')
runtime=load('prototype_publication_runtime',ROOT/'assets/host/lhm-prototype-publication-runtime')

def request(source,request_id='publish-001'):
    data={'alpha-health/sitemap/index.html':b'<title>sealed</title>','alpha-health/sitemap/styles/site.css':b'body{}'}; manifest=[]
    for relative,content in data.items():
        path=source/relative; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(content); manifest.append({'path':relative,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)})
    manifest.sort(key=lambda x:x['path'])
    return {'schema_version':3,'request_id':request_id,'source_basicops_task':'task-123','governed_parent':'RTB-SITEMAP-PUBLISH-2188809-20260820','destination_profile_id':'prototype-main-v1','operation':'publish_sitemap','credential_reference':'LHM_PROTOTYPE_MAIN_DEPLOY_KEY','client_slug':'alpha-health','project_slug':'sitemap','prototype_kind':'sitemap','repository':'michaellhm/lhm-prototype','branch':'main','expected_base_commit':'a'*40,'source_directory':str(source),'source_package_sha256':dispatch.package_digest(manifest),'file_manifest':manifest,'qa_evidence_reference':'qa-123','idempotency_key':request_id,'standing_authority_reference':'MICHAEL-PROTOTYPE-PUBLISH-STANDING-20260820','commit_message':'prototype: alpha-health/sitemap approved static package'}

def queued_bundle(tmp_path,value):
    bundle=tmp_path/'queue'/value['request_id']; source=bundle/'source'; source.mkdir(parents=True)
    original=Path(value['source_directory'])
    for item in value['file_manifest']:
        target=source/item['path']; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes((original/item['path']).read_bytes())
    queued={**value,'source_directory':'source'}; (bundle/'request.json').write_text(json.dumps(queued)); return bundle

def test_container_helper_accepts_exact_sealed_package_and_has_no_host_key_access(tmp_path):
    sealed=tmp_path/'sealed'; source=sealed/'publish-001'; source.mkdir(parents=True); value=request(source)
    with mock.patch.object(dispatch,'SEALED_ROOT',sealed): assert dispatch.validate(value)==source
    text=(ROOT/'assets/container/prototype-dispatch').read_text()
    assert '/etc/lhm-prototype-publisher' not in text and 'id_ed25519' not in text
    unit=(ROOT/'assets/systemd/lhm-prototype-publication.service').read_text()
    assert 'InaccessiblePaths=/home/hermes/.hermes/profiles/lhm_brain/dispatch/prototype-publication/sealed' in unit

@pytest.mark.parametrize('updates',[
    {'source_directory':'/etc'}, {'repository':'other/repository'}, {'branch':'cto/escape'},
    {'credential_reference':'UNIVERSAL_TOKEN'}, {'standing_authority_reference':'OTHER'},
    {'expected_base_commit':'main'}, {'destination_profile_id':'other-profile'},
    {'client_slug':'../escape'}, {'project_slug':'arbitrary'},
])
def test_container_rejects_route_and_path_escape(tmp_path,updates):
    sealed=tmp_path/'sealed'; source=sealed/'publish-001'; source.mkdir(parents=True); value=request(source); value.update(updates)
    with mock.patch.object(dispatch,'SEALED_ROOT',sealed), pytest.raises(SystemExit): dispatch.validate(value)

@pytest.mark.parametrize('field', ['command','refspec','commands','push_refspec'])
def test_closed_schema_rejects_commands_and_refspecs(tmp_path,field):
    sealed=tmp_path/'sealed'; source=sealed/'publish-001'; source.mkdir(parents=True); value=request(source); value[field]='forbidden'
    with mock.patch.object(dispatch,'SEALED_ROOT',sealed), pytest.raises(SystemExit,match='schema'): dispatch.validate(value)

def test_host_stages_exact_package_invokes_only_fixed_publisher_and_returns_receipt(tmp_path):
    original=tmp_path/'sealed'/'publish-001'; original.mkdir(parents=True); value=request(original); bundle=queued_bundle(tmp_path,value)
    staging=tmp_path/'staging'; processed=tmp_path/'processed'; staging.mkdir(); calls=[]
    result={'schema_version':3,'status':'published_and_verified','request_id':value['request_id']}
    def runner(argv,**kwargs):
        calls.append(argv); return mock.Mock(returncode=0,stdout=json.dumps(result),stderr='')
    with mock.patch.multiple(runtime,STAGING=staging,PROCESSED=processed): receipt=runtime.process(bundle,runner)
    assert calls==[[runtime.PUBLISHER,'--request',str(staging/value['request_id']/'request.json')]]
    staged=json.loads((staging/value['request_id']/'request.json').read_text())
    assert staged['source_directory']==str(staging/value['request_id'])
    assert receipt['publisher_result']==result and (processed/value['request_id']/'receipt.json').is_file()
    assert ((processed/value['request_id']/'receipt.json').stat().st_mode & 0o777)==0o644

def test_host_rejects_unmanifested_file_arbitrary_source_and_duplicate_mismatch(tmp_path):
    original=tmp_path/'sealed'/'publish-001'; original.mkdir(parents=True); value=request(original); bundle=queued_bundle(tmp_path,value)
    (bundle/'source'/'extra.html').write_text('x')
    with pytest.raises(ValueError,match='unmanifested'): runtime.validate(json.loads((bundle/'request.json').read_text()),bundle)
    (bundle/'source'/'extra.html').unlink(); queued=json.loads((bundle/'request.json').read_text()); queued['source_directory']='/tmp/arbitrary'
    with pytest.raises(ValueError,match='arbitrary'): runtime.validate(queued,bundle)

def test_parent_symlink_escape_is_rejected_by_both_boundaries(tmp_path):
    outside=tmp_path/'outside'; outside.mkdir(); value=request(outside)
    sealed=tmp_path/'sealed'; sealed.mkdir(); (sealed/'publish-001').symlink_to(outside,target_is_directory=True)
    value['source_directory']=str(sealed/'publish-001')
    with mock.patch.object(dispatch,'SEALED_ROOT',sealed), pytest.raises(SystemExit,match='sealed package root'): dispatch.validate(value)
    bundle=tmp_path/'publish-001'; bundle.mkdir(); (bundle/'source').symlink_to(outside,target_is_directory=True)
    queued={**value,'source_directory':'source'}; (bundle/'request.json').write_text(json.dumps(queued))
    with pytest.raises(ValueError,match='invalid queued'): runtime.validate(queued,bundle)

def test_host_rejects_symlinked_request_bundle(tmp_path):
    original=tmp_path/'sealed'/'publish-001'; original.mkdir(parents=True); value=request(original); bundle=queued_bundle(tmp_path,value)
    request_path=bundle/'request.json'; real=tmp_path/'outside-request.json'; real.write_bytes(request_path.read_bytes()); request_path.unlink(); request_path.symlink_to(real)
    with pytest.raises(ValueError,match='invalid queued request'): runtime.validate(json.loads(real.read_text()),bundle)

def test_systemd_consumer_preserves_root_only_credential_boundary():
    service=(ROOT/'assets/systemd/lhm-prototype-publication.service').read_text(); path=(ROOT/'assets/systemd/lhm-prototype-publication.path').read_text()
    assert 'User=root' in service and 'ReadOnlyPaths=/etc/lhm-prototype-publisher' in service
    assert 'ExecStart=/usr/local/libexec/lhm-prototype-publication-runtime' in service
    assert '/var/lib/lhm-prototype-publication' in service and 'lhm-prototype-publication.service' in path
    runtime_text=(ROOT/'assets/host/lhm-prototype-publication-runtime').read_text()
    assert "PUBLISHER='/usr/local/libexec/lhm-prototype-publisher'" in runtime_text
    assert 'capability_restored' not in runtime_text and 'BasicOps' not in runtime_text
