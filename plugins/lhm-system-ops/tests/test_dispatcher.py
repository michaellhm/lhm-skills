import importlib.util
import subprocess
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


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


if __name__ == '__main__':
    unittest.main()
