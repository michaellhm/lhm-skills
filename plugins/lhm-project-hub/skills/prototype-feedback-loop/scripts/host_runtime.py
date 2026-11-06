"""Root host coordinator for registered prototype feedback intake and Ted dispatch.

Consumes root-promoted extraction evidence; it does not replace the Gmail scanner,
worker, publisher, existing completion observer or desktop notification service.
No shell strings, client emails, credentials or human impersonation are used.
"""
import argparse
import fcntl
import hashlib
import html
import importlib.util
import io
import json
import os
import re
import stat
import subprocess
import tarfile
import uuid
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path, PurePosixPath
from importlib.machinery import SourceFileLoader
from urllib.parse import quote, urlsplit

from adapters import BasicOps, Effects, ReconcileRequired, pages
from feedback_queue import Queue

REGISTRATION = Path('/etc/lhm-prototype-feedback/sites.json')
STATE_ROOT = Path('/var/lib/lhm-prototype-feedback')
AUTHORITY = Path('/opt/lhm-plugin-releases/prototype-feedback-authority/authority.json')
WORKSPACES = Path('/var/lib/lhm-client-workspaces/codex')
TED = 82491
REVIEWER = 36398
STAGE = 110340
REPOSITORY = 'michaellhm/lhm-prototype'
SUBTREE = 'luminary-counselling/'
SITE_FIELDS = {'enabled', 'account', 'senders', 'threads', 'review_start', 'cockpit_id',
               'stage_id', 'client_id', 'client_label', 'canonical_note', 'work_folder_url',
               'repository', 'subtree', 'preview_url', 'reviewer_id', 'worker_root'}
PACKET_FIELDS = {'account', 'message_id', 'thread_id', 'site', 'cockpit_id', 'sender',
                 'received_at', 'source_url', 'original_text', 'items', 'images'}
EVIDENCE_FIELDS = {'account', 'message_id', 'thread_id', 'raw_path', 'raw_sha256',
                   'packet_sha256', 'extraction_receipt_path', 'extraction_receipt_sha256'}
EXTRACTION_FIELDS = {'schema_version', 'status', 'account', 'message_id', 'thread_id',
                     'raw_sha256', 'packet_sha256', 'reviewer', 'attachment_count', 'related_thread'}
