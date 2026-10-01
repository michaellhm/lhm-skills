#!/usr/bin/env python3
"""Create one receipt-bound shared weekly note; never overwrite team feedback."""
import argparse
import fcntl
import hashlib
import importlib.util
import io
import json
import subprocess
from datetime import date
from pathlib import Path

DRIVE = '0AF6X3xDBIuVcUk9PVA'
FOLDER = '60 Knowledge'
INDEX = '60 Knowledge/Weekly Web Projects'


def identity(week):
    day = date.fromisoformat(week)
    if day.weekday() != 0:
        raise ValueError('Monday required')
    year, number, _ = day.isocalendar()
    return f'{year}-W{number:02d}', f'{year}-W{number:02d} — Web Projects.md'


def snapshot(brief, receipt):
    week = brief['week']
    iso, name = identity(week)
    if receipt.get('week') != week or receipt.get('kind') != 'brief' or receipt.get('state') != 'delivered':
        raise ValueError('Verified normal delivery for this week required')
    if receipt.get('recipients') != ['support@localhealthmarketing.com.au'] or not receipt.get('message_id'):
        raise ValueError('Fixed team delivery required')
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = ['---', 'type: knowledge', 'status: current', f'week: {iso}',
             f'created: {week}', f'updated: {week}', '---', '', f'# {iso} — Web Projects', '',
             f'[[{INDEX}|Weekly Web Projects]]', '',
             f'Week commencing **{week}**. Delivered snapshot; live task state remains in BasicOps.', '',
             f'**Evidence cutoff:** {brief["cutoff"]}',
             f'**Delivery:** confirmed to support@localhealthmarketing.com.au; `{receipt["message_id"]}`.', '',
             '## Priorities', '']
    lines += ['- ' + x for x in brief['priorities']]
    lines += ['', '## New projects', '']
    lines += ['- ' + x for x in brief.get('new_projects', [])] or ['No new website projects this week.']
    lines += ['', '## Project snapshot', '', '| Project | Position | Target | Next action |', '| --- | --- | --- | --- |']
    for p in brief['projects']:
        lines.append(f'| [{cell(p["name"])}]({p["url"]}) | **{p["light"].title()}** — {cell(p["state"])} | {cell(p["target"])} | {cell(p["next"])} |')
    lines += ['', '## Actions by person', '']
    for owner in brief['owners']:
        lines += ['### ' + owner['name'], '']
        for action in owner['actions']:
            lines.append('- ' + (action if isinstance(action, str) else
                         f'**{action.get("client", "Action")}:** [{action["text"]}]({action["url"]})'))
        lines.append('')
    lines += ['## Clarifications and limitations', '']
    for b in brief.get('blockers', []):
        lines.append(f'- **{b["project"]}:** {b["issue"]} {b["impact"]} **{b["owner"]}:** {b["next_step"]}')
    if brief.get('limitations'):
        lines += ['', brief['limitations']]
    if brief.get('older_cards'):
        lines += ['', '## Other carried-forward work', ''] + ['- ' + x for x in brief['older_cards']]
    lines += ['', '## Source', '', 'Agent-maintained snapshot of the delivered weekly brief. Task links above and retained research/delivery receipts substantiate the snapshot. It is planning input, not an accepted personal workload.', '']
    body = '\n'.join(lines)
    marker = '<!-- weekly-web-snapshot-sha256:' + hashlib.sha256(body.encode()).hexdigest() + ' -->'
    return name, body + marker + '\n\n## Team corrections after delivery\n\nAdd dated, attributed corrections and source links here. Preserve the delivered snapshot above.\n', marker


def list_exact(service, parent, name):
    # Names are generated/constant, never source-supplied paths.
    token = None
    found = []
    while True:
        result = service.files().list(q=f"trashed=false and '{parent}' in parents and name='{name}'",
            corpora='drive', driveId=DRIVE, supportsAllDrives=True, includeItemsFromAllDrives=True,
            fields='nextPageToken,incompleteSearch,files(id,name,mimeType)', pageToken=token).execute()
        if result.get('incompleteSearch'):
            raise ValueError('Incomplete archive lookup')
        found.extend(result.get('files', []))
        token = result.get('nextPageToken')
        if not token:
            return found


