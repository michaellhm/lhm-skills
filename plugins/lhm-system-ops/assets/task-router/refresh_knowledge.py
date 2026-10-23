#!/usr/bin/env python3
"""One-way shared-Drive reads into a separate cache; never unlock or run bisync."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
CACHE = Path('/home/hermes/.hermes/profiles/lhm_brain/vault-task-router')


def refresh():
    with Path('/var/lib/lhm-task-router/knowledge-refresh.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if CACHE.is_symlink():
            raise ValueError('Knowledge cache must be its dedicated directory')
        CACHE.mkdir(exist_ok=True, mode=0o750)
        outcome = {'status': 'failed', 'source': 'lhm-knowledge:', 'cache': str(CACHE)}
        try:
            # One-way sync reads Drive and removes obsolete local cache files only. It never touches bisync's path or state.
            for prefix in ['20 Clients', '30 Projects']:
                subprocess.run(['/usr/local/bin/rclone', 'sync', 'lhm-knowledge:' + prefix,
                    str(CACHE / prefix), '--config', '/etc/lhm-obsidian-sync/rclone.conf',
                    '--include', '*.md', '--exclude', '**/.*', '--log-level', 'ERROR'],
                    capture_output=True, text=True, timeout=240, check=True)
            for p in [CACHE, *CACHE.rglob('*')]:
                if p.is_symlink():
                    raise ValueError('Unexpected cache symlink')
                os.chown(p, 0, 10000)
                p.chmod(0o750 if p.is_dir() else 0o640)
            outcome.update(status='ready', completed_at=int(time.time()))
        except Exception as exc:
            outcome['error'] = type(exc).__name__ + ': shared-Drive read refresh failed; inspect the bounded service'
        target = PROFILE / 'task-router-knowledge-refresh.json'
        tmp = target.with_suffix('.tmp')
        tmp.write_text(json.dumps(outcome, indent=2) + '\n')
        os.chown(tmp, 0, 10000)
        tmp.chmod(0o640)
        tmp.replace(target)
        print(json.dumps({'status': outcome['status'], 'cache': str(CACHE)}))
        if outcome['status'] != 'ready':
            raise SystemExit(1)


if __name__ == '__main__':
    refresh()
