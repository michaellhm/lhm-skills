#!/usr/bin/env python3
"""Deterministic completion digest. Runs inside the existing Hermes container."""
import fcntl
import hashlib
import importlib.util
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
from render_digest import render

PROFILE = Path('/opt/data/profiles/lhm_brain')
RUNS = PROFILE / 'dispatch/monthly-delivery/runs'
RECEIPTS = PROFILE / 'workspace/google-ads-weekly-digest'
RECIPIENT = 'michael@localhealthmarketing.com.au'
SENDER = 'Lily | Local Health Marketing <lily@mg.brieflyflow.io>'


def block(text, kind):
    # Accept the two labelled fences and a JSON envelope emitted by older workers.
    # Count every explicit candidate: ambiguity must never select the first receipt.
    labelled = re.findall(r'^```(?:json[ \t]+)?' + re.escape(kind) +
                          r'[ \t]*\r?\n(.*?)(?=^```|\Z)', text, re.S | re.M)
    found = [json.loads(body) for body in labelled]
    for body in re.findall(r'^```json[ \t]*\r?\n(.*?)(?=^```|\Z)', text, re.S | re.M):
        try:
            value = json.loads(body)
        except ValueError:
            if re.search(r'"' + re.escape(kind) + r'"\s*:', body):
                raise ValueError('Malformed ' + kind + ' receipt')
            continue
        if isinstance(value, dict) and kind in value:
            found.append(value[kind])
    if len(found) != 1 or not isinstance(found[0], dict):
        raise ValueError('Expected exactly one ' + kind + ' receipt object')
    value = found[0]
    if kind in value:
        if len(value) != 1 or not isinstance(value[kind], dict):
            raise ValueError('Ambiguous ' + kind + ' envelope')
        value = value[kind]
    return value


def digest_card(digest):
    """Normalize recorded summaries only; never infer zones, approvals or new findings."""
    required = {'light', 'status_reason', 'stage', 'highlights', 'next_action'}
    if required & digest.keys():
        if not required <= digest.keys():
            raise ValueError('Incomplete email summary fields')
        card = {k: digest[k] for k in required}
    else:
        # Historical analytical receipts contain evidence instead of newsletter fields.
        # Copy a bounded set of recorded facts with neutral labels, not fresh analysis.
        zone = digest.get('performance_zone')
        confidence = digest.get('measurement_confidence')
        reason = digest.get('measurement_confidence_reason')
        period = digest.get('period', {})
        current = period.get('current', digest.get('current_window', {}))
        prior = period.get('prior', digest.get('prior_window', {}))
        dates = [current.get('start'), current.get('end'), prior.get('start'), prior.get('end')]
        if any(not isinstance(v, str) for v in dates):
            raise ValueError('Missing recorded comparison period')
        parsed = [date.fromisoformat(v) for v in dates]
        if parsed[0] > parsed[1] or parsed[2] > parsed[3] or parsed[3] >= parsed[0]:
            raise ValueError('Invalid recorded comparison period')
        if not isinstance(confidence, str) or not confidence.strip():
            raise ValueError('Missing measurement confidence')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('Missing measurement confidence reason')
        metrics = digest.get('metrics', digest.get('account_metrics', {}))
        totals = digest.get('totals', {})
        pairs = [('Recorded conversions', metrics.get('conversions_current', metrics.get('conversions', totals.get('current', {}).get('conversions'))),
                  metrics.get('conversions_prior', totals.get('prior', {}).get('conversions'))),
                 ('Recorded cost per conversion', metrics.get('cpa_current', metrics.get('cpa', totals.get('current', {}).get('cpa_aud'))),
                  metrics.get('cpa_prior', totals.get('prior', {}).get('cpa_aud')))]
        highlights = []
        for label, now, before in pairs:
            if all(isinstance(v, (int, float)) and not isinstance(v, bool) and
                   math.isfinite(v) and v >= 0 for v in (now, before)):
                highlights.append(f'{label}: {now:g} current; {before:g} prior.')
        if not highlights:
            raise ValueError('Missing recorded comparison metrics')
        highlights.append('Measurement caveat: ' + reason)
        actions = digest.get('actions')
        if not isinstance(actions, list) or not actions or not isinstance(actions[0], dict):
            raise ValueError('Missing recorded first action')
        title = actions[0].get('title')
        if not isinstance(title, str) or not title.strip():
            raise ValueError('Missing recorded first action title')
        caution = digest.get('zone_caution') or digest.get('operational_caution')
        if caution is not None and not isinstance(caution, str):
            raise ValueError('Invalid recorded zone caution')
        card = {'light': zone,
                'status_reason': caution or 'Performance zone recorded in the completed review',
                'stage': f'{dates[0]} to {dates[1]} versus {dates[2]} to {dates[3]}; measurement confidence: {confidence}',
                'highlights': highlights,
                'next_action': 'Review proposed action: ' + title}
    for key in ('light', 'status_reason', 'stage', 'next_action'):
        if not isinstance(card[key], str) or not card[key].strip():
            raise ValueError('Invalid email summary field: ' + key)
    if card['light'].lower() not in ('red', 'orange', 'yellow', 'blue', 'green', 'unknown'):
        raise ValueError('Invalid recorded performance zone')
    if not isinstance(card['highlights'], list) or not 1 <= len(card['highlights']) <= 4 or any(
            not isinstance(v, str) or not v.strip() for v in card['highlights']):
        raise ValueError('Invalid email highlights')
    return card


