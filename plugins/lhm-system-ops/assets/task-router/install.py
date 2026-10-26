#!/usr/bin/env python3
"""Scoped root install, additive MCP allowlists, timestamped rollback assets."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import yaml

stage = Path(__file__).resolve().parent
profile = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
queue = Path('/home/hermes/.hermes/profiles/lhm_brain/dispatch/task-router')
backup = Path('/var/lib/lhm-codex-pilot-build') / ('central-router-' + str(int(time.time())))
backup.mkdir(mode=0o700)
for path in [profile / 'config.yaml', profile / 'skills/basicops-agent-user/SKILL.md',
             Path('/usr/local/libexec/lhm-wellness-codex-pilot.py'), profile / 'task-router.json']:
    if path.exists():
        shutil.copy2(path, backup / path.name)
for directory in [profile / 'task-router', profile / 'task-router-state', queue,
                  queue / 'incoming', queue / 'processed', queue / 'runs', Path('/usr/local/libexec/lhm-task-router')]:
    directory.mkdir(parents=True, exist_ok=True)
    os.chown(directory, 0, 10000)
    directory.chmod(0o755 if 'libexec' in str(directory) else (0o750 if directory in [queue, queue / 'processed', queue / 'runs'] else 0o770))
Path('/var/lib/lhm-task-router').mkdir(exist_ok=True, mode=0o755)
Path('/var/lib/lhm-task-router').chmod(0o755)
for name in ['router.py', 'server.py']:
    shutil.copy2(stage / name, profile / 'task-router' / name)
    os.chown(profile / 'task-router' / name, 0, 10000)
    (profile / 'task-router' / name).chmod(0o640)
for name in ['dispatch.py', 'worker.py', 'interactive.py', 'recover.py', 'recover_admission.py', 'site_workspace.py', 'request_site_publish.py', 'site_source_check.py', 'client_directory.py', 'refresh_knowledge.py', 'workspaces.py', 'delivery.py', 'drive_publisher.py', 'router.py']:
    shutil.copy2(stage / name, Path('/usr/local/libexec/lhm-task-router') / name)
    (Path('/usr/local/libexec/lhm-task-router') / name).chmod(0o755)
# Install the discoverable site workflow into the Hermes coordination profiles.
site_skill = stage.parents[1] / 'skills/hermes-site-workspace/SKILL.md'
site_contract = stage / 'SITE-WORKSPACES.md'
for name in ['lhm_brain', 'lhm_chief_of_staff']:
    destination = Path('/home/hermes/.hermes/profiles') / name / 'skills/hermes-site-workspace'
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(site_skill, destination / 'SKILL.md')
    shutil.copy2(site_contract, destination / 'HOST-CONTRACT.md')
    text = (destination / 'SKILL.md').read_text().replace('../../assets/task-router/SITE-WORKSPACES.md', 'HOST-CONTRACT.md')
    (destination / 'SKILL.md').write_text(text)
    for item in [destination, destination / 'SKILL.md', destination / 'HOST-CONTRACT.md']:
        os.chown(item, 0, 10000)
        item.chmod(0o755 if item.is_dir() else 0o644)
shutil.copy2(stage / 'lhm-codex-session-worker', '/usr/local/libexec/lhm-wellness-codex-pilot.py')
execution_settings = Path('/home/claudeworker/.config/lhm-bridge/task-execution.settings.json')
execution_settings.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(stage / 'task-execution.settings.json', execution_settings)
os.chown(execution_settings, 0, 10002)
execution_settings.chmod(0o640)
Path('/usr/local/libexec/lhm-wellness-codex-pilot.py').chmod(0o755)
skill = profile / 'skills/basicops-agent-user/SKILL.md'
shutil.copy2(stage / 'SKILL.md', skill)
os.chown(skill, 0, 10000)
skill.chmod(0o644)
clients = json.loads(Path('/home/hermes/.hermes/profiles/lhm_brain/config/client-handback-targets.json').read_text())['clients']
# Reuse verified registries; never discover folders by a guessed client path.
ads = json.loads(Path('/home/hermes/.hermes/profiles/lhm_brain/config/google-ads-clients.json').read_text())['clients']
for key, value in ads.items():
    if key not in clients and value.get('evidence_prefix') and value.get('drive_folder_url'):
        clients[key] = {'name': value['name'], 'vault_prefix': value['evidence_prefix'],
                        'drive_folder_query': 'exact registered folder ' + value['drive_folder_url'],
                        'basicops_task_ids': value.get('basicops_task_ids', [])}
prior_config = json.loads((profile / 'task-router.json').read_text()) if (profile / 'task-router.json').exists() else {}
config = {'schema_version': 1, 'require_client_directory': True, 'agent_user_id': 82491, 'reviewer_id': 36398,
          'providers': {'codex': True, 'claude': True}, 'clients': clients}
if prior_config.get('codex_host_id'):
    config['codex_host_id'] = prior_config['codex_host_id']
target = profile / 'task-router.json'
target.write_text(json.dumps(config, indent=2) + '\n')
os.chown(target, 0, 10000)
target.chmod(0o640)
settings = profile / 'config.yaml'
c = yaml.safe_load(settings.read_text())
c.setdefault('mcp_servers', {})['task_router'] = {
    'command': '/opt/hermes/.venv/bin/python',
    'args': ['/opt/data/profiles/lhm_chief_of_staff/task-router/server.py'],
    'tools': {'include': ['task_route_preview', 'task_route_submit', 'task_route_status', 'task_client_lookup']}}
route = c['platforms']['webhook']['extra']['routes']['basicops']
if 'task_router' not in route['toolsets']:
    route['toolsets'].append('task_router')
settings.write_text(yaml.safe_dump(c, sort_keys=False))
unit = '''[Unit]
Description=Verify TED central task requests and supervise saved provider sessions
After=docker.service network-online.target
Requires=docker.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/libexec/lhm-task-router/dispatch.py
TimeoutStartSec=300
UMask=0027
'''
timer = '''[Unit]
Description=Dispatch and return TED central provider tasks
[Timer]
OnBootSec=30
OnUnitActiveSec=20
Unit=lhm-task-router.service
[Install]
WantedBy=timers.target
'''
for name, body in [('lhm-task-router.service', unit), ('lhm-task-router.timer', timer)]:
    path = Path('/etc/systemd/system') / name
    if path.exists():
        shutil.copy2(path, backup / name)
    path.write_text(body)
refresh_unit = '''[Unit]
Description=Read shared client knowledge into TED's isolated routing cache
After=network-online.target
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/libexec/lhm-task-router/refresh_knowledge.py
TimeoutStartSec=510
UMask=0027
'''
refresh_timer = '''[Unit]
Description=Refresh TED shared client knowledge without bidirectional writes
[Timer]
OnBootSec=20
OnUnitActiveSec=300
Unit=lhm-task-router-knowledge.service
[Install]
WantedBy=timers.target
'''
for name, body in [('lhm-task-router-knowledge.service', refresh_unit), ('lhm-task-router-knowledge.timer', refresh_timer)]:
    path = Path('/etc/systemd/system') / name
    if path.exists():
        shutil.copy2(path, backup / name)
    path.write_text(body)
subprocess.run(['systemctl', 'daemon-reload'], check=True)
subprocess.run(['systemctl', 'enable', '--now', 'lhm-task-router-knowledge.timer'], check=True)
subprocess.run(['systemctl', 'enable', '--now', 'lhm-task-router.timer'], check=True)
print(json.dumps({'installed': True, 'backup': str(backup), 'registered_clients': len(clients), 'ted_reload_required': True}))
