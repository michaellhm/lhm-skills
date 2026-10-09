import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('loop', Path(__file__).parents[1] / 'scripts/website_loop.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class API:
    def __init__(self):
        self.messages = []; self.posts = 0; self.fail = False
        self.task = {'id': 1, 'project': {'id': 68635}, 'status': 'Accepted'}
    def identity(self): pass
    def call(self, name, args):
        if name == 'get_task': return self.task
        if name == 'list_replies_in_message': return {'data': []}
        if name == 'create_message_in_task':
            self.posts += 1
            self.messages.append({'id': 'm1', 'message': args['message']})
            if self.fail: raise TimeoutError()
            return {'id': 'm1'}
        raise AssertionError(name)
    def pages(self, name, args):
        if name == 'list_messages_in_task': return json.loads(json.dumps(self.messages))
        if name == 'list_replies_in_message': return []
        if name == 'list_tasks_in_project': return [self.task]
        raise AssertionError(name)


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        (root/'profile.md').write_text('Test profile'); (root/'project.md').write_text('- [ ] Build\n- [ ] Client approval')
        self.cfg = {'state':str(root/'state'),'vault':str(root),'projects':{'1':{'profile':'profile.md','project':'project.md'}}}
        self.api = API(); self.week = '2026-10-12'
        self.dep = patch.object(m, 'dependency', return_value={'week':self.week}); self.dep.start(); self.addCleanup(self.dep.stop)
        self.archive = patch.object(m, 'verify_archive'); self.archive.start(); self.addCleanup(self.archive.stop)
        self.snap = m.prepare(self.cfg,self.api,self.week)
        self.plan = {'snapshot_sha256':self.snap['sha256'],'summaries':[{'task_id':1,'message':'Review; client approval remains pending.'}]}
    def test_retry_does_not_duplicate(self):
        self.assertEqual(m.apply(self.cfg,self.api,self.week,self.plan)['items'][0]['state'],'posted_verified')
        self.assertEqual(m.apply(self.cfg,self.api,self.week,self.plan)['items'][0]['state'],'already_present')
        self.assertEqual(self.api.posts,1)
    def test_uncertain_post_reconciles_before_retry(self):
        self.api.fail=True
        self.assertEqual(m.apply(self.cfg,self.api,self.week,self.plan)['items'][0]['state'],'blocked_uncertain_post')
        self.assertEqual(m.apply(self.cfg,self.api,self.week,self.plan)['items'][0]['state'],'already_present')
        self.assertEqual(self.api.posts,1)
    def test_changed_note_blocks_write(self):
        (Path(self.temp.name)/'project.md').write_text('New client correction')
        self.assertEqual(m.apply(self.cfg,self.api,self.week,self.plan)['items'][0]['state'],'blocked_changed_evidence')
        self.assertEqual(self.api.posts,0)
    def test_missing_dependency_blocks_write(self):
        with patch.object(m,'dependency',side_effect=ValueError('No archive')):
            with self.assertRaises(ValueError): m.apply(self.cfg,self.api,self.week,self.plan)
        self.assertEqual(self.api.posts,0)
    def test_unmapped_target_and_duplicate_rejected(self):
        for entries in [[{'task_id':2,'message':'bad'}],self.plan['summaries']*2]:
            with self.assertRaises(ValueError): m.apply(self.cfg,self.api,self.week,dict(self.plan,summaries=entries))
    def test_outside_vault_rejected(self):
        self.cfg['projects']['1']['project']='../outside.md'
        with self.assertRaises(ValueError): m.context(self.cfg,'1')
    def test_pagination_repeated_cursor_rejected(self):
        api=object.__new__(m.BasicOps); api.call=lambda *a: {'data':[{'id':1}],'nextPage':'same'}
        with self.assertRaises(ValueError): api.pages('list_tasks',{})


if __name__=='__main__': unittest.main()
