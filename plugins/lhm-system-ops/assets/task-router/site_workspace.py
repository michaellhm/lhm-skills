#!/usr/bin/env python3
"""Host-managed website checkouts, GitHub App credentials and repository-wide leases."""
import argparse
import base64
from contextlib import contextmanager, nullcontext
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
import tempfile
import urllib.error
import urllib.request

CONFIG = Path('/etc/lhm-sites/config.json')
ROOT = Path('/var/lib/lhm-sites')
PROVIDERS = {'claude': (10002, 'claudeworker'), 'codex': (10001, 'codexworker')}
REPO = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*')
REQUEST = re.compile(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*')


def read_owned(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise ValueError('Host configuration must be a root-owned regular file without group/world write')
    return json.loads(path.read_text())


def config():
    return read_owned(CONFIG)


def site_for(request, settings=None):
    settings = settings if settings is not None else config()
    matches = [(key, row) for key, row in settings['sites'].items()
               if row['client_id'] == request['client_id']]
    if len(matches) != 1:
        raise ValueError('One registered website is required for this client')
    key, row = matches[0]
    if sum(value['repository'].casefold() == row['repository'].casefold() for value in settings['sites'].values()) != 1:
        raise ValueError('A repository can have only one registered site folder')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', key) or not REPO.fullmatch(row['repository']):
        raise ValueError('Invalid registered website identity')
    if row['mode'] not in {'build', 'live'} or row.get('default_branch') != 'main':
        raise ValueError('Explicit build/live mode and main branch are required')
    if row.get('deployment_verified') is not True or not row.get('authority_source'):
        raise ValueError('Publishing mode requires verified deployment mapping and human authority')
    return key, row


def atomic(path, value, mode=0o644):
    # Task directories are worker-writable: never follow a predictable temporary symlink as root.
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.' + path.name + '.', delete=False) as stream:
        temp = Path(stream.name)
        try:
            stream.write(json.dumps(value, indent=2) + '\n')
            stream.flush()
            os.fchmod(stream.fileno(), mode)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def lease(repository, owner, root=None):
    """Key by canonical GitHub repository, not provider/client alias. Never steal a live lock."""
    root = root or ROOT
    directory = root / '.locks'
    directory.mkdir(parents=True, exist_ok=True, mode=0o755)
    key = hashlib.sha256(repository.casefold().encode()).hexdigest()
    path = directory / (key + '.lock')
    if path.is_symlink():
        raise ValueError('Repository lease cannot be a symlink')
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Website busy: another worker owns this repository') from None
        atomic(directory / (key + '.json'), {**owner, 'repository': repository, 'pid': os.getpid(), 'status': 'active'})
        try:
            yield
        finally:
            atomic(directory / (key + '.json'), {**owner, 'repository': repository, 'status': 'released'})


def app_jwt(app):
    key = Path(app['private_key'])
    info = key.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
        raise ValueError('GitHub App key must be root-only')
    enc = lambda value: base64.urlsafe_b64encode(value).rstrip(b'=')
    now = int(time.time())
    head = enc(b'{"alg":"RS256","typ":"JWT"}')
    body = enc(json.dumps({'iat': now-60, 'exp': now+480, 'iss': str(app['client_id'])}).encode())
    signed = head + b'.' + body
    signature = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(key)], input=signed,
                               capture_output=True, check=True, timeout=10).stdout
    return (signed + b'.' + enc(signature)).decode()


