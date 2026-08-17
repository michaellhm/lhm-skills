import hashlib
import importlib.util
import json
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
RESUMER = ROOT / 'assets/host/lhm-cto-result-resumer'
spec = importlib.util.spec_from_loader('result_resumer', SourceFileLoader('result_resumer', str(RESUMER)))
result_resumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(result_resumer)


class ResultResumerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        result_resumer.BASE = base
        result_resumer.INCOMING = base / 'callback-incoming'
        result_resumer.CLAIMS = base / 'callback-claims'
        result_resumer.PROCESSED = base / 'callback-processed'
        result_resumer.FAILED = base / 'callback-failed'
        result_resumer.CONSUMED = base / 'callback-consumed'
        result_resumer.RUNS = base / 'runs'
        result_resumer.REQUESTS = base / 'processed'
        for directory in (
            result_resumer.INCOMING, result_resumer.CLAIMS, result_resumer.PROCESSED,
            result_resumer.FAILED, result_resumer.CONSUMED, result_resumer.RUNS,
            result_resumer.REQUESTS,
        ):
            directory.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def make_callback(self, request_id='request-001'):
        request = {
            'schema_version': 1, 'request_id': request_id, 'parent_run_id': 'parent-001',
            'capability_incident_id': 'incident-001', 'objective': 'Research safely',
            'acceptance_tests': ['Return evidence'], 'mode': 'research',
            'timeout_seconds': 600, 'return_point': 'Return to Chief',
            'resume_token': 'resume-token-0001',
        }
        (result_resumer.REQUESTS / f'{request_id}.json').write_text(json.dumps(request))
        run = result_resumer.RUNS / request_id
        run.mkdir()
        final = run / 'final.json'
        final.write_text(json.dumps({'status': 'needs_evidence', 'questions_for_chief': ['Read canonical profile']}))
        event = {
            'schema_version': 1, 'event': 'cto_result_ready',
            'event_id': f'{request_id}:result', 'request_id': request_id,
            'parent_run_id': 'parent-001', 'capability_incident_id': 'incident-001',
            'return_point': 'Return to Chief', 'resume_token': 'resume-token-0001',
            'iteration': 1, 'max_iterations': 3,
            'result_sha256': hashlib.sha256(final.read_bytes()).hexdigest(),
            'created_at': '2026-08-17T00:00:00+00:00',
        }
        incoming = result_resumer.INCOMING / f'{request_id}.json'
        incoming.write_text(json.dumps(event))
        return incoming, event

    def test_valid_callback_invokes_chief_once_and_is_consumed(self):
        incoming, event = self.make_callback()
        calls = []

        def runner(*args):
            calls.append(args)
            return SimpleNamespace(returncode=0, stdout='Chief submitted iteration two', stderr='')

        self.assertEqual(result_resumer.process(incoming, runner), 'consumed')
        self.assertEqual(len(calls), 1)
        key = hashlib.sha256(f"{event['event_id']}\0{event['result_sha256']}".encode()).hexdigest()
        self.assertTrue((result_resumer.CONSUMED / f'{key}.json').is_file())

    def test_digest_mismatch_fails_closed(self):
        incoming, _ = self.make_callback('request-002')
        event = json.loads(incoming.read_text())
        event['result_sha256'] = '0' * 64
        incoming.write_text(json.dumps(event))
        self.assertEqual(result_resumer.process(incoming, lambda *_: None), 'failed')
        self.assertIn('digest mismatch', (result_resumer.FAILED / 'request-002.error').read_text())


if __name__ == '__main__':
    unittest.main()
