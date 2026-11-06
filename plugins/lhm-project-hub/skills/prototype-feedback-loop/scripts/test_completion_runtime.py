import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROUTER = HERE.parents[3] / 'lhm-system-ops/assets/task-router'
sys.path.insert(0, str(ROUTER))
PUB = HERE.parents[2] / 'skills/drive-artifact-delivery/assets/publisher.py'
spec = importlib.util.spec_from_file_location('drive_publisher', PUB)
pub = importlib.util.module_from_spec(spec);sys.modules['drive_publisher'] = pub;spec.loader.exec_module(pub)
import completion_runtime as runtime
PUB_SOURCE=ROUTER.parent/'host/lhm-prototype-publisher'
spec=importlib.util.spec_from_loader('completion_publisher_contract',SourceFileLoader('completion_publisher_contract',str(PUB_SOURCE)))
publisher_contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher_contract)


def directory(path, **unused):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def atomic(path, data, **unused):
    Path(path).write_bytes(data)


class CompletionTests(unittest.TestCase):
    def setUp(self):
        patcher=mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes())
        patcher.start();self.addCleanup(patcher.stop)

    def fixture(self, root):
        ident = 'ted-route-123-dm456'
        batch = {'id': 'prototype-' + 'a' * 32, 'run_id': ident, 'task_id': '123','chat_url':'codex://threads/11111111-1111-4111-8111-111111111111?hostId=hermes'}
        reg = {'client_id': 'blue-dragonfly', 'worker_root': str(root / 'client')}
        task = root / 'client/tasks' / ident
        drafts = task / 'drafts'
        for page in runtime.PAGES:
            path = drafts / 'revised-source' / page
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('<html>page</html>')
        (drafts / 'report.md').write_text('Report')
        run = root / 'work' / ident
        run.mkdir(parents=True)
        request = {'request_id': ident, 'task_id': 123, 'client_id': reg['client_id'],
                   'feedback_authority': {'batch_id': batch['id']}}
        receipt = {'request_id': ident, 'provider': 'codex', 'status': 'needs_review',
                   'thread_id': '11111111-1111-4111-8111-111111111111', 'artifact_manifest': runtime.tree(drafts)}
        for name, value in [('request.json', request), ('receipt.json', receipt),
            ('workspace-location.json', {'workspace': reg['worker_root'], 'task_directory': str(task)})]:
            (run / name).write_text(json.dumps(value))
        coordinator = types.SimpleNamespace(queue=types.SimpleNamespace(packets=lambda batch: [
            {'message_id': 'email1', 'items': [{'id': '1', 'request': 'Change heading'}]}]))
        completion = runtime.Completion(coordinator=coordinator, work=root / 'work', qa_root=root / 'qa')
        return completion, batch, reg, drafts, run

    def test_freeze_exact_producer_and_distinct_checklist_ids(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime, 'protected_directory', directory), \
             mock.patch.object(runtime, 'atomic', atomic), mock.patch('delivery.feedback_delivery_authority', return_value=True):
            completion, batch, reg, drafts, run = self.fixture(Path(temp).resolve())
            stage, frozen = completion.freeze(batch, reg)
            self.assertEqual(frozen['items'][0]['id'], 'email1:1')
            self.assertEqual(len(frozen['source']['files']), 5)
            self.assertEqual(frozen['producer_manifest'], runtime.tree(drafts))
            self.assertEqual((stage / 'source' / runtime.PAGES[0]).read_bytes(), b'<html>page</html>')
            # Later feedback cannot change this batch's frozen checklist/source.
            completion.coordinator.queue.packets = lambda batch: [{'message_id': 'later', 'items': [{'id': '2'}]}]
            with mock.patch.object(runtime, 'root_json', lambda path: json.loads(path.read_text())):
                self.assertEqual(completion.freeze(batch, reg)[1], frozen)

    def test_correction_transient_masks_other_clients_and_preserves_active_brief(self):
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'atomic',atomic),mock.patch('delivery.feedback_delivery_authority',return_value=True), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime.subprocess,'run',return_value=types.SimpleNamespace(returncode=0)) as runner:
            completion,batch,reg,drafts,run=self.fixture(Path(temp).resolve())
            control=directory(Path(reg['worker_root'])/'.control');(control/'worker.lock').touch()
            (drafts.parent/'task-context.json').write_text('Original brief');directory(drafts.parent/'context')
            stage,frozen=completion.freeze(batch,reg)
            result=completion.correction(stage,batch,reg,qa={'approved':False,'reason':'Fix mobile overflow'})
            self.assertEqual(result['state'],'correction_started')
            command=runner.call_args.args[0]
            masks=next(value for value in command if value.startswith('--property=TemporaryFileSystem='))
            for mask in ('/var/lib/lhm-client-workspaces:ro','/var/lib/lhm-task-router:ro','/home/codexworker/clients:ro'):
                self.assertIn(mask,masks)
            selected=next(value for value in command if value.startswith('--property=BindPaths='))
            self.assertIn(reg['worker_root'],selected);self.assertIn(str(run),selected)
            readonly=next(value for value in command if value.startswith('--property=BindReadOnlyPaths='))
            self.assertIn(str(drafts.parent/'task-context.json'),readonly)
            self.assertIn(str(run/'request.json'),readonly)
            self.assertEqual((drafts.parent/'task-context.json').read_text(),'Original brief')

    def test_plain_token_in_private_report_rejected_before_any_delivery(self):
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'atomic',atomic),mock.patch('delivery.feedback_delivery_authority',return_value=True):
            completion,batch,reg,drafts,run=self.fixture(Path(temp).resolve())
            (drafts/'report.md').write_text('Do not upload github_pat_example')
            receipt=json.loads((run/'receipt.json').read_text());receipt['artifact_manifest']=runtime.tree(drafts)
            (run/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'credential-like'):completion.freeze(batch,reg)
            self.assertFalse(any(completion.root.rglob('drive-folder-intent.json')))

    def test_finished_manifest_mismatch_fails_before_freeze(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch('delivery.feedback_delivery_authority', return_value=True):
            completion, batch, reg, drafts, run = self.fixture(Path(temp).resolve())
            (drafts / 'report.md').write_text('Changed after completion')
            with self.assertRaisesRegex(ValueError, 'finished manifest'):
                completion.freeze(batch, reg)
            self.assertFalse(completion.root.exists())

    def test_changed_active_producer_cannot_replace_original(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime, 'protected_directory', directory), \
             mock.patch.object(runtime, 'atomic', atomic), mock.patch('delivery.feedback_delivery_authority', return_value=True), \
             mock.patch.object(runtime, 'root_json', lambda path: json.loads(path.read_text())):
            completion, batch, reg, drafts, run = self.fixture(Path(temp).resolve())
            stage, original = completion.freeze(batch, reg)
            (drafts / 'report.md').write_text('New report')
            receipt = json.loads((run / 'receipt.json').read_text())
            receipt['artifact_manifest'] = runtime.tree(drafts)
            (run / 'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, 'active completion evidence changed'):
                completion.freeze(batch, reg)
            self.assertEqual(json.loads((stage / 'frozen.json').read_text()), original)

    def test_symlink_producer_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve();(root / 'real').mkdir();(root / 'linked').symlink_to(root / 'real')
            with self.assertRaisesRegex(ValueError, 'linked'):
                runtime.tree(root / 'linked')

    def test_semantic_reviewer_must_be_independent_and_complete(self):
        producer = '11111111-1111-4111-8111-111111111111'
        reviewer = '22222222-2222-4222-8222-222222222222'
        value = {'approved': True, 'source_package_sha256': 'a' * 64, 'reason': 'Reviewed screenshots and source',
                 'items': [{'id': 'email:1', 'passed': True, 'evidence': 'Heading appears in both screenshots'}]}
        args = {'package': 'a' * 64, 'items': [{'id': 'email:1'}], 'thread': reviewer, 'producer': producer}
        self.assertTrue(runtime.semantic_result(value, **args)['approved'])
        with self.assertRaises(ValueError): runtime.semantic_result(value, **{**args, 'thread': producer})
        with self.assertRaises(ValueError): runtime.semantic_result({**value, 'items': []}, **args)
        with self.assertRaises(ValueError): runtime.semantic_result({**value, 'source_package_sha256': 'b' * 64}, **args)
        with self.assertRaises(ValueError): runtime.semantic_result({**value, 'items': [{**value['items'][0], 'passed': False}]}, **args)

    def test_semantic_normalizes_order_only_after_exact_unique_coverage(self):
        producer='11111111-1111-4111-8111-111111111111';reviewer='22222222-2222-4222-8222-222222222222'
        items=[{'id':'main:R1'},{'id':'main:R12'},{'id':'follow:R10'}]
        rows=[{'id':value,'passed':False,'evidence':'Concrete prototype finding'} for value in ('main:R1','follow:R10','main:R12')]
        value={'approved':False,'source_package_sha256':'a'*64,'reason':'Needs revision','items':rows}
        args={'package':'a'*64,'items':items,'thread':reviewer,'producer':producer}
        result=runtime.semantic_result(value,**args)
        self.assertFalse(result['approved'])
        self.assertEqual([row['id'] for row in result['items']],[row['id'] for row in items])
        for invalid in ([rows[0],rows[0],rows[2]],[rows[0],rows[1]],[*rows[:2],{**rows[2],'id':'invented:R99'}]):
            with self.assertRaises(ValueError):runtime.semantic_result({**value,'items':invalid},**args)
        schema=runtime.semantic_schema({'items':items,'source':{'package_sha256':'a'*64}})
        self.assertEqual(schema['properties']['items']['items']['properties']['id']['enum'],[row['id'] for row in items])
        self.assertEqual(schema['properties']['items']['minItems'],3)
        self.assertEqual(schema['properties']['items']['maxItems'],3)
        self.assertEqual(schema['properties']['source_package_sha256']['enum'],['a'*64])

    def test_not_finished_worker_is_never_snapshotted(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch('delivery.feedback_delivery_authority', return_value=True):
            completion, batch, reg, drafts, run = self.fixture(Path(temp).resolve())
            receipt = json.loads((run / 'receipt.json').read_text());receipt['status'] = 'running'
            (run / 'receipt.json').write_text(json.dumps(receipt))
            self.assertIsNone(completion.freeze(batch, reg))
            self.assertFalse(completion.root.exists())


class HandbackTests(unittest.TestCase):
    def fixture(self, root, crash_review=False, crash_ready=False):
        class Backend:
            def __init__(self):
                self.task={'id':123,'description':'Original brief<p>LHM metadata: unrelated=keep; workflow_state=executing; approval_status=approved</p>','assignee':{'id':82491},'status':'In Progress','reviewers':[]}
                self.messages=[];self.writes=[];self.crash=crash_review
            def basicops(self, action, args):
                if action=='get_task':return dict(self.task)
                if action=='list_messages_in_task':return {'data':list(self.messages)}
                self.writes.append(action)
                if action=='bulk_create_or_update_task':
                    item=args['items'][0];self.task.update(description=item['description'],assignee={'id':item['assignee']},status='Accepted')
                elif action=='request_review':
                    self.task.update(status='Under Review',reviewers=args['reviewers']);self.messages.append({'message':args['message'],'user':{'id':82491}})
                    if self.crash: self.crash=False;raise TimeoutError('connection lost after remote review write')
                else:raise AssertionError(action)
        class Queue:
            def __init__(self):self.checkpoints=[];self.ready_count=0;self.crash=crash_ready
            def checkpoint(self,*args,**kwargs):self.checkpoints.append((args,kwargs))
            def ready(self,*args,**kwargs):
                if self.crash:self.crash=False;raise RuntimeError('crash after handback receipt')
                self.ready_count+=1
        backend,queue=Backend(),Queue()
        tx=runtime.Transaction(types.SimpleNamespace(backend=backend,queue=queue))
        batch={'id':'prototype-'+'a'*32,'task_id':'123','run_id':'ted-route-123-dm456','owner':'root-owner'}
        reg={'reviewer_id':36398,'preview_url':'https://lhmstaging.net/prototypes/luminary-counselling/homepage/'}
        delivery={'folder_url':'https://drive.google.com/drive/folders/evidence123'}
        pub={'release':{'commit':'a'*40,'workflow':{'run_id':1234}}}
        return tx,batch,reg,delivery,pub,backend,queue

    def test_review_last_and_restart_no_reassignment(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
            tx,batch,reg,delivery,pub,backend,queue=self.fixture(Path(temp))
            stage=Path(temp)
            first=tx.handback(stage,batch,{},reg,delivery,pub)
            second=tx.handback(stage,batch,{},reg,delivery,pub)
            self.assertEqual(first,second)
            self.assertEqual(backend.writes,['bulk_create_or_update_task','request_review'])
            self.assertEqual(backend.task['status'],'Under Review')
            self.assertTrue(backend.task['description'].startswith('Original brief'))
            self.assertNotIn('AI authorship:',backend.task['description'])
            self.assertIn('AI authorship: This update was written by Ted.',backend.messages[0]['message'])
            self.assertIn('unrelated=keep; workflow_state=ready-for-review; approval_status=pending-human',backend.task['description'])

    def test_crash_after_review_write_reconciles_no_duplicate(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
            tx,batch,reg,delivery,pub,backend,queue=self.fixture(Path(temp),crash_review=True)
            with self.assertRaises(TimeoutError):tx.handback(Path(temp),batch,{},reg,delivery,pub)
            result=tx.handback(Path(temp),batch,{},reg,delivery,pub)
            self.assertEqual(result['status'],'Under Review')
            self.assertEqual(backend.writes,['bulk_create_or_update_task','request_review'])
            self.assertEqual(queue.ready_count,0)  # Only finish may mark ready after native proof projection.

    def test_identical_discussion_from_other_author_does_not_prove_handback(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
            tx,batch,reg,delivery,pub,backend,queue=self.fixture(Path(temp),crash_review=True)
            with self.assertRaises(TimeoutError):tx.handback(Path(temp),batch,{},reg,delivery,pub)
            backend.messages[0]['user']={'id':999}
            with self.assertRaisesRegex(ValueError,'uncertain'):tx.handback(Path(temp),batch,{},reg,delivery,pub)
            self.assertEqual(queue.ready_count,0)
            self.assertEqual(len(backend.writes),2)

    def test_crash_after_receipt_before_queue_ready_recovers(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
            tx,batch,reg,delivery,pub,backend,queue=self.fixture(Path(temp),crash_ready=True)
            tx.package=lambda *args:{};tx.deliver=lambda *args:delivery;tx.publication=lambda *args:pub
            tx.project=mock.Mock()
            with self.assertRaisesRegex(RuntimeError,'after handback'):tx.finish(Path(temp),batch,{}, {'approved':True},reg)
            tx.finish(Path(temp),batch,{}, {'approved':True},reg)
            self.assertEqual(tx.project.call_count,2)
            self.assertEqual(queue.ready_count,1)
            self.assertEqual(len(backend.writes),2)

    def test_uncertain_review_without_readback_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
            tx,batch,reg,delivery,pub,backend,queue=self.fixture(Path(temp),crash_review=True)
            with self.assertRaises(TimeoutError):tx.handback(Path(temp),batch,{},reg,delivery,pub)
            backend.messages=[]
            with self.assertRaisesRegex(ValueError,'uncertain'):tx.handback(Path(temp),batch,{},reg,delivery,pub)
            self.assertEqual(backend.writes,['bulk_create_or_update_task','request_review'])
            self.assertEqual(queue.ready_count,0)

    def test_failed_qa_never_calls_drive_publisher_or_handback(self):
        tx=runtime.Transaction(types.SimpleNamespace())
        with mock.patch.object(tx,'package') as package:
            result=tx.finish(None,None,None,{'approved':False,'reason':'Missing mobile menu'},None)
            self.assertEqual(result['state'],'qa_blocked');package.assert_not_called()


class PublicationTests(unittest.TestCase):
    def fixture(self, root, bad_workflow=False, bad_public=False, crash=False, unchanged_index=False):
        batch={'id':'prototype-'+'a'*32,'task_id':'123','run_id':'ted-route-123-dm456','owner':'owner'}
        stage=root/'ted-route-123-dm456-r0';stage.mkdir();(stage/'independent-qa.json').write_text('{"approved":true}')
        source=directory(stage/'source')
        files=[]
        for name,data in [('index.html',b'changed homepage'),('style.css',b'changed CSS')]:
            relative=runtime.SOURCE_SUBTREE+name;path=source/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            files.append({'path':relative,'size_bytes':len(data),'sha256':runtime.sha(data)})
        files.sort(key=lambda row:row['path'])
        state=root/'state';basepath=directory(state/'sources'/batch['id'])/'source-manifest.json'
        basepath.write_text(json.dumps({'repository':'michaellhm/lhm-prototype','subtree':runtime.SOURCE_SUBTREE,
            'base_commit':'a'*40,'files':[dict(entry,sha256=entry['sha256'] if unchanged_index and entry['path'].endswith('index.html') else '0'*64) for entry in files]}))
        frozen={'source':{'files':files},'request':{'request_id':batch['run_id'],'task_url':'https://app.basicops.com/task/123',
                'feedback_authority':{'batch_id':batch['id']}}}
        delivery={'files':[{'relative':'revised-source/'+runtime.SOURCE_SUBTREE+'index.html','file_id':'indexfile123',
                           'readback_sha256':files[0]['sha256'],'size_bytes':files[0]['size_bytes']}]}
        calls=[]
        def runner(command,**kwargs):
            request=json.loads(Path(command[-1]).read_text());calls.append(request)
            with mock.patch.object(publisher_contract,'SOURCE_ROOT',root/'incoming'):
                publisher_contract.validate(request)
            self.assertEqual(request['source_package_sha256'],publisher_contract.package_digest(request['file_manifest']))
            if crash and len(calls)==1:return types.SimpleNamespace(returncode=1,stdout='')
            commit='b'*40;workflow={'id':289562388,'name':'Deploy to lhmstaging','path':'.github/workflows/deploy.yml',
                'head_sha':commit,'head_branch':'main','status':'completed','conclusion':'success','run_id':123,
                'html_url':'https://github.com/michaellhm/lhm-prototype/actions/runs/123'}
            if bad_workflow:workflow['head_sha']='c'*40
            result={'status':'published_and_verified','request_id':request['request_id'],
                    'source_package_sha256':request['source_package_sha256'],'repository':request['repository'],
                    'branch':'main','commit':commit,'workflow':workflow,'changed_files':[entry['path'] for entry in files if not (unchanged_index and entry['path'].endswith('index.html'))]}
            return types.SimpleNamespace(returncode=0,stdout=json.dumps(result))
        httpcalls=[]
        def http(url):
            relative=url.removeprefix('https://lhmstaging.net/prototypes/');httpcalls.append(relative)
            data=(source/relative).read_bytes()
            return 200,b'wrong CSS' if bad_public and relative.endswith('style.css') else data
        tx=runtime.Transaction(types.SimpleNamespace(root=state),runner=runner,http=http,publication_root=root/'incoming')
        return tx,stage,batch,frozen,delivery,calls,httpcalls

    def test_exact_workflow_and_every_public_file_verified(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:path.read_bytes()):
            tx,stage,batch,frozen,delivery,calls,httpcalls=self.fixture(Path(temp))
            result=tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
            self.assertEqual(len(result['public_files']),2)
            self.assertEqual(httpcalls,[entry['path'] for entry in frozen['source']['files']])
            self.assertEqual(calls[0]['expected_base_commit'],'a'*40)

    def test_native_http_uses_existing_publisher_identity_and_checks_all_bytes(self):
        import urllib.request
        from urllib.parse import urlsplit
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:path.read_bytes()):
            tx,stage,batch,frozen,delivery,calls,httpcalls=self.fixture(Path(temp))
            tx.http=None;observed=[]
            def response(request,timeout):
                self.assertEqual(request.get_header('User-agent'),'LHM-Prototype-Publisher/2')
                self.assertEqual(request.get_header('Cache-control'),'no-cache')
                self.assertEqual(timeout,40)
                path=urlsplit(request.full_url).path.removeprefix('/prototypes/')
                self.assertIn('lhm_verify=',request.full_url);observed.append(path)
                data=(stage/'source'/path).read_bytes()
                stream=mock.MagicMock();stream.status=200
                stream.read.side_effect=lambda maximum:data[:maximum]
                stream.__enter__.return_value=stream
                return stream
            with mock.patch.object(urllib.request,'urlopen',side_effect=response):
                result=tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
            self.assertEqual(observed,[entry['path'] for entry in frozen['source']['files']])
            self.assertEqual(len(result['public_files']),2)

    def test_css_only_index_anchor_passes_real_publisher_contract(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:path.read_bytes()):
            tx,stage,batch,frozen,delivery,calls,httpcalls=self.fixture(Path(temp),unchanged_index=True)
            result=tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
            self.assertEqual(result['changed_files'],[runtime.SOURCE_SUBTREE+'style.css'])
            self.assertEqual(len(calls[0]['file_manifest']),2)
            self.assertEqual(len(httpcalls),2)
            publisher_contract.approved_changes([entry['path'] for entry in calls[0]['file_manifest']],
                result['changed_files'],runtime.SOURCE_SUBTREE+'index.html',True)

    def test_crash_after_push_reuses_exact_publisher_request(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'protected_directory',directory), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:path.read_bytes()):
            tx,stage,batch,frozen,delivery,calls,httpcalls=self.fixture(Path(temp),crash=True)
            with self.assertRaisesRegex(ValueError,'pending journal'):tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
            tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
            self.assertEqual(calls[0],calls[1])
            self.assertEqual(calls[0]['idempotency_key'],stage.name)

    def test_wrong_workflow_or_non_index_public_bytes_never_verify(self):
        for wrong in ('workflow','public'):
            with self.subTest(wrong=wrong), tempfile.TemporaryDirectory() as temp, \
                 mock.patch.object(runtime,'atomic',atomic),mock.patch.object(runtime,'protected_directory',directory), \
                 mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
                 mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:path.read_bytes()):
                tx,stage,batch,frozen,delivery,calls,httpcalls=self.fixture(Path(temp),bad_workflow=wrong=='workflow',bad_public=wrong=='public')
                with self.assertRaises(ValueError):tx.publication(stage,batch,frozen,delivery,{'cockpit_id':999})
                self.assertFalse((stage/'verified-publication.json').exists())


class GateTests(unittest.TestCase):
    def test_screenshot_pixels_do_not_become_text_credentials_but_metadata_is_rejected(self):
        import struct,zlib
        def chunk(kind,body):
            return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
        header=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',4,1,8,2,0,0,0))
        # Real uncompressed-deflate pixel bytes can coincidentally spell a token.
        pixels=chunk(b'IDAT',zlib.compress(b'\x00sk-example12',level=0))
        image=header+pixels+chunk(b'IEND',b'')
        self.assertIn(b'sk-example',image)
        runtime.safe_output(image)
        for extra in (chunk(b'tEXt',b'comment\x00ghp_example'),chunk(b'zTXt',b'comment\x00\x00'+zlib.compress(b'ghp_example')),chunk(b'eXIf',b'private metadata')):
            with self.assertRaisesRegex(ValueError,'metadata'):runtime.safe_output(header+extra+pixels+chunk(b'IEND',b''))
        with self.assertRaisesRegex(ValueError,'checksum'):runtime.safe_output(image[:-1]+bytes([image[-1]^1]))
        with self.assertRaises(ValueError):runtime.safe_output(image[:-7])

    def setUp(self):
        patcher=mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes())
        patcher.start();self.addCleanup(patcher.stop)

    def test_sensitive_policy_matches_publisher_without_desk_workers_false_positive(self):
        self.assertEqual(runtime.SENSITIVE.pattern,publisher_contract.SENSITIVE.pattern)
        runtime.safe_output(b'Use desk-workers in a CSS label')
        for data in (b'ghp_example',b'github_pat_example',b'sk-example',b'AKIA0123456789ABCDEF'):
            with self.assertRaises(ValueError):runtime.safe_output(data)

    def test_semantic_cli_receives_exact_source_inline_with_verified_hardening_flags(self):
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(runtime.os,'chown'),mock.patch.object(runtime,'protected_directory',directory),mock.patch.object(runtime,'atomic',atomic):
            stage=Path(temp).resolve();directory(stage/'source')
            producer='11111111-1111-4111-8111-111111111111';reviewer='22222222-2222-4222-8222-222222222222'
            evidence={'source':{'package_sha256':'a'*64},'items':[{'id':'email:1'}],
                      'mechanical':{'pages':[]},'source_text':[{'path':'index.html','text':'<h1>Exact reviewed source</h1>'}]}
            calls=[]
            def runner(command,**kwargs):
                calls.append((command,kwargs))
                (stage/'review/output/result.json').write_text(json.dumps({'approved':True,'source_package_sha256':'a'*64,
                    'reason':'Reviewed exact evidence','items':[{'id':'email:1','passed':True,'evidence':'Exact source and screenshot'}]}))
                return types.SimpleNamespace(returncode=0,stdout=json.dumps({'type':'thread.started','thread_id':reviewer}))
            service=runtime.QA(runner=runner)
            result=service.semantic(stage,evidence,producer)
            with mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())):
                self.assertEqual(service.semantic(stage,evidence,producer),result)
            self.assertEqual(len(calls),1)
            self.assertTrue((stage/'semantic-native-run.json').is_file())
            command,options=calls[0]
            self.assertIn('--strict-config',command)
            for feature in ('shell_tool','apps','plugins','browser_use','computer_use','multi_agent','code_mode','hooks'):
                self.assertTrue(any(command[n:n+2]==['--disable',feature] for n in range(len(command)-1)))
            self.assertIn('web_search="disabled"',command)
            self.assertIn('<h1>Exact reviewed source</h1>',options['input'])
            self.assertIn('public claim is excluded',options['input'])
            self.assertEqual(result['reviewer_thread_id'],reviewer)

    def test_semantic_root_schema_and_group_directories_keep_exact_modes_under_umask_0077(self):
        import host_runtime
        with tempfile.TemporaryDirectory() as temp:
            stage=Path(temp).resolve();(stage/'source').mkdir()
            producer='11111111-1111-4111-8111-111111111111';reviewer='22222222-2222-4222-8222-222222222222'
            evidence={'source':{'package_sha256':'a'*64},'items':[{'id':'item:1'}],'mechanical':{'pages':[]}}
            def runner(*args,**kwargs):
                (stage/'review/output/result.json').write_text(json.dumps({'approved':True,'source_package_sha256':'a'*64,
                    'reason':'Exact source checked','items':[{'id':'item:1','passed':True,'evidence':'Checked'}]}))
                return types.SimpleNamespace(returncode=0,stdout=json.dumps({'type':'thread.started','thread_id':reviewer}))
            real=os.fstat
            def root_fstat(fd):
                info=real(fd);return types.SimpleNamespace(st_mode=info.st_mode,st_uid=0,st_gid=10001,
                    st_nlink=info.st_nlink,st_size=info.st_size)
            previous=os.umask(0o077)
            try:
                with mock.patch.object(host_runtime.os,'fstat',side_effect=root_fstat), \
                     mock.patch.object(host_runtime.os,'chown'),mock.patch.object(host_runtime.os,'fchown'):
                    result=runtime.QA(runner=runner).semantic(stage,evidence,producer)
            finally:os.umask(previous)
            self.assertTrue(result['approved'])
            self.assertEqual((stage/'review').stat().st_mode&0o777,0o750)
            self.assertEqual((stage/'review/schema.json').stat().st_mode&0o777,0o640)
            self.assertEqual((stage/'review/runtime').stat().st_mode&0o777,0o700)
            self.assertEqual((stage/'review/output').stat().st_mode&0o777,0o700)
            self.assertEqual((stage/'semantic-native-run.json').stat().st_mode&0o777,0o600)

    def test_mechanical_requires_every_exact_page_viewport_and_no_semantic_grant(self):
        source={'package_sha256':'a'*64}
        receipt={'source_package_sha256':'a'*64,'source_manifest_sha256':'b'*64,'semantic_qa_approved':False,
                 'status':'mechanical_passed','pages':[{'page':page,'viewport':{'width':w,'height':h},'status':'passed','errors':[]}
                    for page in runtime.PAGES for w,h in ((1440,1000),(390,844))]}
        self.assertIs(runtime.validate_mechanical(receipt,source,'b'*64),receipt)
        with self.assertRaises(ValueError):runtime.validate_mechanical({**receipt,'semantic_qa_approved':True},source,'b'*64)
        with self.assertRaises(ValueError):runtime.validate_mechanical({**receipt,'pages':[receipt['pages'][0]]*10},source,'b'*64)

    def test_correction_is_bounded_without_any_worker_write(self):
        completion=runtime.Completion(coordinator=types.SimpleNamespace())
        with mock.patch.object(runtime.subprocess,'run') as runner:
            result=completion.correction(None,{'revision':2},None)
            self.assertEqual(result['state'],'blocked');runner.assert_not_called()

    def test_corrected_same_chat_revision_advances_without_relaunch(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_json',lambda path,**kwargs:json.loads(path.read_text())), \
             mock.patch.object(runtime,'worker_bytes',lambda path,*args:path.read_bytes()):
            root=Path(temp);stage=directory(root/'qa/original-r0');run=directory(root/'work/ted-route-123-dm456')
            (stage/'correction-authority.json').write_text(json.dumps({'thread_id':'same-thread'}))
            (run/'receipt.json').write_text(json.dumps({'qa_correction_revision':1,'status':'needs_review','thread_id':'same-thread'}))
            completion=runtime.Completion(coordinator=types.SimpleNamespace(),work=root/'work',qa_root=root/'qa')
            with mock.patch.object(runtime.subprocess,'run') as runner:
                result=completion.correction(stage,{'run_id':run.name,'revision':0},{})
                self.assertEqual(result,{'state':'correction_completed','revision':1});runner.assert_not_called()
            self.assertEqual(json.loads((root/'qa'/ (run.name+'-revision.json')).read_text()),{'revision':1})

    def test_interrupted_qa_output_retained_and_bounded_retry(self):
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(runtime.os,'chown'):
            stage=Path(temp);old=directory(stage/'review');(old/'partial.json').write_text('partial')
            qa=runtime.QA(runner=lambda *args,**kwargs:types.SimpleNamespace(stdout='inactive'))
            qa.recover_directory(stage,'review','fixed-unit')
            self.assertEqual((stage/'review-interrupted-1/partial.json').read_text(),'partial')
            self.assertFalse(old.exists())
            directory(old);qa.recover_directory(stage,'review','fixed-unit');directory(old)
            with self.assertRaisesRegex(ValueError,'retries exhausted'):qa.recover_directory(stage,'review','fixed-unit')

    def test_active_qa_service_is_never_interrupted_or_erased(self):
        with tempfile.TemporaryDirectory() as temp:
            stage=Path(temp);directory(stage/'output')
            qa=runtime.QA(runner=lambda *args,**kwargs:types.SimpleNamespace(stdout='active'))
            with self.assertRaisesRegex(ValueError,'still active'):qa.recover_directory(stage,'output','fixed-unit')
            self.assertTrue((stage/'output').is_dir())
            self.assertFalse((stage/'output-interrupted-1').exists())

    def test_crash_after_drive_folder_write_reconciles_without_second_create(self):
        from adapters import Effects
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);effects=Effects(root/'effects.sqlite');rows=[];writes=[]
            def call(action,parent,name):
                writes.append((action,parent,name));rows.append({'Name':name,'IsDir':True,'ID':'folder12345'})
                raise TimeoutError('lost folder create response')
            drive=types.SimpleNamespace(children=lambda parent:list(rows),call=call)
            tx=runtime.Transaction(types.SimpleNamespace(effects=effects))
            try:
                with self.assertRaises(TimeoutError):tx.directory(drive,'parent12345','feedback',root)
                self.assertEqual(tx.directory(drive,'parent12345','feedback',root),'folder12345')
                self.assertEqual(len(writes),1)
            finally:effects.db.close()

    def test_crash_after_drive_file_create_adopts_full_readback_without_recreate(self):
        from adapters import Effects
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);effects=Effects(root/'effects.sqlite');rows=[];writes=[];data=b'report'
            def publish(*args):
                writes.append(args);rows.append({'Name':'report.md','IsDir':False,'ID':'file1234567','Size':6,'MimeType':'text/markdown'})
                raise TimeoutError('lost file create response')
            drive=types.SimpleNamespace(children=lambda parent:list(rows),publish=publish,call=lambda *args:data)
            tx=runtime.Transaction(types.SimpleNamespace(effects=effects))
            entry={'relative':'report.md','size_bytes':6,'sha256':runtime.sha(data)}
            try:
                with self.assertRaises(TimeoutError):tx.drive_file(drive,root/'report.md','parent12345',entry,'text/markdown',root)
                receipt=tx.drive_file(drive,root/'report.md','parent12345',entry,'text/markdown',root)
                self.assertEqual(receipt['file_id'],'file1234567')
                self.assertEqual(receipt['readback_sha256'],entry['sha256'])
                self.assertEqual(len(writes),1)
            finally:effects.db.close()

    def test_unknown_drive_file_write_is_never_replayed_without_readback(self):
        from adapters import Effects,ReconcileRequired
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);effects=Effects(root/'effects.sqlite');writes=[]
            def publish(*args):writes.append(args);raise TimeoutError('unknown create outcome')
            drive=types.SimpleNamespace(children=lambda parent:[],publish=publish)
            tx=runtime.Transaction(types.SimpleNamespace(effects=effects))
            entry={'relative':'report.md','size_bytes':1,'sha256':'a'*64}
            try:
                with self.assertRaises(TimeoutError):tx.drive_file(drive,root/'report.md','parent12345',entry,'text/markdown',root)
                with self.assertRaises(ReconcileRequired):tx.drive_file(drive,root/'report.md','parent12345',entry,'text/markdown',root)
                self.assertEqual(len(writes),1)
            finally:effects.db.close()

    def test_drive_readback_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(runtime,'atomic',atomic), \
             mock.patch('delivery.folder_for',return_value='clientfolder123'):
            root=Path(temp);source=directory(root/'drafts')/'report.md';source.write_bytes(b'report')
            entry={'relative':'report.md','size_bytes':6,'sha256':runtime.sha(b'report')}
            drive=types.SimpleNamespace(ensure_path=lambda folder,path:'destination123',publish=lambda *args:{
                'run_result':'passed','sha256':entry['sha256'],'readback_sha256':'wrong','size_bytes':6})
            tx=runtime.Transaction(types.SimpleNamespace(),drive=drive)
            tx.directory=lambda *args:'destination123'
            tx.drive_file=lambda *args:drive.publish()
            with self.assertRaisesRegex(ValueError,'full-content readback'):
                tx.deliver(root,{'request':{'request_id':'ted-route-123-dm456'}},{'files':[entry],'package_sha256':'a'*64},
                           {'work_folder_url':'https://drive.google.com/drive/folders/clientfolder123'})
            self.assertFalse((root/'drive-delivery.json').exists())


