import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "assets/host/lhm-source-adapter"

def invoke(path, payload, env):
    return subprocess.run([str(path)], input=json.dumps(payload).encode(), capture_output=True, env=env, check=True).stdout

def test_actual_adapter_binaries_with_fake_connector_backends(tmp_path):
    backend = tmp_path / "fake-backend"
    backend.write_text("""#!/usr/bin/env python3
import json, os, sys
p=json.load(sys.stdin); state=os.environ['FAKE_STATE']
if p['action']=='read' and 'content' not in p:
 print(json.dumps({'full_content':open(state).read()}) if os.path.exists(state) else ('drive source' if 'drive' in p.get('identifier','') else 'fathom transcript'))
elif p['action']=='upsert': open(state,'w').write(p['content']); print('{}')
elif p['action']=='produce': print('production:' + '|'.join(x['content'] for x in p['package']['sources']))
else: print('{}')
""")
    backend.chmod(0o755)
    registry = tmp_path / "registrations"; registry.mkdir()
    (registry / "run-one.json").write_text(json.dumps({"sources":[{"kind":"google_drive_file","identifier":"drive-exact"},{"kind":"fathom_transcript","identifier":123}],"destination_identifier":"folder-exact"}))
    config = tmp_path / "adapters.json"
    backends={name:[str(backend)] for name in ("drive_read","production","drive_publish")}
    backends["fathom_read"]=["/usr/bin/sudo","-n","/usr/local/libexec/lhm-evidence-fathom-backend"]
    config.write_text(json.dumps({"schema_version":1,"backends":backends}))
    bindir = tmp_path / "bin"; bindir.mkdir()
    executable = bindir / "lhm-source-adapter"; executable.write_bytes(ADAPTER.read_bytes()); executable.chmod(0o755)
    links = {}
    for name in ("lhm-claude-drive-read","lhm-fathom-transcript-read","lhm-campaign-production-worker","lhm-registered-drive-publisher"):
        link = bindir / name; link.symlink_to(executable); links[name] = link
    env = {**os.environ, "LHM_SOURCE_ADAPTER_CONFIG":str(config), "LHM_SOURCE_REGISTRY":str(registry), "FAKE_STATE":str(tmp_path / "published")}
    drive = invoke(links["lhm-claude-drive-read"], {"run_id":"run-one","identifier":"drive-exact"}, env).decode().strip()
    fathom = "fathom transcript"  # The root bridge has independent boundary tests below.
    package = {"package_type":"verified_evidence","package_sha256":"a"*64,"sources":[{"content":drive},{"content":fathom}]}
    produced = invoke(links["lhm-campaign-production-worker"], package, env).decode().strip()
    published = json.loads(invoke(links["lhm-registered-drive-publisher"], {"run_id":"run-one","destination_identifier":"folder-exact","content":produced}, env))
    assert produced == "production:drive source|fathom transcript"
    assert published["full_content"] == produced and len(published["idempotency_key"]) == 64

def test_adapter_rejects_unregistered_identifier(tmp_path):
    registry=tmp_path/'r'; registry.mkdir(); (registry/'r.json').write_text('{"sources":[],"destination_identifier":"x"}')
    backend=tmp_path/'b'; backend.write_text('#!/bin/sh\nexit 0\n'); backend.chmod(0o755)
    backends={x:[str(backend)] for x in ("drive_read","production","drive_publish")}; backends['fathom_read']=["/usr/bin/sudo","-n","/usr/local/libexec/lhm-evidence-fathom-backend"]
    config=tmp_path/'c'; config.write_text(json.dumps({"schema_version":1,"backends":backends}))
    binary=tmp_path/'lhm-claude-drive-read'; binary.write_bytes(ADAPTER.read_bytes()); binary.chmod(0o755)
    env={**os.environ,"LHM_SOURCE_ADAPTER_CONFIG":str(config),"LHM_SOURCE_REGISTRY":str(registry)}
    done=subprocess.run([str(binary)],input=b'{"run_id":"r","identifier":"no"}',capture_output=True,env=env)
    assert done.returncode != 0 and b'not registered' in done.stderr
