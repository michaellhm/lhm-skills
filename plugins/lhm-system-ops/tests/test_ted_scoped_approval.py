import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'assets/task-router'))
sys.path.insert(0, str(ROOT / 'scripts'))
from scoped_approval import admission_text
from patch_ted_scoped_approval import patch

EXACT = "Ted - This is all approved - except i don't approve the Melbourne Bid strategy changes, i will investigate it seperately. Send to Claude Please"


class ScopedApprovalTests(unittest.TestCase):
    def test_named_exclusion_is_admission_only(self):
        projected = admission_text(EXACT, 'claude')
        self.assertNotIn("don't", projected)
        self.assertIn('This is all approved', projected)
        self.assertIn('Send to Claude Please', projected)
        self.assertIn("don't approve the Melbourne Bid strategy changes", EXACT)

    def test_no_explicit_provider_does_not_relax_admission(self):
        self.assertEqual(admission_text(EXACT, None), EXACT)

    def test_global_refusals_and_control_commands_remain(self):
        for scope in ['anything', 'all changes', 'the work', 'this task',
                      'sending to Claude', 'the reroute to Codex',
                      'the stop command', 'any campaign changes',
                      'budget changes do not implement them', 'budget changes never execute']:
            text = "Send to Claude, except I don't approve " + scope + '.'
            with self.subTest(scope=scope):
                self.assertEqual(admission_text(text, 'claude'), text)

    def test_stop_outside_exception_is_preserved(self):
        text = EXACT + ' Stop. Do not proceed.'
        self.assertIn('Stop. Do not proceed.', admission_text(text, 'claude'))

    def test_negated_provider_is_preserved(self):
        text = "Don't send to Claude."
        self.assertEqual(admission_text(text, 'claude'), text)

    def test_curly_apostrophe(self):
        self.assertNotIn('don’t', admission_text(EXACT.replace("don't", 'don’t'), 'claude'))


class LiveRouterContractTests(unittest.TestCase):
    """Run with TED_ROUTER_SOURCE pointing to a read-only snapshot of the router."""
    @classmethod
    def setUpClass(cls):
        import os
        source = os.environ.get('TED_ROUTER_SOURCE')
        if not source:
            raise unittest.SkipTest('Set TED_ROUTER_SOURCE for deployed-router contract tests')
        cls.original = Path(source).read_text()
        cls.patched = patch(cls.original)
        cls.module = type(sys)('tested_router')
        cls.module.__file__ = source
        exec(compile(cls.patched, source, 'exec'), cls.module.__dict__)

    def contract(self, instruction=EXACT, author=36398, later_stop=False):
        import tempfile
        task = {'id': 2224639, 'url': 'https://app.basicops.com/task',
                'title': 'Dry Eye Solutions: Google Ads - Review', 'status': 'Accepted'}
        messages = [{'id': 'dm2699017', 'message': instruction, 'user': author, 'created': 1}]
        if later_stop:
            messages.append({'id': 'dm2699018', 'message': 'Stop', 'user': 36398, 'created': 2})
        replies = {'get_current_user': {'id': 82491}, 'get_task': task, 'list_messages_in_task': {'data': messages}}
        with tempfile.TemporaryDirectory() as directory:
            router = self.module.Router.__new__(self.module.Router)
            router.config = {'agent_user_id': 82491, 'reviewer_id': 36398,
                             'providers': {'claude': True},
                             'clients': {'dry-eye-solutions': {'name': 'Dry Eye Solutions'}}}
            router.state = Path(directory)
            router.check_freshness = lambda: None
            router.api = lambda action, payload: replies[action]
            return router.contract(2224639, 'dm2699017')[1]

    def test_exact_request_preserves_scope_and_approval_ceiling(self):
        request = self.contract()
        self.assertEqual(request['instruction'], EXACT)
        self.assertEqual(request['provider'], 'claude')
        self.assertEqual(request['handoff_mode'], 'provider_execution')
        self.assertEqual(request['permission_ceiling'], 'provider_tool_approval')
        self.assertEqual(request['instruction_message_id'], 'dm2699017')

    def test_rejects_global_stops_and_wrong_author(self):
        for text in ["Don't send to Claude", 'Stop. Send to Claude',
                     'Not approved. Send to Claude', EXACT + ' Hold.',
                     "Send to Claude except I don't approve anything."]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.contract(text)
        with self.assertRaises(ValueError):
            self.contract(author=123)
        with self.assertRaises(ValueError):
            self.contract(later_stop=True)

    def test_ai_authorship_is_checked_on_original(self):
        with self.assertRaises(ValueError):
            self.contract("Send to Claude except I don't approve AI authorship: drafted changes.")

    def test_patch_is_idempotent(self):
        self.assertEqual(patch(self.patched), self.patched)


if __name__ == '__main__':
    unittest.main()
