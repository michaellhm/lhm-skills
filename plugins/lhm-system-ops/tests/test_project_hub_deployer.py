import importlib.util
import hashlib
import hmac
import json
import shutil
import tempfile
import unittest
import zipfile
import os
from importlib.machinery import SourceFileLoader
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYER = ROOT / 'assets/host/lhm-approved-project-hub-deployer'
spec = importlib.util.spec_from_loader('project_hub_deployer', SourceFileLoader('project_hub_deployer', str(DEPLOYER)))
deployer = importlib.util.module_from_spec(spec); spec.loader.exec_module(deployer)


def archive(path, *, version='0.1.73', prefix='lhm-project-hub'):
    with zipfile.ZipFile(path, 'w') as bundle:
        bundle.writestr(f'{prefix}/.claude-plugin/plugin.json', json.dumps({'name':'lhm-project-hub','version':version}))
        bundle.writestr(f'{prefix}/skills/basicops-task-manager/SKILL.md', '---\nname: basicops-task-manager\n---\n')


class ProjectHubDeployerTests(unittest.TestCase):
    def test_release_manifest_binds_exact_deployer(self):
        release=json.loads((ROOT/'references/project-hub-deployer-release.json').read_text())
        self.assertEqual(release['source'],'assets/host/lhm-approved-project-hub-deployer')
        self.assertEqual(release['destination'],'/usr/local/libexec/lhm-approved-project-hub-deployer')
        self.assertEqual(release['sha256'],hashlib.sha256(DEPLOYER.read_bytes()).hexdigest())
        self.assertEqual(release['size_bytes'],DEPLOYER.stat().st_size)
        self.assertEqual(release['mode'],'0755')

    def approval_fixture(self, root, *, action='install'):
        approvals=root/'approvals'; approvals.mkdir(); key=approvals/'project-hub-approval.key'; key.write_bytes(b'k'*32)
        nonces=root/'nonces'; source=root/'release.zip'; archive(source); archive_sha=hashlib.sha256(source.read_bytes()).hexdigest()
        issued=datetime.now(timezone.utc)-timedelta(minutes=1); expires=issued+timedelta(hours=1)
        value={'schema_version':3,'approval_id':'approval-1','action':action,'repository':deployer.REPOSITORY,
               'commit':'a'*40,'archive_sha256':archive_sha,'plugin':deployer.PLUGIN,'profile':'lhm_brain',
               'issued_at':issued.isoformat(),'expires_at':expires.isoformat(),
               'nonce':'b'*32,'used':False,'signature':''}
        if action=='rollback': value['backup']=str(root/'backup')
        value['signature']=hmac.new(key.read_bytes(),deployer.signed_payload(value),hashlib.sha256).hexdigest()
        path=approvals/'approval-1.json'; path.write_text(json.dumps(value))
        originals=(deployer.APPROVALS,deployer.APPROVAL_KEY,deployer.USED_NONCES,deployer.secure_root_file,
                   deployer.secure_root_directory,deployer.secure_nonce_directory)
        deployer.APPROVALS=approvals; deployer.APPROVAL_KEY=key; deployer.USED_NONCES=nonces
        deployer.secure_root_file=lambda *args: None; deployer.secure_root_directory=lambda *args: None
        deployer.secure_nonce_directory=lambda *args: None
        return value,path,source,originals

    def restore_approval_fixture(self, originals):
        (deployer.APPROVALS,deployer.APPROVAL_KEY,deployer.USED_NONCES,deployer.secure_root_file,
         deployer.secure_root_directory,deployer.secure_nonce_directory)=originals

    def test_accepts_exact_project_hub_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); source=root/'release.zip'; archive(source)
            plugin, skills=deployer.validate_archive(source, root/'stage')
            self.assertEqual(plugin.name, 'lhm-project-hub')
            self.assertEqual(skills, ['basicops-task-manager'])

    def test_existing_identical_release_can_be_verified_for_relink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); source=root/'approved'; existing=root/'existing'
            (source/'skills/basicops-task-manager').mkdir(parents=True)
            (source/'skills/basicops-task-manager/SKILL.md').write_text('approved\n')
            shutil.copytree(source,existing)
            deployer.verify_existing_release(existing,source,uid=os.getuid())
            (existing/'skills/basicops-task-manager/SKILL.md').write_text('tampered\n')
            with self.assertRaisesRegex(SystemExit,'bytes differ'):
                deployer.verify_existing_release(existing,source,uid=os.getuid())

    def test_existing_release_rejects_extra_member_and_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); source=root/'approved'; existing=root/'existing'
            source.mkdir(); (source/'SKILL.md').write_text('approved\n'); shutil.copytree(source,existing)
            (existing/'extra').write_text('extra\n')
            with self.assertRaisesRegex(SystemExit,'member set differs'):
                deployer.verify_existing_release(existing,source,uid=os.getuid())
            (existing/'extra').unlink(); (existing/'linked').symlink_to(existing/'SKILL.md')
            with self.assertRaisesRegex(SystemExit,'link or special'):
                deployer.verify_existing_release(existing,source,uid=os.getuid())

    def test_existing_release_rejects_writable_root_and_hardlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); source=root/'approved'; existing=root/'existing'
            source.mkdir(); (source/'SKILL.md').write_text('approved\n'); shutil.copytree(source,existing)
            existing.chmod(0o777)
            with self.assertRaisesRegex(SystemExit,'secure directory'):
                deployer.verify_existing_release(existing,source,uid=os.getuid())
            existing.chmod(0o755); (existing/'hardlink').hardlink_to(existing/'SKILL.md')
            (source/'hardlink').write_text('approved\n')
            with self.assertRaisesRegex(SystemExit,'hard-linked'):
                deployer.verify_existing_release(existing,source,uid=os.getuid())

    def test_post_seal_reverification_rejects_injected_tamper(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); source=root/'approved'; existing=root/'existing'
            source.mkdir(); (source/'SKILL.md').write_text('approved\n'); shutil.copytree(source,existing)
            original=deployer.seal_release
            def tampering_seal(path,uid=0):
                original(path,uid=uid)
                (path/'SKILL.md').chmod(0o644)
                (path/'SKILL.md').write_text('tampered\n')
            deployer.seal_release=tampering_seal
            try:
                with self.assertRaisesRegex(SystemExit,'bytes differ'):
                    deployer.seal_and_reverify_release(existing,source,uid=os.getuid())
            finally:
                deployer.seal_release=original

    def test_rejects_wrong_version_or_plugin(self):
        for version, prefix, error in (
            ('0.1.72','lhm-project-hub','identity or version mismatch'),
            ('0.1.73','lhm-system-ops','unsafe plugin archive path'),
        ):
            with self.subTest(version=version,prefix=prefix), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary); source=root/'release.zip'; archive(source,version=version,prefix=prefix)
                with self.assertRaisesRegex(ValueError,error): deployer.validate_archive(source, root/'stage')

    def test_atomic_symlink_switch_and_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); first=root/'release-one'; second=root/'release-two'; first.mkdir(); second.mkdir()
            link=root/'current'; deployer.atomic_symlink(first,link)
            self.assertFalse(Path(link.readlink()).is_absolute())
            record=deployer.snapshot(link,root/'unused')
            deployer.atomic_symlink(second,link); self.assertEqual(link.resolve(),second.resolve())
            deployer.restore(link,record); self.assertEqual(link.resolve(),first.resolve())

    def test_release_and_profile_links_share_readonly_container_visible_tree(self):
        self.assertEqual(deployer.RELEASES, Path('/opt/lhm-plugin-releases/lhm-project-hub'))
        self.assertEqual(deployer.CURRENT, Path('/opt/lhm-plugin-releases/current/lhm-project-hub'))
        self.assertEqual(deployer.VISIBLE_ROOT, Path('/home/hermes/.hermes/immutable-plugin-releases'))
        self.assertEqual(deployer.CONTAINER_VISIBLE_ROOT, Path('/opt/data/immutable-plugin-releases'))
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); profile=root/'.hermes/profiles/lhm_brain'; release=root/'.hermes/immutable-plugin-releases/lhm-project-hub/hash'
            skill=release/'skills/basicops-task-manager'; skill.mkdir(parents=True)
            link=profile/'skills/basicops-task-manager'; deployer.atomic_symlink(skill,link)
            self.assertFalse(Path(link.readlink()).is_absolute())
            self.assertEqual(link.resolve(),skill.resolve())

    def test_secure_ancestor_helpers_reject_symlink_and_writable_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); governed=root/'governed'; child=governed/'current'; child.mkdir(parents=True)
            governed.chmod(0o777)
            with self.assertRaisesRegex(SystemExit,'writable'):
                deployer.secure_root_ancestors(child,governed,uid=os.getuid())
            governed.chmod(0o755); real=root/'real'; real.mkdir(); linked=root/'linked'; linked.symlink_to(real)
            with self.assertRaisesRegex(SystemExit,'linked'):
                deployer.reject_symlink_components(linked/'current')

    def test_mount_contract_is_explicit_and_read_only(self):
        compose=(ROOT/'references/hermes-project-hub-readonly-mount.compose.yaml').read_text()
        provisioner=(ROOT/'assets/host/provision-project-hub-release-mount').read_text()
        mount_unit=(ROOT/'assets/systemd/home-hermes-.hermes-immutable\\x2dplugin\\x2dreleases.mount').read_text()
        self.assertIn('source: /opt/lhm-plugin-releases',compose)
        self.assertIn('target: /opt/data/immutable-plugin-releases',compose)
        self.assertIn('read_only: true',compose)
        self.assertIn('systemctl enable --now',provisioner)
        self.assertIn('Options=bind,ro,nosuid,nodev,noexec',mount_unit)
        source=DEPLOYER.read_text()
        self.assertGreaterEqual(source.count('secure_release_boundary()'),2)
        self.assertNotIn('os.path.ismount(VISIBLE_ROOT)', source)

    def test_mountinfo_accepts_exact_same_filesystem_readonly_bind(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); target=root/'alias'; target.mkdir()
            mountinfo=root/'mountinfo'
            mountinfo.write_text(
                f'147 43 8:1 /opt/lhm-plugin-releases {target} '
                'ro,nosuid,nodev,noexec,relatime shared:1 - ext4 /dev/sda1 rw\n'
            )
            self.assertTrue(deployer.mount_is_read_only(target,mountinfo))
            mountinfo.write_text(
                f'147 43 8:1 /opt/lhm-plugin-releases {target} '
                'rw,nosuid,nodev,noexec,relatime shared:1 - ext4 /dev/sda1 rw\n'
            )
            self.assertFalse(deployer.mount_is_read_only(target,mountinfo))
            readonly=(
                f'147 43 8:1 /opt/lhm-plugin-releases {target} '
                'ro,nosuid,nodev,noexec,relatime shared:1 - ext4 /dev/sda1 rw\n'
            )
            writable=(
                f'148 43 8:1 /opt/lhm-plugin-releases {target} '
                'rw,nosuid,nodev,noexec,relatime shared:1 - ext4 /dev/sda1 rw\n'
            )
            for rows in (readonly+writable,writable+readonly):
                mountinfo.write_text(rows)
                self.assertFalse(deployer.mount_is_read_only(target,mountinfo))

    def test_approval_schema_is_action_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); value,path,source,originals=self.approval_fixture(root,action='rollback')
            try:
                with self.assertRaisesRegex(SystemExit,'invalid approval schema'):
                    deployer.consume_approval('approval-1','install',value['archive_sha256'],value['commit'])
            finally: self.restore_approval_fixture(originals)

    def test_signed_approval_rejects_tamper_and_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); value,path,source,originals=self.approval_fixture(root)
            try:
                tampered=dict(value); tampered['profile']='another-profile'; path.write_text(json.dumps(tampered))
                with self.assertRaisesRegex(SystemExit,'signature mismatch'):
                    deployer.consume_approval('approval-1','install',value['archive_sha256'],value['commit'])
                path.write_text(json.dumps(value))
                accepted=deployer.consume_approval('approval-1','install',value['archive_sha256'],value['commit'])
                self.assertEqual(accepted['nonce'],value['nonce'])
                with self.assertRaisesRegex(SystemExit,'nonce already consumed'):
                    deployer.consume_approval('approval-1','install',value['archive_sha256'],value['commit'])
            finally: self.restore_approval_fixture(originals)

    def test_rollback_rejects_backup_outside_governed_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); original=deployer.BACKUPS; deployer.BACKUPS=root/'backups'; deployer.BACKUPS.mkdir()
            outside=root/'lhm-project-hub-forged'; outside.mkdir()
            try:
                with self.assertRaisesRegex(SystemExit,'outside the governed backup root'):
                    deployer.rollback('unused',outside)
            finally: deployer.BACKUPS=original


if __name__ == '__main__': unittest.main()
