import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).parents[1] / 'assets/codex-session/rtb-delivery.py'
spec = importlib.util.spec_from_file_location('rtb_delivery', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_scope_and_artifact_hash_are_checked_before_delivery(self):
        artifacts = {}
        for name in module.DRAFTS:
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            path.write_text('A prepared review file for Michael.')
            artifacts[name] = module.digest(path.read_bytes())
        receipt = {'artifacts': artifacts}
        self.assertEqual(set(module.artifact_files(receipt, self.root)), module.DRAFTS)
        (self.root / 'drafts/handbook-review.md').write_text('Changed after approval')
        with self.assertRaises(ValueError):
            module.artifact_files(receipt, self.root)
        artifacts['other-client.md'] = 'a' * 64
        with self.assertRaises(ValueError):
            module.artifact_files(receipt, self.root)

    def test_drive_delivery_requires_byte_exact_readback(self):
        path = self.root / 'draft.md'
        path.write_text('Exact draft')
        calls = []
        def run(args):
            calls.append(args)
            if args[1] == 'cat':
                return b'Changed draft'
            return b''
        with self.assertRaises(ValueError):
            module.drive_file(path, 'rtb-2212824-v2-handbook-review.md', run)
        self.assertTrue(all(module.FOLDER in call for call in calls))
        self.assertIn('--immutable', calls[0])

    def test_source_branch_refuses_an_unregistered_request_before_git(self):
        with self.assertRaises(ValueError):
            module.source_branch('push-main', {}, {})

    def test_verified_delivery_has_actual_file_id_and_hash(self):
        path = self.root / 'draft.md'
        path.write_text('Exact draft')
        name = 'rtb-2212824-v2-handbook-review.md'
        def run(args):
            return (b'Exact draft' if args[1] == 'cat' else
                    json.dumps({'ID': 'verified_file_id', 'Name': name}).encode() if args[1] == 'lsjson' else b'')
        result = module.drive_file(path, name, run)
        self.assertEqual(result['file_id'], 'verified_file_id')
        self.assertEqual(result['sha256'], module.digest(b'Exact draft'))
        with self.assertRaises(ValueError):
            module.drive_file(path, '../other-client.md', run)

if __name__ == '__main__':
    unittest.main()