def week_date(value):
    day = date.fromisoformat(value)
    if day.weekday() != 0 or day.isoformat() != value:
        raise ValueError('week must be a Monday YYYY-MM-DD')
    return day


def assemble(manifest, registry, runs=RUNS):
    week = week_date(manifest['week'])
    selected = manifest['selected_clients']
    rows = manifest['clients']
    if len(selected) != len(set(selected)) or any(s not in registry for s in selected):
        raise ValueError('Duplicate or unregistered selection')
    if len(rows) != len(selected) or {r['client'] for r in rows} != set(selected):
        raise ValueError('Manifest must account for every selected client exactly once')
    cards = []
    for row in rows:
        slug = row['client']
        name = registry[slug]['name']
        if row['state'] not in ('complete', 'failed'):
            raise ValueError('All clients must be terminal before sending')
        try:
            if row['state'] == 'failed':
                raise ValueError(str(row['error']))
            run_id = row['delivery_run_id']
            if not re.fullmatch(r'monthly-delivery-\d{8}-\d{2}', run_id):
                raise ValueError('Invalid delivery run ID')
            # Monday 04:00 Melbourne is Sunday UTC; accept that week only.
            run_day = datetime.strptime(run_id.split('-')[2], '%Y%m%d').date()
            if (week - run_day).days not in (0, 1):
                raise ValueError('Stale delivery run from another week')
            run = runs / run_id
            request = json.loads((run / 'request.json').read_text())
            final = json.loads((run / 'final.json').read_text())
            if request['client'] != slug or final.get('exit_code') != 0 or final.get('status') not in ('needs_review', 'complete', 'completed'):
                raise ValueError('Delivery has not completed for this client')
            receipt = block((run / 'result.md').read_text(), 'ads_delivery')
            if receipt.get('client') != slug or receipt.get('delivery_status') != 'complete' or receipt.get('readback_verified') is not True:
                raise ValueError('Verified delivery receipt missing')
            drive = urlsplit(receipt['verified_drive_url'])
            if drive.scheme != 'https' or drive.netloc != 'drive.google.com' or not drive.path.startswith('/file/d/'):
                raise ValueError('Invalid verified Drive URL')
            # The frozen prompt contains the exact report delivered, not mutable vault state.
            prompt = (run / 'prompt.txt').read_text()
            report = prompt.split('REPORT CONTENT\n---\n', 1)[1]
            digest = block(report, 'ads_digest')
            if not isinstance(receipt.get('verified_basicops_url'), str) or not receipt['verified_basicops_url']:
                raise ValueError('Verified BasicOps card URL missing')
            card = {**digest_card(digest), 'name': name, 'task_url': receipt['verified_basicops_url']}
            render({'subject':'Validation','heading':'Validation','intro':'','footer':'','clients':[card]})
            cards.append(card)
        except (ValueError, KeyError, OSError, IndexError) as exc:
            cards.append({'name':name,'light':'unknown','status_reason':'Report or delivery incomplete',
                          'stage':'This client remains in the weekly queue.', 'highlights':[str(exc)],
                          'next_action':'Resolve the recorded blocker, then resume the existing run.', 'task_url':None})
    if not cards:
        return None
    return render({'subject':f'Your weekly Google Ads priorities | {week.isoformat()}',
                   'heading':'Your Google Ads priorities',
                   'intro':f'Week commencing {week.strftime("%d %B %Y")}. Your review cards and the first action for each account.',
                   'footer':'Open a review card for the full report and supporting files. Recommendations still follow the existing approval process.',
                   'clients':cards})


