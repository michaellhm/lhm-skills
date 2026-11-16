#!/usr/bin/env python3
"""Hermes-backed calendar gate and one native, visible Codex chat per meeting."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import time
from urllib.parse import quote
import uuid

from watcher import Config, DispatchNotStarted, Watcher, instant

ROOT = Path('/usr/local/libexec/lhm-calendar-sales-handover')
STATE = Path('/var/lib/lhm-calendar-sales-handover')
CONFIG = Path('/etc/lhm-calendar-sales-handover.json')
CONTAINER_ROOT = '/opt/data/profiles/lhm_brain/calendar-sales-handover'


def atomic(path, value):
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    tmp = Path(temporary)
    with os.fdopen(descriptor, 'w') as handle:
        json.dump(value, handle, indent=2); handle.write('\n')
        handle.flush(); os.fsync(handle.fileno())
    tmp.chmod(0o600); tmp.replace(path)


def read(path, limit=262144):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError('Invalid receipt file')
        return json.load(handle)


def container_read(script, payload, timeout=90):
    result = subprocess.run(['/usr/bin/docker', 'exec', '-i', '--user', 'hermes',
        'hermes', '/opt/hermes/.venv/bin/python', CONTAINER_ROOT + '/' + script],
        input=json.dumps(payload), text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Hermes read adapter failed: ' + script)
    if len(result.stdout.encode()) > 2000000:
        raise ValueError('Hermes adapter output limit')
    return json.loads(result.stdout)


def fathom_read(payload):
    result = subprocess.run(['/usr/sbin/runuser', '-u', 'codexworker', '--',
        '/usr/bin/env', 'HOME=/home/codexworker', '/usr/bin/python3',
        str(ROOT / 'fathom_read.py')], input=json.dumps(payload), text=True,
        capture_output=True, timeout=180)
    if result.returncode or len(result.stdout.encode()) > 200000:
        raise RuntimeError('Existing Fathom read route unavailable')
    return json.loads(result.stdout)


def visible_host_ready():
    # Native non-model health check. Never create a chat Michael cannot open.
    result = subprocess.run(['/usr/sbin/runuser', '-u', 'codexworker', '--',
        '/usr/bin/env', 'HOME=/home/codexworker',
        '/home/codexworker/.local/bin/codex', 'remote-control', 'start', '--json'],
        capture_output=True, text=True, timeout=30)
    return result.returncode == 0


class Calendar:
    def __init__(self, calendar_id):
        self.calendar_id = calendar_id

    def call(self, action, **args):
        return container_read('calendar_read.py', {'action': action,
            'calendar_id': self.calendar_id, **args})

    def identity(self):
        return self.call('identity')['identity']

    def list_events(self, start, end):
        response = self.call('list', start=start, end=end)
        if response.get('pagination_complete') is not True:
            raise RuntimeError('Incomplete calendar read')
        return response['events']

    def get_event(self, event_id):
        return self.call('get', event_id=event_id)


class Dispatcher:
    def __init__(self, config):
        self.config = config

    def receipt(self, run):
        session = run / 'session.json'
        if not session.exists():
            return None
        thread = str(uuid.UUID(read(session)['thread_id']))
        return {'thread_id': thread, 'chat_url': 'codex://threads/' + thread +
                '?hostId=' + quote(self.config['codex_host_id'], safe='')}

    def __call__(self, payload):
        key = payload['dispatch_key']
        if not re.fullmatch(r'[a-f0-9]{64}', key):
            raise ValueError('Invalid dispatch key')
        run = STATE / 'worker-runs' / key
        if run.is_symlink():
            raise ValueError('Invalid run directory')
        run.mkdir(parents=True, exist_ok=True, mode=0o750)
        existing = self.receipt(run)
        if existing:
            return existing
        launch = STATE / 'launches' / (key + '.json')
        if launch.exists() or payload.get('reconcile_only'):
            # systemd or app-server may have accepted creation before the caller timed out.
            raise RuntimeError('Launch outcome pending; reconcile original session, never replay')
        if run.stat().st_uid != os.geteuid() or run.stat().st_mode & 0o022:
            raise RuntimeError('Prelaunch directory is not exclusively operator controlled')
        if not visible_host_ready():
            raise DispatchNotStarted('Existing Codex host needs authentication or reconnection')
        evidence_path = run / 'meeting-evidence.json'
        prior = read(evidence_path) if evidence_path.exists() else {'attempt': 0}
        try:
            evidence = fathom_read(payload)
        except Exception as exc:
            evidence = {'status': 'unavailable', 'error_type': type(exc).__name__}
        attempt = prior.get('attempt', 0) + 1
        evidence.update(attempt=attempt, checked_at=datetime.now(timezone.utc).isoformat())
        atomic(evidence_path, evidence)
        if evidence.get('status') == 'not_ready' and attempt < 3:
            raise DispatchNotStarted('Transcript not ready; retry on next scheduled check')
        # Immutable reviewed skill tree, including its local references and routing contract.
        shutil.copytree(ROOT / 'reviewed-skills', run / 'skills', dirs_exist_ok=True)
        shutil.copytree(ROOT / 'reviewed-references', run / 'references', dirs_exist_ok=True)
        packet = {**payload, 'codex_host_id': self.config['codex_host_id'],
            'meeting_evidence': evidence,
            'skill_sha256': hashlib.sha256((run / 'skills/sales-handover/SKILL.md').read_bytes()).hexdigest(),
            'authority': 'Research and local drafts only; Michael reviews in this saved chat.',
            'source_commit': self.config['source_commit']}
        atomic(run / 'event-context.json', packet)
        unit = 'lhm-onboarding-' + key[:24]
        # Persist before yielding directory ownership or requesting a native launch.
        atomic(launch, {'dispatch_key': key, 'unit': unit, 'state': 'launching',
            'started_at': datetime.now(timezone.utc).isoformat()})
        # Transfer the parent last: no worker-writable path is traversed by root afterwards.
        for parent, dirs, files in os.walk(run, topdown=False):
            for name in files:
                p = Path(parent) / name
                os.chown(p, 0, 10001); p.chmod(0o640)
            os.chown(parent, 10001, 10001); os.chmod(parent, 0o750)
        start_worker(run, unit)
        for _ in range(20):
            existing = self.receipt(run)
            if existing:
                atomic(launch, {'dispatch_key': key, 'unit': unit, 'state': 'in_codex', **existing})
                return existing
            time.sleep(1)
        raise RuntimeError('Native chat creation pending; reconcile on next check')


def start_worker(run, unit, resume=False):
    result = subprocess.run(['/usr/bin/systemd-run', '--quiet', '--collect',
        '--unit=' + unit, '--uid=codexworker', '--property=WorkingDirectory=' + str(run),
        '--property=Environment=HOME=/home/codexworker', '--property=UMask=0077',
        '--property=RuntimeMaxSec=1500', '--property=KillMode=control-group',
        '--property=NoNewPrivileges=yes', '--property=ProtectSystem=strict',
        '--property=ReadWritePaths=' + str(run) + ' /home/codexworker/.codex /home/codexworker/.cache /home/codexworker/.npm -/home/codexworker/.mcp-auth -/home/codexworker/.workspace-mcp -/home/codexworker/.google_workspace_mcp',
        '/usr/bin/python3', str(ROOT / 'codex_worker.py'), *(['--resume'] if resume else []), str(run)],
        capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError('Native worker launch failed; inspect saved launch before retry')


def load_config():
    info = CONFIG.lstat()
    if info.st_uid != 0 or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022:
        raise ValueError('Configuration must be root-owned and not writable by others')
    cfg = read(CONFIG)
    Config.from_dict(cfg)
    if not re.fullmatch(r'remote-control:env_[A-Za-z0-9_-]{1,100}', cfg['codex_host_id']):
        raise ValueError('Verified paired Codex host required')
    return cfg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['scan', 'dry-run', 'status', 'test', 'resume'])
    parser.add_argument('--event-id', help='Explicit existing event for isolated test; does not alter calendar')
    parser.add_argument('--run-key', help='Exact saved run key for explicit same-chat recovery')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Use the operator service')
    STATE.mkdir(exist_ok=True, mode=0o700)
    (STATE / 'launches').mkdir(exist_ok=True, mode=0o700)
    cfg = load_config()
    if args.action == 'resume':
        if not args.run_key or not re.fullmatch(r'[a-f0-9]{64}', args.run_key):
            parser.error('resume requires the exact saved --run-key')
        run = STATE / 'worker-runs' / args.run_key
        if run.is_symlink() or not run.is_dir():
            raise ValueError('Invalid saved run')
        saved = read(run / 'worker-receipt.json')
        if saved.get('status') != 'needs_attention' or not Dispatcher(cfg).receipt(run):
            raise ValueError('Only a failed saved conversation may be explicitly resumed')
        start_worker(run, 'lhm-onboarding-resume-' + args.run_key[:24], resume=True)
        print(json.dumps({'state': 'resuming_same_chat', **Dispatcher(cfg).receipt(run)})); return
    calendar = Calendar(cfg['calendar_id'])
    watcher = Watcher(STATE / 'events.sqlite', Config.from_dict(cfg), calendar, Dispatcher(cfg))
    if args.action == 'status':
        rows = watcher.status()
        test_db = STATE / 'test-events.sqlite'
        if test_db.exists():
            tests = Watcher(test_db, Config.from_dict(cfg), calendar, Dispatcher(cfg)).status()
            rows.extend(dict(row, test_mode=True) for row in tests)
        for row in rows:
            key = row['dispatch_key']
            if row.get('test_mode'):
                key = hashlib.sha256(('test:' + key).encode()).hexdigest()
            row['run_key'] = key
            run = STATE / 'worker-runs' / key
            p = run / 'worker-receipt.json'
            row['worker'] = read(p) if p.exists() else None
        last = STATE / 'last-scan.json'
        print(json.dumps({'events': rows, 'last_scan': read(last) if last.exists() else None}, indent=2)); return
    if args.action == 'test':
        if not args.event_id:
            parser.error('test requires an explicit existing --event-id')
        event = calendar.get_event(args.event_id)
        # Isolated ledger: no historical production queue or repeated test chat flood.
        test_cfg = dict(cfg, enabled_from='2000-01-01T00:00:00+00:00')
        class SelectedCalendar(Calendar):
            def list_events(self, start, end):
                return [self.get_event(args.event_id)]
        dispatch = Dispatcher(cfg)
        def test_dispatch(payload):
            return dispatch({**payload, 'test_mode': True,
                'dispatch_key': hashlib.sha256(('test:' + payload['dispatch_key']).encode()).hexdigest()})
        report = Watcher(STATE / 'test-events.sqlite', Config.from_dict(test_cfg),
            SelectedCalendar(cfg['calendar_id']), test_dispatch).run()
    else:
        report = watcher.run(dry_run=args.action == 'dry-run')
    report['checked_at'] = datetime.now(timezone.utc).isoformat()
    atomic(STATE / ('last-test.json' if args.action == 'test' else 'last-scan.json'), report)
    print(json.dumps(report, indent=2))
    if report['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # API responses and connector diagnostics may contain sensitive content.
        print(json.dumps({'state': 'failed', 'error_type': type(exc).__name__}))
        raise SystemExit(1)
