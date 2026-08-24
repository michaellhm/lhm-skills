#!/usr/bin/env python3
"""Deterministic registered-adapter double; never imports connector clients."""
import hashlib
import json
import sys

request = json.load(sys.stdin)
operation, argv = request["operation"], request["argv"]
if operation == "claude_dispatch":
    command = argv[1]
    if command == "submit-seo-gsc-readonly": result = {"run_id": "claude-gsc-fixture-01", "property": argv[2], "urls": argv[3].split(","), "read_only": True}
    elif command == "submit-specialist-readonly": result = {"run_id": f"claude-{argv[2]}-fixture-01", "route": argv[2], "observed_skills": [f"lhm-marketing-hub:{argv[2]}"]}
    elif command == "submit-google-drive-client-file-create": result = {"run_id": "claude-gdrive-fixture-01", "file_id": "fixture-file-1", "parent_id": "1t3aUHy1ZSMiHophhJQsQC-cDjcZiMxUA", "readback_file_id": "fixture-file-1"}
    elif command == "submit-basicops-task-discussion-update": result = {"run_id": "claude-basicops-fixture-01", "task_id": argv[3], "comment_id": "fixture-comment-1", "readback_comment_id": "fixture-comment-1"}
    else: raise SystemExit(3)
elif operation == "department_lead_accept": result = {"operation": "department-lead-accept", "state": "lead_accepted", "immutable_readback": True}
elif operation == "tracker_cas_readback": result = {"path": argv[0], "sha256": "c" * 64, "readback_sha256": "c" * 64, "cas": True}
else: raise SystemExit(4)
receipt = {"schema_version": 1, "operation": operation, "binding": request["binding"], "result": result}
receipt["receipt_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
print(json.dumps(receipt, sort_keys=True))
