import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router-closeout'
def load(name):
    spec = importlib.util.spec_from_file_location(name, SOURCE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

host = load('host_closeout')
mcp = load('closeout_mcp')
REQUEST = {'request_id': 'ted-route-123-dm456', 'provider': 'claude', 'client_id': 'example',
           'task_id': 123, 'task_url': 'https://app.basicops.com/task/123', 'title': 'Example',
           'client': {'vault_prefix': '20 Clients/Example'}}


class CloseoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_draft_walk_rejects_symlinks_hardlinks_and_oversize(self):
        draft = self.root / 'draft.md'
        draft.write_text('approved close-out')
        self.assertEqual(host.read_file(draft), b'approved close-out')
        alias = self.root / 'alias.md'
        alias.symlink_to(draft)
        with self.assertRaises(OSError): host.read_file(alias)
        nested = self.root / 'nested'
        nested.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(OSError): host.read_file(nested / 'draft.md')
        os.link(draft, self.root / 'hard.md')
        with self.assertRaises(ValueError): host.read_file(draft)
        (self.root / 'large.md').write_bytes(b'x' * 10)
        with self.assertRaises(ValueError): host.read_file(self.root / 'large.md', 5)
        fifo = self.root / 'pipe'
        os.mkfifo(fifo)
        with self.assertRaises(ValueError): host.read_file(fifo)

    def test_closed_operations_and_no_arbitrary_path(self):
        packet = {'request_id': REQUEST['request_id'], 'operation': 'complete_task', 'arguments': {}}
        with self.assertRaises(ValueError): host.handle(packet)
        packet['operation'] = 'post_basicops_closeout'
        with patch.object(host, 'ROOT', self.root), patch.object(host, 'authority', return_value=(REQUEST, self.root)):
            for name in ('../other.md', '/etc/passwd', 'nested/closeout.md', '.hidden.md'):
                packet['arguments'] = {'draft_name': name}
                with self.assertRaises(ValueError): host.handle(packet)

    def test_remote_path_is_registered_not_caller_supplied(self):
        self.assertEqual(host.remote_note(REQUEST), '20 Clients/Example/Task Close-outs/ted-route-123-dm456.md')
        for prefix in ('/etc', '20 Clients/../Other', '30 Projects/Other'):
            with self.assertRaises(ValueError): host.remote_note({**REQUEST, 'client': {'vault_prefix': prefix}})

    def test_basicops_post_readback_dedup_and_changed_draft(self):
        messages, calls = [], []
        def api(name, arguments):
            calls.append(name)
            if name == 'get_task': return {'id': 123, 'url': REQUEST['task_url']}
            if name == 'get_current_user': return {'id': 7}
            if name == 'list_messages_in_task': return messages
            if name == 'create_message_in_task':
                messages.append({'id': 'dm789', 'user': 7, 'message': arguments['message']})
                return messages[-1]
            self.fail('Unbounded API operation')
        actor = types.SimpleNamespace(actor=lambda m: m['user'])
        state = self.root / 'state.json'
        with patch.object(host, 'api', side_effect=api), patch.dict(sys.modules, {'router': actor}):
            first = host.post(REQUEST, b'Close-out <verified> & ready\n', state)
            again = host.post(REQUEST, b'Close-out <verified> & ready\n', state)
            self.assertEqual(first, again)
            self.assertEqual(calls.count('create_message_in_task'), 1)
            with self.assertRaises(ValueError): host.post(REQUEST, b'Changed', state)

    def test_uncertain_basicops_attempt_never_reposts(self):
        content = b'Close-out'
        state = self.root / 'state.json'
        host.save(state, {'sha256': host.hashlib.sha256(content).hexdigest(), 'attempted': True})
        def api(name, args):
            if name == 'get_task': return {'id': 123, 'url': REQUEST['task_url']}
            if name == 'get_current_user': return {'id': 7}
            if name == 'list_messages_in_task': return []
            self.fail('Must not retry mutation after uncertain outcome')
        with patch.object(host, 'api', side_effect=api), patch.dict(sys.modules, {'router': types.SimpleNamespace(actor=lambda m: 7)}):
            with self.assertRaisesRegex(ValueError, 'uncertain'): host.post(REQUEST, content, state)

    def test_knowledge_conflict_does_not_write(self):
        with patch.object(host, 'knowledge_read', return_value=b'Human-authored note'), patch.object(host.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'overwrite'): host.write_note(REQUEST, b'Close-out', self.root / 'state.json')
            run.assert_not_called()

    def test_knowledge_copy_is_create_only_and_requires_readback(self):
        captured = []
        def copy(command, **kwargs):
            self.assertIn('--ignore-existing', command)
            captured.append(Path(command[2]).read_bytes())
            return types.SimpleNamespace(returncode=0)
        reads = [None]
        def read(relative):
            return reads.pop(0) if reads else captured[0]
        with patch.object(host, 'ROOT', self.root), patch.object(host, 'knowledge_read', side_effect=read), patch.object(host.subprocess, 'run', side_effect=copy):
            result = host.write_note(REQUEST, b'Close-out', self.root / 'state.json')
            self.assertEqual(result['status'], 'verified')
        with patch.object(host, 'knowledge_read', return_value=b'Wrong readback'):
            with self.assertRaises(ValueError): host.write_note(REQUEST, b'Close-out', self.root / 'other.json')

    def test_mcp_only_exposes_bounded_tools(self):
        tools = mcp.dispatch({'method': 'tools/list'})['tools']
        self.assertEqual({t['name'] for t in tools}, host.OPERATIONS)
        self.assertTrue(all(not t['inputSchema']['additionalProperties'] for t in tools))
        result = mcp.dispatch({'method': 'tools/call', 'params': {'name': 'update_task'}})
        self.assertTrue(result['isError'])

    def test_wrong_basicops_task_never_posts(self):
        with patch.object(host, 'api', return_value={'id': 999, 'url': 'https://app.basicops.com/task/999'}) as api:
            with self.assertRaisesRegex(ValueError, 'identity'): host.post(REQUEST, b'Close-out', self.root / 'state.json')
            self.assertEqual(api.call_count, 1)

    def test_failed_basicops_readback_is_not_success(self):
        calls = []
        def api(name, args):
            calls.append(name)
            if name == 'get_task': return {'id': 123, 'url': REQUEST['task_url']}
            if name == 'get_current_user': return {'id': 7}
            if name == 'list_messages_in_task': return []
            if name == 'create_message_in_task': return {'id': 'dm789'}
            self.fail('Unsupported API call')
        with patch.object(host, 'api', side_effect=api), patch.dict(sys.modules, {'router': types.SimpleNamespace(actor=lambda m: 7)}):
            with self.assertRaisesRegex(ValueError, 'readback'): host.post(REQUEST, b'Close-out', self.root / 'state.json')
            self.assertNotEqual(json.loads((self.root / 'state.json').read_text()).get('status'), 'verified')

    def test_unprivileged_peer_is_rejected_before_reading_packet(self):
        import struct
        handler = object.__new__(host.Handler)
        handler.request = unittest.mock.Mock()
        handler.request.getsockopt.return_value = struct.pack('3i', 123, 10001, 10001)
        handler.rfile = unittest.mock.Mock()
        handler.wfile = unittest.mock.Mock()
        with patch.object(host.socket, 'SO_PEERCRED', 17, create=True):
            handler.handle()
        handler.rfile.readline.assert_not_called()
        self.assertIn(b'Claude worker peer identity required', handler.wfile.write.call_args.args[0])

    def test_mcp_initialization_and_tool_argument_forwarding(self):
        result = mcp.dispatch({'method': 'initialize', 'params': {'protocolVersion': '2025-03-26'}})
        self.assertEqual(result['protocolVersion'], '2025-03-26')
        with patch.object(mcp, 'call_broker', return_value={'status': 'verified'}) as broker:
            mcp.dispatch({'method': 'tools/call', 'params': {'name': 'post_basicops_closeout', 'arguments': {'draft_name': 'closeout.md'}}})
            broker.assert_called_once_with('post_basicops_closeout', {'draft_name': 'closeout.md'})


if __name__ == '__main__':
    unittest.main()
