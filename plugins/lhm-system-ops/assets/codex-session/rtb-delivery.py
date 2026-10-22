#!/usr/bin/env python3
"""Pinned RTB review delivery. Uses rclone's normal OAuth connection, never credential files."""
from pathlib import Path
import hashlib
import html
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import subprocess

PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
QUEUE = Path('/home/hermes/.hermes/profiles/lhm_brain/dispatch/codex-pilot')
WORK = Path('/home/codexworker/clients/raise-the-bar')
STATE = Path('/var/lib/lhm-rtb-codex')
FOLDER = '1VWZkidj1x869sKc2zBxo8IrSb37w337H'
REMOTE = 'lhm-rtb:'
EDITABLE = {'prototype/rtb/homepage/index.html', 'prototype/rtb/homepage/assets/css/style.css',
            'prototype/rtb/homepage/assets/js/main.js'}
DRAFTS = {'drafts/handbook-review.md', 'drafts/reply-draft.md', 'drafts/feedback-checklist.md'}

def digest(content):
    return hashlib.sha256(content).hexdigest()

def command(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, **kwargs).stdout

def artifact_files(receipt, workspace=WORK):
    artifacts = receipt.get('artifacts', {})
    if not DRAFTS <= artifacts.keys() or not set(artifacts) <= DRAFTS | EDITABLE:
        raise ValueError('Invalid RTB artifact allowlist')
    result = {}
    for name, expected in artifacts.items():
        path = workspace / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Missing or linked RTB artifact')
        raw = path.read_bytes()
        if len(raw) > 200000 or digest(raw) != expected:
            raise ValueError('RTB artifact changed after worker verification')
        result[name] = raw
    return result

def drive_file(path, file_name, runner=command):
    if not re.fullmatch(r'rtb-2212824-v[1-9][0-9]*-[a-z-]+\.md', file_name):
        raise ValueError('Unregistered Drive review file name')
    args = ['--drive-root-folder-id', FOLDER, '--retries', '1', '--low-level-retries', '1']
    # --immutable refuses a differing existing object; normal retries reuse identical files.
    runner(['rclone', 'copyto', str(path), REMOTE + file_name, '--immutable', *args])
    readback = runner(['rclone', 'cat', REMOTE + file_name, *args])
    if readback != path.read_bytes():
        raise ValueError('Drive full-content readback mismatch')
    metadata = json.loads(runner(['rclone', 'lsjson', REMOTE + file_name, '--stat', *args]))
    file_id = metadata.get('ID', '')
    if metadata.get('Name') != file_name or not re.fullmatch(r'[A-Za-z0-9_-]+', file_id):
        raise ValueError('Drive file identity readback mismatch')
    return {'name': file_name, 'url': 'https://drive.google.com/file/d/' + file_id + '/view',
            'file_id': file_id, 'folder_id': FOLDER, 'sha256': digest(readback)}

def publisher():
    loader = importlib.machinery.SourceFileLoader('registered_prototype', '/usr/local/libexec/lhm-prototype-publisher')
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

def source_branch(request_id, manifest, files):
    if not re.fullmatch(r'ted-codex-2212824-v[1-9][0-9]*', request_id):
        raise ValueError('Invalid RTB request identity')
    pub = publisher()
    branch = 'codex/rtb-' + request_id.removeprefix('ted-codex-')
    checkout = STATE / request_id / 'repository'
    def git(*args):
        return command(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(checkout), *args], text=True).strip()
    if not checkout.exists():
        command(['git', 'clone', '--shared', '--no-checkout', str(pub.CHECKOUT), str(checkout)])
        git('checkout', '-b', branch, manifest['base_commit'])
        for relative, raw in files.items():
            if relative not in EDITABLE:
                continue
            name = relative.removeprefix('prototype/')
            if pub.SENSITIVE.search(raw):
                raise ValueError('Sensitive content in proposed prototype source')
            (checkout / name).write_bytes(raw)
        git('add', '--', 'rtb/homepage/index.html', 'rtb/homepage/assets/css/style.css', 'rtb/homepage/assets/js/main.js')
        changed = set(git('diff', '--cached', '--name-only').splitlines())
        allowed = {name.removeprefix('prototype/') for name in EDITABLE}
        if not changed or not changed <= allowed:
            raise ValueError('Prototype branch has no change or escapes RTB scope')
        git('-c', 'user.name=Codex RTB worker', '-c', 'user.email=codex@localhealthmarketing.com.au',
            'commit', '-m', 'RTB: prepare approved handbook feedback prototype revisions')
    # Recheck immutable file hashes before any push, including resumed delivery.
    for relative, raw in files.items():
        if relative in EDITABLE and (checkout / relative.removeprefix('prototype/')).read_bytes() != raw:
            raise ValueError('Prepared source branch differs from approved artifacts')
    commit = git('rev-parse', 'HEAD')
    env = pub.ssh_env()
    old = command(['git', 'ls-remote', pub.REMOTE, 'refs/heads/' + branch], text=True, env=env).strip()
    if old and old.split()[0] != commit:
        raise ValueError('Review branch already differs; refuse overwrite')
    if not old:
        command(['git', '-C', str(checkout), 'push', pub.REMOTE, 'HEAD:refs/heads/' + branch], env=env)
    remote = command(['git', 'ls-remote', pub.REMOTE, 'refs/heads/' + branch], text=True, env=env).split()[0]
    if remote != commit:
        raise ValueError('Review branch remote verification failed')
    return {'name': 'RTB prototype review branch', 'url': 'https://github.com/michaellhm/lhm-prototype/tree/' + branch,
            'commit': commit, 'branch': branch, 'published_shared_site': False}

