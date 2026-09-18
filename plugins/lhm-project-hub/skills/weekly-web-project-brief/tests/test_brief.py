import importlib.util
import tempfile
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
            self.assertEqual(payload['to'], b.TO)
            self.assertFalse(b.gate()['wakeAgent'])

    def test_all_recipients_required(self):
        b.save(b.receipt('2026-09-21'), {'state': 'queued', 'message_id': '<test>', 'recipients': b.RECIPIENTS})
        events = [{'event': 'delivered', 'recipient': r, 'message': {'headers': {'message-id': 'test'}}} for r in b.RECIPIENTS]
        with patch.object(b, 'mailgun', return_value={'items': events[:1]}):
            self.assertEqual(b.verify('2026-09-21')['state'], 'queued')
        with patch.object(b, 'mailgun', return_value={'items': events[1:]}):
            self.assertEqual(b.verify('2026-09-21')['state'], 'delivered')

if __name__ == '__main__': unittest.main()
