from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .secureio import UnsafeFile, read_trusted

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")


class BridgeError(ValueError):
    pass


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _json(path: Path, *, root: Path, uid: int) -> dict:
    try:
        value = json.loads(read_trusted(path, root=root, uid=uid))
    except (json.JSONDecodeError, UnicodeDecodeError, UnsafeFile) as exc:
        raise BridgeError(str(exc)) from exc
    if not isinstance(value, dict):
        raise BridgeError("expected JSON object")
    return value


@dataclass(frozen=True)
class BridgeRoots:
    contracts: Path
    host_events: Path
    worker_results: Path
    adapter_source: Path
    processed: Path
    quarantine: Path


def build_receipt(contract: dict, events_raw: bytes, result: dict) -> dict:
    contract_hash = digest(contract)
    try:
        events = [json.loads(line) for line in events_raw.splitlines() if line.strip()]
    except json.JSONDecodeError as exc:
        raise BridgeError("invalid host event JSONL") from exc
    if not events:
        raise BridgeError("empty host event stream")
    required = {"parent_run_id", "child_run_id", "workflow_id", "stage_id", "idempotency_key", "worker", "required_skills", "required_capabilities", "expected_mutation_state"}
    if not required.issubset(contract) or not NAME.fullmatch(str(contract.get("child_run_id", ""))):
        raise BridgeError("invalid issued contract")
    if (not isinstance(contract.get("worker"), dict)
            or not isinstance(contract.get("required_skills"), list)
            or not contract["required_skills"]
            or not all(isinstance(item, str) and item for item in contract["required_skills"])
            or not isinstance(contract.get("required_capabilities"), list)
            or not all(isinstance(item, str) and item for item in contract["required_capabilities"])):
        raise BridgeError("invalid issued contract types")
    skills: list[str] = []
    capabilities: list[str] = []
    terminal = None
    admitted = False
    for index, event in enumerate(events, 1):
        if not isinstance(event, dict) or event.get("source") != "host-dispatcher":
            raise BridgeError("non-host event in protected stream")
        if event.get("seq") != index or event.get("child_run_id") != contract["child_run_id"] or event.get("contract_sha256") != contract_hash:
            raise BridgeError("host event binding or sequence mismatch")
        kind = event.get("event")
        if kind == "dispatch_admitted":
            if admitted or index != 1 or event.get("worker") != contract["worker"]:
                raise BridgeError("invalid dispatch admission")
            admitted = True
        elif kind == "skill_invoked":
            skills.append(event.get("skill"))
        elif kind == "capability_observed":
            capabilities.append(event.get("capability"))
        elif kind == "terminal":
            if terminal is not None or index != len(events):
                raise BridgeError("terminal event must occur exactly once at end")
            terminal = event.get("status")
        else:
            raise BridgeError("unknown protected host event")
    if not admitted or terminal != "completed":
        raise BridgeError("host dispatch did not complete")
    if skills != contract["required_skills"] or sorted(set(capabilities)) != sorted(contract["required_capabilities"]):
        raise BridgeError("host-observed skill or capability contract incomplete")
    if result.get("child_run_id") != contract["child_run_id"] or result.get("status") != "candidate":
        raise BridgeError("worker result binding or status mismatch")
    evidence = result.get("evidence")
    checks = result.get("checks")
    audit = result.get("mutation_audit")
    if not isinstance(evidence, list) or not evidence or not isinstance(checks, list) or not checks or not isinstance(audit, dict):
        raise BridgeError("worker result lacks candidate assurance")
    if audit.get("mutation_state") != contract["expected_mutation_state"]:
        raise BridgeError("worker result mutation state mismatch")
    receipt = {key: contract[key] for key in ("parent_run_id", "child_run_id", "workflow_id", "stage_id", "idempotency_key", "worker")}
    receipt.update({
        "schema_version": 1,
        "event": "stage_receipt",
        "event_id": f"receipt:{contract['child_run_id']}",
        "status": "candidate",
        "evidence": evidence,
        "host_provenance": {
            "observer": "host-dispatcher",
            "required_skills": contract["required_skills"],
            "observed_skill_calls": skills,
            "required_capabilities": contract["required_capabilities"],
            "observed_capabilities": sorted(set(capabilities)),
            "contract_sha256": contract_hash,
            "host_events_sha256": hashlib.sha256(events_raw).hexdigest(),
        },
        "checks": sorted(set(checks + ["host_event_binding", "host_skill_observation"])),
        "mutation_audit": audit,
        "bridge_input_sha256": digest({"contract": contract_hash, "events": hashlib.sha256(events_raw).hexdigest(), "result": digest(result)}),
    })
    return receipt


