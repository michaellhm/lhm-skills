#!/usr/bin/env python3
"""Local-only review inventory and guarded register operations. No Git/network actions."""
import argparse
from contextlib import contextmanager
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

REGISTER = 'client-review.json'
PROJECT = 'CLIENT-REVIEW.md'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def safe(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('Use repository-relative paths without ..')
    path = root / rel
    # Even internal symlinks are refused for managed files, including lock/register.
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink not allowed: {relative}')
    if not path.resolve().is_relative_to(root):
        raise ValueError('Path escapes repository')
    return path


def fingerprint(root, sources):
    hashes = {}
    for source in sorted(set(sources)):
        path = safe(root, source)
        if not path.is_file():
            raise ValueError(f'Missing content/dependency: {source}')
        hashes[source] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest(hashes)


def read_register(root):
    p = safe(root, REGISTER)
    if not p.exists():
        return {'schema_version': 1, 'pages': [], 'releases': []}
    reg = json.loads(p.read_text(encoding='utf-8'))
    if reg.get('schema_version') != 1 or not isinstance(reg.get('pages'), list) or not isinstance(reg.get('releases'), list):
        raise ValueError('Unsupported or invalid review register')
    return reg


def inventory(root, config):
    if config.get('schema_version') != 1 or not config.get('client'):
        raise ValueError('Config needs schema_version1 and verified client name')
    root = Path(root).resolve()
    pages, gaps = {}, []
    shared = config.get('shared_dependencies', [])
    for item in config.get('pages', []):
        page = copy.deepcopy(item)
        route = page['route']
        if not route.startswith('/') or '?' in route or '#' in route:
            raise ValueError('Page route must be an absolute site path')
        if route in pages:
            raise ValueError(f'Duplicate route: {route}')
        page.setdefault('id', route)
        page.setdefault('dependencies', [])
        if not page.get('sources'):
            raise ValueError(f'Page has no sources: {route}')
        pages[route] = page
    pages_dir = safe(root, 'src/pages')
    resolved = set(config.get('resolved_dynamic_routes', []))
    for path in sorted(pages_dir.rglob('*')) if pages_dir.exists() else []:
        if path.is_symlink():
            safe(root, path.relative_to(root))
        if not path.is_file() or path.suffix not in {'.astro', '.md', '.mdx', '.html'}:
            continue
        source = path.relative_to(root).as_posix()
        rel = path.relative_to(pages_dir)
        if '[' in rel.as_posix():
            mapped = [p for p in pages.values() if source in p['sources'] + p['dependencies']]
            if source not in resolved or not mapped:
                gaps.append({'source': source, 'reason': 'Dynamic route requires verified complete concrete page mapping'})
            continue
        parts = list(rel.with_suffix('').parts)
        if parts[-1] == 'index':
            parts.pop()
        route = '/' + '/'.join(parts) + ('/' if parts else '')
        if route in pages:
            if source not in pages[route]['sources']:
                raise ValueError(f'Duplicate route or incomplete explicit mapping: {route}')
        else:
            pages[route] = {'id': route, 'route': route, 'sources': [source], 'dependencies': []}
    # Conservatively fingerprint all source content/layout/component/data files unless
    # the operator explicitly verifies complete per-page dependency mappings.
    conservative = []
    if config.get('dependency_mapping_verified') is not True:
        for path in sorted(safe(root, 'src').rglob('*')) if safe(root, 'src').exists() else []:
            if path.is_file():
                conservative.append(path.relative_to(root).as_posix())
    ids = set()
    for page in pages.values():
        if page['id'] in ids:
            raise ValueError('Duplicate stable page ID')
        ids.add(page['id'])
        page['dependencies'] = sorted(set(page['dependencies'] + shared + conservative) - set(page['sources']))
        page['fingerprint'] = fingerprint(root, page['sources'] + page['dependencies'])
    return {'pages': sorted(pages.values(), key=lambda p: p['route']), 'gaps': gaps,
            'coverage': 'partial' if gaps else 'mapped-routes',
            'dependency_policy': 'verified' if config.get('dependency_mapping_verified') is True else 'conservative-all-src'}


def propose(root, config, release):
    if not release.get('id') or not isinstance(release['id'], str):
        raise ValueError('Release needs stable id')
    inv = inventory(root, config)
    reg = read_register(root)
    old = {p['id']: p for p in reg['pages']}
    selected, excluded, outside = [], [], []
    routes = release.get('routes')
    known_routes = {p['route'] for p in inv['pages']}
    if routes is not None and set(routes) - known_routes:
        raise ValueError('Requested route not found; resolve inventory first')
    for page in inv['pages']:
        page = copy.deepcopy(page)
        prior = old.get(page['id'], {})
        questions = list(dict.fromkeys(prior.get('questions', []) + release.get('questions', []) + release.get('page_questions', {}).get(page['route'], [])))
        page['questions'] = questions
        page['reason'] = 'new' if not prior else ('changed' if prior.get('fingerprint') != page['fingerprint'] else 'pending')
        if page['route'] in release.get('exclude', []):
            excluded.append(page)
        elif routes is not None and page['route'] not in routes:
            outside.append(page)
        elif prior.get('status') != 'approved' or prior.get('approved_fingerprint') != page['fingerprint'] or questions != prior.get('questions', []):
            selected.append(page)
    removed = [p for p in reg['pages'] if p['id'] not in {v['id'] for v in inv['pages']}]
    proposal = {'schema_version': 1, 'client': config['client'], 'config': config, 'release': release,
                'inventory': inv, 'selected': selected, 'excluded': excluded, 'out_of_scope': outside,
                'removed': removed, 'register_digest': digest(reg)}
    proposal['digest'] = digest(proposal)
    return proposal


@contextmanager
def locked(root):
    path = safe(root, '.client-review.lock')
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError('Another review writer is active; inspect lock owner before recovery') from exc
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink()


def atomic_write(path, text):
    fd, name = tempfile.mkstemp(prefix='.review-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def render_project(reg):
    lines = ['# Website review', '', f"Client: {reg.get('client', '')}", '',
             'Generated from client-review.json. Use review-website to record decisions.', '']
    for page in reg['pages']:
        mark = 'x' if page['status'] == 'approved' else ' '
        lines.append(f"- [{mark}] {page['route']} ({page['status']})")
        for q in page.get('questions', []):
            lines.append(f"  - {q}: {page.get('answers', {}).get(q, 'Awaiting answer')}")
    lines += ['', '## Releases', '']
    for release in reg['releases']:
        lines.append(f"- {release['id']}: {len(release['page_ids'])} pages, approved by {release['operator']}")
    return '\n'.join(lines) + '\n'


def save(root, reg):
    # Validate both destinations before writing either. JSON is authoritative;
    # render CLI repairs the derived checklist if its write fails.
    jp, mp = safe(root, REGISTER), safe(root, PROJECT)
    cp = safe(root, '.lhm-review/client-config.json')
    if cp.exists():
        atomic_write(cp, json.dumps(reg['config'], indent=2, ensure_ascii=False) + '\n')
    atomic_write(jp, json.dumps(reg, indent=2, ensure_ascii=False) + '\n')
    atomic_write(mp, render_project(reg))


def apply_proposal(root, proposal, approval):
    content = {k: v for k, v in proposal.items() if k != 'digest'}
    if approval.get('approved') is not True or not approval.get('operator') or not approval.get('evidence') or approval.get('proposal_digest') != proposal.get('digest') or digest(content) != proposal.get('digest'):
        raise ValueError('Explicit operator approval matching unchanged proposal is required')
    with locked(root):
        reg = read_register(root)
        existing = next((x for x in reg['releases'] if x.get('proposal_digest') == proposal['digest']), None)
        if existing:
            if inventory(root, proposal['config']) != proposal['inventory']:
                raise ValueError('Content changed after applied release')
            return reg
        if digest(reg) != proposal['register_digest'] or propose(root, proposal['config'], proposal['release']) != proposal:
            raise ValueError('Stale proposal; regenerate and review again')
        if proposal['inventory']['gaps'] and approval.get('acknowledge_partial_coverage') is not True:
            raise ValueError('Resolve gaps or explicitly acknowledge partial coverage')
        if any(x['id'] == proposal['release']['id'] for x in reg['releases']):
            raise ValueError('Release ID already used; choose a new revision ID')
        reg = copy.deepcopy(reg)
        old = {p['id']: p for p in reg['pages']}
        chosen = {p['id']: p for p in proposal['selected']}
        current_ids = set()
        for current in proposal['inventory']['pages']:
            current_ids.add(current['id'])
            prior = old.get(current['id'])
            if not prior and current['id'] not in chosen:
                continue
            page = copy.deepcopy(prior or current)
            page.setdefault('approval_history', [])
            page.setdefault('answers', {})
            page.setdefault('releases', [])
            changed = prior and prior.get('fingerprint') != current['fingerprint']
            page.update(current)
            questions_changed = current['id'] in chosen and chosen[current['id']]['questions'] != (prior or {}).get('questions', [])
            if not prior or changed or questions_changed or prior.get('status') == 'needs-reconciliation':
                if prior and prior.get('status') == 'approved':
                    page['approval_history'].append({k: prior[k] for k in ['approved_fingerprint', 'approval'] if k in prior})
                page['status'] = 'awaiting-review'
                page.pop('approved_fingerprint', None)
                page.pop('approval', None)
                if changed:
                    page['previous_answers'] = page.pop('answers', {})
                    page['answers'] = {}
            if current['id'] in chosen:
                page['questions'] = chosen[current['id']]['questions']
                if proposal['release']['id'] not in page['releases']:
                    page['releases'].append(proposal['release']['id'])
            old[current['id']] = page
        for page_id in set(old) - current_ids:
            old[page_id]['status'] = 'needs-reconciliation'
        reg.update({'client': proposal['client'], 'config': proposal['config'], 'pages': sorted(old.values(), key=lambda p: p['route'])})
        reg['releases'].append({'id': proposal['release']['id'], 'page_ids': list(chosen),
                                'operator': approval['operator'], 'evidence': approval['evidence'],
                                'proposal_digest': proposal['digest'], 'coverage': proposal['inventory']['coverage']})
        save(root, reg)
        return reg


def record_review(root, page_id, status, approver, evidence, answers, expected_fingerprint=None):
    if status not in {'approved', 'changes-underway', 'needs-lhm', 'awaiting-review'} or not approver or not evidence:
        raise ValueError('Valid status, explicit person and decision evidence required')
    with locked(root):
        reg = read_register(root)
        page = next((p for p in reg['pages'] if p['id'] == page_id), None)
        if not page or page['status'] == 'needs-reconciliation':
            raise ValueError('Page not available for review')
        actual = fingerprint(root, page['sources'] + page['dependencies'])
        expected = expected_fingerprint or page['fingerprint']
        if actual != expected:
            raise ValueError('Content changed; preview current content and provide its fingerprint')
        if any(q not in page.get('questions', []) for q in answers):
            raise ValueError('Answer refers to an unknown review question')
        # A revision of a shared dependency invalidates other affected approvals.
        for other in reg['pages']:
            if other['id'] == page_id or other['status'] == 'needs-reconciliation':
                continue
            latest = fingerprint(root, other['sources'] + other['dependencies'])
            if latest != other['fingerprint']:
                if other.get('approval'):
                    other.setdefault('approval_history', []).append(other['approval'])
                other['status'] = 'awaiting-review'
                other.pop('approved_fingerprint', None)
                other.pop('approval', None)
        if actual != page['fingerprint']:
            if page.get('approval'):
                page.setdefault('approval_history', []).append(page['approval'])
            page['previous_answers'] = page.get('answers', {})
            page['answers'] = {}
        page.update({'status': status, 'fingerprint': actual})
        page.setdefault('answers', {}).update(answers)
        if status == 'approved':
            if set(page.get('questions', [])) - set(page['answers']):
                raise ValueError('Answer release questions before approval, or record a needs-lhm decision')
            page['approved_fingerprint'] = actual
            page['approval'] = {'person': approver, 'evidence': evidence, 'at': datetime.now(timezone.utc).isoformat()}
        else:
            page.pop('approved_fingerprint', None)
            page.pop('approval', None)
            page['decision'] = {'person': approver, 'evidence': evidence}
        save(root, reg)
        return reg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['scan', 'apply', 'review', 'render', 'fingerprint'])
    parser.add_argument('--root', required=True, type=Path)
    for name in ['config', 'release', 'proposal', 'approval', 'answers']:
        parser.add_argument('--' + name, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--page-id')
    parser.add_argument('--status')
    parser.add_argument('--person')
    parser.add_argument('--evidence')
    parser.add_argument('--fingerprint')
    args = parser.parse_args()
    def load(name):
        path = getattr(args, name)
        if path is None:
            raise ValueError(f'--{name} is required')
        return json.loads(path.read_text(encoding='utf-8'))
    try:
        if args.output and args.output.resolve() in {safe(args.root, REGISTER).resolve(), safe(args.root, PROJECT).resolve()}:
            raise ValueError('Output cannot overwrite managed review records')
        if args.command == 'scan':
            result = propose(args.root, load('config'), load('release'))
        elif args.command == 'apply':
            result = apply_proposal(args.root, load('proposal'), load('approval'))
        elif args.command == 'review':
            result = record_review(args.root, args.page_id, args.status, args.person, args.evidence, load('answers'), args.fingerprint)
        elif args.command == 'fingerprint':
            p = next(p for p in read_register(args.root)['pages'] if p['id'] == args.page_id)
            result = {'fingerprint': fingerprint(args.root, p['sources'] + p['dependencies'])}
        else:
            with locked(args.root):
                result = read_register(args.root)
                atomic_write(safe(args.root, PROJECT), render_project(result))
        output = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if args.output:
            if args.output.resolve() in {safe(args.root, REGISTER).resolve(), safe(args.root, PROJECT).resolve()}:
                raise ValueError('Output cannot overwrite managed review records')
            atomic_write(args.output, output)
        else:
            print(output, end='')
    except (ValueError, OSError, KeyError, StopIteration) as exc:
        parser.exit(2, f'Review operation stopped: {exc}\n')

if __name__ == '__main__':
    main()
