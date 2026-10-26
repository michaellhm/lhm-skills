#!/usr/bin/env python3
"""Worker-facing request/receipt client; no credentials or privileged operations."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import uuid
from site_workspace import REQUEST, atomic, validate_mapping


def request_publication(request_id, wait_seconds=45):
    if not REQUEST.fullmatch(request_id) or not 0 <= wait_seconds <= 60:
        raise ValueError('Exact task request ID and bounded wait required')
    run = Path('/var/lib/lhm-task-router') / request_id
    request = json.loads((run / 'request.json').read_text())
    mapping = validate_mapping(run, request)
    repo = Path(mapping['repo'])
    sha = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    if subprocess.run(['git', '-C', str(repo), 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout:
        raise ValueError('Commit scoped website edits before requesting publication')
    packet = {'request_id': request_id, 'commit': sha, 'nonce': str(uuid.uuid4())}
    atomic(Path(mapping['task_directory']) / 'publish-request.json', packet)
    deadline = time.monotonic() + wait_seconds
    while True:
        path = run / 'site-publication.json'
        if path.exists():
            from site_workspace import read_owned
            receipt = read_owned(path)
            if receipt.get('commit') == sha:
                if receipt.get('status') == 'published':
                    return receipt
                import hashlib
                fingerprint = hashlib.sha256(json.dumps(packet, sort_keys=True).encode()).hexdigest()
                if receipt.get('fingerprint') == fingerprint:
                    return receipt
        if time.monotonic() >= deadline:
            return {'status': 'pending', 'commit': sha, 'receipt_path': str(run / 'site-publication.json'), 'next_step': 'Read the existing receipt; do not create a duplicate push request'}
        time.sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('request_id')
    parser.add_argument('--wait-seconds', type=int, default=45)
    args = parser.parse_args()
    result = request_publication(args.request_id, args.wait_seconds)
    print(json.dumps(result))
    raise SystemExit(1 if result['status'] == 'failed' else 0)
