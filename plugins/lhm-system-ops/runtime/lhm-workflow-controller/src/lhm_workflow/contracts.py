from __future__ import annotations
import hashlib, json, re
from pathlib import Path

WORKFLOW_TYPE="seo-content-astro-v1"
STAGES={
 "seo_evidence":("claude",("lhm-marketing-hub:seo-audit",),("google_search_console.property_read",)),
 "content_production":("claude",("lhm-marketing-hub:seo-content-writer",),()),
 "site_implementation":("codex",("lhm-wordpress-hub:astro-build",),("repo.branch_write","preview.create")),
 "verification":("lhm_host_verifier",("lhm-system:workflow-verification",),("artifact.read","repo.read","preview.read")),
}
ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$"); SHA=re.compile(r"^[0-9a-f]{64}$")
class ContractError(ValueError): pass
def canonical_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def validate_contract(c):
 for k in ("workflow_id","workflow_type","stage_id","child_run_id","worker","required_skills","required_capabilities"):
  if k not in c: raise ContractError(f"missing {k}")
 if c["workflow_type"]!=WORKFLOW_TYPE or c["stage_id"] not in STAGES: raise ContractError("unknown workflow/stage")
 if not ID.fullmatch(c["workflow_id"]) or not ID.fullmatch(c["child_run_id"]): raise ContractError("invalid id")
 worker,skills,caps=STAGES[c["stage_id"]]
 if c["worker"]!=worker or tuple(c["required_skills"])!=skills or tuple(c["required_capabilities"])!=caps: raise ContractError("fixed contract mismatch")
 return c
def validate_artifact(a,root:Path):
 if set(a)!={"artifact_id","logical_name","media_type","size_bytes","sha256","purpose","path"} or not SHA.fullmatch(str(a.get("sha256",""))): raise ContractError("artifact schema")
 p=Path(a["path"])
 try: rp=p.resolve(strict=True); rr=root.resolve(strict=True)
 except OSError as e: raise ContractError("artifact missing") from e
 if p.is_symlink() or not rp.is_relative_to(rr) or not rp.is_file(): raise ContractError("artifact path")
 raw=rp.read_bytes()
 if len(raw)!=a["size_bytes"] or hashlib.sha256(raw).hexdigest()!=a["sha256"]: raise ContractError("artifact integrity")
 return a
def validate_connector(e):
 if e.get("observer")!="host-connector-adapter" or e.get("mutation") is not True or e.get("readback") is not True or not e.get("remote_id"): raise ContractError("connector readback")
 return e
def validate_site(e):
 if e.get("observer")!="host-site-adapter" or not re.fullmatch(r"[0-9a-f]{40}",e.get("commit","")) or not str(e.get("preview_url","")).startswith("https://") or e.get("preview_noindex") is not True or e.get("configured_checks") is not True: raise ContractError("site evidence")
 return e
