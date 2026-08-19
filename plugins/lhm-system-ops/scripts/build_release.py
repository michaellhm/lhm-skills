#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def git(*args):
    return subprocess.run(['git', '-C', str(REPO), *args], check=True, capture_output=True, text=True).stdout.strip()


def generated_bytecode_paths(root):
    return sorted(
        path.relative_to(root)
        for path in root.rglob('*')
        if '__pycache__' in path.parts or (path.is_file() and path.suffix == '.pyc')
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.suffix != '.zip':
        raise SystemExit('output must be a .zip archive')
    if git('status', '--porcelain'):
        raise SystemExit('release requires a clean working tree')
    bytecode = generated_bytecode_paths(PLUGIN)
    if bytecode:
        raise SystemExit(f'release rejects generated Python bytecode: {bytecode[0]}')
    commit = git('rev-parse', 'HEAD')
    files = sorted(path for path in PLUGIN.rglob('*') if path.is_file())
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = Path(PLUGIN.name) / path.relative_to(PLUGIN)
            info = zipfile.ZipInfo(relative.as_posix(), FIXED_TIME)
            info.external_attr = (0o755 if os.access(path, os.X_OK) or path.suffix == '.py' else 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    result = {'schema_version': 1, 'repository': 'michaellhm/lhm-skills', 'commit': commit, 'plugin': PLUGIN.name, 'archive': str(output), 'sha256': digest, 'files': len(files)}
    output.with_suffix(output.suffix + '.manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
