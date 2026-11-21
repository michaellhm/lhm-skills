#!/usr/bin/env python3
"""Fail closed on incomplete research or an unreviewed/changed email payload."""
import hashlib
import html
import json
import sys
from read_audit import precise_time, read_entry, task_index
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


PROJECT_FIELDS = ('project_key', 'recorded_task_state', 'reconciled_state', 'next_actor', 'next_action', 'ownership_basis', 'approval_evidence', 'original_target', 'estimated_target', 'effective_target', 'target_basis', 'risk_reason', 'unresolved_conflicts', 'last_substantive_basicops_at', 'inactivity_days', 'expected_activity', 'light_reason', 'evidence')


def validate(directory, require_review=True):
    root = Path(directory).resolve()
    def read(name):
        return json.loads((root / name).read_text())
    def require(test, message):
        if not test:
            raise ValueError(message)
    def bound_file(item):
        p = Path(item['path'])
        if not p.is_absolute():
            p = root / p
        require(p.is_file() and digest(p) == item['sha256'], 'Evidence/baseline file missing or changed')
    access, research, comparison = [read(n) for n in ('access-receipt.json', 'research-receipt.json', 'comparison.json')]
    require(access.get('worker') == 'codex-cli', 'Codex CLI worker required')
    bound_file({'path': access['skill_path'], 'sha256': access['skill_sha256']})
    for source in ('gmail', 'obsidian', 'basicops'):
        a = access.get('sources', {}).get(source, {})
        require(a.get('status') == 'passed' and a.get('evidence'), 'Live worker read missing: ' + source)
        require(research.get('coverage', {}).get(source, {}).get('status') == 'complete', 'Incomplete research: ' + source)
    meeting = research.get('coverage', {}).get('meetings', {})
    require(meeting.get('status') in ('complete', 'not_required') and meeting.get('reason'), 'Meeting coverage unresolved')
    meeting_access = access.get('sources', {}).get('meetings', {})
    if meeting['status'] == 'complete':
        require(meeting_access.get('status') == 'passed' and meeting_access.get('evidence'), 'Live meeting read missing')
    else:
        require(meeting_access.get('status') == 'not_required' and meeting_access.get('reason'), 'Meeting access exemption missing')
    require(research.get('material_gaps') == [], 'Material research gaps')
    brief = read('brief.json')
    names={p['name'] for p in brief['projects']}
    gaps = research.get('project_gaps', [])
    blockers = brief.get('blockers', [])
    require(isinstance(gaps, list) and isinstance(blockers, list), 'Project gaps/blockers must be lists')
    ids = [b.get('id') for b in blockers]
    require(all(isinstance(i, str) and i.strip() for i in ids) and len(ids) == len(set(ids)), 'Unique blocker IDs required')
    gap_ids = [g.get('id') for g in gaps]
    require(len(gap_ids) == len(set(gap_ids)) and set(gap_ids) <= set(ids), 'Every project gap needs a visible blocker')
    file_names = {f['path'] for f in research.get('evidence_files', [])}
    from brief import new_project_items
    new_project_items(brief)
    for item in brief.get('new_projects', []):
        require(item['evidence'] in file_names, 'New project date evidence must be retained')
    for gap in gaps:
        require(gap.get('scope') == 'project' and gap.get('source') in ('gmail', 'obsidian', 'basicops'), 'Only scoped project gaps may be disclosed')
        require(gap.get('evidence') and isinstance(gap['evidence'], list) and all(e in file_names for e in gap['evidence']), 'Project gap search evidence must be retained')
        blocker = next(b for b in blockers if b['id'] == gap['id'])
        require(gap.get('project') == blocker.get('project'), 'Project gap/blocker mismatch')
    if blockers:
        from brief import blocker_text
        email = read('email.json')
        require(all('Blockers and information needed' in email.get(k, '') for k in ('html', 'text')), 'Visible blocker section required')
        for blocker in blockers:
            label = blocker_text(blocker)
            require(label in email.get('text', '') and html.escape(label) in email.get('html', ''), 'Blocker disclosure missing from email')
    coverage=research.get('project_source_coverage',[])
    require(len(coverage)==len(names) and {p.get('project') for p in coverage}==names, 'Per-project source coverage required')
    for project in coverage:
        for source in ('gmail','obsidian','basicops'):
            item=project.get(source,{})
            evidence = isinstance(item.get('evidence'), list) and bool(item['evidence'])
            disclosed = item.get('status') == 'limited' and any(g.get('id') == item.get('gap_id') and g.get('project') == project['project'] and g.get('source') == source for g in gaps)
            require(evidence and (item.get('status') == 'complete' or disclosed), 'Incomplete project source: '+project['project']+' / '+source)
        require(any(project.get(source, {}).get('status') == 'complete' for source in ('gmail','obsidian','basicops')), 'Project needs verified source evidence')
    records = research.get('projects', [])
    require(isinstance(records, list) and len(records) == len(names) and
            {p.get('project') for p in records} == names, 'Per-project reconciled records required')
    for project in records:
        require(set(PROJECT_FIELDS) <= set(project), 'Incomplete reconciled project record: ' + project['project'])
        for key in ('project_key','recorded_task_state','reconciled_state','next_actor','next_action','ownership_basis','target_basis','light_reason'):
            require(isinstance(project[key], str) and bool(project[key].strip()), 'Missing project reasoning: ' + key)
        require(isinstance(project['unresolved_conflicts'], list), 'Project conflicts must be explicit')
        last = project['last_substantive_basicops_at']
        require(last is None or precise_time(last), 'Activity date must be an observed ISO timestamp or null')
        days = project['inactivity_days']
        require(days is None or (type(days) is int and days >= 0), 'Invalid project inactivity')
        if days is not None:
            require(last is not None and precise_time(brief.get('evidence_cutoff')), 'Dated inactivity requires an actual activity date and cutoff')
            tz=ZoneInfo('Australia/Melbourne')
            elapsed=(datetime.fromisoformat(brief['evidence_cutoff'].replace('Z','+00:00')).astimezone(tz).date()-datetime.fromisoformat(last.replace('Z','+00:00')).astimezone(tz).date()).days
            require(days == elapsed, 'Inactivity days differ from actual activity/cutoff dates')
        require(isinstance(project['evidence'], list) and bool(project['evidence']) and
                all(e in file_names for e in project['evidence']), 'Project reasoning must reference retained evidence')
    for gap in gaps:
        if gap['project'] in names:
            entry = next(p for p in coverage if p['project'] == gap['project'])[gap['source']]
            require(entry.get('status') == 'limited' and entry.get('gap_id') == gap['id'], 'Disclosed gap cannot claim complete project coverage')
    files = research.get('evidence_files', [])
    require(bool(files), 'No retained primary evidence')
    for f in files:
        bound_file(f)
    audit_ref = access.get('controller_read_receipts', {})
    require(audit_ref.get('path') in file_names, 'Controller source read timestamps missing')
    bound_file(audit_ref)
    audit = read(audit_ref['path'])
    require(audit.get('time_basis') == 'controller_received_result', 'Invalid source read time basis')
    reads = audit.get('reads', [])
    require(bool(reads) and len({x.get('read_id') for x in reads}) == len(reads), 'Unique source read IDs required')
    for item in reads:
        require(precise_time(item.get('read_at')) and item.get('evidence') in file_names,
                'Source-specific actual read timestamp and evidence required')
        raw = read(item['evidence'])
        matches = [r for r in raw.get('records', []) if r.get('id') == item.get('record_id')]
        require(len(matches) == 1, 'Source timestamp must identify one retained result')
        log_name = item['read_id'].rsplit(':', 1)[0]
        require(read_entry(matches[0], log_name, item['evidence']) == item,
                'Source timestamp differs from controller-observed result')
    for source, details in access['sources'].items():
        if details.get('status') == 'passed':
            expected = [x for x in reads if x['source'] == source]
            require(bool(expected) and details.get('reads') == expected,
                    'Source-specific read times missing: ' + source)
    task_ref=access.get('controller_task_evidence', {})
    require(task_ref.get('path') in file_names, 'Controller task evidence index missing')
    bound_file(task_ref)
    indexed=read(task_ref['path'])
    require(indexed == task_index(reads, read), 'Task index differs from actual native results')
    tasks=indexed['tasks']
    for row in brief['projects']:
        require(any(identity['url'] == row.get('url') for task in tasks.values() for identity in task['identities']), 'Project URL lacks native task identity: '+row['name'])
    inbox_path = root / 'inbox-review.json'
    require(any((root / f['path']).resolve() == inbox_path for f in files), 'Inbox review must be retained and hash-bound')
    inbox = read('inbox-review.json')
    boards = inbox.get('boards', [])
    require(len(boards) == 3 and {b.get('owner') for b in boards} == {'Michael', 'Kristalyn', 'Aiya'}, 'Three owner inbox sweeps required')
    for board in boards:
        require(board.get('status') == 'complete' and board.get('terminal') is True and board.get('board_id') and board.get('section_id'), 'Incomplete owner inbox sweep: ' + str(board.get('owner')))
        require(isinstance(board.get('selected_actions'), list), 'Selected weekly actions missing')
        for action in board['selected_actions']:
            task=tasks.get(str(action.get('task_id')), {})
            require(task.get('identities') and task.get('task_reads') and task.get('discussion_reads'), 'Selected Inbox action lacks actual task/discussion reads: '+str(action.get('task_id')))
    bound_file(comparison['baseline'])
    require(bool(comparison.get('projects')), 'No baseline comparison')
    require(comparison.get('unresolved_regressions') == [], 'Unresolved factual regression')
    if not require_review:
        return {'state': 'research_passed'}
    review = read('quality-review.json')
    require(review.get('accepted') is True and review.get('reviewer') and review.get('issues') == [], 'Independent review not accepted')
    for key, name in [('brief', 'brief.json'), ('email', 'email.json'), ('research', 'research-receipt.json'), ('comparison', 'comparison.json'), ('access', 'access-receipt.json')]:
        require(review.get(key + '_sha256') == digest(root / name), 'Review invalidated: ' + name)
    return {'state': 'quality_passed', 'email_sha256': digest(root / 'email.json')}


if __name__ == '__main__':
    print(json.dumps(validate(sys.argv[1])))
