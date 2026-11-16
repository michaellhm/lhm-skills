"""Explicit operator recovery stays in the original native Codex conversation."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / 'assets/calendar-sales-handover/codex_worker.py'
SPEC = importlib.util.spec_from_file_location('calendar_recovery_worker', SOURCE)
W = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(W)
THREAD = '01a16759-a875-7d41-8a19-f8f49025000b'
HOST = 'remote-control:env_test'


class RecoveryAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.skill = self.run / 'skills/sales-handover/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('Exact reviewed skill')
        self.packet = {'codex_host_id': HOST, 'summary': 'Onboarding test',
                       'skill_sha256': hashlib.sha256(self.skill.read_bytes()).hexdigest()}
        W.atomic(self.run / 'event-context.json', self.packet)
        W.atomic(self.run / 'session.json', {'thread_id': THREAD})
        self.prior = {'status': 'needs_attention', 'initial_turn_status': 'failed',
                      'error_kind': 'authentication_required', 'thread_id': THREAD}
        W.atomic(self.run / 'worker-receipt.json', self.prior)

    @contextlib.contextmanager
    def native(self, callback):
        native = SimpleNamespace(conversation=Mock(side_effect=callback))
        helper = Mock()
        helper.lstat.return_value = SimpleNamespace(st_mode=stat.S_IFREG, st_uid=0)
        spec = SimpleNamespace(loader=Mock())
        with patch.object(W, 'NATIVE_HELPER', helper), \
                patch.object(W.importlib.util, 'spec_from_file_location', return_value=spec), \
                patch.object(W.importlib.util, 'module_from_spec', return_value=native):
            yield native

    def produce(self, task, prompt, run, **kwargs):
        self.assertEqual(task['task_type'], 'feedback')
        self.assertEqual(task['resume_thread_id'], THREAD)
        self.assertIn('Invoke the reviewed lhm-project-hub:sales-handover', prompt)
        self.assertIn('Stop for Michael', prompt)
        self.assertTrue(kwargs['read_only_integrations'])
        (run / 'drafts/internal-handover-email.md').write_text('To: team@example.com\nDraft')
        (run / 'result.md').write_text('Prepared for review')
        return THREAD

    def test_operator_resume_uses_same_chat_and_retains_private_receipt_history(self):
        with self.native(self.produce) as native:
            result = W.execute(self.run, resume=True)
        self.assertEqual(result['status'], 'ready_for_review')
        self.assertEqual(result['thread_id'], THREAD)
        self.assertEqual(result['attempt'], 2)
        self.assertEqual(result['resume_thread_id'], THREAD)
        native.conversation.assert_called_once()
        history = list((self.run / 'worker-history').glob('*-receipt.json'))
        self.assertEqual(len(history), 1)
        self.assertEqual(json.loads(history[0].read_text()), self.prior)
        self.assertEqual(stat.S_IMODE(history[0].stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(history[0].parent.stat().st_mode), 0o700)

    def test_ordinary_retry_never_invokes_model_even_after_auth_repaired(self):
        with self.native(self.produce) as native:
            result = W.execute(self.run)
        native.conversation.assert_not_called()
        self.assertEqual(result['status'], 'needs_attention')
        self.assertFalse((self.run / 'worker-history').exists())

    def test_explicit_resume_refuses_starting_ready_and_completed(self):
        for status in ['starting', 'ready_for_review', 'completed']:
            with self.subTest(status=status):
                W.atomic(self.run / 'worker-receipt.json', {'status': status})
                with self.native(self.produce) as native:
                    with self.assertRaisesRegex(ValueError, 'needs_attention'):
                        W.execute(self.run, resume=True)
                native.conversation.assert_not_called()

    def test_resume_requires_verified_uuid_and_matching_receipt(self):
        W.atomic(self.run / 'session.json', {'thread_id': 'not-a-uuid'})
        with self.native(self.produce) as native:
            with self.assertRaises(ValueError):
                W.execute(self.run, resume=True)
        native.conversation.assert_not_called()
        W.atomic(self.run / 'session.json', {'thread_id': '01a16759-a875-7d41-8a19-f8f49025000c'})
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            W.execute(self.run, resume=True)

    def test_skill_hash_mismatch_stops_before_receipt_or_native_changes(self):
        before = (self.run / 'worker-receipt.json').read_bytes()
        self.skill.write_text('Changed skill')
        with self.native(self.produce) as native:
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                W.execute(self.run, resume=True)
        native.conversation.assert_not_called()
        self.assertEqual((self.run / 'worker-receipt.json').read_bytes(), before)
        self.assertFalse((self.run / 'worker-history').exists())

    def test_failed_auth_resume_retains_same_thread_and_only_safe_error_kind(self):
        def fail(task, prompt, run, **kwargs):
            self.assertEqual(task['task_type'], 'feedback')
            self.assertEqual(task['resume_thread_id'], THREAD)
            (run / 'events.jsonl').write_text(json.dumps({'method': 'error', 'params': {'error': {'codexErrorInfo': 'unauthorized', 'message': 'raw token=never-copy'}}}) + '\n')
            raise ValueError('raw token=never-copy')
        with self.native(fail) as native:
            result = W.execute(self.run, resume=True)
        self.assertEqual(result['status'], 'needs_attention')
        self.assertEqual(result['thread_id'], THREAD)
        self.assertEqual(result['error_kind'], 'authentication_required')
        self.assertNotIn('never-copy', json.dumps(result))
        with self.native(self.produce) as automatic:
            W.execute(self.run)
        automatic.conversation.assert_not_called()

    def test_error_classifier_uses_bounded_allowlisted_native_enum(self):
        path = self.run / 'events.jsonl'
        path.write_text(json.dumps({'method': 'error', 'params': {'error': {'codexErrorInfo': 'unauthorized'}}}) + '\n' + ('x' * 70000))
        self.assertEqual(W.failure_kind(self.run), 'bootstrap_failed')
        path.write_text(json.dumps({'method': 'turn/completed', 'params': {'turn': {'error': {'codexErrorInfo': 'unauthorized'}}}}) + '\n')
        self.assertEqual(W.failure_kind(self.run), 'authentication_required')
        path.write_text(json.dumps({'method': 'error', 'params': {'error': {'message': 'unauthorized', 'codexErrorInfo': 'other'}}}) + '\n')
        self.assertEqual(W.failure_kind(self.run), 'bootstrap_failed')


if __name__ == '__main__':
    unittest.main()
