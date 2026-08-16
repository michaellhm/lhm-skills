import importlib.util
import tempfile
import unittest
import zipfile
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOYER = ROOT / 'assets/host/lhm-approved-plugin-deployer'
spec = importlib.util.spec_from_loader('deployer', SourceFileLoader('deployer', str(DEPLOYER)))
deployer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deployer)


class ArchiveSafetyTests(unittest.TestCase):
    def test_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('lhm-system-ops/../escape', 'bad')
            with self.assertRaisesRegex(ValueError, 'unsafe plugin archive path'):
                deployer.validate_archive(archive, root / 'stage')

    def test_wrong_plugin_prefix_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('another-plugin/SKILL.md', 'bad')
            with self.assertRaisesRegex(ValueError, 'unsafe plugin archive path'):
                deployer.validate_archive(archive, root / 'stage')

    def test_file_count_ceiling_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'large.zip'
            with zipfile.ZipFile(archive, 'w') as bundle:
                for index in range(251):
                    bundle.writestr(f'lhm-system-ops/assets/{index}.txt', 'x')
            with self.assertRaisesRegex(ValueError, 'exceeds size or file-count'):
                deployer.validate_archive(archive, root / 'stage')


if __name__ == '__main__':
    unittest.main()
