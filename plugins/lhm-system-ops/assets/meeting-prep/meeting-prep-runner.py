#!/usr/bin/env python3
"""Bounded briefing research, durable retry state, and receipt-verified delivery.

Run as a Hermes no-agent cron script. The child is the existing profile and skill,
not a new worker identity. No credentials, profile limits or permissions change.
"""
import argparse
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import meeting_prep as runtime

PROFILE = 'lhm_brain'
MAX_ATTEMPTS = 3
MAX_TURNS = 60
RUN_BUDGET = 1500
HARD_TIMEOUT = 1650


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def selected_date(at):
    local = at.astimezone(runtime.TZ)
    # Retry the same next-day batch after a late start or incomplete attempt.
    if 13 <= local.hour <= 18:
        return str(local.date() + timedelta(days=1))
    # Recover a previously discovered batch the next morning, never invent one.
    today = str(local.date())
    if 7 <= local.hour <= 10 and (runtime.BASE/'runs'/today/'calendar.json').exists():
        return today
    return None


def child_run(prompt, directory, attempt):
    query = directory / f'prompt-{attempt}.txt'
    query.write_text(prompt)
    os.chmod(query, 0o600)
    cmd = ['hermes', '-p', PROFILE, 'chat', '--oneshot', '--quiet',
           '--query-file', str(query), '--skills', 'lily-meeting-prep',
           '--max-turns', str(MAX_TURNS), '--run-budget', str(RUN_BUDGET),
           '--in', str(directory)]
    # Child output is private evidence, not an email or an implicit success.
    # The Calendar helper selects the shared Google credential home in-process.
    # Restore the real Hermes root for the CLI's explicit profile selection.
    environment = dict(os.environ, HERMES_HOME='/opt/data')
    environment.pop('HERMES_PROFILE', None)
    with (directory/f'agent-{attempt}.log').open('w') as log:
        os.chmod(log.name, 0o600)
        child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, start_new_session=True,
                                 env=environment)
        try:
            return child.wait(timeout=HARD_TIMEOUT)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            raise RuntimeError('Briefing research exceeded its bounded runtime')


def validate_research(data, date, attempt):
    if not isinstance(data, dict) or data.get('meeting_date') != date or data.get('attempt') != attempt:
        raise ValueError('Missing current-attempt research receipt')
    if data.get('status') not in ('ready', 'no_client_meetings'):
        raise ValueError('Research is incomplete; no email sent')
    classified = data.get('calendar_classification')
    if not isinstance(classified, list) or not classified:
        raise ValueError('Calendar classification missing')
    if any(not isinstance(x, dict) or not x.get('event_id') or
           x.get('classification') not in ('client', 'excluded', 'uncertain') or
           not x.get('reason') for x in classified):
        raise ValueError('Calendar classification evidence incomplete')
    if data['status'] == 'no_client_meetings':
        if any(x['classification'] != 'excluded' for x in classified):
            raise ValueError('Cannot skip client or uncertain meetings')
        return
    coverage = data.get('source_coverage', {})
    for name in ('basicops', 'fathom', 'gmail'):
        item = coverage.get(name, {})
        if item.get('status') not in ('checked', 'unavailable') or not item.get('evidence'):
            raise ValueError(f'{name} coverage missing: research must try every source')
    issues = data.get('issues')
    if not isinstance(issues, list):
        raise ValueError('Issue reconciliation missing')
    for item in issues:
        if item.get('included') and not all(item.get(k) for k in
                ('issue_key', 'latest_evidence_at', 'evidence_urls', 'next_actor',
                 'next_action', 'owner_basis', 'confidence')):
            raise ValueError('Included issue lacks current evidence or next actor')



def validate_email(data, email):
    """Bind every body paragraph to the reconciled, included issue ledger."""
    if not isinstance(email, dict) or set(email) != {'subject', 'body'}:
        raise ValueError('Current brief email is missing or invalid')
    entries = []
    for item in data['issues']:
        if not item.get('included'):
            continue
        if not item.get('email_entry'):
            raise ValueError('Included issue needs its exact email entry')
        if any('app.basicops.com/' in url for url in item['evidence_urls']):
            discussion = item.get('latest_discussion', {})
            if not all(discussion.get(k) for k in ('task_id', 'message_id', 'created_at', 'read_at')):
                raise ValueError('Task issue requires latest discussion message evidence')
        entries.append(item['email_entry'])
    if not data.get('email_opening') or not entries:
        raise ValueError('Missing calendar opening or included email entries')
    gap = any(data['source_coverage'][s]['status'] == 'unavailable'
              for s in ('basicops', 'fathom', 'gmail'))
    if gap and not data.get('limitation_sentence'):
        raise ValueError('Source gap must be disclosed in the email')
    parts = [data['email_opening'], *entries]
    if data.get('limitation_sentence'):
        parts.append(data['limitation_sentence'])
    expected = '\n\n'.join([*parts, 'Lily'])
    if email['body'] != expected:
        raise ValueError('Email contains material outside the reconciled issue ledger')


def reconcile_send(date):
    stored = read(runtime.receipt(date))
    if stored is None:
        return None
    if stored.get('state') != 'delivered' and stored.get('message_id'):
        # Verify an existing attempt; never delete its receipt or submit again.
        runtime.verify(date)
        stored = read(runtime.receipt(date))
    return stored