def check_approval(request):
    # Fresh normal TED connector read. Never access its authentication storage here.
    script = '''import json,sys,hashlib
sys.path.insert(0,'/opt/data/profiles/lhm_chief_of_staff')
from codex_sessions_mcp import Bridge
r=json.load(sys.stdin);b=Bridge();c=b.approved_contract(2212824,r['basicops']['plan_message_id'],r['basicops']['approval_message_id'])
assert hashlib.sha256(c[2]['message'].encode()).hexdigest()==r['basicops']['plan_sha256']
assert hashlib.sha256(c[3]['message'].encode()).hexdigest()==r['basicops']['approval_sha256']
assert c[5]==r['objective']
print('approved')'''
    checked = command(['docker', 'exec', '-i', '--user', 'hermes', 'hermes', '/opt/hermes/.venv/bin/python', '-c', script],
                      input=json.dumps(request).encode())
    if checked.strip() != b'approved':
        raise ValueError('Fresh RTB approval check failed')

def main():
    mapping = PROFILE / 'codex-session-state/2212824.json'
    if not mapping.exists():
        return
    request = json.loads(mapping.read_text())['request']
    request_id = request['request_id']
    if not re.fullmatch(r'ted-codex-2212824-v[1-9][0-9]*', request_id):
        raise ValueError('Unregistered RTB request')
    receipt_path = QUEUE / 'runs' / request_id / 'receipt.json'
    if not receipt_path.exists():
        return
    receipt = json.loads(receipt_path.read_text())
    if receipt.get('status') != 'needs_review' or receipt.get('basicops') != request['basicops']:
        return
    target = PROFILE / 'codex-session-deliveries' / (request_id + '.json')
    if target.exists():
        return
    check_approval(request)
    files = artifact_files(receipt)
    run = STATE / request_id
    run.mkdir(parents=True, exist_ok=True, mode=0o700)
    output = {'basicops': request['basicops'], 'artifacts': receipt['artifacts'], 'verification': 'pending'}
    try:
        # Require a working normal Drive connection before creating a Git review branch.
        command(['rclone', 'lsf', REMOTE, '--drive-root-folder-id', FOLDER, '--max-depth', '1', '--retries', '1'])
        deliverables = []
        for name in sorted(DRAFTS):
            path = run / Path(name).name
            path.write_bytes(files[name])
            deliverables.append(drive_file(path, 'rtb-2212824-v' + str(request['basicops']['plan_version']) + '-' + Path(name).name))
        deliverables.append(source_branch(request_id, json.loads((WORK / 'task-context.json').read_text()), files))
        output.update(verification='passed', deliverables=deliverables)
    except Exception:
        output.update(verification='failed', error='RTB review delivery failed; inspect the host adapter before retrying. No shared-site publication or client email was attempted.')
    target.parent.mkdir(exist_ok=True)
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(output, indent=2) + '\n')
    os.chown(temporary, 0, 10000)
    temporary.chmod(0o640)
    temporary.replace(target)
    print(json.dumps({'request_id': request_id, 'verification': output['verification']}))

if __name__ == '__main__':
    main()
