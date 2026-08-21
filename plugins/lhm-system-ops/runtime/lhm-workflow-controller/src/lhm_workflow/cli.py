from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .controller import ControllerError, WorkflowController


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
