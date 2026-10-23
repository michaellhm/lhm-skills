"""Read canonical client entry points; export pointers, never a second client database."""
import copy
import json
import os
from pathlib import Path
import re
import stat
import time
from urllib.parse import urlparse

import yaml

MAX_NOTE = 512000


def note(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_NOTE:
            raise ValueError('Client entry point is not a bounded regular note')
        return stream.read()


def build(vault, registered):
    vault = Path(vault).resolve()
    root = vault / '20 Clients'
    index = root / 'Clients.md'
    if not index.is_file() or index.is_symlink():
        raise ValueError('Canonical shared Clients index is unavailable')
    clients = copy.deepcopy(registered)
    indexed = set(re.findall(r'\[\[(20 Clients/[^\]|\\]+)', note(index)))
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or folder.is_symlink() or folder.name.startswith(('.', '_')):
            continue
        overview = folder / (folder.name + '.md')
        if not overview.is_file() or overview.is_symlink() or not overview.resolve().is_relative_to(root):
            continue
        text = note(overview)
        front = yaml.safe_load(text.split('---', 2)[1]) if text.startswith('---\n') else {}
        front = front if isinstance(front, dict) else {}
        if front.get('type', 'client') != 'client' or front.get('status') in {'archived', 'inactive', 'prospect'}:
            continue
        heading = re.search(r'^#\s+(.+)$', text, re.M)
        name = heading.group(1).strip() if heading else folder.name
        prefix = str(folder.relative_to(vault)) + '/'
        matches = [key for key, item in clients.items() if item.get('vault_prefix', '').rstrip('/') == prefix.rstrip('/')]
        if len(matches) > 1:
            raise ValueError('Several client registrations point to one canonical root')
        slug = matches[0] if matches else re.sub(r'[^a-z0-9]+', '-', folder.name.casefold()).strip('-')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', slug):
            raise ValueError('Invalid canonical client identifier')
        if not matches and slug in clients:
            raise ValueError('Canonical client identifier collision; do not merge clients')
        entry = clients.setdefault(slug, {'name': name, 'vault_prefix': prefix, 'basicops_task_ids': []})
        aliases = front.get('aliases', [])
        if isinstance(aliases, str):
            aliases = [aliases]
        if not isinstance(aliases, list) or any(not isinstance(a, str) or not 1 <= len(a) <= 120 for a in aliases):
            raise ValueError('Malformed client aliases in canonical overview')
        entry['aliases'] = sorted(set([name, folder.name, *entry.get('aliases', []), *aliases]))
        entry['canonical_overview'] = str(overview.relative_to(vault))
        entry['knowledge_index'] = '20 Clients/Clients.md'
        entry['listed_in_index'] = str(overview.relative_to(vault))[:-3] in indexed
        entry['context_notes'] = [str(p.relative_to(vault)) for p in [
            overview, folder / 'client_profile.md', folder / 'Goals.md', folder / 'Current Projects.md']
            if p.is_file() and not p.is_symlink()]
        entry['project_notes'] = prefix + 'project-management/'
        # These are sourced links, NOT a declaration of live access or write authority.
        section = re.search(r'^## Systems and files\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
        links = []
        for url in re.findall(r'https://[^\s)<>\]]+', section.group(1) if section else ''):
            parsed = urlparse(url.rstrip('.,;'))
            if parsed.hostname not in {'drive.google.com', 'docs.google.com', 'github.com'} or parsed.query or parsed.fragment:
                continue
            links.append({'url': parsed.geturl(), 'source': entry['canonical_overview'] + '#Systems and files',
                          'verification': 'recorded_link_recheck_before_writes'})
        entry['systems_links'] = sorted(links, key=lambda x: x['url'])
    return {'schema_version': 1, 'source': 'shared LHM Knowledge / 20 Clients/Clients.md and canonical client overviews',
            'clients': clients}


def refresh(vault, profile, registered):
    profile = Path(profile)
    status = json.loads((profile / 'task-router-knowledge-refresh.json').read_text())
    if status.get('status') != 'ready' or not 0 <= time.time() - status.get('completed_at', 0) <= 900:
        raise ValueError('Shared client knowledge refresh is unavailable or stale; use live canonical evidence')
    directory = build(vault, registered)
    directory['knowledge_refreshed_at'] = status['completed_at']
    target = profile / 'task-router-client-directory.json'
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(directory, indent=2) + '\n')
    os.chown(tmp, 0, 10000)
    tmp.chmod(0o640)
    tmp.replace(target)
    return directory
