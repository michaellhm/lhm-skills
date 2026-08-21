"""Fixed SEO -> content -> Astro workflow progression."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

STAGES = (
    {"id":"seo_analysis","worker":{"runtime":"claude","identity":"lhm-marketing-hub:seo"},"required_skills":["lhm-marketing-hub:seo-audit"],"required_capabilities":["google_search_console.property_read"],"permission_ceiling":"green"},
    {"id":"content","worker":{"runtime":"claude","identity":"lhm-marketing-hub:content"},"required_skills":["lhm-marketing-hub:seo-content-writer"],"required_capabilities":[],"permission_ceiling":"green"},
    {"id":"astro","worker":{"runtime":"codex","identity":"codexworker"},"required_skills":["lhm-wordpress-hub:start-astro","lhm-wordpress-hub:astro-build"],"required_capabilities":["git.feature_branch_write","cloudflare.preview_readback"],"permission_ceiling":"amber"},
)

def _canonical(value: Any) -> bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def _safe(value: str, label: str) -> str:
    if not isinstance(value,str) or not SAFE_ID.fullmatch(value): raise ValueError(f"invalid {label}")
    return value

def _artifacts(items: Any, *, required: bool) -> list[dict]:
    if not isinstance(items,list) or (required and not items): raise ValueError("invalid artifacts")
    result=[]; seen=set()
    for item in items:
        if not isinstance(item,dict) or set(item)!={"artifact_id","sha256","media_type"}: raise ValueError("invalid artifact schema")
        _safe(item["artifact_id"],"artifact_id")
        if not isinstance(item["sha256"],str) or not SHA256.fullmatch(item["sha256"]): raise ValueError("invalid artifact hash")
        if not isinstance(item["media_type"],str) or not item["media_type"]: raise ValueError("invalid media_type")
        if item["artifact_id"] in seen: raise ValueError("duplicate artifact_id")
        seen.add(item["artifact_id"]); result.append(dict(item))
    return sorted(result,key=lambda x:x["artifact_id"])

def new_workflow(parent_run_id: str, objective: str) -> dict:
    _safe(parent_run_id,"parent_run_id")
    if not isinstance(objective,str) or not objective.strip(): raise ValueError("invalid objective")
    stages=[]
    for index,spec in enumerate(STAGES):
        stages.append({"id":spec["id"],"status":"ready" if index==0 else "pending","child_run_id":None,"idempotency_key":None,"input_artifacts":[],"output_artifacts":[],"receipt_id":None})
    return {"schema_version":1,"workflow_id":"seo-content-astro-v1","parent_run_id":parent_run_id,"objective":objective.strip(),"state":"ready_for_production","current_stage":"seo_analysis","stages":stages}

def issue_current(parent: dict, child_run_id: str) -> tuple[dict,dict]:
    _safe(child_run_id,"child_run_id"); updated=copy.deepcopy(parent)
    if updated.get("workflow_id")!="seo-content-astro-v1" or updated.get("state")!="ready_for_production": raise ValueError("workflow is not dispatchable")
    current=next((s for s in updated["stages"] if s["id"]==updated.get("current_stage")),None)
    if not current or current["status"]!="ready": raise ValueError("current stage is not ready")
    index=next(i for i,s in enumerate(STAGES) if s["id"]==current["id"]); inputs=[] if index==0 else _artifacts(updated["stages"][index-1]["output_artifacts"],required=True)
    seed={"parent_run_id":updated["parent_run_id"],"stage_id":current["id"],"child_run_id":child_run_id,"inputs":inputs}
    key=hashlib.sha256(_canonical(seed)).hexdigest(); spec=STAGES[index]
    current.update(status="running",child_run_id=child_run_id,idempotency_key=key,input_artifacts=inputs)
    updated["state"]="worker_running"
    contract={"schema_version":1,"workflow_id":updated["workflow_id"],"parent_run_id":updated["parent_run_id"],"stage_id":current["id"],"child_run_id":child_run_id,"idempotency_key":key,"worker":copy.deepcopy(spec["worker"]),"required_skills":list(spec["required_skills"]),"required_capabilities":list(spec["required_capabilities"]),"permission_ceiling":spec["permission_ceiling"],"input_artifacts":inputs}
    return updated,contract

def accept_receipt(parent: dict, receipt: dict) -> dict:
    updated=copy.deepcopy(parent)
    required={"schema_version","receipt_id","workflow_id","parent_run_id","stage_id","child_run_id","idempotency_key","worker","input_artifacts","output_artifacts","disposition"}
    if not isinstance(receipt,dict) or set(receipt)!=required or receipt.get("schema_version")!=1 or receipt.get("disposition")!="verified": raise ValueError("invalid receipt")
    for key in ("receipt_id","parent_run_id","stage_id","child_run_id"): _safe(receipt.get(key),key)
    if receipt["workflow_id"]!=updated.get("workflow_id") or receipt["parent_run_id"]!=updated.get("parent_run_id"): raise ValueError("workflow binding mismatch")
    index=next((i for i,s in enumerate(updated["stages"]) if s["id"]==receipt["stage_id"]),None)
    if index is None: raise ValueError("unknown stage")
    stage=updated["stages"][index]; spec=STAGES[index]
    if stage["status"]!="running" or receipt["child_run_id"]!=stage["child_run_id"] or receipt["idempotency_key"]!=stage["idempotency_key"]: raise ValueError("issued contract mismatch")
    if receipt["worker"]!=spec["worker"]: raise ValueError("worker identity mismatch")
    if _artifacts(receipt["input_artifacts"],required=index>0)!=stage["input_artifacts"]: raise ValueError("artifact dependency mismatch")
    outputs=_artifacts(receipt["output_artifacts"],required=True)
    stage.update(status="accepted",output_artifacts=outputs,receipt_id=receipt["receipt_id"])
    if index+1<len(updated["stages"]):
        updated["stages"][index+1]["status"]="ready"; updated["current_stage"]=updated["stages"][index+1]["id"]; updated["state"]="ready_for_production"
    else:
        updated["current_stage"]=None; updated["state"]="review_ready"
    return updated
