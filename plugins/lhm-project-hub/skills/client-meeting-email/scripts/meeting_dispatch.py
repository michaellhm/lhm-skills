#!/usr/bin/env python3
"""Hermes-side submit/status/result helper for meeting capture."""

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
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not SAFE_ID.fullmatch(run_id):
        raise SystemExit("invalid run_id")
    incoming = BASE / "meeting-incoming"
    fd, temporary = tempfile.mkstemp(prefix=f".{run_id}.", dir=incoming)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, incoming / f"{run_id}.json")
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(json.dumps({"run_id": run_id, "status": "queued"}))


def checked(value):
    if not SAFE_ID.fullmatch(value):
        raise SystemExit("invalid run_id")
    return value


def status(args):
    run_id = checked(args.run_id)
    final = BASE / "meeting-runs" / run_id / "final.json"
    if final.is_file():
        data = json.loads(final.read_text(encoding="utf-8"))
        data.pop("result", None)
        print(json.dumps(data, indent=2))
        return
    events = BASE / "meeting-runs" / run_id / "events.jsonl"
    if events.is_file():
        lines = events.read_text(encoding="utf-8").splitlines()
        print(lines[-1] if lines else json.dumps({"run_id": run_id, "status": "queued"}))
        return
    error = BASE / "meeting-failed" / f"{run_id}.error"
    if error.is_file():
        print(json.dumps({"run_id": run_id, "status": "rejected", "reason": error.read_text().strip()}))
        return
    print(json.dumps({"run_id": run_id, "status": "pending_or_unknown"}))


def result(args):
    run_id = checked(args.run_id)
    final = BASE / "meeting-runs" / run_id / "final.json"
    if not final.is_file():
        raise SystemExit("result not ready")
    print(final.read_text(encoding="utf-8"), end="")


def main():
    parser = argparse.ArgumentParser(prog="meeting-dispatch")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("submit").set_defaults(func=submit)
    for name, function in (("status", status), ("result", result)):
        item = commands.add_parser(name)
        item.add_argument("run_id")
        item.set_defaults(func=function)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
