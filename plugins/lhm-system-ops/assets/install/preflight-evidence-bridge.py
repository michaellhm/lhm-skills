#!/usr/bin/env python3
"""Static host preflight; container visibility is a separate authenticated smoke."""
import json
import os
import sys
from pathlib import Path

EXPECTED = {
    "evidence_claude_dispatcher": "/usr/local/libexec/lhm-evidence-claude-dispatcher",
    "evidence_claude_worker": "/usr/local/libexec/lhm-evidence-claude-worker",
    "evidence_fathom_backend": "/usr/local/libexec/lhm-evidence-fathom-backend",
    "fathom_host_skill": "/home/hermes/.hermes/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md",
    "sudo": "/usr/bin/sudo",
}


def main():
    if len(sys.argv) != 2: raise SystemExit("usage: preflight-evidence-bridge.py routes.json")
    with open(sys.argv[1], encoding="utf-8") as handle: config = json.load(handle)
    if config != {"schema_version": 1, "routes": EXPECTED}:
        raise SystemExit("route registration differs from verified host paths")
    for name, path in EXPECTED.items():
        item = Path(path)
        executable = name != "fathom_host_skill"
        if not item.is_absolute() or not item.is_file() or (executable and not os.access(item, os.X_OK)):
            raise SystemExit("required host-visible route absent: " + name)
        stat = item.stat()
        if name in {"evidence_claude_dispatcher", "evidence_claude_worker", "evidence_fathom_backend"} and (stat.st_uid != 0 or stat.st_mode & 0o777 != 0o755):
            raise SystemExit("evidence gateway ownership or mode differs from root:root 0755")
    print('{"host_preflight":"ok","container_smoke_required":true}')


if __name__ == "__main__": main()
