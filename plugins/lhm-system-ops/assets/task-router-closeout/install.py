#!/usr/bin/env python3
"""Install the bounded broker and merge one MCP definition; never print secrets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import re
import subprocess
import tempfile
import time

SOURCE = Path(__file__).resolve().parent
DEST = Path('/usr/local/libexec/lhm-task-router/closeout')
CONFIG = Path('/home/claudeworker/.config/lhm-bridge')


def write(path, content, mode, group=0):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), mode)
        os.fchown(stream.fileno(), 0, group)
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.source_commit):
        raise ValueError('Exact approved source commit required')
    if os.geteuid() != 0:
        raise SystemExit('Run as the existing host operator')
    backup = Path('/root/lhm-closeout-backups') / str(time.time_ns())
    backup.mkdir(parents=True, mode=0o700)
    backup.parent.chmod(0o700)
    paths = [CONFIG / 'voyager-review.mcp.json', CONFIG / 'task-execution.settings.json']
    values = [json.loads(path.read_bytes()) for path in paths]
    server = {'type': 'stdio', 'command': '/usr/bin/python3', 'args': [str(DEST / 'closeout_mcp.py')]}
    current = values[0].setdefault('mcpServers', {}).get('LHMCloseout')
    if current is not None and current != server:
        raise ValueError('Existing LHMCloseout definition differs; refusing replacement')
    values[0]['mcpServers']['LHMCloseout'] = server
    allowed = values[1].setdefault('allowedMcpServers', [])
    if {'serverName': 'LHMCloseout'} not in allowed:
        allowed.append({'serverName': 'LHMCloseout'})
    asks = values[1].setdefault('permissions', {}).setdefault('ask', [])
    for tool in ('post_basicops_closeout', 'write_knowledge_closeout'):
        name = 'mcp__LHMCloseout__' + tool
        if name not in asks:
            asks.append(name)
    DEST.mkdir(mode=0o755, exist_ok=True)
    manifest = {}
    for name in ('closeout_mcp.py', 'host_closeout.py'):
        target = DEST / name
        if target.exists():
            shutil.copy2(target, backup / name)
        raw = (SOURCE / name).read_bytes()
        write(target, raw, 0o644)
        manifest[name] = hashlib.sha256(raw).hexdigest()
    unit = Path('/etc/systemd/system/lhm-task-closeout.service')
    if unit.exists():
        shutil.copy2(unit, backup / unit.name)
    write(unit, (SOURCE / unit.name).read_bytes(), 0o644)
    # Start and verify the broker before exposing it to workers.
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    subprocess.run(['systemctl', 'enable', '--now', 'lhm-task-closeout.service'], check=True)
    subprocess.run(['systemctl', 'restart', 'lhm-task-closeout.service'], check=True)
    subprocess.run(['systemctl', 'is-active', '--quiet', 'lhm-task-closeout.service'], check=True)
    for path, value in zip(paths, values):
        shutil.copy2(path, backup / path.name)
        (backup / path.name).chmod(0o600)
        write(path, (json.dumps(value, indent=2) + '\n').encode(), 0o640, 10002)
    write(backup / 'installed.json', (json.dumps({'source_commit': args.source_commit, 'files': manifest}, indent=2) + '\n').encode(), 0o600)
    print(json.dumps({'status': 'installed', 'backup': str(backup), 'source_sha256': manifest,
                      'source_commit': args.source_commit,
                      'vault_permissions': 'unchanged', 'existing_sessions': 'Reconnect LHMCloseout via /mcp; if absent, resume the saved session after config reload. No task replay.'}))


if __name__ == '__main__':
    main()
