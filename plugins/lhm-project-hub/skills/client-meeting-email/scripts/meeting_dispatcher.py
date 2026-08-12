#!/usr/bin/env python3
"""Validate and dispatch review-only client meeting capture jobs."""

import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
from pathlib import Path

BASE = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch")
INCOMING = BASE / "meeting-incoming"
PROCESSED = BASE / "meeting-processed"
FAILED = BASE / "meeting-failed"
RUNS = BASE / "meeting-runs"
SNAPSHOTS = BASE / "meeting-snapshots"
REGISTRY = Path("/etc/lhm-codex/clients")
VAULT = Path("/home/hermes/.hermes/profiles/lhm_brain/vault")
SKILL = Path("/home/codexworker/lhm-skills-marketplace/plugins/lhm-project-hub/skills/client-meeting-email")
WORKER_UID = 10001
WORKER_GID = 10001
HERMES_GID = 10000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
CLIENT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED_FIELDS = {
    "workflow_id", "workflow_version", "run_id", "worker_route", "client_id",
    "meeting_locator", "evidence_mode", "evidence_package", "founder_context",
    "requested_outputs", "permissions", "approval_stage", "success_test",
    "timeout_seconds",
}


def atomic_text(path, text, mode=0o640, uid=0, gid=HERMES_GID):
    temp = path.with_name(f".{path.name}.{secrets.token_hex(4)}")
    temp.write_text(text, encoding="utf-8")
    os.chown(temp, uid, gid)
    os.chmod(temp, mode)
    os.replace(temp, path)


