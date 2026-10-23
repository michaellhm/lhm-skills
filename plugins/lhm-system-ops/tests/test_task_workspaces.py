import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/workspaces.py'
spec = importlib.util.spec_from_file_location('workspaces', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkspaceTests(unittest.TestCase):
    def test_stable_identity_and_preserved_pilots(self):
        self.assertEqual(module.location('codex', 'alpha-sports-med'), module.ROOT / 'codex/alpha-sports-med')
        self.assertEqual(module.location('codex', 'raise-the-bar'), Path('/home/codexworker/clients/raise-the-bar'))
        self.assertNotEqual(module.location('codex', 'alpha-sports-med'), module.location('claude', 'alpha-sports-med'))
        for provider, client in [('bash', 'alpha'), ('codex', '../other'), ('claude', '/tmp/x'), ('codex', 'alpha;id')]:
            with self.assertRaises(ValueError): module.location(provider, client)

    def test_tasks_reuse_root_without_overwriting_prior_drafts(self):
        import os
        with tempfile.TemporaryDirectory() as tmp, patch.object(module, 'ROOT', Path(tmp) / 'clients'), patch.object(module, 'LEGACY', {}), patch.object(module.os, 'chown'):
            # Ownership assertions use real metadata; mock only the root identity for this non-root fixture.
            real_stat = Path.stat
            def stat(path, *a, **kw):
                value = real_stat(path, *a, **kw)
                from types import SimpleNamespace
                return SimpleNamespace(st_uid=0, st_mode=value.st_mode, st_size=value.st_size)
            with patch.object(Path, 'stat', stat):
                request = {'provider':'codex','client_id':'alpha','client':{'name':'Alpha'},'request_id':'ted-route-1-dm1'}
                root, task = module.provision(request, 10001)
                (task / 'draft.md').write_text('keep this')
                request['request_id'] = 'ted-route-2-dm2'
                root2, task2 = module.provision(request, 10001)
                self.assertEqual(root, root2)
                self.assertNotEqual(task, task2)
                self.assertEqual((task / 'draft.md').read_text(), 'keep this')
                with self.assertRaises(FileExistsError): module.provision(request, 10001)
                self.assertIn(str(root), module.registry_text())
                self.assertNotIn('keep this', module.registry_text())
                (root / 'tasks').rename(root / 'saved-tasks')
                (root / 'tasks').symlink_to(root / 'saved-tasks', target_is_directory=True)
                request['request_id'] = 'ted-route-3-dm3'
                with self.assertRaises(ValueError): module.provision(request, 10001)

    def test_registry_never_overwrites_human_note_or_ignores_read_failure(self):
        from types import SimpleNamespace
        for reply in [SimpleNamespace(returncode=0, stdout='# My human note'), SimpleNamespace(returncode=1, stdout='')]:
            with patch.object(module, 'registry_text', return_value='# generated'), patch.object(module.subprocess, 'run', return_value=reply) as run:
                with self.assertRaises(ValueError): module.publish_registry()
                self.assertEqual(run.call_count, 1)

if __name__ == '__main__': unittest.main()
