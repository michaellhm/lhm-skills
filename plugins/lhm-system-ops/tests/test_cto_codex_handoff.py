import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SOURCE=Path(__file__).resolve().parents[1]/'assets/host/lhm-cto-codex-handoff.py'
spec=importlib.util.spec_from_file_location('cto_visible_handoff',SOURCE)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class VisibleHandoffTests(unittest.TestCase):
    def test_packet_keeps_parent_and_tests_but_never_exposes_callback_secret(self):
        request={'request_id':'r1','parent_run_id':'parent1','capability_incident_id':'incident1',
                 'objective':'Fix specific capability','acceptance_tests':['Regression passes'],
                 'return_point':'Original worker','resume_token':'SECRET-CALLBACK-TOKEN'}
        packet=module.packet(request,{'summary':'Investigated','sources':['Authoritative source']})
        self.assertNotIn('SECRET-CALLBACK-TOKEN',json.dumps(packet))
        self.assertEqual(packet['parent_run_id'],'parent1')
        self.assertEqual(packet['acceptance_tests'],['Regression passes'])
        self.assertEqual(packet['repository'],module.REPO)

    def test_completed_handoff_reuses_task_and_chat_without_starting_model_again(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=root/'config.json';cfg.write_text(json.dumps({'enabled':True,'project_id':69105,'repository':module.REPO}))
            state=root/'state';state.mkdir();saved={'task_id':123,'task_url':'https://app.basicops.com/task/123','chat_url':'codex://threads/existing','link_verified':True}
            (state/'incident1.json').write_text(json.dumps(saved))
            def api(name,args):
                if name=='get_current_user':return {'id':82491}
                if name=='get_project':return {'id':69105,'title':'*The Intervention'}
                if name=='get_task':return {'id':123,'project':{'id':69105},'description':'LHM CTO incident: incident1'}
                self.fail('Unexpected mutation: '+name)
            with patch.object(module,'CONFIG',cfg),patch.object(module,'STATE',state),patch.object(module,'api',side_effect=api),patch.object(module.subprocess,'Popen') as popen:
                self.assertEqual(module.handoff({'capability_incident_id':'incident1'},{}),saved)
                popen.assert_not_called()

    def test_unknown_create_outcome_never_creates_a_second_task(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);cfg=root/'config.json';cfg.write_text(json.dumps({'enabled':True,'project_id':69105,'repository':module.REPO}))
            (root/'incident1.json').write_text(json.dumps({'task_creation_pending':True}))
            def api(name,args):
                if name=='get_current_user':return {'id':82491}
                if name=='get_project':return {'id':69105,'title':'*The Intervention'}
                if name=='list_tasks':return []
                self.fail('Unexpected mutation: '+name)
            with patch.object(module,'CONFIG',cfg),patch.object(module,'STATE',root),patch.object(module,'api',side_effect=api):
                with self.assertRaisesRegex(ValueError,'outcome unknown'):
                    module.handoff({'capability_incident_id':'incident1'}, {})

    def test_creation_posts_real_session_link_and_verifies_it_on_same_board_task(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);state=root/'state';state.mkdir();work=root/'work';work.mkdir()
            cfg=root/'config.json';cfg.write_text(json.dumps({'enabled':True,'project_id':69105,'repository':module.REPO,'base_ref':'main'}))
            messages=[]
            task={'id':456,'url':'https://app.basicops.com/task/456','project':{'id':69105},'description':'LHM CTO incident: incident1'}
            def api(name,args):
                if name=='get_current_user':return {'id':82491}
                if name=='get_project':return {'id':69105,'title':'*The Intervention'}
                if name=='list_tasks':return []
                if name=='create_task':
                    self.assertEqual(args['projectId'],69105);return {'id':456}
                if name=='get_task':return task
                if name=='create_message_in_task':messages.append({'message':args['message']});return {'id':'dm1'}
                if name=='list_messages_in_task':return messages
                self.fail(name)
            def child(*args,**kwargs):
                run=work/'incident1/handoff'
                (run/'session.json').write_text(json.dumps({'thread_id':'12345678-1234-4234-8234-123456789abc'}))
                return SimpleNamespace(poll=lambda:0,returncode=0)
            with patch.object(module,'CONFIG',cfg),patch.object(module,'STATE',state),patch.object(module,'WORK',work),patch.object(module,'api',side_effect=api),patch.object(module.os,'chown'),patch.object(module.subprocess,'run',return_value=SimpleNamespace(returncode=0)),patch.object(module.subprocess,'Popen',side_effect=child):
                result=module.handoff({'request_id':'r1','parent_run_id':'p1','capability_incident_id':'incident1','objective':'Validate handoff','acceptance_tests':['Original task and real chat link']},{'summary':'Investigated'})
            self.assertTrue(result['link_verified'])
            self.assertEqual(result['task_id'],456)
            self.assertIn('12345678-1234-4234-8234-123456789abc',result['chat_url'])
            self.assertEqual(len(messages),1)


if __name__=='__main__':unittest.main()
