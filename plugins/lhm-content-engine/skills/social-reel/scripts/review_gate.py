#!/usr/bin/env python3
"""Bind explicit human script/audio approval to package bytes. No publication authority."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def local_file(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('Artefact paths must be package-relative')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'Missing or out-of-package artefact: {relative}')
    return path


def fingerprint(package):
    root = Path(package).resolve()
    script = json.loads(local_file(root, 'script.json').read_text())
    voice = json.loads(local_file(root, 'voice.json').read_text())
    manifest = json.loads(local_file(root, 'audio-manifest.json').read_text())
    if not isinstance(script, list) or not script or any(not isinstance(x, str) or not x.strip() for x in script):
        raise ValueError('script.json must contain non-empty narration strings')
    if not isinstance(voice, dict) or not voice.get('engine') or not voice.get('model'):
        raise ValueError('voice.json must identify engine and model')
    rate = voice.get('playback_rate', 1)
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 < rate <= 5:
        raise ValueError('Invalid playback_rate')
    audio = manifest.get('audio') if isinstance(manifest, dict) else None
    refs = voice.get('references', [])
    if not isinstance(audio, list) or not audio or len(audio) not in (1, len(script)):
        raise ValueError('List one full narration file or one audio file per scene')
    if not isinstance(refs, list):
        raise ValueError('references must be a list')
    names = ['script.json', 'voice.json', 'audio-manifest.json'] + audio + refs
    hashes = {name: hashlib.sha256(local_file(root, name).read_bytes()).hexdigest() for name in names}
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return digest, hashes


def approve(package, reviewer, note):
    if not reviewer.strip() or not note.strip():
        raise ValueError('Reviewer and exact approval evidence are required')
    digest, hashes = fingerprint(package)
    result = {'state': 'script_audio_approved', 'digest': digest, 'files': hashes,
              'reviewer': reviewer, 'evidence': note,
              'recorded_at': datetime.now(timezone.utc).isoformat(), 'publication': 'not_authorised'}
    path = Path(package) / 'approval.json'
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(result, indent=2) + '\n')
    tmp.replace(path)
    return result


def check(package):
    digest, _ = fingerprint(package)
    approval = json.loads(local_file(Path(package).resolve(), 'approval.json').read_text())
    if approval.get('state') != 'script_audio_approved' or approval.get('digest') != digest:
        raise ValueError('Approval is stale: review the current script/audio version')
    if not approval.get('reviewer') or not approval.get('evidence'):
        raise ValueError('Missing human approval evidence')
    return {'state': 'script_audio_approved', 'digest': digest, 'publication': 'not_authorised'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['approve', 'check'])
    parser.add_argument('package')
    parser.add_argument('--by', dest='reviewer')
    parser.add_argument('--note')
    args = parser.parse_args()
    try:
        if args.action == 'approve':
            if not args.reviewer or not args.note:
                parser.error('approve requires --by and --note from explicit human approval')
            result = approve(args.package, args.reviewer, args.note)
        else:
            result = check(args.package)
        print(json.dumps(result))
    except (ValueError, OSError, TypeError, AttributeError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
