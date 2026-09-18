#!/usr/bin/env python3
"""Install this scoped Ads digest release on the existing host, with rollback evidence."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

release=Path(sys.argv[1]).resolve()
commit=sys.argv[2]
source=release/'plugins/lhm-marketing-hub/skills/google-ads-monthly-review'
assert source.is_dir() and len(commit)==40
brain=Path('/home/hermes/.hermes/profiles/lhm_brain')
ads=Path('/home/hermes/.hermes/profiles/lhm_google_ads')
registry=Path('/home/claudeworker/.claude/plugins/installed_plugins.json')
entry=json.loads(registry.read_text())['plugins']['lhm-marketing-hub@lhm-marketing-skills'][0]
live_skill=Path(entry['installPath'])/'skills/google-ads-monthly-review'
dispatcher=Path('/usr/local/libexec/lhm-monthly-delivery-dispatcher')
patch=json.loads((source/'references/delivery-patch.json').read_text())
original=dispatcher.read_text()
assert hashlib.sha256(original.encode()).hexdigest()==patch['expected_sha256'], 'Dispatcher changed; reconcile before deployment'
assert original.count(patch['old'])==1
assert hashlib.sha256((live_skill/'SKILL.md').read_bytes()).hexdigest()=='1fba208694f855e6991a9b49876eb236466c64007eb96c0ee4029f0cc6115b4a', 'Review skill changed; reconcile first'
assert not live_skill.is_symlink(), 'Unexpected prior scoped deployment'
backup=release/'rollback';backup.mkdir()
shutil.copy2(dispatcher,backup/'monthly-delivery-dispatcher')
shutil.copytree(live_skill,backup/'google-ads-monthly-review')
shutil.copytree(ads/'skills/lhm-google-ads-dispatch',backup/'lhm-google-ads-dispatch')
jobs=json.loads((ads/'cron/jobs.json').read_text())
job=next(j for j in jobs['jobs'] if j['id']=='b0ec0fbc005c')
(backup/'ads-job.json').write_text(json.dumps(job,indent=2)+'\n')
assert job['enabled'] and job['schedule']['expr']=='0 17,18 * * 0'
# No installed-plugin registry changes: only this skill is sourced from the release.
prior=live_skill.with_name('google-ads-monthly-review.before-'+commit[:12])
live_skill.rename(prior);live_skill.symlink_to(source,target_is_directory=True)
profile_release=brain/'skill-releases/ads-weekly-digest'/commit
shutil.copytree(source/'scripts',profile_release)
shutil.copy2(source/'references/monday-digest.md',profile_release/'monday-digest.md')
for path in [profile_release,*profile_release.rglob('*')]:os.chown(path,10000,10000)
link=brain/'scripts/ads-weekly-digest'
assert not link.exists()
link.symlink_to('../skill-releases/ads-weekly-digest/'+commit,target_is_directory=True)
updated=original.replace(patch['old'],patch['new'])
compile(updated,str(dispatcher),'exec')
temp=dispatcher.with_suffix('.ads-digest.tmp');temp.write_text(updated);shutil.copystat(dispatcher,temp);os.replace(temp,dispatcher)
router=ads/'skills/lhm-google-ads-dispatch/SKILL.md'
router.write_text(router.read_text()+'''\n\n## Monday completion digest\n\nFor the authorised weekly cron, follow its completion-email stage. Invoke the deterministic script at `/opt/data/profiles/lhm_brain/scripts/ads-weekly-digest/ads-weekly-digest.py` with a complete terminal-client manifest. It reads worker-produced highlights and verified delivery receipts, renders the Lily newsletter, and sends to Michael only. Preserve its durable send receipt; do not resend uncertain outcomes. Manual tests use preview unless sending is explicitly requested. Read `/opt/data/profiles/lhm_brain/scripts/ads-weekly-digest/monday-digest.md` for the full contract.\n''')
prompt=(source/'references/hermes-router-prompt.txt').read_text()
subprocess.run(['docker','exec','--user','hermes','-e','HERMES_HOME=/opt/data/profiles/lhm_google_ads','hermes','hermes','cron','edit','b0ec0fbc005c','--prompt',prompt],check=True)
after=json.loads((ads/'cron/jobs.json').read_text());current=next(j for j in after['jobs'] if j['id']==job['id'])
assert current['enabled'] and current['schedule']==job['schedule'] and current['prompt']==prompt
assert current['deliver']==job['deliver']
receipt={'commit':commit,'source_plugin_version':'2.2.20','deployment':'scoped review skill and digest scripts; other installed plugin files and registry unchanged','prior_skill':str(prior),'dispatcher_backup':str(backup/'monthly-delivery-dispatcher'),'job_id':job['id'],'enabled':current['enabled'],'schedule':current['schedule'],'skill_sha256':hashlib.sha256((live_skill/'SKILL.md').read_bytes()).hexdigest(),'source_skill_sha256':hashlib.sha256((source/'SKILL.md').read_bytes()).hexdigest(),'script_sha256':hashlib.sha256((link/'ads-weekly-digest.py').read_bytes()).hexdigest()}
assert receipt['skill_sha256']==receipt['source_skill_sha256']
(release/'installation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
