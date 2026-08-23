#!/usr/bin/env python3
"""Offline root-only recovery candidate for an admission-only site launch failure."""
from __future__ import annotations

import argparse, fcntl, json, os, re, shutil, stat, subprocess
from datetime import datetime, timezone
from pathlib import Path

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
DISPATCH = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch")
WORKFLOW = Path("/var/lib/lhm-workflow")
ROOT_UID = 0
WORKER_UID = 10001


def inactive(unit: str) -> bool:
    return subprocess.run(["systemctl", "is-active", "--quiet", unit]).returncode != 0

def trusted(path: Path, *, uid: int, directory: bool) -> None:
    info=path.lstat()
    wanted=stat.S_ISDIR if directory else stat.S_ISREG
    if path.is_symlink() or not wanted(info.st_mode) or info.st_uid != uid or info.st_mode & 0o022:
        raise SystemExit(f"unsafe recovery input: {path}")


def reconcile(child: str, *, dispatch: Path = DISPATCH, workflow: Path = WORKFLOW) -> Path:
    if os.geteuid() != 0 or not NAME.fullmatch(child):
        raise SystemExit("root and valid child id required")
    safe = re.sub(r"[^A-Za-z0-9_.-]", "-", child)
    lock_path=workflow/"host-events"/f"{child}.lock"
    trusted(lock_path,uid=ROOT_UID,directory=False)
    lock=lock_path.open("r+"); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    for unit in (f"lhm-site-run-{safe}.service", f"lhm-change-worker-{safe}.service"):
        if not inactive(unit):
            raise SystemExit(f"worker unit remains active: {unit}")
    events_path = workflow / "host-events" / f"{child}.jsonl"
    trusted(events_path,uid=ROOT_UID,directory=False)
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    if len(events) != 1 or events[0].get("event") != "dispatch_admitted":
        raise SystemExit("only admission-only failures are retryable; issue a new child id")
    run = dispatch / "site-runs" / child
    trusted(run,uid=WORKER_UID,directory=True)
    final = run / "final.json"
    if final.exists() and json.loads(final.read_text()).get("status") != "failed":
        raise SystemExit("run is not failed")
    processed = dispatch / "site-processed" / f"{child}.json"
    incoming = dispatch / "site-incoming" / f"{child}.json"
    if not processed.is_file() or incoming.exists():
        raise SystemExit("request is not in a uniquely recoverable processed state")
    trusted(processed,uid=ROOT_UID,directory=False)
    recovery_root=dispatch/"site-reconciliation"
    trusted(recovery_root,uid=ROOT_UID,directory=True)
    child_root=recovery_root/child
    if not child_root.exists(): os.mkdir(child_root,0o700)
    trusted(child_root,uid=ROOT_UID,directory=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = child_root / stamp
    os.mkdir(archive,0o700)
    trusted(archive,uid=ROOT_UID,directory=True)
    for name, source in (
        ("run", run),
        ("snapshot", dispatch / "site-snapshots" / child),
        ("draft", dispatch / "site-drafts" / child),
        ("artifacts", dispatch / "site-artifacts" / child),
    ):
        if source.exists():
            trusted(source,uid=WORKER_UID if name in {"run","draft"} else ROOT_UID,directory=True)
            shutil.move(str(source), archive / name)
    shutil.copy2(processed, archive / "request.json")
    shutil.move(str(processed), incoming)
    return archive


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("child")
    print(reconcile(parser.parse_args().child))


if __name__ == "__main__": main()
