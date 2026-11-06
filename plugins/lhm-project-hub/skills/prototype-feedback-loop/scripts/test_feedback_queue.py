import copy
import os
import tempfile
import unittest
from feedback_queue import Queue


def packet(mid='one', site='example-clinic'):
    return dict(account='agency@example.invalid', message_id=mid, thread_id='thread-1',
                site=site, cockpit_id='cockpit-1', sender='client@example.invalid',
                received_at='2026-11-06T17:00:00+11:00', source_url='https://example.invalid/mail/1',
                original_text='Change the heading. See image.',
                items=[{'id': 'F1', 'request': 'Change heading to Welcome'}],
                images=[dict(content_id='cid:one', private_ref='private://image-one',
                             sha256='a' * 64, context='Heading reference', status='verified')])


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'queue.db')
        self.q = Queue(self.path)

    def tearDown(self):
        self.q.db.close()
        self.tmp.cleanup()

    def add(self, p=None):
        return self.q.enqueue(p or packet(), eligible=True)

    def test_duplicate_after_restart(self):
        self.add()
        self.q.db.close()
        self.q = Queue(self.path)
        self.assertEqual('existing', self.add())
        self.assertEqual(1, len(self.q.packets(self.q.claim('example-clinic', owner='poller-one', eligible=True)['id'])))

    def test_stage_exit_does_not_consume(self):
        self.add()
        self.assertIsNone(self.q.claim('example-clinic', owner='poller-one', eligible=False))
        self.assertIsNotNone(self.q.claim('example-clinic', owner='poller-one', eligible=True))

    def test_intake_requires_eligibility(self):
        with self.assertRaises(ValueError):
            self.q.enqueue(packet(), eligible=False)

    def test_followup_cannot_change_active_batch(self):
        self.add()
        first = self.q.claim('example-clinic', owner='poller-one', eligible=True)
        self.add(packet('two'))
        self.assertEqual(first, self.q.claim('example-clinic', owner='poller-one', eligible=True))
        self.assertEqual(1, len(self.q.packets(first['id'])))
        self.q.checkpoint(first['id'], owner='poller-one', task_id='task', run_id='run', chat_url='chat', handback_receipt='receipt')
        self.q.ready(first['id'], owner='poller-one', verified=True)
        second = self.q.claim('example-clinic', owner='poller-one', eligible=True)
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual('two', self.q.packets(second['id'])[0]['message_id'])

    def test_cross_site_message_rejected(self):
        self.add()
        with self.assertRaises(ValueError):
            self.add(packet(site='another-clinic'))

    def test_separate_accounts_do_not_collide(self):
        self.add()
        p = packet()
        p['account'] = 'second@example.invalid'
        self.assertEqual('queued', self.add(p))

    def test_missing_image_blocks_intake(self):
        p = packet()
        p['images'][0]['status'] = 'unavailable'
        with self.assertRaises(ValueError):
            self.add(p)

    def test_cids_not_duplicate_filenames(self):
        p = packet()
        image = copy.deepcopy(p['images'][0])
        image['content_id'] = 'cid:two'
        p['images'].append(image)
        self.assertEqual('queued', self.add(p))

    def test_bad_image_digest(self):
        p = packet()
        p['images'][0]['sha256'] = 'bad'
        with self.assertRaises(ValueError):
            self.add(p)

    def test_duplicate_items_rejected(self):
        p = packet()
        p['items'].append(p['items'][0])
        with self.assertRaises(ValueError):
            self.add(p)

    def test_incomplete_result_cannot_be_ready(self):
        self.add()
        batch = self.q.claim('example-clinic', owner='poller-one', eligible=True)['id']
        with self.assertRaises(ValueError):
            self.q.ready(batch, owner='poller-one', verified=True)

    def test_retry_cannot_switch_runs(self):
        self.add()
        batch = self.q.claim('example-clinic', owner='poller-one', eligible=True)['id']
        self.q.checkpoint(batch, owner='poller-one', task_id='task', run_id='original')
        self.q.checkpoint(batch, owner='poller-one', run_id='original')
        with self.assertRaises(ValueError):
            self.q.checkpoint(batch, owner='poller-one', run_id='replayed')
        self.assertEqual('original', self.q.claim('example-clinic', owner='poller-one', eligible=True)['run_id'])

    def test_unknown_checkpoint_field(self):
        with self.assertRaises(ValueError):
            self.q.checkpoint('unknown', owner='poller-one', state='ready_for_review')

    def test_two_pollers_get_one_owner(self):
        self.add()
        first = self.q.claim('example-clinic', owner='one', eligible=True)
        other = Queue(self.path)
        try:
            second = other.claim('example-clinic', owner='two', eligible=True)
            self.assertEqual('busy', second['state'])
            self.assertEqual(first['id'], second['id'])
            with self.assertRaises(ValueError):
                other.checkpoint(first['id'], owner='two', task_id='duplicate')
        finally:
            other.db.close()

    def test_symlink_rejected_without_chmod_target(self):
        target = os.path.join(self.tmp.name, 'target')
        with open(target, 'w') as out:
            out.write('keep')
        os.chmod(target, 0o644)
        link = os.path.join(self.tmp.name, 'link')
        os.symlink(target, link)
        with self.assertRaises(OSError):
            Queue(link)
        self.assertEqual(0o644, os.stat(target).st_mode & 0o777)

    def test_readiness_and_notification_are_separate(self):
        self.add()
        batch = self.q.claim('example-clinic', owner='poller-one', eligible=True)['id']
        self.q.checkpoint(batch, owner='poller-one', task_id='task', run_id='run',
                          chat_url='chat', handback_receipt='verified-handback')
        with self.assertRaises(ValueError):
            self.q.ready(batch, owner='poller-one', verified=False)
        with self.assertRaises(ValueError):
            self.q.ready(batch, owner='another-poller', verified=True)
        self.q.ready(batch, owner='poller-one', verified=True)
        self.q.checkpoint(batch, owner='poller-one', notification_receipt='delivered')
        self.assertIsNone(self.q.claim('example-clinic', owner='new-poller', eligible=True))

    def test_stage_exit_after_claim_preserves_batch(self):
        self.add()
        first = self.q.claim('example-clinic', owner='poller-one', eligible=True)
        self.assertIsNone(self.q.claim('example-clinic', owner='poller-one', eligible=False))
        self.assertEqual(first, self.q.claim('example-clinic', owner='poller-one', eligible=True))

    def test_private_database(self):
        self.assertEqual(0o600, os.stat(self.path).st_mode & 0o777)


if __name__ == '__main__':
    unittest.main()
