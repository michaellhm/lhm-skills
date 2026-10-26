import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router'
spec = importlib.util.spec_from_file_location('task_interactive', SOURCE / 'interactive.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InteractiveTests(unittest.TestCase):
    def setUp(self):
        agent = patch('capabilities.agent_definition', return_value={'description':'test', 'prompt':'Lead'})
        agent.start(); self.addCleanup(agent.stop)
        self.request = {'title':'Morr: Google Ads', 'description':'Linked original report',
                        'instruction':'I approve A2, A3, A4; implement via AdPulse',
                        'instruction_message_id':'dm123', 'context_messages':[{'text':'A1 remains proposed'}]}

    def test_connected_same_session_keeps_native_approval_and_exact_human_context(self):
        self.request['resume_thread_id'] = 'existing'
        with patch.object(Path, 'is_file', return_value=True):
            cmd = module.command(self.request, Path('/registered/tasks/request'), 'existing')
        self.assertEqual(cmd[cmd.index('--resume')+1], 'existing')
        self.assertIn('--remote-control', cmd)
        self.assertNotIn('-p', cmd)
        self.assertNotIn('--strict-mcp-config', cmd)
        self.assertNotIn('--dangerously-skip-permissions', cmd)
        self.assertEqual(cmd[cmd.index('--permission-mode')+1], 'default')
        self.assertNotIn('adpulse_graphql_mutation',cmd[cmd.index('--allowedTools')+1])
        self.assertIn(self.request['instruction'], cmd[-1])
        self.assertIn('A1 remains proposed', cmd[-1])
        self.assertIn('not a completed change', cmd[-1])
        settings=json.loads((SOURCE/'task-execution.settings.json').read_text())
        self.assertIn('mcp__claude_ai_AdPulse_MCP__adpulse_graphql_mutation',settings['permissions']['ask'])

    def test_missing_profile_still_opens_a_conversation_and_reports_exact_gap(self):
        with patch.object(Path,'is_file',return_value=False):
            cmd=module.command(self.request,Path('/task'),'local-uuid')
            self.assertIn('--remote-control',cmd)
            self.assertIn('connector profile is missing',cmd[-1])
            self.assertIn('{"mcpServers":{}}',cmd)
        self.assertFalse(module.URL.findall('claude --resume local-uuid'))
        self.assertFalse(module.URL.findall('https://claude.ai/code/session_partial'))
        self.assertEqual(module.URL.findall('https://claude.ai/code/session_real123\n'),['https://claude.ai/code/session_real123'])

    def test_receipt_is_atomic_and_heartbeat_preserves_provider_approval_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp);r={'status':'interactive','thread_id':'existing','delivery_required':False}
            module.save(run,r);saved=json.loads((run/'receipt.json').read_text())
            self.assertGreater(saved['heartbeat_at'],0)
            self.assertEqual(saved['status'],'interactive')
            self.assertFalse(saved['delivery_required'])

    def test_terminal_connects_but_never_answers_a_native_tool_approval(self):
        calls=[];screens=iter(['No, exit\nYes, I trust this folder\n',
                              'https://claude.ai/code/session_native123\nDo you want to proceed?\n'])
        states=iter(['0:\n','0:\n','1:0\n'])
        def run(args,**kwargs):
            calls.append(args)
            if 'display-message' in args:return SimpleNamespace(returncode=0,stdout=next(states))
            if 'capture-pane' in args:return SimpleNamespace(returncode=0,stdout=next(screens))
            return SimpleNamespace(returncode=0,stdout='')
        with tempfile.TemporaryDirectory() as tmp, patch.object(module,'command',return_value=['claude']), patch.object(module.subprocess,'run',side_effect=run), patch.object(module.time,'sleep'):
            r={'thread_id':'saved'};module.run_session(self.request,Path(tmp),Path('/registered'),Path('/registered/task'),r)
            self.assertEqual(r['remote_session_url'],'https://claude.ai/code/session_native123')
        sent=[c for c in calls if 'send-keys' in c]
        self.assertEqual(len(sent),1)
        self.assertEqual(sent[0][-2:],['Down','Enter'])
        self.assertEqual(sum('new-session' in c for c in calls),1)


if __name__ == '__main__': unittest.main()
