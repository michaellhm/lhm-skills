"""Transport, saved-session and failure-boundary acceptance without live inference."""
import importlib.util
import contextlib
import hashlib
import io
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ASSETS = Path(__file__).resolve().parents[1] / 'assets/calendar-sales-handover'


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ASSETS / file)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


W = module('watcher', 'watcher.py')
R = module('calendar_handover_runtime', 'runtime.py')
C = module('calendar_handover_calendar_read', 'calendar_read.py')
B = module('calendar_handover_codex_worker', 'codex_worker.py')
THREAD = '01a16759-a875-7d41-8a19-f8f49025000b'
HOST = 'remote-control:env_test'


class CalendarAdapterAcceptance(unittest.TestCase):
    def test_fully_paginates_and_strips_meeting_secrets(self):
        api = Mock()
        api.events.return_value.list.return_value.execute.side_effect = [
            {'items': [{'id': 'a', 'summary': 'Onboarding', 'location': 'password',
                        'description': 'private notes', 'organizer': {'email': 'partner@example.com'}}],
             'nextPageToken': 'page2'},
            {'items': [{'id': 'b'}]},
        ]
        google = SimpleNamespace(build_service=Mock(return_value=api))
        with patch.dict(sys.modules, {'google_api': google}):
            result = C.execute({'action': 'list', 'calendar_id': 'primary',
                                'start': '2026-11-16T00:00:00Z', 'end': '2026-11-17T00:00:00Z'})
        self.assertTrue(result['pagination_complete'])
        self.assertEqual([e['id'] for e in result['events']], ['a', 'b'])
        self.assertNotIn('description', result['events'][0])
        self.assertNotIn('location', result['events'][0])
        self.assertEqual(api.events.return_value.list.call_args_list[1].kwargs['pageToken'], 'page2')

    def test_pagination_failure_never_returns_partial_success(self):
        api = Mock()
        api.events.return_value.list.return_value.execute.side_effect = [
            {'items': [{'id': 'a'}], 'nextPageToken': 'page2'}, RuntimeError('sensitive API failure')]
        with patch.dict(sys.modules, {'google_api': SimpleNamespace(build_service=lambda *a: api)}):
            with self.assertRaises(RuntimeError):
                C.execute({'action': 'list', 'calendar_id': 'primary', 'start': 'a', 'end': 'b'})

    def test_host_rejects_unproven_pagination_and_redacts_adapter_error(self):
        with patch.object(R, 'container_read', return_value={'events': [], 'pagination_complete': False}):
            with self.assertRaises(RuntimeError):
                R.Calendar('primary').list_events('a', 'b')
        with patch.object(R.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='secret', stderr='token')):
            with self.assertRaisesRegex(RuntimeError, '^Hermes read adapter failed: calendar_read.py$'):
                R.container_read('calendar_read.py', {})


class DispatchAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        self.key = 'a' * 64
        self.run = self.state / 'worker-runs' / self.key
        self.run.mkdir(parents=True)
        (self.state / 'launches').mkdir()
        self.patcher = patch.object(R, 'STATE', self.state)
        self.patcher.start(); self.addCleanup(self.patcher.stop)
        self.dispatch = R.Dispatcher({'codex_host_id': HOST})

    def test_existing_native_session_recovered_without_any_launch(self):
        (self.run / 'session.json').write_text(json.dumps({'thread_id': THREAD}))
        with patch.object(R, 'container_read') as fetch, patch.object(R.subprocess, 'run') as launch:
            result = self.dispatch({'dispatch_key': self.key, 'reconcile_only': True})
        self.assertEqual(result['thread_id'], THREAD)
        self.assertIn('hostId=remote-control%3Aenv_test', result['chat_url'])
        fetch.assert_not_called(); launch.assert_not_called()

    def test_unknown_launch_is_not_replayed(self):
        (self.state / 'launches' / (self.key + '.json')).write_text('{}')
        with patch.object(R.subprocess, 'run') as launch, patch.object(R, 'container_read') as fetch:
            with self.assertRaisesRegex(RuntimeError, 'reconcile original'):
                self.dispatch({'dispatch_key': self.key})
        launch.assert_not_called(); fetch.assert_not_called()

    def test_reconcile_only_without_record_cannot_create_another_chat(self):
        with patch.object(R.subprocess, 'run') as launch:
            with self.assertRaises(RuntimeError):
                self.dispatch({'dispatch_key': self.key, 'reconcile_only': True})
        launch.assert_not_called()

    def test_transcript_not_ready_is_a_retryable_prelaunch_state(self):
        with patch.object(R, 'visible_host_ready', return_value=True), \
                patch.object(R, 'fathom_read', return_value={'status': 'not_ready'}), \
                patch.object(R.subprocess, 'run') as launch:
            for expected in (1, 2):
                with self.assertRaises(W.DispatchNotStarted):
                    self.dispatch({'dispatch_key': self.key})
                self.assertEqual(json.loads((self.run / 'meeting-evidence.json').read_text())['attempt'], expected)
        self.assertFalse((self.state / 'launches' / (self.key + '.json')).exists())
        launch.assert_not_called()

    def test_disconnected_host_waits_without_creating_a_chat(self):
        with patch.object(R, 'visible_host_ready', return_value=False), \
                patch.object(R, 'fathom_read') as fetch, patch.object(R, 'start_worker') as launch:
            with self.assertRaises(W.DispatchNotStarted):
                self.dispatch({'dispatch_key': self.key})
        fetch.assert_not_called(); launch.assert_not_called()
        self.assertFalse((self.state / 'launches' / (self.key + '.json')).exists())

    def test_connection_check_never_spawns_an_unmanaged_daemon(self):
        with patch.object(R, 'daemon_owned_by_host_unit', return_value=False), \
                patch.object(R.subprocess, 'run') as command:
            self.assertFalse(R.visible_host_ready())
        command.assert_not_called()

    def test_connection_check_requires_daemon_to_remain_in_its_service(self):
        from types import SimpleNamespace
        responses = [SimpleNamespace(returncode=0, stdout='{"status":"running","backend":"pid"}'),
                     SimpleNamespace(returncode=0, stdout='{}')]
        with patch.object(R, 'daemon_owned_by_host_unit', side_effect=[True, False]), \
                patch.object(R.subprocess, 'run', side_effect=responses):
            self.assertFalse(R.visible_host_ready())

    def test_untrusted_session_symlink_is_not_followed_by_root(self):
        target = self.state / 'elsewhere.json'
        target.write_text(json.dumps({'thread_id': THREAD}))
        (self.run / 'session.json').symlink_to(target)
        with self.assertRaises(OSError):
            self.dispatch({'dispatch_key': self.key})


class NativeWorkerAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = Path(self.temp.name)
        self.skill = self.run / 'skills/sales-handover/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('Reviewed skill content')
        (self.run / 'event-context.json').write_text(json.dumps({'codex_host_id': HOST, 'summary': 'Onboarding test'}))

    def test_existing_starting_receipt_is_never_replayed(self):
        B.atomic(self.run / 'worker-receipt.json', {'status': 'starting'})
        with patch.object(B.importlib.util, 'spec_from_file_location') as helper:
            result = B.execute(self.run)
        self.assertEqual(result['status'], 'starting'); helper.assert_not_called()

    def test_existing_saved_chat_becomes_attention_not_a_new_turn(self):
        B.atomic(self.run / 'session.json', {'thread_id': THREAD})
        with patch.object(B.importlib.util, 'spec_from_file_location') as helper:
            first = B.execute(self.run); second = B.execute(self.run)
        self.assertEqual(first['thread_id'], THREAD)
        self.assertEqual(second['thread_id'], THREAD)
        self.assertEqual(first['status'], 'needs_attention'); helper.assert_not_called()

    def test_review_ready_requires_real_draft_and_matching_saved_session(self):
        def produce(task, prompt, run, **kwargs):
            self.assertTrue(kwargs['read_only_integrations'])
            self.assertEqual(kwargs['cwd'], self.run.resolve())
            self.assertIn('Do not send or', prompt)
            B.atomic(run / 'session.json', {'thread_id': THREAD})
            (run / 'drafts/internal-handover-email.md').write_text('To: internal@example.com\nSubject: Test\nDraft for review')
            (run / 'result.md').write_text('Prepared for review')
            return THREAD
        native = SimpleNamespace(conversation=Mock(side_effect=produce))
        fake_file = Mock()
        fake_file.lstat.return_value = SimpleNamespace(st_mode=stat.S_IFREG, st_uid=0)
        spec = SimpleNamespace(loader=Mock())
        with patch.object(B, 'NATIVE_HELPER', fake_file), \
                patch.object(B.importlib.util, 'spec_from_file_location', return_value=spec), \
                patch.object(B.importlib.util, 'module_from_spec', return_value=native):
            result = B.execute(self.run)
        self.assertEqual(result['status'], 'ready_for_review')
        self.assertEqual(result['thread_id'], THREAD)
        self.assertEqual(B.execute(self.run)['thread_id'], THREAD)
        native.conversation.assert_called_once()

    def test_source_skill_hash_mismatch_stops_before_native_launch(self):
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            B.prompt_for({'skill_sha256': '0' * 64}, self.run)


