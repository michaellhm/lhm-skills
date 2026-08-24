#!/usr/bin/env python3
"""Deterministic registered-adapter double; never imports connector clients."""
import hashlib
import json
import sys
from pathlib import Path

request = json.load(sys.stdin)
operation, argv = request["operation"], request["argv"]
if operation == "claude_dispatch":
    command = argv[1]
    if command == "submit-seo-gsc-readonly":
        result = {"run_id": "claude-gsc-fixture-01", "property": argv[2], "urls": argv[3].split(","), "read_only": True}
    elif command == "submit-specialist-readonly":
        contract = json.loads(argv[5]); route = argv[2]
        skill = {"keyword-research": "lhm-marketing-hub:keyword-research", "seo-delivery-qa": "lhm-marketing-hub:seo-delivery-qa"}[route]
        if route == "keyword-research":
            path = Path(contract["output_contract"]["artifact_path"])
            path.parent.mkdir(parents=True, exist_ok=True); path.write_text("# Bounded keyword evidence\n")
            result = {"run_id": "claude-keyword-fixture-01", "route": route, "observed_skills": [skill], "artifact_path": str(path), "artifact_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        else:
            result = {"run_id": "claude-qa-fixture-01", "route": route, "observed_skills": [skill], "artifact_sha256": contract["artifact_sha256"], "drive_file_id": contract["drive_file_id"], "disposition": "accepted"}
    elif command == "submit-google-drive-client-file-create":
        value = hashlib.sha256(Path(argv[3]).read_bytes()).hexdigest()
        result = {"run_id": "claude-gdrive-fixture-01", "file_id": "fixture-file-1", "parent_id": "1t3aUHy1ZSMiHophhJQsQC-cDjcZiMxUA", "readback_file_id": "fixture-file-1", "source_sha256": value, "readback_sha256": value}
    elif command == "submit-basicops-task-discussion-update":
        result = {"run_id": "claude-basicops-fixture-01", "task_id": argv[3], "comment_id": "fixture-comment-1", "readback_comment_id": "fixture-comment-1"}
    else:
        raise SystemExit(3)
elif operation == "department_lead_accept":
    supplied = json.loads(argv[3]); result = {"operation": "department-lead-accept", "state": "lead_accepted", "qa_receipt_sha256": supplied["qa_receipt_sha256"], "immutable_readback": True}
elif operation == "tracker_cas_readback":
    result = {"path": "30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md", "sha256": "c" * 64, "readback_sha256": "c" * 64, "cas": True}
else:
    raise SystemExit(4)
receipt = {"schema_version": 1, "operation": operation, "binding": request["binding"], "result": result}
receipt["receipt_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
print(json.dumps(receipt, sort_keys=True))
