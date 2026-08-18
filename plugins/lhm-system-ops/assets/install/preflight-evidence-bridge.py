#!/usr/bin/env python3
"""Fail-closed static preflight for the verified live gateway registrations."""
import json, os, sys
from pathlib import Path

EXPECTED={
 "claude_dispatcher":"/usr/local/libexec/lhm-claude-dispatcher",
 "claude_worker":"/usr/local/libexec/lhm-claude-worker",
 "fathom_wrapper":"/home/hermes/.hermes/profiles/lhm_brain/bin/fathom-exact-recording-wrapper",
 "fathom_skill":"/opt/data/profiles/lhm_brain/skills/fathom-meeting-lookup/SKILL.md",
}
def main():
    config=json.load(open(sys.argv[1],encoding="utf-8"))
    if config!={"schema_version":1,"routes":EXPECTED}: raise SystemExit("route registration is absent or differs from verified absolute paths")
    for name,path in EXPECTED.items():
        item=Path(path)
        if not item.is_absolute() or not item.exists() or (name!="fathom_skill" and not os.access(item,os.X_OK)):
            raise SystemExit("required route absent: "+name)
        stat=item.stat()
        if name in ("claude_dispatcher","claude_worker") and (stat.st_uid != 0 or stat.st_mode & 0o777 != 0o755):
            raise SystemExit("Claude gateway ownership or mode differs from verified root:root 0755 evidence")
    print('{"preflight":"ok"}')
if __name__=="__main__": main()
