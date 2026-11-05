import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / 'skills/development-workspaces/scripts/rehearse_active_pin.py'
spec = importlib.util.spec_from_file_location('rehearsal', SOURCE)
rehearsal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rehearsal)


class RehearsalBoundaryTests(unittest.TestCase):
    def test_non_administrator_cannot_create_mounts(self):
        with patch.object(rehearsal.sys, 'platform', 'linux'), \
                patch.object(rehearsal.os, 'geteuid', return_value=1000), \
                patch.object(rehearsal.subprocess, 'run') as run:
            with self.assertRaises(RuntimeError):
                rehearsal.run('/mnt/example')
            run.assert_not_called()

    def test_unmounted_directory_is_rejected_without_changes(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(rehearsal.sys, 'platform', 'linux'), \
                patch.object(rehearsal.os, 'geteuid', return_value=0), \
                patch.object(rehearsal.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                rehearsal.run(tmp)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            run.assert_not_called()

    def test_main_filesystem_is_not_a_valid_destination(self):
        with patch.object(rehearsal.sys, 'platform', 'linux'), \
                patch.object(rehearsal.os, 'geteuid', return_value=0), \
                patch.object(rehearsal.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'different filesystem'):
                rehearsal.run('/')
            run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
