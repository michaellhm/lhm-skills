#!/usr/bin/env python3
"""Prepare the fixed RTB draft workspace. Does not activate dispatch or publish anything."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile

STAGE = Path(__file__).resolve().parent
ROOT = Path('/home/codexworker/clients/raise-the-bar')
REPO = Path('/srv/lhm-prototype-publisher/lhm-prototype')
PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if ROOT.exists():
        raise SystemExit('RTB workspace already exists; inspect it before replacing any prepared work')
    base = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'FETCH_HEAD'], text=True).strip()
    ROOT.mkdir(parents=True)
    (ROOT / 'context').mkdir()
    for source in (STAGE / 'context').glob('*.md'):
        shutil.copyfile(source, ROOT / 'context' / source.name)
    # Export only RTB's homepage subtree, never other clients or repository credentials.
    with tempfile.TemporaryFile() as archive:
        subprocess.run(['git', '-C', str(REPO), 'archive', base, 'rtb/homepage'], stdout=archive, check=True)
        archive.seek(0)
        with tarfile.open(fileobj=archive) as files:
            for member in files.getmembers():
                if member.issym() or member.islnk() or '..' in Path(member.name).parts or not (member.name.startswith('rtb/homepage') or (member.isdir() and member.name.rstrip('/') == 'rtb')):
                    raise ValueError('Unexpected prototype archive member')
            files.extractall(ROOT / 'prototype', filter='data')
    # Root-owned immutable originals for patch production and output validation.
    for name in ['index.html', 'assets/css/style.css', 'assets/js/main.js']:
        target = ROOT / 'original' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'prototype/rtb/homepage' / name, target)
    (ROOT / 'drafts').mkdir()
    baseline = {str(p.relative_to(ROOT)): digest(p) for p in ROOT.rglob('*') if p.is_file()}
    sources = [{'label': p.name, 'snapshot': str(p.relative_to(ROOT)), 'sha256': digest(p)}
               for p in sorted((ROOT / 'context').glob('*.md'))]
    manifest = {'schema_version': 1, 'client_id': 'raise-the-bar', 'task_id': 2212824,
        'knowledge_root': '20 Clients/Raise The Bar',
        'work_root': 'https://drive.google.com/drive/folders/1VWZkidj1x869sKc2zBxo8IrSb37w337H',
        'repository': 'michaellhm/lhm-prototype', 'base_commit': base,
        'editable_prototype': 'rtb/homepage', 'sources': sources, 'baseline': baseline,
        'mode': 'rtb_draft_edit', 'delivery_ready': False, 'execution_ready': False,
        'boundary': 'New review files and a review branch only. No main push, shared-site publication, client email or clinical letter.'}
    (ROOT / 'task-context.json').write_text(json.dumps(manifest, indent=2) + '\n')
    # The model may change only the staged copies and create the three draft outputs.
    for path in ROOT.rglob('*'):
        os.chown(path, 0, 10001)
        path.chmod(0o750 if path.is_dir() else 0o440)
    for path in [ROOT / 'drafts', ROOT / 'prototype/rtb/homepage/index.html',
                 ROOT / 'prototype/rtb/homepage/assets/css/style.css', ROOT / 'prototype/rtb/homepage/assets/js/main.js',
                 ROOT / 'prototype/rtb/homepage', ROOT / 'prototype/rtb/homepage/assets/css', ROOT / 'prototype/rtb/homepage/assets/js']:
        os.chown(path, 10001, 10001)
        path.chmod(0o750 if path.is_dir() else 0o640)
    os.chown(ROOT, 0, 10001)
    ROOT.chmod(0o750)
    registry = PROFILE / 'codex-session-pilot.json'
    data = json.loads(registry.read_text())
    data['tasks']['2212824'] = {'enabled': True, 'ready': False, 'mode': 'rtb_draft_edit',
        'client_id': 'raise-the-bar', 'project_id': 49020, 'reviewer_id': 36398}
    registry.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'prepared': True, 'task_id': 2212824, 'base_commit': base,
                      'sources': len(sources), 'ready': False}))

if __name__ == '__main__':
    main()
