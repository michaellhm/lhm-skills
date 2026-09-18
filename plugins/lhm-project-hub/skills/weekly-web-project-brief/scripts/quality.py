#!/usr/bin/env python3
"""Fail closed on incomplete research or an unreviewed/changed email payload."""
import hashlib
import json
import sys
from pathlib import Path


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate(directory):
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
    access, research, comparison, review = [read(n) for n in ('access-receipt.json', 'research-receipt.json', 'comparison.json', 'quality-review.json')]
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
    files = research.get('evidence_files', [])
    require(bool(files), 'No retained primary evidence')
    for f in files:
        bound_file(f)
    bound_file(comparison['baseline'])
    require(bool(comparison.get('projects')), 'No baseline comparison')
    require(comparison.get('unresolved_regressions') == [], 'Unresolved factual regression')
    require(review.get('accepted') is True and review.get('reviewer') and review.get('issues') == [], 'Independent review not accepted')
    for key, name in [('email', 'email.json'), ('research', 'research-receipt.json'), ('comparison', 'comparison.json'), ('access', 'access-receipt.json')]:
        require(review.get(key + '_sha256') == digest(root / name), 'Review invalidated: ' + name)
    return {'state': 'quality_passed', 'email_sha256': digest(root / 'email.json')}


if __name__ == '__main__':
    print(json.dumps(validate(sys.argv[1])))
