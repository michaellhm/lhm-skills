"""Read-only client readiness gate for governed Hermes workflows."""

from __future__ import annotations

import json
import re
import hashlib
import os
import stat
from pathlib import Path

SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEFAULT_VAULT = Path("/home/hermes/.hermes/profiles/lhm_brain/vault")


class ClientOnboardingRequired(ValueError):
    pass


def record_path(vault: Path, client_id: str) -> Path:
    if not SAFE_ID.fullmatch(client_id):
        raise ClientOnboardingRequired("client_onboarding_required: unsafe client_id")
    root = (vault / "_System/Hermes/clients").resolve()
    path = root / client_id / "capabilities.json"
    if not path.parent.resolve().is_relative_to(root):
        raise ClientOnboardingRequired("client_onboarding_required: client record escaped vault root")
    return path


def _safe_regular(path: Path, expected_uid: int, label: str) -> bytes:
    try:
        info = path.lstat()
    except OSError as exc:
        raise ClientOnboardingRequired(f"client_onboarding_required: missing {label}") from exc
    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
        raise ClientOnboardingRequired(f"client_onboarding_required: unsafe {label} type")
    if info.st_uid != expected_uid or info.st_mode & 0o077:
        raise ClientOnboardingRequired(f"client_onboarding_required: unsafe {label} owner or mode")
    return path.read_bytes()


def require_capability(vault: Path, client_id: str, capability: str, *, test_mode: bool = False) -> dict:
    path = record_path(vault, client_id)
    try:
        vault_info=vault.lstat()
    except OSError as exc:
        raise ClientOnboardingRequired("client_onboarding_required: missing canonical vault") from exc
    if vault.is_symlink() or not stat.S_ISDIR(vault_info.st_mode):
        raise ClientOnboardingRequired("client_onboarding_required: unsafe canonical vault type")
    # The synchronized Obsidian record is trusted only when it retains the
    # fixed vault owner's identity. Runtime evidence is a separate root-owned
    # trust boundary. Test mode explicitly substitutes the invoking UID for
    # both so fixtures do not require privilege.
    record_uid = os.getuid() if test_mode else vault_info.st_uid
    evidence_uid = os.getuid() if test_mode else 0
    try:
        record = json.loads(_safe_regular(path, record_uid, "client capability record"))
        client = record["client"]
        value = record["capabilities"][capability]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ClientOnboardingRequired(
            f"client_onboarding_required: invalid {capability} record"
        ) from exc
    if client.get("id") != client_id or value.get("status") != "verified":
        raise ClientOnboardingRequired(
            f"client_onboarding_required: {capability} is not verified; run hermes-client-onboarding"
        )
    required = ("route", "identifiers", "allowed_operations", "last_test")
    if any(not value.get(field) for field in required):
        raise ClientOnboardingRequired(
            f"client_onboarding_required: {capability} verification is incomplete"
        )
    last_test = value["last_test"]
    if (last_test.get("result") != "passed" or not last_test.get("evidence_ref")
            or not re.fullmatch(r"[0-9a-f]{64}", str(last_test.get("evidence_sha256", "")))):
        raise ClientOnboardingRequired(
            f"client_onboarding_required: {capability} has no passing evidence"
        )
    evidence_path = Path(last_test["evidence_ref"])
    if not evidence_path.is_absolute():
        raise ClientOnboardingRequired("client_onboarding_required: evidence_ref must be absolute")
    if evidence_path.resolve() != evidence_path:
        raise ClientOnboardingRequired("client_onboarding_required: capability evidence path contains a link")
    evidence_raw = _safe_regular(evidence_path, evidence_uid, "client capability evidence")
    if hashlib.sha256(evidence_raw).hexdigest() != last_test["evidence_sha256"]:
        raise ClientOnboardingRequired("client_onboarding_required: capability evidence hash mismatch")
    try:
        evidence = json.loads(evidence_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClientOnboardingRequired("client_onboarding_required: capability evidence is not JSON") from exc
    if capability == "google_search_console":
        prop = value["identifiers"].get("property")
        operations = value["allowed_operations"]
        binding = last_test.get("binding")
        expected_binding = {
            "client_id": client_id,
            "property": prop,
            "capability": "google_search_console.property_read",
            "allowed_operations": operations,
        }
        if binding != expected_binding:
            raise ClientOnboardingRequired("client_onboarding_required: GSC evidence binding is incomplete")
        requests=evidence.get("requests")
        if not isinstance(requests,dict):
            raise ClientOnboardingRequired("client_onboarding_required: GSC evidence has no structured requests")
        matched=False
        for record in requests.values():
            request=record.get("value") if isinstance(record,dict) else None
            if not isinstance(request,dict):
                continue
            capabilities=request.get("required_capabilities")
            if (request.get("profile")=="seo_gsc_readonly" and request.get("site_property")==prop
                    and isinstance(capabilities,list) and "google_search_console.property_read" in capabilities):
                matched=True; break
        if not matched:
            raise ClientOnboardingRequired("client_onboarding_required: GSC evidence property or capability binding mismatch")
    return value
