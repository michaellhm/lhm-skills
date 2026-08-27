#!/usr/bin/env python3
"""Build a deterministic lhm-project-hub zip from the clean exact HEAD."""
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[3]
PLUGIN = 'plugins/lhm-project-hub'
EXPECTED_VERSION = '0.1.81'

def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True,text=True).stdout

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True,type=Path); a=p.parse_args()
    if git('status','--porcelain').strip(): raise SystemExit('refusing to build from dirty checkout')
    files=[x for x in git('ls-tree','-r','--name-only','HEAD','--',PLUGIN).splitlines() if x]
    if not files: raise SystemExit('project hub is absent from HEAD')
    manifest=json.loads(git('show',f'HEAD:{PLUGIN}/.claude-plugin/plugin.json'))
    if manifest.get('name')!='lhm-project-hub' or manifest.get('version')!=EXPECTED_VERSION:
        raise SystemExit('project hub identity/version mismatch')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source in sorted(files):
            relative=PurePosixPath(source).relative_to('plugins')
            info=zipfile.ZipInfo(str(relative),date_time=(1980,1,1,0,0,0))
            info.create_system=3; info.external_attr=(0o100644 << 16); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,subprocess.run(['git','-C',str(ROOT),'show',f'HEAD:{source}'],check=True,capture_output=True).stdout)
    print(json.dumps({'plugin':'lhm-project-hub','version':EXPECTED_VERSION,
                      'commit':git('rev-parse','HEAD').strip(),'archive':str(a.output.resolve()),
                      'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()},sort_keys=True))

if __name__=='__main__': main()
