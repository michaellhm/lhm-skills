import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/client_directory.py'
spec = importlib.util.spec_from_file_location('client_directory', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.vault = Path(self.tmp.name)
        self.root = self.vault / '20 Clients'
        self.root.mkdir()
        (self.root / 'Clients.md').write_text('[[20 Clients/Alpha Sports Med/Alpha Sports Med|Alpha]]')
        self.alpha = self.root / 'Alpha Sports Med'
        self.alpha.mkdir()
        (self.alpha / 'Alpha Sports Med.md').write_text('''---
type: client
aliases: [Alpha, Alpha Sports Medicine]
---
# Alpha Sports Med
## Systems and files
- https://drive.google.com/drive/folders/known-folder
- https://github.com/verified-org/alpha
## Other
Private irrelevant prose must not be exported.
''')
        (self.alpha / 'Current Projects.md').write_text('Current state')

    def test_exports_aliases_and_pointers_without_client_body(self):
        result = module.build(self.vault, {})
        alpha = result['clients']['alpha-sports-med']
        self.assertIn('Alpha', alpha['aliases'])
        self.assertEqual(alpha['canonical_overview'], '20 Clients/Alpha Sports Med/Alpha Sports Med.md')
        self.assertTrue(alpha['listed_in_index'])
        self.assertEqual(len(alpha['systems_links']), 2)
        self.assertNotIn('Private irrelevant prose', str(result))

    def test_keeps_verified_registration_and_work_folder(self):
        original = {'alpha-existing-id': {'name': 'Alpha Sports Medicine', 'vault_prefix': '20 Clients/Alpha Sports Med/',
                    'drive_folder_query': 'exact folder known', 'basicops_task_ids': ['12']}}
        result = module.build(self.vault, original)['clients']
        self.assertEqual(list(result), ['alpha-existing-id'])
        self.assertEqual(result['alpha-existing-id']['drive_folder_query'], 'exact folder known')
        self.assertNotIn('aliases', original['alpha-existing-id'])

    def test_includes_existing_website_clients_outside_retainer_table(self):
        folder = self.root / 'Website Client'
        folder.mkdir()
        (folder / 'Website Client.md').write_text('# Website Client\nExisting canonical overview')
        self.assertIn('website-client', module.build(self.vault, {})['clients'])

    def test_does_not_follow_symlinked_clients(self):
        (self.root / 'External').symlink_to(self.alpha, target_is_directory=True)
        self.assertNotIn('external', module.build(self.vault, {})['clients'])

    def test_rejects_missing_index_or_identifier_collision(self):
        with self.assertRaises(ValueError): module.build(self.vault, {'alpha-sports-med': {'name': 'Other', 'vault_prefix': '20 Clients/Other/'}})
        (self.root / 'Clients.md').unlink()
        with self.assertRaises(ValueError): module.build(self.vault, {})

    def test_archived_notes_do_not_auto_enroll_new_client(self):
        (self.alpha / 'Alpha Sports Med.md').write_text('---\nstatus: archived\n---\n# Alpha Sports Med')
        self.assertEqual(module.build(self.vault, {})['clients'], {})


if __name__ == '__main__': unittest.main()
