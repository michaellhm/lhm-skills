"""Closed SEO-01 capability envelope and fail-fast transition guard.

This module is package source only.  It does not start services or call connectors.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re

TRACKER_PATH = "30 Projects/LHM Growth/LHM Website SEO Growth Rollout/rollout-state.md"
MARKETING_HUB = {
    "name": "lhm-marketing-hub",
    "version": "2.2.2",
    "archive_sha256": "61b46faa9105e45c517bdd6d1de78ebee458887896ac7b31eb92c46b959df7ac",
    "skills": [
        {"id": "keyword-research", "sha256": "0c00eb58c4bc6c829545fa2def4558299f18577d30d7c5009380ab6613ea617a"},
        {"id": "seo-delivery-qa", "sha256": "cf11a40e0479b41229363768cf98b9edd28959167f62ab1c0a269efda09e18e1"},
    ],
}
GSC = {"client_id": "local-health-marketing", "property": "https://localhealthmarketing.com/", "operations": ["list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"], "mode": "read_only"}
DRIVE = {"folder_id": "1t3aUHy1ZSMiHophhJQsQC-cDjcZiMxUA", "relative_root": "seo/", "extension": ".md", "operations": ["file_create", "file_readback"], "overwrite": False}
BASICOPS = {"workspace_id": "481630853364967730", "project_id": "49020", "section_id": "74627", "task_id": "2192596", "operations": ["task_read", "discussion_create", "discussion_readback"], "subtasks": False}
UNAVAILABLE = {"keywords_everywhere": "unavailable", "google_ads": "unavailable"}
STAGES = ("keyword-research", "seo-delivery-qa", "lead-acceptance", "canonical-projection", "drive-projection", "basicops-projection", "stopped")
HEX = re.compile(r"^[0-9a-f]{64}$")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def envelope(parent_run_id: str, version: int = 1) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,119}", parent_run_id) or version != 1:
        raise ValueError("invalid parent/version")
    value = {"schema_version": 1, "parent_run_id": parent_run_id, "action_id": "SEO-01", "action_version": version, "tracker": {"path": TRACKER_PATH, "operations": ["cas_write", "exact_readback"]}, "marketing_hub": copy.deepcopy(MARKETING_HUB), "gsc": copy.deepcopy(GSC), "drive": copy.deepcopy(DRIVE), "basicops": copy.deepcopy(BASICOPS), "unavailable_evidence": copy.deepcopy(UNAVAILABLE), "degraded_evidence_required": True, "permission_ceiling": "read_gsc_create_markdown_and_discussion", "services_enabled": False, "retry_limit": 1, "incident_limit": 1}
    value["envelope_sha256"] = digest(value)
    return value


def validate(value: dict) -> dict:
    if not isinstance(value, dict) or value != envelope(value.get("parent_run_id", ""), value.get("action_version")):
        raise ValueError("SEO capability envelope mismatch")
    return copy.deepcopy(value)


def new_state(bound_envelope: dict) -> dict:
    e = validate(bound_envelope)
    return {"schema_version": 1, "parent_run_id": e["parent_run_id"], "action_id": "SEO-01", "action_version": 1, "envelope_sha256": e["envelope_sha256"], "stage": STAGES[0], "keyword_artifact": None, "qa_receipt": None, "lead_receipt": None, "projections": {}, "retry_count": 0, "incident": None, "failure_receipt": None}


def _binding(state, value):
    expected = (state["parent_run_id"], state["action_id"], state["action_version"], state["envelope_sha256"])
    observed = tuple(value.get(k) for k in ("parent_run_id", "action_id", "action_version", "envelope_sha256"))
    if observed != expected:
        raise ValueError("parent/version/envelope binding mismatch")


def dispatch(state: dict, bound_envelope: dict) -> dict:
    e = validate(bound_envelope); _binding(state, e)
    if state["stage"] not in {"keyword-research", "seo-delivery-qa"}:
        raise ValueError("stage is not specialist-dispatchable")
    skill = state["stage"]
    if skill == "seo-delivery-qa" and state["keyword_artifact"] is None:
        raise ValueError("durable keyword artefact required before QA")
    return {"parent_run_id": state["parent_run_id"], "action_id": "SEO-01", "action_version": 1, "envelope_sha256": e["envelope_sha256"], "skill": skill, "accepted_input": copy.deepcopy(state["keyword_artifact"]), "gsc": copy.deepcopy(e["gsc"]) if skill == "keyword-research" else None, "unavailable_evidence": copy.deepcopy(UNAVAILABLE), "degraded_evidence": True, "extra_authority": []}


def accept_keyword(state: dict, receipt: dict) -> dict:
    if state["stage"] != "keyword-research": raise ValueError("keyword receipt out of sequence")
    _binding(state, receipt)
    required = {"parent_run_id", "action_id", "action_version", "envelope_sha256", "skill", "artifact_id", "sha256", "drive_folder_id", "relative_path", "media_type", "readback_sha256", "degraded_evidence", "unavailable_evidence"}
    if set(receipt) != required or receipt["skill"] != "keyword-research" or receipt["drive_folder_id"] != DRIVE["folder_id"] or not receipt["relative_path"].startswith("seo/") or not receipt["relative_path"].endswith(".md") or ".." in receipt["relative_path"].split("/") or receipt["media_type"] != "text/markdown" or not HEX.fullmatch(str(receipt["sha256"])) or receipt["readback_sha256"] != receipt["sha256"] or receipt["degraded_evidence"] is not True or receipt["unavailable_evidence"] != UNAVAILABLE:
        raise ValueError("invalid durable degraded keyword artefact")
    updated = copy.deepcopy(state); updated["keyword_artifact"] = copy.deepcopy(receipt); updated["stage"] = "seo-delivery-qa"; return updated


def accept_qa(state: dict, receipt: dict) -> dict:
    if state["stage"] != "seo-delivery-qa" or state["keyword_artifact"] is None: raise ValueError("QA out of sequence")
    _binding(state, receipt)
    required = {"parent_run_id", "action_id", "action_version", "envelope_sha256", "skill", "decision", "artifact_sha256", "readback_sha256", "degraded_evidence_verified", "extra_authority"}
    if set(receipt) != required or receipt["skill"] != "seo-delivery-qa" or receipt["decision"] != "pass" or receipt["artifact_sha256"] != digest(state["keyword_artifact"]) or not HEX.fullmatch(str(receipt["readback_sha256"])) or receipt["degraded_evidence_verified"] is not True or receipt["extra_authority"] != []:
        raise ValueError("invalid SEO delivery QA receipt")
    updated=copy.deepcopy(state);updated["qa_receipt"]=copy.deepcopy(receipt);updated["stage"]="lead-acceptance";return updated


def accept_lead(state: dict, receipt: dict) -> dict:
    if state["stage"] != "lead-acceptance": raise ValueError("Lead acceptance out of sequence")
    _binding(state, receipt)
    if set(receipt) != {"parent_run_id","action_id","action_version","envelope_sha256","decision","qa_receipt_sha256"} or receipt["decision"] != "accepted" or receipt["qa_receipt_sha256"] != digest(state["qa_receipt"]): raise ValueError("invalid Lead acceptance")
    updated=copy.deepcopy(state);updated["lead_receipt"]=copy.deepcopy(receipt);updated["stage"]="canonical-projection";return updated


def accept_projection(state: dict, receipt: dict) -> dict:
    kinds={"canonical-projection": "canonical", "drive-projection": "drive", "basicops-projection": "basicops"}
    kind=kinds.get(state["stage"])
    if kind is None: raise ValueError("projection out of sequence")
    _binding(state, receipt)
    required={"parent_run_id","action_id","action_version","envelope_sha256","projection","destination","source_sha256","readback_sha256","operation"}
    destination={"canonical":TRACKER_PATH,"drive":DRIVE["folder_id"],"basicops":BASICOPS["task_id"]}[kind]
    operation={"canonical":"cas_write_exact_readback","drive":"create_md_exact_readback","basicops":"discussion_create_exact_readback"}[kind]
    if set(receipt)!=required or receipt["projection"]!=kind or receipt["destination"]!=destination or receipt["operation"]!=operation or receipt["source_sha256"]!=digest(state["lead_receipt"]) or not HEX.fullmatch(str(receipt["readback_sha256"])): raise ValueError("projection binding/readback mismatch")
    updated=copy.deepcopy(state);updated["projections"][kind]=copy.deepcopy(receipt);updated["stage"]={"canonical":"drive-projection","drive":"basicops-projection","basicops":"stopped"}[kind];return updated


def fail_fast(state: dict, reason: str, *, same_key_safe: bool) -> dict:
    if not isinstance(reason,str) or not reason.strip(): raise ValueError("failure reason required")
    updated=copy.deepcopy(state)
    if same_key_safe and updated["retry_count"] < 1 and updated["incident"] is None:
        updated["retry_count"] += 1
    else:
        incident_id=f"CII-20260824-seo-lead-capability-envelope:{updated['parent_run_id']}"
        if updated["incident"] is not None and updated["incident"].get("incident_id") != incident_id: raise ValueError("conflicting incident")
        if updated["incident"] is None: updated["incident"]={"incident_id":incident_id,"parent_run_id":updated["parent_run_id"],"immutable":True,"diagnostic_redispatch":False,"search_loop":False}
    updated["failure_receipt"]={"parent_run_id":updated["parent_run_id"],"action_id":"SEO-01","action_version":1,"envelope_sha256":updated["envelope_sha256"],"reason_sha256":hashlib.sha256(reason.strip().encode()).hexdigest(),"retry_count":updated["retry_count"],"incident_id":updated["incident"]["incident_id"] if updated["incident"] else None,"persist_immediately":True}
    return updated
