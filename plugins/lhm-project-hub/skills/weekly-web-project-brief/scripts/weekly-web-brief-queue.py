#!/usr/bin/env python3
"""Native Hermes no-agent scheduler: queue only during Monday noon Melbourne."""
import importlib.util,json,os
from pathlib import Path
SKILL=Path('/opt/data/profiles/lhm_brain/skills/weekly-web-project-brief')
spec=importlib.util.spec_from_file_location('brief',SKILL/'scripts/brief.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
result=b.gate()
if result['wakeAgent']:
    week=result['week'];queue=b.BASE/'incoming';queue.mkdir(exist_ok=True)
    path=queue/(week+'.json')
    tmp=queue/('.'+week+'.'+str(os.getpid())+'.tmp')
    tmp.write_text(json.dumps({'week':week,'mode':'scheduled'}))
    try:
        os.link(tmp,path)
        result={'state':'queued_for_codex','week':week}
    except FileExistsError:result={'state':'already_queued','week':week}
    finally:tmp.unlink()
print(json.dumps(result))