class ProjectionTests(unittest.TestCase):
    def test_actual_native_reader_accepts_projection_before_any_queue_ready_claim(self):
        import router as native
        with tempfile.TemporaryDirectory() as temp,mock.patch.object(runtime,'atomic',atomic), \
             mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes()):
            root=Path(temp);stage=directory(root/'qa');ident='ted-route-123-dm456';run=directory(root/'native'/ident)
            producer='11111111-1111-4111-8111-111111111111';reviewer='22222222-2222-4222-8222-222222222222'
            batch={'id':'prototype-'+'a'*32,'task_id':'123','owner':'owner','run_id':ident}
            request={'request_id':ident,'task_id':123,'client_id':'blue-dragonfly','reviewer_id':36398,
                     'feedback_authority':{'batch_id':batch['id'],'subtree':'luminary-counselling/'}}
            original={'request_id':ident,'thread_id':producer,'status':'needs_review','started_at':1,'artifact_manifest':['original']}
            (run/'receipt.json').write_text(json.dumps(original));before=(run/'receipt.json').read_bytes()
            old_delivery=b'{"files":["original17deliveryfiles"]}';old_completion=b'{"historical":"real prior proof"}'
            (run/'delivery.json').write_bytes(old_delivery);(run/'completion.json').write_bytes(old_completion)
            frozen={'request':request,'producer_thread_id':producer,'source':{'package_sha256':'a'*64},
                    'producer_receipt':{'request_id':ident,'thread_id':producer,'status':'needs_review','artifact_manifest':['corrected']}}
            qa={'approved':True,'source_package_sha256':'a'*64,'reviewer_thread_id':reviewer}
            workflow={'id':289562388,'name':'Deploy to lhmstaging','path':'.github/workflows/deploy.yml','head_sha':'b'*40,
                      'head_branch':'main','status':'completed','conclusion':'success','run_id':123,
                      'html_url':'https://github.com/michaellhm/lhm-prototype/actions/runs/123'}
            public={'url':'https://lhmstaging.net/prototypes/luminary-counselling/homepage/index.html','status':200,'bytes':13,'sha256':'e'*64}
            publication={'release':{'commit':'b'*40,'workflow':workflow,'source_package_sha256':'d'*64},
                         'public_files':[public],'changed_files':['luminary-counselling/homepage/index.html']}
            delivery={'package_sha256':'c'*64,'folder_url':'https://drive.google.com/drive/folders/evidence123','files':[]}
            handback={'status':'Under Review','commit':'b'*40,'reviewer_id':36398,'discussion_sha256':'f'*64,
                      'preview_url':'https://lhmstaging.net/prototypes/luminary-counselling/homepage/?rev=bbbbbbb'}
            backend=types.SimpleNamespace(route=mock.Mock(side_effect=lambda action,task_id:{'request_id':ident,'task_id':123,
                'completion':native.completion_proof(run/'completion.json',request)}))
            coordinator=types.SimpleNamespace(queue=mock.Mock(),backend=backend)
            tx=runtime.Transaction(coordinator,queue_root=root/'native')
            real=os.fstat
            def root_fstat(fd):
                info=real(fd);return types.SimpleNamespace(st_mode=info.st_mode,st_uid=0,st_nlink=info.st_nlink,st_size=info.st_size)
            with mock.patch.object(native.os,'fstat',side_effect=root_fstat):
                proof=tx.project(stage,batch,frozen,qa,delivery,publication,handback)
                self.assertEqual(native.completion_proof(run/'completion.json',request),proof)
            self.assertEqual((stage/'native-receipt-before-completion.json').read_bytes(),before)
            self.assertEqual((stage/'native-delivery-before-completion.json').read_bytes(),old_delivery)
            self.assertEqual((stage/'native-completion-before-completion.json').read_bytes(),old_completion)
            self.assertEqual(json.loads((run/'receipt.json').read_text())['artifact_manifest'],['corrected'])
            self.assertEqual(json.loads((run/'receipt.json').read_text())['started_at'],1)
            self.assertNotIn('notification_receipt',proof)
            coordinator.queue.ready.assert_not_called();coordinator.backend.route.assert_called_once_with('status',123)