class TestRunAcceptance(unittest.TestCase):
    def test_explicit_test_has_separate_launch_key_and_status_worker_receipt(self):
        cfg = {'calendar_id': 'primary', 'calendar_identity': 'operator@example.com',
               'organizer_emails': ['partner@example.com'], 'enabled_from': '2026-11-16T00:00:00Z',
               'codex_host_id': HOST}
        current = datetime.now(timezone.utc)
        event = {'id': 'old-instance', 'status': 'confirmed', 'summary': 'Website Onboarding',
                 'start': {'dateTime': (current - timedelta(hours=3)).isoformat()},
                 'end': {'dateTime': (current - timedelta(hours=2)).isoformat()},
                 'organizer': {'email': 'partner@example.com'},
                 'attendees': [{'email': 'operator@example.com', 'self': True}]}
        captured = []
        class Calendar:
            def __init__(self, calendar_id): pass
            def identity(self): return 'operator@example.com'
            def get_event(self, event_id): return event
            def list_events(self, start, end): return []
        def dispatch(payload):
            captured.append(payload)
            return {'thread_id': THREAD, 'chat_url': 'codex://threads/' + THREAD}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(R, 'STATE', root), patch.object(R, 'Calendar', Calendar), \
                    patch.object(R, 'load_config', return_value=cfg), \
                    patch.object(R.os, 'geteuid', return_value=0), \
                    patch.object(R, 'Dispatcher', return_value=dispatch), \
                    patch.object(sys, 'argv', ['runtime.py', 'test', '--event-id', 'old-instance']), \
                    contextlib.redirect_stdout(io.StringIO()):
                R.main()
            self.assertEqual(len(captured), 1)
            base = W.event_key(event, W.Config.from_dict(cfg))
            expected = hashlib.sha256(('test:' + base).encode()).hexdigest()
            self.assertEqual(captured[0]['dispatch_key'], expected)
            self.assertTrue(captured[0]['test_mode'])
            work = root / 'worker-runs' / expected
            work.mkdir(parents=True)
            (work / 'worker-receipt.json').write_text(json.dumps({'status': 'ready_for_review'}))
            output = io.StringIO()
            with patch.object(R, 'STATE', root), patch.object(R, 'Calendar', Calendar), \
                    patch.object(R, 'load_config', return_value=cfg), \
                    patch.object(R.os, 'geteuid', return_value=0), \
                    patch.object(R, 'Dispatcher', return_value=dispatch), \
                    patch.object(sys, 'argv', ['runtime.py', 'status']), contextlib.redirect_stdout(output):
                R.main()
            result = json.loads(output.getvalue())
            self.assertEqual(result['events'][0]['worker']['status'], 'ready_for_review')
            self.assertTrue(result['events'][0]['test_mode'])


if __name__ == '__main__':
    unittest.main()