def run(date=None, at=None):
    os.umask(0o077)
    at = at or runtime.now()
    date = date or selected_date(at)
    if date is None:
        return {'wakeAgent': False, 'reason': 'outside_briefing_and_recovery_windows'}
    datetime.strptime(date, '%Y-%m-%d')
    directory = runtime.BASE/'runs'/date
    directory.mkdir(parents=True, exist_ok=True)
    with (directory/'.run.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {'wakeAgent': False, 'reason': 'existing_attempt_running', 'meeting_date': date}
        state_path = directory/'run-state.json'
        state = read(state_path, {'meeting_date': date, 'attempts': 0})

        def checkpoint(status, **extra):
            state.update(status=status, updated_at=runtime.now().isoformat(), **extra)
            runtime.save(state_path, state)

        try:
            delivery = reconcile_send(date)
            if delivery:
                if delivery.get('state') == 'delivered':
                    checkpoint('delivered', delivery_receipt=str(runtime.receipt(date)))
                    return {'wakeAgent': False, 'state': 'delivered', 'meeting_date': date}
                checkpoint('delivery_attention', delivery_state=delivery.get('state'))
                raise RuntimeError('Existing email delivery is '+str(delivery.get('state'))+'; no resend')
            if state.get('status') in ('no_client_meetings', 'no_calendar_candidates'):
                return {'wakeAgent': False, 'state': state['status'], 'meeting_date': date}
            if state.get('attempts', 0) >= MAX_ATTEMPTS:
                raise RuntimeError('Research attempt limit reached; manual review required')
            # Count calendar failures too, so repeated source failures stay bounded.
            attempt = state.get('attempts', 0) + 1
            checkpoint('running', attempts=attempt, started_at=at.isoformat())
            inputs = runtime.gate(at=at, force=True, date=date)
            if not inputs.get('wakeAgent'):
                checkpoint('no_calendar_candidates')
                return {'wakeAgent': False, 'reason': inputs['reason'], 'meeting_date': date}
            calendar = read(Path(inputs['calendar_file']))
            event_ids = {x['id'] for x in calendar['events']}
            prompt = f'''Prepare the scheduled internal meeting brief for {date}.
Calendar input: {inputs['calendar_file']}. Output directory: {directory}.
This is attempt {attempt}, with {MAX_TURNS} turns and {RUN_BUDGET} seconds maximum.
Use the attached lily-meeting-prep skill and its runtime/editorial references.
RESEARCH-ONLY MODE: do not call send, verify, Mailgun, or another email tool.
The deterministic parent validates your files and owns authorised delivery.
Read existing research/checkpoint files first. Reuse verified evidence, refresh
newer material discussions and replies, and continue at the first incomplete source.
Visit BasicOps, Fathom and Gmail before deepening any one source. Batch independent
reads, use targeted queries, and focus on 5-8 material issues, not the full backlog.
Reserve the final 10 turns for reconciliation and saving output. Save partial
research after each source so a retry can continue. Do not delegate or change setup.
Write email.json with exactly subject and body, and research-receipt.json with:
meeting_date={date}, attempt={attempt}, status=ready (or incomplete),
source_coverage: basicops/fathom/gmail each with status=checked or unavailable
and evidence describing queries, newest reads, pagination bounds or exact failure;
calendar_classification: one event_id, classification=client/excluded/uncertain
and reason per supplied event; issues: the skill's per-issue evidence records.
Follow runtime.md's exact email_entry/email_opening body contract. Read the latest
discussion for every included task and record its message ID and timestamp.
Never research personal attendees: exclude personal events from calendar context.
If a source is unavailable after one retry, explicitly scope the gap in the receipt
and brief; do not invent evidence or spend the whole run retrying. If research
cannot support a useful brief, save status=incomplete and the exact missing step.
If every event is excluded, save status=no_client_meetings with classification
evidence instead of an email. No send, source mutations, personal or patient data.
Report success only after saving both current-attempt files.''' 
            produced_after = time.time()
            result = child_run(prompt, directory, attempt)
            data = read(directory/'research-receipt.json')
            validate_research(data, date, attempt)
            classified = data['calendar_classification']
            if len(classified) != len(event_ids) or {x['event_id'] for x in classified} != event_ids:
                raise ValueError('Research did not account for every calendar event')
            if data['status'] == 'no_client_meetings':
                checkpoint('no_client_meetings', child_exit_code=result)
                return {'wakeAgent': False, 'state': 'no_client_meetings', 'meeting_date': date}
            email = read(directory/'email.json')
            if not isinstance(email, dict) or set(email) != {'subject', 'body'}:
                raise ValueError('Current brief email is missing or invalid')
            if (directory/'email.json').stat().st_mtime < produced_after:
                raise ValueError('Email was not saved by the current attempt')
            if any(data['source_coverage'][s]['status'] == 'unavailable' for s in ('basicops','fathom','gmail')):
                if not data.get('limitation_sentence') or data['limitation_sentence'] not in email['body']:
                    raise ValueError('Source gap must be disclosed in the email')
            validate_email(data, email)
            checkpoint('ready', child_exit_code=result)
            runtime.send(date, email['subject'], email['body'])
            for n in range(4):
                outcome = runtime.verify(date)
                if outcome.get('state') == 'delivered':
                    checkpoint('delivered', delivery_receipt=outcome['receipt'])
                    return {'state': 'delivered', 'meeting_date': date, 'receipt': outcome['receipt']}
                if outcome.get('state') in ('failed', 'delivery_uncertain'):
                    break
                if n < 3:
                    time.sleep(15)
            checkpoint('delivery_attention', delivery_state=outcome.get('state'))
            raise RuntimeError('Email delivery not confirmed: '+str(outcome.get('state')))
        except Exception as exc:
            # A provider turn ending normally is not a verified business outcome.
            if state.get('status') != 'delivery_attention':
                checkpoint('failed', error=str(exc), retry_allowed=state.get('attempts',0)<MAX_ATTEMPTS)
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Explicitly authorised recovery meeting date')
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.date)))
    except Exception as exc:
        print(json.dumps({'state': 'failed', 'error': str(exc)}))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
