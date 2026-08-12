#!/usr/bin/env python3
"""Submit both hash-bound meeting approvals without exposing their JSON schemas to Hermes."""

import argparse
import json
import os
import re
import secrets
import tempfile
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/data/profiles/lhm_brain/dispatch")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
HASH = re.compile(r"^[0-9a-f]{64}$")


def queue(directory, item_id, payload):
    target_dir = BASE / directory
    fd, temp = tempfile.mkstemp(prefix=f".{item_id}.", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.chmod(temp, 0o600)
        os.replace(temp, target_dir / f"{item_id}.json")
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def available_gmail_id():
    prefix = f"meeting-draft-{datetime.now().strftime('%Y%m%d')}"
    directories = ("gmail-incoming", "gmail-processed", "gmail-failed")
    for number in range(1, 100):
        candidate = f"{prefix}-{number:02d}"
        if not any(any((BASE / directory).glob(f"{candidate}*")) for directory in directories):
            return candidate
    raise SystemExit("no Gmail draft run IDs available today")


def approve_both(args):
    if not SAFE_ID.fullmatch(args.source_run_id):
        raise SystemExit("invalid source run ID")
    if not HASH.fullmatch(args.content_hash):
        raise SystemExit("invalid content hash")
    text = args.approval_text.strip()
    lowered = text.lower()
    if len(text) > 1000 or "approve" not in lowered or "vault" not in lowered or "gmail" not in lowered or "draft" not in lowered:
        raise SystemExit("approval text must explicitly approve the vault changes and Gmail draft")

    suffix = secrets.token_hex(4)
    vault_id = f"meeting-vault-{suffix}"
    gmail_approval_id = f"meeting-gmail-{suffix}"
    gmail_run_id = available_gmail_id()
    common = {
        "schema_version": 1,
        "source_run_id": args.source_run_id,
        "content_hash": args.content_hash,
        "approved_by": "Michael",
        "approval_text": text,
    }
    queue("vault-apply-incoming", vault_id, {
        **common, "approval_id": vault_id, "operation": "apply_vault"
    })
    queue("gmail-approval-incoming", gmail_approval_id, {
        **common, "approval_id": gmail_approval_id, "gmail_run_id": gmail_run_id,
        "operation": "create_gmail_draft"
    })
    print(json.dumps({
        "status": "queued", "source_run_id": args.source_run_id,
        "content_hash": args.content_hash, "vault_approval_id": vault_id,
        "gmail_approval_id": gmail_approval_id, "gmail_run_id": gmail_run_id,
        "next": [
            f"meeting-vault-approval status {vault_id}",
            f"meeting-gmail-approval status {gmail_approval_id}",
            f"gmail-draft status {gmail_run_id}",
        ],
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(prog="meeting-approve")
    sub = parser.add_subparsers(dest="command", required=True)
    both = sub.add_parser("approve-both")
    both.add_argument("source_run_id")
    both.add_argument("content_hash")
    both.add_argument("approval_text")
    both.set_defaults(func=approve_both)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
