import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock

SOURCE = Path(__file__).resolve().parents[1] / 'assets/task-router/site_workspace.py'
spec = importlib.util.spec_from_file_location('site_workspace', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def settings():
    return {'commit_name': 'Hermes', 'commit_email': 'hermes@example.invalid', 'sites': {'ysp': {'client_id': 'ysp', 'repository': 'lhmorg/your-story-physio',
        'default_branch': 'main', 'mode': 'build', 'deployment_verified': True,
        'authority_source': 'Human approval, 26 October'}},
        'github_app': {'client_id': 'app', 'installation_id': 123, 'private_key': '/host-only/key'}}


class WebsiteTests(unittest.TestCase):
    def test_repository_lock_excludes_other_provider_and_alias_and_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with m.lease('lhmorg/your-story-physio', {'provider': 'claude'}, root):
                with self.assertRaisesRegex(ValueError, 'Website busy'):
                    with m.lease('LHMORG/YOUR-STORY-PHYSIO', {'provider': 'codex'}, root):
                        self.fail('Another provider acquired the same repository')
                with m.lease('lhmorg/different-site', {'provider': 'codex'}, root):
                    pass
            with m.lease('lhmorg/your-story-physio', {'provider': 'codex'}, root):
                pass

    def test_explicit_mode_and_deployment_authority_are_required(self):
        for field, bad in [('mode', 'production'), ('deployment_verified', False), ('authority_source', ''), ('repository', '../other')]:
            s = settings(); s['sites']['ysp'][field] = bad
            with self.assertRaises(ValueError): m.site_for({'client_id': 'ysp'}, s)
        with self.assertRaises(ValueError): m.site_for({'client_id': 'another-client'}, settings())

    def test_installation_token_is_scoped_to_one_repo_and_requested_permission(self):
        s = settings(); row = s['sites']['ysp']
        with patch.object(m, 'app_jwt', return_value='redacted'), patch.object(m, 'api', return_value={'token': 'ephemeral'}) as api:
            self.assertEqual(m.installation_token(s, row, True), 'ephemeral')
            payload = api.call_args.args[2]
            self.assertEqual(payload, {'repositories': ['your-story-physio'], 'permissions': {'contents': 'write', 'metadata': 'read'}})

    def test_clone_uses_worker_and_stores_no_token_in_remote_url(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'ROOT', Path(tmp)), patch.object(m.os, 'chown'), patch.object(m, 'installation_token', return_value='ephemeral'), patch.object(m, 'git') as git:
            repo = m.ensure_checkout(settings(), 'ysp', settings()['sites']['ysp'], 'claude')
            args = git.call_args.args
            self.assertEqual(repo, Path(tmp)/'ysp/repo')
            self.assertIn('https://github.com/lhmorg/your-story-physio.git', args[1])
            self.assertNotIn('ephemeral', ' '.join(args[1]))
            self.assertEqual(args[2], 'claude')

    def test_dirty_checkout_is_preserved_without_fetch_or_reset(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'ROOT', Path(tmp)), patch.object(m.os, 'chown'):
            repo = Path(tmp)/'ysp/repo'; (repo/'.git').mkdir(parents=True); (repo/'.git/HEAD').write_text('ref: refs/heads/main')
            (repo/'important.astro').write_text('unfinished work')
            def git(_repo, args, *_a, **_kw):
                return SimpleNamespace(stdout='https://github.com/lhmorg/your-story-physio.git\n' if args[0]=='remote' else ' M important.astro\n')
            with patch.object(m, 'git', side_effect=git) as mock, self.assertRaisesRegex(ValueError, 'uncommitted'):
                m.ensure_checkout(settings(), 'ysp', settings()['sites']['ysp'], 'claude')
            self.assertEqual((repo/'important.astro').read_text(), 'unfinished work')
            self.assertFalse(any(call.args[1][0] in {'fetch','reset','clean','stash'} for call in mock.call_args_list))

    def test_build_stays_main_live_creates_task_branch(self):
        request = {'client_id': 'ysp', 'request_id': 'ted-route-1-dm1'}
        for mode, branch in [('build', 'main'), ('live', 'task/ted-route-1-dm1')]:
            s = settings(); s['sites']['ysp']['mode'] = mode
            with patch.object(m, 'ensure_checkout', return_value=Path('/site/repo')), patch.object(m, 'git') as git:
                self.assertEqual(m.prepare(s, request, 'codex')[3], branch)
                branches = [call.args[1] for call in git.call_args_list if call.args[1][0]=='checkout']
                self.assertEqual(branches, [] if mode=='build' else [['checkout','-b',branch]])

    def test_git_authentication_is_ephemeral_and_errors_do_not_echo_secrets(self):
        with patch.object(m.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='', stderr='ephemeral')) as run:
            with self.assertRaisesRegex(ValueError, 'Git operation failed') as exc:
                m.git(Path('/site'), ['fetch','origin'], 'claude', token='ephemeral')
            self.assertNotIn('ephemeral', str(exc.exception))
            args, kw = run.call_args
            self.assertEqual(args[0][:4], ['runuser','-u','claudeworker','--'])
            self.assertNotIn('ephemeral', ' '.join(args[0]))
            self.assertEqual(kw['env']['GIT_CONFIG_KEY_0'], 'http.https://github.com/.extraheader')

