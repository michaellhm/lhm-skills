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
VERSION = '3'
GEMINI = 'GEMINI.md'
GEMINI_START = '<!-- lhm-review-skills:start -->'
GEMINI_END = '<!-- lhm-review-skills:end -->'


def gemini_block(names):
    """Managed list for Gemini CLI, which reads GEMINI.md but has no skills folder."""
    lines = [GEMINI_START, '## Website review skills', '',
             'When the user asks to start, review, preview or finish website work, read and follow the matching file:', '']
    lines += [f'- `skills/{name}/SKILL.md`' for name in names]
    lines.append(GEMINI_END)
    return '\n'.join(lines)


def gemini_text(current, block, recorded):
    """Return GEMINI.md text with the managed list, or None when nothing changes.
    Client text outside the markers is never touched; an edited list is refused."""
    if current is None:
        return block + '\n'
    starts, ends = current.count(GEMINI_START), current.count(GEMINI_END)
    if starts == 0 and ends == 0:
        return current.rstrip('\n') + '\n\n' + block + '\n'
    if starts != 1 or ends != 1 or current.index(GEMINI_START) > current.index(GEMINI_END):
        raise ValueError(f'Existing or edited client file needs review: {GEMINI}')
    s, e = current.index(GEMINI_START), current.index(GEMINI_END) + len(GEMINI_END)
    existing = current[s:e]
    if existing == block:
        return None
    if recorded != hashlib.sha256(existing.encode()).hexdigest():
        raise ValueError(f'Existing or edited client file needs review: {GEMINI}')
    return current[:s] + block + current[e:]


def pointer(name, canonical):
    description = next(line for line in canonical.splitlines() if line.startswith('description:'))
    return (f'---\nname: {name}\n{description}\n---\n'
            f'Read and follow `skills/{name}/SKILL.md`.\n').encode()


def install(root, approval_evidence):
    root = Path(root).resolve()
    if not approval_evidence:
        raise ValueError('Actual operator installation approval evidence is required')
    files = {
        '.lhm-review/workflows.md': (BASE / 'references/client-workflows.md').read_bytes(),
        '.lhm-review/review_release.py': (BASE / 'scripts/review_release.py').read_bytes(),
    }
    for skill in sorted((BASE / 'assets/skills').iterdir()):
        # Canonical client skills live in skills/<name>/; the tool folders only point at them.
        files[f'skills/{skill.name}/SKILL.md'] = (skill / 'SKILL.md').read_bytes()
        for tool in ['.agents', '.claude']:
            files[f'{tool}/skills/{skill.name}/SKILL.md'] = pointer(skill.name, (skill / 'SKILL.md').read_text())
    with r.locked(root):
        manifest_path = r.safe(root, '.lhm-review/manifest.json')
        old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'files': {}}
        for rel, data in files.items():
            path = r.safe(root, rel)
            if path.exists() and path.read_bytes() != data:
                if old.get('files', {}).get(rel) != hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError(f'Existing or edited client file needs review: {rel}')
        gemini_path = r.safe(root, GEMINI)
        block = gemini_block(sorted(s.name for s in (BASE / 'assets/skills').iterdir()))
        current = gemini_path.read_text(encoding='utf-8') if gemini_path.exists() else None
        new_gemini = gemini_text(current, block, old.get('managed_blocks', {}).get(GEMINI))
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
        if new_gemini is not None:
            r.atomic_write(gemini_path, new_gemini)
        manifest = {'toolkit_version': VERSION, 'approval_evidence': approval_evidence,
                    'files': {rel: hashlib.sha256(data).hexdigest() for rel, data in files.items()},
                    'managed_blocks': {GEMINI: hashlib.sha256(block.encode()).hexdigest()}}
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
