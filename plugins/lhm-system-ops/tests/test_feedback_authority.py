import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/feedback_authority.py'
spec = importlib.util.spec_from_file_location('feedback_authority', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'config').mkdir()
        self.path = self.root/'config/prototype-feedback-authority.json'
        self.task = {'id': 12, 'url': 'https://app.basicops.com/task/12', 'assignee': 82491, 'status': 'In Progress'}
        self.message = {'id': 'dm34', 'user': {'id': 82491}, 'message': '<p>Implement revisions. AI authorship: Ted.</p>'}
        self.cockpit = {'id': 99, 'project': {'id': 68635}, 'section': {'id': 110340}, 'status': 'Accepted'}
        self.grant = {'authority_id': mod.AUTHORITY, 'task_id': 12, 'instruction_message_id': 'dm34',
                      'instruction_sha256': hashlib.sha256(self.message['message'].encode()).hexdigest(),
                      'cockpit_id': 99, 'stage_id': 110340, 'client_id': 'blue-dragonfly',
                      'batch_id': 'prototype-'+'a'*32, 'author_id': 82491, 'reviewer_id': 36398,
                      'repository': 'michaellhm/lhm-prototype', 'subtree': 'luminary-counselling/', 'enabled': True}
        self.identity = 82491
        self.save()
        real_fstat = os.fstat
        def root_stat(fd):
            s = real_fstat(fd)
            return SimpleNamespace(st_uid=0, st_mode=s.st_mode, st_size=s.st_size)
        self.mock_owner = patch.object(mod.os, 'fstat', side_effect=root_stat)
        self.mock_owner.start()
        self.addCleanup(self.mock_owner.stop)

    def save(self):
        self.path.write_text(json.dumps({'schema_version': 1, 'grants': {'12': self.grant}}))
        self.path.chmod(0o644)

    def api(self, name, args):
        if name == 'get_current_user': return {'id': self.identity}
        if name == 'get_task':
            self.assertEqual(args, {'taskId': 99})
            return self.cockpit
        self.fail(name)

    def check(self, **kwargs):
        return mod.verify(self.root, self.api, self.task, self.message, **kwargs)

    def router(self):
        source = SOURCE.with_name('router.py')
        spec = importlib.util.spec_from_file_location('feedback_test_router', source)
        router_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(router_mod)
        (self.root/'task-router.json').write_text(json.dumps({
            'codex_host_id': 'remote-control:test-host', 'agent_user_id': 82491, 'reviewer_id': 36398, 'providers': {'codex': True, 'claude': True},
            'clients': {'blue-dragonfly': {'name': 'Blue Dragonfly', 'vault_prefix': '20 Clients/Blue Dragonfly/', 'basicops_task_ids': ['12']}}}))
        self.task.update(title='Blue Dragonfly: Website - Revise the prototype', description='')
        self.message['created'] = 1
        self.messages = [self.message]
        queue = self.root/'queue'
        (queue/'incoming').mkdir(parents=True, exist_ok=True)
        def api(name, args):
            if name == 'get_task' and args['taskId'] == 12: return self.task
            if name == 'list_messages_in_task': return self.messages
            if name == 'create_message_in_task':
                value = {'id': 'dm'+str(100+len(self.messages)), 'user': 82491, 'created': 2, 'message': args['message']}
                self.messages.append(value)
                return value
            return self.api(name, args)
        return router_mod.Router(self.root, queue, api)

    def test_router_registered_ai_contract_is_scoped_and_idempotent(self):
        router = self.router()
        request = router.contract(12, 'dm34')[1]
        self.assertEqual(request['provider'], 'codex')
        self.assertEqual(request['handoff_mode'], 'provider_execution')
        self.assertEqual(request['permission_ceiling'], 'registered_prototype_revision')
        self.assertEqual(request['feedback_authority']['repository'], 'michaellhm/lhm-prototype')
        self.assertEqual(router.submit(12, 'dm34')['status'], 'queued')
        self.assertEqual(router.contract(12, 'dm34')[1], request)
        self.assertEqual(router.submit(12, 'dm34')['status'], 'queued')
        self.assertEqual(len(list((self.root/'queue/incoming').glob('*.json'))), 1)

    def admission(self, router, status='running'):
        request = router.contract(12, 'dm34')[1]
        router.submit(12, 'dm34')
        run = self.root/'queue/runs'/request['request_id']
        run.mkdir(parents=True)
        receipt = {'request_id': request['request_id'], 'provider': 'codex', 'status': status,
                   'thread_id': 'd0ed0bb4-343b-4df2-bba7-69d2e6889cfa'}
        (run/'receipt.json').write_text(json.dumps(receipt))
        return run, receipt

    def test_exit_after_running_keeps_run_and_returns_session_link(self):
        router = self.router()
        run, receipt = self.admission(router)
        self.cockpit['section']['id'] = 110341
        result = router.reconcile(12)
        self.assertEqual(result['thread_id'], receipt['thread_id'])
        self.assertTrue(result['session_notification']['verified'])
        self.assertEqual(len(list((self.root/'queue/incoming').glob('*.json'))), 1)
        with self.assertRaises(ValueError): router.submit(12, 'dm34')

    def test_exit_after_completion_permits_handback_without_new_dispatch(self):
        router = self.router()
        run, receipt = self.admission(router, 'needs_review')
        self.cockpit['section']['id'] = 110341
        (run/'result.md').write_text('Existing worker result; requires human review.')
        self.assertTrue(router.reconcile(12)['notification']['verified'])
        before = len(self.messages)
        router.reconcile(12)
        self.assertEqual(len(self.messages), before)

    def test_exit_before_admission_does_not_hand_back_as_running(self):
        router = self.router()
        router.submit(12, 'dm34')
        self.cockpit['section']['id'] = 110341
        self.assertEqual(router.reconcile(12)['status'], 'queued')
        self.assertEqual(len(self.messages), 1)

    def test_starting_receipt_cannot_bypass_stage(self):
        router = self.router()
        run, receipt = self.admission(router, 'starting')
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.contract(12, 'dm34', _reconcile=True)

    def test_invalid_thread_receipt_cannot_bypass_stage(self):
        router = self.router()
        run, receipt = self.admission(router)
        receipt['thread_id'] = 'not-an-existing-codex-thread'
        (run/'receipt.json').write_text(json.dumps(receipt))
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.contract(12, 'dm34', _reconcile=True)

    def test_changed_observed_thread_does_not_qualify_as_admitted(self):
        router = self.router()
        run, receipt = self.admission(router)
        observation = dict(receipt, thread_id='94eb6c67-6514-4572-849d-3c113f097a82')
        self.assertIsNone(router.feedback_admitted_request(12, 'dm34', observation))

    def test_wrong_run_receipt_cannot_bypass_stage(self):
        router = self.router()
        run, receipt = self.admission(router)
        receipt['request_id'] = 'ted-route-99-dm34'
        (run/'receipt.json').write_text(json.dumps(receipt))
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.contract(12, 'dm34', _reconcile=True)

    def test_world_writable_receipt_cannot_bypass_stage(self):
        router = self.router()
        run, receipt = self.admission(router)
        (run/'receipt.json').chmod(0o666)
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.contract(12, 'dm34', _reconcile=True)

    def test_symlink_receipt_cannot_bypass_stage(self):
        router = self.router()
        run, receipt = self.admission(router)
        original = run/'receipt.json'
        original.rename(run/'saved.json')
        original.symlink_to(run/'saved.json')
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(OSError): router.contract(12, 'dm34', _reconcile=True)

    def test_human_stop_still_blocks_post_admission_handback(self):
        router = self.router()
        run, receipt = self.admission(router)
        self.messages.append({'id': 'dm88', 'user': 36398, 'created': 9, 'message': 'Stop this task'})
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.reconcile(12)
        self.assertEqual(len(self.messages), 2)

    def test_router_stage_exit_blocks_host_admission(self):
        router = self.router()
        router.submit(12, 'dm34')
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): router.contract(12, 'dm34')
        self.assertEqual(router.status(12)['status'], 'queued')

    def test_router_rejects_ai_instruction_without_grant(self):
        router = self.router()
        self.path.unlink()
        with self.assertRaises(ValueError): router.contract(12, 'dm34')

    def test_router_rejects_canonical_client_conflict(self):
        router = self.router()
        self.grant['client_id'] = 'wrong-client'
        self.save()
        with self.assertRaises(ValueError): router.contract(12, 'dm34')

    def test_router_preserves_live_negated_approval_repair(self):
        router = self.router()
        self.path.unlink()
        self.message.update(user=36398, message='This is not yet approved. Work on it later.')
        with self.assertRaises(ValueError): router.contract(12, 'dm34')

    def test_ai_instruction_has_explicit_system_authority(self):
        self.assertEqual(self.check()['subtree'], 'luminary-counselling/')

    def test_missing_registry_keeps_ordinary_human_path(self):
        self.path.unlink()
        self.assertIsNone(self.check())

    def test_unregistered_task_keeps_human_path(self):
        self.task['id'] = 13
        self.assertIsNone(self.check())

    def test_wrong_author_rejected(self):
        self.message['user']['id'] = 36398
        with self.assertRaises(ValueError): self.check()

    def test_changed_body_rejected(self):
        self.message['message'] += ' Publish another repository.'
        with self.assertRaises(ValueError): self.check()

    def test_changed_message_id_rejected(self):
        self.message['id'] = 'dm35'
        with self.assertRaises(ValueError): self.check()

    def test_wrong_connector_rejected(self):
        self.identity = 36398
        with self.assertRaises(ValueError): self.check()

    def test_wrong_stage_stops_new_dispatch(self):
        self.cockpit['section']['id'] = 110341
        with self.assertRaises(ValueError): self.check()

    def test_wrong_project_rejected(self):
        self.cockpit['project']['id'] = 1
        with self.assertRaises(ValueError): self.check()

    def test_wrong_task_owner_rejected(self):
        self.task['assignee'] = 36398
        with self.assertRaises(ValueError): self.check()

    def test_stopped_task_rejected(self):
        self.task['status'] = 'Cancelled'
        with self.assertRaises(ValueError): self.check()

    def test_stage_exit_preserves_verified_admitted_scope(self):
        binding = self.check()
        request = {'task_id': 12, 'instruction_message_id': 'dm34',
                   'instruction_sha256': self.grant['instruction_sha256'], 'feedback_authority': binding}
        self.cockpit['section']['id'] = 110341
        self.assertEqual(self.check(admitted_request=request), binding)
        request['feedback_authority'] = dict(binding, subtree='prototypes/other/')
        with self.assertRaises(ValueError): self.check(admitted_request=request)

    def test_forged_repository_rejected(self):
        self.grant['repository'] = 'michaellhm/live-site'
        self.save()
        with self.assertRaises(ValueError): self.check()

    def test_subtree_traversal_rejected(self):
        self.grant['subtree'] = 'luminary-counselling/../../'
        self.save()
        with self.assertRaises(ValueError): self.check()

    def test_wrong_task_binding_rejected(self):
        self.grant['task_id'] = 13
        self.save()
        with self.assertRaises(ValueError): self.check()

    def test_world_writable_registry_rejected(self):
        self.path.chmod(0o666)
        with self.assertRaises(ValueError): self.check()

    def test_non_root_registry_rejected(self):
        self.mock_owner.stop()
        if os.getuid() == 0: self.skipTest('requires non-root local test account')
        with self.assertRaises(ValueError): self.check()

    def test_symlink_registry_rejected(self):
        target = self.path.with_suffix('.saved')
        self.path.rename(target)
        self.path.symlink_to(target)
        with self.assertRaises(OSError): self.check()

    def test_extra_grant_field_rejected(self):
        self.grant['allow_email_commands'] = True
        self.save()
        with self.assertRaises(ValueError): self.check()

    def test_malformed_registry_rejected(self):
        self.path.write_text('{"schema_version":1,"grants":[],"extra":true}')
        with self.assertRaises(ValueError): self.check()


if __name__ == '__main__': unittest.main()
