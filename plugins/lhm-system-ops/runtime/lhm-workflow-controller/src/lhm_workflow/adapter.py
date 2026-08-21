from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path

from .secureio import UnsafeFile, read_trusted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--key", type=Path, default=Path("/var/lib/lhm-workflow/secrets/adapter.key"))
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--event-root", type=Path)
    parser.add_argument("--expected-source-uid", type=int, default=os.getuid())
    args = parser.parse_args()
    event_root = (args.event_root or args.source.parent).resolve()
    try:
        value = json.loads(read_trusted(args.source, root=event_root, uid=args.expected_source_uid))
    except (UnsafeFile, json.JSONDecodeError) as exc:
        raise SystemExit(f"unsafe source event: {exc}") from exc
    value.pop("adapter_attestation", None)
    runtime = (value.get("worker") or {}).get("runtime")
    expected_evidence_uid = os.getuid() if os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1" else {"claude": 10002, "codex": 10001, "lhm_host_verifier": 10006}.get(runtime)
    if expected_evidence_uid is None:
        raise SystemExit("unknown worker runtime")
    artifact_root = args.artifact_root or (args.output.parent / "artifacts")
    source_root = (args.source_root or (args.output.parent.parent / "worker")).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    for evidence in value.get("evidence", []):
        source = Path(evidence.get("path", ""))
        try:
            raw = read_trusted(source, root=source_root, uid=expected_evidence_uid)
        except UnsafeFile as exc:
            raise SystemExit(f"unsafe source evidence: {exc}") from exc
        observed = hashlib.sha256(raw).hexdigest()
        if observed != evidence.get("sha256"):
            raise SystemExit("source evidence digest mismatch")
        target = artifact_root / f"{observed}.evidence"
        if target.exists():
            try:
                existing = read_trusted(target, root=artifact_root, uid=os.getuid())
            except UnsafeFile as exc:
                raise SystemExit(f"unsafe existing artifact: {exc}") from exc
            if existing != raw:
                raise SystemExit("artifact digest collision or replacement")
        else:
            temporary_artifact = target.with_name(f".{target.name}.{os.getpid()}.tmp")
            temporary_artifact.write_bytes(raw)
            os.chmod(temporary_artifact, 0o640)
            os.replace(temporary_artifact, target)
        evidence["path"] = str(target)
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    value["adapter_attestation"] = hmac.new(args.key.read_bytes(), canonical, hashlib.sha256).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(temporary, 0o640)
    os.replace(temporary, args.output)


if __name__ == "__main__":
    main()
