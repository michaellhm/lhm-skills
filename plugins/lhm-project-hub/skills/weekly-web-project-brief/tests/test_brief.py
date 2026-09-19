import importlib.util
import tempfile
import json
import sys
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('brief', Path(__file__).parents[1] / 'scripts/brief.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class BriefTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = patch.object(b, 'BASE', Path(self.temp.name))
        self.base.start()
        self.addCleanup(self.base.stop)

    def fixture(self):
        return {'week': '2026-09-21', 'cutoff': '19 September', 'intro': 'Fixture only', 'priorities': [], 'new_projects': [], 'owners': [{'name': 'Jaimee', 'actions': ['No immediate action.']}], 'projects': [{'name': name, 'url': 'https://example.org/project', 'light': light, 'state': '<script>alert(1)</script>', 'target': 'To confirm', 'next': 'Michael: check date'} for name, light in [('Green project', 'green'), ('Red project', 'red'), ('Orange project', 'orange')]]}

    def test_dst_gate(self):
        for stamp in ['2026-09-21T02:00:00+00:00', '2026-10-05T01:00:00+00:00']:
            self.assertTrue(b.gate(datetime.fromisoformat(stamp))['wakeAgent'])
        for stamp in ['2026-09-21T01:00:00+00:00', '2026-10-05T02:00:00+00:00', '2026-09-22T02:00:00+00:00']:
            self.assertFalse(b.gate(datetime.fromisoformat(stamp))['wakeAgent'])

    def test_render(self):
        result = b.render(self.fixture())
        self.assertLess(result['html'].index('Red project'), result['html'].index('Orange project'))
        self.assertLess(result['html'].index('Orange project'), result['html'].index('Green project'))
        self.assertNotIn('<script>', result['html'])
        self.assertIn('&lt;script&gt;', result['html'])
        self.assertIn('BasicOps chat with Lily', result['text'])
        self.assertNotIn('AI Support', result['html'])

    def test_readable_linked_owner_action(self):
        d = self.fixture(); d['owners'] = [{'name':'Michael','actions':[{'text':'Your Story: review sitemap & copy','url':'https://app.basicops.com/task/123'}]}]
        result = b.render(d)
        self.assertIn('href="https://app.basicops.com/task/123">Your Story: review sitemap &amp; copy</a>',result['html'])
        self.assertIn('https://app.basicops.com/task/123',result['text'])

    def test_client_groups_preserve_nonadjacent_actions_and_links(self):
        d = self.fixture()
        d['owners'] = [{'name': 'Michael', 'actions': [
            {'client': 'mhealth & LP', 'text': 'Follow up Nick', 'url': 'https://example.org/1'},
            {'client': 'Your Story', 'text': 'Review copy', 'url': 'https://example.org/2'},
            {'client': 'mhealth & LP', 'text': 'Obtain access', 'url': 'https://example.org/3'}]}]
        result = b.render(d)
        self.assertEqual(result['html'].count('<strong>mhealth &amp; LP:</strong>'), 1)
        self.assertLess(result['html'].index('Obtain access'), result['html'].index('<strong>Your Story:</strong>'))
        for i in (1, 2, 3):
            self.assertIn('https://example.org/' + str(i), result['html'])
            self.assertIn('https://example.org/' + str(i), result['text'])
        d['owners'][0]['actions'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaisesRegex(ValueError, 'Action links'): b.render(d)

    def test_reject_unsafe_owner_action_link(self):
        d = self.fixture(); d['owners'] = [{'name':'Michael','actions':[{'text':'Review','url':'javascript:alert(1)'}]}]
        with self.assertRaisesRegex(ValueError,'Action links'):b.render(d)

    def test_bad_link_and_owner(self):
        d = self.fixture(); d['projects'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError): b.render(d)
        d = self.fixture(); d['owners'] = [{'name': 'AI Support', 'actions': []}]
        with self.assertRaises(ValueError): b.render(d)

    def test_uncertain_never_resends(self):
        email = b.render(self.fixture())
        with patch.object(b, 'mailgun', side_effect=TimeoutError) as net:
            with self.assertRaises(RuntimeError): b.send('2026-09-21', email, 'test')
            self.assertEqual(b.send('2026-09-21', email, 'test')['state'], 'deduplicated')
            self.assertEqual(net.call_count, 1)

    def test_week_binding(self):
        with self.assertRaises(ValueError): b.send('2026-09-28', b.render(self.fixture()), 'test')
        with self.assertRaises(ValueError): b.monday('2026-09-22')

    def test_multipart_and_receipt_gate(self):
        email = b.render(self.fixture())
        with patch.object(b, 'now', return_value=datetime.fromisoformat('2026-09-21T12:01:00+10:00')), patch.object(b, 'mailgun', return_value={'id': '<test>'}) as net:
            b.send('2026-09-21', email)
            payload = net.call_args.args[1]
            self.assertEqual(payload['html'], email['html'])
            self.assertEqual(payload['text'], email['text'])
            self.assertEqual(payload['to'], 'support@localhealthmarketing.com.au')
            self.assertNotIn('cc', payload)
            self.assertNotIn('bcc', payload)
            self.assertEqual(payload['h:Reply-To'], 'michael@localhealthmarketing.com.au')
            self.assertFalse(b.gate()['wakeAgent'])

    def test_cli_self_only_and_single_test_prefix(self):
        email = b.render(self.fixture())
        email['subject'] = 'TEST | ' + email['subject']
        payload = Path(self.temp.name) / 'email.json'
        payload.write_text(json.dumps(email))
        quality = types.SimpleNamespace(validate=lambda path: None)
        with patch.dict(sys.modules, {'quality': quality}), patch.object(sys, 'argv', ['brief.py', 'send', '--week', '2026-09-21', '--kind', 'test', '--to-self', '--file', str(payload)]), patch.object(b, 'TO', b.TO), patch.object(b, 'CC', b.CC[:]), patch.object(b, 'RECIPIENTS', b.RECIPIENTS[:]), patch.object(b, 'mailgun', return_value={'id': '<test>'}) as net:
            b.main()
            sent = net.call_args.args[1]
            self.assertEqual(sent['to'], 'michael@localhealthmarketing.com.au')
            self.assertNotIn('cc', sent)
            self.assertNotIn('bcc', sent)
            self.assertEqual(sent['subject'].count('TEST | '), 1)
            receipt = json.loads(b.receipt('2026-09-21', 'test').read_text())
            self.assertEqual(receipt['recipients'], [b.TO])

    def test_cli_quality_failure_prevents_submission(self):
        quality = types.SimpleNamespace(validate=lambda path: (_ for _ in ()).throw(ValueError('Incomplete research')))
        with patch.dict(sys.modules, {'quality': quality}), patch.object(sys, 'argv', ['brief.py', 'send', '--week', '2026-09-21', '--file', str(Path(self.temp.name) / 'email.json')]), patch.object(b, 'mailgun') as net:
            with self.assertRaisesRegex(ValueError, 'Incomplete research'):
                b.main()
            net.assert_not_called()
            self.assertFalse(b.receipt('2026-09-21').exists())

    def test_all_recipients_required(self):
        historical_recipients = ['first@example.com', 'second@example.com']
        b.save(b.receipt('2026-09-21'), {'state': 'queued', 'message_id': '<test>', 'recipients': historical_recipients})
        events = [{'event': 'delivered', 'recipient': r, 'message': {'headers': {'message-id': 'test'}}} for r in historical_recipients]
        with patch.object(b, 'mailgun', return_value={'items': events[:1]}):
            self.assertEqual(b.verify('2026-09-21')['state'], 'queued')
        with patch.object(b, 'mailgun', return_value={'items': events[1:]}):
            self.assertEqual(b.verify('2026-09-21')['state'], 'delivered')

if __name__ == '__main__': unittest.main()
