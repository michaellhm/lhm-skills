import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('route',Path(__file__).parents[1]/'scripts/completion_route.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class RouteTests(unittest.TestCase):
    def test_exact_command_from_html(self):
        r=m.parse('<p>@<span>Lily</span> website done: TEST-1 | evidence: https://example.com/test | next: Kristalyn reviews the homepage</p>')
        self.assertEqual(r,{'item':'TEST-1','evidence':'https://example.com/test','next_action':'Kristalyn reviews the homepage'})
    def test_general_chat_not_captured(self):
        self.assertIsNone(m.parse('What is next on the website?'))
    def test_missing_evidence_not_captured(self):
        self.assertIsNone(m.parse('website done: TEST-1'))
    def test_next_action_stops_at_paragraph_boundary(self):
        r=m.parse('<p>website done: TEST-1 | evidence: https://example.com/test | next: Kristalyn reviews the homepage</p><p>Internal test notes.</p>')
        self.assertEqual(r['next_action'],'Kristalyn reviews the homepage')

if __name__=='__main__':unittest.main()
