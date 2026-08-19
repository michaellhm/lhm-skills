#!/usr/bin/env python3
"""Governed campaign evidence bridge. Connector bodies never enter operational logs."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

DRIVE_URL = re.compile(r"https://drive\.google\.com/drive/folders/([A-Za-z0-9_-]+)")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")
SAFE_RUN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
INCIDENT = {
    "status": "waiting_on_capability",
    "capability_incident_id": "campaign-evidence-bridge-20260818",
    "parent": "campaign-playbook-flow-20260818-01",
    "return_point": "head_of_production.release_and_live_test",
    "resume_token": "campaign-playbook-flow-20260818-resume-01",
}


class CapabilityUnavailable(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.result = {**INCIDENT, "reason": reason}


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def exact_json(value, keys, profile=None):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("request fields do not match the persisted contract")
    if value.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    if profile and value.get("profile") != profile:
        raise ValueError("incorrect profile")
    return value


def load_registration(root, run_id):
    if not isinstance(run_id, str) or not SAFE_RUN.fullmatch(run_id):
        raise ValueError("invalid run_id")
    path = Path(root) / (run_id + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    stat = path.stat()
    if stat.st_uid != 0 or stat.st_mode & 0o007:
        raise PermissionError("registration must be root-owned and not world accessible")
    return data


def require_registered(registration, field, identifier):
    if not isinstance(identifier, (str, int)) or str(registration.get(field)) != str(identifier):
        raise CapabilityUnavailable("requested identifier is not exactly registered")


def discover_client_folder(overview, client, drive):
    """Canonical overview first; search only if its Systems and files section has no folder."""
    text = Path(overview).read_text(encoding="utf-8")
    section = re.search(r"(?ims)^#{1,6}\s+Systems and files\s*$\n(.*?)(?=^#{1,6}\s|\Z)", text)
    matches = DRIVE_URL.findall(section.group(1) if section else "")
    if len(matches) == 1:
        metadata = drive.get_file_metadata(matches[0])
        if metadata.get("id") != matches[0] or metadata.get("mime_type") != "application/vnd.google-apps.folder":
            raise CapabilityUnavailable("canonical client folder failed metadata verification")
        return matches[0], False
    if len(matches) > 1:
        raise CapabilityUnavailable("canonical client folder is ambiguous")
    found = drive.search_folders_exact(client)
    if len(found) != 1:
        raise CapabilityUnavailable("exact-name client folder discovery was missing or ambiguous")
    folder_id = found[0].get("id")
    metadata = drive.get_file_metadata(folder_id)
    if not SAFE_ID.fullmatch(str(folder_id)) or metadata.get("id") != folder_id or metadata.get("name") != client or metadata.get("mime_type") != "application/vnd.google-apps.folder":
        raise CapabilityUnavailable("discovered client folder failed exact metadata verification")
    heading = "## Systems and files"
    link = f"https://drive.google.com/drive/folders/{folder_id}"
    updated = text.rstrip() + (f"\n\n{heading}\n" if not section else "\n") + f"- Google Drive folder: {link}\n"
    _atomic_text(Path(overview), updated.encode(), 0o640)
    return folder_id, True


def drive_exact_read(request, registration, gateway, run_root):
    keys = ("schema_version run_id profile agent_id client file_id timeout_seconds").split()
    exact_json(request, keys, "google_drive_exact_file_read")
    if request["agent_id"] != "lhm-connector-repair": raise ValueError("incorrect agent_id")
    require_registered(registration, "drive_source_file_id", request["file_id"])
    raw, mime = gateway.read_exact_file(request["file_id"], request["timeout_seconds"])
    output = bounded_artifact(run_root, request["run_id"], "drive-source.bin", raw)
    return {"schema_version":1,"verification":"verified","file_id":request["file_id"],"mime_type":mime,
            "byte_count":len(raw),"sha256":sha256_bytes(raw),"content_file":str(output),"error":None}


def fathom_exact_read(request, registration, gateway, run_root):
    keys = ("schema_version run_id profile agent_id client recording_id timeout_seconds").split()
    exact_json(request, keys, "fathom_exact_recording_read")
    require_registered(registration, "fathom_recording_id", request["recording_id"])
    raw = gateway.get_meeting_transcript(recording_id=request["recording_id"], timeout=request["timeout_seconds"])
    if isinstance(raw, str): raw = raw.encode()
    output = bounded_artifact(run_root, request["run_id"], "fathom-source.txt", raw)
    return {"schema_version":1,"verification":"verified","recording_id":request["recording_id"],
            "byte_count":len(raw),"sha256":sha256_bytes(raw),"content_file":str(output),"error":None}


def produce(request, gateway, run_root):
    keys = ("schema_version run_id profile agent_id client drive_source_file drive_source_sha256 fathom_source_file fathom_source_sha256 output_file_name timeout_seconds").split()
    exact_json(request, keys, "campaign_playbook_production")
    if request["agent_id"] != "lhm-marketing-hub:content": raise ValueError("incorrect content agent")
    drive = verified_artifact(run_root, request["run_id"], request["drive_source_file"], request["drive_source_sha256"])
    fathom = verified_artifact(run_root, request["run_id"], request["fathom_source_file"], request["fathom_source_sha256"])
    raw = gateway.produce_campaign_playbook(drive, fathom, request["output_file_name"], request["timeout_seconds"])
    if isinstance(raw, str): raw = raw.encode()
    if not raw.strip(): raise CapabilityUnavailable("content production returned an empty artifact")
    output = bounded_artifact(run_root, request["run_id"], request["output_file_name"], raw)
    return {"schema_version":1,"verification":"verified","output_file":str(output),"byte_count":len(raw),"sha256":sha256_bytes(raw),"error":None}


def publish(request, registration, drive, run_root):
    keys = ("schema_version run_id profile agent_id client folder_id file_name content_file content_sha256 timeout_seconds").split()
    exact_json(request, keys, "google_drive_exact_folder_publish")
    require_registered(registration, "destination_drive_folder_id", request["folder_id"])
    content = verified_artifact(run_root, request["run_id"], request["content_file"], request["content_sha256"])
    matches = drive.search_exact_name(request["folder_id"], request["file_name"])
    if len(matches) > 1: raise CapabilityUnavailable("multiple exact-name destination files exist")
    if matches:
        file_id = matches[0]["id"]
        existing = drive.read_file_content(file_id)
        if isinstance(existing, str): existing = existing.encode()
        if existing != content:
            return {"schema_version":1,"status":"refused","file_id":file_id,"folder_id":request["folder_id"],
                    "file_name":request["file_name"],"byte_count":len(content),"sha256":sha256_bytes(content),
                    "error":"differing existing content"}
        status = "already_existed"
    else:
        file_id = drive.create_file(request["folder_id"], request["file_name"], content)
        status = "created"
    metadata = drive.get_file_metadata(file_id)
    readback = drive.read_file_content(file_id)
    if isinstance(readback, str): readback = readback.encode()
    if metadata.get("id") != file_id or metadata.get("name") != request["file_name"] or metadata.get("parent_id") != request["folder_id"] or readback != content:
        raise CapabilityUnavailable("Drive metadata or full-content read-back verification failed")
    return {"schema_version":1,"status":status,"file_id":file_id,"folder_id":request["folder_id"],
            "file_name":request["file_name"],"byte_count":len(content),"sha256":sha256_bytes(content),"error":None}


def bounded_artifact(root, run_id, name, raw):
    base = (Path(root) / run_id).resolve(); base.mkdir(parents=True, exist_ok=True)
    if Path(name).name != name: raise ValueError("artifact name must be a basename")
    target = (base / name).resolve()
    if target.parent != base: raise ValueError("artifact escaped run root")
    _atomic_text(target, raw, 0o640); return target


def verified_artifact(root, run_id, supplied, expected):
    base = (Path(root) / run_id).resolve(); path = Path(supplied).resolve()
    if path.parent != base or not path.is_file(): raise ValueError("source is not a bounded run artifact")
    raw = path.read_bytes()
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or sha256_bytes(raw) != expected: raise ValueError("artifact SHA-256 mismatch")
    return raw


def safe_log(result):
    allowed = {"status","verification","file_id","recording_id","folder_id","file_name","byte_count","sha256","error"}
    return {key: result[key] for key in result.keys() & allowed}


def _atomic_text(path, raw, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(raw)
        os.chmod(tmp, mode); os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