def atomic_idempotent(path: Path, value: dict, *, owner_uid: int, adapter_gid: int) -> None:
    payload = canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            existing = read_trusted(path, root=path.parent, uid=owner_uid)
        except UnsafeFile as exc:
            raise BridgeError(f"unsafe existing receipt: {exc}") from exc
        if existing == payload:
            return
        raise BridgeError("conflicting receipt already exists")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.chown(temporary, owner_uid, adapter_gid)
        os.chmod(temporary, 0o640)
        try:
            os.link(temporary, path)
        except FileExistsError:
            try:
                winner = read_trusted(path, root=path.parent, uid=owner_uid)
            except UnsafeFile as exc:
                raise BridgeError(f"unsafe receipt race winner: {exc}") from exc
            if winner != payload:
                raise BridgeError("conflicting receipt won output race")
    finally:
        Path(temporary).unlink(missing_ok=True)


def process_manifest(manifest: Path, roots: BridgeRoots, *, root_uid: int = 0, worker_uids: dict[str, int] | None = None, adapter_gid: int | None = None) -> Path | None:
    try:
        request = _json(manifest, root=manifest.parent, uid=root_uid)
        if set(request) != {"contract", "host_events", "worker_result"} or any(not NAME.fullmatch(str(value)) for value in request.values()):
            raise BridgeError("invalid bridge manifest")
        contract = _json(roots.contracts / request["contract"], root=roots.contracts, uid=root_uid)
        worker = contract.get("worker")
        if not isinstance(worker, dict) or not isinstance(worker.get("runtime"), str):
            raise BridgeError("invalid contract worker")
        runtime = worker["runtime"]
        allowed_worker_uids = worker_uids or {"claude": 10002, "codex": 10001, "lhm_host_verifier": 10006}
        worker_uid = allowed_worker_uids.get(runtime)
        if worker_uid is None:
            raise BridgeError("unrecognised contract worker runtime")
        events_path = roots.host_events / request["host_events"]
        try:
            events_raw = read_trusted(events_path, root=roots.host_events, uid=root_uid)
        except UnsafeFile as exc:
            raise BridgeError(str(exc)) from exc
        result = _json(roots.worker_results / request["worker_result"], root=roots.worker_results, uid=worker_uid)
        receipt = build_receipt(contract, events_raw, result)
        output = roots.adapter_source / f"{receipt['event_id'].replace(':', '_')}.json"
        atomic_idempotent(output, receipt, owner_uid=root_uid, adapter_gid=os.getgid() if adapter_gid is None else adapter_gid)
        marker = roots.processed / manifest.name
        marker.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(manifest), str(marker))
        return output
    except (OSError, BridgeError, TypeError, ValueError) as exc:
        roots.quarantine.mkdir(parents=True, exist_ok=True)
        target = roots.quarantine / manifest.name
        if manifest.exists():
            shutil.move(str(manifest), str(target))
        target.with_suffix(target.suffix + ".reason").write_text(str(exc)[:4000] + "\n")
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path("/var/lib/lhm-workflow"))
    parser.add_argument("--root-uid", type=int, default=0)
    parser.add_argument("--adapter-gid", type=int, required=True)
    args = parser.parse_args()
    base = args.root
    roots = BridgeRoots(base / "issued-contracts", base / "host-events", base / "worker-results", base / "adapter-source", base / "processed" / "bridge", base / "quarantine" / "bridge")
    if process_manifest(args.manifest, roots, root_uid=args.root_uid, adapter_gid=args.adapter_gid) is None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
