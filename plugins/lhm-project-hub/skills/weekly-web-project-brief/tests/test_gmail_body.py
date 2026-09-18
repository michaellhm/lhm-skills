import base64
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('gmail_body', Path(__file__).parents[1] / 'scripts/gmail_body.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

def part(mime, text, **extra):
    return {'mimeType': mime, 'body': {'data': base64.urlsafe_b64encode(text.encode()).decode().rstrip('=')}, **extra}

class GmailBodyTest(unittest.TestCase):
    def test_nested_thread_prefers_plain(self):
        msg = {'payload': {'mimeType': 'multipart/mixed', 'parts': [
            {'mimeType': 'multipart/alternative', 'parts': [part('text/plain', 'Approved — revised homepage feedback next.'), part('text/html', '<p>Approved</p>')]},
            part('text/plain', 'Unrelated attachment', filename='notes.txt')]}}
        self.assertEqual(g.extract_message_body(msg), 'Approved — revised homepage feedback next.')
    def test_html_only(self):
        self.assertEqual(g.extract_message_body({'payload': part('text/html', '<p>Feedback</p>')}), '<p>Feedback</p>')
    def test_empty_stays_empty(self):
        self.assertEqual(g.extract_message_body({'payload': {'mimeType': 'multipart/mixed'}}), '')

if __name__ == '__main__': unittest.main()
