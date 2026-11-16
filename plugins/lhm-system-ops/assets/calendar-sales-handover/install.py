#!/usr/bin/env python3
"""Install an exact approved Git export; snapshot all affected files for rollback."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

UNIT = 'lhm-calendar-sales-handover'
ROOT = Path('/usr/local/libexec') / UNIT
STATE = Path('/var/lib') / UNIT
PROFILE = Path('/home/hermes/.hermes/profiles/lhm_brain') / 'calendar-sales-handover'
FILES = ['runtime.py', 'watcher.py', 'codex_worker.py', 'calendar_read.py', 'fathom_read.py']


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=240)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--config-file', required=True, type=Path)
    parser.add_argument('--hold', action='store_true', help='Install without enabling until live acceptance passes')
    args = parser.parse_args()
    if os.geteuid() != 0 or not re.fullmatch('[a-f0-9]{40}', args.commit):
        parser.error('Root and an immutable full source SHA are required')
    source = Path(__file__).resolve().parent
    repo = source.parents[3]
    project = repo / 'plugins/lhm-project-hub'
    for name in FILES:
        compile((source / name).read_text(), name, 'exec')
    config = json.loads(args.config_file.read_text())
    config['source_commit'] = args.commit
    release = Path('/opt') / UNIT / 'releases' / args.commit
    if release.exists():
        raise ValueError('Release already installed; inspect existing receipt instead of overwriting')
    backup = Path('/root') / (UNIT + '-backups') / args.commit
    backup.mkdir(parents=True, mode=0o700)
    targets = [Path('/etc/' + UNIT + '.json'),
        Path('/etc/systemd/system/' + UNIT + '.service'),
        Path('/etc/systemd/system/' + UNIT + '.timer'),
        PROFILE / 'calendar_read.py']
    previous = {'symlink': str(ROOT.readlink()) if ROOT.is_symlink() else None,
        'timer_enabled': subprocess.run(['systemctl', 'is-enabled', UNIT + '.timer'], capture_output=True).returncode == 0,
        'targets': {}}
    if ROOT.exists() and not ROOT.is_symlink():
        raise ValueError('Runtime path occupied by a non-symlink; preserve it')
    for i, target in enumerate(targets):
        if target.exists():
            info = target.stat()
            saved = backup / str(i); shutil.copy2(target, saved)
            previous['targets'][str(target)] = {'backup': str(saved), 'uid': info.st_uid,
                'gid': info.st_gid, 'mode': info.st_mode & 0o777}
        else:
            previous['targets'][str(target)] = None
    (backup / 'before.json').write_text(json.dumps(previous, indent=2))
    release.mkdir(parents=True, mode=0o755)
    try:
        if subprocess.run(['systemctl', 'is-active', '--quiet', UNIT + '.service']).returncode == 0:
            raise ValueError('Calendar scan active; retry installation after it exits')
        active = run('/usr/bin/systemctl', 'list-units', '--state=running', '--plain',
                     '--no-legend', 'lhm-onboarding-*').stdout.strip()
        if active:
            raise ValueError('Saved-chat bootstrap active; retain it and install after completion')
        subprocess.run(['systemctl', 'stop', UNIT + '.timer'], capture_output=True)
        for name in FILES:
            shutil.copyfile(source / name, release / name)
            (release / name).chmod(0o644)
        skills = release / 'reviewed-skills'; skills.mkdir()
        for name in ('sales-handover', 'client-onboarding'):
            shutil.copytree(project / 'skills' / name, skills / name,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'LEARNED.md'))
        shutil.copytree(project / 'references', release / 'reviewed-references')
        config_target = Path('/etc/' + UNIT + '.json')
        config_target.write_text(json.dumps(config, indent=2) + '\n'); config_target.chmod(0o600)
        STATE.mkdir(exist_ok=True, mode=0o700)
        os.chown(STATE, 0, 10001); STATE.chmod(0o710)
        worker_runs = STATE / 'worker-runs'; worker_runs.mkdir(exist_ok=True)
        os.chown(worker_runs, 0, 10001); worker_runs.chmod(0o710)
        PROFILE.mkdir(exist_ok=True, mode=0o755)
        for name in ('calendar_read.py',):
            target = PROFILE / name
            shutil.copyfile(source / name, target); target.chmod(0o644)
        for suffix in ('service', 'timer'):
            shutil.copyfile(source / (UNIT + '.' + suffix), '/etc/systemd/system/' + UNIT + '.' + suffix)
        new = ROOT.with_name(ROOT.name + '.new')
        new.symlink_to(release); new.replace(ROOT)
        run('/usr/bin/systemd-analyze', 'verify', '/etc/systemd/system/' + UNIT + '.service',
            '/etc/systemd/system/' + UNIT + '.timer')
        run('/usr/bin/systemctl', 'daemon-reload')
        preflight = json.loads(run('/usr/bin/python3', str(ROOT / 'runtime.py'), 'dry-run').stdout)
        if preflight.get('errors') or preflight.get('state') != 'dry_run':
            raise ValueError('Calendar preflight did not pass')
        hashes = {name: hashlib.sha256((release / name).read_bytes()).hexdigest() for name in FILES}
        for name in ('calendar_read.py',):
            assert hashlib.sha256((PROFILE / name).read_bytes()).hexdigest() == hashes[name]
        if args.hold:
            run('/usr/bin/systemctl', 'disable', '--now', UNIT + '.timer')
        else:
            run('/usr/bin/systemctl', 'enable', '--now', UNIT + '.timer')
            run('/usr/bin/systemctl', 'is-active', UNIT + '.timer')
        receipt = {'status': 'installed_held_for_validation' if args.hold else 'installed_verified',
            'commit': args.commit, 'hashes': hashes,
            'release': str(release), 'backup': str(backup), 'preflight': preflight}
        (backup / 'installation.json').write_text(json.dumps(receipt, indent=2))
        print(json.dumps(receipt))
    except Exception:
        subprocess.run(['systemctl', 'disable', '--now', UNIT + '.timer'], capture_output=True)
        if ROOT.is_symlink(): ROOT.unlink()
        if previous['symlink']: ROOT.symlink_to(previous['symlink'])
        for target, meta in previous['targets'].items():
            path = Path(target)
            if meta:
                shutil.copyfile(meta['backup'], path)
                os.chown(path, meta['uid'], meta['gid']); path.chmod(meta['mode'])
            elif path.exists(): path.unlink()
        subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
        if previous['timer_enabled']:
            subprocess.run(['systemctl', 'enable', '--now', UNIT + '.timer'], capture_output=True)
        raise


if __name__ == '__main__':
    main()
