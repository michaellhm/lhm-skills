#!/usr/bin/env python3
"""Portable HTML renderer, Melbourne gate and receipt-backed fixed-recipient sender."""
import argparse
import base64
import fcntl
import hashlib
import html
import json
import os
import shlex
import tempfile
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Australia/Melbourne')
BASE = Path(os.environ.get('LHM_WEB_BRIEF_STATE', '/opt/data/profiles/lhm_brain/workspace/weekly-web-project-brief'))
TO = 'michael@localhealthmarketing.com.au'
CC = ['kristalyn@localhealthmarketing.com.au', 'aiyajobelle.quinones08@gmail.com', 'jaimee@localhealthmarketing.com.au']
RECIPIENTS = [TO] + CC
FROM = 'Lily | LHM Web Projects <lily@mg.brieflyflow.io>'
FEEDBACK = ('Open your BasicOps chat with Lily and paste: “Update the weekly web brief for {week}. '
            'Here are my project corrections: [notes]. Update the existing BasicOps discussions '
            'and Obsidian project records, then tell me what changed and what still needs my decision.” '
            'One message or voice note covering several projects is fine. Email replies are not automatically processed by Lily.')
LIGHTS = {'red': ('Red', '#b42318', '#fff1f0'), 'orange': ('Orange', '#925800', '#fff8e6'), 'green': ('Green', '#18733b', '#edf8ef')}
OWNERS = {'Michael', 'Kristalyn', 'Aiya', 'Jaimee', 'Josephine'}


def now():
    return datetime.now(TZ)


def monday(value):
    d = date.fromisoformat(value)
    if d.weekday() != 0:
        raise ValueError('week must be a Monday')
    return d


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.')
    with os.fdopen(fd, 'w') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def receipt(week, kind='brief'):
    monday(week)
    if kind not in ('brief', 'test'):
        raise ValueError('Invalid delivery kind')
    # Identity is week + kind, deliberately not recipients/content: configuration
    # changes must never make a second production send possible for the same week.
    return BASE / 'receipts' / f'{week}-{kind}.json'


def gate(at=None):
    at = (at or now()).astimezone(TZ)
    if at.weekday() != 0 or at.hour != 12:
        return {'wakeAgent': False, 'reason': 'outside_monday_noon_melbourne'}
    week = at.date().isoformat()
    if receipt(week).exists():
        return {'wakeAgent': False, 'reason': 'existing_delivery_record', 'week': week}
    return {'wakeAgent': True, 'week': week, 'timezone': str(TZ), 'cutoff': at.isoformat(),
            'output_directory': str(BASE / 'runs' / week)}


def render(d):
    week = monday(d['week']).strftime('%-d %B %Y')
    projects = d['projects']
    if not projects:
        raise ValueError('Empty portfolio must be investigated, not sent as a normal brief')
    for p in projects:
        if p['light'] not in LIGHTS:
            raise ValueError('Invalid traffic light')
        u = urllib.parse.urlsplit(p['url'])
        if u.scheme != 'https' or not u.netloc or u.username or u.password:
            raise ValueError('Project links must be verified HTTPS URLs')
        for field in ('name', 'state', 'target', 'next'):
            if not isinstance(p[field], str) or not p[field].strip():
                raise ValueError('Incomplete project row')
    if any(o['name'] not in OWNERS for o in d['owners']):
        raise ValueError('Unrecognised owner or AI Support section')
    subject = f'Web projects | Week of {week} | What needs moving this week'
    text = ['Hi team,', d['intro']]
    parts = [f'<p>Hi team,</p><p>{html.escape(d["intro"])}</p>']

    def section(title, items):
        if not items:
            return
        text.extend([title] + ['• ' + x for x in items])
        parts.append('<h2 style="font-size:19px;margin:26px 0 12px">' + html.escape(title) + '</h2><ul>' + ''.join('<li style="margin:8px 0">' + html.escape(x) + '</li>' for x in items) + '</ul>')

    section('The main things to get moving', d['priorities'])
    section('New projects this week', d['new_projects'] or ['No new website projects this week.'])
    legend = 'Red: blocked or overdue. Orange: needs attention. Green: progressing with no known blocker.'
    dates = 'Dates are working targets unless stated otherwise. Estimates use eight weeks from confirmed client prototype approval; existing agreed targets take precedence.'
    text += ['Project snapshot', legend, dates]
    parts.append('<h2 style="font-size:19px;margin:26px 0 12px">Project snapshot</h2><p>' + legend + '</p><p style="font-size:13px;color:#526070">' + dates + '</p><div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:14px"><thead><tr>' + ''.join('<th scope="col" style="text-align:left;padding:12px;background:#16354a;color:white">' + x + '</th>' for x in ['Project', "Where we’re at", 'Target finish', 'What needs to happen next']) + '</tr></thead><tbody>')
    for p in sorted(projects, key=lambda p: list(LIGHTS).index(p['light'])):
        label, colour, bg = LIGHTS[p['light']]
        text += [f'{label} | {p["name"]}', p['state'], 'Target: ' + p['target'], 'Next: ' + p['next'], p['url']]
        cell = 'style="padding:12px;border-bottom:1px solid #dce3e8;vertical-align:top"'
        parts.append(f'<tr style="background:{bg}"><td {cell}><strong style="color:{colour}">{label}</strong><br><a href="{html.escape(p["url"], quote=True)}">{html.escape(p["name"])}</a></td>' + ''.join(f'<td {cell}>{html.escape(p[k])}</td>' for k in ('state', 'target', 'next')) + '</tr>')
    parts.append('</tbody></table></div>')
    for o in d['owners']:
        section(o['name'], o['actions'])
    section('Older cards to clear up', d.get('older_cards', []))
    section('Updates or corrections?', [FEEDBACK.format(week=week)])
    tail = 'Evidence checked: ' + d['cutoff'] + '. ' + d.get('limitations', '')
    text += [tail, 'Lily | LHM Web Projects']
    parts.append('<p style="font-size:12px;color:#526070">' + html.escape(tail) + '</p><p>Lily | LHM Web Projects</p>')
    body = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(subject) + '</title></head><body style="margin:0;background:#eef2f5;font-family:Arial,sans-serif;color:#203040;line-height:1.5"><div style="max-width:1050px;margin:0 auto;padding:24px;background:white">' + ''.join(parts) + '</div></body></html>'
    return {'week': d['week'], 'subject': subject, 'text': '\n\n'.join(text), 'html': body}


