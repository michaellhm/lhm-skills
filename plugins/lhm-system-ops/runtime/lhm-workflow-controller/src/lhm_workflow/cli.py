from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .controller import ControllerError, WorkflowController
from .tracker_connector import TrackerConnector


def _controller() -> WorkflowController:
    override = os.environ.get("LHM_WORKFLOW_ROOT")
    if override:
        if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
            raise ControllerError("root override requires explicit test mode")
        root = Path(override).resolve()
        if not (str(root).startswith("/tmp/") or str(root).startswith("/private/var/folders/")):
            raise ControllerError("test root must be under /tmp")
        return WorkflowController(root, test_mode=True)
    return WorkflowController(Path("/var/lib/lhm-workflow"), test_mode=False)


def _stdin_json() -> dict:
    return json.load(sys.stdin)


def main() -> None:
    try:
        ctl = _controller()
        if len(sys.argv) < 2:
            raise ControllerError("command required")
        command = sys.argv[1]
        if command == "init-parent" and len(sys.argv) == 2:
            result = ctl.initialise(_stdin_json())
        elif command == "init-workflow" and len(sys.argv) == 2:
            result = ctl.initialise_workflow(_stdin_json())
        elif command == "ingest-stage" and len(sys.argv) == 3:
            result = ctl.ingest_stage_file(Path(sys.argv[2]))
        elif command == "ingest-verification" and len(sys.argv) == 3:
            result = ctl.ingest_verification(Path(sys.argv[2]))
        elif command == "status" and len(sys.argv) == 3:
            result = ctl.status(sys.argv[2])
        elif command == "department-init" and len(sys.argv) == 2:
            result = ctl.departmental_init(_stdin_json())
        elif command == "department-status" and len(sys.argv) == 3:
            result = ctl.departmental.load(sys.argv[2])
        elif command == "delegated-init" and len(sys.argv) == 2:
            result = ctl.delegated_init(_stdin_json())
        elif command == "delegated-status" and len(sys.argv) == 3:
            result = ctl.delegated.load(sys.argv[2])
        elif command == "delegated-monitor-all" and len(sys.argv) == 2:
            result = ctl.barney.run(**_stdin_json())
        elif command == "delegated-monitor-receipt" and len(sys.argv) == 2:
            result = ctl.barney.record_receipt(_stdin_json(), (ctl.secrets / "barney-executor.key").read_bytes())
        elif command == "tracker-cas-readback" and len(sys.argv) == 3:
            vault_override = os.environ.get("LHM_TRACKER_VAULT")
            if vault_override:
                if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
                    raise ControllerError("tracker vault override requires test mode")
                vault = Path(vault_override).resolve()
            else:
                vault = Path("/home/hermes/.hermes/profiles/lhm_brain/vault")
            receipt, _ = TrackerConnector(vault).append_structured(_stdin_json(), sys.argv[2])
            result = {"path": str(TrackerConnector(vault).path.relative_to(vault)), "sha256": receipt["sha256"], "readback_sha256": receipt["sha256"], "cas": True}
        elif command in {"department-issue", "department-candidate", "department-qa-accept", "department-lead-accept", "department-project", "department-revise-inputs", "department-complete-dossier", "department-approval-event"} and len(sys.argv) == 3:
            result = ctl.departmental_transition(sys.argv[2], command.removeprefix("department-"), _stdin_json())
        elif command in {"delegated-post-plan", "delegated-plan-decision", "delegated-chief-start", "delegated-review-ready", "delegated-delivery-decision", "delegated-chief-complete", "delegated-heartbeat", "delegated-project", "delegated-steward-disposition", "delegated-correction-fixed", "delegated-capability-restored", "delegated-monitor"} and len(sys.argv) == 3:
            result = ctl.delegated_transition(sys.argv[2], command.removeprefix("delegated-"), _stdin_json())
        elif command == "recover" and len(sys.argv) == 2:
            result = ctl.recover()
        else:
            raise ControllerError("invalid command")
        print(json.dumps(result, sort_keys=True))
    except (ControllerError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
