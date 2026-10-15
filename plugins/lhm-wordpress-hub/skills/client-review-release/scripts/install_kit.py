#!/usr/bin/env python3
"""Install client-only review skills locally; no Git, deployment or email actions."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_release', BASE / 'scripts/review_release.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
START, END = '<!-- LHM-REVIEW:START -->', '<!-- LHM-REVIEW:END -->'
VERSION = '2'


def install(root, approval_evidence):
    root = Path(root).resolve()
    if not approval_evidence:
        raise ValueError('Actual operator installation approval evidence is required')
    files = {
        '.lhm-review/workflows.md': (BASE / 'references/client-workflows.md').read_bytes(),
        '.lhm-review/review_release.py': (BASE / 'scripts/review_release.py').read_bytes(),
    }
    for tool in ['.agents', '.claude']:
        for skill in sorted((BASE / 'assets/skills').iterdir()):
            files[f'{tool}/skills/{skill.name}/SKILL.md'] = (skill / 'SKILL.md').read_bytes()
    with r.locked(root):
        manifest_path = r.safe(root, '.lhm-review/manifest.json')
        old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'files': {}}
        for rel, data in files.items():
            path = r.safe(root, rel)
            if path.exists() and path.read_bytes() != data:
                if old.get('files', {}).get(rel) != hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError(f'Existing or edited client file needs review: {rel}')
        readme = r.safe(root, 'README.md')
        text = readme.read_text(encoding='utf-8') if readme.exists() else ''
        block = START + '\n' + (BASE / 'assets/README-client.md').read_text() + '\n' + END
        if text.count(START) != text.count(END) or text.count(START) > 1:
            raise ValueError('README review markers are ambiguous')
        if START in text:
            before, rest = text.split(START)
            _, after = rest.split(END)
            text = before + block + after
        else:
            text = text.rstrip() + '\n\n' + block + '\n'
        config = r.safe(root, '.lhm-review/client-config.json')
        if not config.exists():
            files['.lhm-review/client-config.json'] = (BASE / 'assets/client-config.example.json').read_bytes()
        # Preflight every path before any install write. Manifest is written last;
        # after I/O failure read these same paths and reconcile before retry.
        for rel in files:
            r.safe(root, rel)
        r.safe(root, '.lhm-review/manifest.json')
        for rel, data in files.items():
            path = r.safe(root, rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            r.atomic_write(path, data.decode('utf-8'))
        r.atomic_write(readme, text)
        manifest = {'toolkit_version': VERSION, 'approval_evidence': approval_evidence,
                    'files': {rel: hashlib.sha256(data).hexdigest() for rel, data in files.items()}}
        r.atomic_write(manifest_path, json.dumps(manifest, indent=2) + '\n')
        for rel, expected in manifest['files'].items():
            if hashlib.sha256(r.safe(root, rel).read_bytes()).hexdigest() != expected:
                raise ValueError(f'Install readback failed: {rel}')
        return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--approval-evidence', required=True)
    a = p.parse_args()
    try:
        print(json.dumps(install(a.root, a.approval_evidence), indent=2))
    except (ValueError, OSError) as exc:
        p.exit(2, f'Install stopped: {exc}\n')
