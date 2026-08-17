import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from source_production_workflow import Workflow


def manifest():
    return {"schema_version": 1, "run_id": "replay-campaign-master-playbook", "parent_run_id": "parent-1",
            "saved_role": "Context and Research", "return_point": "context_research.acquire_required_sources",
            "source_policy": "all_required", "sources": [
                {"source_id": "strategy", "kind": "google_drive_file", "allowlisted_identifier": "fixture-drive-id", "required": True},
                {"source_id": "meeting", "kind": "fathom_transcript", "allowlisted_identifier": "fixture-fathom-id", "required": True}],
            "production": {"packaged_worker": "campaign-playbook-worker", "publisher": "registered_google_drive_publisher",
                           "destination_allowlisted_identifier": "fixture-destination-id"}}


def receipt(source):
    return {"schema_version": 1, "receipt_type": "retrieval", "source_id": source["source_id"], "kind": source["kind"],
            "identifier_sha256": hashlib.sha256(source["allowlisted_identifier"].encode()).hexdigest(),
            "content_sha256": hashlib.sha256((source["source_id"] + " redacted fixture").encode()).hexdigest(),
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "worker": "bounded-claude-research", "verified": True}


def test_all_required_rejects_missing_receipt(tmp_path):
    flow = Workflow(tmp_path); flow.create_parent(manifest())
    flow.record_receipt("parent-1", receipt(manifest()["sources"][0]))
    with pytest.raises(ValueError, match="all_required"):
        flow.evidence_package("parent-1")


def test_unavailable_persists_typed_cto_blocker_without_draft(tmp_path):
    flow = Workflow(tmp_path); state = flow.create_parent(manifest())
    blocker = flow.block("parent-1", "strategy", "google_drive_read_unavailable", "incident-1")
    assert blocker["route"] == "lhm-cto"
    assert state.get("evidence_package") is None
    assert (tmp_path / "incidents" / "incident-1.json").exists()


def test_restoration_is_exact_and_idempotent(tmp_path):
    flow = Workflow(tmp_path); flow.create_parent(manifest()); flow.block("parent-1", "strategy", "google_drive_read_unavailable", "incident-1")
    event = {"schema_version": 1, "event": "capability_restored", "event_id": "event-1", "capability_incident_id": "incident-1",
             "parent_run_id": "parent-1", "saved_role": "Context and Research", "return_point": "context_research.acquire_required_sources",
             "created_at": datetime.now(timezone.utc).isoformat()}
    assert flow.consume_capability_restored(event)["return_point"] == manifest()["return_point"]
    assert flow.consume_capability_restored(event) == {"outcome": "duplicate"}


def test_healthy_fixture_reaches_verified_drive_delivery(tmp_path):
    flow = Workflow(tmp_path); flow.create_parent(manifest())
    for source in manifest()["sources"]: flow.record_receipt("parent-1", receipt(source))
    package = flow.evidence_package("parent-1")
    assert len(package["receipt_digests"]) == 2
    content = hashlib.sha256(b"complete fixture production").hexdigest()
    delivery = {"schema_version": 1, "receipt_type": "drive_delivery", "parent_run_id": "parent-1",
                "publisher": "registered_google_drive_publisher",
                "destination_identifier_sha256": hashlib.sha256(b"fixture-destination-id").hexdigest(),
                "published_content_sha256": content, "read_back_content_sha256": content,
                "full_content_read_back": True, "verified_at": datetime.now(timezone.utc).isoformat()}
    assert flow.record_delivery("parent-1", delivery)["full_content_read_back"]
