"""CTO investigation -> one Intervention task and a paired, resumable Codex repair chat."""
import html
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
from urllib.parse import quote

CONFIG = Path('/etc/lhm-cto-codex-handoff.json')
STATE = Path('/var/lib/lhm-cto-codex-handoff')
WORK = Path('/home/codexworker/cto-repairs')
REPO = 'https://github.com/michaellhm/lhm-skills.git'
HOST = 'remote-control:env_e_6ad97900b7388321a12a5df9ddf1b2b2'


def atomic(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2)+'\n');temp.chmod(0o600);temp.replace(path)


def api(name, arguments):
    code = ('import json,sys;sys.path.insert(0,"/opt/data/profiles/lhm_chief_of_staff/task-router");'
            'import server;r=json.load(sys.stdin);print(json.dumps(server.instance().api(r["name"],r["arguments"])))')
    r = subprocess.run(['docker','exec','-i','--user','hermes','hermes','/opt/hermes/.venv/bin/python','-c',code],
                       input=json.dumps({'name':name,'arguments':arguments}),capture_output=True,text=True,timeout=45,check=True)
    return json.loads(r.stdout)


def items(value):
    return value if isinstance(value,list) else value.get('data',[])


def packet(request, findings):
    # Workflow resume tokens never leave the governed root callback lane.
    return {k:request.get(k) for k in ['request_id','parent_run_id','capability_incident_id','objective','acceptance_tests','return_point']} | {
        'investigation': {k:findings.get(k) for k in ['summary','decision','sources','questions_for_chief','next_action']},
        'authority':'Prepare a scoped repair and tests. Michael reviews in this Codex conversation. No main merge, live deployment, root access or copied credentials.',
        'repository':REPO}


