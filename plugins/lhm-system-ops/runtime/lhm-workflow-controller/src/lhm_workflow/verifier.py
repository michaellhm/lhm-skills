from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--key", type=Path, default=Path("/var/lib/lhm-workflow/secrets/verifier.key"))
    args = parser.parse_args()
    request = json.loads(args.request.read_text())
    stage_event = json.loads(Path(request["receipt_path"]).read_text())
    stage_hash = canonical_digest(stage_event)
    if stage_hash != request["stage_event_sha256"]:
        raise SystemExit("stage event digest mismatch")
    evidence_ids = [stage_hash]
    for evidence in stage_event.get("evidence", []):
        path = Path(evidence["path"])
        if path.is_symlink() or not path.is_file():
            raise SystemExit("unsafe evidence")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != evidence["sha256"]:
            raise SystemExit("artifact digest mismatch")
        evidence_ids.append(observed)
    receipt = {
        "schema_version": 1,
        "event": "verification_receipt",
        "event_id": request["verification_id"],
        "parent_run_id": request["parent_run_id"],
        "child_run_id": request["child_run_id"],
        "workflow_id": request["workflow_id"],
        "stage_id": request["stage_id"],
        "verifier_identity": "lhmworkflowverify",
        "stage_event_sha256": stage_hash,
        "disposition": "verified",
        "checks": ["stage_event_digest", "workflow_binding", "artifact_hashes", "mutation_boundary"],
        "evidence_ids": evidence_ids,
        "mutation_audit": stage_event["mutation_audit"],
    }
    unsigned = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["verifier_attestation"] = hmac.new(args.key.read_bytes(), unsigned, hashlib.sha256).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(temporary, 0o640)
    os.replace(temporary, args.output)


if __name__ == "__main__":
    main()
