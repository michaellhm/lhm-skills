from __future__ import annotations

import argparse
import grp
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .controller import WorkflowController
from .host_bridge import BridgeRoots, process_manifest

ROOT = Path("/var/lib/lhm-workflow")


def bridge_scan() -> None:
    roots = BridgeRoots(ROOT / "issued-contracts", ROOT / "host-events", ROOT / "worker-results", ROOT / "adapter-source", ROOT / "processed" / "bridge", ROOT / "quarantine" / "bridge")
    adapter_gid = grp.getgrnam("lhmworkflowadapter").gr_gid
    for manifest in sorted((ROOT / "bridge-incoming").glob("*.json")):
        process_manifest(manifest, roots, root_uid=0, adapter_gid=adapter_gid)


def _finish(source: Path, bucket: str) -> None:
    target = ROOT / "processed" / bucket / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))


def _fail(source: Path, bucket: str, message: str) -> None:
    target = ROOT / "quarantine" / bucket / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        shutil.move(str(source), str(target))
    target.with_suffix(target.suffix + ".reason").write_text(message[:4000] + "\n")


def adapter_scan() -> None:
    incoming = ROOT / "adapter-source"
    for source in sorted(incoming.glob("*.json")):
        output = ROOT / "adapter-incoming" / source.name
        result = subprocess.run([
            sys.executable, "-m", "lhm_workflow.adapter", str(source), str(output),
            "--key", str(ROOT / "secrets" / "adapter.key"),
            "--source-root", str(ROOT / "worker"),
            "--event-root", str(ROOT / "adapter-source"),
            "--expected-source-uid", "0",
            "--artifact-root", str(ROOT / "adapter-incoming" / "artifacts"),
        ], text=True, capture_output=True)
        if result.returncode:
            _fail(source, "adapter", result.stderr or result.stdout)
        else:
            _finish(source, "adapter-source")


def stage_scan() -> None:
    controller = WorkflowController(ROOT)
    for source in sorted((ROOT / "adapter-incoming").glob("*.json")):
        try:
            controller.ingest_stage_file(source)
            _finish(source, "adapter-incoming")
        except Exception as exc:
            _fail(source, "stage", str(exc))


def verifier_scan() -> None:
    for source in sorted((ROOT / "verifier-requests").glob("*.json")):
        output = ROOT / "verifier-results" / source.name
        result = subprocess.run([
            sys.executable, "-m", "lhm_workflow.verifier", str(source), str(output),
            "--key", str(ROOT / "secrets" / "verifier.key"),
        ], text=True, capture_output=True)
        if result.returncode:
            _fail(source, "verifier", result.stderr or result.stdout)


def verification_scan() -> None:
    controller = WorkflowController(ROOT)
    for source in sorted((ROOT / "verifier-results").glob("*.json")):
        try:
            controller.ingest_verification(source)
            _finish(source, "verifier-results")
            request = ROOT / "verifier-requests" / source.name
            if request.exists():
                _finish(request, "verifier-requests")
        except Exception as exc:
            _fail(source, "verification", str(exc))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["bridge-scan", "adapter-scan", "stage-scan", "verifier-scan", "verification-scan"])
    command = parser.parse_args().command
    {"bridge-scan": bridge_scan, "adapter-scan": adapter_scan, "stage-scan": stage_scan, "verifier-scan": verifier_scan, "verification-scan": verification_scan}[command]()


if __name__ == "__main__":
    main()
