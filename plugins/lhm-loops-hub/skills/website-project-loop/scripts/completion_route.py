#!/usr/bin/env python3
"""Signed webhook's exact completion command filter; other events retain Lily chat."""
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path('/opt/data/profiles/lhm_project_manager')


def parse(text):
    text=re.sub(r'</(?:p|div)>|<br\s*/?>','\n',text,flags=re.I)
    plain=html.unescape(re.sub('<[^>]+>',' ',text))
    found=re.search(r'\bwebsite done:\s*([^|\n]{1,200})\s*\|\s*evidence:\s*(https://[^\s|<>]+)(?:\s*\|\s*next:\s*([^\n]{1,500}))?',plain,re.I)
    if not found:return None
    return {'item':found[1].strip(),'evidence':found[2].strip(),'next_action':(found[3] or '').strip()}


def main():
    payload=json.load(sys.stdin)
    # Preserve the existing sanitized event capture for every request.
    subprocess.run([sys.executable,str(ROOT/'scripts/lily-basicops-event-capture.py')],input=json.dumps(payload),text=True,capture_output=True,check=True,timeout=10)
    data=payload.get('data',payload);context=data.get('context',{})
    command=parse(str(data.get('request','')))
    if command and context.get('userId') in [36398,36401,36402,36403,63471] and isinstance(context.get('taskId'),int):
        mid=context.get('messageId','')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',mid):raise ValueError('Invalid source message ID')
        queue=ROOT/'workspace/website-loop/completions/incoming';queue.mkdir(parents=True,exist_ok=True)
        receipt=queue.parent/'receipts'/ (mid+'.json')
        if not receipt.exists():
            target=queue/(mid+'.json');temp=queue/('.'+mid+'.'+str(os.getpid())+'.tmp')
            temp.write_text(json.dumps(dict(command,task_id=context['taskId'],source_message_id=mid)))
            try:os.link(temp,target)
            except FileExistsError:pass
            finally:temp.unlink(missing_ok=True)
        print(json.dumps({'__hermes_ignore__':True}));return
    print(json.dumps(payload))


if __name__=='__main__':main()
