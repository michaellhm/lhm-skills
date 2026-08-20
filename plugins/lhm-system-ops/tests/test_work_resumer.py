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
DEPLOYMENT = ROOT / 'references/work-control-deployment.json'
PATH_UNIT = ROOT / 'assets/systemd/lhm-work-resumer.path'
SERVICE_UNIT = ROOT / 'assets/systemd/lhm-work-resumer.service'
spec = importlib.util.spec_from_loader('work_resumer', SourceFileLoader('work_resumer', str(SCRIPT)))
resumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resumer)
validator_spec = importlib.util.spec_from_file_location(
    'validate_system_ops', ROOT / 'scripts/validate_system_ops.py')
validator = importlib.util.module_from_spec(validator_spec)
validator_spec.loader.exec_module(validator)
INSTALLED_BASE = resumer.BASE
INSTALLED_INCOMING = resumer.INCOMING
INSTALLED_HANDOFFS = resumer.HANDOFFS
INSTALLED_HERMES_HANDOFFS = resumer.HERMES_HANDOFFS
class WorkResumerIntegrationTests(unittest.TestCase):
    def test_installed_producer_watcher_consumer_and_bind_mapping_are_one_store(self):
        deployment = json.loads(DEPLOYMENT.read_text())
        path_unit = PATH_UNIT.read_text()
        service_unit = SERVICE_UNIT.read_text()
        container_profile = '/opt/data/profiles/lhm_brain'
        host_profile = '/home/hermes/.hermes/profiles/lhm_brain'

        self.assertEqual(deployment['producer_executable_container'],
                         f'{container_profile}/bin/work-control')
        self.assertEqual(deployment['producer_store_container'],
                         f'{container_profile}/dispatch/work-control')
        self.assertEqual(deployment['store_host'],
                         deployment['producer_store_container'].replace(container_profile, host_profile, 1))
        self.assertEqual(INSTALLED_BASE, Path(deployment['store_host']))
        producer_name = validator.producer_incoming_name(
            deployment['producer_restore_path_expression'])
        self.assertEqual(producer_name, 'incoming')
        self.assertEqual(INSTALLED_INCOMING, Path(deployment['store_host']) / producer_name)
        self.assertEqual(deployment['watch_glob_host'], str(INSTALLED_INCOMING / '*.json'))
        self.assertIn(f"PathExistsGlob={deployment['watch_glob_host']}", path_unit)
        self.assertIn(f"ReadWritePaths={deployment['store_host']}", service_unit)
        self.assertEqual(deployment['handoff_host'], f"{deployment['store_host']}/handoffs")
        self.assertEqual(deployment['handoff_container'],
                         f"{deployment['producer_store_container']}/handoffs")
        self.assertEqual(INSTALLED_HANDOFFS, INSTALLED_BASE / 'handoffs')
        self.assertEqual(INSTALLED_HERMES_HANDOFFS, Path(deployment['handoff_container']))
        self.assertNotIn('/opt/run', SCRIPT.read_text() + json.dumps(deployment) + service_unit)
        self.assertNotIn('/var/lib/lhm-work-control', SCRIPT.read_text() + path_unit + service_unit)

    def test_deployment_parity_rejects_nonexistent_events_alternate(self):
        deployment = json.loads(DEPLOYMENT.read_text())
        deployment['watch_glob_host'] = f"{deployment['store_host']}/events/*.json"
        errors = validator.validate_work_control_parity(
            deployment, SCRIPT.read_text(),
            PATH_UNIT.read_text().replace('/incoming/*.json', '/events/*.json'))
        self.assertTrue(errors)
        self.assertTrue(any('producer restore path literal' in error for error in errors))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        for name in ('INCOMING', 'CLAIMS', 'PARENTS', 'PROCESSED', 'FAILED', 'CONSUMED',
                     'AGENT_CONSUMED', 'RECONCILIATIONS', 'HANDOFFS'):
            path = base / name.lower()
            setattr(resumer, name, path)
            path.mkdir()
        self.event = {"event_id":"release-publishing-engineer-installed-20260820","parent_run_id":"RELEASE-PUBLISHING-ENGINEER-20260820","capability_incident_id":"release-publishing-engineer-capability-20260820","return_role":"head_of_production","return_point":"desktop control; review CTO branch, merge and install only after exact approval","resume_token":"release-publishing-engineer-20260820-resume","evidence_refs":["https://github.com/michaellhm/lhm-skills/pull/18","merge:fb07cf96ae20289323ecb4790ee04913fa5a6a13","tests:83-passed-19-subtests","publisher-sha256:980301020ddc5125421437f9af18c81e02af95cfbbce0226ec756434029876d7","runtime-sha256:9b7766da09b7c276aea91b1af00fa1e46c576db2da373c1bb25a6afa8758e5ca"],"schema_version":1,"event":"capability_restored","timestamp":"2026-08-20T05:24:42.929856+00:00","idempotency_key":"ae2501bfb959119b7154e096f639c517d15f1551a6297d7625695b7563551648"}
        self.parent = {
            "parent_run_id":"RELEASE-PUBLISHING-ENGINEER-20260820","capability_incident_id":"release-publishing-engineer-capability-20260820","return_point":"desktop control; review CTO branch, merge and install only after exact approval","resume_token":"release-publishing-engineer-20260820-resume","objective":"Create a governed Release & Publishing Engineer under Head of Production. It must publish sealed, approved releases through destination-specific profiles, beginning with the existing lhm-prototype main-branch route, and later support separately approved Astro, WordPress API and hosting routes without universal credentials.","acceptance_test":"A reviewed feature branch registers the employee and prototype destination profile; repairs publisher preflight and post-push recovery; aligns capability-restored durable resume schemas; produces durable release receipts and canonical-state/BasicOps handoff contracts; passes independent security and regression QA without mutating any live site, repository, BasicOps task or credential.","permission_ceiling":"amber","schema_version":1,"status":"waiting_on_capability","updated_at":"2026-08-20T05:11:35.845440+00:00"
        }
        self.event_path = resumer.INCOMING / 'release-publishing-engineer-installed-20260820.json'
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

    def legacy_marker(self):
        return {"idempotency_key":"ae2501bfb959119b7154e096f639c517d15f1551a6297d7625695b7563551648","event_id":"release-publishing-engineer-installed-20260820","parent_run_id":"RELEASE-PUBLISHING-ENGINEER-20260820","consumed_at":"2026-08-20T05:28:56.519434+00:00","exit_code":0}

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
        key = self.event['idempotency_key']
        self.assertEqual(json.loads((resumer.CONSUMED / f'{key}.json').read_text())['event_id'], self.event['event_id'])
        self.assertTrue((resumer.AGENT_CONSUMED / f'{key}.json').is_file())
        self.assertFalse((resumer.HANDOFFS / key).exists())

    def test_authoritative_general_restore_digest_and_deployment_evidence(self):
        deployment = json.loads(DEPLOYMENT.read_text())
        byte_input = f"{self.event['parent_run_id']}\0{self.event['resume_token']}".encode()
        self.assertEqual(hashlib.sha256(byte_input).hexdigest(), self.event['idempotency_key'])
        self.assertEqual(resumer.marker_key(self.event), self.event['idempotency_key'])
        self.assertEqual(deployment['producer_executable_container'], '/opt/data/profiles/lhm_brain/bin/work-control')
        self.assertEqual(deployment['producer_executable_host'], '/home/hermes/.hermes/profiles/lhm_brain/bin/work-control')
        self.assertEqual(deployment['producer_sha256'], '7814ccfba1670b389764222b6d2bfa108b3bdd30af22f2f4a9b40f4a6d9cc35a')

    def test_live_cli_contract_uses_in_handoff_and_writes_exact_response(self):
        """A captured live argparse contract exercises the complete subprocess boundary."""
        handoff = resumer.HANDOFFS / self.event['idempotency_key']
        with mock.patch.object(resumer.os, 'chown'):
            handoff = resumer.make_handoff(self.event, self.parent)
        canonical_sibling = resumer.HANDOFFS.parent / 'parents-private-fixture.json'
        canonical_sibling.write_text('{"private":"canonical"}')
        canonical_sibling.chmod(0)
        fixture_bin = Path(self.temp.name) / 'bin'
        fixture_bin.mkdir()
        docker = fixture_bin / 'docker'
        docker.write_text('''#!/usr/bin/env python3
import argparse, json, os, pathlib, sys
argv = sys.argv[1:]
if argv[:2] != ["exec", "-u"] or argv[2] != "10000:10000" or argv[3] != "hermes":
    raise SystemExit("unexpected docker identity or container")
cli = argv[4:]
if not cli or cli.pop(0) != "/opt/hermes/.venv/bin/hermes":
    raise SystemExit("unexpected Hermes executable")
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--profile", required=True)
parser.add_argument("--in", dest="working_directory", required=True)
parser.add_argument("-z", "--oneshot", required=True)
args = parser.parse_args(cli)
expected = "/opt/data/profiles/lhm_brain/dispatch/work-control/handoffs/" + os.environ["EXPECTED_KEY"]
if args.profile != "lhm_brain" or args.working_directory != expected:
    raise SystemExit("wrong Hermes profile or container working directory")
handoff = pathlib.Path(os.environ["HOST_HANDOFF"])
os.chdir(handoff)
canonical_sibling = pathlib.Path(os.environ["HOST_CANONICAL_SIBLING"])
if canonical_sibling.is_file() and os.access(canonical_sibling, os.R_OK):
    raise SystemExit("canonical sibling state is readable")
if sorted(str(path) for path in pathlib.Path(".").iterdir()) != ["event.json", "parent.json", "response"]:
    raise SystemExit("handoff exposed unexpected state")
event = json.loads(pathlib.Path("event.json").read_text())
parent = json.loads(pathlib.Path("parent.json").read_text())
record = {"schema_version": 1, "event_id": event["event_id"],
          "parent_run_id": parent["parent_run_id"], "parent_sha256": "fixture",
          "transitioned": True, "next_status": "continued",
          "evidence": ["captured Hermes CLI fixture"]}
pathlib.Path("response/agent-consumed.json").write_text(json.dumps(record))
print(json.dumps({"cwd": str(pathlib.Path.cwd()), "requested_identity": argv[2]}))
''')
        docker.chmod(0o755)
        environment = {
            **os.environ, 'PATH': f'{fixture_bin}:{os.environ["PATH"]}',
            'EXPECTED_KEY': self.event['idempotency_key'], 'HOST_HANDOFF': str(handoff),
            'HOST_CANONICAL_SIBLING': str(canonical_sibling),
        }
        with mock.patch.dict(resumer.os.environ, environment, clear=True):
            result = resumer.invoke(handoff)
        self.assertEqual(result.returncode, 0, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual(observed, {'cwd': str(handoff), 'requested_identity': '10000:10000'})
        response = handoff / 'response' / 'agent-consumed.json'
        self.assertTrue(response.is_file())
        self.assertEqual(json.loads(response.read_text())['event_id'], self.event['event_id'])
        release_text = SCRIPT.read_text()
        self.assertNotIn('attachment', release_text)
        self.assertIn("'--in', str(container_handoff),\n        '-z', prompt", release_text)

    def test_invoke_rejects_handoff_outside_configured_root(self):
        with self.assertRaisesRegex(ValueError, 'outside the configured handoff root'):
            resumer.invoke(Path(self.temp.name) / 'outside')

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
        self.assertEqual(stat.S_IMODE((handoff / 'response').stat().st_mode), 0o700)
        self.assertFalse((handoff / 'UNRELATED.json').exists())
        for unrelated in unrelated_paths:
            probe = subprocess.run(['sh', '-c', 'test -r "$1"', 'probe', str(unrelated)])
            self.assertNotEqual(probe.returncode, 0)

    def test_failed_resume_removes_handoff_and_preserves_canonical_state(self):
        key = self.event['idempotency_key']
        with mock.patch.object(resumer.os, 'chown'):
            outcome = resumer.process(self.event_path, self.runner(None, 1, 'fixture failure'))
        self.assertEqual(outcome, 'failed')
        self.assertFalse((resumer.HANDOFFS / key).exists())
        self.assertEqual(json.loads(self.parent_path.read_text()), self.parent)
        self.assertEqual(list(resumer.CONSUMED.iterdir()), [])
        self.assertEqual(list(resumer.AGENT_CONSUMED.iterdir()), [])

    def test_partial_handoff_creation_failure_is_cleaned_up(self):
        key = self.event['idempotency_key']
        with mock.patch.object(resumer.os, 'chown', side_effect=PermissionError('fixture')):
            with self.assertRaises(PermissionError):
                resumer.make_handoff(self.event, self.parent)
        self.assertFalse((resumer.HANDOFFS / key).exists())

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

    def test_event_parent_identity_return_point_and_token_mismatches_fail_closed(self):
        for field in ('parent_run_id', 'capability_incident_id', 'return_point', 'resume_token'):
            with self.subTest(field=field):
                event = dict(self.event)
                event[field] += '-mismatch'
                if field in ('parent_run_id', 'resume_token'):
                    event['idempotency_key'] = hashlib.sha256(
                        f"{event['parent_run_id']}\0{event['resume_token']}".encode()).hexdigest()
                self.event_path.write_text(json.dumps(event))
                self.assertEqual(resumer.process(self.event_path, self.runner(self.record())), 'failed')
                self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'waiting_on_capability')
                self.event_path = resumer.INCOMING / self.event_path.name
                self.event_path.write_text(json.dumps(self.event))

    def test_digest_timestamp_and_evidence_mismatches_fail_closed(self):
        for field, value in (
                ('idempotency_key', '0' * 64), ('timestamp', '2026-08-20T05:24:42'),
                ('evidence_refs', [])):
            with self.subTest(field=field):
                event = dict(self.event)
                event[field] = value
                candidate = resumer.INCOMING / f'{field}.json'
                candidate.write_text(json.dumps(event))
                self.assertEqual(resumer.process(candidate, self.runner(self.record())), 'failed')

    def test_legacy_marker_identity_or_exit_mismatch_is_not_requeued(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        for field, value in (('parent_run_id', 'OTHER'), ('exit_code', 1),
                             ('idempotency_key', '0' * 64)):
            with self.subTest(field=field):
                marker = resumer.CONSUMED / f"{self.event['idempotency_key']}.json"
                bad = self.legacy_marker()
                bad[field] = value
                marker.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    resumer.reconcile_false_marker(marker, processed)
                marker.unlink()
                self.assertFalse((resumer.INCOMING / processed.name).exists())

    def test_explicit_wait_requires_evidence_and_is_successful(self):
        record = self.record('waiting_on_evidence')
        record['evidence'] = ['Chief must supply authoritative branch-protection readback']
        with mock.patch.object(resumer.os, 'chown'):
            self.assertEqual(resumer.process(self.event_path, self.runner(record)), 'consumed')
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'waiting_on_evidence')

    def test_false_marker_reconciliation_preserves_audit_and_is_idempotent(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        key = self.event['idempotency_key']
        marker = resumer.CONSUMED / f'{key}.json'
        marker.write_text(json.dumps(self.legacy_marker()))
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'requeued')
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'already_requeued')
        self.assertFalse(marker.exists())
        self.assertTrue((resumer.RECONCILIATIONS / f'{key}.false-marker.json').is_file())
        audit = json.loads((resumer.RECONCILIATIONS / f'{key}.json').read_text())
        self.assertEqual(audit['action'], 'requeued')
        self.assertTrue((resumer.INCOMING / processed.name).is_file())

    def test_legacy_false_marker_processed_event_and_waiting_parent_transition_once(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        key = self.event['idempotency_key']
        marker = resumer.CONSUMED / f'{key}.json'
        marker.write_text(json.dumps(self.legacy_marker()))

        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'requeued')
        self.assertEqual(resumer.INCOMING.name, 'incoming')
        self.assertTrue((resumer.INCOMING / processed.name).is_file())
        calls = []
        runner = self.runner(self.record())
        def counted(handoff):
            calls.append(self.event['event_id'])
            return runner(handoff)
        with mock.patch.object(resumer.os, 'chown'):
            self.assertEqual(resumer.process(resumer.INCOMING / processed.name, counted), 'consumed')
        self.assertEqual(calls, [self.event['event_id']])
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'continued')
        replay = resumer.INCOMING / 'legacy-replay.json'
        replay.write_text(json.dumps(self.event))
        self.assertEqual(resumer.process(replay, lambda *_: calls.append('unexpected')), 'duplicate')
        self.assertEqual(calls, [self.event['event_id']])

    def test_completed_event_is_idempotent_without_second_agent_invocation(self):
        with mock.patch.object(resumer.os, 'chown'):
            self.assertEqual(resumer.process(self.event_path, self.runner(self.record())), 'consumed')
        replay = resumer.INCOMING / 'replay.json'
        replay.write_text(json.dumps(self.event))
        calls = []
        self.assertEqual(resumer.process(replay, lambda *_: calls.append(1)), 'duplicate')
        self.assertEqual(calls, [])

    def test_durable_agent_record_recovers_interrupted_parent_apply_without_reinvocation(self):
        key = self.event['idempotency_key']
        (resumer.AGENT_CONSUMED / f'{key}.json').write_text(json.dumps(self.record()))
        calls = []
        self.assertEqual(resumer.process(self.event_path, lambda *_: calls.append(1)), 'consumed')
        self.assertEqual(calls, [])
        self.assertEqual(json.loads(self.parent_path.read_text())['status'], 'continued')

    def test_interrupted_false_marker_audit_finalisation_recovers_idempotently(self):
        processed = resumer.PROCESSED / self.event_path.name
        os.replace(self.event_path, processed)
        key = self.event['idempotency_key']
        marker = resumer.CONSUMED / f'{key}.json'
        marker.write_text(json.dumps(self.legacy_marker()))
        (resumer.INCOMING / processed.name).write_text(processed.read_text())
        os.replace(marker, resumer.RECONCILIATIONS / f'{key}.false-marker.json')
        self.assertEqual(resumer.reconcile_false_marker(marker, processed), 'recovered_reconciliation')
        self.assertTrue((resumer.RECONCILIATIONS / f'{key}.json').is_file())

    def test_interrupted_success_marker_write_recovers_without_agent_reinvocation(self):
        key = self.event['idempotency_key']
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