def reject(path, reason):
    FAILED.mkdir(parents=True, exist_ok=True)
    target = FAILED / path.name
    if target.exists():
        target = FAILED / f"{path.stem}-{secrets.token_hex(3)}.json"
    shutil.move(path, target)
    atomic_text(target.with_suffix(".error"), reason[:1000] + "\n")


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_request(data, filename):
    if not isinstance(data, dict) or set(data) != EXPECTED_FIELDS:
        raise ValueError("request does not match the closed field set")
    if data["workflow_id"] != "client_meeting_capture" or data["workflow_version"] != 1:
        raise ValueError("unsupported workflow")
    run_id = data["run_id"]
    if not isinstance(run_id, str) or not SAFE_ID.fullmatch(run_id) or filename != run_id + ".json":
        raise ValueError("invalid run identity")
    if data["worker_route"] != "codex" or data["approval_stage"] != "review_only":
        raise ValueError("invalid worker or approval stage")
    client_id = data["client_id"]
    if not isinstance(client_id, str) or not CLIENT_ID.fullmatch(client_id):
        raise ValueError("invalid client ID")
    permissions = data["permissions"]
    expected_permissions = {
        "read_fathom": True, "read_client_context": True, "stage_artifacts": True,
        "apply_vault": False, "create_gmail_draft": False, "basicops": False,
    }
    if permissions != expected_permissions:
        raise ValueError("preparation permissions must be exact and mutation-free")
    if data["evidence_mode"] != "compatibility_relay":
        raise ValueError("worker Fathom mode is not authorised yet")
    evidence = data["evidence_package"]
    if not isinstance(evidence, dict) or set(evidence) != {
        "meeting", "summary", "transcript", "retrieved_at", "summary_sha256", "transcript_sha256"
    }:
        raise ValueError("invalid compatibility evidence package")
    summary, transcript = evidence["summary"], evidence["transcript"]
    if not isinstance(summary, str) or not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("complete transcript evidence is required")
    if sha256(summary) != evidence["summary_sha256"] or sha256(transcript) != evidence["transcript_sha256"]:
        raise ValueError("evidence hash mismatch")
    timeout = data["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 60 <= timeout <= 1800:
        raise ValueError("invalid timeout")
    tests = data["success_test"]
    if not isinstance(tests, list) or not 1 <= len(tests) <= 15 or not all(isinstance(x, str) and x for x in tests):
        raise ValueError("invalid success tests")


def load_client(client_id):
    path = REGISTRY / f"{client_id}.json"
    if not path.is_file() or path.is_symlink():
        raise ValueError("unregistered client")
    stat = path.stat()
    if stat.st_uid != 0 or stat.st_mode & 0o022:
        raise ValueError("unsafe client registry entry")
    profile = json.loads(path.read_text(encoding="utf-8"))
    if set(profile) != {"schema_version", "client_id", "enabled", "vault_relative_root", "allowed_context_files"}:
        raise ValueError("invalid client registry schema")
    if profile["schema_version"] != 1 or profile["client_id"] != client_id or profile["enabled"] is not True:
        raise ValueError("client registry mismatch")
    root = (VAULT / profile["vault_relative_root"]).resolve()
    if VAULT.resolve() not in root.parents or not root.is_dir() or root.is_symlink():
        raise ValueError("invalid registered client root")
    return profile, root


def readonly_tree(root):
    for current, _, files in os.walk(root):
        current = Path(current)
        os.chown(current, 0, WORKER_GID)
        os.chmod(current, 0o550)
        for name in files:
            item = current / name
            os.chown(item, 0, WORKER_GID)
            os.chmod(item, 0o440)


def process(path):
    try:
        if path.stat().st_size > 3_000_000:
            raise ValueError("request too large")
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_request(data, path.name)
        profile, client_root = load_client(data["client_id"])
        run_dir = RUNS / data["run_id"]
        snapshot_root = SNAPSHOTS / data["run_id"]
        if run_dir.exists() or snapshot_root.exists():
            raise ValueError("duplicate run ID")
        run_dir.mkdir(mode=0o2750)
        os.chown(run_dir, WORKER_UID, WORKER_GID)
        snapshot_root.mkdir(mode=0o550)
        os.chown(snapshot_root, 0, WORKER_GID)
        client_snapshot = snapshot_root / "client"
        skill_snapshot = snapshot_root / "skill"
        client_snapshot.mkdir(mode=0o550)
        for relative in profile["allowed_context_files"]:
            source = (client_root / relative).resolve()
            if client_root not in source.parents or not source.is_file() or source.is_symlink():
                raise ValueError(f"invalid registered context file: {relative}")
            destination = client_snapshot / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        shutil.copytree(SKILL, skill_snapshot, symlinks=False)
        readonly_tree(snapshot_root)
        atomic_text(run_dir / "request.json", json.dumps(data, indent=2) + "\n", 0o440, 0, WORKER_GID)
        atomic_text(run_dir / "client-profile.json", json.dumps(profile, indent=2) + "\n", 0o440, 0, WORKER_GID)
        shutil.copy2(skill_snapshot / "references/output-schema.json", run_dir / "output-schema.json")
        os.chown(run_dir / "output-schema.json", 0, WORKER_GID)
        os.chmod(run_dir / "output-schema.json", 0o440)
        atomic_text(run_dir / "events.jsonl", json.dumps({"event": "queued", "run_id": data["run_id"]}) + "\n", 0o640, WORKER_UID)
        unit_id = re.sub(r"[^A-Za-z0-9_.-]", "-", data["run_id"])
        runtime_run = Path("/run/lhm-meeting-run")
        runtime_snapshot = Path("/run/lhm-meeting-snapshot")
        runtime_run.mkdir(mode=0o755, exist_ok=True)
        runtime_snapshot.mkdir(mode=0o755, exist_ok=True)
        command = [
            "systemd-run", "--quiet", f"--unit=lhm-meeting-run-{unit_id}",
            "--uid=codexworker", "--gid=codexworker", "--property=Type=oneshot",
            "--property=NoNewPrivileges=yes", "--property=PrivateTmp=yes",
            "--property=ProtectSystem=strict", "--property=ProtectHome=read-only",
            "--property=RestrictSUIDSGID=yes", "--property=UMask=0027",
            f"--property=BindPaths={run_dir}:{runtime_run}",
            f"--property=BindReadOnlyPaths={snapshot_root}:{runtime_snapshot}",
            "--property=ReadWritePaths=/run/lhm-meeting-run /home/codexworker/.codex",
            "/usr/local/libexec/lhm-meeting-worker", str(runtime_run), str(runtime_snapshot), str(data["timeout_seconds"]),
        ]
        subprocess.run(command, check=True)
        shutil.move(path, PROCESSED / path.name)
    except Exception as exc:
        reject(path, str(exc))


def main():
    for directory in (INCOMING, PROCESSED, FAILED, RUNS, SNAPSHOTS):
        if not directory.exists():
            raise SystemExit(f"missing dispatch directory: {directory}")
    for path in sorted(INCOMING.glob("*.json")):
        process(path)


if __name__ == "__main__":
    main()