class DiagnosticTests(unittest.TestCase):
    def test_semantic_only_ready_pilot_never_changes_queue_or_native_business_state(self):
        import sqlite3
        import host_runtime
        for approved in (True,False):
            with self.subTest(approved=approved),tempfile.TemporaryDirectory() as temp:
                root=Path(temp).resolve();state=directory(root/'state');qa_root=directory(root/'qa');stage=directory(qa_root/'pilot')
                ident='ted-route-123-dm456';thread='11111111-1111-4111-8111-111111111111';batch='prototype-'+'a'*32
                queue=directory(state/'state')/'queue.sqlite';db=sqlite3.connect(queue)
                db.executescript('CREATE TABLE batches(id TEXT,site TEXT,task_id TEXT,run_id TEXT,chat_url TEXT,state TEXT); CREATE TABLE messages(account TEXT,message_id TEXT,batch TEXT,packet TEXT);')
                db.execute('INSERT INTO batches VALUES (?,?,?,?,?,?)',(batch,'luminary-counselling','123',ident,'codex://threads/'+thread+'?hostId=hermes','ready_for_review'))
                packet={'message_id':'email1','items':[{'id':'1','request':'Use revised heading'}],'images':[]}
                db.execute('INSERT INTO messages VALUES (?,?,?,?)',('account','email1',batch,json.dumps(packet)));db.commit();db.close();queue.chmod(0o600)
                queue_before=queue.read_bytes()
                worker_root=directory(root/'client');task=directory(worker_root/'tasks'/ident);drafts=directory(task/'drafts')
                (drafts/'report.md').write_text('Unverified rebate claims are held and excluded.')
                run=directory(root/'runs'/ident)
                request={'request_id':ident,'task_id':123,'client_id':'blue-dragonfly','feedback_authority':{'batch_id':batch}}
                (run/'request.json').write_text(json.dumps(request));(run/'receipt.json').write_text(json.dumps({'thread_id':thread,'status':'needs_review'}))
                (run/'workspace-location.json').write_text(json.dumps({'workspace':str(worker_root),'task_directory':str(task)}))
                request_before=(run/'request.json').read_bytes();receipt_before=(run/'receipt.json').read_bytes()
                files=[]
                for page in runtime.PAGES:
                    path=directory((stage/'source'/page).parent)/Path(page).name;path.write_text('<h1>Exact source</h1>')
                    files.append({'path':page,'size_bytes':path.stat().st_size,'sha256':runtime.sha(path.read_bytes())})
                files.sort(key=lambda row:row['path'])
                manifest={'files':files,'pages':runtime.PAGES,'package_sha256':runtime.sha(runtime.canonical(files))}
                manifest_raw=runtime.canonical(manifest);(stage/'source-manifest.json').write_bytes(manifest_raw)
                mechanical={'status':'mechanical_passed','source_package_sha256':manifest['package_sha256'],
                    'source_manifest_sha256':runtime.sha(manifest_raw),'semantic_qa_approved':False,'pages':[
                    {'page':page,'viewport':{'width':w,'height':h},'status':'passed','errors':[]} for page in runtime.PAGES for w,h in ((1440,1000),(390,844))]}
                directory(stage/'output');(stage/'output/mechanical-qa.json').write_text(json.dumps(mechanical))
                backend=types.SimpleNamespace(basicops=mock.Mock(return_value={'status':'Under Review','assignee':36398,'reviewers':[36398]}))
                captured=[]
                def semantic(stage,evidence,producer):
                    captured.append(evidence)
                    return {'approved':approved,'source_package_sha256':manifest['package_sha256'],
                            'reviewer_thread_id':'22222222-2222-4222-8222-222222222222'}
                real=os.fstat
                def root_fstat(fd):
                    info=real(fd);return types.SimpleNamespace(st_mode=info.st_mode,st_uid=0,st_nlink=info.st_nlink,st_size=info.st_size)
                with mock.patch.object(runtime,'STATE_ROOT',state),mock.patch.object(runtime,'QA_ROOT',qa_root), \
                     mock.patch.object(runtime,'WORK',root/'runs'),mock.patch.object(runtime,'registration',return_value={
                         'client_id':'blue-dragonfly','reviewer_id':36398,'worker_root':str(worker_root)}), \
                     mock.patch.object(runtime,'protected_directory',directory),mock.patch.object(runtime,'atomic',atomic), \
                     mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes()), \
                     mock.patch.object(runtime.os,'fstat',side_effect=root_fstat),mock.patch.object(host_runtime,'NativeTed',return_value=backend), \
                     mock.patch('delivery.feedback_delivery_authority',return_value=True),mock.patch.object(runtime,'Transaction') as transaction:
                    result=runtime.semantic_diagnostic('luminary-counselling','pilot',123,qa=types.SimpleNamespace(semantic=semantic))
                    transaction.assert_not_called()
                self.assertEqual(result['approved'],approved)
                self.assertEqual(result['queue_state'],'ready_for_review')
                self.assertEqual(queue.read_bytes(),queue_before)
                self.assertEqual((run/'request.json').read_bytes(),request_before)
                self.assertEqual((run/'receipt.json').read_bytes(),receipt_before)
                backend.basicops.assert_called_once_with('get_task',{'taskId':123})
                self.assertEqual(captured[0]['items'][0]['id'],'email1:1')
                self.assertEqual(len(captured[0]['source_text']),5)
                self.assertTrue((stage/'semantic-diagnostic.json').is_file())


