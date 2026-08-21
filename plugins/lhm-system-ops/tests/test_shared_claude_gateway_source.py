import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
import subprocess
import types
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((PLUGIN / "references/shared-claude-gateway-release.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_shared_gateway_sources_match_verified_inventory():
    assert MANIFEST["capability_id"] == "CAP-015"
    assert MANIFEST["release_version"] == "0.8.7"
    for name in MANIFEST["assets"]:
        item = MANIFEST["assets"][name]
        source = PLUGIN / item["source"]
        assert source.is_file()
        if "size_bytes" in item:
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
    assert "'/usr/sbin/runuser', '--user', 'claudeworker'" in text
    assert "/usr/local/libexec/lhm-claude-worker" in text
    assert "google_ads_readonly" in text
    assert "Path('/home/hermes/.hermes')," in text
    assert "Path('/home/hermes/.hermes/profiles/lhm_brain')," in text
    assert "'u:claudeworker:rwx', str(run_dir)" in text
    assert "setfacl', '-R'" not in text
    assert "def load_google_ads_evidence(client):" in text
    assert "expected_prefix = client['evidence_prefix']" in text
    assert "registered evidence pack exceeds total limit" in text
    assert "prompt['evidence_pack'] = load_google_ads_evidence(client)" in text
    assert "required_timeout = admitted_timeout_seconds(profile)" in text


def test_google_ads_profile_admits_only_extended_bounded_timeout():
    dispatcher = load_dispatcher()
    assert dispatcher.admitted_timeout_seconds("google_ads_readonly") == 600
    assert 300 != dispatcher.admitted_timeout_seconds("google_ads_readonly")
    assert dispatcher.admitted_timeout_seconds("handback_target_registration") == 30
    assert dispatcher.admitted_timeout_seconds("html_artifact_producer") == 1200


def test_google_ads_runtime_extension_preserves_readonly_tool_and_budget_ceiling():
    worker = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "if is_marketing else ('12', '2.00')" in worker
    assert "if is_marketing else 'Skill'" in worker
    assert "google-ads-readonly.mcp.json" in worker
    assert "mcp__GoogleAds__execute_gaql" in worker
    for forbidden in ("mcp__GoogleAds__mutate", "Bash", "WebFetch", "WebSearch"):
        assert forbidden not in worker


def test_worker_persists_terminal_artifacts_inside_supplied_run_directory():
    text = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "run_dir = Path(sys.argv[1]).resolve()" in text
    assert "(run_dir / 'result.md').write_text" in text
    assert "(run_dir / 'final.json').write_text" in text
    assert "--strict-mcp-config" in text
    assert "The evidence pack is host-validated reference material" in text
    assert "Canonical reconciliation evidence supplied by Hermes" in text
    assert "provisioned_tools = 'Agent,Skill' if is_marketing else 'Skill'" in text


def test_google_ads_evidence_pack_is_bounded_hashed_and_client_scoped(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    vault = tmp_path / "vault"
    allowed = vault / "20 Clients/Any Stage Physio/project-management/Google Ads.md"
    allowed.parent.mkdir(parents=True)
    allowed.write_text("canonical commitments\n")
    monkeypatch.setattr(dispatcher, "VAULT", vault)
    client = {
        "name": "Any Stage Physio",
        "evidence_prefix": "20 Clients/Any Stage Physio/",
        "evidence_files": ["20 Clients/Any Stage Physio/project-management/Google Ads.md"],
    }
    pack = dispatcher.load_google_ads_evidence(client)
    assert pack == [{
        "path": "20 Clients/Any Stage Physio/project-management/Google Ads.md",
        "sha256": hashlib.sha256(b"canonical commitments\n").hexdigest(),
        "content": "canonical commitments\n",
    }]

    client["evidence_files"] = ["20 Clients/Another Client/project-management/Google Ads.md"]
    other = vault / client["evidence_files"][0]
    other.parent.mkdir(parents=True)
    other.write_text("wrong client\n")
    # Registry validation is the first scope boundary; the loader independently
    # remains confined to the vault root for already validated registrations.
    monkeypatch.setattr(dispatcher, "CLIENT_REGISTRY", tmp_path / "clients.json")
    dispatcher.CLIENT_REGISTRY.write_text(json.dumps({"clients": {"any-stage-physio": {
        "name": "Any Stage Physio", "customer_id": "5308308105", "manager_id": "3947361921",
        "evidence_prefix": "20 Clients/Any Stage Physio/",
        "evidence_files": client["evidence_files"],
    }}}))
    try:
        dispatcher.load_clients()
    except SystemExit as exc:
        assert "outside registered scope" in str(exc)
    else:
        raise AssertionError("cross-client evidence registration was accepted")


def test_evidence_prefix_is_independent_of_client_display_name(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    registry = tmp_path / "clients.json"
    registry.write_text(json.dumps({"clients": {"mhealth": {
        "name": "mhealth", "customer_id": "2228366786", "manager_id": "3947361921",
        "evidence_prefix": "20 Clients/Mhealth/",
        "evidence_files": ["20 Clients/Mhealth/project-management/Google Ads.md"],
    }}}))
    monkeypatch.setattr(dispatcher, "CLIENT_REGISTRY", registry)
    assert dispatcher.load_clients()["mhealth"]["evidence_prefix"] == "20 Clients/Mhealth/"


def test_release_mapping_tracks_current_units_without_live_install_side_effects():
    for name in ("dispatch_unit", "gateway_acl_dropin"):
        item = MANIFEST["assets"][name]
        assert (PLUGIN / item["source"]).is_file()
        assert item["owner"] == item["group"] == "root"
        assert item["mode"] == "0644"


def load_dispatcher():
    path = PLUGIN / MANIFEST["assets"]["dispatcher"]["source"]
    spec = importlib.util.spec_from_loader("shared_dispatcher", SourceFileLoader("shared_dispatcher", str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mask_reset_mid_run_is_repaired_and_terminal_artifacts_persist(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-99"
    ancestor_a = tmp_path / "hermes"
    ancestor_b = ancestor_a / "brain"
    run_dir.mkdir(parents=True)
    ancestor_b.mkdir(parents=True)
    (run_dir / "prompt.json").write_text(json.dumps({"profile": "google_ads_readonly", "agent_id": "lhm-marketing-hub:google-ads"}))
    (run_dir / "events.jsonl").write_text("{}\n")
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher, "WORKER_TRAVERSAL_ANCESTORS", (ancestor_a, ancestor_b))
    monkeypatch.setattr(dispatcher, "ACL_POLL_SECONDS", 0)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    calls = {"ensure": 0}
    real_run = subprocess.run

    def ensure():
        calls["ensure"] += 1
        if calls["ensure"] == 3:
            real_run(["setfacl", "-m", "m::---", str(ancestor_a), str(ancestor_b)], check=True)
        # This workspace filesystem permits mask mutation but not named-user ACLs;
        # the tracked-command assertions above cover the exact claudeworker entry.
        real_run(["setfacl", "-m", "m::--x", str(ancestor_a), str(ancestor_b)], check=True)

    class Worker:
        def __init__(self):
            self.polls = 0
        def poll(self):
            self.polls += 1
            if self.polls < 4:
                return None
            (run_dir / "result.md").write_text("honest result\n")
            (run_dir / "final.json").write_text('{"status":"needs_review"}\n')
            with (run_dir / "events.jsonl").open("a") as handle:
                handle.write('{"event":"completed"}\n')
            return 0
        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(dispatcher, "ensure_worker_traversal", ensure)
    monkeypatch.setattr(dispatcher, "subprocess", types.SimpleNamespace(
        Popen=lambda command: Worker(), CalledProcessError=subprocess.CalledProcessError,
        TimeoutExpired=subprocess.TimeoutExpired))
    assert dispatcher.supervise_worker(run_dir, 300) == 0
    assert calls["ensure"] >= 4
    acl = real_run(["getfacl", "--absolute-names", str(ancestor_a), str(ancestor_b)], check=True, capture_output=True, text=True).stdout
    assert acl.count("mask::--x") == 2
    assert (run_dir / "result.md").read_text() == "honest result\n"
    assert json.loads((run_dir / "final.json").read_text())["status"] == "needs_review"
    assert '"event":"completed"' in (run_dir / "events.jsonl").read_text()


def test_acl_repair_failure_terminates_worker_and_persists_explicit_failure(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-98"
    run_dir.mkdir(parents=True)
    (run_dir / "prompt.json").write_text(json.dumps({"profile": "google_ads_readonly", "agent_id": "lhm-marketing-hub:google-ads"}))
    (run_dir / "events.jsonl").write_text("{}\n")
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher, "ACL_POLL_SECONDS", 0)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    calls = {"ensure": 0}
    def ensure():
        calls["ensure"] += 1
        if calls["ensure"] > 1:
            raise subprocess.CalledProcessError(1, ["setfacl"])
    class Worker:
        def poll(self): return None
        def terminate(self): pass
        def wait(self, timeout=None): return -15
    monkeypatch.setattr(dispatcher, "ensure_worker_traversal", ensure)
    monkeypatch.setattr(dispatcher, "subprocess", types.SimpleNamespace(
        Popen=lambda command: Worker(), CalledProcessError=subprocess.CalledProcessError,
        TimeoutExpired=subprocess.TimeoutExpired))
    assert dispatcher.supervise_worker(run_dir, 300) == 1
    final = json.loads((run_dir / "final.json").read_text())
    assert final["status"] == "failed"
    assert "failed closed" in final["error"]
