import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from types import SimpleNamespace
from pathlib import Path

import pytest


PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((PLUGIN / "references/shared-claude-gateway-release.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_dispatcher():
    path = PLUGIN / MANIFEST["assets"]["dispatcher"]["source"]
    loader = SourceFileLoader("shared_claude_dispatcher", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shared_gateway_sources_match_verified_inventory():
    for name in ("dispatcher", "worker"):
        item = MANIFEST["assets"][name]
        source = PLUGIN / item["source"]
        assert source.is_file()
        assert source.stat().st_size == item["size_bytes"]
        assert digest(source) == item["sha256"]


def test_shared_gateway_destinations_are_exact_and_distinct_from_evidence_bridge():
    assets = MANIFEST["assets"]
    assert assets["dispatcher"]["destination"] == "/usr/local/libexec/lhm-claude-dispatcher"
    assert assets["worker"]["destination"] == "/usr/local/libexec/lhm-claude-worker"
    assert "lhm-evidence-claude" not in assets["dispatcher"]["destination"]
    assert "lhm-evidence-claude" not in assets["worker"]["destination"]
    assert assets["dispatcher"]["mode"] == assets["worker"]["mode"] == "0755"


def test_dispatcher_contains_current_bounded_worker_contract():
    text = (PLUGIN / MANIFEST["assets"]["dispatcher"]["source"]).read_text()
    assert "ensure_worker_traversal" in text
    assert "configure_worker_run_dir" in text
    assert "--uid=claudeworker" in text
    assert "/usr/local/libexec/lhm-claude-worker" in text
    assert "google_ads_readonly" in text
    assert "guard_worker_traversal" in text
    assert "worker_can_traverse" in text


def test_worker_persists_terminal_artifacts_inside_supplied_run_directory():
    text = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "run_dir = Path(sys.argv[1]).resolve()" in text
    assert "persist_text(run_dir / 'result.md'" in text
    assert "persist_text(run_dir / 'final.json'" in text
    assert "--strict-mcp-config" in text
    assert "except PermissionError" in text
    assert "persist_text(run_dir / 'final.json'" in text


def test_release_mapping_tracks_current_units_without_live_install_side_effects():
    for name in ("dispatch_unit", "gateway_acl_dropin"):
        item = MANIFEST["assets"][name]
        assert (PLUGIN / item["source"]).is_file()
        assert item["owner"] == item["group"] == "root"
        assert item["mode"] == "0644"


def test_acl_mask_reset_is_repaired_only_on_exact_ancestors(monkeypatch):
    dispatcher = load_dispatcher()
    calls = []
    effective = {path: False for path in dispatcher.TRAVERSAL_ANCESTORS}

    def fake_run(command, check=False):
        calls.append(command)
        if command[0] == "/usr/sbin/runuser":
            return SimpleNamespace(returncode=0 if effective[Path(command[-1])] else 1)
        assert command[-4:-1] == ["/usr/bin/setfacl", "-m", "m::x,u:claudeworker:--x"]
        target = Path(command[-1])
        assert target in dispatcher.TRAVERSAL_ANCESTORS
        effective[target] = True
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(dispatcher.subprocess, "run", fake_run)
    dispatcher.ensure_worker_traversal()
    acl_calls = [call for call in calls if "/usr/bin/setfacl" in call]
    assert [Path(call[-1]) for call in acl_calls] == list(dispatcher.TRAVERSAL_ANCESTORS)
    assert all("codexworker" not in " ".join(call) for call in acl_calls)


def test_guard_repairs_reset_during_terminal_persistence(monkeypatch, tmp_path):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-01"
    run_dir.mkdir(parents=True)
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    checks = []

    def ensure():
        checks.append("effective")
        if len(checks) == 2:
            (run_dir / "final.json").write_text('{"status":"failed"}\n')

    monkeypatch.setattr(dispatcher, "ensure_worker_traversal", ensure)
    monkeypatch.setattr(dispatcher.time, "sleep", lambda _interval: None)
    monkeypatch.setattr(
        dispatcher.subprocess, "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=0),
    )
    dispatcher.guard_worker_traversal(
        "lhm-claude-run-claude-gads-20260820-01", run_dir
    )
    assert (run_dir / "final.json").is_file()
    assert len(checks) == 3  # before, during persistence, and terminal verification


def test_lost_run_recovery_is_honest_and_idempotent(monkeypatch, tmp_path):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-01"
    run_dir.mkdir(parents=True)
    request = {
        "run_id": run_dir.name, "profile": "google_ads_readonly",
        "agent_id": "lhm-marketing-hub:google-ads",
    }
    request_bytes = (json.dumps(request, indent=2) + "\n").encode()
    (run_dir / "request.json").write_bytes(request_bytes)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *_args: None)

    dispatcher.recover_lost_run(run_dir.name, request_hash)
    final = json.loads((run_dir / "final.json").read_text())
    error = (run_dir / "error.txt").read_text()
    assert final["status"] == "failed"
    assert final["failure_reason"] == "lost_before_persistence"
    assert final["dedupe_key"] == f"{run_dir.name}:{request_hash}"
    assert "No analysis was recovered" in error
    first = (run_dir / "final.json").read_bytes()
    dispatcher.recover_lost_run(run_dir.name, request_hash)
    assert (run_dir / "final.json").read_bytes() == first


def test_lost_run_recovery_refuses_digest_mismatch_or_existing_result(monkeypatch, tmp_path):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-01"
    run_dir.mkdir(parents=True)
    (run_dir / "request.json").write_text('{"profile":"google_ads_readonly"}\n')
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    with pytest.raises(SystemExit, match="digest mismatch"):
        dispatcher.recover_lost_run(run_dir.name, "0" * 64)
    request_hash = hashlib.sha256((run_dir / "request.json").read_bytes()).hexdigest()
    (run_dir / "result.md").write_text("existing analysis\n")
    with pytest.raises(SystemExit, match="persisted analysis"):
        dispatcher.recover_lost_run(run_dir.name, request_hash)
