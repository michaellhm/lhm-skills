#!/usr/bin/env python3
"""Resume one root-bound QA correction in the existing implementation conversation."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys

QA_ROOT=Path('/var/lib/lhm-prototype-feedback/qa-runs')
WORK_ROOT=Path('/var/lib/lhm-task-router')
WORKSPACE_ROOT=Path('/var/lib/lhm-client-workspaces/codex')


def digest(data): return hashlib.sha256(data).hexdigest()


def protected(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if info.st_uid != 0 or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022 or info.st_nlink != 1 or info.st_size > 1000000:
            raise ValueError('root-bound correction authority required')
        return json.loads(stream.read())


def atomic(path, value):
    temp=path.with_name(path.name+'.next')
    temp.write_text(json.dumps(value,sort_keys=True));temp.chmod(0o640);temp.replace(path)


def execute(authority_path):
    if os.geteuid()!=10001: raise ValueError('existing authenticated Codex worker required')
    authority_path=Path(authority_path)
    root=QA_ROOT
    if authority_path.parent.parent!=root or authority_path.name!='correction-authority.json':
        raise ValueError('correction authority path exceeds fixed QA root')
    authority=protected(authority_path)
    fields={'schema_version','request_id','batch_id','revision','thread_id','request_sha256','client_id','task_directory','workspace','reason','qa_sha256'}
    if set(authority)!=fields or authority['schema_version']!=1 or authority['revision'] not in (1,2):
        raise ValueError('closed bounded correction authority required')
    ident=authority['request_id']
    if not re.fullmatch(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*',ident): raise ValueError('invalid original request')
    run=WORK_ROOT/ident
    raw=(run/'request.json').read_bytes();request=json.loads(raw)
    if (digest(raw)!=authority['request_sha256'] or request['request_id']!=ident
            or request['client_id']!=authority['client_id'] or request['provider']!='codex'
            or request.get('feedback_authority',{}).get('batch_id')!=authority['batch_id']):
        raise ValueError('correction differs from original native request')
    workspace=WORKSPACE_ROOT/request['client_id']
    task=workspace/'tasks'/ident
    if str(workspace)!=authority['workspace'] or str(task)!=authority['task_directory']:
        raise ValueError('correction workspace differs from native task')
    previous=json.loads((run/'receipt.json').read_text())
    if previous.get('status')!='needs_review' or previous.get('thread_id')!=authority['thread_id']:
        raise ValueError('original worker conversation must have finished before correction')
    lock=(workspace/'.control/worker.lock').open('r')
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close();raise ValueError('another worker is active; correction must wait')
    corr=run/('qa-correction-'+str(authority['revision']))
    if corr.exists():
        lock.close();raise ValueError('unreceipted correction run requires root reconciliation')
    corr.mkdir(mode=0o750)
    receipt={**previous,'status':'running','qa_correction_revision':authority['revision']}
    atomic(run/'receipt.json',receipt)
    try:
        spec=importlib.util.spec_from_file_location('native_codex','/usr/local/libexec/lhm-wellness-codex-pilot.py')
        native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
        prompt=('Continue this SAME prototype feedback batch and conversation. Independent QA requested a bounded correction. '
                'Preserve the original active brief and source context; do not add later emails or other clients. '
                'Use prototype-revisions. Update existing task drafts/revised-source only in the registered Luminary prototype scope. '
                'Preserve reports and explain corrections. Do not publish, push, send email or alter live accounts. '
                'The root supervisor owns independent QA and delivery. Rebate/booking claims need evidence or remain omitted. '
                '\nTASK DIRECTORY: '+str(task)+'\nINDEPENDENT QA FINDINGS:\n'+authority['reason'])
        thread=native.conversation({'client_id':'central-router','task_type':'feedback','title':request['title'],
            'resume_thread_id':authority['thread_id']},prompt,corr,cwd=workspace,write=True,timeout=1200,read_only_integrations=True)
        if thread!=authority['thread_id']: raise ValueError('correction opened a different implementation conversation')
        files=[];total=0
        for path in sorted((task/'drafts').rglob('*')):
            if path.is_symlink(): raise ValueError('correction produced linked output')
            if path.is_file():
                if path.stat().st_size>10000000 or len(files)>=100:raise ValueError('bounded correction package exceeded')
                data=path.read_bytes();total+=len(data)
                if total>100000000:raise ValueError('bounded correction package exceeded')
                files.append({'relative':str(path.relative_to(task/'drafts')),'size_bytes':len(data),'sha256':digest(data)})
        receipt.update(status='needs_review',artifact_manifest=files,delivery_required=True)
    except Exception as exc:
        receipt.update(status='failed',error=str(exc)[:700])
    atomic(run/'receipt.json',receipt)
    lock.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('authority');args=parser.parse_args()
    execute(args.authority)
