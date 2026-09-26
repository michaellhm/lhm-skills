"""Deterministic organisational routing for the governed weekly SEO run."""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
import re
import tempfile
import fcntl
import base64,subprocess
from pathlib import Path
from typing import Any

CRON_ID = "3994012c42ba"
WORKFLOW = "lhm-weekly-seo-org-v1"
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
HEX = re.compile(r"^[0-9a-f]{64}$")

ROLE_POLICY = {
    "chief_intake": ("lhm_chief_of_staff", "deterministic", [], []),
    "context": ("lhm_researcher", "hermes", [], ["canonical_sources.read"]),
    "context_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "production_plan": ("lhm_head_of_production", "deterministic", [], []),
    "seo_plan": ("lhm_seo_lead", "deterministic", ["lhm-seo-rollout"], []),
    "seo_plan_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "seo_accept": ("lhm_seo_lead", "deterministic", ["lhm-seo-rollout"], []),
    "research": ("lhm_researcher", "claude", ["lhm-marketing-hub:seo-audit"], ["google_search_console.property_read"]),
    "research_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "content": ("lhm_content", "claude", ["lhm-marketing-hub:seo-content-writer"], []),
    "content_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "website": ("lhm_website", "codex", ["lhm-wordpress-hub:start-astro", "lhm-wordpress-hub:astro-build"], ["git.feature_branch_write", "cloudflare.preview_readback"]),
    "website_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "final_verify": ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]),
    "operations_write": ("lhm_operations", "deterministic", ["lhm-knowledge-hub:obsidian-vault-manager"], ["knowledge.tracker_write"]),
    "operations_readback": ("lhm_operations", "deterministic", ["lhm-knowledge-hub:obsidian-vault-manager"], ["knowledge.tracker_readback"]),
    "learning": ("lhm_learning_steward", "deterministic", ["lhm-learn:learn"], []),
    "production_closeout": ("lhm_head_of_production", "deterministic", [], []),
    "chief_handback": ("lhm_chief_of_staff", "deterministic", [], ["telegram.governed_delivery"]),
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _id(value: str, label: str) -> str:
    if not isinstance(value, str) or not SAFE.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _artifact(item: dict) -> dict:
    if not isinstance(item, dict) or set(item) != {"artifact_id", "sha256", "media_type"}:
        raise ValueError("invalid artifact")
    _id(item["artifact_id"], "artifact_id")
    if not HEX.fullmatch(str(item["sha256"])) or not isinstance(item["media_type"], str) or not item["media_type"]:
        raise ValueError("invalid artifact")
    return dict(item)


def intake(cron_event: dict, parent_run_id: str) -> dict:
    """Chief of Staff accepts only the alternate no-delivery cron envelope."""
    if set(cron_event) != {"source", "source_cron_id", "job_name", "prompt", "delivery", "triggered_at"}:
        raise ValueError("invalid cron intake fields")
    if cron_event["source"] != "hermes-cron-alternate" or cron_event["source_cron_id"] != CRON_ID:
        raise ValueError("untrusted cron source")
    if cron_event["delivery"] != "none":
        raise ValueError("cron delivery must be disabled")
    if not isinstance(cron_event["prompt"], str) or not cron_event["prompt"].strip():
        raise ValueError("empty cron objective")
    _id(parent_run_id, "parent_run_id")
    stages = ["chief_intake", "production_plan", "seo_plan", "research", "research_verify", "seo_accept"]
    ROLE_POLICY.setdefault("research_verify", ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]))
    return {"schema_version": 1, "workflow_id": WORKFLOW, "parent_run_id": parent_run_id,
            "source_cron_id": CRON_ID, "objective": cron_event["prompt"].strip(), "state": "ready",
            "stage_order": stages, "cursor": 0, "stages": [], "delivery": {"channel": "suppressed_canary", "status": "blocked"}}


def _inputs(parent: dict) -> list[dict]:
    if not parent["stages"]:
        return []
    return [_artifact(x) for x in parent["stages"][-1]["outputs"]]


