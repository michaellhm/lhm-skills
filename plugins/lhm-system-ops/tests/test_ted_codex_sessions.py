import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).parents[1] / 'assets/container/ted_codex_sessions.py'
spec = importlib.util.spec_from_file_location('bridge', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BasicOps:
    def __init__(self):
        self.task = {'id': 123, 'project': {'id': 10}, 'assignee': {'id': 20},
                     'status': 'In Progress', 'title': 'Wellness pilot', 'url': 'https://app.basicops.com/task'}
        self.messages = [
            {'id': 'plan', 'user': 20, 'created': 1,
             'message': 'TED PLAN v1 — AWAITING APPROVAL. Saved-context review-only brief.'},
            {'id': 'approve', 'user': 30, 'created': 2, 'message': 'Approve TED PLAN v1.'},
        ]
        self.writes = []

    def __call__(self, name, args):
        if name == 'get_current_user':
            return {'id': 20}
        if name == 'get_task':
            return self.task
        if name == 'list_messages_in_task':
            return {'data': self.messages}
        if name == 'list_replies_in_message':
            return {'data': []}
        self.writes.append((name, args))
        if name == 'create_message_in_task':
            self.messages.append({'id': 'handback', 'user': 20, 'created': 3, 'message': args['message']})
            return {'id': 'handback'}
        if name == 'request_review':
            return {'success': True}
        if name == 'update_task':
            self.task.update(status=args['status'], assignee={'id': args['assignee']})
            return self.task
        raise AssertionError(name)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = self.root / 'queue'
        (self.queue / 'incoming').mkdir(parents=True)
        (self.queue / 'runs').mkdir()
        self.api = BasicOps()
        config = self.root / 'config.json'
        config.write_text(json.dumps({'agent_user_id': 20, 'tasks': {
            '123': {'enabled': True, 'client_id': 'wellness-chiropractic', 'project_id': 10, 'reviewer_id': 30}}}))
        self.bridge = module.Bridge(config, self.queue, self.root / 'state', self.api)

    def test_no_execution_without_current_human_approval(self):
        self.api.messages[1]['user'] = 20
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')
        self.assertFalse(list((self.queue / 'incoming').iterdir()))

    def test_agent_relay_does_not_impersonate_personal_approval(self):
        self.api.messages[1]['message'] += ' AI authorship: Codex, relaying earlier instructions.'
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')
        self.assertFalse(list((self.queue / 'incoming').iterdir()))

    def test_route_readiness_is_visible_and_blocks_dispatch(self):
        self.bridge.config['tasks']['123']['ready'] = False
        state = self.bridge.status(123)
        self.assertFalse(state['ready'])
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')
        self.assertFalse(list((self.queue / 'incoming').iterdir()))

    def test_stale_plan_is_rejected(self):
        self.api.messages.append({'id': 'newplan', 'user': 20, 'created': 3,
                                  'message': 'TED PLAN v2 — AWAITING APPROVAL. Saved-context review-only.'})
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')

    def test_unregistered_task_and_wrong_project_are_rejected(self):
        with self.assertRaises(ValueError):
            self.bridge.submit(999, 'plan', 'approve')
        self.api.task['project']['id'] = 11
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')

    def test_submission_is_idempotent_and_binds_approval(self):
        first = self.bridge.submit(123, 'plan', 'approve')
        self.assertEqual(first, self.bridge.submit(123, 'plan', 'approve'))
        self.assertEqual(len(list((self.queue / 'incoming').iterdir())), 1)
        self.api.messages[1]['message'] += ' Modified scope.'
        with self.assertRaises(ValueError):
            self.bridge.submit(123, 'plan', 'approve')

    def completed_run(self):
        state = self.bridge.submit(123, 'plan', 'approve')
        request = json.loads((self.queue / 'incoming' / (state['request_id'] + '.json')).read_text())
        run = self.queue / 'runs' / state['request_id']
        run.mkdir()
        (run / 'receipt.json').write_text(json.dumps({'request_id': state['request_id'],
            'status': 'needs_review', 'thread_id': 'native-session', 'basicops': request['basicops']}))
        (run / 'result.md').write_text('Saved evidence needs a fresh read-only measurement check.')
        return run

    def test_handback_updates_same_task_and_reads_back_without_duplicates(self):
        self.completed_run()
        result = self.bridge.reconcile_one(123)
        self.assertTrue(result['notification']['verified'])
        self.assertEqual(self.api.task['status'], 'Under Review')
        self.assertEqual(self.api.task['assignee']['id'], 30)
        count = len(self.api.writes)
        self.bridge.reconcile_one(123)
        self.assertEqual(len(self.api.writes), count)
        self.assertNotIn('Complete', [args.get('status') for _, args in self.api.writes])

    def test_tampered_receipt_cannot_post_a_handback(self):
        run = self.completed_run()
        receipt = json.loads((run / 'receipt.json').read_text())
        receipt['basicops']['task_id'] = 999
        (run / 'receipt.json').write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            self.bridge.reconcile_one(123)
        self.assertFalse(self.api.writes)

    def test_reply_author_identity_and_uncertain_review_request(self):
        self.assertEqual(module.actor({'userId': 30}), 30)
        self.completed_run()
        original = self.bridge.api
        def uncertain(name, args):
            if name == 'request_review':
                raise TimeoutError('ambiguous remote outcome')
            return original(name, args)
        self.bridge.api = uncertain
        with self.assertRaises(TimeoutError):
            self.bridge.reconcile_one(123)
        self.bridge.api = original
        count = len(self.api.writes)
        with self.assertRaises(ValueError):
            self.bridge.reconcile_one(123)
        self.assertEqual(len(self.api.writes), count)

    def test_rejected_queue_request_returns_visible_blocker(self):
        state = self.bridge.submit(123, 'plan', 'approve')
        failed = self.queue / 'failed'
        failed.mkdir()
        (failed / (state['request_id'] + '.json.error.json')).write_text(
            json.dumps({'reason': 'Invalid task envelope'}))
        result = self.bridge.reconcile_one(123)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(self.api.task['status'], 'Blocked')
        self.assertEqual(self.api.task['assignee']['id'], 30)
        self.assertFalse(any(name == 'request_review' for name, _ in self.api.writes))

    def test_new_owner_is_preserved(self):
        self.completed_run()
        self.api.task['assignee'] = {'id': 999}
        with self.assertRaises(ValueError):
            self.bridge.reconcile_one(123)
        self.assertFalse(self.api.writes)


if __name__ == '__main__':
    unittest.main()
