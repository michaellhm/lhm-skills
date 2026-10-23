"""Head-of-Production adapter to the shared registered Drive artefact publisher."""
import hashlib
import json
import os
import mimetypes
from pathlib import Path
import re
import stat
import time
import subprocess
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from drive_publisher import Drive, ROUTE, digest
from workspaces import location

ROOT = Path('/var/lib/lhm-drive-delivery')
CONFIG = Path('/etc/lhm-task-router/drive-delivery.json')
CAPS = Path('/home/hermes/.hermes/profiles/lhm_brain/vault-task-router/_System/Hermes/clients')
ID = re.compile(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*')


def read(path, limit=25000000):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Source must be an absolute bounded path')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory);directory = next_fd
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, 'rb') as f:
        info = os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit or info.st_nlink != 1:
            raise ValueError('Invalid linked/oversized delivery source')
        raw = f.read(limit + 1)
        if len(raw) > limit:
            raise ValueError('Delivery source grew beyond its byte limit')
        return raw


def save(path, value, mode=0o600):
    temp = path.with_name(path.name + '.next')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    if os.geteuid() == 0:
        os.chown(temp, 0, 10000 if mode == 0o640 else 0)
    temp.chmod(mode);temp.replace(path)


def manifest(request, run, queue_run):
    ident = request['request_id']
    if not ID.fullmatch(ident) or request['permission_ceiling'] != 'prepare_for_review':
        raise ValueError('Unsupported delivery contract')
    result = json.loads(read(run / 'receipt.json'))
    if result.get('status') != 'needs_review' or result.get('request_id') != ident or result.get('provider') != request['provider']:
        raise ValueError('Producer has not completed this exact request')
    work = run / 'workspace'
    if (run / 'workspace-location.json').exists():
        mapping = json.loads(read(run / 'workspace-location.json'))
        expected = location(request['provider'], request['client_id'])
        task = expected / 'tasks' / ident
        if mapping != {'workspace': str(expected), 'task_directory': str(task)}:
            raise ValueError('Drafts are outside the registered task workspace')
        work = task
    drafts = work / 'drafts'
    if drafts.is_symlink() or not drafts.is_dir():
        raise ValueError('Registered drafts are missing or linked')
    entries = []
    total = 0
    for base, dirs, files in os.walk(drafts, followlinks=False):
        if any((Path(base) / n).is_symlink() for n in dirs):
            raise ValueError('Linked output folders cannot be delivered')
        for name in sorted(files):
            path = Path(base) / name
            relative = path.relative_to(drafts)
            if any(p.startswith('.') or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._()&-]{0,119}', p) for p in relative.parts):
                raise ValueError('Hidden or unsafe output file requires explicit review')
            raw = read(path)
            if re.search(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|"(?:access_token|refresh_token|client_secret|private_key)"\s*:', raw):
                raise ValueError('Credential-like material cannot be delivered to a client folder')
            total += len(raw)
            if len(entries) >= 100 or total > 100000000:
                raise ValueError('Output package exceeds bounded delivery limits')
            entries.append({'relative': str(relative), 'size_bytes': len(raw), 'sha256': digest(raw), 'media_type': mimetypes.guess_type(str(relative))[0] or 'application/octet-stream'})
    entries.sort(key=lambda f: f['relative'])
    if not entries:
        return None
    declared = result.get('artifact_manifest')
    if declared is not None and sorted(declared, key=lambda f: f['relative']) != [{k: f[k] for k in ['relative','size_bytes','sha256']} for f in entries]:
        raise ValueError('Drafts changed after the producer manifest; no upload authorised')
    if declared is None:
        backfill = json.loads(read(queue_run / 'delivery-request.json')) if (queue_run / 'delivery-request.json').exists() else {}
        expected = [{k: f[k] for k in ['relative','size_bytes','sha256']} for f in entries]
        if backfill.get('files') != expected or backfill.get('request_id') != ident:
            raise ValueError('Legacy files need an explicit digest-bound delivery request')
    package = digest(json.dumps(entries, sort_keys=True).encode())
    ROOT.mkdir(parents=True, exist_ok=True);ROOT.chmod(0o700)
    stage = ROOT / ident
    stage.mkdir(exist_ok=True, mode=0o700);stage.chmod(0o700)
    target = stage / 'manifest.json'
    if target.exists():
        existing = json.loads(read(target))
        if existing['package_sha256'] != package:
            raise ValueError('Deliverable package changed; do not silently replace an existing delivery')
        return existing
    for entry in entries:
        dest = stage / 'sources' / entry['relative'];dest.parent.mkdir(parents=True, exist_ok=True)
        raw = read(drafts / entry['relative'])
        if digest(raw) != entry['sha256']:
            raise ValueError('Draft changed during producer QA snapshot')
        dest.write_bytes(raw);dest.chmod(0o600)
    started = json.loads(read(queue_run / 'receipt.json')).get('started_at', datetime.now(timezone.utc).timestamp())
    month = datetime.fromtimestamp(started, timezone.utc).astimezone(ZoneInfo('Australia/Melbourne')).strftime('%Y-%m')
    title = request['title'].casefold()
    service = 'google_ads' if 'google ads' in title else 'client_updates' if any(t in title for t in ['client comms', 'meeting', 'client update']) else 'run-hermes-task'
    result = {'parent_run_id': ident, 'child_run_id': ident + '-drive', 'client_id': request['client_id'],
              'producer_session': result.get('thread_id'), 'producer_receipt': str(run / 'receipt.json'),
              'qa_disposition': 'source_package_hash_verified', 'package_sha256': package,
              'permission_ceiling': 'internal_review_file_create_only', 'files': entries,
              'relative_folder': service + '/' + month + '/' + ident,
              'reviewer_id': request['reviewer_id'], 'return_point': request['task_url']}
    save(target, result)
    return result


def folder_for(request, drive):
    client = request['client']
    values = set(re.findall(r'(?:folders/|folder ID\s+)([A-Za-z0-9_-]{8,160})', client.get('drive_folder_query', '')))
    if not values:
        values = {url['url'].split('/folders/')[-1] for url in client.get('systems_links', []) if '/folders/' in url.get('url', '')}
    actual = {p.get('ID') for p in drive.children(drive.config['current_clients_id']) if p.get('IsDir')}
    matches = values & actual
    if len(matches) != 1:
        raise ValueError('client_onboarding_required: exact registered Current Clients folder unresolved')
    folder = matches.pop();drive.verify_client(folder)
    return folder


def knowledge(action, relative, source=None):
    args = ['/usr/local/bin/rclone', action]
    if source is not None:
        args.append(str(source))
    args += ['lhm-knowledge:' + relative, '--config', '/etc/lhm-obsidian-sync/rclone.conf', '--retries', '1']
    result = subprocess.run(args, capture_output=True, timeout=60)
    if result.returncode and not (action == 'cat' and result.returncode in {3, 4}):
        raise ValueError('Canonical capability record transport failed')
    return result.stdout if result.returncode == 0 else None


def capability(request, folder, drive, package, dest_folder):
    """Governed client onboarding: smoke one required artefact, retain exact evidence, verify registration."""
    client = request['client_id']
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', client):
        raise ValueError('Invalid capability identity')
    relative = '_System/Hermes/clients/' + client + '/capabilities.json'
    existing = knowledge('cat', relative)
    value = json.loads(existing) if existing else {'schema_version': 1, 'client': {'id': client, 'name': request['client']['name'], 'type': 'client'},
              'onboarding': {'status': 'incomplete', 'owner': 'lhm_client_onboarding'},
              'capabilities': {name: {'required': False, 'status': 'unconfigured', 'route': None, 'identifiers': {}, 'allowed_operations': [], 'owner': None, 'last_test': None}
                               for name in ['google_search_console','google_analytics','google_ads','website','google_drive','basicops','knowledge']}}
    if value.get('client', {}).get('id') != client:
        raise ValueError('Capability record belongs to another client')
    cap = value['capabilities'].get('google_drive', {})
    if cap.get('status') == 'verified':
        if cap.get('route') != ROUTE or cap.get('identifiers', {}).get('folder_id') != folder or not {'file_create','file_readback'} <= set(cap.get('allowed_operations', [])):
            raise ValueError('Verified Drive capability conflicts with the registered destination')
        test = cap.get('last_test') or {}
        evidence_path = Path(test.get('evidence_ref', '/missing-evidence'))
        if evidence_path.is_relative_to(ROOT) and evidence_path.is_file() and not evidence_path.is_symlink() and digest(read(evidence_path)) == test.get('evidence_sha256') and test.get('result') == 'passed':
            return
    if not drive.config.get('allow_client_onboarding'):
        raise ValueError('client_onboarding_required: Drive file create/readback not yet verified')
    # Onboarding smoke uses a real required artefact, not an unrelated test file.
    first = package['files'][0];nested = str(Path(first['relative']).parent)
    parent = drive.ensure_path(dest_folder, nested) if nested != '.' else dest_folder
    receipt = drive.publish(ROOT / request['request_id'] / 'sources' / first['relative'], Path(first['relative']).name,
                            parent, first['sha256'], first['size_bytes'], first['media_type'])
    evidence = ROOT / request['request_id'] / 'onboarding-evidence.json'
    save(evidence, {'client_id':client,'route':ROUTE,'client_folder_id':folder,'result':'passed','file':receipt})
    cap = {'required': True, 'status': 'verified', 'route': ROUTE,
           'identifiers': {'folder_id':folder,'folder_name':request['client']['name'],'current_clients_id':drive.config['current_clients_id']},
           'allowed_operations':['file_create','file_readback','scoped_folder_create'],'owner':'lhm_client_onboarding',
           'last_test':{'result':'passed','evidence_ref':str(evidence),'evidence_sha256':digest(evidence.read_bytes())}}
    value['capabilities']['google_drive'] = cap
    value['onboarding']['updated_at'] = datetime.now(timezone.utc).isoformat()
    target = CAPS / client / 'capabilities.json';target.parent.mkdir(parents=True, exist_ok=True)
    for directory in [CAPS.parent.parent, CAPS.parent, CAPS, target.parent]:
        os.chown(directory, 0, 10000);directory.chmod(0o750)
    save(target, value, 0o640)
    # Preserve unrelated capabilities and stop if the canonical record changed during the smoke.
    if knowledge('cat', relative) != existing:
        raise ValueError('Canonical capability record changed concurrently')
    knowledge('copyto', relative, target)
    if knowledge('cat', relative) != target.read_bytes():
        raise ValueError('Capability record readback mismatch')


def deliver(request, run, queue_run):
    package = manifest(request, run, queue_run)
    if package is None:
        result = {'artefact_state':'no_files_produced','reason':'No draft files were produced; no Drive delivery is claimed','files':[]}
        save(queue_run / 'delivery.json', result, 0o640);return result
    config = json.loads(read(CONFIG))
    drive = Drive(config)
    folder = folder_for(request, drive)
    destination = drive.ensure_path(folder, package['relative_folder'])
    capability(request, folder, drive, package, destination)
    target = queue_run / 'delivery.json'
    prior = json.loads(read(target)) if target.exists() else {}
    preserved = prior.get('files', []) if prior.get('package_sha256') == package['package_sha256'] and prior.get('folder_id') == destination else []
    result = {'artefact_state':'delivery_incomplete','route':ROUTE,'parent_run_id':request['request_id'],
              'client_folder_id':folder,'folder_id':destination,'folder_url':'https://drive.google.com/drive/folders/'+destination,
              'package_sha256':package['package_sha256'],'files':preserved,'attempted_at':int(time.time()),
              'reason':'Delivery is in progress; verified items are retained and only incomplete items are retried'}
    done = {f['relative']:f for f in preserved}
    started = time.monotonic()
    for entry in package['files']:
        item = done.get(entry['relative'])
        if item and item.get('sha256') == entry['sha256'] and item.get('size_bytes') == entry['size_bytes'] and item.get('readback_sha256') == entry['sha256'] and item.get('run_result') == 'passed':
            continue
        if time.monotonic() - started > 120:
            save(target,result,0o640);return result
        nested = str(Path(entry['relative']).parent)
        parent = drive.ensure_path(destination, nested) if nested != '.' else destination
        item = drive.publish(ROOT/request['request_id']/'sources'/entry['relative'], Path(entry['relative']).name,
                             parent, entry['sha256'],entry['size_bytes'],entry['media_type'])
        result['files'] = [f for f in result['files'] if f['relative'] != entry['relative']]
        result['files'].append({**item,'relative':entry['relative']});save(target,result,0o640)
    result['artefact_state']='delivered';save(target,result,0o640)
    return result
