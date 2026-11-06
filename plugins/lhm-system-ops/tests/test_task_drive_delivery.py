import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[1]
SOURCE = PLUGIN / 'assets/task-router'
sys.path.insert(0,str(SOURCE))
PUB = PLUGIN.parent / 'lhm-project-hub/skills/drive-artifact-delivery/assets/publisher.py'
spec=importlib.util.spec_from_file_location('drive_publisher',PUB)
pub=importlib.util.module_from_spec(spec);sys.modules['drive_publisher']=pub;spec.loader.exec_module(pub)
spec=importlib.util.spec_from_file_location('central_delivery_test',SOURCE/'delivery.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class FakeDrive(pub.Drive):
    def __init__(self):
        super().__init__({'route':pub.ROUTE,'remote':'existing:','workspace_id':'workspace000','current_clients_id':'clients000'})
        self.data={};self.items={'workspace000':[{'ID':'clients000','Name':'Current Clients','IsDir':True}],
             'clients000':[{'ID':'alpha000','Name':'Alpha','IsDir':True}],'alpha000':[]}
    def children(self,folder,path=''):
        return self.items.get(folder,[])
    def call(self,command,folder,path='',*options):
        if command=='cat':return self.data[(folder,path)]
        raise AssertionError(command)
    def create(self,args,**kw):
        from types import SimpleNamespace
        folder=args[args.index('--drive-root-folder-id')+1];name=args[3].split(':',1)[1]
        raw=Path(args[2]).read_bytes();self.data[(folder,name)]=raw
        self.items[folder].append({'ID':'file00001','Name':name,'IsDir':False,'Size':len(raw)})
        return SimpleNamespace(returncode=0)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.source=self.root/'report.md';self.source.write_text('exact draft')

    def test_root_delivery_receipts_are_readable_by_the_hermes_group(self):
        target=self.root/'receipt.json'
        with patch.object(module.os,'geteuid',return_value=0),patch.object(module.os,'chown') as chown:
            module.save(target,{'artefact_state':'delivered'},0o640)
            chown.assert_called_once_with(target.with_name('receipt.json.next'),0,10000)
        self.assertEqual(target.stat().st_mode & 0o777,0o640)

    def test_create_and_retry_verify_exact_bytes_without_overwriting(self):
        d=FakeDrive();d.verify_client('alpha000')
        with patch.object(pub.subprocess,'run',side_effect=d.create) as run:
            result=d.publish(self.source,'report.md','alpha000',pub.digest(self.source.read_bytes()),11)
            self.assertEqual(result['artefact_state'],'delivered');self.assertEqual(result['folder_id'],'alpha000')
            self.assertEqual(d.publish(self.source,'report.md','alpha000',pub.digest(self.source.read_bytes()),11)['action'],'already_existed')
            self.assertEqual(run.call_count,1)
            self.source.write_text('other draft')
            with self.assertRaises(ValueError):d.publish(self.source,'report.md','alpha000',pub.digest(self.source.read_bytes()),11)
            self.assertEqual(run.call_count,1)

    def test_rejects_wrong_ancestry_ambiguous_names_or_corrupt_readback(self):
        d=FakeDrive()
        with self.assertRaises(ValueError):d.verify_client('not-client')
        with self.assertRaises(ValueError):d.publish(self.source,'../secret','alpha000',pub.digest(self.source.read_bytes()),11)
        def corrupt(args,**kw):
            value=d.create(args,**kw);d.data[('alpha000','report.md')]=b'wrong bytes';return value
        with patch.object(pub.subprocess,'run',side_effect=corrupt):
            with self.assertRaises(ValueError):d.publish(self.source,'report.md','alpha000',pub.digest(self.source.read_bytes()),11)

        d.items['alpha000'].append({'ID':'file00002','Name':'report.md','IsDir':False,'Size':11})
        with self.assertRaises(ValueError):d.publish(self.source,'report.md','alpha000',pub.digest(self.source.read_bytes()),11)

    def prepare(self):
        run=self.root/'run';(run/'workspace/drafts').mkdir(parents=True)
        draft=run/'workspace/drafts/review.md';draft.write_bytes(b'prepared report')
        artifact={'relative':'review.md','sha256':pub.digest(draft.read_bytes()),'size_bytes':15}
        request={'request_id':'ted-route-123-dm123','client_id':'alpha','provider':'codex','permission_ceiling':'prepare_for_review',
                 'title':'Alpha: Client Comms meeting review','reviewer_id':36398,'task_url':'https://app.basicops.com/test'}
        (run/'receipt.json').write_text(json.dumps({'status':'needs_review','request_id':request['request_id'],'provider':'codex','artifact_manifest':[artifact]}))
        q=self.root/'queue';q.mkdir();(q/'receipt.json').write_text(json.dumps({'started_at':1792719000}))
        return request,run,q,draft

    def feedback_request(self, request):
        grant = {'authority_id': 'MICHAEL-PROTOTYPE-FEEDBACK-20261107', 'task_id': 123,
                 'instruction_message_id': 'dm123', 'instruction_sha256': 'a'*64,
                 'cockpit_id': 99, 'stage_id': 110340, 'client_id': 'alpha',
                 'batch_id': 'prototype-'+'b'*32, 'author_id': 82491, 'reviewer_id': 36398,
                 'repository': 'michaellhm/lhm-prototype', 'subtree': 'luminary-counselling/', 'enabled': True}
        request.update(permission_ceiling='registered_prototype_revision', task_id=123,
                       instruction_message_id='dm123', instruction_sha256='a'*64)
        request['feedback_authority'] = {'authority_id': grant['authority_id'],
            'grant_sha256': pub.digest(json.dumps(grant, sort_keys=True, separators=(',', ':')).encode()),
            **{k: grant[k] for k in ('batch_id', 'client_id', 'repository', 'subtree')}}
        registry = self.root/'authority/authority.json'
        registry.parent.mkdir()
        registry.write_text(json.dumps({'schema_version': 1, 'grants': {'123': grant}}))
        registry.chmod(0o644)
        return registry, grant

    def root_stats(self, uid=0):
        from types import SimpleNamespace
        real = module.os.fstat
        def result(fd):
            value = real(fd)
            return SimpleNamespace(st_uid=uid, st_mode=value.st_mode, st_nlink=value.st_nlink, st_size=value.st_size)
        return patch.object(module.os, 'fstat', side_effect=result)

    def test_registered_feedback_delivers_only_internal_review_files(self):
        request, run, q, draft = self.prepare()
        registry, grant = self.feedback_request(request)
        with patch.object(module, 'ROOT', self.root/'delivery'), patch.object(module, 'FEEDBACK_REGISTRY', registry), self.root_stats():
            package = module.manifest(request, run, q)
        self.assertEqual(package['permission_ceiling'], 'internal_review_file_create_only')
        self.assertEqual(package['files'][0]['sha256'], pub.digest(b'prepared report'))
        self.assertNotIn('publish', package)

    def test_feedback_delivery_rejects_forged_or_incomplete_request_binding(self):
        request, run, q, draft = self.prepare()
        registry, grant = self.feedback_request(request)
        changes = [
            {'feedback_authority': None},
            {'feedback_authority': dict(request['feedback_authority'], grant_sha256='c'*64)},
            {'feedback_authority': dict(request['feedback_authority'], subtree='other/')},
            {'feedback_authority': dict(request['feedback_authority'], batch_id='prototype-'+'c'*32)},
            {'client_id': 'another-client'}, {'provider': 'claude'}, {'task_id': 124},
            {'reviewer_id': 99}, {'instruction_sha256': 'd'*64}, {'instruction_message_id': 'dm124'}]
        with patch.object(module, 'ROOT', self.root/'delivery'), patch.object(module, 'FEEDBACK_REGISTRY', registry), self.root_stats():
            for change in changes:
                with self.subTest(change=change), self.assertRaises(ValueError):
                    module.manifest({**copy.deepcopy(request), **change}, run, q)
        self.assertFalse((self.root/'delivery').exists())

    def test_feedback_delivery_requires_actual_protected_root_source(self):
        request, run, q, draft = self.prepare()
        registry, grant = self.feedback_request(request)
        with patch.object(module, 'ROOT', self.root/'delivery'), patch.object(module, 'FEEDBACK_REGISTRY', registry):
            with self.root_stats(uid=1000), self.assertRaises(ValueError):
                module.manifest(request, run, q)
            with self.root_stats():
                registry.chmod(0o666)
                with self.assertRaises(ValueError): module.manifest(request, run, q)
                registry.chmod(0o644)
                original = registry.with_suffix('.saved')
                registry.rename(original);registry.symlink_to(original)
                with self.assertRaises(OSError): module.manifest(request, run, q)
                registry.unlink()
                with self.assertRaises(OSError): module.manifest(request, run, q)

    def test_feedback_scope_cannot_bypass_immutable_producer_manifest(self):
        request, run, q, draft = self.prepare()
        registry, grant = self.feedback_request(request)
        draft.write_text('correction is still being produced')
        with patch.object(module, 'ROOT', self.root/'delivery'), patch.object(module, 'FEEDBACK_REGISTRY', registry), self.root_stats(), self.assertRaises(ValueError):
            module.manifest(request, run, q)

    def test_other_execution_ceilings_remain_denied_for_delivery(self):
        request, run, q, draft = self.prepare()
        request['permission_ceiling'] = 'provider_tool_approval'
        with patch.object(module, 'ROOT', self.root/'delivery'), self.assertRaises(ValueError):
            module.manifest(request, run, q)

    def test_manifest_snapshots_only_verified_drafts_and_detects_changed_package(self):
        request,run,q,draft=self.prepare()
        with patch.object(module,'ROOT',self.root/'delivery'):
            result=module.manifest(request,run,q)
            self.assertEqual(len(result['files']),1);self.assertTrue(result['relative_folder'].startswith('client_updates/2026-10/'))
            self.assertEqual((module.ROOT/request['request_id']/'sources/review.md').read_bytes(),b'prepared report')
            draft.write_text('changed')
            with self.assertRaises(ValueError):module.manifest(request,run,q)

    def test_completed_worker_receipt_declares_every_draft_for_drive_delivery(self):
        from types import SimpleNamespace
        spec=importlib.util.spec_from_file_location('drive_worker_test',SOURCE/'worker.py')
        worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
        run=self.root/'worker-run';work=run/'workspace';(work/'drafts').mkdir(parents=True)
        request={'provider':'claude','request_id':'ted-route-1-dm1','title':'Prepare a client draft','description':'Internal review','instruction':'Please draft this'}
        (run/'request.json').write_text(json.dumps(request))
        def complete(*a,**kw):
            (work/'drafts/review.md').write_text('draft')
            return SimpleNamespace(stdout=json.dumps({'result':'Prepared draft','is_error':False}),stderr='',returncode=0)
        with patch.object(worker.subprocess,'run',side_effect=complete):worker.execute(run,'claude')
        receipt=json.loads((run/'receipt.json').read_text())
        self.assertTrue(receipt['delivery_required']);self.assertEqual(receipt['status'],'needs_review')
        self.assertEqual(receipt['artifact_manifest'],[{'relative':'review.md','size_bytes':5,'sha256':pub.digest(b'draft')}])

    def test_partial_retry_keeps_verified_receipts_and_uploads_only_incomplete_item(self):
        request={'request_id':'ted-route-123-dm123'}
        entries=[{'relative':name,'size_bytes':1,'sha256':name,'media_type':'text/plain'} for name in ['one.txt','two.txt']]
        package={'package_sha256':'package','relative_folder':'run-hermes-task/2026-10/request','files':entries}
        q=self.root/'queue';q.mkdir()
        first={'relative':'one.txt','size_bytes':1,'sha256':'one.txt','readback_sha256':'one.txt','run_result':'passed'}
        (q/'delivery.json').write_text(json.dumps({'package_sha256':'package','folder_id':'dest00000','files':[first]}))
        config=self.root/'config.json';config.write_text('{}')
        class Backend:
            def __init__(self):self.names=[]
            def ensure_path(self,*args):return 'dest00000'
            def publish(self,source,name,parent,sha,size,media):
                self.names.append(name)
                return {'run_result':'passed','sha256':sha,'readback_sha256':sha,'size_bytes':size}
        backend=Backend()
        with patch.object(module,'CONFIG',config),patch.object(module,'manifest',return_value=package),patch.object(module,'Drive',return_value=backend),patch.object(module,'folder_for',return_value='alpha000'),patch.object(module,'capability'):
            result=module.deliver(request,self.root/'unused',q)
        self.assertEqual(backend.names,['two.txt']);self.assertEqual(result['artefact_state'],'delivered')
        self.assertEqual(len(result['files']),2)

    def test_symlinks_credentials_and_unregistered_roots_are_rejected(self):
        request,run,q,draft=self.prepare()
        with patch.object(module,'ROOT',self.root/'delivery'):
            draft.unlink();draft.symlink_to(self.source)
            with self.assertRaises((ValueError,OSError)):module.manifest(request,run,q)
            draft.unlink();module.os.link(self.source,draft)
            with self.assertRaises(ValueError):module.manifest(request,run,q)
            draft.unlink();draft.write_text('{"refresh_token":"do not upload"}')
            with self.assertRaises(ValueError):module.manifest(request,run,q)
            draft.write_bytes(b'prepared report')
            (run/'workspace-location.json').write_text(json.dumps({'workspace':'/etc','task_directory':'/etc'}))
            with self.assertRaises(ValueError):module.manifest(request,run,q)
            alias=self.root/'linked';alias.symlink_to(run,target_is_directory=True)
            with self.assertRaises(OSError):module.read(alias/'receipt.json')

if __name__=='__main__':unittest.main()
