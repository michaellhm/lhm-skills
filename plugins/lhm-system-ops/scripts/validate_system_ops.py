#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {
    'lhm-cto', 'lhm-capability-researcher', 'lhm-platform-engineer',
    'lhm-qa-tester', 'lhm-security-reviewer', 'lhm-plugin-release-manager',
    'lhm-chief-of-staff-source-handoff', 'lhm-context-research-source-handoff',
    'lhm-cto-source-handoff', 'lhm-head-of-production-source-handoff',
}


def generated_bytecode_paths(root):
    return sorted(
        path.relative_to(root)
        for path in root.rglob('*')
        if '__pycache__' in path.parts or (path.is_file() and path.suffix == '.pyc')
    )


def main():
    errors = []
    for relative in generated_bytecode_paths(PLUGIN):
        errors.append(f'generated Python bytecode in plugin release contents: {relative}')
    for relative in ('.codex-plugin/plugin.json', '.claude-plugin/plugin.json'):
        path = PLUGIN / relative
        try:
            manifest = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'{relative}: {exc}')
            continue
        if manifest.get('name') != PLUGIN.name or manifest.get('version') != '0.6.2':
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
        'assets/host/lhm-cto-branch-publisher',
        'assets/host/lhm-asp-sitemap-publisher',
        'assets/host/lhm-prototype-publisher',
        'assets/systemd/lhm-cto-result-resumer.path',
        'assets/systemd/lhm-cto-result-resumer.service',
        'assets/systemd/lhm-cto-result-resumer.timer',
        'assets/container/source-dispatch',
        'assets/host/lhm-source-production-runtime',
        'assets/host/lhm-source-adapter',
        'assets/host/lhm-evidence-fathom-backend',
        'assets/sudoers/lhm-evidence-fathom-backend',
        'assets/worker/source-production-worker-profile.json',
        'assets/systemd/lhm-source-production.path',
        'assets/systemd/lhm-source-production.service',
        'assets/install/install-source-production.sh',
        'assets/install/preflight-evidence-bridge.py',
        'assets/gateways/lhm-evidence-claude-dispatcher',
        'assets/gateways/lhm-evidence-claude-worker',
        'assets/gateways/lhm-evidence-fathom-backend',
    }
    for relative in required_assets:
        if not (PLUGIN / relative).is_file():
            errors.append(f'missing runtime asset: {relative}')
    schemas = list((PLUGIN / 'references/evidence-bridge').glob('*.schema.json'))
    if len(schemas) != 8:
        errors.append('evidence bridge requires exact request/result schemas for four backends')
    for schema_path in schemas:
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
        if schema.get('additionalProperties') is not False:
            errors.append(f'{schema_path.relative_to(PLUGIN)}: schema must fail closed')
    service = (PLUGIN / 'assets/systemd/lhm-cto-plugin-dispatch.service').read_text(encoding='utf-8')
    if 'setfacl' in service:
        errors.append('dispatcher service must not grant ctoworker traversal into the Hermes home tree')
    if 'Environment=PATH=/home/ctoworker/.local/bin:/usr/bin:/bin' not in service:
        errors.append('dispatcher service is missing the bounded CTO runtime PATH')
    if 'PrivateTmp=yes' not in service:
        errors.append('dispatcher service is missing its private writable sandbox temporary directory')
    if 'Hermes\\x20Reviews' not in service:
        errors.append('dispatcher service is missing the bounded Obsidian review-note write path')
    dispatcher = (PLUGIN / 'assets/host/lhm-cto-plugin-dispatcher').read_text(encoding='utf-8')
    if "WORKER_RUNS = WORKSPACES / '.runs'" not in dispatcher:
        errors.append('dispatcher is missing the private CTO run-control directory')
    if "subprocess.run(['/usr/sbin/runuser'" not in dispatcher:
        errors.append('dispatcher must use the absolute restricted-worker launcher path')
    callback = (PLUGIN / 'assets/host/lhm-cto-result-resumer').read_text(encoding='utf-8')
    if 'max_iterations' not in callback or 'questions_for_chief' not in callback:
        errors.append('CTO result resumer is missing the bounded evidence-loop contract')
    publisher = (PLUGIN / 'assets/host/lhm-cto-branch-publisher').read_text(encoding='utf-8')
    for required in ('refs/heads/{branch}', 'StrictHostKeyChecking=yes', "branch publisher credential is not configured", "'Hermes Reviews'"):
        if required not in publisher:
            errors.append(f'branch publisher is missing control: {required}')
    if '--untracked-files=all' not in dispatcher or '--untracked-files=all' not in publisher:
        errors.append('dispatcher and publisher must enumerate individual untracked files')
    prototype_publisher = (PLUGIN / 'assets/host/lhm-prototype-publisher').read_text(encoding='utf-8')
    for required in ("REPOSITORY = 'michaellhm/lhm-prototype'", "BRANCH = 'main'", "SOURCE_ROOT = Path('/var/lib/lhm-prototype-publication/incoming')", "SSH_KEY = Path('/etc/lhm-prototype-publisher/id_ed25519')", 'schema_version', 'source_basicops_task', 'governed_parent', 'source_package_sha256', 'file_manifest', 'idempotency_key', 'standing_authority_reference', 'StrictHostKeyChecking=yes', 'actions/workflows/{WORKFLOW["id"]}/runs?', 'public prototype content does not match approved index.html'):
        if required not in prototype_publisher:
            errors.append(f'prototype publisher is missing bounded control: {required}')
    for name in ('prototype-publication.request.schema.json','prototype-publication.result.schema.json','prototype-basicops-handoff.schema.json','capability-restored.schema.json'):
        schema = json.loads((PLUGIN / 'references' / name).read_text(encoding='utf-8'))
        if schema.get('additionalProperties') is not False:
            errors.append(f'{name}: schema must fail closed')
    source_service = (PLUGIN / 'assets/systemd/lhm-source-production.service').read_text(encoding='utf-8')
    if '"/home/hermes/.hermes/profiles/lhm_brain/vault/01 Inbox/Hermes Reviews"' not in source_service:
        errors.append('source service must quote the ReadWritePaths folder containing spaces')
    profile = json.loads((PLUGIN / 'assets/worker/source-production-worker-profile.json').read_text(encoding='utf-8'))
    if not profile.get('commands') or any(not command.startswith('/usr/local/libexec/') for command in profile['commands']):
        errors.append('source worker profile commands must be absolute installed executables')
    if errors:
        print('\n'.join(f'ERROR: {item}' for item in errors), file=sys.stderr)
        return 1
    print(f'LHM system ops validation passed: {len(found)} skills')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
