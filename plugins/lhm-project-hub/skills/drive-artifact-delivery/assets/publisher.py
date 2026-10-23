"""Shared google-drive-file-publish implementation: bounded create, exact readback, no overwrite."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROUTE = 'google-drive-file-publish'
SAFE_ID = re.compile(r'[A-Za-z0-9_-]{8,160}')
SAFE_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9 ._()&-]{0,119}')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class Drive:
    def __init__(self, config):
        self.config = config
        if config.get('route') != ROUTE or not re.fullmatch(r'[A-Za-z0-9_-]+:', config.get('remote', '')):
            raise ValueError('Unregistered Drive publishing route')
        for key in ['current_clients_id', 'workspace_id']:
            if not SAFE_ID.fullmatch(config.get(key, '')):
                raise ValueError('Invalid registered workspace ancestry')

    def call(self, command, folder, path='', *options):
        if not SAFE_ID.fullmatch(folder):
            raise ValueError('Invalid exact Drive folder')
        if path and any(not SAFE_NAME.fullmatch(p) or p in {'.', '..'} for p in path.split('/')):
            raise ValueError('Invalid bounded Drive path')
        args = ['/usr/local/bin/rclone', command, self.config['remote'] + path,
                '--drive-root-folder-id', folder, '--retries', '1', '--low-level-retries', '1', *options]
        done = subprocess.run(args, capture_output=True, timeout=60)
        if done.returncode:
            raise ValueError('Drive operation failed; authentication/transport diagnostics retained by the host, not disclosed')
        return done.stdout

    def children(self, folder, path=''):
        return json.loads(self.call('lsjson', folder, path, '--max-depth', '1'))

    def verify_client(self, folder):
        # Enumerate metadata only; never resolve a client by a guessed name.
        parents = self.children(self.config['workspace_id'])
        if len([p for p in parents if p.get('ID') == self.config['current_clients_id'] and p.get('IsDir')]) != 1:
            raise ValueError('Current Clients ancestry is not verified')
        clients = self.children(self.config['current_clients_id'])
        if len([p for p in clients if p.get('ID') == folder and p.get('IsDir')]) != 1:
            raise ValueError('Registered client is not directly beneath Current Clients')

    def ensure_path(self, folder, path):
        parent = folder
        built = []
        for name in path.split('/'):
            if not SAFE_NAME.fullmatch(name) or name in {'.', '..'}:
                raise ValueError('Invalid delivery folder component')
            matches = [p for p in self.children(parent) if p.get('Name') == name]
            if not matches:
                self.call('mkdir', parent, name)
                matches = [p for p in self.children(parent) if p.get('Name') == name]
            if len(matches) != 1 or not matches[0].get('IsDir') or not SAFE_ID.fullmatch(matches[0].get('ID', '')):
                raise ValueError('Drive folder conflict; refuse an ambiguous destination')
            parent = matches[0]['ID'];built.append(name)
        return parent

    def publish(self, source, name, folder, expected_sha256, expected_size, expected_media_type=None):
        source = Path(source)
        raw = source.read_bytes()
        if len(raw) != expected_size or digest(raw) != expected_sha256:
            raise ValueError('Staged bytes changed after producer QA')
        if not SAFE_NAME.fullmatch(name) or name in {'.', '..'}:
            raise ValueError('Invalid deliverable name')
        matches = [p for p in self.children(folder) if p.get('Name') == name]
        if len(matches) > 1 or (matches and matches[0].get('IsDir')):
            raise ValueError('Exact-name Drive conflict')
        action = 'already_existed' if matches else 'created'
        if matches:
            if self.call('cat', folder, name) != raw:
                raise ValueError('Different Drive file already has the intended name; never overwrite')
        else:
            args = ['/usr/local/bin/rclone', 'copyto', str(source), self.config['remote'] + name,
                    '--drive-root-folder-id', folder, '--immutable', '--ignore-existing',
                    '--retries', '1', '--low-level-retries', '1']
            result = subprocess.run(args, capture_output=True, timeout=90)
            if result.returncode:
                raise ValueError('Drive file create failed')
        matches = [p for p in self.children(folder) if p.get('Name') == name]
        if len(matches) != 1 or matches[0].get('IsDir') or not SAFE_ID.fullmatch(matches[0].get('ID', '')):
            raise ValueError('Drive file metadata readback failed')
        observed_type = matches[0].get('MimeType', '').split(';', 1)[0]
        if expected_media_type and observed_type != expected_media_type:
            raise ValueError('Drive media type readback mismatch')
        content = self.call('cat', folder, name)
        if (len(content) != expected_size or digest(content) != expected_sha256
                or matches[0].get('Size') != expected_size):
            raise ValueError('Drive full-content/size/hash readback failed')
        file_id = matches[0]['ID']
        return {'run_result': 'passed', 'artefact_state': 'delivered', 'route': ROUTE,
                'name': name, 'file_id': file_id, 'url': 'https://drive.google.com/file/d/' + file_id + '/view',
                'folder_id': folder, 'folder_url': 'https://drive.google.com/drive/folders/' + folder,
                'size_bytes': expected_size, 'media_type': observed_type, 'sha256': expected_sha256, 'readback_sha256': digest(content),
                'action': action, 'checks': ['exact_name', 'exact_parent_listing', 'file_id', 'byte_count', 'full_content_sha256'],
                'approval_still_required': 'Publishing, live account changes and client sends remain separate'}
