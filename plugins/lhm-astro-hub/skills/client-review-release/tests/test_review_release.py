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
        self.write('site/src/pages/index.astro', '<h1>Home</h1>')
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
        self.write('site/src/pages/services/physio.md', '# Physio')
        self.write('site/src/pages/api/form.ts', 'endpoint')
        pages = r.inventory(self.root, self.config)['pages']
        self.assertEqual([p['route'] for p in pages], ['/', '/services/physio/'])

    def test_dynamic_routes_report_gap(self):
        self.write('site/src/pages/services/[slug].astro', 'dynamic')
        self.assertTrue(r.inventory(self.root, self.config)['gaps'])

    def test_mapped_dynamic_routes(self):
        self.write('site/src/pages/services/[slug].astro', 'template')
        self.write('site/src/content/services/physio.md', '# Physio')
        self.config['pages'] = [{'id': 'physio', 'route': '/services/physio/', 'sources': ['site/src/content/services/physio.md'], 'dependencies': ['site/src/pages/services/[slug].astro']}]
        self.config['resolved_dynamic_routes'] = ['site/src/pages/services/[slug].astro']
        inv = r.inventory(self.root, self.config)
        self.assertFalse(inv['gaps'])
        self.assertEqual(len(inv['pages']), 2)

    def test_unapproved_apply_refused(self):
        with self.assertRaises(ValueError):
            r.apply_proposal(self.root, self.proposal(), {'approved': False})
        self.assertFalse((self.root / '.lhm-review/client-review.json').exists())

    def test_stale_proposal_refused(self):
        p = self.proposal()
        self.write('site/src/pages/index.astro', 'Changed after review')
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
        self.write('site/src/pages/index.astro', 'New wording')
        reg = self.apply(self.proposal({'id': 'round-2'}))
        self.assertEqual(reg['pages'][0]['status'], 'awaiting-review')
        self.assertTrue(reg['pages'][0]['approval_history'])

    def test_unrelated_change_keeps_approval(self):
        self.approve_home()
        self.write('notes.txt', 'Unrelated')
        self.assertEqual(self.proposal({'id': 'round-2'})['selected'], [])

    def test_shared_dependency_change(self):
        self.write('site/src/layouts/Base.astro', 'layout')
        self.config['shared_dependencies'] = ['site/src/layouts/Base.astro']
        self.approve_home()
        self.write('site/src/layouts/Base.astro', 'changed layout')
        self.assertEqual(len(self.proposal({'id': 'round-2'})['selected']), 1)

    def test_pending_old_pages_preserved(self):
        self.apply(self.proposal())
        self.write('site/src/pages/services/new.astro', 'New service')
        reg = self.apply(self.proposal({'id': 'round-2', 'routes': ['/services/new/']}))
        self.assertEqual(len(reg['pages']), 2)
        self.assertEqual(reg['pages'][0]['status'], 'awaiting-review')

    def test_exclusions_visible(self):
        p = self.proposal({'id': 'round-1', 'exclude': ['/']})
        self.assertEqual(p['selected'], [])
        self.assertEqual(p['excluded'][0]['route'], '/')

    def test_deleted_page_visible(self):
        self.apply(self.proposal())
        (self.root / 'site/src/pages/index.astro').unlink()
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

    def test_client_identity_round_trips(self):
        self.write('.lhm-review/client-config.json', json.dumps({'client': 'Example'}))
        self.config['client_identity'] = {'github_login': 'client-user', 'commit_emails': ['1+client-user@users.noreply.github.com']}
        self.apply(self.proposal())
        reg = json.loads((self.root / '.lhm-review/client-review.json').read_text())
        installed = json.loads((self.root / '.lhm-review/client-config.json').read_text())
        self.assertEqual(reg['config']['client_identity'], self.config['client_identity'])
        self.assertEqual(installed['client_identity'], self.config['client_identity'])

    def test_restored_page_can_be_reviewed_again(self):
        reg = self.apply(self.proposal())
        original = (self.root / 'site/src/pages/index.astro').read_text()
        (self.root / 'site/src/pages/index.astro').unlink()
        self.apply(self.proposal({'id': 'deleted'}))
        self.write('site/src/pages/index.astro', original)
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
            (self.root / 'site/src/pages/leak.md').symlink_to(secret)
            with self.assertRaises(ValueError):
                self.proposal()

    def test_explicit_review_and_answers(self):
        reg = self.approve_home()
        self.assertEqual(reg['pages'][0]['status'], 'approved')
        self.assertEqual(reg['pages'][0]['answers']['Is this accurate?'], 'Yes')
        self.assertIn('[x]', (self.root / 'brain/Project.md').read_text())

    def test_changed_content_cannot_approve_stale_page(self):
        reg = self.apply(self.proposal())
        self.write('site/src/pages/index.astro', 'changed locally')
        with self.assertRaises(ValueError):
            r.record_review(self.root, reg['pages'][0]['id'], 'approved', 'Client', 'yes', {})

    def test_concurrent_register_refused(self):
        p = self.proposal()
        self.write('.lhm-review/client-review.json', json.dumps({'schema_version': 1, 'pages': [], 'releases': [], 'new': 'other session'}))
        with self.assertRaises(ValueError):
            self.apply(p)

    def test_duplicate_routes_refused(self):
        self.write('site/src/pages/index.md', '# duplicate route')
        with self.assertRaises(ValueError):
            self.proposal()

    def test_specific_fifteen_page_release(self):
        routes = []
        for n in range(15):
            self.write(f'site/src/pages/services/service-{n}.md', f'# Service{n}')
            routes.append(f'/services/service-{n}/')
        p = self.proposal({'id': 'services', 'routes': routes})
        self.assertEqual(len(p['selected']), 15)
        self.assertEqual(len(p['out_of_scope']), 1)

    def test_project_grouped_by_round(self):
        self.apply(self.proposal({'id': 'round-1', 'questions': []}))
        self.write('site/src/pages/services/new.astro', 'New service')
        self.apply(self.proposal({'id': 'round-2', 'routes': ['/services/new/'], 'questions': []}))
        text = (self.root / 'brain/Project.md').read_text()
        self.assertTrue(text.startswith('---\ntype: project\n'))
        self.assertIn('client: "Demo Clinic"', text)
        self.assertIn('sources: []', text)
        first, second = text.index('## Round round-1'), text.index('## Round round-2')
        self.assertLess(first, second)
        self.assertIn('- [ ] / \u2014 awaiting client review', text[first:second])
        self.assertNotIn('/services/new/', text[first:second])
        self.assertIn('- [ ] /services/new/ \u2014 awaiting client review', text[second:])

    def test_project_marks_approved_pages(self):
        self.approve_home()
        self.assertIn('- [x] / \u2014 approved', (self.root / 'brain/Project.md').read_text())

    def test_render_project_without_client_has_empty_client(self):
        text = r.render_project({'pages': [], 'releases': []})
        self.assertIn('\nclient: ""\n', text)
        self.assertIn('updated: ', text)

    def test_conservative_coverage_hashes_site_src(self):
        self.approve_home()
        self.write('site/src/components/Card.astro', 'card')
        self.assertEqual(len(self.proposal({'id': 'round-2'})['selected']), 1)
        self.assertEqual(self.proposal({'id': 'round-2'})['inventory']['dependency_policy'], 'conservative-all-site-src')

    def test_save_creates_client_config_when_missing(self):
        self.config['client_identity'] = {'github_login': 'client-user', 'commit_emails': ['1+client-user@users.noreply.github.com']}
        self.assertFalse((self.root / '.lhm-review/client-config.json').exists())
        self.apply(self.proposal())
        installed = json.loads((self.root / '.lhm-review/client-config.json').read_text())
        self.assertEqual(installed, self.config)
        self.assertEqual(installed['client_identity']['github_login'], 'client-user')

    def verified_site(self):
        self.write('site/src/layouts/Base.astro', 'layout')
        self.write('site/src/components/Card.astro', 'card')
        self.write('site/src/components/Hero.astro', 'hero')
        self.write('site/src/pages/about.astro', 'About')
        self.write('site/src/pages/admin/index.astro', 'Admin')
        self.write('site/src/pages/thank-you.astro', 'Thanks')
        self.config['dependency_mapping_verified'] = True
        self.config['pages'] = [
            {'id': 'home', 'route': '/', 'sources': ['site/src/pages/index.astro'],
             'dependencies': ['site/src/layouts/Base.astro', 'site/src/components/Hero.astro']},
            {'id': 'about', 'route': '/about/', 'sources': ['site/src/pages/about.astro'],
             'dependencies': ['site/src/layouts/Base.astro']},
        ]
        exclude = ['/admin/', '/thank-you/']
        reg = self.apply(self.proposal({'id': 'round-1', 'questions': [], 'routes': ['/', '/about/'], 'exclude': exclude}))
        for page_id in ['home', 'about']:
            r.record_review(self.root, page_id, 'approved', 'Client', 'Explicit client approval', {})
        # Round 2 adds one new page that uses its own component.
        self.write('site/src/pages/services/new.astro', 'New service')
        self.config['pages'].append({'id': 'new', 'route': '/services/new/', 'sources': ['site/src/pages/services/new.astro'],
                                     'dependencies': ['site/src/layouts/Base.astro', 'site/src/components/Card.astro']})
        self.write('site/src/components/Card.astro', 'card used by the new page')
        return {'id': 'round-2', 'questions': [], 'routes': ['/services/new/'], 'exclude': exclude}

    def statuses(self, reg):
        return {p['id']: p['status'] for p in reg['pages']}

    def test_verified_mapping_round_two_keeps_round_one_approvals(self):
        release = self.verified_site()
        p = self.proposal(release)
        self.assertEqual(p['inventory']['dependency_policy'], 'verified')
        self.assertEqual([x['route'] for x in p['selected']], ['/services/new/'])
        self.assertEqual(sorted(x['route'] for x in p['excluded']), ['/admin/', '/thank-you/'])
        reg = self.apply(p)
        status = self.statuses(reg)
        self.assertEqual(status['home'], 'approved')
        self.assertEqual(status['about'], 'approved')
        self.assertEqual(status['new'], 'awaiting-review')
        self.assertNotIn('/admin/', [x['route'] for x in reg['pages']])
        self.assertIn('- [x] / \u2014 approved', (self.root / 'brain/Project.md').read_text())

    def test_verified_mapping_shared_layout_change_reopens_dependants(self):
        release = self.verified_site()
        self.write('site/src/layouts/Base.astro', 'changed shared layout')
        reg = self.apply(self.proposal(release))
        status = self.statuses(reg)
        self.assertEqual(status['home'], 'awaiting-review')
        self.assertEqual(status['about'], 'awaiting-review')
        home = next(x for x in reg['pages'] if x['id'] == 'home')
        self.assertTrue(home['approval_history'])
        self.assertNotIn('approval', home)

    def test_verified_mapping_unlisted_component_change_keeps_approval(self):
        release = self.verified_site()
        # Card.astro already changed, but only the new page lists it.
        reg = self.apply(self.proposal(release))
        self.assertEqual(self.statuses(reg)['about'], 'approved')
        self.write('site/src/components/Hero.astro', 'changed hero')
        self.assertEqual([x['route'] for x in self.proposal({'id': 'round-3', 'questions': [], 'exclude': ['/admin/', '/thank-you/']})['selected']], ['/', '/services/new/'])

    def test_lock_lives_in_lhm_review(self):
        with r.locked(self.root):
            self.assertTrue((self.root / '.lhm-review/review.lock').exists())
            self.assertFalse((self.root / '.client-review.lock').exists())
        self.assertFalse((self.root / '.lhm-review/review.lock').exists())
        self.assertFalse((self.root / '.lhm-review').exists())

    def test_lock_refuses_second_writer(self):
        with r.locked(self.root):
            with self.assertRaises(ValueError):
                with r.locked(self.root):
                    pass
        self.assertFalse((self.root / '.lhm-review').exists())

    def test_client_name_with_colon_is_quoted(self):
        text = r.render_project({'client': 'Smith: Physio "&" Co', 'pages': [], 'releases': []})
        self.assertIn('\nclient: "Smith: Physio \\"&\\" Co"\n', text)
        line = next(l for l in text.splitlines() if l.startswith('client: '))
        self.assertEqual(json.loads(line[len('client: '):]), 'Smith: Physio "&" Co')

    def test_register_lives_in_lhm_review(self):
        self.apply(self.proposal())
        self.assertTrue((self.root / '.lhm-review/client-review.json').exists())
        self.assertFalse((self.root / 'client-review.json').exists())


