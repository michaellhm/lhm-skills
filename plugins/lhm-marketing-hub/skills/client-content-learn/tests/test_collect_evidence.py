import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('collector', Path(__file__).parents[1] / 'scripts/collect_evidence.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.run_git('init', '-q')
        self.run_git('config', 'user.name', 'Test Agency')
        self.run_git('config', 'user.email', 'agency@example.org')
        (self.repo / 'copy.json').write_text('{"copy":"First draft"}')
        self.commit('agency baseline')
        self.base = self.run_git('rev-parse', 'HEAD').strip()
        (self.repo / 'copy.json').write_text('{"copy":"Client-approved wording"}')
        self.run_git('config', 'user.email', 'client@example.org')
        self.commit('client correction')
        self.approved = self.run_git('rev-parse', 'HEAD').strip()
        self.manifest = {'pages': [{'route':'/service/', 'approved_revision':self.approved,
                                   'approval_evidence':'Explicit client review event', 'sources':['copy.json']}]}

    def run_git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], text=True)

    def commit(self, message):
        self.run_git('add', 'copy.json')
        self.run_git('commit', '-qm', message)

    def collect(self, since=None):
        return m.collect(self.repo, self.manifest, since or self.base, 'HEAD', ['client@example.org'])

    def test_corpus_diff_and_idempotent_rerun(self):
        result = self.collect()
        self.assertEqual(result, self.collect())
        self.assertTrue(result['pages'][0]['eligible'])
        self.assertEqual(result['coverage']['candidate_content_commits'], 1)
        self.assertIn('-{"copy":"First draft"}', result['candidate_client_changes'][0]['patch'])
        self.assertIn('Client-approved wording', result['pages'][0]['sources'][0]['text'])
        self.assertEqual(self.collect(self.approved)['candidate_client_changes'], [])

    def test_new_unapproved_source_does_not_enter_corpus(self):
        (self.repo / 'copy.json').write_text('{"copy":"Later, not reviewed"}')
        self.commit('new edit')
        self.assertFalse(self.collect()['pages'][0]['eligible'])

    def test_dirty_sources_fail(self):
        (self.repo / 'copy.json').write_text('uncommitted')
        with self.assertRaises(ValueError): self.collect()

    def test_approval_and_path_validation(self):
        self.manifest['pages'][0]['approval_evidence'] = ''
        with self.assertRaises(ValueError): self.collect()
        for path in ['../private.md', '/etc/passwd', '.git/config', 'image.png']:
            with self.assertRaises(ValueError): m.safe_path(path)

    def test_agency_commit_is_not_client_attributed(self):
        self.run_git('config', 'user.email', 'agency@example.org')
        (self.repo / 'copy.json').write_text('{"copy":"Agency edit"}')
        self.commit('agency change')
        self.assertEqual(len(self.collect()['candidate_client_changes']), 1)


if __name__ == '__main__': unittest.main()
