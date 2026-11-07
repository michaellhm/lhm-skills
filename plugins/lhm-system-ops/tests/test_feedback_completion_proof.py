import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import types
import unittest
from unittest import mock

SOURCE=Path(__file__).resolve().parents[1]/'assets/task-router/router.py'
spec=importlib.util.spec_from_file_location('feedback_proof_router',SOURCE)
router=importlib.util.module_from_spec(spec);spec.loader.exec_module(router)


def proof_for(request,thread):
    commit='b'*40
    return {'schema_version':1,'status':'verified_for_review','request_id':request['request_id'],'task_id':123,
        'client_id':'blue-dragonfly','batch_id':request['feedback_authority']['batch_id'],'producer_thread_id':thread,
        'source_package_sha256':'a'*64,'qa_receipt_sha256':'a'*64,'delivery_package_sha256':'a'*64,
        'publication_package_sha256':'a'*64,'commit':commit,'workflow':{'id':289562388,'name':'Deploy to lhmstaging',
        'path':'.github/workflows/deploy.yml','head_sha':commit,'head_branch':'main','status':'completed','conclusion':'success',
        'run_id':123,'html_url':'https://github.com/michaellhm/lhm-prototype/actions/runs/123'},
        'public_files':[{'url':'https://lhmstaging.net/prototypes/luminary-counselling/homepage/index.html','status':200,'bytes':10,'sha256':'a'*64}],
        'changed_files':['luminary-counselling/homepage/index.html'],
        'preview_url':'https://lhmstaging.net/prototypes/luminary-counselling/homepage/?rev='+commit[:7],
        'reviewer_id':36398,'basicops_status':'Under Review','discussion_sha256':'a'*64,
        'drive_folder_url':'https://drive.google.com/drive/folders/evidence123','handback_receipt_sha256':'a'*64,'verified_at':int(time.time())}


class ProofTests(unittest.TestCase):
    def fixture(self,root,feedback=True,session=True):
        state=root/'state';queue=root/'queue';state.mkdir();run=queue/'runs/ted-route-123-dm456';run.mkdir(parents=True)
        request={'task_id':123,'task_url':'https://app.basicops.com/task/123','request_id':run.name,'provider':'codex',
            'reason':'prototype','client_id':'blue-dragonfly','title':'Prototype feedback','reviewer_id':36398,'instruction_message_id':'dm456'}
        if feedback:request['feedback_authority']={'batch_id':'prototype-'+'a'*32,'subtree':'luminary-counselling/'}
        thread='11111111-1111-4111-8111-111111111111'
        (state/'123.json').write_text(json.dumps({'request':request,'notification':None,'session_notification':{'verified':True} if session else None}))
        (run/'receipt.json').write_text(json.dumps({'request_id':run.name,'provider':'codex','status':'needs_review','thread_id':thread,'delivery_required':True}))
        (run/'delivery.json').write_text(json.dumps({'artefact_state':'delivered','package_sha256':'a'*64,'folder_url':'https://drive.google.com/drive/folders/evidence123','files':[]}))
        instance=object.__new__(router.Router);instance.state=state;instance.queue=queue
        instance.config={'agent_user_id':82491,'reviewer_id':36398,'codex_host_id':'remote-control:env_e_test'}
        messages=[]
        def api(name,args):
            if name=='list_messages_in_task':return messages
            if name=='create_message_in_task':
                value={'id':'dm'+str(1000+len(messages)),'user':82491,'message':args['message']};messages.append(value);return value
            raise AssertionError(name)
        instance.api=api;instance.contract=lambda *args,**kwargs:({'assignee':82491},request)
        return instance,request,thread,run,messages

    def root_fstat(self,fd):
        info=self.real_fstat(fd)
        return types.SimpleNamespace(st_mode=info.st_mode,st_uid=0,st_nlink=info.st_nlink,st_size=info.st_size)

    def test_root_proof_projected_without_notification_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            instance,request,thread,run,messages=self.fixture(Path(temp))
            proof=proof_for(request,thread);(run/'completion.json').write_text(json.dumps(proof))
            self.real_fstat=os.fstat
            with mock.patch.object(router.os,'fstat',side_effect=self.root_fstat):result=instance.status(123)
            self.assertEqual(result['completion'],proof)
            self.assertIsNone(result['notification']);self.assertIsNone(result['delivery_notification'])
            self.assertNotIn('notification_receipt',result['completion'])

    def test_zero_workflow_or_other_native_thread_is_rejected(self):
        for wrong in ('workflow','thread'):
            with self.subTest(wrong=wrong),tempfile.TemporaryDirectory() as temp:
                instance,request,thread,run,messages=self.fixture(Path(temp));proof=proof_for(request,thread)
                if wrong=='workflow':proof['workflow']['run_id']=0
                else:proof['producer_thread_id']='22222222-2222-4222-8222-222222222222'
                (run/'completion.json').write_text(json.dumps(proof));self.real_fstat=os.fstat
                with mock.patch.object(router.os,'fstat',side_effect=self.root_fstat),self.assertRaises(ValueError):instance.status(123)

    def test_feedback_skips_generic_result_and_drive_handbacks(self):
        with tempfile.TemporaryDirectory() as temp:
            instance,request,thread,run,messages=self.fixture(Path(temp))
            result=instance.reconcile(123)
            self.assertEqual(messages,[]);self.assertIsNone(result['notification'])
            self.assertIsNone(result['delivery_notification'])

    def test_feedback_still_preserves_existing_session_link(self):
        with tempfile.TemporaryDirectory() as temp:
            instance,request,thread,run,messages=self.fixture(Path(temp),session=False)
            result=instance.reconcile(123)
            self.assertEqual(len(messages),1);self.assertTrue(result['session_notification']['verified'])
            self.assertIn('session available',messages[0]['message'])
            self.assertNotIn('TED central route:',messages[0]['message'])
            self.assertIsNone(result['notification'])

    def test_ordinary_route_retains_generic_delivery_and_result(self):
        with tempfile.TemporaryDirectory() as temp:
            instance,request,thread,run,messages=self.fixture(Path(temp),feedback=False)
            result=instance.reconcile(123)
            self.assertEqual(len(messages),2)
            self.assertTrue(result['notification']['verified'])
            self.assertTrue(any('TED central route:' in row['message'] for row in messages))
            self.assertTrue(any('TED Drive delivery:' in row['message'] for row in messages))


if __name__=='__main__':unittest.main()