def mailgun(path, data=None, query=None):
    secret = os.environ.get('MAILGUN_API_KEY')
    if not secret:
        for line in Path('/opt/data/.env').read_text().splitlines():
            line = line.strip().removeprefix('export ')
            if line.startswith('MAILGUN_API_KEY='):
                values = shlex.split(line.split('=', 1)[1], comments=True)
                secret = values[0] if values else None
                break
    if not secret:
        raise RuntimeError('Mailgun configuration unavailable')
    url = 'https://api.mailgun.net/v3/mg.brieflyflow.io' + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    auth = base64.b64encode(('api:' + secret).encode()).decode()
    request = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                                     headers={'Authorization': 'Basic ' + auth})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def send(week, email, kind='brief'):
    p = receipt(week, kind)
    if email.get('week') != week:
        raise ValueError('Email week does not match receipt week')
    if not all(isinstance(email.get(k), str) and email[k].strip() for k in ('subject', 'text', 'html')):
        raise ValueError('Subject, HTML and text are required')
    if '<table' not in email['html'] or 'Updates or corrections?' not in email['html']:
        raise ValueError('Required table or feedback footer missing')
    if kind == 'brief':
        at = now()
        if at.weekday() != 0 or at.date().isoformat() != week or at.hour < 12:
            raise ValueError('Production send allowed only on its Monday after noon')
    BASE.mkdir(parents=True, exist_ok=True)
    with (BASE / '.send.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if p.exists():
            return {'state': 'deduplicated', 'receipt': str(p)}
        r = {'week': week, 'kind': kind, 'state': 'sending', 'recipients': RECIPIENTS,
             'started_at': now().isoformat(), 'content_sha256': hashlib.sha256(json.dumps(email, sort_keys=True).encode()).hexdigest()}
        save(p, r)
        try:
            result = mailgun('/messages', {'from': FROM, 'to': TO, 'cc': ','.join(CC), 'h:Reply-To': TO,
                              'subject': ('TEST | ' if kind == 'test' else '') + email['subject'],
                              'text': email['text'], 'html': email['html'], 'o:tag': 'lhm-weekly-web-brief',
                              'v:brief_week': week})
            r.update(state='queued', message_id=result['id'])
        except Exception as exc:
            r.update(state='delivery_uncertain', error_type=type(exc).__name__)
            save(p, r)
            raise RuntimeError('Delivery uncertain; receipt retained, do not resend') from None
        save(p, r)
        return {'state': r['state'], 'message_id': r['message_id'], 'receipt': str(p)}


def verify(week, kind='brief'):
    p = receipt(week, kind)
    r = json.loads(p.read_text())
    if not r.get('message_id'):
        return {'state': r['state'], 'receipt': str(p)}
    data = mailgun('/events', query={'message-id': r['message_id'], 'limit': 300})
    evidence = r.get('events', [])
    for item in data.get('items', []):
        mid = item.get('message', {}).get('headers', {}).get('message-id', '')
        if mid.strip('<>') == r['message_id'].strip('<>') and item.get('recipient') in r['recipients']:
            e = {k: item.get(k) for k in ('event', 'recipient', 'timestamp', 'severity')}
            if e not in evidence:
                evidence.append(e)
    states = {}
    for recipient in r['recipients']:
        events = [e for e in evidence if e['recipient'] == recipient]
        states[recipient] = 'delivered' if any(e['event'] == 'delivered' for e in events) else 'failed' if any(e['event'] == 'failed' and e['severity'] == 'permanent' for e in events) else 'pending'
    r.update(events=evidence, recipient_states=states, checked_at=now().isoformat())
    r['state'] = 'delivered' if all(s == 'delivered' for s in states.values()) else 'failed' if 'failed' in states.values() else 'queued'
    save(p, r)
    return {'state': r['state'], 'recipient_states': states, 'receipt': str(p)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['gate', 'render', 'send', 'verify'])
    parser.add_argument('--week')
    parser.add_argument('--kind', choices=['brief', 'test'], default='brief')
    parser.add_argument('--file')
    parser.add_argument('--out')
    args = parser.parse_args()
    if args.action == 'gate':
        result = gate()
    elif args.action == 'render':
        result = render(json.loads(Path(args.file).read_text()))
        out = Path(args.out)
        save(out / 'email.json', result)
        (out / 'preview.html').write_text(result['html'])
        (out / 'email.txt').write_text(result['text'])
        result = {'state': 'rendered', 'directory': str(out)}
    elif args.action == 'send':
        result = send(args.week, json.loads(Path(args.file).read_text()), args.kind)
    else:
        result = verify(args.week, args.kind)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