class StaticPrototypeTests(unittest.TestCase):
    def test_static_check_finds_missing_local_assets(self):
        source = SOURCE.parent/'site_source_check.py'
        spec = importlib.util.spec_from_file_location('site_source_check', source)
        check = importlib.util.module_from_spec(spec); spec.loader.exec_module(check)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'index.html').write_text('<html><img src="missing.jpg"><script src="https://example.com/script.js"></script></html>')
            result=check.check(root)
            self.assertFalse(result['passed'])
            self.assertEqual(result['missing_assets'], [{'page':'index.html','asset':'missing.jpg'}])
            (root/'missing.jpg').write_bytes(b'image')
            self.assertTrue(check.check(root)['passed'])

class PublicationTests(unittest.TestCase):
    def test_publication_rejects_remote_drift_and_stale_checks(self):
        import sys
        request = {'client_id':'ysp','request_id':'ted-route-1-dm1','provider':'claude'}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); work=root/'work'; run=work/request['request_id'];run.mkdir(parents=True)
            (run/'request.json').write_text(json.dumps(request))
            s=settings()
            mapping={'repo':str(root/'ysp/repo'),'branch':'main','mode':'build'}
            for case in ['remote-drift','stale-checks','success']:
                calls=[]
                def git(repo,args,*_a,**_kw):
                    calls.append(args)
                    if args[0]=='remote': out='https://github.com/lhmorg/your-story-physio.git\n'
                    elif args[0]=='branch':out='main\n'
                    elif args[0]=='rev-parse':out='abc123\n'
                    elif args[0]=='ls-remote':out='abc123\trefs/heads/main\n'
                    else:out=''
                    return SimpleNamespace(stdout=out,returncode=1 if args[0]=='merge-base' and case=='remote-drift' else 0)
                dispatch=SimpleNamespace(WORK=work,verified=lambda _id:request)
                (root/'ysp').mkdir(exist_ok=True)
                with patch.dict(sys.modules,{'dispatch':dispatch}), patch.object(m,'ROOT',root), patch.object(m.os,'geteuid',return_value=0), patch.object(m,'config',return_value=s), patch.object(m,'validate_mapping',return_value=mapping), patch.object(m,'git',side_effect=git), patch.object(m,'installation_token',return_value='ephemeral'), patch.object(m,'read_owned',return_value={'passed':True,'commit':'old' if case=='stale-checks' else 'abc123'}):
                    if case=='success':
                        self.assertEqual(m.publish('ysp',request['request_id'],'reviewed')['commit'],'abc123')
                        self.assertIn(['push','origin','HEAD:refs/heads/main'],calls)
                    else:
                        with self.assertRaises(ValueError):m.publish('ysp',request['request_id'],'reviewed')
                        self.assertFalse(any(c[0]=='push' for c in calls))
                self.assertFalse(any('--force' in c for c in calls))
