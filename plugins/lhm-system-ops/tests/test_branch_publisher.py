import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'assets/host/lhm-cto-branch-publisher'
spec = importlib.util.spec_from_loader('branch_publisher', SourceFileLoader('branch_publisher', str(HELPER)))
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def request(branch='cto/incident-001-fix'):
    return {
        'schema_version': 1,
        'request_id': 'request-001',
        'parent_run_id': 'parent-001',
        'capability_incident_id': 'incident-001',
        'branch': branch,
        'summary': 'Bounded change',
        'reported_changed_files': ['plugins/lhm-system-ops/skills/lhm-cto/SKILL.md'],
        'tests': ['validator passed'],
        'qa': 'passed',
        'security': 'passed',
    }


class PublisherBoundaryTests(unittest.TestCase):
    def test_changed_paths_preserves_first_porcelain_status_prefix(self):
        output = (
            ' M .claude-plugin/marketplace.json\0'
            ' M plugins/lhm-project-hub/.claude-plugin/plugin.json\0'
        )
        with mock.patch.object(publisher, 'run', return_value=output):
            self.assertEqual(
                publisher.changed_paths(Path('/bounded/workspace')),
                [
                    '.claude-plugin/marketplace.json',
                    'plugins/lhm-project-hub/.claude-plugin/plugin.json',
                ],
            )

    def test_accepts_generated_cto_branch(self):
        publisher.validate_request(request())

    def test_rejects_main(self):
        with self.assertRaisesRegex(ValueError, 'cto feature branches'):
            publisher.validate_request(request('main'))

    def test_rejects_path_escape_and_credentials(self):
        self.assertFalse(publisher.allowed_path('../secrets'))
        self.assertFalse(publisher.allowed_path('/etc/passwd'))
        self.assertTrue(publisher.allowed_path('plugins/lhm-system-ops/SKILL.md'))

    def test_missing_credential_fails_before_push(self):
        with tempfile.TemporaryDirectory() as temporary:
            publisher.SSH_KEY = Path(temporary) / 'missing-key'
            publisher.KNOWN_HOSTS = Path(temporary) / 'missing-hosts'
            with self.assertRaisesRegex(ValueError, 'credential is not configured'):
                publisher.push_and_verify(Path(temporary), 'cto/incident-001-fix', 'a' * 40)

    def test_review_note_contains_human_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            publisher.REVIEWS = Path(temporary)
            with mock.patch.object(publisher.os, 'chown'):
                note = publisher.write_review(
                    request(), 'a' * 40,
                    ['plugins/lhm-system-ops/skills/lhm-cto/SKILL.md'],
                )
            text = note.read_text()
            self.assertIn('status: needs-michael-review', text)
            self.assertIn('It did not push `main`, merge, release or deploy', text)
            self.assertIn('GitHub comparison', text)


if __name__ == '__main__':
    unittest.main()
