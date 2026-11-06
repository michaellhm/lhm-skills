"""Prepare/apply one bounded immutable prototype-feedback runtime release.

No timer installation/activation, gateway restart, worker interruption, credential
changes, queue migration or authority-registry replacement is performed.
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import sqlite3
import stat
import tarfile
import uuid
from datetime import datetime, timezone
from email.utils import parseaddr
from pathlib import Path, PurePosixPath

PREFIX = 'plugins/lhm-project-hub/skills/prototype-feedback-loop/'
SCRIPTS = ('adapters.py', 'feedback_queue.py', 'workspace_gmail.py', 'intake_scan.py',
           'host_runtime.py', 'completion_runtime.py', 'poll_runtime.py', 'visual_qa.mjs', 'install_runtime.py')
ASSETS = {PREFIX + 'scripts/' + name: 'scripts/' + name for name in SCRIPTS}
ASSETS.update({PREFIX + 'SKILL.md': 'SKILL.md',
              PREFIX + 'agents/openai.yaml': 'agents/openai.yaml',
              PREFIX + 'references/integration.md': 'references/integration.md',
              PREFIX + 'references/host-runtime.md': 'references/host-runtime.md',
              PREFIX + 'assets/systemd/lhm-prototype-feedback.service': 'systemd/lhm-prototype-feedback.service',
              PREFIX + 'assets/systemd/lhm-prototype-feedback.timer': 'systemd/lhm-prototype-feedback.timer'})
SYSTEM = 'plugins/lhm-system-ops/'
EXTERNAL = {
    SYSTEM + 'assets/task-router/router.py': '/home/hermes/.hermes/profiles/lhm_chief_of_staff/task-router/router.py',
    SYSTEM + 'assets/task-router/github_deployment.py': '/usr/local/libexec/lhm-task-router/github_deployment.py',
    SYSTEM + 'assets/task-router/correction_worker.py': '/usr/local/libexec/lhm-task-router/correction_worker.py',
    SYSTEM + 'assets/task-router/dispatch.py': '/usr/local/libexec/lhm-task-router/dispatch.py',
    SYSTEM + 'assets/task-router/delivery.py': '/usr/local/libexec/lhm-task-router/delivery.py',
    SYSTEM + 'assets/host/lhm-prototype-publisher': '/usr/local/libexec/lhm-prototype-publisher',
}
ASSETS.update({source: 'host/' + Path(target).name for source, target in EXTERNAL.items()})
PROFILE_FILES = {
    '/home/hermes/.hermes/profiles/' + profile + '/skills/prototype-feedback-loop/' + relative: PREFIX + relative
    for profile in ('lhm_brain', 'lhm_chief_of_staff')
    for relative in ('SKILL.md', 'references/integration.md', 'references/host-runtime.md', 'agents/openai.yaml')
}
INSTALL = Path('/opt/lhm-prototype-feedback')
CURRENT = INSTALL / 'current'
COMPAT = Path('/usr/local/libexec/lhm-prototype-feedback')
CODEX_SKILL = Path('/home/codexworker/.agents/skills/lhm-project-hub--prototype-feedback-loop')
CONFIG = Path('/etc/lhm-prototype-feedback/sites.json')
STATE = Path('/var/lib/lhm-prototype-feedback')
QA_ROOT = STATE / 'qa-runs'
DISPATCH_LOCK = Path('/var/lib/lhm-task-router/dispatch.lock')
SITE_FIELDS = {'enabled', 'account', 'senders', 'threads', 'review_start', 'cockpit_id', 'stage_id',
               'client_id', 'client_label', 'canonical_note', 'work_folder_url', 'repository',
               'subtree', 'preview_url', 'reviewer_id', 'worker_root'}
MAX_ARCHIVE = 100 * 1024 * 1024


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_file(path, *, private=False, root=False, maximum=2 * 1024 * 1024):
    path = Path(path)
    directory = directory_fd(path.parent)
    try:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum
                or private and info.st_mode & 0o077 or root and (info.st_uid != 0 or info.st_mode & 0o022)):
            raise ValueError('unsafe install input or existing destination')
        data = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(data) != info.st_size or (info.st_size, info.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('install source changed during read')
        return data


def directory_fd(path, *, create=False, mode=0o755):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute no-follow install path required')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            created = False
            if create:
                try:
                    os.mkdir(component, mode=mode, dir_fd=directory)
                    created = True
                except FileExistsError: pass
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            if created:
                os.fchown(child, 0, 0)
                os.fchmod(child, mode)  # Restore exact requested mode despite operator UMask.
            os.close(directory);directory = child
        return directory
    except BaseException:
        os.close(directory)
        raise


def protected(path, *, mode=0o755):
    fd = directory_fd(path, create=True, mode=mode)
    try:
        info = os.fstat(fd)
        if (info.st_uid != 0 or info.st_mode & 0o022 or mode == 0o700 and info.st_mode & 0o077
                or mode != 0o700 and info.st_mode & (mode & 0o055) != mode & 0o055):
            raise ValueError('install directory is not root protected')
    finally: os.close(fd)


def atomic(path, data, *, mode=0o644):
    path = Path(path);directory = directory_fd(path.parent)
    temporary = '.' + path.name + '.' + uuid.uuid4().hex + '.next'
    try:
        info = os.fstat(directory)
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('unsafe install destination parent')
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=directory)
        with os.fdopen(fd, 'wb') as stream:
            os.fchown(stream.fileno(), 0, 0);os.fchmod(stream.fileno(), mode)
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
    finally:
        try: os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError: pass
        os.close(directory)


def link(path, target):
    path = Path(path);directory = directory_fd(path.parent)
    temporary = '.' + path.name + '.' + uuid.uuid4().hex + '.next'
    try:
        os.symlink(target, temporary, dir_fd=directory)
        os.replace(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
    finally:
        try: os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError: pass
        os.close(directory)


def archive_payload(path, commit, expected):
    if not re.fullmatch(r'[a-f0-9]{40}', commit) or not re.fullmatch(r'[a-f0-9]{64}', expected):
        raise ValueError('exact source commit and archive SHA-256 required')
    raw = read_file(path, maximum=MAX_ARCHIVE)
    if digest(raw) != expected:
        raise ValueError('archive SHA-256 differs from reviewed source')
    import io
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as source:
        if source.pax_headers.get('comment') != commit:
            raise ValueError('archive is not bound to the expected git-archive commit')
        for member in source:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts:
                raise ValueError('unsafe archive path')
            if member.name not in ASSETS:
                continue
            if not member.isfile() or member.name in payload or not 0 < member.size <= 2 * 1024 * 1024:
                raise ValueError('selected install asset is linked, duplicate or oversized')
            stream = source.extractfile(member)
            data = stream.read(2 * 1024 * 1024 + 1)
            if len(data) != member.size:
                raise ValueError('selected asset truncated')
            payload[member.name] = data
    if set(payload) != set(ASSETS):
        raise ValueError('committed archive is missing explicit runtime assets')
    return payload


def registration_payload(path):
    raw = read_file(path, private=True)
    value = json.loads(raw)
    if set(value) != {'schema_version', 'sites'} or value['schema_version'] != 1 or set(value['sites']) != {'luminary-counselling'}:
        raise ValueError('closed pilot registration required')
    row = value['sites']['luminary-counselling']
    if (not isinstance(row, dict) or set(row) != SITE_FIELDS or row['enabled'] is not True
            or row['stage_id'] != 110340 or row['reviewer_id'] != 36398 or type(row['cockpit_id']) is not int or row['cockpit_id'] <= 0
            or row['repository'] != 'michaellhm/lhm-prototype' or row['subtree'] != 'luminary-counselling/'
            or row['preview_url'] != 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/'):
        raise ValueError('registration differs from approved pilot scope')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row['client_id']) or row['worker_root'] != '/var/lib/lhm-client-workspaces/codex/' + row['client_id']:
        raise ValueError('unregistered worker-root mapping')
    if not row['senders'] or not row['threads'] or any(not re.fullmatch(r'[a-f0-9]{8,64}', item) for item in row['threads']):
        raise ValueError('exact sender/thread mappings required')
    if any(parseaddr(item)[1] != item or '@' not in item or item != item.lower() for item in [row['account'], *row['senders']]):
        raise ValueError('exact account and sender addresses required')
    if datetime.fromisoformat(row['review_start']).tzinfo is None:
        raise ValueError('review-window timezone required')
    if not re.fullmatch(r'https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]{8,160}', row['work_folder_url']):
        raise ValueError('verified work folder required')
    note = PurePosixPath(row['canonical_note'])
    if note.is_absolute() or '..' in note.parts or not str(note).startswith('20 Clients/') or note.suffix != '.md':
        raise ValueError('canonical shared client note required')
    return canonical(value)


def current_state():
    targets = {}
    for target in [*EXTERNAL.values(), *PROFILE_FILES, str(CONFIG)]:
        path = Path(target)
        if path.exists() or path.is_symlink():
            data = read_file(path, root=True)
            info = path.lstat()
            targets[target] = {'sha256': digest(data), 'mode': stat.S_IMODE(info.st_mode)}
        else: targets[target] = None
    links = {}
    for path in (CURRENT, COMPAT, CODEX_SKILL):
        if path.is_symlink(): links[str(path)] = os.readlink(path)
        elif path.exists(): raise ValueError('existing component path is not a managed symlink; prepare a scoped migration')
        else: links[str(path)] = None
    return {'schema_version': 1, 'targets': targets, 'links': links}


def qa_root_info():
    if not QA_ROOT.exists() and not QA_ROOT.is_symlink(): return None
    fd = directory_fd(QA_ROOT)
    try:
        info = os.fstat(fd)
        if info.st_uid != 0 or info.st_gid != 10001 or stat.S_IMODE(info.st_mode) != 0o750:
            raise ValueError('QA root needs explicit nonrecursive root:10001 mode0750 reconciliation before installation')
        return {'uid': 0, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}
    finally: os.close(fd)


def apply(commit, payload, config, baseline):
    if os.geteuid() != 0:
        raise ValueError('scoped installation requires the existing root operator')
    if baseline != current_state():
        raise ValueError('live baseline changed; preserve independent repairs and recapture')
    qa_before = qa_root_info()
    if payload[PREFIX + 'scripts/install_runtime.py'] != Path(__file__).read_bytes():
        raise ValueError('running installer differs from the committed archive')
    protected(INSTALL);protected(INSTALL/'releases')
    protected(STATE);protected(STATE/'state', mode=0o700)
    if qa_before is None:
        protected(QA_ROOT, mode=0o750)
        fd = directory_fd(QA_ROOT)
        try: os.fchown(fd, 0, 10001)
        finally: os.close(fd)
    qa_root_info()
    handles = []
    try:
        for path in (INSTALL/'.install.lock', STATE/'poll.lock', STATE/'runner.lock', STATE/'scan.lock', QA_ROOT/'.coordinator.lock', DISPATCH_LOCK):
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600);handles.append(fd)
            info = os.fstat(fd)
            if info.st_uid != 0 or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022 or info.st_nlink != 1:
                raise ValueError('install coordination lock is not a protected root file')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if baseline != current_state():
            raise ValueError('live source changed while acquiring install locks')
        release = INSTALL/'releases'/commit
        protected(release)
        manifest = {}
        for source, relative in ASSETS.items():
            target = release/relative
            protected(target.parent)
            if target.exists():
                if read_file(target, root=True) != payload[source]: raise ValueError('immutable release path already contains different bytes')
                if target.stat().st_mode & 0o044 != 0o044: raise ValueError('immutable release asset is unreadable; explicit scoped reconciliation required')
            else: atomic(target, payload[source])
            manifest[relative] = digest(payload[source])
        receipt = {'schema_version': 1, 'commit': commit, 'files': manifest, 'registration_sha256': digest(config),
                   'previous': baseline, 'timer_installed': False, 'timer_enabled': False,
                   'gateway_restarted': False, 'workers_interrupted': False}
        if (release/'release.json').exists():
            existing = json.loads(read_file(release/'release.json', root=True))
            if existing.get('files') != manifest or existing.get('registration_sha256') != digest(config):
                raise ValueError('existing immutable release receipt differs')
        else: atomic(release/'release.json', canonical(receipt))
        backup = STATE/'backups'/('runtime-' + commit + '-' + uuid.uuid4().hex[:8])
        protected(backup, mode=0o700)
        atomic(backup/'before.json', canonical(baseline), mode=0o600)
        atomic(backup/'qa-root-before.json', canonical({'prior': qa_before, 'current': qa_root_info()}), mode=0o600)
        backup_index = {}
        for index, (target, prior) in enumerate(sorted(baseline['targets'].items())):
            if prior is not None:
                name = 'target-' + str(index)
                atomic(backup/name, read_file(target, root=True), mode=0o600)
                backup_index[target] = {'file': name, **prior}
            else: backup_index[target] = None
        atomic(backup/'target-index.json', canonical(backup_index), mode=0o600)
        queue = STATE/'state/queue.sqlite'
        if queue.exists():
            import urllib.parse
            with sqlite3.connect('file:' + urllib.parse.quote(str(queue), safe='/') + '?mode=ro', uri=True) as source, sqlite3.connect(backup/'queue.snapshot.sqlite') as destination:
                source.backup(destination)
            (backup/'queue.snapshot.sqlite').chmod(0o600)
        # Only the explicit helper files change; the router/profile installer is never invoked.
        for source, target in EXTERNAL.items():
            protected(Path(target).parent)
            atomic(target, payload[source], mode=0o755)
        for target, source in PROFILE_FILES.items():
            protected(Path(target).parent)
            atomic(target, payload[source])
        protected(CONFIG.parent)
        atomic(CONFIG, config, mode=0o600)
        for source, target in EXTERNAL.items():
            if read_file(target, root=True) != payload[source]: raise RuntimeError('scoped helper readback failed; use recorded backup')
        for target, source in PROFILE_FILES.items():
            if read_file(target, root=True) != payload[source]: raise RuntimeError('scoped skill-document readback failed')
        if read_file(CONFIG, private=True, root=True) != config: raise RuntimeError('registration readback failed')
        link(CURRENT, 'releases/' + commit)
        protected(COMPAT.parent)
        link(COMPAT, str(CURRENT/'scripts'))
        protected(CODEX_SKILL.parent)
        link(CODEX_SKILL, str(CURRENT))
        if (os.readlink(CURRENT) != 'releases/' + commit or os.readlink(COMPAT) != str(CURRENT/'scripts')
                or os.readlink(CODEX_SKILL) != str(CURRENT)):
            raise RuntimeError('release projection readback failed')
        receipt['backup'] = str(backup)
        atomic(backup/'installed.json', canonical(receipt), mode=0o600)
        return {'state': 'installed-not-activated', 'commit': commit, 'backup': str(backup),
                'release': str(release), 'timer_installed': False, 'timer_enabled': False}
    finally:
        for fd in reversed(handles): os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-baseline', metavar='PRIVATE_JSON')
    parser.add_argument('--archive');parser.add_argument('--commit');parser.add_argument('--archive-sha256')
    parser.add_argument('--registration');parser.add_argument('--baseline');parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.capture_baseline:
        if os.geteuid() != 0: raise ValueError('baseline capture requires the existing root operator')
        atomic(args.capture_baseline, canonical(current_state()), mode=0o600)
        print(json.dumps({'state': 'baseline-prepared'}));return
    if not all((args.archive, args.commit, args.archive_sha256, args.registration)):
        parser.error('archive, commit, archive SHA-256 and private registration are required')
    payload = archive_payload(args.archive, args.commit, args.archive_sha256)
    config = registration_payload(args.registration)
    if args.apply:
        if not args.baseline: parser.error('exact private live baseline is required for apply')
        baseline = json.loads(read_file(args.baseline, private=True, root=True))
        result = apply(args.commit, payload, config, baseline)
    else:
        result = {'state': 'prepared', 'commit': args.commit, 'assets': len(payload),
                  'registration_sha256': digest(config), 'timer_installed': False, 'timer_enabled': False}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__': main()
