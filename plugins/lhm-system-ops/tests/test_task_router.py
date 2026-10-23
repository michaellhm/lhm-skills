import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/router.py'
spec = importlib.util.spec_from_file_location('router', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / 'queue'
        (self.queue / 'incoming').mkdir(parents=True)
        self.task = {'id': 123, 'url': 'https://app.basicops.com/task/123',
                     'title': 'Example Clinic: write a client update', 'description': 'Use the supplied notes.',
                     'assignee': 82491, 'status': 'In Progress'}
        self.messages = [{'id': 'dm123', 'user': 36398, 'created': 1, 'message': '@Ted can we work on this?'}]
        (self.root / 'task-router.json').write_text(json.dumps({
            'agent_user_id': 82491, 'reviewer_id': 36398, 'providers': {'codex': True, 'claude': True},
            'clients': {'example': {'name': 'Example Clinic', 'vault_prefix': '20 Clients/Example Clinic/', 'basicops_task_ids': []}}}))
        def api(name, args):
            if name == 'get_current_user': return {'id': 82491}
            if name == 'get_task': return self.task
            if name == 'list_messages_in_task': return self.messages
            if name == 'create_message_in_task':
                self.messages.append({'id': 'dm999', 'user': 82491, 'message': args['message']})
                return {'id': 'dm999'}
            raise AssertionError(name)
        self.router = module.Router(self.root, self.queue, api)

    def test_natural_request_uses_claude_without_plan(self):
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.assertEqual(self.router.submit(123, 'dm123')['status'], 'queued')

    def test_mixed_work_uses_one_codex_session(self):
        self.task['description'] = 'Revise the handbook on Google Drive and update the prototype website.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'codex')

    def test_only_personal_instruction_can_override(self):
        self.task['description'] = 'use codex'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'claude')
        self.messages[0]['message'] += ' Please use Codex.'
        self.assertEqual(self.router.preview(123, 'dm123')['provider'], 'codex')

    def test_agent_relay_and_ai_authorship_rejected(self):
        for user, text in [(82491, 'work on this'), (36398, 'AI authorship: agent. work on this')]:
            self.messages[0].update(user=user, message=text)
            with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_repeated_request_enqueues_once(self):
        one = self.router.submit(123, 'dm123')
        self.assertEqual(one, self.router.submit(123, 'dm123'))
        self.assertEqual(len(list((self.queue / 'incoming').glob('*.json'))), 1)

    def test_changed_task_does_not_duplicate(self):
        self.router.submit(123, 'dm123')
        self.task['description'] = 'different scope'
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_missing_or_ambiguous_client_is_not_guessed(self):
        self.task['title'] = 'Write an update'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')
        self.router.config['clients']['second'] = {'name': 'Second Clinic'}
        self.task['title'] = 'Example Clinic / Second Clinic'
        with self.assertRaises(ValueError): self.router.preview(123, 'dm123')

    def test_unavailable_provider_not_substituted(self):
        self.router.config['providers']['claude'] = False
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_later_stop_cancels_unstarted_request(self):
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted hold this please'})
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_legacy_pilot_not_duplicated(self):
        (self.root / 'codex-session-state').mkdir()
        (self.root / 'codex-session-state/123.json').write_text('{}')
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_feedback_resumes_same_session(self):
        saved = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / saved['request_id']
        run.mkdir(parents=True)
        (run / 'receipt.json').write_text(json.dumps({'status': 'needs_review', 'thread_id': 'saved-session'}))
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted revise the wording please'})
        self.router.submit(123, 'dm124')
        request = json.loads(next((self.queue / 'incoming').glob('*dm124.json')).read_text())
        self.assertEqual(request['resume_thread_id'], 'saved-session')
        self.assertEqual(request['provider'], 'claude')
        self.assertEqual(self.router.submit(123, 'dm124')['status'], 'queued')

    def test_active_session_does_not_accept_duplicate_feedback(self):
        self.router.submit(123, 'dm123')
        self.messages.append({'id': 'dm124', 'user': 36398, 'created': 2, 'message': '@Ted revise the wording please'})
        with self.assertRaises(ValueError): self.router.submit(123, 'dm124')

    def test_assignment_alone_not_permission(self):
        self.messages[0]['message'] = 'Thanks Ted'
        with self.assertRaises(ValueError): self.router.submit(123, 'dm123')

    def test_restart_handback_exactly_once(self):
        saved = self.router.submit(123, 'dm123')
        run = self.queue / 'runs' / saved['request_id']
        run.mkdir(parents=True)
        (run / 'receipt.json').write_text(json.dumps({'status': 'needs_review', 'thread_id': 'saved'}))
        (run / 'result.md').write_text('Useful actual draft')
        self.router.reconcile(123)
        self.router.reconcile(123)
        self.assertEqual(len(self.messages), 2)
        self.assertEqual(self.task['status'], 'In Progress')


if __name__ == '__main__': unittest.main()
