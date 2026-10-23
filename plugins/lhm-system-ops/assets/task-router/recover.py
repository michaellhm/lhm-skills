#!/usr/bin/env python3
"""Explicit root recovery of a completed draft-only approval into its original Claude session."""
import json
import os
import sys
from pathlib import Path
import subprocess
import time
from dispatch import BASE, WORK, ID, verified, read, atomic, launch
from router import execution_handoff


def recover(request_id):
    if os.geteuid() != 0 or not ID.fullmatch(request_id):
        raise ValueError('Root and an exact registered request ID are required')
    request = verified(request_id)
    run, queued = WORK / request_id, BASE / 'runs' / request_id
    if json.loads(read(run/'request.json')) != request or not execution_handoff(request['provider'],request['instruction']):
        raise ValueError('Recovery requires the unchanged personal implementation approval')
    receipt = json.loads(read(run/'receipt.json'))
    if receipt.get('status') not in {'needs_review','failed'} or not receipt.get('thread_id'):
        raise ValueError('Existing conversation must be terminal and saved')
    if (run/'interactive-recovery.json').exists():
        raise ValueError('Recovery already admitted; inspect the saved session, never replay')
    active = subprocess.run(['systemctl','show','--property=ActiveState','--value','lhm-task-'+request_id],capture_output=True,text=True,timeout=10)
    if active.stdout.strip() in {'active','activating'}:
        raise ValueError('Prior worker is still active')
    mapping = json.loads(read(run/'workspace-location.json'))
    work, task = Path(mapping['workspace']),Path(mapping['task_directory'])
    expected=Path('/var/lib/lhm-client-workspaces/claude')/request['client_id']
    if work != expected or task != work/'tasks'/request_id:
        raise ValueError('Recovery must use the exact registered client workspace')
    authority={'request_id':request_id,'client_id':request['client_id'],
               'instruction_sha256':request['instruction_sha256'],'thread_id':receipt['thread_id'],
               'reason':'Michael requested repair of draft-only approval forwarding; native tool approval remains required'}
    marker=run/'interactive-recovery.json'
    fd=os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o440)
    with os.fdopen(fd,'w') as f:json.dump(authority,f,indent=2)
    os.chown(marker,0,10002);marker.chmod(0o440)
    archive=queued/'pre-interactive-recovery.json';atomic(archive,receipt)
    starting={'status':'starting','provider':'claude','request_id':request_id,
              'thread_id':receipt['thread_id'],'started_at':int(time.time()),'recovery':True}
    atomic(queued/'receipt.json',starting)
    # Avoid the supervisor re-reading the previous terminal receipt during startup.
    atomic(run/'receipt.json',starting);os.chown(run/'receipt.json',10002,10002)
    packet=json.loads((task/'task-context.json').read_text())
    packet.update(task_id=request['task_id'],task_name=request['title'],task_description=request['description'],
                  personal_instruction=request['instruction'],instruction_message_id=request['instruction_message_id'],
                  instruction_sha256=request['instruction_sha256'],discussion=request.get('context_messages',[]),
                  permission_ceiling='provider_tool_approval',interactive_recovery=authority)
    (task/'task-context.json').write_text(json.dumps(packet,indent=2)+'\n')
    launch({**request,'handoff_mode':'provider_execution'},run,work)
    return {'request_id':request_id,'thread_id':receipt['thread_id'],'status':'starting'}


if __name__=='__main__':print(json.dumps(recover(sys.argv[1])))
