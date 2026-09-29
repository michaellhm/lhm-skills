#!/usr/bin/env python3
"""Root-owned, allowlisted profile-asset installer; run from an exact Git export."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PROFILE = Path('/home/hermes/.hermes/profiles/lhm_brain')
JOB = '43c5187a2005'
FILES = {
    'meeting_prep.py': 'scripts/meeting_prep.py',
    'meeting-prep-runner.py': 'scripts/meeting-prep-runner.py',
    'lily-meeting-prep/SKILL.md': 'skills/lily-meeting-prep/SKILL.md',
    'lily-meeting-prep/references/runtime.md': 'skills/lily-meeting-prep/references/runtime.md',
    'lily-meeting-prep/references/editorial-feedback.md': 'skills/lily-meeting-prep/references/editorial-feedback.md',
}


def atomic(path, data, uid, gid, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data); out.flush(); os.fsync(out.fileno())
        os.chown(temporary, uid, gid); os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)


def update_job(fields):
    code = 'import json,sys;from cron.jobs import update_job;assert update_job('+repr(JOB)+',json.load(sys.stdin))'
    subprocess.run(['docker','exec','-i','--user','hermes',
        '-e','HERMES_HOME=/opt/data/profiles/lhm_brain','hermes',
        '/opt/hermes/.venv/bin/python','-c',code],
        input=json.dumps(fields), text=True, check=True, capture_output=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--commit',required=True)
    args=parser.parse_args()
    if os.geteuid()!=0 or not re.fullmatch('[0-9a-f]{40}',args.commit):
        raise SystemExit('Root and an exact source commit are required')
    source=Path(__file__).resolve().parent
    jobs=PROFILE/'cron/jobs.json'
    before=next(j for j in json.loads(jobs.read_text())['jobs'] if j['id']==JOB)
    if before.get('fire_claim'):raise SystemExit('Briefing is active; install after it exits')
    if before['schedule']['expr']!='0 * * * *':raise SystemExit('Unexpected scheduler cadence')
    for name in ('meeting_prep.py','meeting-prep-runner.py'):
        compile((source/name).read_text(),name,'exec')
    backup=Path('/root/lhm-meeting-prep-recovery')/args.commit
    backup.mkdir(parents=True,exist_ok=False,mode=0o700)
    (backup/'job-before.json').write_text(json.dumps(before,indent=2))
    originals={};hashes={}
    for name,destination in FILES.items():
        target=PROFILE/destination
        if target.exists():
            st=target.stat();originals[destination]={'uid':st.st_uid,'gid':st.st_gid,'mode':st.st_mode & 0o777}
            saved=backup/destination;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        else:originals[destination]=None
        hashes[destination]=hashlib.sha256((source/name).read_bytes()).hexdigest()
    (backup/'metadata.json').write_text(json.dumps(originals,indent=2))
    try:
        for name,destination in FILES.items():
            target=PROFILE/destination
            meta=originals[destination] or {'uid':10000,'gid':10000,'mode':0o700}
            atomic(target,(source/name).read_bytes(),**meta)
        update_job({'script':'meeting-prep-runner.py','no_agent':True,
                    'prompt':'Run the deterministic meeting-prep runner. Success requires verified recipient delivery or evidenced no-client classification. Research and recovery use bounded durable state.'})
        after=next(j for j in json.loads(jobs.read_text())['jobs'] if j['id']==JOB)
        for field in ('id','schedule','deliver','enabled','skills','workdir'):
            assert after.get(field)==before.get(field),field+' changed'
        assert after['no_agent'] and after['script']=='meeting-prep-runner.py'
        for destination,digest in hashes.items():
            assert hashlib.sha256((PROFILE/destination).read_bytes()).hexdigest()==digest
        result={'commit':args.commit,'job_id':JOB,'files':hashes,'backup':str(backup),'status':'installed_verified'}
        (backup/'installation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
    except Exception:
        for destination,meta in originals.items():
            target=PROFILE/destination
            if meta:atomic(target,(backup/destination).read_bytes(),**meta)
            elif target.exists():target.unlink()
        update_job({k:before.get(k) for k in ('script','no_agent','prompt')})
        raise


if __name__=='__main__':main()
