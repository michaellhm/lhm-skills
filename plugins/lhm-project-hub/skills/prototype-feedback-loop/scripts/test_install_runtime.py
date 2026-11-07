"""Disposable installer tests; no live paths, units or workers are changed."""
import io
import json
import os
from pathlib import Path
import sqlite3
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import install_runtime as mod


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.commit = 'a'*40
        self.config = self.root/'sites.json'
        self.row = {'enabled': True, 'account': 'michael@example.com', 'senders': ['tara@example.com'],
                    'threads': ['1a1a8d364f7f2f43'], 'review_start': '2026-11-05T10:09:48+11:00', 'cockpit_id': 2220225,
                    'stage_id': 110340, 'client_id': 'blue-dragonfly', 'client_label': 'Blue Dragonfly',
                    'canonical_note': '20 Clients/Blue Dragonfly/project-management/website.md',
                    'work_folder_url': 'https://drive.google.com/drive/folders/clientfolder0000',
                    'repository': 'michaellhm/lhm-prototype', 'subtree': 'luminary-counselling/',
                    'preview_url': 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/',
                    'reviewer_id': 36398, 'worker_root': '/var/lib/lhm-client-workspaces/codex/blue-dragonfly'}
        self.save_config()

    def save_config(self):
        self.config.write_bytes(mod.canonical({'schema_version': 1, 'sites': {'luminary-counselling': self.row}}));self.config.chmod(0o600)

    def archive(self, *, commit=None, omitted=None, linked=None, extra=None):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w', format=tarfile.PAX_FORMAT, pax_headers={'comment': commit or self.commit}) as archive:
            for name in mod.ASSETS:
                if name == omitted: continue
                entry = tarfile.TarInfo(name)
                if name == linked:
                    entry.type = tarfile.SYMTYPE;entry.linkname = '/etc/shadow';archive.addfile(entry)
                else:
                    raw = ('reviewed source ' + name).encode();entry.size = len(raw);archive.addfile(entry, io.BytesIO(raw))
            if extra:
                entry = tarfile.TarInfo(extra);entry.size = 1;archive.addfile(entry, io.BytesIO(b'x'))
        path = self.root/'source.tar';path.write_bytes(output.getvalue())
        return path, mod.digest(output.getvalue())

    def test_exact_archive_marker_and_digest_yield_only_explicit_assets(self):
        path, checksum = self.archive(extra='other-plugin/unrelated.txt')
        payload = mod.archive_payload(path, self.commit, checksum)
        self.assertEqual(set(payload), set(mod.ASSETS))
        self.assertFalse(any('other-plugin' in name for name in payload))
        self.assertIn(mod.PREFIX+'SKILL.md', payload)
        self.assertIn(mod.PREFIX+'scripts/poll_runtime.py', payload)

    def test_wrong_commit_or_digest_rejected(self):
        path, checksum = self.archive()
        with self.assertRaises(ValueError): mod.archive_payload(path, 'b'*40, checksum)
        with self.assertRaises(ValueError): mod.archive_payload(path, self.commit, '0'*64)

    def test_missing_linked_or_traversing_assets_rejected(self):
        selected = next(iter(mod.ASSETS))
        for change in ({'omitted': selected}, {'linked': selected}, {'extra': '../escape'}):
            with self.subTest(change=change):
                path, checksum = self.archive(**change)
                with self.assertRaises(ValueError): mod.archive_payload(path, self.commit, checksum)

    def test_private_closed_registration_only(self):
        self.assertEqual(json.loads(mod.registration_payload(self.config))['sites']['luminary-counselling']['cockpit_id'], 2220225)
        self.config.chmod(0o644)
        with self.assertRaises(ValueError): mod.registration_payload(self.config)
        self.row['command'] = 'not allowed';self.save_config()
        with self.assertRaises(ValueError): mod.registration_payload(self.config)

    def test_unregistered_repository_or_workspace_rejected(self):
        self.row['repository'] = 'michaellhm/live-site';self.save_config()
        with self.assertRaises(ValueError): mod.registration_payload(self.config)
        self.row['repository'] = 'michaellhm/lhm-prototype';self.row['worker_root'] = '/etc';self.save_config()
        with self.assertRaises(ValueError): mod.registration_payload(self.config)

    def test_disposable_apply_backs_up_exact_files_and_preserves_live_queue_owner(self):
        install = self.root/'opt/runtime';state = self.root/'var/state';state.mkdir(parents=True);state.chmod(0o755)
        (state/'state').mkdir(mode=0o700)
        owner = state/'state/owner.json';owner.write_bytes(b'{"owner":"existing-immutable-owner"}');owner.chmod(0o600)
        queue = state/'state/queue.sqlite'
        with sqlite3.connect(queue) as db: db.execute('CREATE TABLE historical(value TEXT)');db.execute("INSERT INTO historical VALUES ('keep')")
        queue.chmod(0o600);before_queue = queue.read_bytes()
        helper = self.root/'libexec/github_deployment.py';helper.parent.mkdir();helper.parent.chmod(0o755);helper.write_bytes(b'old independent helper');helper.chmod(0o755)
        profile = self.root/'profile/SKILL.md';profile.parent.mkdir();profile.parent.chmod(0o755);profile.write_bytes(b'old scope doc')
        router = self.root/'hermes-profile/task-router/router.py'
        router.parent.mkdir(parents=True);router.parent.chmod(0o770)
        router.write_bytes(b'old root router');router.chmod(0o755)
        router_inode = router.parent.stat().st_ino
        router_owner = [10000]
        router_source = mod.SYSTEM+'assets/task-router/router.py'
        ext_source = mod.SYSTEM+'assets/task-router/github_deployment.py'
        payload = {source: ('new reviewed '+source).encode() for source in mod.ASSETS}
        payload[mod.PREFIX+'scripts/install_runtime.py'] = Path(mod.__file__).read_bytes()
        real_fstat = os.fstat
        def root_stat(fd):
            info = real_fstat(fd)
            return SimpleNamespace(st_uid=router_owner[0] if info.st_ino == router_inode else 0, st_gid=10000 if info.st_ino == router_inode else 10001, st_mode=info.st_mode, st_nlink=info.st_nlink, st_size=info.st_size, st_mtime_ns=info.st_mtime_ns)
        patches = [patch.object(mod, 'QA_ROOT', state/'qa-runs'), patch.object(mod, 'DISPATCH_LOCK', self.root/'libexec/dispatch.lock'),
                   patch.object(mod, 'INSTALL', install), patch.object(mod, 'CURRENT', install/'current'),
                   patch.object(mod, 'COMPAT', self.root/'libexec/runtime'), patch.object(mod, 'CODEX_SKILL', self.root/'codex/skills/loop'),
                   patch.object(mod, 'CONFIG', self.root/'etc/sites.json'), patch.object(mod, 'STATE', state),
                   patch.object(mod, 'EXTERNAL', {ext_source: str(helper), router_source: str(router)}),
                   patch.object(mod, 'PROFILE_ROUTER', str(router)),
                   patch.object(mod, 'PROFILE_FILES', {str(profile): mod.PREFIX+'SKILL.md'}),
                   patch.object(mod.os, 'geteuid', return_value=0), patch.object(mod.os, 'fstat', side_effect=root_stat), patch.object(mod.os, 'fchown')]
        for item in patches: item.start();self.addCleanup(item.stop)
        baseline = mod.current_state()
        # Even when a root helper comes first, an unknown late profile owner aborts
        # the whole preflight without replacing any existing target.
        router_owner[0] = 12345
        with self.assertRaisesRegex(ValueError, 'untrusted scoped Hermes'):
            mod.apply(self.commit, payload, mod.registration_payload(self.config), baseline)
        self.assertEqual(helper.read_bytes(), b'old independent helper')
        self.assertEqual(router.read_bytes(), b'old root router')
        self.assertFalse((install/'releases'/self.commit).exists())
        router_owner[0] = 10000
        pinned = mod.target_parent(router)
        try:
            router.write_bytes(b'independent repair after baseline')
            with self.assertRaisesRegex(ValueError, 'changed after preflight'):
                mod.verify_destination(router, pinned, baseline['targets'][str(router)])
            router.write_bytes(b'old root router')
        finally:
            os.close(pinned)
        original_parent = router.parent.with_name('original-task-router')
        router.parent.rename(original_parent)
        router.parent.symlink_to(original_parent, target_is_directory=True)
        with self.assertRaises(OSError):
            mod.apply(self.commit, payload, mod.registration_payload(self.config), baseline)
        self.assertEqual(helper.read_bytes(), b'old independent helper')
        router.parent.unlink();original_parent.rename(router.parent)
        previous = os.umask(0o077)
        try:
            result = mod.apply(self.commit, payload, mod.registration_payload(self.config), baseline)
        finally:
            os.umask(previous)
        release = install/'releases'/self.commit
        for path, expected in ((release, 0o755), (release/'scripts', 0o755),
                               (release/'SKILL.md', 0o644), (helper, 0o755),
                               (self.root/'etc/sites.json', 0o600), (state/'qa-runs', 0o750)):
            self.assertEqual(path.stat().st_mode & 0o777, expected, str(path))
        self.assertEqual(result['state'], 'installed-not-activated')
        self.assertFalse(result['timer_installed']);self.assertFalse(result['timer_enabled'])
        self.assertEqual(queue.read_bytes(), before_queue)
        self.assertEqual(owner.read_bytes(), b'{"owner":"existing-immutable-owner"}')
        index = json.loads((Path(result['backup'])/'target-index.json').read_text())
        self.assertEqual((Path(result['backup'])/index[str(helper)]['file']).read_bytes(), b'old independent helper')
        self.assertEqual(helper.read_bytes(), payload[ext_source])
        self.assertEqual(router.read_bytes(), payload[router_source])
        self.assertEqual(router.parent.stat().st_mode & 0o777, 0o770)
        self.assertEqual(index[str(router)]['uid'], router.stat().st_uid)
        self.assertEqual(index[str(router)]['gid'], router.stat().st_gid)
        # A later path swap cannot redirect writes through the retained descriptor.
        fd = mod.target_parent(router)
        outside = self.root/'outside';outside.mkdir();(outside/'router.py').write_bytes(b'untouched')
        router.parent.rename(original_parent);router.parent.symlink_to(outside, target_is_directory=True)
        try:
            mod.atomic(router, b'anchored', mode=0o755, parent_fd=fd)
        finally:
            os.close(fd)
        self.assertEqual((outside/'router.py').read_bytes(), b'untouched')
        self.assertEqual((original_parent/'router.py').read_bytes(), b'anchored')
        router.parent.unlink();original_parent.rename(router.parent)
        router.write_bytes(payload[router_source])
        self.assertEqual(os.readlink(install/'current'), 'releases/'+self.commit)
        self.assertEqual(os.readlink(self.root/'codex/skills/loop'), str(install/'current'))
        self.assertFalse((self.root/'etc/systemd').exists())
        # Busy existing supervisor/completion work prevents all helper/link mutations.
        import fcntl
        import subprocess
        for held in (state/'qa-runs/.coordinator.lock', self.root/'libexec/dispatch.lock'):
            with held.open('a') as lock, patch.object(subprocess, 'run') as commands:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                stable = mod.current_state()
                with self.assertRaises(BlockingIOError):
                    mod.apply('d'*40, payload, mod.registration_payload(self.config), stable)
                commands.assert_not_called()
                self.assertEqual(mod.current_state(), stable)
                self.assertFalse((install/'releases'/('d'*40)).exists())
                self.assertEqual(queue.read_bytes(), before_queue)
        grant = self.root/'external-authority.json';grant.write_bytes(b'preserve existing grants')
        changed = mod.current_state();helper.write_bytes(b'a newer independent repair')
        with self.assertRaisesRegex(ValueError, 'baseline changed'):
            mod.apply('c'*40, payload, mod.registration_payload(self.config), changed)
        self.assertFalse((install/'releases'/('c'*40)).exists())
        self.assertEqual(grant.read_bytes(), b'preserve existing grants')
        self.assertEqual(queue.read_bytes(), before_queue)
        self.assertEqual(helper.read_bytes(), b'a newer independent repair')


if __name__ == '__main__': unittest.main()
