import hashlib
import json
import os
from pathlib import Path

import pytest

from lhm_workflow.client_preflight import ClientOnboardingRequired, require_capability
from lhm_workflow.org_canary import Canary, KEY_NAMES
from test_org_routing import cron


def _research(root: Path):
    def run(parent, contract, config):
        path = root / f"{parent}-research.md"
        path.write_text("bounded read-only evidence\n")
        path.chmod(0o600)
        artifact = {
            "artifact_id": f"{parent}:research",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "media_type": "text/markdown",
        }
        return artifact, path
    return run


def _config():
    return {
        "client_id": "example-client",
        "objective": "Read-only SEO evidence",
        "site_property": "sc-domain:example.test",
        "urls": ["https://example.test/a"],
        "completed_at": "2026-08-22T08:00:00Z",
        "content_required": False,
        "website_required": False,
    }


def test_evidence_bundle_contains_only_the_requested_parent(tmp_path):
    key = os.urandom(32)
    keys = {role: key for role in KEY_NAMES}
    canary = Canary(tmp_path, keys, research=_research(tmp_path), trusted_internal=True)
    # Prefix collision is intentional: substring-based scoping must not leak
    # bundle-parent-extra records into bundle-parent.
    for parent in ("bundle-parent:research-extra", "bundle-parent"):
        canary.initialise(cron(), parent)
        assert canary.run(parent, _config())["state"] == "closed"

    bundle = json.loads((tmp_path / "evidence/bundle-parent.json").read_text())
    encoded = json.dumps(bundle, sort_keys=True)
    assert "bundle-parent:research-extra" not in encoded
    assert len(bundle["operations"]) == len(bundle["parent"]["stages"])
    assert len(bundle["role-receipts"]) == len(bundle["parent"]["stages"])
    assert all("bundle-parent:" in name for name in bundle["mappings"])
    assert all("bundle-parent:" in name for name in bundle["requests"])
    assert all("bundle-parent:" in name for name in bundle["bridge_evidence"])


def _client_record(vault: Path, evidence: Path, *, evidence_sha256=None):
    record = vault / "_System/Hermes/clients/example-client/capabilities.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    value = {
        "client": {"id": "example-client"},
        "capabilities": {"google_search_console": {
            "status": "verified",
            "route": "seo_gsc_readonly",
            "identifiers": {"property": "sc-domain:example.test"},
            "allowed_operations": ["list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"],
            "last_test": {
                "at": "2026-08-22T08:00:00Z",
                "result": "passed",
                "mutation": "none",
                "evidence_ref": str(evidence),
                "evidence_sha256": evidence_sha256 or (hashlib.sha256(evidence.read_bytes()).hexdigest() if evidence.exists() else "0" * 64),
            },
        }},
    }
    record.write_text(json.dumps(value))
    record.chmod(0o600)
    return record


def _evidence(path: Path, property_name="sc-domain:example.test"):
    value = {
        "schema_version": 1,
        "parent": {"state": "closed", "delivery": {"channel": "suppressed_canary", "status": "suppressed"}},
        "requests": {"research.json": {"value": {
            "profile": "seo_gsc_readonly", "site_property": property_name,
            "required_capabilities": ["google_search_console.property_read"],
        }}},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))
    path.chmod(0o600)
    return path


def test_client_preflight_rejects_missing_evidence(tmp_path):
    vault = tmp_path / "vault"
    _client_record(vault, tmp_path / "missing-evidence.json")
    with pytest.raises(ClientOnboardingRequired, match="evidence"):
        require_capability(vault, "example-client", "google_search_console")


def test_client_preflight_rejects_wrong_evidence_hash(tmp_path):
    vault = tmp_path / "vault"; evidence = _evidence(tmp_path / "evidence.json")
    _client_record(vault, evidence, evidence_sha256="f" * 64)
    with pytest.raises(ClientOnboardingRequired, match="hash|evidence"):
        require_capability(vault, "example-client", "google_search_console")


def test_client_preflight_rejects_evidence_for_wrong_property(tmp_path):
    vault = tmp_path / "vault"; evidence = _evidence(tmp_path / "evidence.json", "sc-domain:other.test")
    _client_record(vault, evidence)
    with pytest.raises(ClientOnboardingRequired, match="property|evidence"):
        require_capability(vault, "example-client", "google_search_console")


def test_client_preflight_rejects_property_or_capability_only_in_unrelated_note(tmp_path):
    vault = tmp_path / "vault"; evidence = _evidence(tmp_path / "evidence.json", "sc-domain:other.test")
    value = json.loads(evidence.read_text())
    value["untrusted_note"] = {
        "property": "sc-domain:example.test",
        "words": "google_search_console.property_read seo_gsc_readonly",
    }
    evidence.write_text(json.dumps(value, sort_keys=True))
    _client_record(vault, evidence)
    with pytest.raises(ClientOnboardingRequired, match="property|binding|evidence"):
        require_capability(vault, "example-client", "google_search_console")


def test_client_preflight_rejects_linked_or_writable_record(tmp_path):
    vault = tmp_path / "vault"; evidence = _evidence(tmp_path / "evidence.json")
    real = _client_record(vault, evidence); target = real.with_name("capabilities-target.json")
    real.rename(target); real.symlink_to(target)
    with pytest.raises(ClientOnboardingRequired):
        require_capability(vault, "example-client", "google_search_console")

    real.unlink(); target.unlink(); real = _client_record(vault, evidence); real.chmod(0o660)
    with pytest.raises(ClientOnboardingRequired, match="unsafe|permission|record"):
        require_capability(vault, "example-client", "google_search_console")


@pytest.mark.skipif(os.geteuid() != 0, reason="ownership boundary requires Linux root")
def test_client_preflight_rejects_record_not_owned_by_fixed_vault_owner(tmp_path):
    vault = tmp_path / "vault"; evidence = _evidence(tmp_path / "evidence.json")
    _client_record(vault, evidence); os.chown(vault, 65534, -1)
    with pytest.raises(ClientOnboardingRequired, match="owner|unsafe|record"):
        require_capability(vault, "example-client", "google_search_console")
