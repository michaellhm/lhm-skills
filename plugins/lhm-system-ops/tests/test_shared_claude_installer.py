import importlib.util
import json
import os
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def load_installer():
    path = PLUGIN / "assets/install/install-shared-claude-gateway.py"
    spec = importlib.util.spec_from_file_location("shared_installer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cap_015_preflight_pins_exact_version_sources_and_predecessors(tmp_path):
    installer = load_installer()
    manifest = installer.load_manifest()
    installer.verify_sources(manifest)
    assert manifest["capability_id"] == "CAP-015"
    assert manifest["release_version"] == "0.9.8"
    assert all(item["sha256"] and item["previous_sha256"] for item in manifest["assets"].values())
    destinations = {}
    for name, item in manifest["assets"].items():
        destination = tmp_path / name
        destination.write_bytes(b"wrong")
        destinations[name] = {**item, "destination": str(destination)}
    bad = {**manifest, "assets": destinations}
    try:
        installer.preflight_destinations(bad)
    except SystemExit as exc:
        assert "exact approved CAP-015 predecessor" in str(exc)
    else:
        raise AssertionError("preflight accepted a mismatched deployed binary")


def test_rollback_restores_exact_prior_acl_binaries_and_metadata(tmp_path, monkeypatch):
    installer = load_installer()
    destination = tmp_path / "dispatcher"
    backup = tmp_path / "dispatcher.backup"
    destination.write_bytes(b"new")
    backup.write_bytes(b"prior exact bytes")
    os.chmod(backup, 0o600)
    acl = tmp_path / "ancestors.acl"
    acl.write_text("# exact ACL fixture\n")
    state = tmp_path / "rollback.json"
    state.write_text(json.dumps({
        "capability_id": "CAP-015", "assets": {"dispatcher": {
            "destination": str(destination), "backup": str(backup),
            "sha256": installer.sha256(backup), "uid": os.getuid(), "gid": os.getgid(), "mode": 0o751}},
        "acl_backup": str(acl)}))
    calls = []
    def runner(command, check): calls.append(command)
    installer.rollback(state, runner=runner)
    assert destination.read_bytes() == b"prior exact bytes"
    assert destination.stat().st_mode & 0o777 == 0o751
    assert calls == [["/usr/bin/setfacl", "--restore", str(acl)], ["/usr/bin/systemctl", "daemon-reload"]]


def test_atomic_install_applies_manifest_numeric_client_identity(tmp_path, monkeypatch):
    installer = load_installer()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    source = plugin / "client"
    source.write_bytes(b"governed client")
    destination = tmp_path / "claude-dispatch"
    destination.write_bytes(b"predecessor")
    manifest = {"assets": {"container_client": {
        "source": "client", "destination": str(destination),
        "owner": 10000, "group": 10000, "mode": "0755",
    }}}
    chowns = []
    monkeypatch.setattr(installer.os, "chown", lambda path, uid, gid: chowns.append((uid, gid)))
    installer.atomic_install(manifest, plugin=plugin)
    assert destination.read_bytes() == b"governed client"
    assert destination.stat().st_mode & 0o777 == 0o755
    assert chowns == [(10000, 10000)]
