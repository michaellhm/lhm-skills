#!/usr/bin/env python3
"""Hermes helper for hash-bound Gmail draft approvals."""

import argparse
import json
import os
import re
import tempfile
from pathlib import Path

BASE = Path("/opt/data/profiles/lhm_brain/dispatch")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")


def submit(_):
    data = json.load(__import__("sys").stdin)
    approval_id = data.get("approval_id")
    if not isinstance(approval_id, str) or not SAFE_ID.fullmatch(approval_id):
        raise SystemExit("invalid approval_id")
    incoming = BASE / "gmail-approval-incoming"
    fd, temp = tempfile.mkstemp(prefix=f".{approval_id}.", dir=incoming)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        os.chmod(temp, 0o600)
        os.replace(temp, incoming / f"{approval_id}.json")
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(json.dumps({"approval_id": approval_id, "status": "queued"}))


def status(args):
    if not SAFE_ID.fullmatch(args.approval_id):
        raise SystemExit("invalid approval_id")
    for directory in ("gmail-approval-processed", "gmail-approval-failed"):
        result = BASE / directory / f"{args.approval_id}.result.json"
        if result.is_file():
            print(result.read_text(encoding="utf-8"), end="")
            return
    print(json.dumps({"approval_id": args.approval_id, "status": "pending_or_unknown"}))


def main():
    parser = argparse.ArgumentParser(prog="meeting-gmail-approval")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("submit").set_defaults(func=submit)
    item = sub.add_parser("status")
    item.add_argument("approval_id")
    item.set_defaults(func=status)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
