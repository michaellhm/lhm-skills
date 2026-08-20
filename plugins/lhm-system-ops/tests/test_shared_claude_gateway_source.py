import hashlib
import json
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((PLUGIN / "references/shared-claude-gateway-release.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def test_worker_persists_terminal_artifacts_inside_supplied_run_directory():
    text = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "run_dir = Path(sys.argv[1]).resolve()" in text
    assert "(run_dir / 'result.md').write_text" in text
    assert "(run_dir / 'final.json').write_text" in text
    assert "--strict-mcp-config" in text


def test_release_mapping_tracks_current_units_without_live_install_side_effects():
    for name in ("dispatch_unit", "gateway_acl_dropin"):
        item = MANIFEST["assets"][name]
        assert (PLUGIN / item["source"]).is_file()
        assert item["owner"] == item["group"] == "root"
        assert item["mode"] == "0644"
