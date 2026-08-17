import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'assets/host/cto-dispatch'
spec = importlib.util.spec_from_loader('cto_dispatch', SourceFileLoader('cto_dispatch', str(HELPER)))
cto_dispatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cto_dispatch)


class StatusTests(unittest.TestCase):
    def status(self, request_id):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cto_dispatch.status(argparse.Namespace(request_id=request_id))
        return json.loads(output.getvalue())

    def test_failed_request_wins_over_partial_run_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            cto_dispatch.BASE = Path(temporary)
            for name in ('failed', 'runs', 'incoming'):
                (cto_dispatch.BASE / name).mkdir()
            request_id = 'test-001'
            (cto_dispatch.BASE / 'runs' / request_id).mkdir()
            (cto_dispatch.BASE / 'failed' / f'{request_id}.json').write_text('{}\n')
            (cto_dispatch.BASE / 'failed' / f'{request_id}.error').write_text('Not logged in\n')
            self.assertEqual(
                self.status(request_id),
                {'request_id': request_id, 'status': 'rejected', 'reason': 'Not logged in'},
            )

    def test_inaccessible_partial_run_does_not_crash_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            cto_dispatch.BASE = Path(temporary)
            for name in ('failed', 'runs', 'incoming'):
                (cto_dispatch.BASE / name).mkdir()
            original = Path.is_file

            def guarded(path):
                if 'runs' in path.parts:
                    raise PermissionError('simulated')
                return original(path)

            with mock.patch.object(Path, 'is_file', guarded):
                self.assertEqual(self.status('test-002'), {'request_id': 'test-002', 'status': 'unknown'})


if __name__ == '__main__':
    unittest.main()
