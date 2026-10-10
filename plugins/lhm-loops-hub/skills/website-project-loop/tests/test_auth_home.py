import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('shared_vault_auth',Path(__file__).parents[1]/'scripts/shared_vault.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class AuthHomeTests(unittest.TestCase):
    def test_profile_caller_uses_existing_auth_home_and_is_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            helper=Path(directory)/'google_api.py'
            helper.write_text('import os\ndef build_service(*args):return os.environ["HERMES_HOME"]\n')
            with patch.dict(os.environ,{'HERMES_HOME':'/opt/data/profiles/lhm_project_manager'}):
                self.assertEqual(m.drive_service({'google_api':str(helper)}),'/opt/data')
                self.assertEqual(os.environ['HERMES_HOME'],'/opt/data/profiles/lhm_project_manager')
    def test_failed_client_initialization_restores_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            helper=Path(directory)/'google_api.py';helper.write_text('def build_service(*args):raise ValueError("unavailable")\n')
            with patch.dict(os.environ,{'HERMES_HOME':'/opt/data/profiles/lhm_project_manager'}):
                with self.assertRaises(ValueError):m.drive_service({'google_api':str(helper)})
                self.assertEqual(os.environ['HERMES_HOME'],'/opt/data/profiles/lhm_project_manager')

if __name__=='__main__':unittest.main()
