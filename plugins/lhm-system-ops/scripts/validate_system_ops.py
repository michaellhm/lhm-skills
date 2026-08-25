#!/usr/bin/env python3
import ast
import hashlib
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
    'release-publishing-engineer',
}


def producer_incoming_name(expression):
    """Extract the literal directory selected by the native restore expression."""
    try:
        tree = ast.parse(expression, mode='eval')
    except SyntaxError as exc:
        raise ValueError('invalid producer restore path expression') from exc
    nodes = []
    node = tree.body
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        nodes.append(node.right)
        node = node.left
    nodes.reverse()
    if (not isinstance(node, ast.Name) or node.id != 'BASE' or len(nodes) != 2
            or not isinstance(nodes[0], ast.Constant) or not isinstance(nodes[0].value, str)
            or not isinstance(nodes[1], ast.JoinedStr)):
        raise ValueError('producer restore path must be BASE / literal / event filename')
    return nodes[0].value


def validate_work_control_parity(contract, work_resumer, work_path):
    errors = []
    host_store = contract.get('store_host')
    try:
        incoming_name = producer_incoming_name(contract.get('producer_restore_path_expression', ''))
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    incoming_host = f'{host_store}/{incoming_name}' if host_store else None
    if not host_store or f"BASE = Path('{host_store}')" not in work_resumer:
        errors.append('work resumer BASE does not match the authoritative host store')
    if f"INCOMING = BASE / '{incoming_name}'" not in work_resumer:
        errors.append('work resumer INCOMING does not match the producer restore path literal')
    expected_glob = f'{incoming_host}/*.json'
    if contract.get('watch_glob_host') != expected_glob:
        errors.append('deployment watch glob does not match the producer restore path literal')
    if f'PathExistsGlob={expected_glob}' not in work_path:
        errors.append('work resumer path unit does not watch the producer restore path literal')
    handoff_host = contract.get('handoff_host')
    handoff_container = contract.get('handoff_container')
    expected_handoff_host = f'{host_store}/handoffs'
    container_store = contract.get('producer_store_container')
    expected_handoff_container = f'{container_store}/handoffs'
    if handoff_host != expected_handoff_host:
        errors.append('deployment handoff host is not inside the authoritative host store')
    if handoff_container != expected_handoff_container:
        errors.append('deployment handoff container path does not use the authoritative /opt/data bind')
    if "HANDOFFS = BASE / 'handoffs'" not in work_resumer:
        errors.append('work resumer handoff root is not derived from the authoritative host store')
    if f"HERMES_HANDOFFS = Path('{expected_handoff_container}')" not in work_resumer:
        errors.append('work resumer container handoff root does not match deployment')
    return errors


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
        if manifest.get('name') != PLUGIN.name or manifest.get('version') != '0.9.18':
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
        'assets/host/lhm-approved-project-hub-deployer',
        'assets/host/provision-project-hub-release-mount',
        'assets/systemd/home-hermes-.hermes-immutable\\x2dplugin\\x2dreleases.mount',
        'assets/systemd/lhm-cto-plugin-dispatch.path',
        'assets/systemd/lhm-cto-plugin-dispatch.service',
        'assets/host/lhm-cto-result-resumer',
        'assets/host/lhm-work-resumer',
        'assets/systemd/lhm-work-resumer.path',
        'assets/systemd/lhm-work-resumer.service',
        'assets/host/lhm-cto-branch-publisher',
        'assets/host/lhm-asp-sitemap-publisher',
        'assets/host/lhm-prototype-publisher',
        'assets/systemd/lhm-cto-result-resumer.path',
        'assets/systemd/lhm-cto-result-resumer.service',
        'assets/systemd/lhm-cto-result-resumer.timer',
        'assets/container/source-dispatch',
        'assets/container/claude-dispatch',
        'assets/host/lhm-source-production-runtime',
        'assets/host/lhm-source-adapter',
        'assets/host/lhm-evidence-fathom-backend',
        'assets/sudoers/lhm-evidence-fathom-backend',
        'assets/worker/source-production-worker-profile.json',
        'assets/systemd/lhm-source-production.path',
        'assets/systemd/lhm-source-production.service',
        'assets/install/install-source-production.sh',
        'assets/install/preflight-evidence-bridge.py',
        'assets/install/install-shared-claude-gateway.py',
        'assets/gateways/lhm-evidence-claude-dispatcher',
        'assets/gateways/lhm-evidence-claude-worker',
        'assets/gateways/lhm-evidence-fathom-backend',
        'assets/gateways/lhm-shared-claude-dispatcher',
        'assets/gateways/lhm-shared-claude-worker',
        'assets/systemd/lhm-claude-dispatch.service',
        'assets/systemd/lhm-brain-gateway-acl.conf',
        'references/shared-claude-gateway-release.json',
        'references/shared-claude-gateway-release.md',
        'references/google-ads-evidence-pack.md',
        'references/project-hub-production-release.md',
        'references/project-hub-deployer-release.json',
        'references/hermes-project-hub-readonly-mount.compose.yaml',
        'scripts/build_project_hub_release.py',
    }
    for relative in required_assets:
        if not (PLUGIN / relative).is_file():
            errors.append(f'missing runtime asset: {relative}')
    deployer_release = json.loads((PLUGIN / 'references/project-hub-deployer-release.json').read_text(encoding='utf-8'))
    deployer_source = PLUGIN / deployer_release.get('source', '')
    if (deployer_release.get('capability_id') != 'LHM-PROJECT-HUB-DEPLOYER'
            or deployer_release.get('destination') != '/usr/local/libexec/lhm-approved-project-hub-deployer'
            or not deployer_source.is_file()
            or hashlib.sha256(deployer_source.read_bytes()).hexdigest() != deployer_release.get('sha256')
            or deployer_source.stat().st_size != deployer_release.get('size_bytes')
            or deployer_release.get('mode') != '0755'):
        errors.append('Project Hub deployer release manifest does not bind the exact source and destination')
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
    work_contract = json.loads((PLUGIN / 'references/work-control-deployment.json').read_text(encoding='utf-8'))
    work_resumer = (PLUGIN / 'assets/host/lhm-work-resumer').read_text(encoding='utf-8')
    work_path = (PLUGIN / 'assets/systemd/lhm-work-resumer.path').read_text(encoding='utf-8')
    work_service = (PLUGIN / 'assets/systemd/lhm-work-resumer.service').read_text(encoding='utf-8')
    errors.extend(validate_work_control_parity(work_contract, work_resumer, work_path))
    if f"ReadWritePaths={work_contract['store_host']}" not in work_service:
        errors.append('work resumer service is missing its authoritative store write boundary')
    if '/opt/run' in work_resumer or '/opt/run' in json.dumps(work_contract) or '/opt/run' in work_service:
        errors.append('work resumer release contains an unsupported /opt/run mount assumption')
    if '/var/lib/lhm-work-control' in work_resumer or '/var/lib/lhm-work-control' in work_path:
        errors.append('work resumer release contains the empty alternate store')
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
    profiles=json.loads((PLUGIN/'references/destination-profiles.json').read_text(encoding='utf-8'))
    enabled=[profile for profile in profiles.get('profiles',[]) if profile.get('enabled')]
    if [profile.get('profile_id') for profile in enabled] != ['prototype-main-v1']:
        errors.append('only prototype-main-v1 may be enabled')
    if any(profile.get('credential_reference') and profile.get('credential_reference') == enabled[0].get('credential_reference') for profile in profiles['profiles'] if not profile.get('enabled')):
        errors.append('disabled profiles must not inherit the prototype credential')
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
