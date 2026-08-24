"""Durable, disabled-by-default executor for registered scheduled parents.

Bots receive bounded snapshots and write closed JSON results.  They never receive signing
keys, tracker write access, deployment authority, or Search Console mutation authority.
"""
from __future__ import annotations

import hashlib
import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable

from .org_routing import ROLE_POLICY, Router, digest
from .scheduled_work import normalise_urls

DEFAULT_ROOT = Path("/var/lib/lhm-workflow")
URL = re.compile(r"(?:https://localhealthmarketing\.com)?/[A-Za-z0-9][A-Za-z0-9_./-]*")
BOT_STAGES = {"chief_intake", "context", "research", "production_plan", "seo_plan", "seo_accept", "content", "website", "production_closeout", "chief_handback", "learning"}


def atomic_json(path: Path, value: object, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":")); handle.write("\n")
            handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, mode); os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def artifact(path: Path, artifact_id: str) -> dict:
    data = path.read_bytes()
    return {"artifact_id": artifact_id, "path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "media_type": "application/json"}


def snapshot_sources(paths: list[str], destination: Path, site: str) -> tuple[list[dict], list[str]]:
    """Copy only registered source bytes and derive same-property URLs on every run."""
    records, candidates = [], []
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    selected: list[Path] = []
    for raw in paths:
        source = Path(raw)
        selected.extend(sorted(p for p in source.iterdir() if p.name in {"rollout-state.md", "sitemap.json", "LHM-Proposed-Sitemap.html"})) if source.is_dir() else selected.append(source)
    for index, source in enumerate(selected):
        if source.is_symlink() or not source.is_file(): raise ValueError("canonical source is not a regular file")
        data = source.read_bytes(); target = destination / f"source-{index:02d}{source.suffix}"
        target.write_bytes(data); target.chmod(0o600)
        if target.read_bytes() != data: raise ValueError("canonical snapshot readback mismatch")
        records.append({"source_path": str(source), **artifact(target, f"canonical-source-{index:02d}")})
        candidates.extend(match.group(0) for match in URL.finditer(data.decode("utf-8", errors="ignore")))
    urls = normalise_urls(site, candidates)
    if not urls: raise ValueError("canonical sources yielded no registered-property URLs")
    return records, urls


def compare_and_swap_tracker(path: Path, expected_sha256: str, replacement: bytes) -> dict:
    """Perform the only tracker mutation, with precondition and full byte readback."""
    before = path.read_bytes()
    if hashlib.sha256(before).hexdigest() != expected_sha256: raise ValueError("tracker compare-and-swap conflict")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(replacement); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777); os.replace(temporary, path)
    finally: Path(temporary).unlink(missing_ok=True)
    if path.read_bytes() != replacement: raise ValueError("tracker full readback mismatch")
    return {"before_sha256": expected_sha256, "after_sha256": hashlib.sha256(replacement).hexdigest(), "readback": True}


