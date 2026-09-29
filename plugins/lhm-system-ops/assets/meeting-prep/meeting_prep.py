#!/usr/bin/env python3
"""Calendar gate and fixed-recipient, receipt-backed Mailgun delivery."""
import re, argparse, fcntl, hashlib, json, os, sys, tempfile, urllib.request, urllib.parse, base64
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE=Path('/opt/data/profiles/lhm_brain/workspace/meeting-prep-daily')
TZ=ZoneInfo('Australia/Melbourne')
TO='michael@localhealthmarketing.com.au'
CC='kristalyn@localhealthmarketing.com.au'
DOMAIN='mg.brieflyflow.io'
API='https://api.mailgun.net/v3/'+DOMAIN

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.')
    with os.fdopen(fd,'w') as f:
        json.dump(value,f,indent=2); f.flush(); os.fsync(f.fileno())
    os.chmod(tmp,0o600); os.replace(tmp,path)

def now(): return datetime.now(TZ)
def window(at):
    start=datetime.combine(at.astimezone(TZ).date()+timedelta(days=1),datetime.min.time(),TZ)
    return start,start+timedelta(days=1)
def key(date,kind='brief'):
    return hashlib.sha256(f'{kind}|{date}|{TO}|{CC}'.encode()).hexdigest()
def receipt(date,kind='brief'): return BASE/'receipts'/(key(date,kind)+'.json')
def google():
    os.environ['HERMES_HOME']='/opt/data/.hermes'
    sys.path.insert(0,'/opt/data/skills/productivity/google-workspace/scripts')
    import google_api
    return google_api

def gate(at=None,force=False,date=None):
    at=at or now()
    if not force and at.astimezone(TZ).hour!=13:
        return {'wakeAgent':False,'reason':'outside_13_melbourne'}
    if date:
        start=datetime.strptime(date,'%Y-%m-%d').replace(tzinfo=TZ)
        end=start+timedelta(days=1)
    else:
        start,end=window(at)
    r=receipt(str(start.date()))
    if r.exists():return {'wakeAgent':False,'reason':'existing_delivery_record','receipt':str(r)}
    service=google().build_service('calendar','v3')
    identity=service.calendars().get(calendarId='primary').execute()
    if identity.get('id','').lower()!=TO:raise RuntimeError('Unexpected calendar identity')
    events=[]; token=None
    while True:
        response=service.events().list(calendarId='primary',timeMin=start.isoformat(),timeMax=end.isoformat(),singleEvents=True,orderBy='startTime',maxResults=250,pageToken=token).execute()
        for e in response.get('items',[]):
            if e.get('status')=='cancelled':continue
            if any(a.get('self') and a.get('responseStatus')=='declined' for a in e.get('attendees',[])):continue
            if e.get('eventType') in ('outOfOffice','workingLocation','focusTime'):continue
            events.append({k:e[k] for k in ('id','summary','description','start','end','attendees','organizer','htmlLink','eventType') if k in e})
        token=response.get('nextPageToken')
        if not token:break
    p=BASE/'runs'/str(start.date())/'calendar.json'
    save(p,{'date':str(start.date()),'timezone':str(TZ),'calendar':TO,'events':events,'checked_at':at.isoformat()})
    return {'wakeAgent':bool(events),'meeting_date':str(start.date()),'calendar_file':str(p),'candidate_events':len(events),'reason':'calendar_checked'}

def mailgun(path,data=None,query=None):
    import shlex
    secret=os.environ.get('MAILGUN_API_KEY')
    if not secret:
        for line in Path('/opt/data/.env').read_text().splitlines():
            line=line.strip().removeprefix('export ')
            if line.startswith('MAILGUN_API_KEY='):
                values=shlex.split(line.split('=',1)[1],comments=True)
                secret=values[0] if values else None
                break
    if not secret:raise RuntimeError('Mailgun configuration unavailable')
    url=API+path
    if query:url+='?'+urllib.parse.urlencode(query)
    auth=base64.b64encode(('api:'+secret).encode()).decode()
    req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode() if data else None,headers={'Authorization':'Basic '+auth})
    with urllib.request.urlopen(req,timeout=45) as response:return json.load(response)

def send(date,subject,body,kind='brief'):
    datetime.strptime(date,'%Y-%m-%d')
    if not subject.strip() or not body.strip():raise ValueError('Empty email')
    if re.search(r'cliniko', subject + '\n' + body, re.I):
        raise ValueError('Excluded topic in meeting brief; revise before sending')
    BASE.mkdir(parents=True,exist_ok=True)
    with (BASE/'.send.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        p=receipt(date,kind)
        if p.exists():return {'status':'deduplicated','receipt':str(p)}
        r={'kind':kind,'date':date,'to':TO,'cc':CC,'state':'sending','started_at':now().isoformat(),'subject':subject,'body_sha256':hashlib.sha256(body.encode()).hexdigest()}
        save(p,r) # Persist before network: uncertain responses must never auto-resend.
        try:
            response=mailgun('/messages',{'from':'Lily — LHM Meeting Prep <lily@mg.brieflyflow.io>','to':TO,'cc':CC,'h:Reply-To':TO,'subject':subject,'text':body,'o:tag':'lhm-meeting-prep','v:dedup_key':key(date,kind)})
            r.update(state='queued',message_id=response['id'],queued_at=now().isoformat()); save(p,r)
        except Exception as e:
            r.update(state='delivery_uncertain',error_type=type(e).__name__); save(p,r); raise
        return {'state':r['state'],'message_id':r['message_id'],'receipt':str(p)}

def verify(date,kind='brief'):
    p=receipt(date,kind); r=json.loads(p.read_text())
    if not r.get('message_id'):return {'state':r['state'],'receipt':str(p)}
    data=mailgun('/events',query={'message-id':r['message_id'],'limit':100})
    found=[]
    for item in data.get('items',[]):
        mid=item.get('message',{}).get('headers',{}).get('message-id','')
        if mid.strip('<>')!=r['message_id'].strip('<>'):continue
        if item.get('recipient') not in (TO,CC):continue
        found.append({'event':item.get('event'),'recipient':item.get('recipient'),'timestamp':item.get('timestamp'),'severity':item.get('severity')})
    delivered={x['recipient'] for x in found if x['event']=='delivered'}
    if delivered=={TO,CC}:r['state']='delivered'
    elif any(x['event']=='failed' and x.get('severity')=='permanent' for x in found):r['state']='failed'
    r.update(events=found,checked_at=now().isoformat()); save(p,r)
    return {'state':r['state'],'delivered_to':sorted(delivered),'receipt':str(p)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['gate','send','verify']); p.add_argument('--force',action='store_true'); p.add_argument('--date'); p.add_argument('--kind',choices=['brief','test','test-correction'],default='brief'); p.add_argument('--file'); a=p.parse_args()
    if a.action=='gate':out=gate(force=a.force)
    elif a.action=='verify':out=verify(a.date,a.kind)
    else:
        d=json.loads(Path(a.file).read_text()); out=send(a.date,d['subject'],d['body'],a.kind)
    print(json.dumps(out))
if __name__=='__main__':main()
