from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import os
import signal
import stat
from contextlib import contextmanager
from pathlib import Path

from .storage import Storage, StorageConfig, digest
from .departmental_state import (DepartmentalStateStore, new_departmental_state,
    issue_next_action, record_candidate, record_qa_acceptance,
    record_lead_acceptance, record_projection, revise_action_inputs)
from .departmental_state import validate_approval, accept_completion_dossier, record_approval_event


class ControllerError(ValueError):
    pass


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class WorkflowController:
    def __init__(self, root: Path, *, test_mode: bool = False):
        self.root = root.resolve()
        self.storage = Storage(StorageConfig.for_test(self.root) if test_mode else StorageConfig())
        self.receipts = self.root / "receipts"
        self.verifier_requests = self.root / "verifier-requests"
        self.processed = self.root / "processed"
        self.operations = self.root / "operations"
        self.audit = self.root / "audit"
        self.failure_receipts = self.root / "failure-receipts"
        self.repair_queue = self.root / "repair-queue"
        self.diagnostic_queue = self.root / "diagnostic-queue"
        self.secrets = self.root / "secrets"
        self.adapter_root = self.root.parent / "adapter" if test_mode else self.root / "adapter-incoming"
        self.worker_root = self.adapter_root / "artifacts"
        self.departmental = DepartmentalStateStore(self.root / "departmental-parents")
        self.verifier_root = self.root.parent / "verifier" if test_mode else self.root / "verifier-results"
        self.expected_adapter_uid = os.getuid() if test_mode else 10005
        self.expected_worker_uid = self.expected_adapter_uid
        self.expected_verifier_uid = os.getuid() if test_mode else 10006
        for path in (self.receipts, self.verifier_requests, self.processed, self.operations, self.audit, self.secrets,
                     self.failure_receipts, self.repair_queue, self.diagnostic_queue):
            path.mkdir(parents=True, exist_ok=True, mode=0o750)
        if test_mode:
            for name in ("adapter.key", "verifier.key", "production.key", "department-lead.key", "projection.key", "approval.key", "head-production.key"):
                key_path = self.secrets / name
                if not key_path.exists():
                    key_path.write_bytes(os.urandom(32))
                    os.chmod(key_path, 0o600)

    @contextmanager
    def global_lock(self):
        path = self.root / "controller.lock"
        with path.open("a+b") as handle:
            os.chmod(path, 0o640)
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def _fault(self, boundary: str) -> None:
        if os.environ.get("LHM_FAULT_INJECT") == f"sigkill_after:{boundary}":
            os.kill(os.getpid(), signal.SIGKILL)

    @staticmethod
    def _safe_name(value: str) -> str:
        if not value or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._:-" for ch in value):
            raise ControllerError("unsafe identifier")
        return value

    def _atomic(self, path: Path, value: object, mode: int = 0o640) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def initialise(self, contract: dict) -> dict:
        parent_id = self._safe_name(contract.get("parent_run_id", ""))
        required = {"schema_version", "parent_run_id", "child_run_id", "workflow_id", "stage_id", "idempotency_key", "worker", "required_skills", "required_capabilities", "expected_mutation_state"}
        if set(contract) != required:
            raise ControllerError("invalid contract fields")
        if not contract["required_skills"] or not isinstance(contract["worker"], dict):
            raise ControllerError("invalid contract")
        parent = {
            "schema_version": 1,
            "parent_run_id": parent_id,
            "workflow_id": contract["workflow_id"],
            "state": "worker_running",
            "stages": [{"stage_id": contract["stage_id"], "child_run_id": contract["child_run_id"], "status": "issued", "contract": contract}],
            "event_counts": {},
            "pending_verifications": [],
        }
        with self.global_lock():
            existing = self.storage.read_parent(parent_id)
            if existing:
                if existing["stages"][0]["contract"] != contract:
                    raise ControllerError("parent already exists with different contract")
                return existing
            self.storage.transact(parent_id, parent, expected_hash=None, tx_id=f"init:{parent_id}")
        return parent

    def initialise_workflow(self, value: dict) -> dict:
        if set(value) != {"schema_version", "parent_run_id", "workflow_id", "stages"} or value.get("schema_version") != 1:
            raise ControllerError("invalid workflow fields")
        stages = value.get("stages")
        if not isinstance(stages, list) or len(stages) != 4:
            raise ControllerError("fixed workflow requires four stages")
        expected = ["seo_evidence", "content_production", "site_implementation", "verification"]
        if [item.get("stage_id") for item in stages] != expected:
            raise ControllerError("invalid workflow stage order")
        parent_id = self._safe_name(value["parent_run_id"])
        parent_stages = []
        for index, contract in enumerate(stages):
            if contract.get("parent_run_id") != parent_id or contract.get("workflow_id") != value["workflow_id"]:
                raise ControllerError("workflow contract binding mismatch")
            parent_stages.append({"stage_id": contract["stage_id"], "child_run_id": contract["child_run_id"], "status": "issued" if index == 0 else "pending", "contract": contract})
        parent = {"schema_version": 1, "parent_run_id": parent_id, "workflow_id": value["workflow_id"], "state": "worker_running", "stages": parent_stages, "event_counts": {}, "pending_verifications": []}
        with self.global_lock():
            if self.storage.read_parent(parent_id):
                raise ControllerError("parent already exists")
            self.storage.transact(parent_id, parent, expected_hash=None, tx_id=f"init:{parent_id}")
        return parent

    def _validate_file(self, path: Path, *, root: Path, uid: int) -> None:
        if path.is_symlink():
            raise ControllerError("symlink evidence denied")
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(root.resolve(strict=True))
        except (ValueError, OSError) as exc:
            raise ControllerError("evidence outside trusted root") from exc
        info = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != uid or info.st_mode & 0o022:
            raise ControllerError("unsafe evidence ownership or mode")

    def _validate_stage_event(self, parent: dict, event: dict, *, recovery: bool = False) -> None:
        stage = next((item for item in parent["stages"] if item["stage_id"] == event.get("stage_id")), None)
        allowed_statuses = {"issued", "verifying"} if recovery else {"issued"}
        if stage is None or stage["status"] not in allowed_statuses:
            raise ControllerError("stage is not issued")
        if stage["status"] == "verifying" and parent.get("event_counts", {}).get(event.get("event_id")) != 1:
            raise ControllerError("recovery event is not reflected in parent")
        contract = stage["contract"]
        for key in ("parent_run_id", "child_run_id", "workflow_id", "stage_id", "idempotency_key", "worker"):
            if event.get(key) != contract.get(key):
                raise ControllerError(f"stage receipt {key} mismatch")
        if event.get("event") != "stage_receipt" or event.get("status") != "candidate":
            raise ControllerError("invalid stage event")
        provenance = event.get("host_provenance") or {}
        if provenance.get("observer") != "host-dispatcher":
            raise ControllerError("untrusted provenance observer")
        if provenance.get("required_skills") != contract["required_skills"] or provenance.get("observed_skill_calls") != contract["required_skills"]:
            raise ControllerError("missing host-observed skill")
        audit = event.get("mutation_audit") or {}
        if audit.get("mutation_state") != contract["expected_mutation_state"]:
            raise ControllerError("mutation state mismatch")
        if not event.get("checks") or not event.get("evidence"):
            raise ControllerError("missing stage assurance")
        for evidence in event["evidence"]:
            path = Path(evidence.get("path", ""))
            self._validate_file(path, root=self.worker_root, uid=self.expected_worker_uid)
            if hashlib.sha256(path.read_bytes()).hexdigest() != evidence.get("sha256"):
                raise ControllerError("evidence digest mismatch")

    def _verify_seal(self, value: dict, field: str, key_name: str) -> None:
        seal = value.get(field)
        unsigned = dict(value)
        unsigned.pop(field, None)
        expected = hmac.new((self.secrets / key_name).read_bytes(), json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        if not isinstance(seal, str) or not hmac.compare_digest(seal, expected):
            raise ControllerError("invalid service attestation")

    def _operation_path(self, event_id: str) -> Path:
        return self.operations / f"{self._safe_name(event_id)}.json"

    def _apply_stage_operation(self, operation: dict) -> dict:
        event = operation["event"]
        parent_id = event["parent_run_id"]
        event_id = event["event_id"]
        receipt_path = self.receipts / f"{self._safe_name(event_id)}.json"
        marker_path = self.processed / f"{self._safe_name(event_id)}.json"
        verification_id = f"verify:{event['child_run_id']}"
        request_path = self.verifier_requests / f"{self._safe_name(verification_id)}.json"
        if not receipt_path.exists():
            self._atomic(receipt_path, event)
        self._fault("receipt_sealed")
        parent = self.storage.read_parent(parent_id)
        if parent is None:
            raise ControllerError("unknown parent")
        if parent["event_counts"].get(event_id, 0) == 0:
            updated = json.loads(json.dumps(parent))
            updated["event_counts"][event_id] = 1
            target = next(item for item in updated["stages"] if item["stage_id"] == event["stage_id"])
            target["status"] = "verifying"
            updated["state"] = "verifying"
            if verification_id not in updated["pending_verifications"]:
                updated["pending_verifications"].append(verification_id)
            expected = digest(parent)
            self.storage.transact(
                parent_id,
                updated,
                expected_hash=expected,
                tx_id=f"stage:{event_id}",
                fault=lambda point: self._fault("parent_applied") if point == "after_parent" else None,
            )
        self._fault("wal_committed")
        if not request_path.exists():
            request = {
                "verification_id": verification_id,
                "parent_run_id": parent_id,
                "child_run_id": event["child_run_id"],
                "workflow_id": event["workflow_id"],
                "stage_id": event["stage_id"],
                "stage_event_sha256": canonical_digest(event),
                "receipt_path": str(receipt_path),
            }
            self._atomic(request_path, request)
        self._fault("verifier_enqueued")
        if not marker_path.exists():
            self._atomic(marker_path, {"event_id": event_id, "stage_event_sha256": canonical_digest(event)})
        self._fault("processed_marker")
        operation["phase"] = "committed"
        self._atomic(self._operation_path(event_id), operation)
        self._fault("source_cleanup")
        return {"event_id": event_id, "stage_event_sha256": canonical_digest(event)}

    def ingest_stage(self, event: dict) -> dict:
        event_id = self._safe_name(event.get("event_id", ""))
        with self.global_lock():
            marker = self.processed / f"{event_id}.json"
            if marker.exists():
                return json.loads(marker.read_text())
            parent = self.storage.read_parent(event.get("parent_run_id", ""))
            if parent is None:
                raise ControllerError("unknown parent")
            self._validate_stage_event(parent, event)
            operation = {"phase": "prepared", "event": event, "event_sha256": canonical_digest(event)}
            self._atomic(self._operation_path(event_id), operation)
            self._fault("wal_prepared")
            return self._apply_stage_operation(operation)

    def ingest_stage_file(self, path: Path) -> dict:
        self._validate_file(path, root=self.adapter_root, uid=self.expected_adapter_uid)
        event = json.loads(path.read_text())
        self._verify_seal(event, "adapter_attestation", "adapter.key")
        return self.ingest_stage(event)

    def ingest_verification(self, path: Path) -> dict:
        self._validate_file(path, root=self.verifier_root, uid=self.expected_verifier_uid)
        receipt = json.loads(path.read_text())
        self._verify_seal(receipt, "verifier_attestation", "verifier.key")
        if receipt.get("verifier_identity") != "lhmworkflowverify" or receipt.get("disposition") != "verified":
            raise ControllerError("untrusted verifier result")
        if not receipt.get("checks") or not receipt.get("evidence_ids") or not receipt.get("mutation_audit"):
            raise ControllerError("empty verifier assurance")
        parent_id = receipt.get("parent_run_id", "")
        with self.global_lock():
            parent = self.storage.read_parent(parent_id)
            if parent is None:
                raise ControllerError("unknown parent")
            stage = next((item for item in parent["stages"] if item["stage_id"] == receipt.get("stage_id")), None)
            if stage is None:
                raise ControllerError("unknown verification stage")
            contract = stage["contract"]
            verification_id = f"verify:{contract['child_run_id']}"
            request_path = self.verifier_requests / f"{verification_id}.json"
            if not request_path.exists():
                raise ControllerError("verification was not requested")
            request = json.loads(request_path.read_text())
            for key in ("parent_run_id", "child_run_id", "workflow_id", "stage_id", "stage_event_sha256"):
                if receipt.get(key) != request.get(key):
                    raise ControllerError(f"verification {key} mismatch")
            if not receipt["evidence_ids"] or receipt["evidence_ids"][0] != receipt["stage_event_sha256"]:
                raise ControllerError("verification evidence binding mismatch")
            if receipt["mutation_audit"].get("mutation_state") != contract["expected_mutation_state"]:
                raise ControllerError("verification mutation mismatch")
            if stage["status"] == "accepted":
                return parent
            updated = json.loads(json.dumps(parent))
            target_index = next(index for index, item in enumerate(updated["stages"]) if item["stage_id"] == receipt["stage_id"])
            updated["stages"][target_index]["status"] = "accepted"
            if target_index + 1 < len(updated["stages"]):
                updated["stages"][target_index + 1]["status"] = "issued"
                updated["state"] = "worker_running"
            else:
                updated["state"] = "review_ready"
            updated["pending_verifications"] = []
            updated["verification_receipt_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.storage.transact(parent_id, updated, expected_hash=digest(parent), tx_id=f"verification:{verification_id}")
            return updated

    def recover(self) -> dict:
        recovered = 0
        with self.global_lock():
            for parent_path in sorted(self.storage.parents.glob("*.json")):
                self.storage.reconcile(parent_path.stem)
            for operation_path in sorted(self.operations.glob("*.json")):
                operation = json.loads(operation_path.read_text())
                if operation.get("phase") != "committed":
                    parent = self.storage.read_parent(operation["event"]["parent_run_id"])
                    self._validate_stage_event(parent, operation["event"], recovery=True)
                    self._apply_stage_operation(operation)
                    recovered += 1
        return {"recovered": recovered, "status": "ok"}

    def status(self, parent_id: str) -> dict:
        parent = self.storage.read_parent(self._safe_name(parent_id))
        if parent is None:
            raise ControllerError("unknown parent")
        return parent

    def departmental_init(self, value: dict) -> dict:
        state = new_departmental_state(**value)
        return self.departmental.checkpoint(state, expected_generation=None)

    def departmental_transition(self, parent_id: str, operation: str, payload: dict) -> dict:
        """Governed CLI boundary: load current state, apply one transition, CAS checkpoint."""
        current = self.departmental.load(self._safe_name(parent_id))
        if operation == "complete-dossier":
            accepted = accept_completion_dossier(current, payload, (self.secrets / "head-production.key").read_bytes())
            path = self.audit / f"department-completion-{self._safe_name(parent_id)}.json"
            if path.exists():
                observed = json.loads(path.read_text())
                if observed != accepted: raise ControllerError("conflicting completion dossier replay")
                return observed
            self._atomic(path, accepted, mode=0o440)
            return json.loads(path.read_text())
        generation = current["generation"]
        action = next((a for a in current["action_register"] if a["status"] not in {"accepted","cancelled","obsolete"}), None)
        contract = None if action is None else action.get("contract")
        if operation == "issue":
            validate_approval(current, (self.secrets / "approval.key").read_bytes())
            updated, contract = issue_next_action(current, payload.get("child_run_id"))
        elif operation == "candidate":
            verifier = self.root / "public" / "adapter.public.pem"
            updated = record_candidate(current, contract, payload, verifier if verifier.exists() else (self.secrets / "adapter.key").read_bytes())
        elif operation == "qa-accept": updated = record_qa_acceptance(current, contract, payload, (self.secrets / "verifier.key").read_bytes())
        elif operation == "lead-accept": updated = record_lead_acceptance(current, contract, payload, (self.secrets / "department-lead.key").read_bytes())
        elif operation == "project":
            verifier = self.root / "public" / "projection.public.pem"
            updated = record_projection(current, contract, payload, verifier if verifier.exists() else (self.secrets / "projection.key").read_bytes())
        elif operation == "revise-inputs": updated = revise_action_inputs(current, payload.get("action_id"), payload.get("accepted_inputs"))
        elif operation == "approval-event": updated = record_approval_event(current, payload, (self.secrets / "approval.key").read_bytes())
        else: raise ControllerError("invalid departmental operation")
        persisted = self.departmental.checkpoint(updated, expected_generation=generation)
        return {"state": persisted, "contract": contract} if operation == "issue" else persisted

    def record_failure(self, failure: dict) -> dict:
        """Record a controller-owned failure decision; workers cannot resume themselves."""
        required = {"schema_version", "failure_id", "parent_run_id", "child_run_id", "stage_id",
                    "classification", "reason", "evidence_sha256", "observer", "failure_attestation"}
        if set(failure) != required or failure.get("schema_version") != 1:
            raise ControllerError("invalid failure fields")
        failure_id = self._safe_name(failure.get("failure_id", ""))
        if failure.get("observer") != "lhmworkflowverify":
            raise ControllerError("worker self-certification denied")
        self._verify_seal(failure, "failure_attestation", "verifier.key")
        if failure.get("classification") not in {"needs_more_research", "capability_incident", "terminal_failure"}:
            raise ControllerError("invalid failure classification")
        if not isinstance(failure.get("reason"), str) or not failure["reason"].strip():
            raise ControllerError("empty failure reason")
        hashes = failure.get("evidence_sha256")
        if not isinstance(hashes, list) or not hashes or any(not isinstance(v, str) or len(v) != 64 or any(ch not in "0123456789abcdef" for ch in v) for v in hashes):
            raise ControllerError("failure evidence must be immutable hashes")
        with self.global_lock():
            parent = self.storage.read_parent(failure.get("parent_run_id", ""))
            if parent is None:
                raise ControllerError("unknown parent")
            stage = next((s for s in parent["stages"] if s["stage_id"] == failure.get("stage_id")), None)
            if stage is None or stage["child_run_id"] != failure.get("child_run_id"):
                raise ControllerError("failure contract binding mismatch")
            if stage.get("status") not in {"issued", "verifying", "failed"}:
                raise ControllerError("accepted stage cannot be rewound by failure")
            receipt_path = self.failure_receipts / f"{failure_id}.json"
            receipt_exists = receipt_path.exists()
            if receipt_path.exists():
                existing = json.loads(receipt_path.read_text())
                if existing != failure:
                    raise ControllerError("conflicting immutable failure receipt")
                if stage.get("failure_id") == failure_id and stage.get("status") == "failed":
                    return existing
            updated = json.loads(json.dumps(parent))
            target = next(s for s in updated["stages"] if s["stage_id"] == failure["stage_id"])
            contract = target["contract"]
            consequential = contract.get("expected_mutation_state") != "none"
            attempts = int(target.get("failure_attempts", 0)) + 1
            target.update(status="failed", failure_attempts=attempts, failure_id=failure_id)
            classification = failure["classification"]
            if classification == "needs_more_research" and not consequential and attempts == 1:
                target["recovery_disposition"] = "production_resume_available"
                updated["state"] = "needs_more_research"
            else:
                target["recovery_disposition"] = "no_automatic_retry"
                updated["state"] = "capability_incident" if classification == "capability_incident" else "failed"
            if not receipt_exists:
                self._atomic(receipt_path, failure, mode=0o440)
            self._fault("failure_receipt_sealed")
            if classification == "capability_incident":
                self._atomic(self.repair_queue / f"{failure_id}.json", {
                    "failure_id": failure_id, "parent_run_id": failure["parent_run_id"],
                    "stage_id": failure["stage_id"], "status": "awaiting_repair",
                    "evidence_sha256": list(hashes)})
                self._atomic(self.diagnostic_queue / f"{failure_id}.json", {
                    "failure_id": failure_id, "worker": "lhm_diagnostic_specialist",
                    "required_skill": "lhm-system:capability-diagnostic", "mode": "diagnostic_only",
                    "may_mutate": False, "may_resume": False})
            self.storage.transact(failure["parent_run_id"], updated, expected_hash=digest(parent), tx_id=f"failure:{failure_id}")
            return failure

    def production_resume(self, parent_id: str, stage_id: str, authorization: dict) -> dict:
        """Issue one bounded retry only from a Production-owned decision."""
        required = {"schema_version", "mode", "actor", "decision", "failure_id", "failure_receipt_sha256", "production_attestation"}
        if set(authorization) != required or authorization.get("schema_version") != 1:
            raise ControllerError("invalid resume authorization")
        if authorization.get("mode") != "Production" or authorization.get("actor") != "lhm_production_manager" or authorization.get("decision") != "resume":
            raise ControllerError("Production-only resume required")
        self._verify_seal(authorization, "production_attestation", "production.key")
        with self.global_lock():
            parent = self.storage.read_parent(self._safe_name(parent_id))
            if parent is None:
                raise ControllerError("unknown parent")
            stage = next((s for s in parent["stages"] if s["stage_id"] == stage_id), None)
            if (stage is not None and stage.get("status") == "issued" and stage.get("recovery_disposition") == "retry_issued"
                    and stage.get("failure_id") == authorization.get("failure_id")):
                return parent
            if stage is None or stage.get("status") != "failed" or stage.get("recovery_disposition") != "production_resume_available":
                raise ControllerError("stage is not resumable")
            failure_id = stage.get("failure_id")
            if authorization["failure_id"] != failure_id:
                raise ControllerError("resume failure binding mismatch")
            receipt_path = self.failure_receipts / f"{self._safe_name(failure_id)}.json"
            if hashlib.sha256(receipt_path.read_bytes()).hexdigest() != authorization["failure_receipt_sha256"]:
                raise ControllerError("resume receipt digest mismatch")
            if stage["contract"].get("expected_mutation_state") != "none":
                raise ControllerError("consequential retry denied")
            updated = json.loads(json.dumps(parent)); target = next(s for s in updated["stages"] if s["stage_id"] == stage_id)
            attempt = target["failure_attempts"]
            if attempt != 1:
                raise ControllerError("retry budget exhausted")
            target["status"] = "issued"; target["recovery_disposition"] = "retry_issued"
            target["retry_attempt"] = attempt
            target["retry_idempotency_key"] = hashlib.sha256(f"{target['contract']['idempotency_key']}:{attempt}".encode()).hexdigest()
            updated["state"] = "worker_running"
            self.storage.transact(parent_id, updated, expected_hash=digest(parent), tx_id=f"resume:{failure_id}:{attempt}")
            return updated
