import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

SOURCE=Path(__file__).resolve().parents[1]/'assets/task-router/correction_worker.py'
spec=importlib.util.spec_from_file_location('feedback_correction_test',SOURCE)
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)


class CorrectionTests(unittest.TestCase):
    def fixture(self, root):
        ident='ted-route-123-dm456';batch='prototype-'+'a'*32
        workspace=root/'clients/blue-dragonfly';task=workspace/'tasks'/ident
        (task/'drafts').mkdir(parents=True);(workspace/'.control').mkdir();(workspace/'.control/worker.lock').touch()
        (task/'task-context.json').write_text('Original active brief')
        run=root/'runs'/ident;run.mkdir(parents=True)
        request={'request_id':ident,'client_id':'blue-dragonfly','provider':'codex','title':'Revision',
                 'feedback_authority':{'batch_id':batch}}
        raw=json.dumps(request).encode();(run/'request.json').write_bytes(raw)
        thread='11111111-1111-4111-8111-111111111111'
        receipt={'status':'needs_review','thread_id':thread,'request_id':ident,'provider':'codex','artifact_manifest':[]}
        (run/'receipt.json').write_text(json.dumps(receipt))
        stage=root/'qa'/ (ident+'-r0');stage.mkdir(parents=True)
        authority={'schema_version':1,'request_id':ident,'batch_id':batch,'revision':1,'thread_id':thread,
                   'request_sha256':worker.digest(raw),'client_id':'blue-dragonfly','task_directory':str(task),
                   'workspace':str(workspace),'reason':'Fix mobile overflow','qa_sha256':'a'*64}
        return stage/'correction-authority.json',authority,run,task

    def test_resumes_same_native_chat_without_overwriting_brief(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path,authority,run,task=self.fixture(root)
            calls=[]
            def conversation(native_task,prompt,logs,**kwargs):
                calls.append((native_task,prompt,logs,kwargs));(task/'drafts/report.md').write_text('Corrected')
                return authority['thread_id']
            native=types.SimpleNamespace(conversation=conversation)
            loader=types.SimpleNamespace(exec_module=lambda module:None)
            with mock.patch.object(worker,'QA_ROOT',root/'qa'),mock.patch.object(worker,'WORK_ROOT',root/'runs'), \
                 mock.patch.object(worker,'WORKSPACE_ROOT',root/'clients'),mock.patch.object(worker.os,'geteuid',return_value=10001), \
                 mock.patch.object(worker,'protected',return_value=authority), \
                 mock.patch.object(worker.importlib.util,'spec_from_file_location',return_value=types.SimpleNamespace(loader=loader)), \
                 mock.patch.object(worker.importlib.util,'module_from_spec',return_value=native):
                worker.execute(path)
            receipt=json.loads((run/'receipt.json').read_text())
            self.assertEqual(receipt['status'],'needs_review')
            self.assertEqual(receipt['thread_id'],authority['thread_id'])
            self.assertEqual(receipt['qa_correction_revision'],1)
            self.assertEqual(calls[0][0]['resume_thread_id'],authority['thread_id'])
            self.assertTrue(calls[0][3]['read_only_integrations'])
            self.assertEqual((task/'task-context.json').read_text(),'Original active brief')
            self.assertEqual(receipt['artifact_manifest'][0]['relative'],'report.md')

    def test_busy_worker_never_starts_correction_or_changes_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path,authority,run,task=self.fixture(root);before=(run/'receipt.json').read_bytes()
            with mock.patch.object(worker,'QA_ROOT',root/'qa'),mock.patch.object(worker,'WORK_ROOT',root/'runs'), \
                 mock.patch.object(worker,'WORKSPACE_ROOT',root/'clients'),mock.patch.object(worker.os,'geteuid',return_value=10001), \
                 mock.patch.object(worker,'protected',return_value=authority),mock.patch.object(worker.fcntl,'flock',side_effect=BlockingIOError), \
                 mock.patch.object(worker.importlib.util,'spec_from_file_location') as native:
                with self.assertRaisesRegex(ValueError,'another worker is active'):worker.execute(path)
                native.assert_not_called()
            self.assertEqual((run/'receipt.json').read_bytes(),before)
            self.assertFalse((run/'qa-correction-1').exists())


if __name__=='__main__':unittest.main()
