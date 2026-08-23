import importlib.util
import hashlib
import hmac
import json
import tempfile
import unittest
import zipfile
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
            record=deployer.snapshot(link,root/'unused')
            deployer.atomic_symlink(second,link); self.assertEqual(link.resolve(),second.resolve())
            deployer.restore(link,record); self.assertEqual(link.resolve(),first.resolve())

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
