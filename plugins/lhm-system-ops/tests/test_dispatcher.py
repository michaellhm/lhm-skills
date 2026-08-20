import importlib.util
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
DISPATCHER = ROOT / 'assets/host/lhm-cto-plugin-dispatcher'
spec = importlib.util.spec_from_loader('cto_dispatcher', SourceFileLoader('cto_dispatcher', str(DISPATCHER)))
cto_dispatcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cto_dispatcher)


class FailureReasonTests(unittest.TestCase):
    def test_subprocess_stderr_is_preserved(self):
        error = subprocess.CalledProcessError(1, ['codex'], stderr='schema permission denied')
        self.assertEqual(cto_dispatcher.failure_reason(error), 'schema permission denied')

    def test_generic_error_is_preserved(self):
        self.assertEqual(cto_dispatcher.failure_reason(ValueError('bad request')), 'bad request')

    def test_second_iteration_accepts_bounded_chief_answers(self):
        request = {
            'schema_version': 1, 'request_id': 'request-002', 'parent_run_id': 'parent-001',
            'capability_incident_id': 'incident-001', 'objective': 'Continue research',
            'acceptance_tests': ['Verify evidence'], 'mode': 'research',
            'timeout_seconds': 600, 'return_point': 'Return to Chief',
            'resume_token': 'resume-token-0001', 'iteration': 2, 'max_iterations': 3,
            'prior_request_id': 'request-001',
            'chief_answers': ['Aiya profile confirms project 49049 and Inbox 80530.'],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'request-002.json'
            cto_dispatcher.validate(request, path)

    def test_iteration_above_ceiling_is_rejected(self):
        request = {
            'schema_version': 1, 'request_id': 'request-004', 'parent_run_id': 'parent-001',
            'capability_incident_id': 'incident-001', 'objective': 'Continue research',
            'acceptance_tests': ['Verify evidence'], 'mode': 'research',
            'timeout_seconds': 600, 'return_point': 'Return to Chief',
            'resume_token': 'resume-token-0001', 'iteration': 4, 'max_iterations': 4,
            'prior_request_id': 'request-003', 'chief_answers': ['answer'],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'request-004.json'
            with self.assertRaisesRegex(ValueError, 'iteration'):
                cto_dispatcher.validate(request, path)

    def test_evidence_iterations_use_deterministic_distinct_branches(self):
        first = {'capability_incident_id': 'ASP-PROTO-PUBLISH-ROUTE-20260820'}
        second = {**first, 'iteration': 2}
        self.assertEqual(cto_dispatcher.change_branch(first), 'cto/asp-proto-publish-route-20260820')
        self.assertEqual(cto_dispatcher.change_branch(second), 'cto/asp-proto-publish-route-20260820-i2')

    def test_existing_exact_workspace_is_reused_without_deletion(self):
        request = {'request_id': 'request-002', 'capability_incident_id': 'incident-001', 'iteration': 2}
        with tempfile.TemporaryDirectory() as temporary:
            cto_dispatcher.WORKSPACES = Path(temporary)
            workspace = Path(temporary) / 'request-002'
            workspace.mkdir()
            completed = mock.Mock(stdout='cto/incident-001-i2\n')
            with mock.patch.object(cto_dispatcher, 'run_worker', return_value=completed) as worker:
                branch, selected = cto_dispatcher.prepare_change_workspace(request)
            self.assertEqual((branch, selected), ('cto/incident-001-i2', workspace))
            worker.assert_called_once()


if __name__ == '__main__':
    unittest.main()
