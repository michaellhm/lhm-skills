#!/usr/bin/env python3
"""Activate only after a normal, user-authorised Drive connection passes exact-client preflight."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path('/home/codexworker/clients/raise-the-bar')
PROFILE = Path('/home/hermes/.hermes/profiles/lhm_chief_of_staff')
FOLDER = '1VWZkidj1x869sKc2zBxo8IrSb37w337H'
REMOTE = 'lhm-rtb:'

def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout

def main():
    if json.loads((ROOT / 'task-context.json').read_text()).get('execution_ready') or any((ROOT / 'drafts').iterdir()):
        raise ValueError('RTB has already been activated or has prepared outputs; do not replace its source baseline')
    # Provider access is through rclone's normal CLI, never raw configuration/credential inspection.
    remotes = run(['rclone', 'listremotes', '--long']).decode()
    if not any('lhm-rtb:' in line and 'drive' in line for line in remotes.splitlines()):
        raise ValueError('Normal Google Drive OAuth connection lhm-rtb is missing')
    args = ['--drive-root-folder-id', FOLDER, '--max-depth', '1', '--retries', '1']
    records = json.loads(run(['rclone', 'lsjson', REMOTE, *args]))
    expected = {'1m4se3qS2tSOLMjb3QU3yH8ISLtkfvIf9': 'handbook-shared.md',
                '1Vqqdtm5UxeP1pBeJF8ClJEsOIjidsUnm': 'handbook-review-existing.md'}
    by_id = {item.get('ID'): item for item in records}
    if not expected.keys() <= by_id.keys():
        raise ValueError('Registered RTB source files were not found in the exact work folder')
    for identifier, snapshot in expected.items():
        name = by_id[identifier]['Name']
        full = run(['rclone', 'cat', REMOTE + name, '--drive-root-folder-id', FOLDER, '--retries', '1']).decode()
        # Patient letter and comments are not needed for this homepage feedback task.
        body = full.split('**Example letter', 1)[0].rstrip()
        target = ROOT / 'context' / snapshot
        target.write_text(body + '\n\n[Clinical example letter and comment appendix omitted; do not recreate or publish.]\n')
        target.chmod(0o440)
    manifest_path = ROOT / 'task-context.json'
    manifest = json.loads(manifest_path.read_text())
    for source in manifest['sources']:
        source['sha256'] = hashlib.sha256((ROOT / source['snapshot']).read_bytes()).hexdigest()
    manifest['baseline'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in ROOT.rglob('*') if p.is_file() and p.name != 'task-context.json'}
    manifest.update(execution_ready=True, delivery_ready=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    registry = PROFILE / 'codex-session-pilot.json'
    data = json.loads(registry.read_text())
    data['tasks']['2212824']['ready'] = True
    registry.write_text(json.dumps(data, indent=2) + '\n')
    subprocess.run(['systemctl', 'enable', '--now', 'lhm-rtb-codex-delivery.timer'], check=True)
    print(json.dumps({'task_id': 2212824, 'ready': True, 'dispatch_still_requires_personal_plan_approval': True}))

if __name__ == '__main__':
    main()