def api(path, token, body=None):
    req = urllib.request.Request('https://api.github.com' + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                 'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'LHM-Hermes-Sites'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise ValueError('GitHub App request failed (HTTP ' + str(exc.code) + ')') from None


def installation_token(settings, row, write=False):
    app = settings['github_app']
    return api('/app/installations/' + str(int(app['installation_id'])) + '/access_tokens', app_jwt(app),
               {'repositories': [row['repository'].split('/')[1]],
                'permissions': {'contents': 'write' if write else 'read', 'metadata': 'read'}})['token']


def git(repo, args, provider, token=None, check=True):
    """Run repository-controlled Git configuration as the worker, never as root."""
    uid, user = PROVIDERS[provider]
    env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/' + user,
           'GIT_TERMINAL_PROMPT': '0', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
    options = ['-c', 'credential.helper=', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false']
    if token:
        auth = base64.b64encode(('x-access-token:' + token).encode()).decode()
        env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                   GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + auth)
    command = ['/usr/sbin/runuser', '-u', user, '--', 'git', *options]
    if repo is not None:
        command += ['-C', str(repo)]
    result = subprocess.run(command + args, env=env, text=True, capture_output=True, timeout=180)
    if check and result.returncode:
        raise ValueError('Git operation failed: ' + args[0] + ' (exit ' + str(result.returncode) + ')')
    return result


def ensure_checkout(settings, key, row, provider):
    folder = ROOT / key
    folder.mkdir(parents=True, exist_ok=True, mode=0o755)
    repo = folder / 'repo'
    uid = PROVIDERS[provider][0]
    if repo.is_symlink():
        raise ValueError('Website checkout cannot be a symlink')
    if repo.exists() and any(repo.iterdir()):
        # A previous stopped worker keeps its files. Only ownership changes, never reset/clean/stash.
        for base, dirs, files in os.walk(repo, followlinks=False):
            os.chown(base, uid, uid)
            for name in dirs + files:
                os.chown(Path(base) / name, uid, uid, follow_symlinks=False)
        if not (repo / '.git/HEAD').is_file():
            raise ValueError('Existing site folder is not a Git checkout; preserve it for review')
        url = git(repo, ['remote', 'get-url', 'origin'], provider).stdout.strip()
        if url != 'https://github.com/' + row['repository'] + '.git':
            raise ValueError('Repository remote does not match registered website')
        if git(repo, ['status', '--porcelain'], provider).stdout:
            raise ValueError('Website has uncommitted work; preserve and resume it before another task')
        git(repo, ['fetch', 'origin', 'main'], provider, installation_token(settings, row))
        if git(repo, ['rev-list', '--count', 'origin/main..HEAD'], provider).stdout.strip() != '0':
            raise ValueError('Unpublished commits exist; reconcile before updating')
        git(repo, ['checkout', 'main'], provider)
        git(repo, ['merge', '--ff-only', 'origin/main'], provider)
    else:
        repo.mkdir(mode=0o750, exist_ok=True); os.chown(repo, uid, uid)
        git(None, ['clone', '--branch', 'main', '--single-branch', 'https://github.com/' + row['repository'] + '.git', str(repo)],
            provider, installation_token(settings, row))
    return repo


def prepare(settings, request, provider):
    key, row = site_for(request, settings)
    repo = ensure_checkout(settings, key, row, provider)
    if row['mode'] == 'live':
        branch = 'task/' + request['request_id']
        git(repo, ['checkout', '-b', branch], provider)
    else:
        branch = 'main'
    git(repo, ['config', 'user.name', settings['commit_name']], provider)
    git(repo, ['config', 'user.email', settings['commit_email']], provider)
    return key, row, repo, branch


def validate_mapping(run, request):
    path = run / 'site-location.json'
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
        raise ValueError('Website mapping requires host-owned authority')
    value = json.loads(path.read_text())
    if (value['request_id'] != request['request_id'] or value['client_id'] != request['client_id']
            or value['instruction_sha256'] != request['instruction_sha256']
            or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', value['site_id'])
            or Path(value['repo']) != ROOT / value['site_id'] / 'repo'):
        raise ValueError('Website mapping identity mismatch')
    return value


def supervise(request_id):
    from dispatch import WORK, BASE, verified, read, launch
    if os.geteuid() != 0 or not REQUEST.fullmatch(request_id):
        raise ValueError('Host administrator and verified request ID required')
    request = verified(request_id)
    run = WORK / request_id
    if json.loads(read(run / 'request.json')) != request:
        raise ValueError('Saved task contract changed')
    settings = config()
    key, row = site_for(request, settings)
    with lease(row['repository'], {'request_id': request_id, 'provider': request['provider']}):
        key, row, repo, branch = prepare(settings, request, request['provider'])
        old = json.loads(read(run / 'workspace-location.json'))
        resume = read_owned(run / 'site-resume.json') if (run / 'site-resume.json').exists() else {}
        mapping = {'request_id': request_id, 'client_id': request['client_id'],
                   'instruction_sha256': request['instruction_sha256'], 'site_id': key,
                   'repo': str(repo), 'branch': branch, 'mode': row['mode'],
                   'authority_source': row['authority_source'], 'scope_note': row.get('scope_note', ''),
                   'task_directory': old['task_directory'],
                   'resume_thread_id': resume.get('thread_id'), 'lease_pid': os.getpid()}
        atomic(run / 'site-location.json', mapping)
        starting = {'status': 'starting', 'provider': request['provider'], 'request_id': request_id,
                    'started_at': int(time.time()), 'site_workspace': str(repo)}
        atomic(BASE / 'runs' / request_id / 'receipt.json', starting, 0o640)
        os.chown(BASE / 'runs' / request_id / 'receipt.json', 0, 10000)
        # Archive the old terminal receipt before restarting the same conversation.
        if (run / 'receipt.json').exists():
            atomic(run / 'pre-site-receipt.json', json.loads(read(run / 'receipt.json')), 0o600)
            (run / 'receipt.json').unlink()
        launch(request, run, repo)
        unit = 'lhm-task-' + request_id
        time.sleep(3)
        while True:
            result = subprocess.run(['systemctl', 'show', '--property=ActiveState', '--value', unit],
                                    capture_output=True, text=True, timeout=10)
            if result.stdout.strip() not in {'active', 'activating', 'deactivating', 'reloading'}:
                break
            process_publication_request(run, unit)
            time.sleep(5)


def check_site(site_id, request_id, *, _lease_held=False):
    from dispatch import WORK, verified
    if os.geteuid() != 0 or not REQUEST.fullmatch(request_id):
        raise ValueError('Host administrator and exact request required')
    settings = config()
    request = verified(request_id)
    if json.loads((WORK / request_id / 'request.json').read_text()) != request:
        raise ValueError('Saved task authority changed')
    key, row = site_for(request, settings)
    mapping = validate_mapping(WORK / request_id, request)
    if key != site_id:
        raise ValueError('Wrong website')
    provider, repo = request['provider'], Path(mapping['repo'])
    with (nullcontext() if _lease_held else lease(row['repository'], {'request_id': request_id, 'action': 'checks'})):
        if git(repo, ['status', '--porcelain'], provider).stdout:
            raise ValueError('Commit source changes before binding checks to a revision')
        sha = git(repo, ['rev-parse', 'HEAD'], provider).stdout.strip()
        commands = row.get('checks', [])
        if not commands or any(not isinstance(c, list) or not c or not all(isinstance(a, str) for a in c) for c in commands):
            raise ValueError('Registered check commands are required')
        evidence = ROOT / key / 'evidence'
        evidence.mkdir(exist_ok=True, mode=0o700)
        results = []
        user = PROVIDERS[provider][1]
        for index, command in enumerate(commands):
            with (evidence / (request_id + '-check-' + str(index) + '.log')).open('w') as log:
                result = subprocess.run(['/usr/sbin/runuser', '-u', user, '--', *command], cwd=repo,
                    env={'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': '/home/' + user, 'CI': 'true'},
                    stdout=log, stderr=subprocess.STDOUT, timeout=600)
            results.append({'command': command, 'exit_code': result.returncode})
            if result.returncode:
                break
        passed = all(r['exit_code'] == 0 for r in results) and len(results) == len(commands)
        passed = passed and git(repo, ['rev-parse', 'HEAD'], provider).stdout.strip() == sha and not git(repo, ['status', '--porcelain'], provider).stdout
        receipt = {'commit': sha, 'passed': bool(passed), 'request_id': request_id, 'checks': results}
        atomic(ROOT / key / 'checks.json', receipt)
        return receipt


def publish(site_id, request_id, message, *, _lease_held=False):
    """Host publishes with an exclusive lease and a stopped/frozen writer; mode controls the branch."""
    from dispatch import WORK, verified
    if os.geteuid() != 0 or not REQUEST.fullmatch(request_id):
        raise ValueError('Host administrator and exact request required')
    settings = config()
    request = verified(request_id)
    if json.loads((WORK / request_id / 'request.json').read_text()) != request:
        raise ValueError('Saved task authority changed')
    mapping = validate_mapping(WORK / request_id, request)
    key, row = site_for(request, settings)
    if key != site_id or mapping['mode'] != row['mode']:
        raise ValueError('Publishing mode or website changed; review required')
    with (nullcontext() if _lease_held else lease(row['repository'], {'request_id': request_id, 'provider': request['provider'], 'action': 'publish'})):
        repo, provider = Path(mapping['repo']), request['provider']
        expected = 'https://github.com/' + row['repository'] + '.git'
        if any(git(repo, args, provider).stdout.strip() != expected for args in [['remote','get-url','origin'], ['remote','get-url','--push','origin']]):
            raise ValueError('Publishing remote changed; review required')
        branch = git(repo, ['branch', '--show-current'], provider).stdout.strip()
        if branch != mapping['branch'] or (row['mode'] == 'live' and branch == 'main'):
            raise ValueError('Publishing branch differs from the authorised mode')
        git(repo, ['fetch', 'origin', 'main'], provider, installation_token(settings, row))
        if git(repo, ['merge-base', '--is-ancestor', 'origin/main', 'HEAD'], provider, check=False).returncode:
            raise ValueError('Remote main advanced; reconcile without force pushing')
        if git(repo, ['status', '--porcelain'], provider).stdout:
            raise ValueError('Commit reviewed changes and complete build checks before host publication')
        changed = git(repo, ['diff', '--name-only', 'origin/main', 'HEAD'], provider).stdout.splitlines()
        if any(name.startswith('.github/workflows/') or any(part == '.env' or part.startswith('.env.') for part in Path(name).parts) for name in changed):
            raise ValueError('Workflow or environment-file changes require a separate reviewed route')
        sha = git(repo, ['rev-parse', 'HEAD'], provider).stdout.strip()
        evidence = read_owned(ROOT / key / 'checks.json')
        if evidence.get('commit') != sha or evidence.get('passed') is not True:
            raise ValueError('Build/check evidence must match the exact commit')
        git(repo, ['push', 'origin', 'HEAD:refs/heads/' + branch], provider, installation_token(settings, row, True))
        remote = git(repo, ['ls-remote', 'origin', 'refs/heads/' + branch], provider, installation_token(settings, row)).stdout.split()[0]
        if remote != sha:
            raise ValueError('Remote commit readback mismatch')
        result = {'repository': row['repository'], 'branch': branch, 'commit': sha,
                  'url': 'https://github.com/' + row['repository'] + '/commit/' + sha,
                  'message': message, 'mode': row['mode']}
        atomic(ROOT / key / 'publication.json', result)
        return result


def read_publication_packet(path, request):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid not in {0, PROVIDERS[request['provider']][0]} or info.st_size > 4096:
            raise ValueError('Invalid publication request file')
        packet = json.load(stream)
    if (set(packet) != {'request_id', 'commit', 'nonce'} or packet['request_id'] != request['request_id']
            or not re.fullmatch(r'[0-9a-f]{40}', str(packet['commit']))
            or not re.fullmatch(r'[A-Za-z0-9-]{8,80}', str(packet['nonce']))):
        raise ValueError('Publication request must name only this task, exact commit and unique nonce')
    return packet


def process_publication_request(run, unit):
    """The owning site supervisor borrows its own lease while freezing its writer."""
    request = json.loads((run / 'request.json').read_text())
    mapping = validate_mapping(run, request)
    path = Path(mapping['task_directory']) / 'publish-request.json'
    if not path.exists():
        return
    target = run / 'site-publication.json'
    frozen = False
    result = {'status': 'failed', 'request_id': request['request_id']}
    try:
        packet = read_publication_packet(path, request)
        fingerprint = hashlib.sha256(json.dumps(packet, sort_keys=True).encode()).hexdigest()
        prior = read_owned(target) if target.exists() else {}
        if prior.get('fingerprint') == fingerprint or (prior.get('status') == 'published' and prior.get('commit') == packet['commit']):
            return
        result.update(commit=packet['commit'], fingerprint=fingerprint)
        subprocess.run(['systemctl', 'freeze', unit], check=True, capture_output=True, timeout=15)
        frozen = True
        if git(Path(mapping['repo']), ['rev-parse', 'HEAD'], request['provider']).stdout.strip() != packet['commit']:
            raise ValueError('Requested commit differs from current HEAD')
        checks = check_site(mapping['site_id'], request['request_id'], _lease_held=True)
        if checks.get('passed') is not True:
            raise ValueError('Registered website checks failed; inspect host check evidence')
        published = publish(mapping['site_id'], request['request_id'], 'Provider requested host publication after scoped website changes', _lease_held=True)
        result.update(published, status='published', checks=checks, published_at=int(time.time()))
    except Exception as exc:
        result['error'] = str(exc)[:700]
    finally:
        if frozen:
            try:
                thaw = subprocess.run(['systemctl', 'thaw', unit], capture_output=True, timeout=15)
                if thaw.returncode:
                    raise ValueError('Thaw failed')
            except (subprocess.SubprocessError, ValueError):
                result['worker_thaw_error'] = 'Host must thaw the paused worker; do not replay publication'
    atomic(target, result)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['run', 'check', 'publish'])
    parser.add_argument('request_id')
    parser.add_argument('--site')
    parser.add_argument('--message', default='Reviewed website changes')
    args = parser.parse_args()
    if args.action == 'run':
        try:
            supervise(args.request_id)
        except Exception as exc:
            from dispatch import BASE
            receipt = BASE / 'runs' / args.request_id / 'receipt.json'
            if REQUEST.fullmatch(args.request_id) and receipt.parent.is_dir():
                atomic(receipt, {'status': 'failed', 'error': str(exc)[:700]}, 0o640)
                os.chown(receipt, 0, 10000)
            raise
    elif args.action == 'check':
        print(json.dumps(check_site(args.site, args.request_id)))
    else:
        print(json.dumps(publish(args.site, args.request_id, args.message)))
