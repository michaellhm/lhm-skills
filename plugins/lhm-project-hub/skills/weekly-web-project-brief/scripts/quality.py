#!/usr/bin/env python3
"""Fail closed on incomplete research or an unreviewed/changed email payload."""
import hashlib
import html
import json
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate_actions(brief, boards, baseline, comparison):
    """Bind selected execution cards and account for every approved baseline action."""
    def require(test, message):
        if not test:
            raise ValueError(message)
    owners = {o['name']: o.get('actions', []) for o in brief.get('owners', [])}
    require(len(owners) == len(brief.get('owners', [])), 'Duplicate owner sections')
    for actions in owners.values():
        for action in actions:
            require(isinstance(action, dict) or (isinstance(action, str) and action.strip().rstrip('.') in
                    ('No immediate website action identified for this week', 'No immediate action')),
                    'Actionable owner work needs a linked action object, not unchecked prose')
    rendered = [(owner, a.get('client'), a.get('text'), a.get('url'))
                for owner, actions in owners.items() for a in actions if isinstance(a, dict)]
    require(len(rendered) == len(set(rendered)), 'Duplicate rendered action')
    selected_keys = []
    for board in boards:
        for selected in board['selected_actions']:
            owner = selected.get('action_owner', board['owner'])
            selected_keys.append((owner, selected.get('client'), selected.get('rendered_action'), selected.get('url')))
            require(selected.get('selection_kind') in ('execution', 'prerequisite'),
                    'Selected action needs execution/prerequisite classification')
            require(selected.get('dependency_state') in ('clear', 'unresolved', 'not_applicable'),
                    'Selected action needs dependency state')
            require(not (selected['selection_kind'] == 'execution' and selected['dependency_state'] == 'unresolved'),
                    'Future-gated execution must be replaced by its immediate prerequisite')
            require(not (selected['selection_kind'] == 'execution' and
                         selected.get('status') in ('Complete', 'Cancelled', 'Decline')),
                    'Completed or cancelled task cannot select execution')
            require(selected.get('url') and selected.get('client') and selected.get('rendered_action'),
                    'Selected action needs exact client, task/evidence URL and rendered action')
            require(any(isinstance(a, dict) and all(a.get(k) == selected.get(v)
                    for k, v in (('client', 'client'), ('url', 'url'), ('text', 'rendered_action')))
                    for a in owners.get(owner, [])),
                    'Selected action missing or mapped to a different task/owner: ' + str(selected.get('task_id', selected['url'])))
    require(len(selected_keys) == len(set(selected_keys)), 'Duplicate selected action')
    require(set(rendered) == set(selected_keys),
            'Every rendered action needs an exact verified selection; include supplemental owner sweeps')
    def key(owner, action):
        return json.dumps([owner, action], sort_keys=True, ensure_ascii=False)
    expected = {key(o['name'], a) for o in baseline.get('owners', []) for a in o.get('actions', [])}
    dispositions = comparison.get('action_dispositions', [])
    require(isinstance(dispositions, list), 'Baseline action dispositions must be a list')
    actual = []
    for item in dispositions:
        require(isinstance(item, dict) and 'owner' in item and 'baseline_action' in item,
                'Baseline action disposition needs exact owner and original action')
        actual.append(key(item['owner'], item['baseline_action']))
        require(item.get('disposition') in ('retained', 'completed', 'cancelled', 'superseded', 'prerequisite')
                and item.get('reason') and isinstance(item.get('current_evidence_ids'), list)
                and item['current_evidence_ids'] and all(isinstance(x, str) and x.strip() for x in item['current_evidence_ids']),
                'Every baseline action needs an evidenced disposition')
    require(len(actual) == len(set(actual)) and set(actual) == expected,
            'Every approved baseline action needs exactly one disposition; do not silently drop commitments')

    for group in ('action_dispositions', 'archive_action_dispositions', 'archive_correction_dispositions'):
        require(isinstance(comparison.get(group, []), list), 'Action disposition group must be a list')
        for item in comparison.get(group, []):
            require(item.get('disposition') in ('retained', 'completed', 'cancelled', 'superseded', 'prerequisite')
                    and item.get('reason') and item.get('current_evidence_ids'),
                    'Every historical commitment needs an evidenced disposition')
            links = item.get('current_actions', [])
            if item['disposition'] in ('retained', 'prerequisite'):
                require(isinstance(links, list) and links,
                        'Retained commitment needs exact current_actions mappings: ' + group)
            require(isinstance(links, list), 'Current action mappings must be a list')
            for link in links:
                require(isinstance(link, dict) and isinstance(link.get('action'), dict)
                        and link.get('action') in owners.get(link.get('owner'), []),
                        'Historical commitment maps to an absent or changed current action: ' + group)
    return {'count': len(rendered), 'selected_count': len(selected_keys),
            'unique_task_urls': len({a[3] for a in rendered}), 'unmatched': 0}


def action_check(directory):
    """Compute final reconciliation from the files, never a model's claimed count."""
    root = Path(directory)
    def read(name):
        return json.loads((root / name).read_text())
    comparison, inbox = read('comparison.json'), read('inbox-review.json')
    baseline = json.loads((root / comparison['baseline']['path']).read_text())
    return validate_actions(read('brief.json'), inbox['boards'] + inbox.get('additional_owner_sweeps', []),
                            baseline, comparison)