class ScheduledExecutor:
    def __init__(self, root: Path = DEFAULT_ROOT, *, runner: Callable = subprocess.run, test_mode: bool = False):
        self.root, self.runner, self.test_mode = root, runner, test_mode
        self.router = Router(root, self._public_keys())

    def _public_keys(self) -> dict:
        public = self.root / "public"
        return {p.name.removesuffix(".public.pem"): p for p in public.glob("*.public.pem")} if public.exists() else {}

    def _checkpoint(self, parent: str, value: dict) -> None:
        atomic_json(self.root / "scheduled-runs" / parent / "checkpoint.json", value)

    def _invoke(self, alias: str, run_dir: Path, request: Path, result: Path) -> None:
        done = self.runner([alias, "--in", str(run_dir), "-z", f"Complete the closed request JSON at {request.name}; write only {result.name}.", "--usage-file", str(run_dir / "usage.json"), "--skills", "none"], capture_output=True, text=True, timeout=900)
        if done.returncode or not result.is_file(): raise RuntimeError("bounded Hermes role invocation failed")

    def _wait_signed(self, contract: dict, envelope: dict, run_dir: Path) -> dict:
        registry_path = self.root / "artifact-registry.json"
        registry = json.loads(registry_path.read_text()) if registry_path.exists() else {}
        for item in envelope["outputs"]:
            candidate = run_dir / "result.json"
            if not candidate.exists() and contract["input_artifacts"]:
                prior = registry.get(item["artifact_id"]); candidate = Path(prior["path"]) if prior else candidate
            if candidate.exists(): registry[item["artifact_id"]] = {"path": str(candidate), "sha256": item["sha256"]}
        atomic_json(registry_path, registry, 0o640)
        request = self.root / "org-signer-requests" / contract["owner"] / f"{contract['child_run_id']}.json"
        result = self.root / "org-signer-results" / contract["owner"] / request.name
        atomic_json(request, envelope, 0o640)
        deadline = time.monotonic() + (2 if self.test_mode else 120)
        while time.monotonic() < deadline:
            if result.exists():
                value = json.loads(result.read_text()); atomic_json(run_dir / "signed-receipt.json", value); return value
            time.sleep(0.01 if self.test_mode else 0.25)
        raise TimeoutError(f"isolated signer unavailable: {contract['owner']}")

    def _block(self, parent: dict, contract: dict, reason: str) -> None:
        incident = f"scheduled-{contract['stage_id']}-capability"
        resume = digest({"parent": parent["parent_run_id"], "incident": incident, "contract": digest(contract)})
        wc = parent["scheduled_contract"]["work_control"]
        args = [wc["path"], "block", "--parent-run-id", parent["parent_run_id"], "--capability-incident-id", incident, "--return-point", wc["return_point"], "--resume-token", resume, "--objective", parent["objective"], "--acceptance-test", parent["scheduled_contract"]["completion_test"], "--permission-ceiling", parent["scheduled_contract"]["permission_ceiling"]]
        done = self.runner(args, capture_output=True, text=True, timeout=60)
        if done.returncode: raise RuntimeError("work-control block failed")
        self._checkpoint(parent["parent_run_id"], {"status": "waiting_on_capability", "incident": incident, "return_point": wc["return_point"], "reason": reason, "resume_token_sha256": hashlib.sha256(resume.encode()).hexdigest()})

    def run_parent(self, parent: dict) -> dict:
        parent_id = parent["parent_run_id"]
        try: self.router.initialise({key: parent[key] for key in ("source", "source_cron_id", "job_name", "prompt", "delivery", "triggered_at")}, parent_id)
        except KeyError:
            # Persisted ingress parents contain the already validated intake fields under their canonical names.
            self.router._atomic(self.router._path(parent_id), parent)
        while True:
            state = self.router.load(parent_id)
            if state["state"] == "closed": return state
            child = f"{parent_id}-{state['cursor']:02d}"
            contract = self.router.issue(parent_id, child)
            run_dir = self.root / "scheduled-runs" / parent_id / "children" / child
            run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            request_path, result_path = run_dir / "request.json", run_dir / "result.json"
            request = {"schema_version": 1, "contract": contract, "parent_run_id": parent_id, "permission_ceiling": contract["permission_ceiling"]}
            if contract["stage_id"] == "context":
                sources, urls = snapshot_sources(parent["scheduled_contract"]["canonical_sources"], run_dir / "sources", parent["scheduled_contract"]["gsc"]["property"])
                request.update(canonical_sources=sources, gsc={**parent["scheduled_contract"]["gsc"], "candidate_urls": urls})
            atomic_json(request_path, request)
            try:
                if contract["runtime"] == "verifier":
                    outputs = contract["input_artifacts"]
                elif contract["stage_id"] in BOT_STAGES:
                    alias = parent["scheduled_contract"]["profile_aliases"][contract["owner"]]
                    self._invoke(alias, run_dir, request_path, result_path)
                    outputs = [artifact(result_path, f"{contract['stage_id']}-result")]
                else:
                    atomic_json(result_path, {"status": "accepted", "stage_id": contract["stage_id"]})
                    outputs = [artifact(result_path, f"{contract['stage_id']}-result")]
                decision = json.loads(result_path.read_text()).get("decision", {}) if result_path.exists() else {}
                signed = self._wait_signed(contract, {"contract": contract, "outputs": [{k:v for k,v in item.items() if k != "path"} for item in outputs], "checks": ["artifact.readback_sha256"], "decision": decision}, run_dir)
                state = self.router.accept(parent_id, contract, signed)
                self._checkpoint(parent_id, {"status": state["state"], "cursor": state["cursor"], "child_run_id": child, "idempotency_key": contract["idempotency_key"], "signed_receipt_sha256": digest(signed)})
            except Exception as exc:
                checkpoint = self.root / "scheduled-runs" / parent_id / "checkpoint.json"
                previous = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
                if previous.get("failed_child") != child:
                    self._checkpoint(parent_id, {"status": "retrying", "failed_child": child, "safe_retry": 1, "reason": str(exc)})
                    continue
                self._block(parent, contract, str(exc)); return {"state": "incident", "parent_run_id": parent_id}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent", type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    parent = json.loads(args.parent.read_text())
    state = ScheduledExecutor(args.root, test_mode=os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1").run_parent(parent)
    print(json.dumps({"parent_run_id": parent["parent_run_id"], "business_state": state["state"]}, sort_keys=True))


if __name__ == "__main__": main()
