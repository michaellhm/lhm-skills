"""One scheduled host sweep. Completion remains with the existing router tick."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

from adapters import BasicOps
from host_runtime import Coordinator, REGISTRATION, STATE_ROOT, registration, root_json


def sweep(site, *, runner=subprocess.run):
    if os.geteuid() != 0:
        raise ValueError('existing root host coordinator required')
    runtime = Coordinator()
    lock = os.open(STATE_ROOT/'poll.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: return {'site': site, 'state': 'busy'}
        config = root_json(REGISTRATION)
        if config.get('sites', {}).get(site, {}).get('enabled') is not True:
            return {'site': site, 'state': 'paused'}
        reg = registration(REGISTRATION, site)
        runtime.identity()
        ops = BasicOps(runtime.basicops, runtime.effects, reg['stage_id'])
        if not ops.eligible(reg['cockpit_id']):
            return {'site': site, 'state': 'paused'}
        script = Path(__file__).resolve().with_name('intake_scan.py')
        done = runner(['/usr/bin/python3', str(script), 'scan', '--registry', str(REGISTRATION),
                       '--state', str(STATE_ROOT), '--site', site],
                      capture_output=True, text=True, timeout=3300, check=False)
        if done.returncode or len(done.stdout) > 2 * 1024 * 1024:
            raise RuntimeError('feedback scan failed; inspect private held/recovery records')
        scan = json.loads(done.stdout)
        if scan.get('scan_only') is not True or not isinstance(scan.get('outcomes'), list):
            raise ValueError('scanner did not return a bounded scan receipt')
        imported = runtime.run(site, 'scan')
        dispatch = imported if imported['state'] == 'paused' else runtime.run(site, 'dispatch')
        # No raw email, images, model output or connector diagnostics enter journal.
        return {'site': site, 'state': dispatch['state'], 'scanned': len(scan['outcomes']),
                'held': sum(row.get('state') == 'held' for row in scan['outcomes']),
                'import_state': imported['state'],
                **{key: dispatch[key] for key in ('task_id', 'request_id', 'worker_status') if key in dispatch}}
    finally:
        os.close(lock);runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', required=True)
    args = parser.parse_args()
    try:
        result = sweep(args.site)
    except Exception as exc:
        # Detailed evidence remains in private state. Do not print raw exception data.
        print(json.dumps({'site': args.site, 'state': 'blocked', 'error_type': type(exc).__name__}))
        raise SystemExit(1)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__': main()