def issue(parent: dict, child_run_id: str) -> tuple[dict, dict]:
    updated = copy.deepcopy(parent); _id(child_run_id, "child_run_id")
    if updated.get("state")=="running" and updated.get("stages") and updated["stages"][-1].get("child_run_id")==child_run_id:
        return updated,copy.deepcopy(updated["stages"][-1]["contract"])
    if updated.get("workflow_id") != WORKFLOW or updated.get("state") != "ready":
        raise ValueError("workflow not dispatchable")
    stage_id = updated["stage_order"][updated["cursor"]]
    role, runtime, skills, capabilities = ROLE_POLICY[stage_id]
    inputs = _inputs(updated)
    key = digest({"parent": updated["parent_run_id"], "stage": stage_id, "child": child_run_id, "inputs": inputs})
    contract = {"schema_version": 1, "workflow_id": WORKFLOW, "parent_run_id": updated["parent_run_id"],
                "stage_id": stage_id, "child_run_id": child_run_id, "idempotency_key": key,
                "owner": role, "runtime": runtime, "required_skills": list(skills),
                "required_capabilities": list(capabilities), "input_artifacts": inputs,
                "permission_ceiling": "amber" if stage_id == "website" else "green"}
    updated["stages"].append({"stage_id": stage_id, "child_run_id": child_run_id, "status": "running",
                              "contract_sha256": digest(contract), "contract":copy.deepcopy(contract), "outputs": [],"retry_count":0})
    updated["state"] = "running"
    return updated, contract


def _unsigned(receipt: dict) -> dict:
    return {key:value for key,value in receipt.items() if key != "attestation"}


def seal(receipt: dict, key: bytes) -> dict:
    value=copy.deepcopy(receipt)
    value["attestation"]={"algorithm":"hmac-sha256","signature":hmac.new(key,canonical(_unsigned(value)),hashlib.sha256).hexdigest()}
    return value

def verify_attestation(receipt:dict,key)->bool:
    attestation=receipt.get("attestation")
    if isinstance(key,(str,Path)):
        if not isinstance(attestation,dict) or attestation.get("algorithm")!="ed25519": return False
        try: signature=base64.b64decode(attestation.get("signature",""),validate=True)
        except Exception: return False
        fd,path=tempfile.mkstemp(prefix="lhm-signature-"); data_fd,data_path=tempfile.mkstemp(prefix="lhm-signed-data-")
        try:
            os.write(fd,signature); os.close(fd); os.write(data_fd,canonical(_unsigned(receipt))); os.close(data_fd)
            done=subprocess.run(["openssl","pkeyutl","-verify","-pubin","-inkey",str(key),"-rawin","-in",data_path,"-sigfile",path],capture_output=True)
            return done.returncode==0
        finally:
            try: os.close(fd)
            except OSError: pass
            Path(path).unlink(missing_ok=True)
            Path(data_path).unlink(missing_ok=True)
    expected=hmac.new(key or b"",canonical(_unsigned(receipt)),hashlib.sha256).hexdigest()
    return bool(key and isinstance(attestation,dict) and set(attestation)=={"algorithm","signature"} and attestation["algorithm"]=="hmac-sha256" and hmac.compare_digest(str(attestation["signature"]),expected))


