#!/usr/bin/env python3
"""Verify a meeting bundle approval and enqueue its exact reviewed Gmail draft."""

import hashlib
import json
import os
import re
import secrets
import shutil
from pathlib import Path

BASE = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch")
INCOMING = BASE / "gmail-approval-incoming"
PROCESSED = BASE / "gmail-approval-processed"
FAILED = BASE / "gmail-approval-failed"
GMAIL_INCOMING = BASE / "gmail-incoming"
RUNS = BASE / "meeting-runs"
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
GMAIL_ID = re.compile(r"^meeting-draft-[0-9]{8}-[0-9]{2}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_json(path, payload, mode=0o640, uid=0, gid=10000):
    temp = path.with_name(f".{path.name}.{secrets.token_hex(4)}")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.chown(temp, uid, gid)
    os.chmod(temp, mode)
    os.replace(temp, path)


def fail(path, approval_id, reason):
    if path.exists():
        shutil.move(path, FAILED / path.name)
    atomic_json(FAILED / f"{approval_id}.result.json", {
        "approval_id": approval_id, "status": "failed", "reason": str(reason)[:1000]
    })


def process(path):
    approval_id = path.stem
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        expected = {"schema_version", "approval_id", "source_run_id", "content_hash", "gmail_run_id", "operation", "approved_by", "approval_text"}
        if not isinstance(data, dict) or set(data) != expected:
            raise ValueError("Gmail approval request does not match closed schema")
        approval_id, source_run, gmail_run = data["approval_id"], data["source_run_id"], data["gmail_run_id"]
        if not SAFE_ID.fullmatch(approval_id) or not SAFE_ID.fullmatch(source_run) or not GMAIL_ID.fullmatch(gmail_run):
            raise ValueError("invalid approval, source, or Gmail run ID")
        if data["schema_version"] != 1 or data["operation"] != "create_gmail_draft":
            raise ValueError("unsupported Gmail approval operation")
        if data["approved_by"] != "Michael":
            raise ValueError("Michael approval is required")
        approval = data["approval_text"]
        if not isinstance(approval, str) or "approve" not in approval.lower() or "gmail" not in approval.lower() or "draft" not in approval.lower() or len(approval) > 1000:
            raise ValueError("explicit Gmail draft approval is required")
        content_hash = data["content_hash"]
        if not isinstance(content_hash, str) or not HASH.fullmatch(content_hash):
            raise ValueError("invalid content hash")
        final_path = RUNS / source_run / "final.json"
        if not final_path.is_file():
            raise ValueError("source meeting run is unavailable")
        final = json.loads(final_path.read_text(encoding="utf-8"))
        if final.get("status") != "needs_review" or final.get("content_hash") != content_hash:
            raise ValueError("source run status or content hash mismatch")
        result = final["result"]
        canonical = json.dumps({k: result[k] for k in ("email_draft", "meeting_record", "proposed_mutations")}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if digest(canonical) != content_hash:
            raise ValueError("review bundle content no longer matches its hash")
        email = result["email_draft"]
        recipients = email["to_suggestions"]
        if not isinstance(recipients, list) or not recipients or not all(isinstance(item, str) and EMAIL.fullmatch(item) for item in recipients):
            raise ValueError("reviewed recipient suggestions are not valid email addresses")
        if any((GMAIL_INCOMING / f"{gmail_run}.json").exists() for _ in [0]):
            raise ValueError("duplicate Gmail run ID")
        payload = {"schema_version": 1, "run_id": gmail_run, "operation": "create_draft",
                   "account": "michael@localhealthmarketing.com.au", "approved_by": "Michael",
                   "approval_text": approval, "to": recipients, "cc": [], "bcc": [],
                   "subject": email["subject"], "body": email["body"]}
        atomic_json(GMAIL_INCOMING / f"{gmail_run}.json", payload, mode=0o600, uid=10000, gid=10000)
        receipt = {"approval_id": approval_id, "source_run_id": source_run, "content_hash": content_hash,
                   "gmail_run_id": gmail_run, "status": "gmail_draft_queued", "to": recipients,
                   "subject": email["subject"]}
        atomic_json(PROCESSED / f"{approval_id}.result.json", receipt)
        shutil.move(path, PROCESSED / path.name)
    except Exception as exc:
        fail(path, approval_id, exc)


def main():
    for directory in (INCOMING, PROCESSED, FAILED, GMAIL_INCOMING):
        if not directory.exists():
            raise SystemExit(f"missing Gmail approval directory: {directory}")
    for path in sorted(INCOMING.glob("*.json")):
        process(path)


if __name__ == "__main__":
    main()
