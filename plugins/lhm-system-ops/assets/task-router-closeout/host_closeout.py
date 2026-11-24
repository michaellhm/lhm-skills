#!/usr/bin/env python3
"""Exact-task close-out broker. No generic API, arbitrary paths, or task completion."""
import fcntl
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import socketserver
import stat
import struct
import subprocess
import sys
import tempfile

ROOT = Path('/var/lib/lhm-task-closeout')
ROUTER = Path('/usr/local/libexec/lhm-task-router')
SOCKET = Path('/run/lhm-task-closeout/broker.sock')
REQUEST = re.compile(r'ted-route-[1-9][0-9]*-dm[1-9][0-9]*')
OPERATIONS = {'get_closeout_context', 'post_basicops_closeout', 'write_knowledge_closeout'}


def read_file(path, limit=65536):
    """Walk every component with openat/O_NOFOLLOW, including mutable draft dirs."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Absolute confined path required')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
                raise ValueError('Regular, unlinked, bounded source required')
            raw = stream.read(limit + 1)
            if len(raw) > limit:
                raise ValueError('Source exceeds close-out limit')
            return raw
    finally:
        os.close(directory)


def save(path, value):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(value, stream)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), 0o600)
    os.replace(temp, path)


def remote_note(request):
    prefix = PurePosixPath(request['client']['vault_prefix'])
    if prefix.is_absolute() or '..' in prefix.parts or len(prefix.parts) < 2 or prefix.parts[0] != '20 Clients':
        raise ValueError('Registered client knowledge prefix required')
    return str(prefix / 'Task Close-outs' / (request['request_id'] + '.md'))


def authority(ident):
    if not REQUEST.fullmatch(ident):
        raise ValueError('Exact router request required')
    sys.path.insert(0, str(ROUTER))
    from dispatch import verified
    from workspaces import location
    request = verified(ident)  # Live human instruction, task ownership, client and state.
    if request['provider'] != 'claude' or request['request_id'] != ident:
        raise ValueError('Verified Claude request required')
    if request.get('feedback_authority') or request.get('permission_ceiling') == 'registered_prototype_revision':
        raise ValueError('Prototype feedback must use its existing independent completion route')
    task = location('claude', request['client_id']) / 'tasks' / ident
    # Root-created provider/client anchors; no worker-controlled workspace mapping.
    for anchor in (task.parent, task.parent.parent):
        info = anchor.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Untrusted client workspace anchor')
    info = task.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 10002:
        raise ValueError('Expected worker task directory unavailable')
    return request, task


def api(name, arguments):
    if name not in {'get_task', 'list_messages_in_task', 'create_message_in_task', 'get_current_user'}:
        raise ValueError('Unsupported BasicOps operation')
    code = ('import json,sys; sys.path.insert(0,"/opt/data/profiles/lhm_chief_of_staff/task-router"); '
            'from server import instance; p=json.load(sys.stdin); '
            'print(json.dumps(instance().api(p["name"],p["arguments"])))')
    result = subprocess.run(['docker', 'exec', '-i', '--user', 'hermes', 'hermes',
                             '/opt/hermes/.venv/bin/python', '-c', code],
                            input=json.dumps({'name': name, 'arguments': arguments}), text=True,
                            capture_output=True, timeout=50)
    if result.returncode:
        raise ValueError('Existing authenticated BasicOps route failed; no delivery claimed')
    return json.loads(result.stdout)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, value):
        self.parts.append(value)
    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.parts.append('\n')


def text_body(value):
    parser = Text()
    parser.feed(value)
    return ''.join(parser.parts).replace('\r\n', '\n').strip()


def post(request, content, state_path):
    sha = hashlib.sha256(content).hexdigest()
    payload = (content.decode().strip() + '\n\nLHM task close-out: ' + request['request_id'] +
               '\nSource SHA-256: ' + sha + '\nAI authorship: Claude worker; host-verified close-out.')
    state = json.loads(read_file(state_path)) if state_path.exists() else {}
    if state and state.get('sha256') != sha:
        raise ValueError('A different close-out was already submitted for this request; use a new authorised task instruction')
    task_id = request['task_id']
    current = api('get_task', {'taskId': task_id})
    if current.get('id') != task_id or current.get('url') != request['task_url']:
        raise ValueError('BasicOps task readback identity mismatch')
    identity = api('get_current_user', {})['id']
    def find():
        value = api('list_messages_in_task', {'taskId': task_id, 'limit': 50})
        messages = value if isinstance(value, list) else value.get('data', [])
        from router import actor
        return next((m for m in messages if actor(m) == identity and text_body(m.get('message', '')) == payload), None)
    found = find()
    if not found:
        if state.get('attempted'):
            raise ValueError('Previous BasicOps attempt has an uncertain outcome; refusing a duplicate. Inspect the task discussion.')
        save(state_path, {'sha256': sha, 'attempted': True})  # Durable before remote mutation.
        api('create_message_in_task', {'taskId': task_id, 'message': '<pre>' + html.escape(payload) + '</pre>'})
        found = find()
    if not found or not found.get('id'):
        raise ValueError('Close-out discussion readback failed; no verified posting claimed')
    result = {'status': 'verified', 'task_url': request['task_url'], 'task_id': task_id,
              'message_id': found['id'], 'sha256': sha, 'task_completion': 'unchanged'}
    save(state_path, {**result, 'attempted': True})
    return result


def knowledge_read(relative):
    result = subprocess.run(['/usr/local/bin/rclone', 'cat', 'lhm-knowledge:' + relative,
                             '--config', '/etc/lhm-obsidian-sync/rclone.conf', '--retries', '1'],
                            capture_output=True, timeout=45)
    if result.returncode in {3, 4}:
        return None
    if result.returncode:
        raise ValueError('Shared knowledge read failed; no write claimed')
    return result.stdout


def write_note(request, content, state_path):
    relative = remote_note(request)
    note = ('# Task close-out\n\nTask: ' + request['task_url'] + '\nRequest: ' + request['request_id'] +
            '\nClient: ' + request['client_id'] + '\nSource SHA-256: ' + hashlib.sha256(content).hexdigest() +
            '\n\n' + content.decode().strip() + '\n').encode()
    prior = knowledge_read(relative)
    if prior is not None and prior != note:
        raise ValueError('Existing knowledge note differs; refusing overwrite')
    if prior is None:
        with tempfile.NamedTemporaryFile(dir=ROOT) as stream:
            stream.write(note)
            stream.flush()
            result = subprocess.run(['/usr/local/bin/rclone', 'copyto', stream.name, 'lhm-knowledge:' + relative,
                                     '--config', '/etc/lhm-obsidian-sync/rclone.conf', '--ignore-existing', '--retries', '1'],
                                    capture_output=True, timeout=60)
            if result.returncode:
                raise ValueError('Knowledge note write failed; inspect receipt before retrying')
    if knowledge_read(relative) != note:
        raise ValueError('Knowledge close-out readback mismatch; no delivery claimed')
    result = {'status': 'verified', 'knowledge_path': relative, 'sha256': hashlib.sha256(content).hexdigest(),
              'note_sha256': hashlib.sha256(note).hexdigest(), 'sync_directory_access': 'unchanged'}
    save(state_path, result)
    return result


def handle(packet):
    if not isinstance(packet, dict) or set(packet) != {'request_id', 'operation', 'arguments'}:
        raise ValueError('Closed request schema required')
    ident, operation, arguments = packet['request_id'], packet['operation'], packet['arguments']
    if not isinstance(ident, str) or not REQUEST.fullmatch(ident) or operation not in OPERATIONS or not isinstance(arguments, dict):
        raise ValueError('Unsupported close-out request')
    with (ROOT / (ident + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        request, task = authority(ident)
        if operation == 'get_closeout_context':
            if arguments:
                raise ValueError('Context takes no arguments')
            receipts = {}
            for kind in ('basicops', 'knowledge'):
                path = ROOT / (ident + '.' + kind + '.json')
                receipts[kind] = json.loads(read_file(path)) if path.exists() else {'status': 'not_submitted'}
            return {'request_id': ident, 'client_id': request['client_id'], 'task_url': request['task_url'],
                    'title': request['title'], 'knowledge_destination': remote_note(request), 'receipts': receipts,
                    'task_completion': 'This connector never completes or reassigns tasks.'}
        if set(arguments) != {'draft_name'} or not isinstance(arguments['draft_name'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}\.md', arguments['draft_name']):
            raise ValueError('One flat Markdown draft filename required')
        content = read_file(task / 'drafts' / arguments['draft_name'], 48000)
        if not content.decode('utf-8').strip() or b'\x00' in content:
            raise ValueError('Nonempty UTF-8 Markdown required')
        kind = 'basicops' if operation == 'post_basicops_closeout' else 'knowledge'
        target = ROOT / (ident + '.' + kind + '.json')
        return post(request, content, target) if kind == 'basicops' else write_note(request, content, target)


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(160)
        try:
            _, uid, _ = struct.unpack('3i', self.request.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if uid != 10002:
                raise ValueError('Claude worker peer identity required')
            raw = self.rfile.readline(65537)
            if len(raw) > 65536 or not raw.endswith(b'\n'):
                raise ValueError('Bounded JSON request required')
            response = {'result': handle(json.loads(raw))}
        except Exception as exc:
            # Never return subprocess stdout/stderr or credential-bearing config.
            response = {'error': str(exc) if isinstance(exc, ValueError) else 'Host close-out operation failed; inspect the private service log.'}
        self.wfile.write((json.dumps(response) + '\n').encode())


def main():
    if os.geteuid() != 0:
        raise SystemExit('Host service requires root')
    ROOT.mkdir(mode=0o700, exist_ok=True)
    ROOT.chmod(0o700)
    SOCKET.parent.mkdir(mode=0o755, exist_ok=True)
    if SOCKET.exists():
        if not stat.S_ISSOCK(SOCKET.lstat().st_mode):
            raise ValueError('Refusing unexpected socket path')
        SOCKET.unlink()
    with socketserver.ThreadingUnixStreamServer(str(SOCKET), Handler) as server:
        os.chown(SOCKET, 0, 10002)
        SOCKET.chmod(0o660)
        server.daemon_threads = True
        server.serve_forever()


if __name__ == '__main__':
    main()
