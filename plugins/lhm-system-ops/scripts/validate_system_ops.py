#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {
    'lhm-cto', 'lhm-capability-researcher', 'lhm-platform-engineer',
    'lhm-qa-tester', 'lhm-security-reviewer', 'lhm-plugin-release-manager',
}


def main():
    errors = []
    for relative in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
        path = PLUGIN / relative
        try:
            manifest = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'{relative}: {exc}')
            continue
        if manifest.get('name') != PLUGIN.name or manifest.get('version') != '0.2.1':
            errors.append(f'{relative}: name/version mismatch')
    found = {p.parent.name for p in (PLUGIN / 'skills').glob('*/SKILL.md')}
    if found != REQUIRED_SKILLS:
        errors.append(f'skill set mismatch: expected {sorted(REQUIRED_SKILLS)}, found {sorted(found)}')
    for path in (PLUGIN / 'skills').glob('*/SKILL.md'):
        text = path.read_text(encoding='utf-8')
        match = re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: (.+?)\n---\n', text, re.S)
        if not match or match.group(1) != path.parent.name:
            errors.append(f'{path.relative_to(PLUGIN)}: invalid front matter or name')
        if '[TODO:' in text:
            errors.append(f'{path.relative_to(PLUGIN)}: TODO placeholder')
    prohibited = ('.env', 'id_rsa', 'credentials.json', 'approval.json')
    for path in PLUGIN.rglob('*'):
        if path.is_file() and path.name in prohibited:
            errors.append(f'prohibited sensitive filename: {path.relative_to(PLUGIN)}')
    required_assets = {
        'assets/host/cto-dispatch',
        'assets/host/lhm-cto-plugin-dispatcher',
        'assets/host/lhm-approved-plugin-deployer',
        'assets/systemd/lhm-cto-plugin-dispatch.path',
        'assets/systemd/lhm-cto-plugin-dispatch.service',
        'assets/host/lhm-cto-result-resumer',
        'assets/systemd/lhm-cto-result-resumer.path',
        'assets/systemd/lhm-cto-result-resumer.service',
        'assets/systemd/lhm-cto-result-resumer.timer',
    }
    for relative in required_assets:
        if not (PLUGIN / relative).is_file():
            errors.append(f'missing runtime asset: {relative}')
    service = (PLUGIN / 'assets/systemd/lhm-cto-plugin-dispatch.service').read_text(encoding='utf-8')
    if 'setfacl' in service:
        errors.append('dispatcher service must not grant ctoworker traversal into the Hermes home tree')
    if 'Environment=PATH=/home/ctoworker/.local/bin:/usr/bin:/bin' not in service:
        errors.append('dispatcher service is missing the bounded CTO runtime PATH')
    if 'PrivateTmp=yes' not in service:
        errors.append('dispatcher service is missing its private writable sandbox temporary directory')
    dispatcher = (PLUGIN / 'assets/host/lhm-cto-plugin-dispatcher').read_text(encoding='utf-8')
    if "WORKER_RUNS = WORKSPACES / '.runs'" not in dispatcher:
        errors.append('dispatcher is missing the private CTO run-control directory')
    if "subprocess.run(['/usr/sbin/runuser'" not in dispatcher:
        errors.append('dispatcher must use the absolute restricted-worker launcher path')
    callback = (PLUGIN / 'assets/host/lhm-cto-result-resumer').read_text(encoding='utf-8')
    if 'max_iterations' not in callback or 'questions_for_chief' not in callback:
        errors.append('CTO result resumer is missing the bounded evidence-loop contract')
    if errors:
        print('\n'.join(f'ERROR: {item}' for item in errors), file=sys.stderr)
        return 1
    print(f'LHM system ops validation passed: {len(found)} skills')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
