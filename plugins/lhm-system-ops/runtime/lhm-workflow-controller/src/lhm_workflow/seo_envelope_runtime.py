"""Executable, fail-closed SEO-01 integration over the packaged adapter boundary."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PARENT = "lhm-seo-dept-pilot-2192596-20260824"
ACTION = "SEO-01"
TRACKER = "30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md"
DRIVE_PARENT = "1t3aUHy1ZSMiHophhJQsQC-cDjcZiMxUA"
TASK = "2192596"
DISPATCH = "/opt/data/profiles/lhm_brain/bin/claude-dispatch"
CONTROLLER = "/opt/lhm-workflow/current/venv/bin/lhm-workflow"
HEX = re.compile(r"^[0-9a-f]{64}$")


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bound(request: dict) -> tuple[str, int, str, Path]:
    keys = {"schema_version", "parent_run_id", "action_id", "action_version", "envelope_sha256", "site", "urls", "client", "artifact_path", "file_name", "discussion", "tracker_expected_sha256"}
    if set(request) != keys or request["schema_version"] != 1 or request["parent_run_id"] != PARENT or request["action_id"] != ACTION or request["action_version"] != 1:
        raise ValueError("invalid SEO runtime request binding")
    if not HEX.fullmatch(str(request["envelope_sha256"])) or not HEX.fullmatch(str(request["tracker_expected_sha256"])):
        raise ValueError("invalid request digest")
    if not isinstance(request["urls"], list) or not request["urls"] or any(not isinstance(u, str) or "," in u for u in request["urls"]):
        raise ValueError("invalid GSC URLs")
    artifact = Path(request["artifact_path"])
    artifact_root = Path(os.environ.get("LHM_SEO_ARTIFACT_ROOT", "/var/lib/lhm-workflow/artifacts"))
    if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1" and artifact_root != Path("/var/lib/lhm-workflow/artifacts"):
        raise ValueError("artifact root override requires test mode")
    try:
        artifact.relative_to(artifact_root)
    except ValueError as exc:
        raise ValueError("Drive artifact escapes the governed artifact root") from exc
    if artifact.suffix != ".md" or artifact.name != request["file_name"] or ".." in artifact.parts:
        raise ValueError("Drive artifact must be the named Markdown file")
    return request["parent_run_id"], request["action_version"], request["envelope_sha256"], artifact


class RegisteredAdapter:
    def __init__(self, executable: str, *, test_mode: bool = False):
        path = Path(executable)
        if not path.is_absolute() or not path.is_file() or path.is_symlink() or not os.access(path, os.X_OK):
            raise ValueError("LHM_WORKFLOW_ADAPTER must be an absolute registered executable")
        if test_mode:
            allowed = ("/tmp/", "/private/var/folders/", str(Path(__file__).parents[2] / "tests"))
            if not str(path).startswith(allowed):
                raise ValueError("test adapter must remain in an isolated test root")
        elif path != Path("/usr/local/libexec/lhm-workflow-registered-adapter"):
            raise ValueError("unregistered production adapter")
        stat = path.stat()
        if not test_mode and (stat.st_uid != 0 or stat.st_mode & 0o022):
            raise ValueError("production adapter ownership/mode is unsafe")
        self.executable = str(path)

    def invoke(self, operation: str, argv: list[str], binding: dict) -> dict:
        payload = {"schema_version": 1, "operation": operation, "argv": argv, "binding": binding}
        done = subprocess.run([self.executable], input=json.dumps(payload), text=True, capture_output=True, timeout=30, check=False)
        if done.returncode != 0:
            raise ValueError(f"adapter operation failed: {operation}")
        try:
            receipt = json.loads(done.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("adapter returned invalid receipt") from exc
        required = {"schema_version", "operation", "binding", "result", "receipt_sha256"}
        if set(receipt) != required or receipt["schema_version"] != 1 or receipt["operation"] != operation or receipt["binding"] != binding or receipt["receipt_sha256"] != digest(receipt["result"]):
            raise ValueError("adapter receipt binding/readback mismatch")
        return receipt["result"]


class CapabilityFailure(ValueError):
    def __init__(self, operation: str):
        super().__init__(operation)
        self.operation = operation


def _capability(adapter: RegisteredAdapter, operation: str, argv: list[str], binding: dict) -> dict:
    for attempt in (1, 2):
        try:
            return adapter.invoke(operation, argv, {**binding, "attempt": attempt})
        except (ValueError, OSError, subprocess.SubprocessError):
            if attempt == 2:
                raise CapabilityFailure(operation) from None
    raise AssertionError("unreachable")


def _waiting(binding: dict, failure: CapabilityFailure) -> dict:
    root = Path(os.environ.get("LHM_SEO_FAILURE_ROOT", "/var/lib/lhm-workflow/seo-failures"))
    if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1" and root != Path("/var/lib/lhm-workflow/seo-failures"):
        raise ValueError("failure root override requires test mode")
    root.mkdir(parents=True, exist_ok=True, mode=0o750)
    incident_id = f"CII-{digest([binding['idempotency_key'], failure.operation])[:24]}"
    incident_path = root / f"{incident_id}.incident.json"
    waiting_path = root / f"{incident_id}.waiting.json"
    if incident_path.exists() or waiting_path.exists():
        if not (incident_path.is_file() and waiting_path.is_file()) or incident_path.is_symlink() or waiting_path.is_symlink():
            raise ValueError("incomplete immutable failure receipt")
        incident = json.loads(incident_path.read_text()); receipt = json.loads(waiting_path.read_text())
        if receipt.get("incident_sha256") != digest(incident) or receipt.get("incident_id") != incident_id or incident.get("failed_operation") != failure.operation:
            raise ValueError("immutable failure receipt conflict")
        return receipt
    incident = {"schema_version": 1, "incident_id": incident_id, "parent_run_id": PARENT, "action_id": ACTION, "failed_operation": failure.operation, "attempts": 2, "created_at": datetime.now(timezone.utc).isoformat(), "immutable": True}
    receipt = {"schema_version": 1, "status": "waiting_on_capability", "parent_run_id": PARENT, "action_id": ACTION, "incident_id": incident_id, "incident_sha256": digest(incident), "retry_count": 1}
    for path, value in ((incident_path, incident), (waiting_path, receipt)):
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o440)
        except FileExistsError:
            if json.loads(path.read_text()) != value:
                raise ValueError("immutable failure receipt conflict")
        else:
            with os.fdopen(fd, "w") as handle:
                json.dump(value, handle, sort_keys=True, separators=(",", ":")); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
    return receipt


def run(request: dict, adapter: RegisteredAdapter) -> dict:
    parent, version, envelope_sha, artifact = _bound(request)
    binding = {"parent_run_id": parent, "action_id": ACTION, "action_version": version, "envelope_sha256": envelope_sha, "idempotency_key": digest([parent, ACTION, version, envelope_sha])}
    try:
        gsc = _capability(adapter, "claude_dispatch", [DISPATCH, "submit-seo-gsc-readonly", request["site"], ",".join(request["urls"]), json.dumps({**binding, "objective": "Collect bounded GSC evidence for keyword research"}, sort_keys=True, separators=(",", ":"))], binding)
        keyword_contract = {**binding, "route": "keyword-research", "required_skill": "lhm-marketing-hub:keyword-research", "input_receipt_sha256": digest(gsc), "output_contract": {"artifact_path": str(artifact), "media_type": "text/markdown", "content_sha256_required": True}}
        keyword = _capability(adapter, "claude_dispatch", [DISPATCH, "submit-specialist-readonly", "keyword-research", "internal", parent, json.dumps(keyword_contract, sort_keys=True, separators=(",", ":"))], binding)
        if keyword.get("observed_skills") != ["lhm-marketing-hub:keyword-research"] or keyword.get("artifact_path") != str(artifact) or not artifact.is_file():
            raise ValueError("keyword specialist output/provenance mismatch")
        artifact_sha = file_digest(artifact)
        if keyword.get("artifact_sha256") != artifact_sha:
            raise ValueError("keyword specialist artifact hash mismatch")
        drive = _capability(adapter, "claude_dispatch", [DISPATCH, "submit-google-drive-client-file-create", request["client"], str(artifact), request["file_name"]], binding)
        if drive.get("parent_id") != DRIVE_PARENT or drive.get("readback_file_id") != drive.get("file_id") or drive.get("source_sha256") != artifact_sha or drive.get("readback_sha256") != artifact_sha:
            raise ValueError("Drive create/readback artifact mismatch")
        qa_contract = {**binding, "route": "seo-delivery-qa", "required_skill": "lhm-marketing-hub:seo-delivery-qa", "keyword_receipt_sha256": digest(keyword), "artifact_sha256": artifact_sha, "drive_file_id": drive["file_id"], "drive_readback_sha256": drive["readback_sha256"]}
        qa = _capability(adapter, "claude_dispatch", [DISPATCH, "submit-specialist-readonly", "seo-delivery-qa", "internal", parent, json.dumps(qa_contract, sort_keys=True, separators=(",", ":"))], binding)
        if qa.get("observed_skills") != ["lhm-marketing-hub:seo-delivery-qa"] or qa.get("artifact_sha256") != artifact_sha or qa.get("drive_file_id") != drive["file_id"] or qa.get("disposition") != "accepted":
            raise ValueError("SEO delivery QA lineage/provenance mismatch")
        lead_input = {"schema_version": 1, "role": "department_lead", "decision": "accepted", "qa_receipt_sha256": digest(qa), "goal_checks": ["exact_drive_artifact_qa_accepted"]}
        lead = adapter.invoke("department_lead_accept", [CONTROLLER, "department-lead-accept", parent, json.dumps(lead_input, sort_keys=True, separators=(",", ":"))], binding)
        if lead.get("qa_receipt_sha256") != digest(qa) or lead.get("state") != "lead_accepted":
            raise ValueError("Lead acceptance receipt chain mismatch")
        tracker_summary = {"parent_run_id": parent, "workflow_id": "seo-envelope-v1", "run_result": "succeeded", "work_state": "complete", "completed_at": datetime.now(timezone.utc).isoformat(), "accepted_receipts": [{"stage_id": "keyword-research", "contract_sha256": digest(keyword_contract), "artifact_sha256s": [artifact_sha]}, {"stage_id": "seo-delivery-qa", "contract_sha256": digest(qa_contract), "artifact_sha256s": [digest(qa), digest(lead)]}]}
        tracker = adapter.invoke("tracker_cas_readback", [CONTROLLER, "tracker-cas-readback", request["tracker_expected_sha256"], json.dumps(tracker_summary, sort_keys=True, separators=(",", ":"))], binding)
        if tracker.get("path") != TRACKER or tracker.get("readback_sha256") != tracker.get("sha256"):
            raise ValueError("tracker CAS/readback mismatch")
        basicops = _capability(adapter, "claude_dispatch", [DISPATCH, "submit-basicops-task-discussion-update", request["client"], TASK, request["discussion"]], binding)
        if basicops.get("task_id") != TASK or basicops.get("readback_comment_id") != basicops.get("comment_id"):
            raise ValueError("BasicOps discussion/readback mismatch")
    except CapabilityFailure as failure:
        return _waiting(binding, failure)
    return {"status": "completed", "binding": binding, "gsc_receipt": gsc, "keyword_receipt": keyword, "artifact_sha256": artifact_sha, "drive_receipt": drive, "qa_receipt": qa, "lead_acceptance": lead, "tracker_receipt": tracker, "basicops_receipt": basicops, "drive_create_count": 1, "stop_after_basicops_readback": True}


def main() -> None:
    executable = os.environ.get("LHM_WORKFLOW_ADAPTER")
    if not executable:
        raise SystemExit("LHM_WORKFLOW_ADAPTER is required")
    try:
        print(json.dumps(run(json.load(__import__("sys").stdin), RegisteredAdapter(executable, test_mode=os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1")), sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