BASICOPS_READ = frozenset(('get_current_user', 'get_task', 'list_tasks_in_project', 'list_messages_in_task'))
BASICOPS_WRITE = frozenset(('create_task', 'create_message_in_task', 'bulk_create_or_update_task', 'request_review'))
MAX_JSON = 512000
MAX_RAW = 10 * 1024 * 1024
MAX_SOURCE = 100 * 1024 * 1024
PUBLISHER = Path('/usr/local/libexec/lhm-prototype-publisher')
SOURCE_STORE = Path('/srv/lhm-prototype-publisher/feedback-source.git')
SOURCE_SUBTREE = 'luminary-counselling/homepage/'
STATIC = frozenset(('.html', '.css', '.js', '.json', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico', '.avif', '.woff', '.woff2', '.ttf', '.otf'))

# Input is JSON on stdin. This code and every executable/path are constant.
TED_SCRIPT = r'''
import importlib.util,json,sys
from pathlib import Path
PROFILE=Path('/opt/data/profiles/lhm_chief_of_staff')
p=json.load(sys.stdin)
if set(p)!={'kind','action','arguments'}: raise ValueError('closed bridge request required')
if p['kind']=='basicops':
 if p['action'] not in {'get_current_user','get_task','list_tasks_in_project','list_messages_in_task','create_task','create_message_in_task','bulk_create_or_update_task','request_review'}: raise ValueError('unsupported BasicOps action')
 spec=importlib.util.spec_from_file_location('feedback_ted_bridge',PROFILE/'codex_sessions_mcp.py')
 bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
 result=bridge.basicops(p['action'],p['arguments'])
elif p['kind']=='router':
 if p['action'] not in {'submit','status'}: raise ValueError('unsupported router action')
 sys.path.insert(0,str(PROFILE/'task-router'))
 spec=importlib.util.spec_from_file_location('feedback_existing_server',PROFILE/'task-router/server.py')
 server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
 result=getattr(server.instance(),p['action'])(**p['arguments'])
else: raise ValueError('unsupported bridge kind')
print(json.dumps(result,sort_keys=True))
'''
DOCKER = ['/usr/bin/docker', 'exec', '-i', '--user', 'hermes', 'hermes',
          '/opt/hermes/.venv/bin/python', '-c', TED_SCRIPT]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def actor(value):
    user = value.get('user', value.get('userId', value.get('assignee')))
    return user.get('id') if isinstance(user, dict) else user


def root_bytes(path, *, private=False, maximum=MAX_JSON, readable_group=None):
    """Bounded no-follow read through every path component; never reveal contents."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute bounded root source required')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory);directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        mask = 0o077 if private else 0o022
        if (info.st_uid != 0 or not stat.S_ISREG(info.st_mode) or info.st_mode & mask
                or info.st_nlink != 1 or not 0 < info.st_size <= maximum
                or readable_group is not None and (info.st_gid != readable_group or info.st_mode & 0o040 != 0o040)):
            raise ValueError('source must be a protected root-owned regular file')
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(raw) != info.st_size or (info.st_size, info.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('root source changed during read')
        return raw


def root_json(path, *, private=False, readable_group=None):
    return json.loads(root_bytes(path, private=private, readable_group=readable_group))


def directory_fd(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute bounded directory required')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory);directory = child
        return directory
    except BaseException:
        os.close(directory)
        raise


def protected_directory(path, *, private=False, group=0):
    path = Path(path)
    parent = directory_fd(path.parent)
    fd = None
    created = False
    requested = 0o700 if private else 0o750
    try:
        try:
            os.mkdir(path.name, mode=requested, dir_fd=parent)
            created = True
        except FileExistsError:
            pass
        fd = os.open(path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        if created:
            os.fchown(fd, 0, group)
            os.fchmod(fd, requested)  # Unit UMask=0077 must not strip intended group read/traverse.
        info = os.fstat(fd)
        if (info.st_uid != 0 or info.st_mode & (0o077 if private else 0o022)
                or group == 10001 and (info.st_gid != group or info.st_mode & 0o050 != 0o050)):
            raise ValueError('service directory is not root protected')
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent)
    return path


def atomic(path, data, *, mode=0o600, group=0):
    path = Path(path)
    directory = directory_fd(path.parent)
    temporary = '.' + path.name + '.' + uuid.uuid4().hex + '.tmp'
    fd = None
    try:
        info = os.fstat(directory)
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('atomic destination directory must be root protected')
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode, dir_fd=directory)
        os.fchown(fd, 0, group)
        os.fchmod(fd, mode)  # Apply exact reviewed mode before the file becomes visible.
        with os.fdopen(fd, 'wb') as out:
            fd = None
            out.write(data);out.flush();os.fsync(out.fileno())
        os.replace(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
    finally:
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
        os.close(directory)


def registration(path, site):
    value = root_json(path)
    if (not isinstance(value, dict) or set(value) != {'schema_version', 'sites'}
            or value['schema_version'] != 1 or not isinstance(value['sites'], dict)
            or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', site)):
        raise ValueError('closed feedback registration required')
    row = value['sites'].get(site)
    if not isinstance(row, dict) or set(row) != SITE_FIELDS:
        raise ValueError('site registration missing or malformed')
    if row['enabled'] is not True:
        raise ValueError('feedback registration is disabled')
    if (type(row['cockpit_id']) is not int or row['cockpit_id'] <= 0 or row['stage_id'] != STAGE
            or row['reviewer_id'] != REVIEWER or row['repository'] != REPOSITORY or row['subtree'] != SUBTREE):
        raise ValueError('site is outside the currently installed feedback authority scope')
    for key in ('client_id',):
        if not isinstance(row[key], str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', row[key]):
            raise ValueError('invalid registered ' + key)
    if row['worker_root'] != str(WORKSPACES / row['client_id']):
        raise ValueError('worker root differs from the registered central Codex location')
    if not isinstance(row['account'], str) or parseaddr(row['account'])[1] != row['account'] or '@' not in row['account']:
        raise ValueError('invalid registered Gmail account')
    if (not isinstance(row['senders'], list) or not row['senders']
            or any(not isinstance(v, str) or v != v.lower() or parseaddr(v)[1] != v or '@' not in v for v in row['senders'])):
        raise ValueError('exact registered client senders required')
    if (not isinstance(row['threads'], list) or not row['threads']
            or any(not isinstance(v, str) or not re.fullmatch(r'[a-f0-9]{8,64}', v) for v in row['threads'])):
        raise ValueError('exact registered Gmail threads required')
    when = datetime.fromisoformat(row['review_start'])
    if when.tzinfo is None:
        raise ValueError('review window needs timezone')
    if not isinstance(row['client_label'], str) or not 1 <= len(row['client_label']) <= 100 or re.search(r'[<>\r\n]', row['client_label']):
        raise ValueError('verified plain client label required')
    note = Path(row['canonical_note'])
    if (note.is_absolute() or '..' in note.parts or not str(note).startswith('20 Clients/') or note.suffix != '.md'):
        raise ValueError('canonical shared client note required')
    if (not re.fullmatch(r'https://drive\.google\.com/drive/folders/[A-Za-z0-9_-]{8,160}', row['work_folder_url'])
            or row['preview_url'] != 'https://lhmstaging.net/prototypes/luminary-counselling/homepage/'):
        raise ValueError('registered working folder and prototype URL required')
    return row


class NativeTed:
    """Actual existing authenticated bridge, never a new credential or worker."""
    def request(self, kind, action, arguments):
        done = subprocess.run(DOCKER, input=canonical({'kind': kind, 'action': action, 'arguments': arguments}).decode(),
                              text=True, capture_output=True, timeout=100, check=False)
        if done.returncode or len(done.stdout) > 2 * MAX_JSON:
            raise ReconcileRequired('authenticated Ted bridge failed; inspect private host logs')
        try:
            return json.loads(done.stdout)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ReconcileRequired('Ted bridge did not return one structured receipt') from exc

    def basicops(self, action, arguments):
        if action not in BASICOPS_READ | BASICOPS_WRITE:
            raise ValueError('unsupported feedback BasicOps action')
        value = self.request('basicops', action, arguments)
        return {'data': value} if action.startswith('list_') and isinstance(value, list) else value

    def route(self, action, task_id, instruction_message_id=None):
        if action not in ('submit', 'status') or type(task_id) is not int or task_id <= 0:
            raise ValueError('unsupported native router action')
        args = {'task_id': task_id}
        if action == 'submit':
            if not isinstance(instruction_message_id, str) or not re.fullmatch(r'dm[1-9][0-9]*', instruction_message_id):
                raise ValueError('exact Ted instruction receipt required')
            args['instruction_message_id'] = instruction_message_id
        return self.request('router', action, args)


class NativeSourceStore:
    """Fetch the allowlisted prototype source into a separate private object store.

    Reuses the root-owned publisher's transport internally. Neither its key nor
    environment is returned to the worker. No publisher checkout/reset is used.
    """
    def fetch(self):
        root_bytes(PUBLISHER)
        spec = importlib.util.spec_from_loader('feedback_fixed_publisher', SourceFileLoader('feedback_fixed_publisher', str(PUBLISHER)))
        publisher = importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
        remote = 'ssh://git@ssh.github.com:443/michaellhm/lhm-prototype.git'
        if publisher.REPOSITORY != REPOSITORY or publisher.BRANCH != 'main' or publisher.REMOTE != remote:
            raise ValueError('existing publisher differs from registered prototype source route')
        protected_directory(SOURCE_STORE.parent)
        protected_directory(SOURCE_STORE, private=True)
        lock = os.open(SOURCE_STORE.parent / '.feedback-source.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
            def git(arguments, *, env=None, maximum=MAX_JSON):
                result = subprocess.run(['/usr/bin/git', '--git-dir=' + str(SOURCE_STORE), *arguments],
                    env=env, capture_output=True, timeout=120, check=False)
                if result.returncode or len(result.stdout) > maximum:
                    raise ReconcileRequired('bounded prototype source fetch/archive failed; inspect private root logs')
                return result.stdout
            if not (SOURCE_STORE / 'HEAD').exists():
                git(['init', '--bare', '--quiet'])
            else:
                root_bytes(SOURCE_STORE / 'HEAD')
            git(['fetch', '--no-tags', '--depth=1', remote, 'main'], env=publisher.ssh_env())
            commit = git(['rev-parse', 'FETCH_HEAD']).decode().strip()
            if not re.fullmatch(r'[a-f0-9]{40}', commit):
                raise ValueError('prototype source fetch did not resolve one exact commit')
            archive = git(['archive', '--format=tar', commit, SOURCE_SUBTREE.rstrip('/')], maximum=MAX_SOURCE)
            return {'base_commit': commit, 'archive': archive}
        finally:
            os.close(lock)


class Coordinator:
    def __init__(self, *, config=REGISTRATION, state_root=STATE_ROOT, authority=AUTHORITY, backend=None, source_store=None):
        if os.geteuid() != 0:
            raise ValueError('feedback host coordinator requires the existing root service')
        self.config, self.root, self.authority = Path(config), Path(state_root), Path(authority)
        # Existing pilot audit root is 0755; sensitive state and evidence remain
        # in private children. Do not change unrelated historical audit access.
        protected_directory(self.root)
        self.backend = backend or NativeTed()
        self.source_store = source_store or NativeSourceStore()
        self.write_attempts = 0
        self.submit_attempts = 0
        self.state = protected_directory(self.root / 'state', private=True)
        self.queue = Queue(self.state / 'queue.sqlite')
        self.effects = Effects(self.state / 'effects.sqlite')

    def close(self):
        self.queue.db.close();self.effects.db.close()

    def private_path(self, path):
        path = Path(path)
        if not path.is_absolute() or '..' in path.parts or not path.is_relative_to(self.root):
            raise ValueError('scan source escapes the private feedback store')
        return path

    def packet(self, path, site, reg):
        envelope = root_json(path, private=True)
        if (not isinstance(envelope, dict) or set(envelope) != {'schema_version', 'site', 'packet', 'evidence'}
                or envelope['schema_version'] != 1 or envelope['site'] != site):
            raise ValueError('closed root scan envelope required')
        packet, evidence = envelope['packet'], envelope['evidence']
        if (not isinstance(packet, dict) or set(packet) != PACKET_FIELDS
                or not isinstance(evidence, dict) or set(evidence) != EVIDENCE_FIELDS):
            raise ValueError('complete root packet and scan evidence required')
        for key in ('message_id', 'thread_id'):
            if not isinstance(packet[key], str) or not re.fullmatch(r'[a-f0-9]{8,64}', packet[key]):
                raise ValueError('complete Gmail identities required')
        if (not isinstance(packet['items'], list) or not packet['items']
                or any(not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'].strip()
                       or not isinstance(item.get('request'), str) or not 0 < len(item['request'].strip()) <= 4000 for item in packet['items'])
                or len({item['id'] for item in packet['items']}) != len(packet['items'])):
            raise ValueError('unique bounded extracted feedback items required')
        if (packet['account'] != reg['account'] or packet['site'] != site
                or packet['cockpit_id'] != str(reg['cockpit_id']) or packet['sender'] not in reg['senders']
                or packet['source_url'] != 'https://mail.google.com/mail/u/?authuser=' + quote(reg['account'], safe='') + '#all/' + packet['message_id']):
            raise ValueError('packet differs from root-registered site routing')
        when = datetime.fromisoformat(packet['received_at'])
        if when.tzinfo is None or when < datetime.fromisoformat(reg['review_start']):
            raise ValueError('packet falls outside registered feedback review window')
        if any(evidence[k] != packet[k] for k in ('account', 'message_id', 'thread_id')) or evidence['packet_sha256'] != sha(canonical(packet)):
            raise ValueError('scan evidence does not bind this exact packet')
        raw = root_bytes(self.private_path(evidence['raw_path']), private=True, maximum=MAX_RAW)
        if sha(raw) != evidence['raw_sha256']:
            raise ValueError('raw Gmail MIME hash mismatch')
        # Recheck receiving Gmail proof on the immutable raw source, independently
        # of scanner/model classification and root promotion flags. No profile fallback.
        from intake_scan import trusted_gmail_authentication
        trusted_gmail_authentication(raw, packet['sender'])
        receipt_raw = root_bytes(self.private_path(evidence['extraction_receipt_path']), private=True)
        if sha(receipt_raw) != evidence['extraction_receipt_sha256']:
            raise ValueError('extraction receipt hash mismatch')
        receipt = json.loads(receipt_raw)
        if (not isinstance(receipt, dict) or set(receipt) != EXTRACTION_FIELDS
                or receipt['schema_version'] != 1 or receipt['status'] != 'reviewed'
                or any(receipt[k] != evidence[k] for k in ('account', 'message_id', 'thread_id', 'raw_sha256', 'packet_sha256'))
                or not isinstance(receipt['reviewer'], str) or not re.fullmatch(r'codex:[a-f0-9-]{36}', receipt['reviewer'])
                or type(receipt['related_thread']) is not bool):
            raise ValueError('verified extraction run and exact scan receipt required')
        try:
            uuid.UUID(receipt['reviewer'].split(':', 1)[1])
        except ValueError as exc:
            raise ValueError('invalid actual extraction session') from exc
        message = BytesParser(policy=policy.default).parsebytes(raw)
        if any(part.defects for part in message.walk()) or len(message.get_all('From', [])) != 1 or len(message.get_all('Date', [])) != 1:
            raise ValueError('full unambiguous MIME required')
        if parseaddr(str(message['From']))[1].lower() != packet['sender'] or parsedate_to_datetime(str(message['Date'])) != when:
            raise ValueError('MIME sender or timestamp differs from registered packet')
        texts, rich, attachments = [], [], []
        for index, part in enumerate(message.walk()):
            if part.is_multipart():
                continue
            data = part.get_payload(decode=True)
            if part.defects or not isinstance(data, bytes):
                raise ValueError('malformed MIME transfer encoding')
            mime = part.get_content_type()
            if mime in ('text/plain', 'text/html') and part.get_content_disposition() != 'attachment' and not part.get_filename():
                text = data.decode(part.get_content_charset() or 'utf-8', errors='strict')
                (texts if mime == 'text/plain' else rich).append(text)
            else:
                cid = str(part.get('Content-ID', '')).strip().strip('<>') or str(index)
                attachments.append((cid, sha(data)))
        if packet['original_text'] != '\n'.join(texts or rich) or not packet['original_text']:
            raise ValueError('full original message text differs from MIME')
        if not isinstance(packet['images'], list) or type(receipt['attachment_count']) is not int or receipt['attachment_count'] != len(attachments):
            raise ValueError('MIME attachment inventory is incomplete')
        images = []
        for image in packet['images']:
            if (not isinstance(image, dict) or set(image) != {'content_id', 'private_ref', 'sha256', 'context', 'status'}
                    or image['status'] != 'verified' or not isinstance(image['context'], str) or not image['context'].strip()):
                raise ValueError('every attachment needs actual visual/extraction review')
            data = root_bytes(self.private_path(image['private_ref']), private=True, maximum=MAX_RAW)
            if sha(data) != image['sha256']:
                raise ValueError('private attachment hash mismatch')
            images.append((image['content_id'], image['sha256']))
        if sorted(images) != sorted(attachments) or len({cid for cid, _ in images}) != len(images):
            raise ValueError('full CID-specific MIME attachment coverage required')
        if packet['thread_id'] not in reg['threads']:
            original = (str(message.get('Subject', '')) + '\n' + packet['original_text']).casefold()
            names = (reg['client_label'].casefold(), reg['subtree'].strip('/').replace('-', ' ').casefold())
            if receipt['related_thread'] is not True or not (reg['preview_url'].casefold() in original or any(name in original for name in names)):
                raise ValueError('separate follow-up lacks an explicit same-prototype reference')
        # Queue performs its own closed item/image/type validation before persistence.
        return packet

    def inbox(self, site, reg):
        folder = self.root / 'inbox' / site
        if not folder.exists():
            return []
        if folder.is_symlink():
            raise ValueError('scan inbox must not be linked')
        return [self.packet(path, site, reg) for path in sorted(folder.glob('*.json'))]

    def basicops(self, action, arguments):
        if action in BASICOPS_WRITE:
            self.write_attempts += 1  # Before transport: a timeout is still an attempted write.
        return self.backend.basicops(action, arguments)

    def intent(self, key, attempts, operation):
        """Drop only this call's new local intent if no mutation was attempted.

        Process death or any attempted remote write leaves the uncertainty ledger
        intact. This exception permits stage-pause recovery before first write.
        """
        existed = self.effects.db.execute('SELECT 1 FROM effects WHERE key=?', (key,)).fetchone()
        before = attempts()
        try:
            return operation()
        except BaseException:
            if not existed and attempts() == before:
                self.effects.db.execute("DELETE FROM effects WHERE key=? AND state='uncertain' AND receipt IS NULL", (key,))
            raise

    def identity(self):
        if self.backend.basicops('get_current_user', {}).get('id') != TED:
            raise ValueError('existing BasicOps connector is not verified Ted')

    def owner(self):
        path = self.state / 'owner.json'
        if not path.exists():
            atomic(path, canonical({'owner': uuid.uuid4().hex}))
        value = root_json(path, private=True)
        if set(value) != {'owner'} or not isinstance(value['owner'], str):
            raise ValueError('persisted coordinator owner is invalid')
        try:
            uuid.UUID(value['owner'])
        except ValueError as exc:
            raise ValueError('persisted coordinator owner is invalid') from exc
        return value['owner']

    def import_packets(self, packets, ops, reg):
        result = []
        for packet in packets:
            if not ops.eligible(reg['cockpit_id']):
                raise ReconcileRequired('stage exit stopped further intake')
            old = self.queue.db.execute('SELECT packet,site FROM messages WHERE account=? AND message_id=?', (packet['account'], packet['message_id'])).fetchone()
            if old and old['site'] != packet['site']:
                raise ReconcileRequired('message already routed to another registered site')
            if old and sha(canonical(json.loads(old[0]))) != sha(canonical(packet)):
                result.append('existing-extraction-differs')
                continue
            result.append(self.queue.enqueue(packet, eligible=True))
        return result

    def worker_anchor(self, reg):
        root = Path(reg['worker_root'])
        for path in (WORKSPACES.parent, WORKSPACES, root):
            fd = directory_fd(path)
            try:
                info = os.fstat(fd)
                if info.st_uid != 0 or info.st_mode & 0o022:
                    raise ValueError('worker input parent must remain root-owned and nonwritable')
            finally:
                os.close(fd)
        metadata = root_json(root / '.workspace.json')
        if any(metadata.get(k) != v for k, v in {'provider': 'codex', 'client_id': reg['client_id'], 'workspace': str(root)}.items()):
            raise ValueError('existing worker workspace registration is not verified')
        return root

    def assets(self, batch, packets, reg):
        root = self.worker_anchor(reg)
        asset_root = protected_directory(root / 'feedback-assets', group=10001)
        target = protected_directory(asset_root / batch, group=10001)
        refs = {}
        for packet in packets:
            for image in packet['images']:
                data = root_bytes(self.private_path(image['private_ref']), private=True, maximum=MAX_RAW)
                if sha(data) != image['sha256']:
                    raise ValueError('image changed before worker handoff')
                dest = target / image['sha256']
                if dest.exists():
                    if root_bytes(dest, maximum=MAX_RAW, readable_group=10001) != data:
                        raise ValueError('immutable worker image conflict')
                else:
                    atomic(dest, data, mode=0o640, group=10001)
                refs[(packet['message_id'], image['content_id'])] = str(dest)
        return refs

    def snapshot(self, batch, reg):
        records = protected_directory(self.root / 'sources', private=True)
        record_root = protected_directory(records / batch, private=True)
        worker_parent = protected_directory(self.worker_anchor(reg) / 'feedback-source-snapshots', group=10001)
        worker_batch = protected_directory(worker_parent / batch, group=10001)
        source = protected_directory(worker_batch / 'source', group=10001)
        manifest_path = record_root / 'source-manifest.json'
        fetch_path = record_root / 'fetch.json'
        archive_path = record_root / 'archive.tar'
        if fetch_path.exists():
            fetched = root_json(fetch_path, private=True)
            if (set(fetched) != {'schema_version', 'repository', 'base_commit', 'subtree', 'archive_sha256'}
                    or fetched['schema_version'] != 1 or fetched['repository'] != REPOSITORY
                    or fetched['subtree'] != SOURCE_SUBTREE or not re.fullmatch(r'[a-f0-9]{40}', fetched['base_commit'])):
                raise ReconcileRequired('persisted source fetch provenance differs from registered route')
            archive = root_bytes(archive_path, private=True, maximum=MAX_SOURCE)
            if sha(archive) != fetched['archive_sha256']:
                raise ReconcileRequired('persisted source archive hash mismatch')
        else:
            if archive_path.exists() or manifest_path.exists():
                raise ReconcileRequired('source snapshot has no exact fetch provenance; preserve it')
            result = self.source_store.fetch()
            if (not isinstance(result, dict) or set(result) != {'base_commit', 'archive'}
                    or not isinstance(result['base_commit'], str) or not re.fullmatch(r'[a-f0-9]{40}', result['base_commit'])
                    or not isinstance(result['archive'], bytes) or not 0 < len(result['archive']) <= MAX_SOURCE):
                raise ValueError('bounded exact source archive required')
            archive = result['archive']
            fetched = {'schema_version': 1, 'repository': REPOSITORY, 'base_commit': result['base_commit'],
                       'subtree': SOURCE_SUBTREE, 'archive_sha256': sha(archive)}
            atomic(archive_path, archive)
            atomic(fetch_path, canonical(fetched))
        entries, names, total = [], set(), 0
        with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as package:
            for member in package.getmembers():
                name = PurePosixPath(member.name)
                if (name.is_absolute() or '..' in name.parts or any(p.startswith('.') for p in name.parts)):
                    raise ValueError('unsafe path in source archive')
                if member.isdir():
                    if str(name) not in ('luminary-counselling', 'luminary-counselling/homepage') and not str(name).startswith(SOURCE_SUBTREE):
                        raise ValueError('unrelated source archive directory')
                    continue
                if (not member.isfile() or not str(name).startswith(SOURCE_SUBTREE) or name.suffix.lower() not in STATIC
                        or member.size <= 0 or member.size > MAX_RAW or str(name) in names):
                    raise ValueError('source archive contains linked, duplicate, non-static or unrelated files')
                names.add(str(name));total += member.size
                if len(names) > 1000 or total > MAX_SOURCE:
                    raise ValueError('source package exceeds bounded static limits')
                stream = package.extractfile(member)
                if stream is None:
                    raise ValueError('source archive file is missing')
                data = stream.read(MAX_RAW + 1)
                if len(data) != member.size:
                    raise ValueError('source archive file is truncated')
                dest = source.joinpath(*name.parts)
                parent = source
                for part in name.parts[:-1]:
                    parent = protected_directory(parent / part, group=10001)
                if dest.exists():
                    if root_bytes(dest, maximum=MAX_RAW, readable_group=10001) != data:
                        raise ReconcileRequired('immutable active source snapshot differs; never overwrite it')
                else:
                    atomic(dest, data, mode=0o640, group=10001)
                entries.append({'path': str(name), 'size_bytes': len(data), 'sha256': sha(data)})
        entries.sort(key=lambda item: item['path'])
        if SOURCE_SUBTREE + 'index.html' not in names:
            raise ValueError('actual source homepage index is missing')
        actual = []
        for path in source.rglob('*'):
            if path.is_symlink():
                raise ValueError('source snapshot contains a linked path')
            if path.is_file():
                actual.append(str(path.relative_to(source)))
        if sorted(actual) != sorted(names):
            raise ReconcileRequired('unmanifested files exist in immutable source snapshot')
        manifest = {'schema_version': 1, 'repository': REPOSITORY, 'base_commit': fetched['base_commit'],
                    'subtree': SOURCE_SUBTREE, 'source_root': str(source), 'files': entries,
                    'package_sha256': sha(canonical(entries))}
        if manifest_path.exists():
            if root_json(manifest_path, private=True) != manifest:
                raise ReconcileRequired('existing source provenance manifest changed')
        else:
            atomic(manifest_path, canonical(manifest))
        worker_manifest = worker_batch / 'source-manifest.json'
        if worker_manifest.exists():
            if root_json(worker_manifest, readable_group=10001) != manifest:
                raise ReconcileRequired('worker source manifest changed')
        else:
            atomic(worker_manifest, canonical(manifest), mode=0o640, group=10001)
        return manifest

    def payload(self, packets, reg, cockpit):
        links = [cockpit['url'], reg['preview_url'], reg['work_folder_url']]
        links += [packet['source_url'] for packet in packets]
        metadata = ('LHM metadata: work_type=project-task; service=website; source=email; urgent=false; '
                    'handoff_trigger=ready-for-review; next_handoff=Michael Colman; handoff_channel=basicops; '
                    'last_touchpoint=none; touchpoint_cadence=none; next_touchpoint=none; '
                    'orchestration_owner=Ted; workflow_state=executing; approval_status=approved')
        description = '<p>' + metadata + '</p>' + ''.join('<p><a href="' + html.escape(url, quote=True) + '">' + html.escape(url) + '</a></p>' for url in sorted(set(links)))
        return {'title': reg['client_label'] + ': Website - Revise the prototype', 'description': description,
                'projectId': 68635, 'section': reg['stage_id'], 'assignee': TED, 'status': 'In Progress'}

    def brief(self, packets, reg, refs, source):
        esc = html.escape
        items = [item['request'] for packet in packets for item in packet['items']]
        if not items or any(not isinstance(v, str) or not v.strip() or len(v) > 4000 for v in items):
            raise ValueError('bounded extracted checklist required')
        body = '<p>Ted, we need to revise the ' + esc(reg['client_label']) + ' prototype using this client feedback.</p>'
        body += '<ol>' + ''.join('<li>' + esc(value) + '</li>' for value in items) + '</ol>'
        for packet in packets:
            body += '<p><a href="' + esc(packet['source_url'], quote=True) + '">Original feedback</a></p>'
            for image in packet['images']:
                body += '<p>Image ' + esc(image['content_id']) + ': ' + esc(image['context']) + '. Verified private file: ' + esc(refs[(packet['message_id'], image['content_id'])]) + '. SHA-256: ' + esc(image['sha256']) + '.</p>'
        body += ('<p>Exact published source base: ' + esc(source['base_commit']) + '. Immutable source snapshot: ' + esc(source['source_root'] + '/' + SOURCE_SUBTREE)
                 + '. Copy this homepage source into this task’s drafts/revised-source/luminary-counselling/homepage/ before editing. Keep private revision notes outside the public homepage. Do not use earlier source snapshots.</p>')
        body += ('<p>Use prototype-revisions. Keep the change within ' + esc(REPOSITORY + ' / ' + reg['subtree'])
                 + '. Preserve the shared repository’s other prototypes. Verify desktop and mobile. Prepare the scoped drafts/revised-source/luminary-counselling/homepage/ package for the root completion driver; it owns independent QA, the existing prototype-main-v1 publisher and exact deployment/preview readback. Do not publish directly or claim publication from a draft. '
                 'Verify rebate eligibility and actual booking-platform support before adding claims; reference examples are not proof. Do not send client emails or change live client systems.</p>'
                 '<p>Canonical project: ' + esc(reg['canonical_note']) + '. Next handoff: When the checked preview and files are ready, return the verified preview to Michael in BasicOps for review. His existing app handles computer notifications automatically. Do not add a notification service.</p>'
                 '<p>AI authorship: This task was written by Ted.</p>')
        if len(body.encode()) > 24000:
            raise ValueError('feedback brief exceeds central router context bounds')
        return body

    def existing_source_conflict(self, packets, reg, payload):
        ids = {p['message_id'] for p in packets}
        for task in pages(self.backend.basicops, 'list_tasks_in_project', {'projectId': 68635, 'limit': 100}):
            if task['id'] == reg['cockpit_id'] or task.get('status') in ('Complete', 'Cancelled', 'Decline'):
                continue
            if task.get('title') == payload['title'] and task.get('description') == payload['description']:
                continue
            if reg['client_label'].casefold() not in task.get('title', '').casefold():
                continue
            text = task.get('description', '')
            if not any(message in text for message in ids):
                text += '\n'.join(m.get('message', '') for m in pages(self.backend.basicops, 'list_messages_in_task', {'taskId': task['id'], 'limit': 50}))
            if any(message in text for message in ids):
                raise ReconcileRequired('existing feedback task needs explicit queue adoption: ' + task['url'])

    def grant(self, batch, task, message, reg, ops):
        row = self.queue.db.execute('SELECT state,owner,task_id FROM batches WHERE id=?', (batch,)).fetchone()
        if not row or row['state'] != 'active' or row['owner'] != self.owner() or row['task_id'] != str(task['id']):
            raise ValueError('root authority requires the exact active claimed batch/task')
        if not ops.eligible(reg['cockpit_id']):
            raise ReconcileRequired('stage exit stopped new authority admission')
        if actor(task) != TED or task.get('status') != 'In Progress' or actor(message) != TED:
            raise ValueError('live task and instruction must be owned/authored by verified Ted')
        grant = {'authority_id': 'MICHAEL-PROTOTYPE-FEEDBACK-20261107', 'task_id': task['id'],
                 'instruction_message_id': message['id'], 'instruction_sha256': sha(message['message'].encode()),
                 'cockpit_id': reg['cockpit_id'], 'stage_id': reg['stage_id'], 'client_id': reg['client_id'],
                 'batch_id': batch, 'author_id': TED, 'reviewer_id': reg['reviewer_id'],
                 'repository': reg['repository'], 'subtree': reg['subtree'], 'enabled': True}
        protected_directory(self.authority.parent)
        lock = os.open(self.authority.parent / '.write.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(lock, fcntl.LOCK_EX)
            value = root_json(self.authority) if self.authority.exists() else {'schema_version': 1, 'grants': {}}
            if set(value) != {'schema_version', 'grants'} or value['schema_version'] != 1 or not isinstance(value['grants'], dict):
                raise ValueError('existing authority registry is malformed; preserve it')
            prior = value['grants'].get(str(task['id']))
            if prior is not None and prior != grant:
                raise ReconcileRequired('existing task authority differs; do not overwrite active grant')
            value['grants'][str(task['id'])] = grant
            data = canonical(value)
            if len(data) > 262144:
                raise ValueError('authority registry capacity reached; do not truncate grants')
            atomic(self.authority, data, mode=0o644)
            if root_json(self.authority) != value:
                raise ReconcileRequired('authority source readback mismatch')
        finally:
            os.close(lock)
        return grant

    def dispatch(self, site, reg, ops, owner):
        if not ops.eligible(reg['cockpit_id']):
            return {'state': 'paused', 'reason': 'cockpit is outside Prototype Feedback'}
        batch = self.queue.claim(site, owner=owner, eligible=True)
        if batch is None or batch['state'] == 'busy':
            return {'state': 'idle' if batch is None else 'busy'}
        submitted = self.effects.db.execute('SELECT state,receipt FROM effects WHERE key=?',
            (batch['id'] + ':native-submit',)).fetchone()
        if batch['task_id'] and submitted and submitted[0] == 'verified':
            receipt = json.loads(submitted[1])
            task = self.backend.basicops('get_task', {'taskId': int(batch['task_id'])})
            return self.observe(batch, owner, reg, task, receipt['request_id'])
        packets = self.queue.packets(batch['id'])
        cockpit = self.backend.basicops('get_task', {'taskId': reg['cockpit_id']})
        payload = self.payload(packets, reg, cockpit)
        self.existing_source_conflict(packets, reg, payload)
        refs = self.assets(batch['id'], packets, reg)
        source = self.snapshot(batch['id'], reg)
        try:
            task_receipt = self.intent(batch['id'] + ':task', lambda: self.write_attempts,
                lambda: ops.task(batch['id'], reg['cockpit_id'], payload))
        except ReconcileRequired:
            if not ops.eligible(reg['cockpit_id']):
                return {'state': 'paused', 'batch_id': batch['id'], 'reason': 'stage exit before task mutation'}
            raise
        task_id = task_receipt['task_id']
        self.queue.checkpoint(batch['id'], owner=owner, task_id=str(task_id))
        task = self.backend.basicops('get_task', {'taskId': task_id})
        brief = self.brief(packets, reg, refs, source)
        if not ops.eligible(reg['cockpit_id']):
            return {'state': 'paused', 'batch_id': batch['id'], 'task_id': task_id, 'reason': 'stage exit before brief/dispatch'}
        message_receipt = self.intent(batch['id'] + ':brief', lambda: self.write_attempts,
            lambda: ops.discussion(batch['id'], task_id, brief))
        messages = list(pages(self.backend.basicops, 'list_messages_in_task', {'taskId': task_id, 'limit': 50}))
        message = next((m for m in messages if m['id'] == message_receipt['message_id'] and m.get('message') == brief), None)
        if message is None or actor(message) != TED:
            raise ReconcileRequired('Ted instruction author/body readback failed')
        self.grant(batch['id'], task, message, reg, ops)
        expected = f"ted-route-{task_id}-{message['id']}"
        def lookup():
            status = self.backend.route('status', task_id)
            if status.get('status') == 'not_submitted':
                return None
            return {'request_id': status.get('request_id'), 'task_id': task_id}
        def submit():
            if not ops.eligible(reg['cockpit_id']):
                raise ReconcileRequired('stage exit stopped native submit')
            self.submit_attempts += 1
            result = self.backend.route('submit', task_id, message['id'])
            return {'request_id': result.get('request_id'), 'task_id': task_id}
        def verify(receipt):
            status = self.backend.route('status', task_id)
            return (receipt == {'request_id': expected, 'task_id': task_id}
                    and status.get('request_id') == expected and status.get('task_id') == task_id
                    and status.get('provider') == 'codex' and status.get('client_id') == reg['client_id']
                    and status.get('status') in ('queued', 'starting', 'running', 'needs_review', 'failed'))
        try:
            self.intent(batch['id'] + ':native-submit', lambda: self.submit_attempts,
                lambda: self.effects.perform(batch['id'] + ':native-submit', {'task_id': task_id, 'message_id': message['id'], 'request_id': expected}, lookup, submit, verify))
        except ReconcileRequired:
            if not ops.eligible(reg['cockpit_id']):
                return {'state': 'paused', 'batch_id': batch['id'], 'task_id': task_id, 'reason': 'stage exit before native dispatch'}
            raise
        return self.observe(batch, owner, reg, task, expected)

    def observe(self, batch, owner, reg, task, expected):
        task_id = task['id']
        status = self.backend.route('status', task_id)
        if (status.get('request_id') != expected or status.get('task_id') != task_id
                or status.get('provider') != 'codex' or status.get('client_id') != reg['client_id']):
            raise ReconcileRequired('existing native request identity changed')
        state = 'submitted-awaiting-admission'
        if status.get('thread_id') and status.get('chat_url'):
            thread = str(uuid.UUID(status['thread_id']))
            link = urlsplit(status['chat_url'])
            if thread != status['thread_id'] or link.scheme != 'codex' or link.netloc != 'threads' or link.path != '/' + thread or not link.query.startswith('hostId='):
                raise ReconcileRequired('native saved Codex chat identity is invalid')
            self.queue.checkpoint(batch['id'], owner=owner, run_id=expected, chat_url=status['chat_url'])
            state = 'dispatched' if status['status'] in ('running', 'needs_review') else 'blocked-run'
        elif status.get('status') == 'failed':
            state = 'blocked-run'
        return {'state': state, 'batch_id': batch['id'], 'task_id': task_id, 'task_url': task['url'],
                'request_id': expected, 'worker_status': status.get('status'), 'chat_url': status.get('chat_url')}

    def run(self, site, action, *, dry_run=False):
        if action not in ('scan', 'dispatch', 'readback'):
            raise ValueError('unsupported host runtime action')
        lock = os.open(self.root / 'runner.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {'state': 'busy', 'site': site}
            reg = registration(self.config, site)
            self.identity()
            ops = BasicOps(self.basicops, self.effects, reg['stage_id'])
            eligible = ops.eligible(reg['cockpit_id'])
            if action == 'readback':
                batches = [dict(row) for row in self.queue.db.execute('SELECT id,state,task_id,run_id,chat_url FROM batches WHERE site=? ORDER BY id', (site,))]
                for batch in batches:
                    if batch['task_id']:
                        batch['native_status'] = self.backend.route('status', int(batch['task_id']))
                return {'state': 'readback', 'site': site, 'eligible': eligible, 'batches': batches}
            if not eligible:
                return {'state': 'paused', 'site': site, 'reason': 'cockpit is outside Prototype Feedback'}
            packets = self.inbox(site, reg)
            if dry_run:
                return {'state': 'prepared', 'site': site, 'eligible': True, 'inbox_messages': len(packets),
                        'attachments': sum(len(p['images']) for p in packets), 'remote_writes': False}
            imported = self.import_packets(packets, ops, reg)
            if action == 'scan':
                return {'state': 'scanned', 'site': site, 'messages': imported, 'remote_writes': False}
            return dict(self.dispatch(site, reg, ops, self.owner()), site=site)
        finally:
            os.close(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('scan', 'dispatch', 'readback'))
    parser.add_argument('--site', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    runtime = Coordinator()
    try:
        print(json.dumps(runtime.run(args.site, args.action, dry_run=args.dry_run), sort_keys=True))
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