def accept(parent: dict, contract: dict, receipt: dict, *, attestation_keys: dict[str,bytes] | None = None) -> dict:
    updated = copy.deepcopy(parent)
    attestation_keys = attestation_keys or {}
    required = {"schema_version", "workflow_id", "parent_run_id", "stage_id", "child_run_id",
                "contract_sha256", "status", "owner", "checks", "output_artifacts", "decision", "attestation"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt["schema_version"] != 1:
        raise ValueError("invalid organisational receipt")
    if receipt["status"] != "accepted" or receipt["contract_sha256"] != digest(contract):
        raise ValueError("receipt not bound to contract")
    for key in ("workflow_id", "parent_run_id", "stage_id", "child_run_id"):
        if receipt[key] != contract[key]: raise ValueError("receipt binding mismatch")
    if (receipt["owner"] != contract["owner"] or not isinstance(receipt["checks"], list) or not receipt["checks"]
            or not all(isinstance(check,str) and re.fullmatch(r"[a-z][a-z0-9_.:-]*",check) for check in receipt["checks"])):
        raise ValueError("owner or checks mismatch")
    attestation=receipt.get("attestation"); key=attestation_keys.get(contract["owner"])
    if not verify_attestation(receipt,key):
        raise ValueError("invalid service attestation")
    outputs = [_artifact(item) for item in receipt["output_artifacts"]]
    prior=next((item for item in updated["stages"] if item["contract_sha256"]==digest(contract) and item["status"]=="accepted"),None)
    if prior is not None:
        if prior["outputs"] != outputs: raise ValueError("conflicting receipt replay")
        return updated
    current = updated["stages"][-1]
    if current["status"] != "running" or current["contract_sha256"] != digest(contract):
        raise ValueError("stage is not current")
    current.update(status="accepted", outputs=outputs)
    stage = contract["stage_id"]
    decision = receipt["decision"]
    if contract["runtime"] == "verifier" and outputs != contract["input_artifacts"]:
        raise ValueError("verifier must preserve exact input evidence")
    if stage == "operations_readback" and outputs != contract["input_artifacts"]:
        raise ValueError("operations readback must preserve exact written tracker artifact")
    if stage == "chief_handback":
        acceptable=("governed_delivery_suppressed_canary" if updated["delivery"]["channel"]=="suppressed_canary" else "governed_delivery_readback")
        if acceptable not in receipt["checks"]: raise ValueError("chief handback lacks governed delivery assurance")
        updated["delivery"]["status"]="suppressed" if updated["delivery"]["channel"]=="suppressed_canary" else "verified"
    if stage == "seo_accept":
        if (set(decision) != {"content_required", "website_required", "reason"}
                or not all(isinstance(decision[k], bool) for k in ("content_required", "website_required"))
                or not isinstance(decision["reason"], str) or not decision["reason"].strip()):
            raise ValueError("invalid SEO Lead decision")
        tail = []
        if decision["content_required"]: tail += ["content", "content_verify"]
        if decision["website_required"]: tail += ["website", "website_verify"]
        tail += ["final_verify", "production_closeout", "chief_handback", "operations_write", "operations_readback", "learning"]
        # Verification stages have a fixed independent owner and no worker skill claims.
        for verifier in ("research_verify", "content_verify", "website_verify", "final_verify"):
            ROLE_POLICY.setdefault(verifier, ("lhm_verifier", "verifier", ["lhm-system:workflow-verification"], ["artifact.readback"]))
        updated["stage_order"] = ["chief_intake", "production_plan", "seo_plan", "research", "research_verify", "seo_accept"] + tail
    elif decision not in ({}, None):
        raise ValueError("unexpected stage decision")
    updated["cursor"] += 1
    if updated["cursor"] == len(updated["stage_order"]):
        updated["state"] = "closed"
    else:
        updated["state"] = "ready"
    return updated


def receipt(contract: dict, *, outputs: list[dict], checks: list[str], decision: dict | None = None) -> dict:
    """Construct the exact receipt envelope; production receipts remain externally verified."""
    return {"schema_version": 1, "workflow_id": contract["workflow_id"], "parent_run_id": contract["parent_run_id"],
            "stage_id": contract["stage_id"], "child_run_id": contract["child_run_id"],
            "contract_sha256": digest(contract), "status": "accepted", "owner": contract["owner"],
            "checks": list(checks), "output_artifacts": list(outputs), "decision": {} if decision is None else decision,
            "attestation": None}


class Router:
    """Atomic persistent wrapper with exact-once accept, failure, and repair."""
    def __init__(self, root: Path, keys: dict[str,bytes]): self.root=root; self.keys=keys
    def _path(self,parent): return self.root/"parents"/f"{_id(parent,'parent')}.json"
    def _atomic(self,path,value):
        path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=f".{path.name}.")
        try:
            with os.fdopen(fd,"wb") as f: f.write(canonical(value)+b"\n"); f.flush(); os.fsync(f.fileno())
            os.chmod(tmp,0o600); os.replace(tmp,path)
        finally: Path(tmp).unlink(missing_ok=True)
    def _locked(self,parent):
        self.root.mkdir(parents=True,exist_ok=True); lock=self.root/f".{parent}.lock"; lock.touch(mode=0o600,exist_ok=True)
        handle=lock.open("r+"); fcntl.flock(handle,fcntl.LOCK_EX); return handle
    def initialise(self,event,parent):
        with self._locked(parent):
            path=self._path(parent); value=intake(event,parent)
            if path.exists():
                old=json.loads(path.read_text());
                if old!=value: raise ValueError("conflicting intake")
                return old
            self._atomic(path,value); return value
    def load(self,parent): return json.loads(self._path(parent).read_text())
    def issue(self,parent,child):
        with self._locked(parent):
            value,contract=issue(self.load(parent),child); self._atomic(self._path(parent),value); return contract
    def accept(self,parent,contract,value):
        receipt_id=digest(value); marker=self.root/"receipts"/f"{receipt_id}.json"
        binding=self.root/"accepted-contracts"/f"{digest(contract)}.json"
        with self._locked(parent):
            if marker.exists(): return self.load(parent)
            if binding.exists():
                prior=json.loads(binding.read_text())
                if prior.get("receipt_sha256")!=receipt_id: raise ValueError("conflicting signed receipt replay")
                return self.load(parent)
            updated=accept(self.load(parent),contract,value,attestation_keys=self.keys)
            self._atomic(self._path(parent),updated); self._atomic(marker,{"parent_run_id":parent,"receipt_sha256":receipt_id}); self._atomic(binding,{"parent_run_id":parent,"receipt_sha256":receipt_id}); return updated
    def fail(self,parent,contract,reason,attestation):
        with self._locked(parent):
            value=self.load(parent); current=value["stages"][-1]
            if current["status"]=="failed": return value
            if current["status"]!="running" or current["contract_sha256"]!=digest(contract): raise ValueError("failure cannot rewind stage")
            proof={"parent_run_id":parent,"contract_sha256":digest(contract),"reason":reason}
            expected=hmac.new(self.keys.get(contract["owner"],b""),canonical(proof),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(attestation,expected): raise ValueError("invalid failure attestation")
            current["retry_count"]=current.get("retry_count",0)+1
            current.update(status="failed",failure=reason,failure_receipt_sha256=digest({**proof,"attestation":attestation}))
            value["state"]=("needs_consequential_approval" if contract.get("permission_ceiling")=="amber"
                            else "needs_repair" if current["retry_count"]==1 else "incident")
            self._atomic(self._path(parent),value); return value
    def resume(self,parent,production_attestation=None):
        with self._locked(parent):
            value=self.load(parent)
            if value["state"] in {"ready","running"}: return value
            if value["state"]=="needs_consequential_approval": raise ValueError("consequential amber failure requires Michael approval")
            if value["state"]=="incident": raise ValueError("retry budget exhausted; capability incident")
            if value["state"]!="needs_repair" or value["stages"][-1]["status"]!="failed": raise ValueError("not repairable")
            proof={"parent_run_id":parent,"contract_sha256":value["stages"][-1]["contract_sha256"],"failure_receipt_sha256":value["stages"][-1]["failure_receipt_sha256"],"action":"resume"}
            expected=hmac.new(self.keys.get("lhm_head_of_production",b""),canonical(proof),hashlib.sha256).hexdigest()
            if not production_attestation or not hmac.compare_digest(production_attestation,expected):
                raise ValueError("Production attestation required for repair authorization")
            value["stages"][-1]["status"]="running"; value["stages"][-1].pop("failure",None); value["state"]="running"
            self._atomic(self._path(parent),value); return value
