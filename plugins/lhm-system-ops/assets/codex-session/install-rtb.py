#!/usr/bin/env python3
"""Install the prepared RTB route with both readiness switches OFF."""
from pathlib import Path
import os
import shutil
import subprocess
import time

STAGE = Path(__file__).resolve().parent
PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
BACKUP = Path('/var/lib/lhm-codex-pilot-build') / ('rtb-backup-' + str(int(time.time())))
BACKUP.mkdir(mode=0o700)
registry = PROFILE / 'codex-session-pilot.json'
shutil.copy2(registry, BACKUP / registry.name)
subprocess.run(['/usr/bin/python3', str(STAGE / 'provision-rtb.py')], check=True)
for source, target, mode in [
    ('lhm-codex-session-worker', Path('/usr/local/libexec/lhm-wellness-codex-pilot.py'), 0o755),
    ('ted_codex_sessions.py', PROFILE / 'codex_sessions_mcp.py', 0o644),
    ('SKILL.md', PROFILE / 'skills/basicops-agent-user/SKILL.md', 0o644),
    ('rtb-delivery.py', Path('/usr/local/libexec/lhm-rtb-codex-delivery.py'), 0o755),
]:
    if target.exists():
        shutil.copy2(target, BACKUP / target.name)
    shutil.copyfile(STAGE / source, target)
    os.chown(target, 0, 10000)
    target.chmod(mode)
receipts = PROFILE / 'codex-session-deliveries'
receipts.mkdir(exist_ok=True)
os.chown(receipts, 0, 10000)
receipts.chmod(0o750)
dropin = Path('/etc/systemd/system/lhm-wellness-codex-pilot.service.d')
dropin.mkdir(exist_ok=True)
(dropin / 'rtb.conf').write_text('[Service]\nTimeoutStartSec=1500\nReadWritePaths=/home/codexworker/clients/raise-the-bar\n')
service = Path('/etc/systemd/system/lhm-rtb-codex-delivery.service')
service.write_text('''[Unit]
Description=Verify and deliver approved RTB Codex review artifacts
After=network-online.target docker.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /usr/local/libexec/lhm-rtb-codex-delivery.py
TimeoutStartSec=900
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
''')
Path('/etc/systemd/system/lhm-rtb-codex-delivery.timer').write_text('''[Unit]
Description=Check approved RTB Codex draft delivery
[Timer]
OnBootSec=60
OnUnitActiveSec=60
Unit=lhm-rtb-codex-delivery.service
[Install]
WantedBy=timers.target
''')
subprocess.run(['systemctl', 'daemon-reload'], check=True)
# Deliberately do not enable the delivery timer or set readiness before normal Drive OAuth/preflight.
print('RTB installed but inactive; normal Google Drive connection and activation preflight required. Backup: ' + str(BACKUP))