class BrowserNativeDiagnosticsTests(unittest.TestCase):
    def root_stats(self,fd):
        info=self.real_fstat(fd)
        return types.SimpleNamespace(st_mode=info.st_mode,st_uid=0,st_gid=10001,st_nlink=info.st_nlink,st_size=info.st_size)

    def test_no_receipt_records_native_success_failure_and_timeout_before_blocking(self):
        import host_runtime
        for scenario in ('success_without_output','native_failure','timeout'):
            with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as temp:
                stage=Path(temp).resolve();checker=stage/'checker.mjs';checker.write_text('// actual checker')
                manifest=runtime.canonical({'package_sha256':'a'*64});(stage/'source-manifest.json').write_bytes(manifest)
                writes=[];commands=[];original_atomic=host_runtime.atomic
                def tracked_atomic(path,data,**kwargs):
                    writes.append(path);return original_atomic(path,data,**kwargs)
                def runner(command,**kwargs):
                    commands.append(command)
                    if scenario=='timeout':
                        raise runtime.subprocess.TimeoutExpired(command,640,output=b'partial native stdout',stderr=b'private timeout detail')
                    return types.SimpleNamespace(returncode=0 if scenario=='success_without_output' else 7,
                        stdout='native stdout',stderr='private native failure' if scenario=='native_failure' else '')
                self.real_fstat=os.fstat
                with mock.patch.object(runtime,'VISUAL',str(checker)),mock.patch.object(runtime,'atomic',side_effect=tracked_atomic), \
                     mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes()), \
                     mock.patch.object(runtime.os,'fstat',side_effect=self.root_stats),mock.patch.object(runtime.os,'fchown') as owner, \
                     mock.patch.object(runtime.os,'chown'):
                    with self.assertRaisesRegex(ValueError,'private diagnostics: .*native-browser-run.json'):
                        runtime.QA(runner=runner).mechanical(stage)
                path=stage/'native-browser-run.json';record=json.loads(path.read_text())
                self.assertEqual(path.stat().st_mode&0o777,0o600)
                self.assertTrue(any(call.args[1:]==(0,0) for call in owner.call_args_list))
                self.assertTrue(all(path.parent==stage for path in writes))
                self.assertEqual(record['source_manifest_sha256'],runtime.sha(manifest))
                self.assertEqual(record['source_package_sha256'],'a'*64)
                self.assertEqual(record['checker_sha256'],runtime.sha(checker.read_bytes()))
                self.assertEqual(record['checker_path'],str(checker))
                self.assertEqual(record['unit'],'lhm-feedback-browser-'+stage.name)
                self.assertEqual(commands[0][-3],str(checker))
                self.assertFalse((stage/'output/mechanical-qa.json').exists())
                if scenario=='timeout':
                    self.assertEqual(record['status'],'timed_out');self.assertIsNone(record['returncode'])
                    self.assertEqual(record['stderr'],'private timeout detail')
                else:
                    self.assertEqual(record['status'],'exited')
                    self.assertEqual(record['returncode'],0 if scenario=='success_without_output' else 7)
                    self.assertEqual(record['stdout'],'native stdout')
                    if scenario=='native_failure':self.assertEqual(record['stderr'],'private native failure')

    def test_nonzero_requires_a_genuine_exact_failed_receipt_and_cannot_reuse_passed(self):
        for disposition in ('mechanical_failed','mechanical_passed','wrong_source'):
            with self.subTest(disposition=disposition),tempfile.TemporaryDirectory() as temp:
                stage=Path(temp).resolve();checker=stage/'checker.mjs';checker.write_text('// checker')
                source={'package_sha256':'a'*64};raw=runtime.canonical(source);(stage/'source-manifest.json').write_bytes(raw)
                receipt={'status':'mechanical_passed' if disposition=='mechanical_passed' else 'mechanical_failed',
                    'source_package_sha256':'b'*64 if disposition=='wrong_source' else 'a'*64,
                    'source_manifest_sha256':runtime.sha(raw),'semantic_qa_approved':False,
                    'pages':[{'page':page,'viewport':{'width':w,'height':h},'status':'passed' if disposition=='mechanical_passed' else 'failed',
                              'errors':[] if disposition=='mechanical_passed' else ['Actual check failed']}
                             for page in runtime.PAGES for w,h in ((1440,1000),(390,844))]}
                def runner(*args,**kwargs):
                    (stage/'output/mechanical-qa.json').write_text(json.dumps(receipt))
                    return types.SimpleNamespace(returncode=7,stdout='',stderr='native exit detail')
                with mock.patch.object(runtime,'VISUAL',str(checker)),mock.patch.object(runtime,'atomic',atomic), \
                     mock.patch.object(runtime,'root_bytes',lambda path,**kwargs:Path(path).read_bytes()), \
                     mock.patch.object(runtime,'root_json',lambda path:json.loads(path.read_text())),mock.patch.object(runtime.os,'chown'):
                    qa=runtime.QA(runner=runner)
                    if disposition=='mechanical_failed':self.assertEqual(qa.mechanical(stage),receipt)
                    else:
                        with self.assertRaisesRegex(ValueError,'private diagnostics:'):qa.mechanical(stage)
                        if disposition=='mechanical_passed':
                            with self.assertRaisesRegex(ValueError,'private diagnostics:'):qa.mechanical(stage)
                self.assertEqual(json.loads((stage/'native-browser-run.json').read_text())['stderr'],'native exit detail')


if __name__ == '__main__': unittest.main()
