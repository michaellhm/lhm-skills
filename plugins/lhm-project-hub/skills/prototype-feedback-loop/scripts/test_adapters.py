"""Contract/fault tests with fake connectors; these do not prove live integration."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from adapters import BasicOps, Completion, Effects, Gmail, ReconcileRequired, ScanLedger, Ted, pages
from feedback_queue import Queue


class EffectsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'effects.db'
        self.effects = Effects(self.path)
        self.remote = None
        self.writes = 0

    def tearDown(self):
        self.effects.db.close()
        self.tmp.cleanup()

    def write(self):
        self.writes += 1
        self.remote = {'id': 123}
        return self.remote

    def test_timeout_after_remote_write_reconciles_after_restart_without_replay(self):
        def timeout():
            self.write()
            raise TimeoutError('response lost')
        with self.assertRaises(TimeoutError):
            self.effects.perform('a', {'x': 1}, lambda: self.remote, timeout, bool)
        self.effects.db.close()
        self.effects = Effects(self.path)
        self.assertEqual(self.effects.perform('a', {'x': 1}, lambda: self.remote, self.write, bool), {'id': 123})
        self.assertEqual(self.writes, 1)

    def test_unknown_write_with_no_remote_match_never_replays(self):
        def timeout():
            self.writes += 1
            raise TimeoutError()
        with self.assertRaises(TimeoutError):
            self.effects.perform('a', {}, lambda: None, timeout, bool)
        with self.assertRaises(ReconcileRequired):
            self.effects.perform('a', {}, lambda: None, self.write, bool)
        self.assertEqual(self.writes, 1)

    def test_changed_payload_rejected_before_write(self):
        self.effects.perform('a', {'x': 1}, lambda: None, self.write, bool)
        with self.assertRaises(ReconcileRequired):
            self.effects.perform('a', {'x': 2}, lambda: None, self.write, bool)
        self.assertEqual(self.writes, 1)

    def test_failed_readback_stays_uncertain(self):
        with self.assertRaises(ReconcileRequired):
            self.effects.perform('a', {}, lambda: None, self.write, lambda _: False)
        self.assertEqual(self.effects.db.execute('SELECT state FROM effects').fetchone()[0], 'uncertain')
        self.effects.perform('a', {}, lambda: self.remote, self.write, bool)
        self.assertEqual(self.writes, 1)

    def test_two_open_journals_do_not_replay_uncertain_write(self):
        other = Effects(self.path)
        def write():
            with self.assertRaises(ReconcileRequired):
                other.perform('a', {}, lambda: None, self.write, bool)
            return self.write()
        self.effects.perform('a', {}, lambda: None, write, bool)
        other.db.close()
        self.assertEqual(self.writes, 1)

    def test_deleted_verified_remote_receipt_does_not_recreate(self):
        self.effects.perform('a', {}, lambda: None, self.write, bool)
        with self.assertRaises(ReconcileRequired):
            self.effects.perform('a', {}, lambda: None, self.write, lambda _: False)
        self.assertEqual(self.writes, 1)

    def test_symlink_journal_rejected(self):
        target = Path(self.tmp.name) / 'target'
        target.touch()
        link = Path(self.tmp.name) / 'link'
        link.symlink_to(target)
        with self.assertRaises(OSError):
            Effects(link)


class PaginationTests(unittest.TestCase):
    def test_all_pages_read(self):
        def call(name, args):
            return {'data': [2]} if args.get('nextPage') == 'b' else {'data': [1], 'nextPage': 'b'}
        self.assertEqual(list(pages(call, 'list', {})), [1, 2])

    def test_repeated_cursor_fails_closed(self):
        with self.assertRaises(ValueError):
            list(pages(lambda *_: {'data': [], 'nextPage': 'same'}, 'list', {}))


class BasicOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.effects = Effects(Path(self.tmp.name) / 'effects.db')
        self.payload = {'title': 'Client: Website - Apply feedback', 'description': '<p>brief link</p>',
                        'projectId': 12, 'section': 13, 'assignee': 82491}
        self.cockpit = {'id': 1, 'project': {'id': 68635}, 'section': {'id': 110340}, 'status': 'In Progress'}
        self.tasks = []
        self.writes = 0
        self.api = BasicOps(self.call, self.effects, 110340)

    def tearDown(self):
        self.effects.db.close()
        self.tmp.cleanup()

    def call(self, name, args):
        if name == 'get_task':
            return copy.deepcopy(self.cockpit if args['taskId'] == 1 else next(t for t in self.tasks if t['id'] == args['taskId']))
        if name == 'list_tasks_in_project':
            return {'data': copy.deepcopy(self.tasks)}
        if name == 'create_task':
            self.writes += 1
            task = dict(id=2, title=args['title'], description=args['description'], project={'id': args['projectId']},
                        section={'id': args['section']}, assignee={'id': args['assignee']}, url='https://app.basicops.com/task')
            self.tasks.append(task)
            return task
        raise AssertionError(name)

    def test_discussion_obeys_connector_fifty_message_limit(self):
        messages, limits = [], []
        def call(name, args):
            if name == 'list_messages_in_task':
                limits.append(args['limit'])
                if args['limit'] > 50:
                    raise ValueError('BasicOps list_messages_in_task limit exceeds 50')
                return {'data': messages}
            if name == 'create_message_in_task':
                messages.append({'id': 'dm1', 'message': args['message']})
                return {'id': 'dm1'}
            self.fail(name)
        self.api.call = call
        self.assertEqual(self.api.discussion('batch', 2, '<p>Brief</p>'), {'message_id': 'dm1'})
        self.api.discussion('batch', 2, '<p>Brief</p>')
        self.assertEqual(len(messages), 1)
        self.assertEqual(set(limits), {50})

    def test_create_readback_then_repeat_has_one_task(self):
        self.assertEqual(self.api.task('batch', 1, self.payload), {'task_id': 2})
        self.api.task('batch', 1, self.payload)
        self.assertEqual(self.writes, 1)

    def test_stage_exit_blocks_before_write(self):
        self.cockpit['section']['id'] = 99
        with self.assertRaises(ReconcileRequired):
            self.api.task('batch', 1, self.payload)
        self.assertEqual(self.writes, 0)

    def test_stage_exit_between_lookup_and_create_blocks(self):
        original = self.api.call
        def call(name, args):
            result = original(name, args)
            if name == 'list_tasks_in_project':
                self.cockpit['section']['id'] = 99
            return result
        self.api.call = call
        with self.assertRaises(ReconcileRequired):
            self.api.task('batch', 1, self.payload)
        self.assertEqual(self.writes, 0)

    def test_wrong_ted_identity_blocks(self):
        self.payload['assignee'] = 36398
        with self.assertRaises(ValueError):
            self.api.task('batch', 1, self.payload)
        self.assertEqual(self.writes, 0)

    def test_duplicate_remote_candidates_block(self):
        self.call('create_task', self.payload)
        self.tasks.append(dict(self.tasks[0], id=3))
        with self.assertRaises(ReconcileRequired):
            self.api.task('batch', 1, self.payload)
        self.assertEqual(self.writes, 1)

    def test_assignee_readback_mismatch_blocks(self):
        self.call('create_task', self.payload)
        self.tasks[0]['assignee']['id'] = 36398
        with self.assertRaises(ReconcileRequired):
            self.api.task('batch', 1, self.payload)


class GmailTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = {'1': b'first', '2': b'second'}
        self.adapter = Gmail(lambda _: None, lambda msg, att, part: self.data[part], Path(self.tmp.name) / 'images')
        self.reg = {'senders': ['tara@example.com'], 'review_start': '2026-11-05T00:00:00+00:00', 'threads': ['thread'],
                    'account': 'michael@example.com', 'site': 'luminary', 'cockpit_id': 1, 'mail_url': 'https://mail.google.com/#all/'}
        self.msg = {'id': 'msg', 'thread_id': 'thread', 'internal_date': '1793947758000', 'payload': {
            'mime_type': 'multipart/related', 'headers': [{'name': 'From', 'value': 'Tara <tara@example.com>'}],
            'parts': [{'part_id': '0', 'mime_type': 'text/plain', 'body': {'content': 'Please change the logo'}},
                      *[{'part_id': str(i), 'mime_type': 'image/png', 'filename': 'image.png', 'headers': [{'name': 'Content-ID', 'value': f'<cid{i}>'}],
                         'body': {'attachment_id': f'att{i}', 'size': len(self.data[str(i)])}, 'read_attachment_supported': True}
                        for i in (1, 2)]]}}
        self.extracted = {'items': [{'id': '1', 'request': 'Change logo'}], 'image_context': {'cid1': 'sun illustration', 'cid2': 'organic roots'}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_filename_images_have_distinct_files_and_hashes(self):
        packet = self.adapter.intake(self.msg, self.reg, self.extracted)
        images = packet['images']
        self.assertNotEqual(images[0]['private_ref'], images[1]['private_ref'])
        self.assertEqual(images[0]['sha256'], hashlib.sha256(b'first').hexdigest())
        self.assertEqual(images[1]['sha256'], hashlib.sha256(b'second').hexdigest())
        self.assertEqual([i['content_id'] for i in images], ['cid1', 'cid2'])
        self.assertEqual(self.adapter.intake(self.msg, self.reg, self.extracted), packet)

    def test_wrong_sender_rejected(self):
        self.msg['payload']['headers'][0]['value'] = 'Other <other@example.com>'
        with self.assertRaisesRegex(ValueError, 'sender'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_unrelated_separate_thread_requires_explicit_match(self):
        self.msg['thread_id'] = 'separate'
        with self.assertRaisesRegex(ValueError, 'separate email'):
            self.adapter.intake(self.msg, self.reg, self.extracted)
        self.assertEqual(self.adapter.intake(self.msg, self.reg, self.extracted, related_thread=True)['thread_id'], 'separate')

    def test_missing_image_review_blocks(self):
        del self.extracted['image_context']['cid2']
        with self.assertRaisesRegex(ValueError, 'visual review'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_truncated_image_blocks(self):
        self.data['2'] = b'x'
        with self.assertRaisesRegex(ValueError, 'truncated'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_unsupported_attachment_blocks(self):
        self.msg['payload']['parts'][2]['read_attachment_supported'] = False
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_private_image_symlink_is_rejected(self):
        filename = hashlib.sha256(b'michael@example.com:msg:1').hexdigest()
        target = Path(self.tmp.name) / 'external'
        target.write_bytes(b'first')
        (self.adapter.root / filename).symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'storage conflict'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_missing_message_body_blocks(self):
        self.msg['payload']['parts'] = []
        with self.assertRaisesRegex(ValueError, 'message text'):
            self.adapter.intake(self.msg, self.reg, self.extracted)

    def test_pre_review_message_rejected(self):
        self.reg['review_start'] = '2026-12-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError, 'review window'):
            self.adapter.intake(self.msg, self.reg, self.extracted)


class TedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.effects = Effects(Path(self.tmp.name) / 'effects.db')
        self.remote = None
        self.writes = 0
        self.eligible = True
        self.payload = {'task_id': 2, 'authority_kind': 'registered-prototype-feedback'}
        self.adapter = Ted(self.submit, lambda _: copy.deepcopy(self.remote), self.effects, lambda: self.eligible)

    def tearDown(self):
        self.effects.db.close()
        self.tmp.cleanup()

    def submit(self, batch, payload):
        self.writes += 1
        self.remote = {'request_id': batch, 'task_id': payload['task_id'], 'run_id': 'run', 'chat_url': 'codex://threads/test', 'status': 'accepted'}
        return copy.deepcopy(self.remote)

    def test_repeated_dispatch_has_one_run(self):
        self.adapter.dispatch('batch', self.payload)
        self.adapter.dispatch('batch', self.payload)
        self.assertEqual(self.writes, 1)

    def test_status_progress_preserves_immutable_dispatch_receipt(self):
        receipt = self.adapter.dispatch('batch', self.payload)
        self.remote['status'] = 'running'
        self.assertEqual(self.adapter.dispatch('batch', self.payload), receipt)
        self.assertEqual(self.writes, 1)

    def test_wrong_remote_run_does_not_accept_receipt(self):
        self.adapter.dispatch('batch', self.payload)
        self.remote['run_id'] = 'other-run'
        with self.assertRaises(ReconcileRequired):
            self.adapter.dispatch('batch', self.payload)

    def test_stage_exit_blocks_dispatch(self):
        self.eligible = False
        with self.assertRaises(ReconcileRequired):
            self.adapter.dispatch('batch', self.payload)
        self.assertEqual(self.writes, 0)

    def test_wrong_authority_blocks_dispatch(self):
        self.payload['authority_kind'] = 'human'
        with self.assertRaises(ValueError):
            self.adapter.dispatch('batch', self.payload)
        self.assertEqual(self.writes, 0)

    def test_timeout_after_submit_reconciles_same_run(self):
        original = self.adapter.submit
        def submit(*args):
            original(*args)
            raise TimeoutError()
        self.adapter.submit = submit
        with self.assertRaises(TimeoutError):
            self.adapter.dispatch('batch', self.payload)
        receipt = self.adapter.dispatch('batch', self.payload)
        self.assertEqual(receipt['run_id'], 'run')
        self.assertEqual(self.writes, 1)



class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.effects = Effects(Path(self.tmp.name) / 'effects.db')
        self.queue = Queue(Path(self.tmp.name) / 'queue.db')
        self.queue.enqueue(dict(account='michael@example.com', message_id='message', thread_id='thread', site='luminary',
            cockpit_id='1', sender='tara@example.com', received_at='2026-11-06T01:00:00+00:00',
            source_url='https://mail.google.com/#all/message', original_text='change logo',
            items=[{'id': '1', 'request': 'Change logo'}], images=[]), eligible=True)
        self.batch = self.queue.claim('luminary', owner='owner', eligible=True)['id']
        self.queue.checkpoint(self.batch, owner='owner', task_id='2', run_id='run', chat_url='codex://threads/run')
        self.registration = {'repository': 'michaellhm/lhm-prototype', 'branch': 'main',
            'preview_url': 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/', 'reviewer_id': 36398}
        self.body = b'<html>Verified prototype</html>'
        self.run = dict(task_id='2', run_id='run', chat_url='codex://threads/run', status='succeeded', commit='a'*40,
            repository=self.registration['repository'], branch='main', preview_url=self.registration['preview_url'],
            content_sha256=hashlib.sha256(self.body).hexdigest(), worker_identity='worker-1',
            checks={'desktop': True, 'mobile': True},
            independent_qa={'status': 'passed', 'commit': 'a'*40, 'reviewer': 'qa-1', 'package_sha256': 'b'*64})
        self.deployed = {'commit': 'a'*40, 'conclusion': 'success', 'workflow': 'Deploy to lhmstaging', 'id': 'deploy-1'}
        self.handback = dict(task_id='2', run_id='run', commit='a'*40, preview_url=self.registration['preview_url'],
                             status='Under Review', reviewer_id=36398, receipt_id='discussion-1')
        self.notifications = {}
        self.sent = 0
        self.observed = 0
        self.adapter = Completion(self.queue, self.effects, self.observe, lambda *_: 'a'*40,
            lambda *_: self.deployed, lambda _: {'status': 200, 'body': self.body}, lambda _: self.handback,
            lambda key: self.notifications.get(key), self.notify,
            lambda key, payload, receipt: self.notifications.get(key) == receipt)

    def tearDown(self):
        self.effects.db.close()
        self.queue.db.close()
        self.tmp.cleanup()

    def observe(self, run):
        self.observed += 1
        return self.run

    def notify(self, key, payload):
        self.sent += 1
        self.notifications[key] = {'delivery_key': key, 'status': 'delivered', 'receipt_id': 'notification-1'}
        return self.notifications[key]

    def ready(self):
        return self.adapter.ready(self.batch, owner='owner', registration=self.registration)

    def state(self):
        return self.queue.db.execute('SELECT state FROM batches WHERE id=?', (self.batch,)).fetchone()[0]

    def test_all_authoritative_checks_before_ready_and_separate_notification(self):
        self.ready()
        self.assertEqual(self.state(), 'ready_for_review')
        self.assertEqual(self.sent, 0)
        self.adapter.notification(self.batch, owner='owner')
        self.adapter.notification(self.batch, owner='owner')
        self.assertEqual(self.sent, 1)
        self.assertEqual(self.observed, 1)

    def test_wrong_run_identity_blocks_and_retains_active_slot(self):
        self.run['run_id'] = 'other'
        with self.assertRaises(ReconcileRequired):
            self.ready()
        self.assertEqual(self.state(), 'active')
        self.assertEqual(self.queue.claim('luminary', owner='another', eligible=True)['state'], 'busy')

    def test_failed_worker_blocks_and_retains_active_slot(self):
        self.run['status'] = 'failed'
        with self.assertRaises(ReconcileRequired):
            self.ready()
        self.assertEqual(self.state(), 'active')

    def test_remote_commit_mismatch_blocks(self):
        self.adapter.remote_commit = lambda *_: 'c'*40
        with self.assertRaisesRegex(ReconcileRequired, 'remote commit'):
            self.ready()
        self.assertEqual(self.state(), 'active')

    def test_successful_deployment_for_other_commit_blocks(self):
        self.deployed['commit'] = 'c'*40
        with self.assertRaisesRegex(ReconcileRequired, 'exact-commit deployment'):
            self.ready()

    def test_failed_deployment_blocks(self):
        self.deployed['conclusion'] = 'failure'
        with self.assertRaises(ReconcileRequired):
            self.ready()

    def test_nonempty_http_200_and_exact_content_hash_required(self):
        for response in ({'status': 403, 'body': self.body}, {'status': 200, 'body': b''}, {'status': 200, 'body': b'wrong'}):
            with self.subTest(response=response):
                self.adapter.http_get = lambda _, response=response: response
                with self.assertRaises(ReconcileRequired):
                    self.ready()
                self.assertEqual(self.state(), 'active')

    def test_independent_exact_commit_qa_required(self):
        for field, value in (('reviewer', 'worker-1'), ('commit', 'c'*40), ('package_sha256', 'bad'), ('status', 'failed')):
            original = self.run['independent_qa'][field]
            self.run['independent_qa'][field] = value
            with self.subTest(field=field), self.assertRaises(ReconcileRequired):
                self.ready()
            self.run['independent_qa'][field] = original

    def test_both_viewports_required(self):
        self.run['checks']['mobile'] = False
        with self.assertRaises(ReconcileRequired):
            self.ready()

    def test_handback_wrong_reviewer_blocks(self):
        self.handback['reviewer_id'] = 82491
        with self.assertRaisesRegex(ReconcileRequired, 'handback'):
            self.ready()
        self.assertEqual(self.state(), 'active')

    def test_notification_before_ready_blocks(self):
        with self.assertRaises(ReconcileRequired):
            self.adapter.notification(self.batch, owner='owner')
        self.assertEqual(self.sent, 0)

    def test_notification_timeout_after_delivery_reconciles_without_worker_replay(self):
        self.ready()
        notify = self.adapter.notify
        def timeout(key, payload):
            notify(key, payload)
            raise TimeoutError('response lost')
        self.adapter.notify = timeout
        with self.assertRaises(TimeoutError):
            self.adapter.notification(self.batch, owner='owner')
        self.adapter.notification(self.batch, owner='owner')
        self.assertEqual(self.sent, 1)
        self.assertEqual(self.observed, 1)
        self.assertEqual(self.state(), 'ready_for_review')

    def test_unknown_notification_outcome_never_replays_implementation(self):
        self.ready()
        def timeout(*_):
            self.sent += 1
            raise TimeoutError()
        self.adapter.notify = timeout
        with self.assertRaises(TimeoutError):
            self.adapter.notification(self.batch, owner='owner')
        with self.assertRaises(ReconcileRequired):
            self.adapter.notification(self.batch, owner='owner')
        self.assertEqual(self.sent, 1)
        self.assertEqual(self.observed, 1)
        self.assertEqual(self.state(), 'ready_for_review')

    def test_wrong_owner_cannot_ready_or_notify(self):
        with self.assertRaises(ReconcileRequired):
            self.adapter.ready(self.batch, owner='other', registration=self.registration)
        self.ready()
        with self.assertRaises(ReconcileRequired):
            self.adapter.notification(self.batch, owner='other')
        self.assertEqual(self.sent, 0)

    def test_crash_between_handback_checkpoint_and_ready_recovers(self):
        ready = self.queue.ready
        self.queue.ready = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError('crash'))
        with self.assertRaises(RuntimeError):
            self.ready()
        self.assertEqual(self.state(), 'active')
        self.queue.ready = ready
        self.ready()
        self.assertEqual(self.state(), 'ready_for_review')


class ScanLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.effects = Effects(Path(self.tmp.name) / 'effects.db')
        self.ledger = ScanLedger(self.effects)
        self.message = {'id': 'm', 'thread_id': 'thread', 'internal_date': '1793947758000',
                        'payload': {'headers': [{'name': 'From', 'value': 'Tara <tara@example.com>'}]}}
        self.registration = {'account': 'michael@example.com', 'site': 'luminary', 'senders': ['tara@example.com'],
                             'threads': ['thread'], 'review_start': '2026-11-05T00:00:00+00:00'}
        self.classification = {'kind': 'acknowledgement', 'reviewed': True, 'reason': 'Thanks only; no requested changes'}

    def tearDown(self):
        self.effects.db.close()
        self.tmp.cleanup()

    def test_noop_survives_reopening(self):
        self.assertEqual(self.ledger.record(self.message, self.registration, self.classification), 'recorded')
        self.effects.db.close()
        self.effects = Effects(Path(self.tmp.name) / 'effects.db')
        self.ledger = ScanLedger(self.effects)
        self.assertEqual(self.ledger.record(self.message, self.registration, self.classification), 'existing')

    def test_unverified_sender_cannot_record_noop(self):
        self.registration['senders'] = ['other@example.com']
        with self.assertRaises(ValueError):
            self.ledger.record(self.message, self.registration, self.classification)

    def test_before_window_cannot_record_noop(self):
        self.registration['review_start'] = '2026-12-01T00:00:00+00:00'
        with self.assertRaises(ValueError):
            self.ledger.record(self.message, self.registration, self.classification)

    def test_feedback_cannot_be_recorded_as_noop(self):
        self.classification['kind'] = 'feedback'
        with self.assertRaises(ValueError):
            self.ledger.record(self.message, self.registration, self.classification)

    def test_cross_site_or_changed_classification_rejected(self):
        self.ledger.record(self.message, self.registration, self.classification)
        self.registration['site'] = 'other'
        with self.assertRaises(ReconcileRequired):
            self.ledger.record(self.message, self.registration, self.classification)

    def test_unverified_separate_email_rejected(self):
        self.message['thread_id'] = 'other-thread'
        with self.assertRaises(ValueError):
            self.ledger.record(self.message, self.registration, self.classification)


if __name__ == '__main__':
    unittest.main()
