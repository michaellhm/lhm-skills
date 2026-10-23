#!/usr/bin/env python3
"""Non-root paired Codex bootstrap; approvals continue in the saved desktop/mobile chat."""
import importlib.util
import json
import os
from pathlib import Path
import sys

run=Path(sys.argv[1]).resolve()
if os.geteuid()!=10001 or not run.is_relative_to(Path('/home/codexworker/cto-repairs')) or run.name!='handoff':
    raise ValueError('Expected the registered non-root CTO repair workspace')
packet=json.loads((run/'task-context.json').read_text())
spec=importlib.util.spec_from_file_location('paired_codex','/usr/local/libexec/lhm-wellness-codex-pilot.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
cwd=run.parent
prompt=('You are the Codex engineering handoff from the LHM CTO. Read handoff/task-context.json. '
        'The source feature-branch checkout is in source/; read its repository instructions before editing. The packet contains the original outcome, '
        'investigation, evidence, acceptance tests and Intervention task link. Investigate and prepare the scoped repair '
        'with tests in this source feature branch. Keep missing context or source access troubleshooting in this chat. '
        'Do not ask TED for a second generic plan approval. Do not edit live Hermes, access root or credentials, '
        'merge/push main, deploy, send client messages or start unrelated repairs. Michael will review and continue '
        'in this exact Codex chat for further feedback and approval decisions. The unattended bootstrap cannot answer '
        'an interactive permission request; if one is needed, preserve your work and explain the exact pending step '
        'so Michael can continue it here. A code patch or GitHub branch is not a deployed repair. '
        'If this is a handoff validation request, verify the packet/workspace/chat contract and report the result '
        'without inventing or applying an unrelated repair.\n\n'+json.dumps(packet,ensure_ascii=False))
task={'client_id':'cto','task_type':'cto_repair','title':'CTO: '+packet['capability_incident_id']}
native.conversation(task,prompt,run,cwd=cwd,write=True,timeout=1200,read_only_integrations=True)
