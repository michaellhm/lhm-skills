import hashlib
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).parents[1] / 'assets/host/lhm-codex-session-worker'
loader = importlib.machinery.SourceFileLoader('session_worker', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
worker = importlib.util.module_from_spec(spec)
loader.exec_module(worker)

class WorkerTests(unittest.TestCase):
    def test_original_review_remains_valid(self):
        worker.validate({'schema_version': 1, 'request_id': 'existing-review',
                         'client_id': 'wellness-chiropractic', 'task_type': 'context_review', 'title': 'Review'})

    def task(self):
        return {'schema_version': 1, 'request_id': 'ted-codex-123-v1',
                'client_id': 'wellness-chiropractic', 'task_type': 'ted_task', 'title': 'Review',
                'objective': 'Approved saved-context review-only brief.',
                'basicops': {'task_id': 123, 'task_url': 'https://app.basicops.com/task',
                  'plan_version': 1, 'plan_message_id': 'plan', 'approval_message_id': 'approval',
                  'plan_sha256': 'a' * 64, 'approval_sha256': 'b' * 64,
                  'objective_sha256': hashlib.sha256(b'Approved saved-context review-only brief.').hexdigest(),
                  'reviewer_id': 30, 'project_id': 10}}

    def test_objective_and_request_identity_are_bound(self):
        task = self.task()
        worker.validate(task)
        task['objective'] += ' Added scope.'
        with self.assertRaises(ValueError):
            worker.validate(task)
        task = self.task()
        task['request_id'] = 'ted-codex-124-v1'
        with self.assertRaises(ValueError):
            worker.validate(task)

    def test_other_client_and_extra_fields_fail_closed(self):
        task = self.task()
        task['client_id'] = 'other-client'
        with self.assertRaises(ValueError):
            worker.validate(task)
        task = self.task()
        task['basicops']['shell'] = 'anything'
        with self.assertRaises(ValueError):
            worker.validate(task)

if __name__ == '__main__':
    unittest.main()
