#!/usr/bin/env python3
"""Durable, fail-closed source-to-production state machine.

This module is deliberately connector-neutral. Privileged host workers supply retrieval and
publication receipts; Hermes may only create/resume manifests and consume verified receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_KINDS = {"google_drive_file", "fathom_transcript"}
BLOCKER_KINDS = {"google_drive_read_unavailable", "fathom_read_unavailable"}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.chmod(temporary, 0o640)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_manifest(manifest):
    required = {"schema_version", "run_id", "parent_run_id", "saved_role", "return_point",
                "source_policy", "sources", "production"}
    if set(manifest) != required or manifest["schema_version"] != 1:
        raise ValueError("invalid source workflow manifest schema")
    if manifest["source_policy"] != "all_required":
        raise ValueError("source_policy must be all_required")
    ids = set()
    for source in manifest["sources"]:
        if set(source) != {"source_id", "kind", "allowlisted_identifier", "required"}:
            raise ValueError("invalid source declaration")
        if source["kind"] not in SOURCE_KINDS or source["required"] is not True:
            raise ValueError("unsupported or optional source")
        if not source["allowlisted_identifier"] or source["source_id"] in ids:
            raise ValueError("invalid source identifier")
        ids.add(source["source_id"])
    production = manifest["production"]
    if set(production) != {"packaged_worker", "publisher", "destination_allowlisted_identifier"}:
        raise ValueError("invalid production declaration")
    if production["publisher"] != "registered_google_drive_publisher":
        raise ValueError("unregistered publisher")
    return manifest


def validate_retrieval_receipt(receipt, source):
    keys = {"schema_version", "receipt_type", "source_id", "kind", "identifier_sha256",
            "content_sha256", "retrieved_at", "worker", "verified"}
    if set(receipt) != keys or receipt["schema_version"] != 1 or receipt["receipt_type"] != "retrieval":
        raise ValueError("invalid retrieval receipt")
    if receipt["verified"] is not True or receipt["source_id"] != source["source_id"] or receipt["kind"] != source["kind"]:
        raise ValueError("unverified or mismatched retrieval receipt")
    expected = hashlib.sha256(str(source["allowlisted_identifier"]).encode()).hexdigest()
    if receipt["identifier_sha256"] != expected or len(receipt["content_sha256"]) != 64:
        raise ValueError("retrieval receipt digest mismatch")
    return receipt


class Workflow:
    def __init__(self, root: Path):
        self.root = root

    def create_parent(self, manifest):
        validate_manifest(manifest)
        path = self.root / "parents" / f"{manifest['parent_run_id']}.json"
        if path.exists():
            existing = json.loads(path.read_text())
            if existing["manifest_sha256"] != _digest(manifest):
                raise ValueError("parent_run_id already has a different manifest")
            return existing
        state = {"status": "acquiring_sources", "manifest": manifest,
                 "manifest_sha256": _digest(manifest), "receipts": {}, "created_at": _now()}
        atomic_json(path, state)
        return state

    def record_receipt(self, parent_id, receipt):
        path = self.root / "parents" / f"{parent_id}.json"
        state = json.loads(path.read_text())
        source = next((s for s in state["manifest"]["sources"] if s["source_id"] == receipt.get("source_id")), None)
        if not source:
            raise ValueError("receipt source is not allowlisted")
        validate_retrieval_receipt(receipt, source)
        state["receipts"][source["source_id"]] = receipt
        atomic_json(path, state)

    def block(self, parent_id, source_id, blocker_kind, incident_id):
        if blocker_kind not in BLOCKER_KINDS:
            raise ValueError("invalid capability blocker")
        path = self.root / "parents" / f"{parent_id}.json"
        state = json.loads(path.read_text())
        source = next((s for s in state["manifest"]["sources"] if s["source_id"] == source_id), None)
        if not source:
            raise ValueError("blocked source is not allowlisted")
        blocker = {"schema_version": 1, "type": "capability_blocker", "blocker_kind": blocker_kind,
                   "capability_incident_id": incident_id, "parent_run_id": parent_id,
                   "saved_role": state["manifest"]["saved_role"],
                   "return_point": state["manifest"]["return_point"], "source_id": source_id,
                   "route": "lhm-cto", "created_at": _now()}
        state.update(status="blocked", blocker=blocker)
        atomic_json(path, state)
        atomic_json(self.root / "incidents" / f"{incident_id}.json", blocker)
        return blocker

    def consume_capability_restored(self, event):
        required = {"schema_version", "event", "event_id", "capability_incident_id", "parent_run_id",
                    "saved_role", "return_point", "created_at"}
        if set(event) != required or event["schema_version"] != 1 or event["event"] != "capability_restored":
            raise ValueError("invalid capability_restored event")
        marker = self.root / "consumed" / f"{event['event_id']}.json"
        if marker.exists():
            return {"outcome": "duplicate"}
        path = self.root / "parents" / f"{event['parent_run_id']}.json"
        state = json.loads(path.read_text())
        blocker = state.get("blocker", {})
        for key in ("capability_incident_id", "parent_run_id", "saved_role", "return_point"):
            if event[key] != blocker.get(key):
                raise ValueError(f"capability restoration mismatch: {key}")
        resume = {"outcome": "resumed", "parent_run_id": event["parent_run_id"],
                  "role": event["saved_role"], "return_point": event["return_point"]}
        atomic_json(marker, {**event, "consumed_at": _now()})
        state.update(status="acquiring_sources", last_resume=resume)
        state.pop("blocker", None)
        atomic_json(path, state)
        return resume

    def evidence_package(self, parent_id):
        path = self.root / "parents" / f"{parent_id}.json"
        state = json.loads(path.read_text())
        manifest = state["manifest"]
        missing = []
        for source in manifest["sources"]:
            receipt = state["receipts"].get(source["source_id"])
            if not receipt:
                missing.append(source["source_id"])
            else:
                validate_retrieval_receipt(receipt, source)
        if missing:
            raise ValueError("all_required sources lack verified retrieval receipts: " + ", ".join(missing))
        package = {"schema_version": 1, "package_type": "verified_evidence", "parent_run_id": parent_id,
                   "receipt_digests": {k: _digest(v) for k, v in sorted(state["receipts"].items())},
                   "validated_at": _now()}
        package["package_sha256"] = _digest(package)
        state.update(status="production_ready", evidence_package=package,
                     production_child={"role": "Head of Production", "worker": manifest["production"]["packaged_worker"],
                                       "status": "created"})
        atomic_json(path, state)
        return package

    def record_delivery(self, parent_id, receipt):
        required = {"schema_version", "receipt_type", "parent_run_id", "publisher", "destination_identifier_sha256",
                    "published_content_sha256", "read_back_content_sha256", "full_content_read_back", "verified_at"}
        if set(receipt) != required or receipt["receipt_type"] != "drive_delivery" or receipt["schema_version"] != 1:
            raise ValueError("invalid delivery receipt")
        path = self.root / "parents" / f"{parent_id}.json"
        state = json.loads(path.read_text())
        production = state["manifest"]["production"]
        expected = hashlib.sha256(production["destination_allowlisted_identifier"].encode()).hexdigest()
        if (receipt["parent_run_id"] != parent_id or receipt["publisher"] != production["publisher"] or
                receipt["destination_identifier_sha256"] != expected or receipt["full_content_read_back"] is not True or
                receipt["published_content_sha256"] != receipt["read_back_content_sha256"]):
            raise ValueError("delivery was not fully read back and verified")
        state.update(status="delivered", delivery_receipt=receipt)
        atomic_json(path, state)
        return receipt
