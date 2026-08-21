"""Black-box helpers for the LHM workflow controller security contract.

The executable under test is selected with ``LHM_WORKFLOW_CLI``.  Tests never
import production modules: the installed CLI and its durable state are the
security boundary.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Controller:
    executable: Path
    root: Path
    env: dict[str, str]

    @classmethod
    def from_environment(cls, root: Path) -> "Controller":
        configured = os.environ.get("LHM_WORKFLOW_CLI")
        if not configured:
            raise AssertionError("LHM_WORKFLOW_CLI must name the installed v5 CLI")
        executable = Path(configured)
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise AssertionError(f"workflow CLI is not executable: {executable}")
        env = dict(os.environ)
        env["LHM_WORKFLOW_ROOT"] = str(root)
        # A root override must never silently enable test trust rules.  The
        # explicit flag is required by the security tests and must be disabled
        # in the installed production unit.
        env["LHM_WORKFLOW_TEST_MODE"] = "1"
        env["LHM_WORKFLOW_PYTHON"] = sys.executable
        return cls(executable, root, env)

    def run(
        self,
        *args: str,
        payload: dict[str, Any] | None = None,
        ok: bool = True,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = {**self.env, **(extra_env or {})}
        proc = subprocess.run(
            [str(self.executable), *args],
            input=None if payload is None else json.dumps(payload),
            text=True,
            capture_output=True,
            env=env,
            timeout=20,
        )
        if ok and proc.returncode != 0:
            raise AssertionError((args, proc.returncode, proc.stdout, proc.stderr))
        if not ok and proc.returncode == 0:
            raise AssertionError(f"command unexpectedly succeeded: {args}")
        return proc

    def json(self, *args: str, **kwargs: Any) -> dict[str, Any]:
        proc = self.run(*args, **kwargs)
        return json.loads(proc.stdout)

    def state(self, parent: str = "p-security") -> dict[str, Any]:
        return self.json("status", parent)

    def adapter_record(self, event: dict[str, Any], name: str = "stage.json") -> Path:
        source = self.root.parent / "adapter-source" / name
        output = self.root.parent / "adapter" / name
        write_json(source, event)
        proc = subprocess.run(
            [sys.executable, "-m", "lhm_workflow.adapter", str(source), str(output),
             "--key", str(self.root / "secrets" / "adapter.key"),
             "--artifact-root", str(self.root.parent / "adapter" / "artifacts")],
            text=True, capture_output=True, env=self.env,
        )
        if proc.returncode:
            raise AssertionError((proc.returncode, proc.stdout, proc.stderr))
        return output

    def assert_stage_rejected(self, event: dict[str, Any], name: str) -> None:
        source = self.root.parent / "adapter-source" / name
        output = self.root.parent / "adapter" / name
        write_json(source, event)
        proc = subprocess.run(
            [sys.executable, "-m", "lhm_workflow.adapter", str(source), str(output),
             "--key", str(self.root / "secrets" / "adapter.key"),
             "--artifact-root", str(self.root.parent / "adapter" / "artifacts")],
            text=True, capture_output=True, env=self.env,
        )
        if proc.returncode == 0:
            self.run("ingest-stage", str(output), ok=False)

    def ingest_stage(self, event: dict[str, Any], name: str = "stage.json") -> dict[str, Any]:
        return self.json("ingest-stage", str(self.adapter_record(event, name)))

    def verifier_record(self, child_run_id: str, name: str = "final.json") -> Path:
        request = self.root / "verifier-requests" / f"verify:{child_run_id}.json"
        output = self.root.parent / "verifier" / name
        proc = subprocess.run(
            [sys.executable, "-m", "lhm_workflow.verifier", str(request), str(output),
             "--key", str(self.root / "secrets" / "verifier.key")],
            text=True, capture_output=True, env=self.env,
        )
        if proc.returncode:
            raise AssertionError((proc.returncode, proc.stdout, proc.stderr))
        return output

    def verify_stage(self, child_run_id: str, name: str = "final.json") -> dict[str, Any]:
        return self.json("ingest-verification", str(self.verifier_record(child_run_id, name)))


def contract(stage: str = "content") -> dict[str, Any]:
    stage_contracts = {
        "content": ("claude", "lhm-marketing-hub:content", "lhm-marketing-hub:seo-content-writer", []),
        "seo_evidence": ("claude", "lhm-marketing-hub:seo", "lhm-marketing-hub:seo-audit", ["google_search_console.property_read"]),
        "content_production": ("claude", "lhm-marketing-hub:content", "lhm-marketing-hub:seo-content-writer", []),
        "site_implementation": ("codex", "codexworker", "lhm-wordpress-hub:astro-build", ["repo.branch_write", "preview.create"]),
        "verification": ("lhm_host_verifier", "lhmworkflowverify", "lhm-system:workflow-verification", ["artifact.read", "repo.read", "preview.read"]),
    }
    runtime, identity, skill, capabilities = stage_contracts[stage]
    return {
        "schema_version": 1,
        "parent_run_id": "p-security",
        "child_run_id": f"c-{stage}",
        "workflow_id": "seo-content-astro-v1",
        "stage_id": stage,
        "idempotency_key": hashlib.sha256(f"p-security:{stage}".encode()).hexdigest(),
        "worker": {
            "runtime": runtime,
            "identity": identity,
            "run_id": f"run-{stage}",
        },
        "required_skills": [skill],
        "required_capabilities": capabilities,
        "expected_mutation_state": "branch_only" if stage == "site_implementation" else "none",
    }


def initialise(controller: Controller, value: dict[str, Any] | None = None) -> dict[str, Any]:
    return controller.json("init-parent", payload=value or contract())


def write_json(path: Path, value: dict[str, Any], mode: int = 0o600) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    path.chmod(mode)
    return path


def write_sealed_json(path: Path, value: dict[str, Any], key: Path, field: str) -> Path:
    unsigned = dict(value)
    unsigned.pop(field, None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    unsigned[field] = hmac.new(key.read_bytes(), payload, hashlib.sha256).hexdigest()
    return write_json(path, unsigned)


def stage_receipt(c: dict[str, Any], evidence: Path) -> dict[str, Any]:
    return {
        **{k: c[k] for k in (
            "parent_run_id", "child_run_id", "workflow_id", "stage_id",
            "idempotency_key", "worker",
        )},
        "schema_version": 1,
        "event": "stage_receipt",
        "event_id": f"receipt:{c['child_run_id']}",
        "status": "candidate",
        "evidence": [{"kind": "artifact", "path": str(evidence), "sha256": file_digest(evidence)}],
        "host_provenance": {
            "observer": "host-dispatcher",
            "required_skills": c["required_skills"],
            "observed_skill_calls": c["required_skills"],
        },
        "checks": ["artifact_hash", "skills_observed"],
        "mutation_audit": {"mutation_state": c["expected_mutation_state"]},
    }


def verifier_receipt(c: dict[str, Any], stage_event_digest: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "event": "verification_receipt",
        "event_id": f"verify:{c['child_run_id']}",
        **{k: c[k] for k in ("parent_run_id", "child_run_id", "workflow_id", "stage_id")},
        "verifier_identity": "lhmworkflowverify",
        "stage_event_sha256": stage_event_digest,
        "disposition": "verified",
        "checks": ["ids", "hashes", "skills", "mutation_boundary"],
        "evidence_ids": [stage_event_digest],
        "mutation_audit": {"mutation_state": c["expected_mutation_state"]},
    }
