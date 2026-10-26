#!/usr/bin/env python3
"""Root queue supervisor: verified intake, bounded snapshots, non-root providers."""
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
from client_directory import refresh as refresh_directory
from workspaces import provision, publish_registry, location

BASE = Path('/home/hermes/.hermes/profiles/lhm_brain/dispatch/task-router')
WORK = Path('/var/lib/lhm-task-router')
VAULT = Path('/home/hermes/.hermes/profiles/lhm_brain/vault-task-router').resolve()
PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
ID = re.compile(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*')


def read(path, limit=1048576):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as f:
        info = os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError('Invalid or oversized file')
        return f.read()


def atomic(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.chown(tmp, 0, 10000)
    tmp.chmod(0o640)
    tmp.replace(path)


def verified(request_id):
    result = subprocess.run(['docker', 'exec', '--user', 'hermes', 'hermes', '/opt/hermes/.venv/bin/python',
        '/opt/data/profiles/lhm_chief_of_staff/task-router/server.py', '--verify', request_id],
        capture_output=True, text=True, timeout=50)
    if result.returncode:
        raise ValueError('Human instruction, task state or client binding failed re-verification')
    return json.loads(result.stdout)


def copy_prior(request, workspace):
    """Copy bounded task evidence across providers; never mount another provider home."""
    handoff = request.get('provider_handoff')
    if not handoff:
        return
    previous = handoff.get('request_id', '')
    if (not ID.fullmatch(previous) or handoff.get('from_provider') not in {'codex', 'claude'}
            or handoff['from_provider'] == request['provider']):
        raise ValueError('Invalid provider handoff')
    receipt = json.loads(read(BASE / 'runs' / previous / 'receipt.json'))
    if (receipt.get('status') not in {'needs_review', 'failed'}
            or receipt.get('thread_id') != handoff.get('thread_id')
            or receipt.get('provider') != handoff['from_provider']):
        raise ValueError('Prior provider must be terminal with the exact saved session')
    old_run = WORK / previous
    old = json.loads(read(old_run / 'request.json'))
    if (old.get('task_id') != request['task_id'] or old.get('client_id') != request['client_id']
            or old.get('provider') != handoff['from_provider'] or old.get('request_id') != previous
            or (old.get('permission_ceiling') != request['permission_ceiling']
                and not (request.get('handoff_mode') == 'provider_execution'
                         and request['permission_ceiling'] == 'provider_tool_approval'
                         and old.get('permission_ceiling') == 'prepare_for_review'))):
        raise ValueError('Prior task, client, provider or permission ceiling mismatch')
    source = old_run / 'workspace'
    mapping = old_run / 'workspace-location.json'
    if mapping.exists():
        paths = json.loads(read(mapping))
        expected = location(handoff['from_provider'], request['client_id'])
        source = expected / 'tasks' / previous
        if paths != {'workspace': str(expected), 'task_directory': str(source)}:
            raise ValueError('Prior workspace is outside the registered task root')
    if source.is_symlink() or not source.is_dir():
        raise ValueError('Prior draft directory is unavailable or untrusted')
    target = workspace / 'prior-work'
    target.mkdir()
    manifest = {'source': handoff, 'verification': 'Prior draft evidence only; not fresh account readback or authority', 'files': []}
    size = 0
    candidates = [old_run / 'result.md']
    # No recursive traversal of arbitrary provider-created directories.
    draft_root = source / 'drafts'
    if draft_root.is_symlink():
        raise ValueError('Prior drafts must not be symlinked')
    if draft_root.is_dir():
        import itertools
        candidates += sorted(itertools.islice(draft_root.iterdir(), 64))
    for candidate in candidates:
        if len(manifest['files']) >= 24 or size >= 200000:
            break
        if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 64000:
            continue
        if candidate.suffix.lower() not in {'.md', '.txt', '.csv', '.json', '.html', '.css', '.js'}:
            continue
        content = read(candidate, 64000)
        count = len(content.encode())
        if size + count > 200000:
            continue
        name = f'{len(manifest["files"]):02d}-' + candidate.name
        (target / name).write_text(content)
        manifest['files'].append({'copy': name, 'source': str(candidate.relative_to(old_run)) if candidate.is_relative_to(old_run) else 'drafts/' + candidate.name})
        size += count
    if not manifest['files']:
        raise ValueError('No prior draft/result could be preserved; do not launch a context-free handoff')
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


def prepare(request):
    request_id, provider = request['request_id'], request['provider']
    if provider not in {'codex', 'claude'}:
        raise ValueError('Invalid provider')
    uid = 10001 if provider == 'codex' else 10002
    home = '/home/' + ('codexworker' if provider == 'codex' else 'claudeworker')
    run = WORK / request_id
    run.mkdir(mode=0o750)
    client_root, workspace = provision(request, uid)
    (run / 'workspace-location.json').write_text(json.dumps({'workspace': str(client_root), 'task_directory': str(workspace)}))
    (workspace / 'drafts').mkdir()
    for name in ['.git', '.codex', '.agents']:
        (workspace / name).mkdir()
    context = workspace / 'context'
    context.mkdir()
    prefix = request['client']['vault_prefix']
    if Path(prefix).is_absolute() or '..' in Path(prefix).parts:
        raise ValueError('Invalid registered vault prefix')
    source = (VAULT / prefix).resolve()
    if not source.is_relative_to(VAULT):
        raise ValueError('Registered client context escapes the knowledge root')
    missing = [] if source.is_dir() else ['Registered client context is unavailable; open source links in the provider conversation']
    sources, size = [], 0
    priority = {str(VAULT / p): i for i, p in enumerate(request['client'].get('context_notes', []))}
    candidates = sorted(source.rglob('*.md'), key=lambda p: (priority.get(str(p), 999), len(p.parts), str(p)))
    for path in candidates:
        if len(sources) >= 32 or size >= 160000:
            break
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            continue
        limit = 512000 if str(path) in priority else 32000
        try:
            if path.stat().st_size > limit:
                missing.append('Oversized context source: ' + str(path.relative_to(VAULT)))
                continue
            full = read(path, limit).encode()
        except OSError:
            missing.append('Unreadable context source: ' + str(path.relative_to(VAULT)))
            continue
        raw = full if len(full) <= 32000 else (full[:8000].decode(errors='ignore') + '\n[Bounded extract: middle omitted; consult canonical source for full evidence.]\n' + full[-23000:].decode(errors='ignore')).encode()
        if len(raw) > 32000 or size + len(raw) > 160000:
            continue
        name = f'{len(sources):02d}-{path.name}'
        (context / name).write_bytes(raw)
        sources.append({'snapshot': 'context/' + name, 'source': str(path.relative_to(VAULT)), 'truncated': len(raw) != len(full)})
        size += len(raw)
    if not sources:
        missing.append('No readable bounded markdown snapshots; task, discussion and source links are still supplied')
    (workspace / 'task-context.json').write_text(json.dumps({
        'client_id': request['client_id'], 'client': request['client'],
        'task_id': request['task_id'], 'task_url': request['task_url'], 'task_name': request['title'],
        'task_description': request['description'], 'personal_instruction': request['instruction'],
        'instruction_message_id': request['instruction_message_id'],
        'instruction_sha256': request['instruction_sha256'],
        'discussion': request.get('context_messages', []), 'permission_ceiling': request['permission_ceiling'],
        'source_links': request.get('source_links', []), 'missing_context': missing,
        **{k: request[k] for k in ['capability_contract_version', 'agent', 'entry_skill', 'required_skills',
                                  'required_connectors', 'optional_skills', 'optional_connectors'] if k in request},
        'sources': sources, 'snapshot_limit': '32 markdown files, 160KB; missing evidence must be reported'}, indent=2))
    copy_prior(request, workspace)
    (run / 'request.json').write_text(json.dumps(request))
    for path in [run, *run.rglob('*'), workspace, *workspace.rglob('*')]:
        os.chown(path, uid, uid)
        path.chmod(0o750 if path.is_dir() else 0o640)
    for name in ['.git', '.codex', '.agents']:
        os.chown(workspace / name, 0, 0)
        (workspace / name).chmod(0o555)
    publish_registry()
    from site_workspace import CONFIG as site_config, config as read_site_config, site_for
    if site_config.exists():
        settings = read_site_config()
        if any(row['client_id'] == request['client_id'] for row in settings['sites'].values()):
            site_for(request, settings)
            subprocess.run(['systemd-run', '--quiet', '--collect', '--unit=lhm-site-' + request_id,
                            '/usr/bin/python3', '/usr/local/libexec/lhm-task-router/site_workspace.py', 'run', request_id],
                           check=True, timeout=20)
            return
    launch(request, run, client_root)


def launch(request, run, client_root):
    provider, request_id = request['provider'], request['request_id']
    uid = 10001 if provider == 'codex' else 10002
    home = '/home/' + ('codexworker' if provider == 'codex' else 'claudeworker')
    props = ['User=' + ('codexworker' if provider == 'codex' else 'claudeworker'),
             'Group=' + str(uid), 'ProtectSystem=strict', 'ProtectHome=tmpfs',
             'BindPaths=' + home + ' ' + str(run) + ' ' + str(client_root), 'ReadWritePaths=' + str(run) + ' ' + home + ' ' + str(client_root),
             'TemporaryFileSystem=/var/lib/lhm-client-workspaces:ro /var/lib/lhm-task-router:ro' + (' /home/codexworker/clients:ro' if provider == 'codex' else ''),
             'InaccessiblePaths=-' + home + '/.ssh',
             'NoNewPrivileges=true', 'PrivateTmp=true', 'PrivateDevices=true',
             'ProtectKernelTunables=true', 'ProtectControlGroups=true', 'RestrictSUIDSGID=true',
             'UMask=0027', 'RuntimeMaxSec=' + ('86500' if request.get('handoff_mode') in {'provider_execution', 'provider_conversation'} else '1300'), 'WorkingDirectory=' + str(client_root)]
    if (run / 'site-location.json').exists():
        from site_workspace import validate_mapping
        site = validate_mapping(run, request)
        task_path = site['task_directory']
        props += ['BindPaths=' + task_path, 'ReadWritePaths=' + task_path,
                  'InaccessiblePaths=-/etc/lhm-sites -/var/lib/lhm-sites/.locks']
        # Read-only old workspace lock remains available for the original provider/client lease.
        original = json.loads(read(run / 'workspace-location.json'))['workspace']
        props += ['BindReadOnlyPaths=' + original + '/.control']
    command = ['systemd-run', '--quiet', '--collect', '--unit=lhm-task-' + request_id]
    for prop in props:
        command += ['--property=' + prop]
    command += ['/usr/bin/python3', '/usr/local/libexec/lhm-task-router/worker.py', str(run), provider]
    subprocess.run(command, check=True, timeout=20)


def delivery_tick():
    from delivery import deliver
    admitted = 0
    for queue_run in sorted((BASE / 'runs').iterdir()):
        if not queue_run.is_dir() or not ID.fullmatch(queue_run.name):
            continue
        receipt = json.loads(read(queue_run / 'receipt.json'))
        if receipt.get('status') != 'needs_review' or not (receipt.get('delivery_required') or (queue_run / 'delivery-request.json').exists()):
            continue
        target = queue_run / 'delivery.json'
        old = json.loads(read(target)) if target.exists() else {}
        if old.get('artefact_state') in {'delivered', 'no_files_produced'} or time.time() - old.get('attempted_at', 0) < 60:
            continue
        if admitted >= 2:
            break
        admitted += 1
        try:
            request = verified(queue_run.name)
            run = WORK / queue_run.name
            if json.loads(read(run / 'request.json')) != request:
                raise ValueError('Producer request no longer matches the verified task')
            deliver(request, run, queue_run)
        except Exception as exc:
            partial = json.loads(read(target)) if target.exists() else old
            atomic(target, {**partial, 'artefact_state':'delivery_incomplete','error':str(exc)[:700], 'attempted_at':int(time.time())})


def tick():
    # Follow existing governed handback registrations, without generating new client identities.
    config = json.loads((PROFILE / 'task-router.json').read_text())
    registered = json.loads(Path('/home/hermes/.hermes/profiles/lhm_brain/config/client-handback-targets.json').read_text())['clients']
    for key, value in registered.items():
        if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', key) and all(k in value for k in ['name', 'vault_prefix', 'drive_folder_query']):
            config['clients'][key] = value
    atomic(PROFILE / 'task-router.json', config)
    try:
        refresh_directory(VAULT, PROFILE, config['clients'])
    except Exception as exc:
        print(json.dumps({'client_directory': 'unavailable', 'reason': str(exc)}))
    for path in sorted((BASE / 'incoming').glob('*.json'))[:8]:
        request_id = path.stem
        if not ID.fullmatch(request_id):
            continue
        run = BASE / 'runs' / request_id
        run.mkdir(exist_ok=True, mode=0o750)
        os.chown(run, 0, 10000)
        if (run / 'receipt.json').exists():
            path.rename(BASE / 'processed' / path.name)
            continue
        try:
            request = json.loads(read(path, 32768))
            if request != verified(request_id):
                raise ValueError('Queued request differs from verified human contract')
            # Save a durable admission receipt BEFORE starting a provider. A restart never duplicates it.
            atomic(run / 'receipt.json', {'status': 'starting', 'provider': request['provider'], 'request_id': request_id,
                                         'started_at': int(time.time())})
            prepare(request)
        except Exception as exc:
            atomic(run / 'receipt.json', {'status': 'failed', 'error': str(exc)[:1200]})
        path.rename(BASE / 'processed' / path.name)
    for run in (BASE / 'runs').iterdir():
        if not run.is_dir() or not ID.fullmatch(run.name):
            continue
        receipt = json.loads(read(run / 'receipt.json'))
        if receipt['status'] in {'needs_review', 'failed'}:
            continue
        work = WORK / run.name
        provider_receipt = work / 'receipt.json'
        if provider_receipt.exists():
            current = json.loads(read(provider_receipt))
            if current.get('request_id') != run.name:
                current = {'status': 'failed', 'error': 'Provider receipt mismatch'}
            if (work / 'session.json').exists():
                current.update(json.loads(read(work / 'session.json')))
            if (work / 'result.md').exists():
                result = read(work / 'result.md', 200000)
                target = run / 'result.md'
                target.write_text(result)
                os.chown(target, 0, 10000)
                target.chmod(0o640)
            current['started_at'] = receipt.get('started_at', int(time.time()))
            atomic(run / 'receipt.json', current)
        age = time.time() - receipt.get('started_at', time.time())
        if age > 60:
            unit = subprocess.run(['systemctl', 'show', '--property=ActiveState', '--value', 'lhm-task-' + run.name], capture_output=True, text=True, timeout=10)
            if unit.stdout.strip() not in {'active', 'activating'} and (not provider_receipt.exists() or current.get('status') not in {'needs_review', 'failed'}):
                atomic(run / 'receipt.json', {'status': 'failed', 'error': 'Provider service stopped before a terminal receipt; inspect saved logs/session before retrying'})
                continue
        interactive_alive = (provider_receipt.exists() and current.get('transport') == 'claude-code-remote-control'
                             and current.get('status') == 'interactive'
                             and 0 <= time.time() - current.get('heartbeat_at', 0) < 60)
        from site_workspace import publication_active
        if age > 1400 and not interactive_alive and not publication_active(work):
            atomic(run / 'receipt.json', {'status': 'failed', 'error': 'Worker timed out or stopped; inspect its saved session before retrying'})
    delivery_tick()
    subprocess.run(['docker', 'exec', '--user', 'hermes', 'hermes', '/opt/hermes/.venv/bin/python',
        '/opt/data/profiles/lhm_chief_of_staff/task-router/server.py', '--reconcile'], timeout=90, check=True)


if __name__ == '__main__':
    WORK.mkdir(exist_ok=True, mode=0o755)
    WORK.chmod(0o755)
    with (WORK / 'dispatch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        tick()
