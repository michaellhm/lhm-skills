import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'scripts/review_release.py'
spec = importlib.util.spec_from_file_location('review_release', MODULE)
r = importlib.util.module_from_spec(spec)
if MODULE.exists():
    spec.loader.exec_module(r)

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('src/pages/index.astro', '<h1>Home</h1>')
        self.config = {'schema_version': 1, 'client': 'Demo Clinic', 'pages': [], 'shared_dependencies': []}

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def proposal(self, release=None):
        return r.propose(self.root, self.config, release or {'id': 'round-1', 'questions': ['Is this accurate?']})

    def apply(self, proposal):
        return r.apply_proposal(self.root, proposal, {'approved': True, 'proposal_digest': proposal['digest'], 'operator': 'Reviewer', 'evidence': 'Approved in test'})

    def test_static_routes(self):
        self.write('src/pages/services/physio.md', '# Physio')
        self.write('src/pages/api/form.ts', 'endpoint')
        pages = r.inventory(self.root, self.config)['pages']
        self.assertEqual([p['route'] for p in pages], ['/', '/services/physio/'])

    def test_dynamic_routes_report_gap(self):
        self.write('src/pages/services/[slug].astro', 'dynamic')
        self.assertTrue(r.inventory(self.root, self.config)['gaps'])

    def test_mapped_dynamic_routes(self):
        self.write('src/pages/services/[slug].astro', 'template')
        self.write('src/content/services/physio.md', '# Physio')
        self.config['pages'] = [{'id': 'physio', 'route': '/services/physio/', 'sources': ['src/content/services/physio.md'], 'dependencies': ['src/pages/services/[slug].astro']}]
        self.config['resolved_dynamic_routes'] = ['src/pages/services/[slug].astro']
        inv = r.inventory(self.root, self.config)
        self.assertFalse(inv['gaps'])
        self.assertEqual(len(inv['pages']), 2)

    def test_unapproved_apply_refused(self):
        with self.assertRaises(ValueError):
            r.apply_proposal(self.root, self.proposal(), {'approved': False})
        self.assertFalse((self.root / 'client-review.json').exists())

    def test_stale_proposal_refused(self):
        p = self.proposal()
        self.write('src/pages/index.astro', 'Changed after review')
        with self.assertRaises(ValueError):
            self.apply(p)

    def test_tampered_proposal_refused(self):
        p = self.proposal()
        p['release']['questions'] = ['Different question']
        with self.assertRaises(ValueError):
            self.apply(p)

    def test_repeat_release_idempotent(self):
        p = self.proposal()
        first = self.apply(p)
        second = self.apply(p)
        self.assertEqual(first, second)
        self.assertEqual(len(first['releases']), 1)

    def approve_home(self):
        reg = self.apply(self.proposal())
        home = reg['pages'][0]
        return r.record_review(self.root, home['id'], 'approved', 'Client', 'Explicit client approval', {'Is this accurate?': 'Yes'})

    def test_changed_approved_page_reopens(self):
        self.approve_home()
        self.write('src/pages/index.astro', 'New wording')
        reg = self.apply(self.proposal({'id': 'round-2'}))
        self.assertEqual(reg['pages'][0]['status'], 'awaiting-review')
        self.assertTrue(reg['pages'][0]['approval_history'])

    def test_unrelated_change_keeps_approval(self):
        self.approve_home()
        self.write('notes.txt', 'Unrelated')
        self.assertEqual(self.proposal({'id': 'round-2'})['selected'], [])

    def test_shared_dependency_change(self):
        self.write('src/layouts/Base.astro', 'layout')
        self.config['shared_dependencies'] = ['src/layouts/Base.astro']
        self.approve_home()
        self.write('src/layouts/Base.astro', 'changed layout')
        self.assertEqual(len(self.proposal({'id': 'round-2'})['selected']), 1)

    def test_pending_old_pages_preserved(self):
        self.apply(self.proposal())
        self.write('src/pages/services/new.astro', 'New service')
        reg = self.apply(self.proposal({'id': 'round-2', 'routes': ['/services/new/']}))
        self.assertEqual(len(reg['pages']), 2)
        self.assertEqual(reg['pages'][0]['status'], 'awaiting-review')

    def test_exclusions_visible(self):
        p = self.proposal({'id': 'round-1', 'exclude': ['/']})
        self.assertEqual(p['selected'], [])
        self.assertEqual(p['excluded'][0]['route'], '/')

    def test_deleted_page_visible(self):
        self.apply(self.proposal())
        (self.root / 'src/pages/index.astro').unlink()
        p = self.proposal({'id': 'round-2'})
        self.assertEqual(len(p['removed']), 1)

    def test_question_change_reopens_review(self):
        self.approve_home()
        p = self.proposal({'id': 'round-2', 'questions': ['Does the new wording fit?']})
        self.assertEqual(len(p['selected']), 1)
        self.assertEqual(self.apply(p)['pages'][0]['status'], 'awaiting-review')

    def test_pending_disposition_preserved_on_refresh(self):
        reg = self.apply(self.proposal())
        r.record_review(self.root, reg['pages'][0]['id'], 'needs-lhm', 'Client', 'Please check the pricing', {})
        reg = self.apply(self.proposal({'id': 'round-2'}))
        self.assertEqual(reg['pages'][0]['status'], 'needs-lhm')
        self.assertEqual(reg['pages'][0]['decision']['evidence'], 'Please check the pricing')

    def test_verified_config_replaces_installed_example(self):
        self.write('.lhm-review/client-config.json', json.dumps({'client': 'Example'}))
        self.apply(self.proposal())
        actual = json.loads((self.root / '.lhm-review/client-config.json').read_text())
        self.assertEqual(actual, self.config)

    def test_restored_page_can_be_reviewed_again(self):
        reg = self.apply(self.proposal())
        original = (self.root / 'src/pages/index.astro').read_text()
        (self.root / 'src/pages/index.astro').unlink()
        self.apply(self.proposal({'id': 'deleted'}))
        self.write('src/pages/index.astro', original)
        reg = self.apply(self.proposal({'id': 'restored'}))
        self.assertEqual(reg['pages'][0]['status'], 'awaiting-review')
        self.approve_home_after_restore(reg)

    def approve_home_after_restore(self, reg):
        r.record_review(self.root, reg['pages'][0]['id'], 'approved', 'Client', 'Restored page approved', {'Is this accurate?': 'Yes'})

    def test_path_escape_refused(self):
        self.config['shared_dependencies'] = ['../secret.txt']
        with self.assertRaises(ValueError):
            self.proposal()

    def test_symlink_escape_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / 'secret.md'
            secret.write_text('private')
            (self.root / 'src/pages/leak.md').symlink_to(secret)
            with self.assertRaises(ValueError):
                self.proposal()

    def test_explicit_review_and_answers(self):
        reg = self.approve_home()
        self.assertEqual(reg['pages'][0]['status'], 'approved')
        self.assertEqual(reg['pages'][0]['answers']['Is this accurate?'], 'Yes')
        self.assertIn('[x]', (self.root / 'CLIENT-REVIEW.md').read_text())

    def test_changed_content_cannot_approve_stale_page(self):
        reg = self.apply(self.proposal())
        self.write('src/pages/index.astro', 'changed locally')
        with self.assertRaises(ValueError):
            r.record_review(self.root, reg['pages'][0]['id'], 'approved', 'Client', 'yes', {})

    def test_concurrent_register_refused(self):
        p = self.proposal()
        self.write('client-review.json', json.dumps({'schema_version': 1, 'pages': [], 'releases': [], 'new': 'other session'}))
        with self.assertRaises(ValueError):
            self.apply(p)

    def test_duplicate_routes_refused(self):
        self.write('src/pages/index.md', '# duplicate route')
        with self.assertRaises(ValueError):
            self.proposal()

    def test_specific_fifteen_page_release(self):
        routes = []
        for n in range(15):
            self.write(f'src/pages/services/service-{n}.md', f'# Service{n}')
            routes.append(f'/services/service-{n}/')
        p = self.proposal({'id': 'services', 'routes': routes})
        self.assertEqual(len(p['selected']), 15)
        self.assertEqual(len(p['out_of_scope']), 1)


