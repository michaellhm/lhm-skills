import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/local_bundle.py'
spec = importlib.util.spec_from_file_location('local_bundle', SCRIPT)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class LocalBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'interviews'
        self.pages = self.base / 'pages.json'
        self.pages.write_text(json.dumps([{'slug': 'children', 'title': 'Children'}]))

    def init(self):
        return bundle.initialise(self.root, self.pages)

    def test_resume_does_not_overwrite_answers(self):
        self.init()
        page = self.root / 'pages/children.md'
        page.write_text('Nicole’s saved answer')
        with self.assertRaises(ValueError):
            self.init()
        self.assertEqual(page.read_text(), 'Nicole’s saved answer')

    def test_export_preserves_bytes_and_excludes_other_files(self):
        self.init()
        (self.root / 'pages/children.md').write_text('Partial answer — needs confirmation')
        (self.root / '.secret').write_text('do not export')
        (self.root / 'pages/unlisted.md').write_text('do not export')
        output = bundle.export_bundle(self.root)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(set(archive.namelist()), {'support-page-interview/00-index.md', 'support-page-interview/pages/children.md'})
            self.assertEqual(archive.read('support-page-interview/pages/children.md'), (self.root / 'pages/children.md').read_bytes())

    def test_traversal_is_rejected_before_initialisation(self):
        self.pages.write_text(json.dumps([{'slug': '../elsewhere', 'title': 'Unsafe'}]))
        with self.assertRaises(ValueError):
            self.init()
        self.assertFalse(self.root.exists())

    def test_export_rejects_symlinks(self):
        self.init()
        page = self.root / 'pages/children.md'
        page.unlink()
        page.symlink_to(self.pages)
        with self.assertRaises(ValueError):
            bundle.export_bundle(self.root)

    def test_export_rejects_missing_indexed_page(self):
        self.init()
        (self.root / 'pages/children.md').unlink()
        with self.assertRaises(ValueError):
            bundle.export_bundle(self.root)


if __name__ == '__main__':
    unittest.main()
