from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from .contracts import ContractError, validate_contract

class Ingestor:
 def __init__(self, quarantine:Path, processed:Path):
  self.quarantine=quarantine; self.processed=processed; quarantine.mkdir(parents=True,exist_ok=True); processed.mkdir(parents=True,exist_ok=True)
 def _quarantine(self,path,reason):
  target=self.quarantine/path.name
  os.replace(path,target); (target.with_suffix(target.suffix+".reason")).write_text(reason); return None
 def ingest_events(self,path:Path,contract:dict):
  try:
   validate_contract(contract); run=contract["child_run_id"]
   marker=self.processed/f"{run}.json"
   if marker.exists(): raise ContractError("replay")
   events=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
   if not events: raise ContractError("empty events")
   skills=set(); caps=set(); terminal=None
   for e in events:
    if e.get("source")!="host-dispatcher" or e.get("child_run_id")!=run: raise ContractError("untrusted event")
    if e.get("event")=="skill_tool_call": skills.add(e.get("skill"))
    if e.get("event")=="capability_observed": caps.add(e.get("capability"))
    if e.get("event")=="terminal": terminal=e.get("status")
   if not set(contract["required_skills"]).issubset(skills) or caps!=set(contract["required_capabilities"]) or terminal!="completed": raise ContractError("provenance incomplete")
   out={"child_run_id":run,"observed_skill_calls":sorted(skills),"observed_capabilities":sorted(caps),"status":terminal}
   fd,tmp=tempfile.mkstemp(dir=self.processed); os.close(fd); Path(tmp).write_text(json.dumps(out)); os.replace(tmp,marker); os.replace(path,self.processed/(path.name+".events")); return out
  except (OSError,json.JSONDecodeError,ContractError) as e: return self._quarantine(path,str(e))
