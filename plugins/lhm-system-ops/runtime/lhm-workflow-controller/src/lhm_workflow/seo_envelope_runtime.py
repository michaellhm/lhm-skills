"""Executable, fail-closed SEO-01 integration over a registered adapter boundary."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

PARENT = "lhm-seo-dept-pilot-2192596-20260824"
ACTION = "SEO-01"
TRACKER = "30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md"
DRIVE_PARENT = "1t3aUHy1ZSMiHophhJQsQC-cDjcZiMxUA"
TASK = "2192596"
DISPATCH = "/opt/data/profiles/lhm_brain/bin/claude-dispatch"
HEX = re.compile(r"^[0-9a-f]{64}$")


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _bound(request: dict) -> tuple[str, int, str]:
    keys = {"schema_version", "parent_run_id", "action_id", "action_version", "envelope_sha256", "site", "urls", "client", "artifact_path", "file_name", "discussion", "tracker_expected_sha256"}
    if set(request) != keys or request["schema_version"] != 1 or request["parent_run_id"] != PARENT or request["action_id"] != ACTION or request["action_version"] != 1:
        raise ValueError("invalid SEO runtime request binding")
    if not HEX.fullmatch(str(request["envelope_sha256"])) or not HEX.fullmatch(str(request["tracker_expected_sha256"])):
        raise ValueError("invalid request digest")
    if not isinstance(request["urls"], list) or not request["urls"] or any("," in u for u in request["urls"]):
        raise ValueError("invalid GSC URLs")
    artifact = Path(request["artifact_path"])
    artifact_root = Path("/var/lib/lhm-workflow/artifacts")
    try:
        artifact.relative_to(artifact_root)
    except ValueError as exc:
        raise ValueError("Drive artifact escapes the governed artifact root") from exc
    if artifact.suffix != ".md" or artifact.name != request["file_name"] or ".." in artifact.parts:
        raise ValueError("Drive artifact must be the named Markdown file")
    return request["parent_run_id"], request["action_version"], request["envelope_sha256"]


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


def run(request: dict, adapter: RegisteredAdapter) -> dict:
    parent, version, envelope_sha = _bound(request)
    binding = {"parent_run_id": parent, "action_id": ACTION, "action_version": version, "envelope_sha256": envelope_sha, "idempotency_key": digest([parent, ACTION, version, envelope_sha])}
    objective = json.dumps({**binding, "objective": "Collect bounded GSC evidence for keyword research"}, sort_keys=True, separators=(",", ":"))
    gsc = adapter.invoke("claude_dispatch", [DISPATCH, "submit-seo-gsc-readonly", request["site"], ",".join(request["urls"]), objective], binding)
    specialist_results = []
    for route in ("keyword-research", "seo-delivery-qa"):
        routed = {**binding, "route": route, "required_skill": f"lhm-marketing-hub:{route}", "objective": "Produce or verify the bounded SEO-01 delivery"}
        result = adapter.invoke("claude_dispatch", [DISPATCH, "submit-specialist-readonly", route, "internal", parent, json.dumps(routed, sort_keys=True, separators=(",", ":"))], binding)
        if result.get("observed_skills") != [f"lhm-marketing-hub:{route}"]:
            raise ValueError("specialist Skill provenance mismatch")
        specialist_results.append(result)
    lead = adapter.invoke("department_lead_accept", ["department-lead-accept", parent], binding)
    tracker = adapter.invoke("tracker_cas_readback", [TRACKER, request["tracker_expected_sha256"]], binding)
    if tracker.get("path") != TRACKER or tracker.get("readback_sha256") != tracker.get("sha256"):
        raise ValueError("tracker CAS/readback mismatch")
    drive = adapter.invoke("claude_dispatch", [DISPATCH, "submit-google-drive-client-file-create", request["client"], request["artifact_path"], request["file_name"]], binding)
    if drive.get("parent_id") != DRIVE_PARENT or drive.get("readback_file_id") != drive.get("file_id"):
        raise ValueError("Drive create/readback mismatch")
    basicops = adapter.invoke("claude_dispatch", [DISPATCH, "submit-basicops-task-discussion-update", request["client"], TASK, request["discussion"]], binding)
    if basicops.get("task_id") != TASK or basicops.get("readback_comment_id") != basicops.get("comment_id"):
        raise ValueError("BasicOps discussion/readback mismatch")
    return {"status": "completed", "binding": binding, "gsc_receipt": gsc, "specialist_receipts": specialist_results, "lead_acceptance": lead, "tracker_receipt": tracker, "drive_receipt": drive, "basicops_receipt": basicops, "drive_create_count": 1}


def main() -> None:
    executable = os.environ.get("LHM_WORKFLOW_ADAPTER")
    if not executable:
        raise SystemExit("LHM_WORKFLOW_ADAPTER is required")
    try:
        test_mode = os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1"
        print(json.dumps(run(json.load(__import__("sys").stdin), RegisteredAdapter(executable, test_mode=test_mode)), sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
