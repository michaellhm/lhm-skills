#!/usr/bin/env python3
"""Root-only scoped installation; run from a staged directory containing these four assets."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import time
import yaml

stage = Path(__file__).resolve().parent
profile = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
backup = Path('/var/lib/lhm-codex-pilot-build') / ('ted-' + str(int(time.time())))
backup.mkdir(parents=True, mode=0o700)
worker = Path('/usr/local/libexec/lhm-wellness-codex-pilot.py')
skill = profile / 'skills/basicops-agent-user/SKILL.md'
config = profile / 'config.yaml'
for path in (worker, skill, config):
    shutil.copy2(path, backup / path.name)
for src, target, mode in [('lhm-codex-session-worker', worker, 0o755),
                          ('ted_codex_sessions.py', profile / 'codex_sessions_mcp.py', 0o644),
                          ('SKILL.md', skill, 0o644)]:
    shutil.copyfile(stage / src, target)
    os.chown(target, 0, 10000)
    target.chmod(mode)
registry = profile / 'codex-session-pilot.json'
if registry.exists():
    shutil.copy2(registry, backup / registry.name)
    entries = json.loads(registry.read_text())
else:
    entries = {'agent_user_id': 82491, 'tasks': {}}
entries['tasks']['2216123'] = {'enabled': True, 'client_id': 'wellness-chiropractic',
                              'project_id': 49020, 'reviewer_id': 36398}
registry.write_text(json.dumps(entries, indent=2) + '\n')
os.chown(registry, 0, 10000)
registry.chmod(0o640)
state = profile / 'codex-session-state'
state.mkdir(exist_ok=True)
os.chown(state, 10000, 10000)
state.chmod(0o750)
# Parse YAML on the host without printing existing configuration.
c = yaml.safe_load(config.read_text())
c.setdefault('mcp_servers', {})['codex_sessions'] = {
    'command': '/opt/hermes/.venv/bin/python',
    'args': ['/opt/data/profiles/lhm_chief_of_staff/codex_sessions_mcp.py'],
    'tools': {'include': ['codex_session_submit', 'codex_session_status']}}
config.write_text(yaml.safe_dump(c, sort_keys=False))

units = {
'lhm-ted-codex-handback.service': '''[Unit]
Description=Return registered Codex session results to TED BasicOps tasks
After=docker.service network-online.target
Requires=docker.service
[Service]
Type=oneshot
ExecStart=/usr/bin/docker exec --user hermes hermes /opt/hermes/.venv/bin/python /opt/data/profiles/lhm_chief_of_staff/codex_sessions_mcp.py --reconcile
TimeoutStartSec=120
NoNewPrivileges=true
PrivateTmp=true
''',
'lhm-ted-codex-handback.timer': '''[Unit]
Description=Check registered TED Codex results
[Timer]
OnBootSec=30
OnUnitActiveSec=30
Unit=lhm-ted-codex-handback.service
[Install]
WantedBy=timers.target
'''}
for name, content in units.items():
    target = Path('/etc/systemd/system') / name
    if target.exists():
        shutil.copy2(target, backup / name)
    target.write_text(content)
subprocess.run(['systemctl', 'daemon-reload'], check=True)
subprocess.run(['systemctl', 'enable', '--now', 'lhm-ted-codex-handback.timer'], check=True)
print(json.dumps({'installed': True, 'backup': str(backup), 'registered_task': 2216123,
                  'gateway_reload_required': True}))