def validate_task_bindings(boards, tasks, gaps=()):
    """Compare draft fields with controller-retained native get_task responses."""
    for board in boards:
        for selected in board['selected_actions']:
            if selected.get('missing_execution_task') is True:
                if not any(g.get('id') == selected.get('gap_id') and g.get('source') == 'basicops' for g in gaps):
                    raise ValueError('Missing execution card needs a disclosed BasicOps project gap')
                continue
            source = tasks.get(str(selected.get('task_id')), {}).get('task')
            if not isinstance(source, dict):
                raise ValueError('No actual worker get_task response for selected action')
            assignee = source.get('assignee') or {}
            name = ' '.join(assignee.get(k, '') for k in ('firstName', 'lastName')).strip()
            if (selected.get('url') != source.get('url') or selected.get('status') != source.get('status')
                    or selected.get('task_assignee') != name):
                raise ValueError('Selected URL, status or assignee differs from native task response')
            owner = selected.get('action_owner', board['owner'])
            given = assignee.get('firstName', '').split()
            assigned = bool(given) and owner in (assignee.get('firstName'), given[0])
            orchestrates = bool(re.search(r'\borchestration_owner=' + re.escape(owner) + r'(?=[;\s<]|$)',
                                          source.get('description', '')))
            basis = selected.get('ownership_basis', '')
            if not assigned and not (basis and selected.get('source') and
                    ('coordination' in basis.lower() or orchestrates)):
                raise ValueError('Cross-owner action needs evidenced recommended coordination')


def validate_gmail_searches(coverage, searches):
    """Check source-owned search limits instead of trusting a coverage assertion."""
    observed={x['query']:x for x in searches}
    for project in coverage:
        item=project['gmail'];initial=item.get('initial_query')
        if not isinstance(initial,str) or not re.search(r'(?<!\S)newer_than:30d(?!\S)',initial) or initial not in observed or len(re.findall(r'newer_than:',initial))!=1 or re.search(r'(?<!\S)(?:after|newer):',initial):
            raise ValueError('Project needs an observed initial 30-day Gmail search: '+project['project'])
        followups=item.get('followup_queries',[])
        if not isinstance(followups,list) or any(not isinstance(q,str) or q not in observed for q in followups):
            raise ValueError('Gmail follow-up query was not observed')
        if observed[initial]['truncated'] and not followups:
            raise ValueError('Capped Gmail search needs terminal narrower follow-ups')
        if any(observed[q]['truncated'] for q in followups):
            raise ValueError('Gmail follow-up is still capped')


def validate_activity(research, now=None):
    cutoff=research.get('cutoff')
    if not cutoff:
        raise ValueError('Actual ISO evidence cutoff required')
    at=datetime.fromisoformat(cutoff);now=now or datetime.now(ZoneInfo('Australia/Melbourne'))
    if at.tzinfo is None or at>now:
        raise ValueError('Evidence cutoff must be an actual past read time')
    for item in research.get('projects',[]):
        last=item.get('last_substantive_basicops_at')
        if last:
            timestamp=datetime.fromisoformat(last)
            if timestamp.tzinfo is None or timestamp>at:
                raise ValueError('BasicOps activity timestamp is invalid or after cutoff')
            days=(at.astimezone(ZoneInfo('Australia/Melbourne')).date()-timestamp.astimezone(ZoneInfo('Australia/Melbourne')).date()).days
            if type(item.get('inactivity_days')) is not int or item['inactivity_days']!=days:
                raise ValueError('BasicOps inactivity must be calculated from actual project dates')


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
    validate_activity(research)
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
    for gap in gaps:
        if gap['project'] in names:
            entry = next(p for p in coverage if p['project'] == gap['project'])[gap['source']]
            require(entry.get('status') == 'limited' and entry.get('gap_id') == gap['id'], 'Disclosed gap cannot claim complete project coverage')
    gmail_index=research.get('gmail_source_index',{})
    require(gmail_index.get('path') in file_names,'Controller Gmail search index must be hash-bound')
    bound_file(gmail_index)
    validate_gmail_searches(coverage,read(gmail_index['path'])['searches'])
    files = research.get('evidence_files', [])
    require(bool(files), 'No retained primary evidence')
    for f in files:
        bound_file(f)
    inbox_path = root / 'inbox-review.json'
    require(any((root / f['path']).resolve() == inbox_path for f in files), 'Inbox review must be retained and hash-bound')
    inbox = read('inbox-review.json')
    boards = inbox.get('boards', [])
    require(len(boards) == 3 and {b.get('owner') for b in boards} == {'Michael', 'Kristalyn', 'Aiya'}, 'Three owner inbox sweeps required')
    supplemental = inbox.get('additional_owner_sweeps', [])
    require(isinstance(supplemental, list), 'Supplemental owner sweeps must be a list')
    all_boards = boards + supplemental
    require(len({b.get('owner') for b in all_boards}) == len(all_boards), 'Duplicate owner inbox sweep')
    for board in all_boards:
        require(board.get('status') == 'complete' and board.get('terminal') is True and board.get('board_id') and board.get('section_id'), 'Incomplete owner inbox sweep: ' + str(board.get('owner')))
        require(isinstance(board.get('selected_actions'), list), 'Selected weekly actions missing')
    bound_file(comparison['baseline'])
    baseline_path = Path(comparison['baseline']['path'])
    if not baseline_path.is_absolute():
        baseline_path = root / baseline_path
    baseline = json.loads(baseline_path.read_text())
    require(isinstance(baseline, dict) and isinstance(baseline.get('owners'), list), 'Approved baseline must contain owner actions')
    result = validate_actions(brief, all_boards, baseline, comparison)
    require(research.get('mechanical_action_check') == result,
            'Final mechanical action receipt missing or stale; controller must recompute it')
    if result['count']:
        index = research.get('task_source_index', {})
        require(index.get('path') in file_names, 'Controller task-source index must be hash-bound')
        bound_file(index)
        validate_task_bindings(all_boards, read(index['path'])['tasks'], gaps)
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
