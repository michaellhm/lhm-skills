import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'assets/host/lhm-work-resumer'
spec = importlib.util.spec_from_loader('work_resumer', SourceFileLoader('work_resumer', str(SCRIPT)))
resumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resumer)
PRODUCER_SCRIPT = ROOT / 'assets/host/lhm-source-production-runtime'
producer_spec = importlib.util.spec_from_loader('source_producer', SourceFileLoader('source_producer', str(PRODUCER_SCRIPT)))
source_producer = importlib.util.module_from_spec(producer_spec)
producer_spec.loader.exec_module(source_producer)


class WorkResumerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        for name in ('INCOMING', 'CLAIMS', 'PARENTS', 'PROCESSED', 'FAILED', 'CONSUMED',
                     'AGENT_CONSUMED', 'RECONCILIATIONS', 'HANDOFFS'):
            path = base / name.lower()
            setattr(resumer, name, path)
            path.mkdir()
        blocker = {
            'capability_incident_id': 'release-publishing-resume-permissions-20260820',
            'parent_run_id': 'RELEASE-PUBLISHING-ENGINEER-20260820',
            'saved_role': 'Release & Publishing Engineer', 'return_point': 'desktop control',
        }
        self.event = source_producer.capability_restored_event(
            blocker, 'release-publishing-engineer-installed-20260820',
            '2026-08-20T00:00:00+00:00')
        self.parent = {
            'schema_version': 1, 'parent_run_id': self.event['parent_run_id'],
            'capability_incident_id': self.event['capability_incident_id'],
            'status': 'waiting_on_capability', 'private_context': 'bounded parent content',
        }
        self.event_path = resumer.INCOMING / 'event.json'
        self.parent_path = resumer.PARENTS / f"{self.event['parent_run_id']}.json"
        self.event_path.write_text(json.dumps(self.event))
        self.parent_path.write_text(json.dumps(self.parent))

    def tearDown(self):
        self.temp.cleanup()

    def record(self, status='continued', transitioned=True):
        return {
            'schema_version': 1, 'event_id': self.event['event_id'],
            'parent_run_id': self.event['parent_run_id'],
            'parent_sha256': resumer.digest(self.parent), 'transitioned': transitioned,
            'next_status': status, 'evidence': ['saved role resumed at desktop control'],
        }

    def runner(self, record=None, returncode=0, stdout=''):
        value = record
        def run(handoff):
            if value is not None:
                (handoff / 'response' / 'agent-consumed.json').write_text(json.dumps(value))
            return SimpleNamespace(returncode=returncode, stdout=stdout, stderr='')
        return run

    def test_real_producer_contract_bounded_handoff_and_success(self):
        """Exercise the production capability_restored schema and real resumer contract."""
        observed = {}
        def designated_hermes(handoff):
            observed['event'] = json.loads((handoff / 'event.json').read_text())
            observed['parent'] = json.loads((handoff / 'parent.json').read_text())
            observed['files'] = sorted(str(p.relative_to(handoff)) for p in handoff.rglob('*'))
            (handoff / 'response' / 'agent-consumed.json').write_text(json.dumps(self.record()))
            return SimpleNamespace(returncode=0, stdout='transitioned', stderr='')

        with mock.patch.object(resumer.os, 'chown') as chown:
            self.assertEqual(resumer.process(self.event_path, designated_hermes), 'consumed')
        self.assertEqual(observed['event'], self.event)
        self.assertEqual(observed['parent'], self.parent)
        self.assertEqual(observed['files'], ['event.json', 'parent.json', 'response'])
        self.assertTrue(all(call.args[1:] == (10000, 10000) for call in chown.call_args_list))
        updated = json.loads(self.parent_path.read_text())
        self.assertEqual(updated['status'], 'continued')
        self.assertEqual(updated['resume_event_id'], self.event['event_id'])
        key = hashlib.sha256(self.event['event_id'].encode()).hexdigest()
        self.assertEqual(json.loads((resumer.CONSUMED / f'{key}.json').read_text())['event_id'], self.event['event_id'])
        self.assertTrue((resumer.AGENT_CONSUMED / f'{key}.json').is_file())

    def test_worker_has_no_unrelated_store_access(self):
        unrelated_paths = [
            resumer.PARENTS / 'UNRELATED.json', resumer.CLAIMS / 'UNRELATED.json',
            Path(self.temp.name) / 'credentials.json',
        ]
        for unrelated in unrelated_paths:
            unrelated.write_text('{"private":"not exposed"}')
            unrelated.chmod(0)
        with mock.patch.object(resumer.os, 'chown'):
            handoff = resumer.make_handoff(self.event, self.parent)
        self.assertEqual(stat.S_IMODE(handoff.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((handoff / 'event.json').stat().st_mode), 0o400)
        self.assertEqual(stat.S_IMODE((handoff / 'parent.json').stat().st_mode), 0o400)
        self.assertFalse((handoff / 'UNRELATED.json').exists())
        for unrelated in unrelated_paths:
            probe = subprocess.run(['sh', '-c', 'test -r "$1"', 'probe', str(unrelated)])
            self.assertNotEqual(probe.returncode, 0)

    def test_parent_path_traversal_and_symlink_fail_closed(self):
        traversal = dict(self.event)
        traversal['parent_run_id'] = '../../outside'
        self.event_path.write_text(json.dumps(traversal))
        self.assertEqual(resumer.process(self.event_path, self.runner(self.record())), 'failed')
        replay = resumer.INCOMING / 'symlink.json'
        replay.write_text(json.dumps(self.event))
        self.parent_path.unlink()
        self.parent_path.symlink_to(Path(self.temp.name) / 'outside-parent.json')
        (Path(self.temp.name) / 'outside-parent.json').write_text(json.dumps(self.parent))
        self.assertEqual(resumer.process(replay, self.runner(self.record())), 'failed')

    def test_exit_zero_refusal_without_record_fails_without_success_marker(self):
        with mock.patch.object(resumer.os, 'chown'):
            outcome = resumer.process(self.event_path, self.runner(None, 0, 'refused: unreadable'))
        self.assertEqual(outcome, 'failed')
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'waiting_on_capability')
        self.assertEqual(list(resumer.CONSUMED.iterdir()), [])
        self.assertEqual(list(resumer.AGENT_CONSUMED.iterdir()), [])

    def test_exit_zero_not_transitioned_fails_without_success_marker(self):
        with mock.patch.object(resumer.os, 'chown'):
            outcome = resumer.process(self.event_path, self.runner(self.record(transitioned=False)))
        self.assertEqual(outcome, 'failed')
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'waiting_on_capability')
        self.assertEqual(list(resumer.CONSUMED.iterdir()), [])

    def test_missing_event_id_fails_closed(self):
        broken = dict(self.event)
        del broken['event_id']
        self.event_path.write_text(json.dumps(broken))
        self.assertEqual(resumer.process(self.event_path, self.runner(self.record())), 'failed')
        self.assertEqual(list(resumer.CONSUMED.iterdir()), [])

    def test_explicit_wait_requires_evidence_and_is_successful(self):
        record = self.record('waiting_on_evidence')
        record['evidence'] = ['Chief must supply authoritative branch-protection readback']
        with mock.patch.object(resumer.os, 'chown'):
            self.assertEqual(resumer.process(self.event_path, self.runner(record)), 'consumed')
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'waiting_on_evidence')

    def test_false_marker_reconciliation_preserves_audit_and_is_idempotent(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        key = hashlib.sha256(self.event['event_id'].encode()).hexdigest()
        marker = resumer.CONSUMED / f'{key}.json'
        marker.write_text(json.dumps({'event_id': self.event['event_id'], 'legacy': True}))
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'requeued')
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'already_requeued')
        self.assertFalse(marker.exists())
        self.assertTrue((resumer.RECONCILIATIONS / f'{key}.false-marker.json').is_file())
        audit = json.loads((resumer.RECONCILIATIONS / f'{key}.json').read_text())
        self.assertEqual(audit['action'], 'requeued')
        self.assertTrue((resumer.INCOMING / processed.name).is_file())

    def test_completed_event_is_idempotent_without_second_agent_invocation(self):
        with mock.patch.object(resumer.os, 'chown'):
            self.assertEqual(resumer.process(self.event_path, self.runner(self.record())), 'consumed')
        replay = resumer.INCOMING / 'replay.json'
        replay.write_text(json.dumps(self.event))
        calls = []
        self.assertEqual(resumer.process(replay, lambda *_: calls.append(1)), 'duplicate')
        self.assertEqual(calls, [])

    def test_durable_agent_record_recovers_interrupted_parent_apply_without_reinvocation(self):
        key = hashlib.sha256(self.event['event_id'].encode()).hexdigest()
        (resumer.AGENT_CONSUMED / f'{key}.json').write_text(json.dumps(self.record()))
        calls = []
        self.assertEqual(resumer.process(self.event_path, lambda *_: calls.append(1)), 'consumed')
        self.assertEqual(calls, [])
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'continued')

    def test_interrupted_false_marker_audit_finalisation_recovers_idempotently(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        key = hashlib.sha256(self.event['event_id'].encode()).hexdigest()
        marker = resumer.CONSUMED / f'{key}.json'
        marker.write_text(json.dumps({'event_id': self.event['event_id'], 'legacy': True}))
        (resumer.INCOMING / processed.name).write_text(processed.read_text())
        os.replace(marker, resumer.RECONCILIATIONS / f'{key}.false-marker.json')
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'recovered_reconciliation')
        self.assertTrue((resumer.RECONCILIATIONS / f'{key}.json').is_file())

    def test_interrupted_success_marker_write_recovers_without_agent_reinvocation(self):
        key = hashlib.sha256(self.event['event_id'].encode()).hexdigest()
        record = self.record()
        (resumer.AGENT_CONSUMED / f'{key}.json').write_text(json.dumps(record))
        transitioned = {**self.parent, 'status': record['next_status'],
                        'resume_event_id': self.event['event_id'],
                        'resume_evidence': record['evidence'], 'updated_at': '2026-08-20T01:00:00+00:00'}
        self.parent_path.write_text(json.dumps(transitioned))
        calls = []
        self.assertEqual(resumer.process(self.event_path, lambda *_: calls.append(1)), 'recovered')
        self.assertEqual(calls, [])
        self.assertTrue((resumer.CONSUMED / f'{key}.json').is_file())


if __name__ == '__main__':
    unittest.main()