class InstallationTests(unittest.TestCase):
    def test_install_preserves_readme_and_existing_instructions(self):
        from importlib.util import spec_from_file_location, module_from_spec
        path = MODULE.parent / 'install_kit.py'
        self.assertTrue(path.exists(), 'installer must exist')
        s = spec_from_file_location('install_kit', path)
        mod = module_from_spec(s)
        s.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('# Existing website\nKeep me.\n')
            (root / 'AGENTS.md').write_text('Existing instructions')
            mod.install(root, 'explicit operator approval')
            self.assertIn('Keep me.', (root / 'README.md').read_text())
            self.assertEqual((root / 'AGENTS.md').read_text(), 'Existing instructions')
            self.assertTrue((root / '.agents/skills/review-website/SKILL.md').exists())
            self.assertEqual((root / '.agents/skills/review-website/SKILL.md').read_bytes(), (root / '.claude/skills/review-website/SKILL.md').read_bytes())
            mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'README.md').read_text().count('<!-- LHM-REVIEW:START -->'), 1)

    def test_install_conflict_has_no_partial_write(self):
        path = MODULE.parent / 'install_kit.py'
        self.assertTrue(path.exists(), 'installer must exist')
        s = importlib.util.spec_from_file_location('install_kit', path)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = root / '.claude/skills/review-website/SKILL.md'
            p.parent.mkdir(parents=True)
            p.write_text('Client custom skill')
            with self.assertRaises(ValueError):
                mod.install(root, 'explicit operator approval')
            self.assertFalse((root / 'README.md').exists())
            self.assertEqual(p.read_text(), 'Client custom skill')

class CliTests(unittest.TestCase):
    def test_managed_output_refused_before_mutation(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'src/pages').mkdir(parents=True)
            (root / 'src/pages/index.astro').write_text('Home')
            p = r.propose(root, {'schema_version': 1, 'client': 'Demo', 'pages': []}, {'id': 'first'})
            (root / 'proposal.json').write_text(json.dumps(p))
            (root / 'approval.json').write_text(json.dumps({'approved': True, 'proposal_digest': p['digest'], 'operator': 'Test', 'evidence': 'test'}))
            result = subprocess.run(['python3', str(MODULE), 'apply', '--root', str(root), '--proposal', str(root / 'proposal.json'), '--approval', str(root / 'approval.json'), '--output', str(root / 'client-review.json')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / 'client-review.json').exists())

if __name__ == '__main__':
    unittest.main()