def publish(service, name, text, marker, media_factory, intent_path=None):
    drive = service.drives().get(driveId=DRIVE, fields='id,name').execute()
    if drive != {'id': DRIVE, 'name': 'LHM Knowledge'}:
        raise ValueError('Wrong shared vault')
    folders = list_exact(service, DRIVE, FOLDER)
    if len(folders) != 1 or folders[0]['mimeType'] != 'application/vnd.google-apps.folder':
        raise ValueError('Unique existing knowledge folder required')
    existing = list_exact(service, folders[0]['id'], name)
    if len(existing) > 1:
        raise ValueError('Duplicate archive notes need reconciliation')
    if existing:
        current = service.files().get_media(fileId=existing[0]['id'], supportsAllDrives=True).execute().decode('utf-8-sig')
        # Compare the entire immutable prefix, allowing appended human feedback.
        prefix = text.split(marker)[0] + marker
        if not current.startswith(prefix):
            raise ValueError('Existing weekly note differs; preserve it for reconciliation')
        return {'state': 'archived', 'file_id': existing[0]['id'], 'path': FOLDER + '/' + name, 'unchanged': True}
    if intent_path is not None:
        if intent_path.exists():
            raise ValueError('Prior archive creation uncertain; reconcile instead of creating another note')
        # Persist before POST. Retry can discover an existing matching note but cannot create twice.
        with intent_path.open('x') as intent:
            json.dump({'name': name, 'marker': marker, 'state': 'creating'}, intent)
    created = service.files().create(body={'name': name, 'parents': [folders[0]['id']], 'mimeType': 'text/markdown'},
        media_body=media_factory(io.BytesIO(text.encode()), mimetype='text/markdown', resumable=False),
        supportsAllDrives=True, fields='id').execute()
    actual = service.files().get_media(fileId=created['id'], supportsAllDrives=True).execute().decode('utf-8-sig')
    if actual != text:
        raise ValueError('Archive read-back mismatch')
    return {'state': 'archived', 'file_id': created['id'], 'path': FOLDER + '/' + name, 'unchanged': False}


def reconcile(cfg, week):
    """Host-only archive retry. Never starts research or resends email."""
    identity(week)
    root = Path(cfg['state']) / 'archive'
    if not root.exists():
        return {'state': 'not_registered'}
    with (root / (week + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _reconcile(cfg, week)


def _reconcile(cfg, week):
    root = Path(cfg['state'])
    job = root / 'archive' / (week + '.json')
    if not job.exists():
        return {'state': 'not_registered'}
    data = json.loads(job.read_text())
    if data.get('state') == 'archived':
        return data
    receipt = root / 'receipts' / (week + '-brief.json')
    if not receipt.exists() or json.loads(receipt.read_text()).get('state') != 'delivered':
        return {'state': 'awaiting_delivery'}
    run = (root / 'runs' / data['run']).resolve()
    if not run.is_relative_to((root / 'runs').resolve()) or run.name != data['run']:
        raise ValueError('Confined archive run required')
    cmd = ['docker', 'exec', '-u', 'hermes', '-e', 'HERMES_HOME=/opt/data/.hermes', 'hermes',
           '/opt/data/.venv/bin/python', '/opt/data/profiles/lhm_brain/skills/weekly-web-project-brief/scripts/weekly_archive.py',
           '--week', week, '--run', '/opt/data/profiles/lhm_brain/workspace/weekly-web-project-brief/runs/' + run.name]
    try:
        response = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=90)
        data.update(json.loads(response.stdout))
    except (subprocess.SubprocessError, ValueError):
        data.update(state='archive_pending', error='Shared archive unavailable; email delivery retained, no resend')
    tmp = job.with_suffix('.tmp'); tmp.write_text(json.dumps(data, indent=2)); tmp.replace(job)
    return data


def main():
    from brief import BASE
    from quality import validate
    parser = argparse.ArgumentParser(); parser.add_argument('--week', required=True); parser.add_argument('--run', required=True)
    args = parser.parse_args(); identity(args.week)
    run = Path(args.run).resolve()
    if not run.is_relative_to((BASE / 'runs').resolve()):
        raise ValueError('Confined delivered run required')
    validate(run)
    receipt = json.loads((BASE / 'receipts' / (args.week + '-brief.json')).read_text())
    email = json.loads((run / 'email.json').read_text())
    if receipt.get('content_sha256') != hashlib.sha256(json.dumps(email, sort_keys=True).encode()).hexdigest():
        raise ValueError('Archive must match delivered payload')
    brief = json.loads((run / 'brief.json').read_text())
    if brief['week'] != args.week:
        raise ValueError('Archive week mismatch')
    name, text, marker = snapshot(brief, receipt)
    spec = importlib.util.spec_from_file_location('existing_google', '/opt/data/skills/productivity/google-workspace/scripts/google_api.py')
    google = importlib.util.module_from_spec(spec); spec.loader.exec_module(google)
    from googleapiclient.http import MediaIoBaseUpload
    print(json.dumps(publish(google.build_service('drive', 'v3'), name, text, marker, MediaIoBaseUpload,
                             run / 'archive-upload-intent.json')))


if __name__ == '__main__':
    main()