def handoff(request, findings):
    incident=request['capability_incident_id']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,99}',incident):raise ValueError('Invalid incident identity')
    STATE.mkdir(exist_ok=True,mode=0o700)
    with (STATE/(incident+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _handoff(request,findings)


def _handoff(request, findings):
    cfg=json.loads(CONFIG.read_text())
    if not cfg.get('enabled') or cfg.get('project_id') != 69105 or cfg.get('repository') != REPO:
        raise ValueError('CTO visible handoff is not configured for the verified Intervention board')
    incident=request['capability_incident_id']
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,99}',incident):raise ValueError('Invalid incident identity')
    STATE.mkdir(exist_ok=True,mode=0o700)
    state_path=STATE/(incident+'.json');saved=json.loads(state_path.read_text()) if state_path.exists() else {}
    title=('CTO: '+request.get('objective',incident).splitlines()[0])[:160];marker='LHM CTO incident: '+incident
    if api('get_current_user',{}).get('id') != 82491:raise ValueError('TED connector identity mismatch')
    project=api('get_project',{'projectId':69105})
    if project.get('id') != 69105 or project.get('title') != '*The Intervention':raise ValueError('Intervention board identity mismatch')
    if not saved.get('task_id'):
        matches=[t for t in items(api('list_tasks',{'filter_project':[69105],'filter_title':title,'limit':50}))
                 if t.get('title')==title and marker in t.get('description','')]
        if len(matches)>1:raise ValueError('Duplicate incident tasks; inspect instead of creating another')
        if matches:task=matches[0]
        else:
            if saved.get('task_creation_pending'):raise ValueError('Prior task-create outcome unknown; inspect board, do not duplicate')
            atomic(state_path,{'task_creation_pending':True,'incident':incident})
            body=('<p>'+html.escape(marker)+'</p><p><strong>Objective</strong><br>'+html.escape(request['objective'])
                  +'</p><p><strong>CTO investigation</strong><br>'+html.escape(str(findings.get('summary','')))
                  +'</p><p><strong>Acceptance tests</strong></p><ul>'+''.join('<li>'+html.escape(str(x))+'</li>' for x in request['acceptance_tests'])
                  +'</ul><p>Parent: '+html.escape(request['parent_run_id'])+'</p><p>Repair work continues in the linked Codex chat. Michael handles further approvals there. A prepared fix is not a merged or deployed fix.</p>')
            created=api('create_task',{'projectId':69105,'assignee':82491,'status':'In Progress','title':title,'description':body})
            task_id=created if type(created) is int else created['id']
            task=api('get_task',{'taskId':task_id})
        saved={'task_id':task['id'],'task_url':task['url'],'incident':incident}
        atomic(state_path,saved)
    task=api('get_task',{'taskId':saved['task_id']})
    if task.get('project',{}).get('id') != 69105 or marker not in task.get('description',''):
        raise ValueError('Saved task no longer belongs to this incident and board')
    if saved.get('chat_url'):
        return saved  # Never replay repair production on a callback retry.
    if saved.get('worker_started'):raise ValueError('Repair worker already admitted; inspect its saved session')
    slug=re.sub('[^a-z0-9-]+','-',incident.lower()).strip('-')[:90]
    work=WORK/slug;work.mkdir(parents=True,exist_ok=True,mode=0o750);os.chown(work,10001,10001)
    source=work/'source';run=work/'handoff';run.mkdir(exist_ok=True,mode=0o750);os.chown(run,10001,10001)
    base=cfg.get('base_ref','main')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,120}',base) or '..' in base:raise ValueError('Invalid configured source ref')
    user=['/usr/sbin/runuser','-u','codexworker','--','env','HOME=/home/codexworker']
    clone_error=None
    if not source.exists():
        try:
            subprocess.run([*user,'git','clone','--quiet','--single-branch','--branch',base,REPO,str(source)],capture_output=True,text=True,check=True,timeout=90)
            subprocess.run([*user,'git','-C',str(source),'checkout','-b','cto/'+slug],capture_output=True,text=True,check=True,timeout=15)
        except (subprocess.SubprocessError,OSError):
            clone_error='Source checkout failed; troubleshoot the exact repository connection in this Codex chat. Do not invent source contents.'
    if not (source/'.git').is_dir():
        clone_error='The source checkout is unavailable; troubleshoot repository access in this existing Codex chat.'
    data=packet(request,findings);data.update(task_id=task['id'],task_url=task['url'],source_ref=base,source_error=clone_error,
                                            workspace=str(work),source_workspace=str(source),branch='cto/'+slug)
    p=run/'task-context.json';p.write_text(json.dumps(data,indent=2)+'\n');os.chown(p,10001,10001);p.chmod(0o640)
    saved.update(worker_started=True,request_id=request['request_id'],workspace=str(work),status='starting');atomic(state_path,saved)
    log=open(run/'launcher.stderr','w')
    child=subprocess.Popen([*user,'python3','/usr/local/libexec/lhm-cto-codex-handoff-worker.py',str(run)],stderr=log,stdout=log)
    try:
        while child.poll() is None or (run/'session.json').exists():
            session=run/'session.json'
            if session.exists() and not saved.get('chat_url'):
                uid=str(uuid.UUID(json.loads(session.read_text())['thread_id']))
                url='codex://threads/'+uid+'?hostId='+quote(cfg.get('codex_host_id',HOST),safe='')
                msg='<p><strong>CTO repair in Codex</strong></p><p><a href="'+html.escape(url,quote=True)+'">Open existing Codex repair chat</a></p><p>The investigation and original outcome are in the task packet. Continue feedback and permission decisions in this chat; no deployment is implied.</p><p>'+html.escape(marker)+'</p>'
                api('create_message_in_task',{'taskId':task['id'],'message':msg})
                if not any(url in m.get('message','') or html.escape(url,quote=True) in m.get('message','') for m in items(api('list_messages_in_task',{'taskId':task['id'],'limit':50}))):
                    raise ValueError('Codex link readback failed')
                saved.update(chat_url=url,thread_id=uid,status='in_codex',link_verified=True);atomic(state_path,saved)
            if child.poll() is not None:break
            time.sleep(1)
        if not saved.get('chat_url'):raise ValueError('Codex did not return a saved conversation; task retained for troubleshooting')
        saved['initial_turn_finished']=True;saved['initial_turn_exit_code']=child.returncode;atomic(state_path,saved)
        return saved
    finally:
        log.close()
