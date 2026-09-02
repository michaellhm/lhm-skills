#!/usr/bin/env python3
"""Root-owned CAP-015 installer with exact preflight and byte-for-byte rollback."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import grp
import pwd
from pathlib import Path

CAPABILITY_ID = 'CAP-015'
RELEASE_VERSION = '0.9.23'
PLUGIN = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PLUGIN / 'references/shared-claude-gateway-release.json'
ANCESTORS = ('/home/hermes/.hermes', '/home/hermes/.hermes/profiles/lhm_brain')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_identity(value, kind):
    if isinstance(value, int) and value >= 0:
        return value
    if value == 'root':
        return 0
    try:
        return pwd.getpwnam(value).pw_uid if kind == 'owner' else grp.getgrnam(value).gr_gid
    except KeyError as exc:
        raise SystemExit(f'unknown manifest {kind}') from exc
    raise SystemExit(f'unsupported manifest {kind}')


def load_manifest(path=MANIFEST_PATH):
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    if payload.get('capability_id') != CAPABILITY_ID or payload.get('release_version') != RELEASE_VERSION:
        raise SystemExit('CAP-015 manifest identity/version mismatch')
    return payload


def verify_sources(manifest, plugin=PLUGIN):
    for name, item in manifest['assets'].items():
        source = plugin / item['source']
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f'{name}: source missing or linked')
        expected = item.get('sha256')
        if not expected or sha256(source) != expected:
            raise SystemExit(f'{name}: tracked source hash mismatch')


def preflight_destinations(manifest):
    for name, item in manifest['assets'].items():
        destination = Path(item['destination'])
        if item.get('new_in_release') and not destination.exists():
            continue
        if not destination.is_file() or destination.is_symlink():
            raise SystemExit(f'{name}: destination missing or linked')
        expected = item.get('previous_sha256')
        if not expected or sha256(destination) != expected:
            raise SystemExit(f'{name}: deployed source is not the exact approved CAP-015 predecessor')


def write_state(manifest, backup_root, runner=subprocess.run):
    backup_root.mkdir(mode=0o700, parents=False, exist_ok=False)
    records = {}
    for name, item in manifest['assets'].items():
        source = Path(item['destination'])
        if item.get('new_in_release') and not source.exists():
            records[name] = {'destination': str(source), 'created': True}
            continue
        stat = source.stat()
        backup = backup_root / name
        shutil.copyfile(source, backup)
        os.chmod(backup, 0o600)
        records[name] = {'destination': str(source), 'backup': str(backup), 'sha256': sha256(backup),
                         'uid': stat.st_uid, 'gid': stat.st_gid, 'mode': stat.st_mode & 0o7777}
    acl_file = backup_root / 'ancestors.acl'
    completed = runner(['/usr/bin/getfacl', '--absolute-names', *ANCESTORS], check=True, capture_output=True)
    acl_file.write_bytes(completed.stdout)
    os.chmod(acl_file, 0o600)
    state = {'capability_id': CAPABILITY_ID, 'release_version': RELEASE_VERSION,
             'assets': records, 'acl_backup': str(acl_file), 'ancestors': list(ANCESTORS)}
    state_file = backup_root / 'rollback.json'
    state_file.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    os.chmod(state_file, 0o600)
    return state_file


def atomic_install(manifest, plugin=PLUGIN):
    for item in manifest['assets'].values():
        source = plugin / item['source']
        destination = Path(item['destination'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f'.{destination.name}.', dir=destination.parent)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(source.read_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            os.chown(temporary, numeric_identity(item['owner'], 'owner'),
                     numeric_identity(item['group'], 'group'))
            os.chmod(temporary, int(item['mode'], 8))
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def rollback(state_path, runner=subprocess.run):
    state = json.loads(Path(state_path).read_text(encoding='utf-8'))
    if state.get('capability_id') != CAPABILITY_ID:
        raise SystemExit('rollback state is not CAP-015')
    for record in state['assets'].values():
        if record.get('created'):
            destination = Path(record['destination'])
            if destination.exists() and not destination.is_symlink():
                destination.unlink()
            continue
        backup = Path(record['backup'])
        if sha256(backup) != record['sha256']:
            raise SystemExit('rollback backup hash mismatch')
        destination = Path(record['destination'])
        fd, temporary = tempfile.mkstemp(prefix=f'.{destination.name}.rollback.', dir=destination.parent)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(backup.read_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            os.chown(temporary, record['uid'], record['gid'])
            os.chmod(temporary, record['mode'])
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    runner(['/usr/bin/setfacl', '--restore', state['acl_backup']], check=True)
    runner(['/usr/bin/systemctl', 'daemon-reload'], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup-directory')
    parser.add_argument('--rollback-state')
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('CAP-015 installation requires the approved root-owned installer')
    if bool(args.backup_directory) == bool(args.rollback_state):
        raise SystemExit('choose exactly one of --backup-directory or --rollback-state')
    if args.rollback_state:
        rollback(Path(args.rollback_state))
        return
    manifest = load_manifest()
    verify_sources(manifest)
    preflight_destinations(manifest)
    # The caller can create only unpredictable files here, never read or list them.
    os.makedirs('/var/lib/lhm-workflow/claude-artifact-export', mode=0o700, exist_ok=True)
    workflow_gid = grp.getgrnam('lhmworkflow').gr_gid
    adapter_gid = grp.getgrnam('lhmworkflowadapter').gr_gid
    for name, mode, gid in (('incoming', 0o730, workflow_gid), ('processing', 0o700, 0),
                            ('accepted', 0o700, 0), ('failed', 0o700, 0),
                            ('incidents', 0o700, 0), ('locks', 0o700, 0),
                            ('operations', 0o700, 0), ('artifacts', 0o2750, adapter_gid)):
        path = Path('/var/lib/lhm-workflow/claude-artifact-export') / name
        path.mkdir(mode=mode, exist_ok=True); os.chown(path, 0, gid); os.chmod(path, mode)
    key = Path('/var/lib/lhm-workflow/claude-artifact-export/locks/exporter.key')
    if not key.exists():
        key.write_bytes(os.urandom(32)); os.chown(key, 0, 0); os.chmod(key, 0o600)
    state_file = write_state(manifest, Path(args.backup_directory))
    try:
        atomic_install(manifest)
        subprocess.run(['/usr/bin/systemd-analyze', 'verify',
                        manifest['assets']['dispatch_unit']['destination'],
                        manifest['assets']['artifact_export_unit']['destination'],
                        manifest['assets']['artifact_export_path']['destination']], check=True)
        subprocess.run(['/usr/bin/systemctl', 'daemon-reload'], check=True)
    except Exception:
        rollback(state_file)
        raise
    print(json.dumps({'capability_id': CAPABILITY_ID, 'release_version': RELEASE_VERSION,
                      'rollback_state': str(state_file)}))


if __name__ == '__main__':
    main()