def load_installer():
    path = MODULE.parent / 'install_kit.py'
    s = importlib.util.spec_from_file_location('install_kit', path)
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod


class InstallationTests(unittest.TestCase):
    def test_install_canonical_skills_folder(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            mod.install(root, 'explicit operator approval')
            for name in ['start-website', 'review-website', 'share-preview', 'finish-review']:
                self.assertIn('name: ' + name, (root / f'skills/{name}/SKILL.md').read_text())
                for tool in ['.claude', '.agents']:
                    pointer = (root / f'{tool}/skills/{name}/SKILL.md').read_text()
                    self.assertIn(f'skills/{name}/SKILL.md', pointer)
                    self.assertLessEqual(len(pointer.splitlines()), 8)
            self.assertTrue((root / '.lhm-review/review_release.py').exists())

    def test_install_keeps_existing_project_md(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'brain').mkdir()
            original = '---\ntype: project\nclient: Demo\nupdated: 2026-01-01\nsources: []\n---\n\n# Project\n'
            (root / 'brain/Project.md').write_text(original)
            mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'brain/Project.md').read_text(), original)
            reg = {'schema_version': 1, 'pages': [], 'releases': []}
            (root / '.lhm-review/client-review.json').write_text(json.dumps(reg))
            r.save(root, {'client': 'Demo', 'config': {}, 'pages': [], 'releases': []})
            self.assertNotEqual((root / 'brain/Project.md').read_text(), original)

    def test_install_never_manages_readme(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('# Scaffolded\n')
            mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'README.md').read_text(), '# Scaffolded\n')
            self.assertNotIn('LHM-REVIEW', (root / 'README.md').read_text())

    def test_install_preserves_readme_and_existing_instructions(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'README.md').write_text('# Existing website\nKeep me.\n')
            (root / 'AGENTS.md').write_text('Existing instructions')
            mod.install(root, 'explicit operator approval')
            self.assertIn('Keep me.', (root / 'README.md').read_text())
            self.assertEqual((root / 'AGENTS.md').read_text(), 'Existing instructions')
            self.assertTrue((root / '.agents/skills/review-website/SKILL.md').exists())
            self.assertEqual((root / '.agents/skills/review-website/SKILL.md').read_bytes(), (root / '.claude/skills/review-website/SKILL.md').read_bytes())
            self.assertEqual((root / 'README.md').read_text(), '# Existing website\nKeep me.\n')
            mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'README.md').read_text(), '# Existing website\nKeep me.\n')

    def test_install_conflict_has_no_partial_write(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = root / '.claude/skills/review-website/SKILL.md'
            p.parent.mkdir(parents=True)
            p.write_text('Client custom skill')
            with self.assertRaises(ValueError):
                mod.install(root, 'explicit operator approval')
            self.assertFalse((root / 'skills').exists())
            self.assertFalse((root / '.lhm-review').exists())
            self.assertEqual(p.read_text(), 'Client custom skill')

    def test_install_appends_gemini_skill_list(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original = '# Demo\n\n- Read `README.md` first.\n'
            (root / 'GEMINI.md').write_text(original)
            mod.install(root, 'explicit operator approval')
            text = (root / 'GEMINI.md').read_text()
            self.assertTrue(text.startswith(original))
            for name in ['start-website', 'review-website', 'share-preview', 'finish-review']:
                self.assertIn(f'skills/{name}/SKILL.md', text)
            mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'GEMINI.md').read_text(), text)
            self.assertEqual(text.count(mod.GEMINI_START), 1)

    def test_install_creates_gemini_when_missing(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            mod.install(root, 'explicit operator approval')
            self.assertIn('skills/review-website/SKILL.md', (root / 'GEMINI.md').read_text())

    def test_install_refuses_edited_gemini_block(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'GEMINI.md').write_text('# Demo\n')
            mod.install(root, 'explicit operator approval')
            edited = (root / 'GEMINI.md').read_text().replace('review-website', 'my-review')
            (root / 'GEMINI.md').write_text(edited)
            manifest = (root / '.lhm-review/manifest.json').read_text()
            with self.assertRaises(ValueError):
                mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'GEMINI.md').read_text(), edited)
            self.assertEqual((root / '.lhm-review/manifest.json').read_text(), manifest)

    def test_install_conflict_leaves_gemini_untouched(self):
        mod = load_installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'GEMINI.md').write_text('# Demo\n')
            p = root / '.claude/skills/review-website/SKILL.md'
            p.parent.mkdir(parents=True)
            p.write_text('Client custom skill')
            with self.assertRaises(ValueError):
                mod.install(root, 'explicit operator approval')
            self.assertEqual((root / 'GEMINI.md').read_text(), '# Demo\n')

class CliTests(unittest.TestCase):
    def test_managed_output_refused_before_mutation(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'site/src/pages').mkdir(parents=True)
            (root / 'site/src/pages/index.astro').write_text('Home')
            p = r.propose(root, {'schema_version': 1, 'client': 'Demo', 'pages': []}, {'id': 'first'})
            (root / 'proposal.json').write_text(json.dumps(p))
            (root / 'approval.json').write_text(json.dumps({'approved': True, 'proposal_digest': p['digest'], 'operator': 'Test', 'evidence': 'test'}))
            result = subprocess.run(['python3', str(MODULE), 'apply', '--root', str(root), '--proposal', str(root / 'proposal.json'), '--approval', str(root / 'approval.json'), '--output', str(root / '.lhm-review/client-review.json')], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / '.lhm-review/client-review.json').exists())

if __name__ == '__main__':
    unittest.main()
