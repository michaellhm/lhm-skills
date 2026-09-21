#!/usr/bin/env python3
"""Explicitly approved root installer for this workflow only; leaves schedule paused."""
import argparse,base64,json,os,pwd,re,subprocess
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);a=p.parse_args()
if os.geteuid()!=0 or not re.fullmatch('[0-9a-f]{40}',a.commit):raise SystemExit('Root and immutable commit required')
skill=Path(__file__).resolve().parents[1]
if skill!=Path('/srv/lhm-weekly-web-releases')/a.commit/'skill':raise SystemExit('Immutable release location required')
brain=Path('/home/hermes/.hermes/profiles/lhm_brain');state=brain/'workspace/weekly-web-project-brief';hermes=pwd.getpwnam('hermesagent');worker=pwd.getpwnam('codexworker')
active=subprocess.run(['systemctl','show','lhm-weekly-web-brief.service','--property=ActiveState','--value'],capture_output=True,text=True).stdout.strip()
if active in ('active','activating','deactivating'):raise SystemExit('Stop/reconcile the active worker before installation')
queue=state/'incoming'
if queue.exists() and list(queue.glob('*.json')):raise SystemExit('Reconcile pending requests before installation')
queue.mkdir(exist_ok=True);os.chown(queue,hermes.pw_uid,hermes.pw_gid)
runtime=Path('/run/lhm-weekly-web-brief');runtime.mkdir(exist_ok=True)
at=datetime.now(ZoneInfo('Australia/Melbourne'));watch_week=(at.date()-timedelta(days=at.weekday())).isoformat()
prior_config=json.loads(Path('/etc/lhm-weekly-web-brief.json').read_text()) if Path('/etc/lhm-weekly-web-brief.json').exists() else {}
config={'watch_from_week':prior_config.get('watch_from_week',watch_week),'commit':a.commit,'skill':str(skill),'state':str(state),'knowledge_source':'google-drive','baseline':'/srv/lhm-weekly-web-baseline','timeout':3600}
service='''[Unit]
Description=Weekly website brief: Codex research and independent review
OnFailure=lhm-weekly-web-watch.service
[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/python3 SKILL/scripts/weekly_runtime.py queue
TimeoutStartSec=3h
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
RuntimeDirectory=lhm-weekly-web-brief
ReadWritePaths=STATE /home/codexworker/weekly-web-runs /home/codexworker/.codex -/home/codexworker/.mcp-auth /run/lhm-weekly-web-brief
'''.replace('SKILL',str(skill)).replace('STATE',str(state))
path='''[Unit]
Description=Watch native Hermes weekly web brief requests
[Path]
PathExistsGlob=QUEUE/*.json
Unit=lhm-weekly-web-brief.service
[Install]
WantedBy=multi-user.target
'''.replace('QUEUE',str(queue))
watch_service='''[Unit]
Description=Check weekly web brief completion and receipt-backed failure alerts
Requires=docker.service
After=docker.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 SKILL/scripts/supervise.py
TimeoutStartSec=4min
'''.replace('SKILL',str(skill))
watch_timer='''[Unit]
Description=Watch weekly web brief independently of its worker and Hermes scheduler
[Timer]
OnCalendar=*-*-* *:0/5:00
Persistent=true
AccuracySec=5s
Unit=lhm-weekly-web-watch.service
[Install]
WantedBy=timers.target
'''
files={Path('/etc/lhm-weekly-web-brief.json'):json.dumps(config,indent=2),Path('/etc/systemd/system/lhm-weekly-web-brief.service'):service,Path('/etc/systemd/system/lhm-weekly-web-brief.path'):path}
files.update({Path('/etc/systemd/system/lhm-weekly-web-watch.service'):watch_service,Path('/etc/systemd/system/lhm-weekly-web-watch.timer'):watch_timer})
backup=state/('runtime-install-'+a.commit+'.json')
if not backup.exists():
 prior={str(p):base64.b64encode(p.read_bytes()).decode() if p.exists() else None for p in files}
 backup.write_text(json.dumps({'commit':a.commit,'prior_files_base64':prior,'prior_path_enabled':subprocess.run(['systemctl','is-enabled','lhm-weekly-web-brief.path'],capture_output=True,text=True).stdout.strip(),'prior_watch_enabled':subprocess.run(['systemctl','is-enabled','lhm-weekly-web-watch.timer'],capture_output=True,text=True).stdout.strip(),'schedule_enabled_by_installer':False},indent=2))
for path,text in files.items():
 tmp=path.with_name('.'+path.name+'.new');tmp.write_text(text);os.chmod(tmp,0o600 if path.suffix=='.json' else 0o644);os.replace(tmp,path)
work=Path(worker.pw_dir)/'weekly-web-runs';work.mkdir(exist_ok=True);os.chown(work,worker.pw_uid,worker.pw_gid);os.chmod(work,0o700)
subprocess.run(['systemctl','daemon-reload'],check=True)
print(json.dumps({'state':'installed_not_enabled','commit':a.commit,'rollback_record':str(backup)}))