def mailer():
    path = PROFILE / 'skills/weekly-web-project-brief/scripts/brief.py'
    spec = importlib.util.spec_from_file_location('existing_lily_mailgun', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mailgun


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    temp.replace(path)


def send_once(week, email, mailgun, base=RECEIPTS, now=None):
    at = now or datetime.now(ZoneInfo('Australia/Melbourne'))
    if at.date() != week_date(week) or at.hour < 4:
        raise ValueError('Production digest sends only on its Monday after 04:00 Melbourne')
    base.mkdir(parents=True,exist_ok=True)
    with (base / '.send.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        receipt_path = base / (week+'.json')
        if receipt_path.exists():
            return json.loads(receipt_path.read_text())
        receipt = {'week':week,'state':'sending','to':RECIPIENT,'cc':[],'from':SENDER,
                   'content_sha256':hashlib.sha256(json.dumps(email,sort_keys=True).encode()).hexdigest()}
        save(base / (week+'-email.json'), email)
        save(receipt_path,receipt)  # intent survives a timeout/crash; never automatically retry
        try:
            result = mailgun('/messages',{'from':SENDER,'to':RECIPIENT,'h:Reply-To':RECIPIENT,
                              'subject':email['subject'],'html':email['html'],'text':email['text'],
                              'o:tag':'lhm-google-ads-weekly','v:portfolio_week':week})
            receipt.update(state='queued',message_id=result['id'])
        except Exception as exc:
            receipt.update(state='delivery_uncertain',error_type=type(exc).__name__)
        save(receipt_path,receipt)
        return receipt


def status(week):
    week_date(week)
    path = RECEIPTS / (week+'.json')
    receipt = json.loads(path.read_text())
    if not receipt.get('message_id'):
        return receipt
    result = mailer()('/events',query={'message-id':receipt['message_id'],'limit':100})
    events = [e for e in result.get('items',[]) if e.get('recipient') == RECIPIENT and
              e.get('message',{}).get('headers',{}).get('message-id','').strip('<>') == receipt['message_id'].strip('<>')]
    receipt['events'] = [{k:e.get(k) for k in ('event','timestamp','severity')} for e in events]
    if any(e['event']=='delivered' for e in events): receipt['state']='delivered'
    elif any(e['event']=='failed' and e.get('severity')=='permanent' for e in events): receipt['state']='failed'
    save(path,receipt)
    return receipt


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('preview','send','status'):
        raise SystemExit('usage: ads-weekly-digest.py preview|send MANIFEST | status YYYY-MM-DD')
    mode, arg = sys.argv[1:]
    if mode == 'status':
        print(json.dumps(status(arg))); return
    manifest = json.loads(Path(arg).read_text())
    registry = json.loads((PROFILE / 'config/google-ads-clients.json').read_text())['clients']
    email = assemble(manifest,registry)
    if email is None:
        print(json.dumps({'state':'empty_cohort_no_email'})); return
    if mode == 'preview':
        out = Path(arg).with_suffix('.preview.json'); save(out,email)
        out.with_suffix('.html').write_text(email['html'])
        print(json.dumps({'state':'preview_only','path':str(out)})); return
    print(json.dumps(send_once(manifest['week'],email,mailer())))

if __name__ == '__main__':
    main()
