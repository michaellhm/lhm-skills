import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router'
sys.path.insert(0,str(SOURCE))
spec=importlib.util.spec_from_file_location('dispatch_handoff',SOURCE/'dispatch.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HandoffCopyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.work=self.root/'work';self.queue=self.root/'queue'
        self.old_id='ted-route-123-dm1'
        old=self.work/self.old_id;old.mkdir(parents=True)
        (old/'workspace/drafts').mkdir(parents=True)
        (old/'workspace/drafts/review.md').write_text('Prior analysis, not fresh readback')
        (old/'result.md').write_text('Draft ready')
        self.request={'task_id':123,'client_id':'alpha','provider':'claude','permission_ceiling':'prepare_for_review',
                      'provider_handoff':{'request_id':self.old_id,'from_provider':'codex','thread_id':'saved'}}
        (old/'request.json').write_text(json.dumps({'task_id':123,'client_id':'alpha','provider':'codex',
                 'permission_ceiling':'prepare_for_review','request_id':self.old_id}))
        q=self.queue/'runs'/self.old_id;q.mkdir(parents=True)
        (q/'receipt.json').write_text(json.dumps({'status':'needs_review','provider':'codex','thread_id':'saved'}))
        self.target=self.root/'target';self.target.mkdir()
        for key,value in [('WORK',self.work),('BASE',self.queue)]:
            patcher=patch.object(module,key,value);patcher.start();self.addCleanup(patcher.stop)

    def test_preserves_result_drafts_and_audit_without_copying_secrets_or_symlinks(self):
        old=self.work/self.old_id
        (old/'workspace/drafts/private.md').symlink_to(old/'request.json')
        (old/'workspace/drafts/oversized.md').write_text('x'*64001)
        module.copy_prior(self.request,self.target)
        files=list((self.target/'prior-work').glob('*'))
        self.assertEqual(len(files),3)
        manifest=json.loads((self.target/'prior-work/manifest.json').read_text())
        self.assertEqual(len(manifest['files']),2)
        self.assertEqual(manifest['source']['thread_id'],'saved')
        self.assertFalse(any('private' in p.name or 'oversized' in p.name for p in files))

    def test_rejects_wrong_client_live_source_or_unregistered_working_path(self):
        self.request['client_id']='other'
        with self.assertRaises(ValueError):module.copy_prior(self.request,self.target)
        self.request['client_id']='alpha'
        q=self.queue/'runs'/self.old_id/'receipt.json';d=json.loads(q.read_text());d['status']='running';q.write_text(json.dumps(d))
        with self.assertRaises(ValueError):module.copy_prior(self.request,self.target)
        d['status']='needs_review';q.write_text(json.dumps(d))
        (self.work/self.old_id/'workspace-location.json').write_text(json.dumps({'workspace':'/etc','task_directory':'/etc'}))
        with self.assertRaises(ValueError):module.copy_prior(self.request,self.target)

if __name__=='__main__':unittest.main()
