#!/usr/bin/env python3
"""Recover only an unchanged registry-failed admission before any provider launch."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from dispatch import BASE, WORK, ID, verified, read, atomic, launch
from workspaces import location, publish_registry


def recover(request_id):
    if os.geteuid() != 0 or not ID.fullmatch(request_id):
        raise ValueError('Root and an exact registered request ID are required')
    with (WORK / 'dispatch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run, queued = WORK / request_id, BASE / 'runs' / request_id
        receipt = json.loads(read(queued / 'receipt.json'))
        if receipt.get('status') != 'failed' or receipt.get('error') != 'Existing Obsidian registry is not our generated note':
            raise ValueError('Recovery is restricted to the known registry admission failure')
        request = verified(request_id)
        if json.loads(read(run / 'request.json')) != request:
            raise ValueError('Personal task contract changed; do not replay')
        if any((run / name).exists() for name in ['receipt.json', 'session.json', 'result.md', 'admission-recovery.json']):
            raise ValueError('Provider evidence or prior recovery exists; inspect instead of replaying')
        state = subprocess.run(['systemctl', 'show', '--property=ActiveState', '--value', 'lhm-task-' + request_id], capture_output=True, text=True, timeout=10, check=True)
        if state.stdout.strip() in {'active', 'activating', 'reloading'}:
            raise ValueError('Provider is already active')
        root = location(request['provider'], request['client_id'])
        task = root / 'tasks' / request_id
        mapping = json.loads(read(run / 'workspace-location.json'))
        if mapping != {'workspace': str(root), 'task_directory': str(task)} or task.is_symlink():
            raise ValueError('Workspace identity mismatch')
        packet = json.loads(read(task / 'task-context.json'))
        if packet.get('instruction_sha256') != request['instruction_sha256']:
            raise ValueError('Prepared context differs from the verified instruction')
        if list((task / 'drafts').iterdir()):
            raise ValueError('Existing drafts require manual reconciliation')
        publish_registry()
        # Durable admission before launch: a second invocation cannot duplicate a worker.
        atomic(run / 'admission-recovery.json', {'request_id': request_id, 'reason': receipt['error'], 'recovered_at': int(time.time())})
        atomic(queued / 'pre-admission-recovery.json', receipt)
        atomic(queued / 'receipt.json', {'status': 'starting', 'provider': request['provider'], 'request_id': request_id, 'started_at': int(time.time())})
        launch(request, run, root)
        return {'request_id': request_id, 'status': 'starting'}


if __name__ == '__main__':
    print(json.dumps(recover(sys.argv[1])))
