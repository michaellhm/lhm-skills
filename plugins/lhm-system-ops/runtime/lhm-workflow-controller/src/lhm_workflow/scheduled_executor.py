"""Durable, disabled-by-default executor for registered scheduled parents.

Bots receive bounded snapshots and write closed JSON results.  They never receive signing
keys, tracker write access, deployment authority, or Search Console mutation authority.
"""
from __future__ import annotations

import hashlib
import argparse
import json
import os
import re
import stat
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable

from .org_routing import ROLE_POLICY, Router, digest
from .scheduled_work import normalise_urls

DEFAULT_ROOT = Path("/var/lib/lhm-workflow")
HOST_HANDOFF_ROOT = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch/scheduled-executor")
URL = re.compile(r"(?:https://localhealthmarketing\.com)?/[A-Za-z0-9][A-Za-z0-9_./-]*")
BOT_STAGES = {"chief_intake", "context", "research", "production_plan", "seo_plan", "seo_accept", "content", "website", "production_closeout", "chief_handback", "operations_write", "operations_readback", "learning"}
DOCKER = "/usr/bin/docker"
CONTAINER = "hermes"
CONTAINER_USER = "10000:10000"
ADAPTER = "/usr/local/libexec/lhm-workflow-registered-adapter"
DISPATCH = "/opt/data/profiles/lhm_brain/bin/claude-dispatch"
WORK_CONTROL_CONTAINER = "/opt/data/profiles/lhm_brain/bin/work-control"
PROFILE_ROOT = "/opt/data/profiles/lhm_brain"
PROFILE_NAMES = {
    "lhm_chief_of_staff": "lhm_chief_of_staff", "lhm_production": "lhm_production",
    "lhm_seo": "lhm_seo", "lhm_researcher": "lhm_researcher", "lhm_content": "lhm_content",
    "lhm_website": "lhm_website", "lhm_verifier": "lhm_verifier",
    "lhm_operations": "lhm_operations_connector", "lhm_learning_steward": "lhm_learning_steward",
}
RESULT_FIELDS = {"schema_version", "parent_run_id", "child_run_id", "role", "request_sha256", "status", "artifact_hashes", "decision"}


def atomic_json(path: Path, value: object, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o750)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":")); handle.write("\n")
            handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, mode); os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def artifact(path: Path, artifact_id: str) -> dict:
    data = path.read_bytes()
    return {"artifact_id": artifact_id, "path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "media_type": "application/json"}


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_closed_result(path: Path, contract: dict, request_sha256: str, *, prior_result_sha256: str | None = None) -> dict:
    """Accept only a new, exact, request-bound result from the named child role."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("closed result is absent or not a regular file")
    raw = path.read_bytes(); result_sha256 = hashlib.sha256(raw).hexdigest()
    if prior_result_sha256 and result_sha256 == prior_result_sha256:
        raise ValueError("stale result replay")
    try: value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise ValueError("malformed closed result") from exc
    if not isinstance(value, dict) or set(value) != RESULT_FIELDS or value["schema_version"] != 1:
        raise ValueError("malformed closed result")
    expected = (contract["parent_run_id"], contract["child_run_id"], contract["owner"], request_sha256)
    if (value["parent_run_id"], value["child_run_id"], value["role"], value["request_sha256"]) != expected:
        raise ValueError("closed result binding mismatch")
    if value["status"] != "accepted" or not isinstance(value["decision"], dict):
        raise ValueError("closed result not accepted")
    hashes = value["artifact_hashes"]
    if not isinstance(hashes, list) or any(not re.fullmatch(r"[0-9a-f]{64}", str(item)) for item in hashes):
        raise ValueError("invalid artifact hashes")
    return {"value": value, "result_sha256": result_sha256}


def hermes_argv(profile: str, container_run_dir: str, prompt: str) -> list[str]:
    """The sole allowlisted Hermes invocation: fixed container, numeric owner and profile path."""
    if profile not in PROFILE_NAMES:
        raise ValueError("unregistered Hermes profile")
    expected_root = f"/opt/data/profiles/{PROFILE_NAMES[profile]}/dispatch/scheduled-executor/"
    if not container_run_dir.startswith(expected_root):
        raise ValueError("handoff outside role profile")
    toolsets = "file,code_execution" if profile == "lhm_verifier" else "file"
    return [DOCKER, "exec", "-i", "--user", CONTAINER_USER, CONTAINER,
            "/opt/hermes/bin/hermes", "-p", PROFILE_NAMES[profile], "--in", container_run_dir,
            "-t", toolsets, "-z", prompt, "--usage-file", f"{container_run_dir}/usage.json"]


def materialise_stdout_result(path: Path, stdout: str, contract: dict, request_sha256: str) -> None:
    """Persist only a single strict JSON object returned by Hermes one-shot stdout."""
    if path.exists():
        return
    try:
        value = json.loads(stdout.strip())
    except json.JSONDecodeError:
        decoder=json.JSONDecoder(); candidates=[]
        for index,character in enumerate(stdout):
            if character != "{": continue
            try: candidate,_ = decoder.raw_decode(stdout[index:])
            except json.JSONDecodeError: continue
            if isinstance(candidate,dict) and set(candidate)=={"status","artifact_hashes","decision"}:
                candidates.append(candidate)
        if len(candidates) != 1: raise ValueError("Hermes stdout is not one closed JSON result")
        value=candidates[0]
    if not isinstance(value, dict) or set(value) != {"status", "artifact_hashes", "decision"}:
        raise ValueError("Hermes stdout is not a closed JSON object")
    # Hermes roles sometimes use terminal synonyms despite the prompt's closed
    # enum. Canonicalise only known affirmative terminal words on the host;
    # every other status still fails validation.
    if value["status"] in {"complete", "completed", "validated", "success", "succeeded"}: value["status"] = "accepted"
    atomic_json(path, {"schema_version": 1, "parent_run_id": contract["parent_run_id"],
                       "child_run_id": contract["child_run_id"], "role": contract["owner"],
                       "request_sha256": request_sha256, **value})


def metadata_probe_argv(profile: str) -> list[str]:
    """Read real numeric ownership/mode metadata without granting shell expansion."""
    if profile not in PROFILE_NAMES:
        raise ValueError("unregistered Hermes profile")
    directory = f"/opt/data/profiles/{PROFILE_NAMES[profile]}"
    return [DOCKER, "exec", "-i", "--user", CONTAINER_USER, CONTAINER, "/usr/bin/stat", "--format=%u:%g:%a", directory]


def probe_profile_metadata(profile: str, runner: Callable = subprocess.run) -> dict:
    if profile not in PROFILE_NAMES: raise ValueError("unregistered Hermes profile")
    host_path=Path(f"/home/hermes/.hermes/profiles/{PROFILE_NAMES[profile]}")
    host=host_path.stat(follow_symlinks=False)
    if host_path.is_symlink() or (host.st_uid,host.st_gid,stat.S_IMODE(host.st_mode))!=(10000,10000,0o700):
        raise ValueError("unsafe host Hermes profile metadata")
    done=runner(metadata_probe_argv(profile),capture_output=True,text=True,timeout=30)
    if done.returncode or done.stdout.strip()!="10000:10000:700": raise ValueError("unsafe container Hermes profile metadata")
    return {"profile":profile,"host":{"uid":host.st_uid,"gid":host.st_gid,"mode":"0700"},"container":{"uid":10000,"gid":10000,"mode":"0700"}}


def registered_gsc_request(contract: dict, site_key: str, property_name: str, urls: list[str]) -> dict:
    if site_key != "lhm-main" or property_name != "https://localhealthmarketing.com/" or not urls or normalise_urls(property_name, urls) != urls:
        raise ValueError("research plan exceeds registered GSC property")
    binding = {"parent_run_id": contract["parent_run_id"], "child_run_id": contract["child_run_id"], "role": contract["owner"], "site_key": site_key, "property": property_name, "operations": ["list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"]}
    argv = [DISPATCH, "submit-seo-gsc-readonly", site_key, ",".join(urls), json.dumps({**binding, "objective": "Collect bounded GSC evidence for scheduled SEO research"}, sort_keys=True, separators=(",", ":"))]
    return {"schema_version": 1, "operation": "claude_dispatch", "argv": argv, "binding": binding}


def validate_registered_adapter_receipt(receipt: dict, request: dict) -> dict:
    if receipt.get("binding") != request["binding"] or receipt.get("operation") != "claude_dispatch": raise ValueError("GSC connector receipt binding mismatch")
    if receipt.get("receipt_sha256") != canonical_sha(receipt.get("result")): raise ValueError("GSC connector receipt hash mismatch")
    result = receipt.get("result")
    if (not isinstance(result, dict) or result.get("completion", {}).get("status") != "needs_review" or
            result.get("completion", {}).get("profile") != "seo_gsc_readonly" or not isinstance(result.get("evidence"), str) or
            not result["evidence"].strip() or result.get("evidence_sha256") != hashlib.sha256(result["evidence"].encode()).hexdigest()):
        raise ValueError("GSC connector did not return terminal evidence")
    return receipt


def invoke_registered_adapter(request: dict, runner: Callable = subprocess.run) -> dict:
    payload = json.dumps(request, sort_keys=True, separators=(",", ":"))
    done = runner([ADAPTER], input=payload, capture_output=True, text=True, timeout=610)
    if done.returncode: raise RuntimeError("registered GSC connector failed")
    return validate_registered_adapter_receipt(json.loads(done.stdout), request)


def work_control_request(parent: dict, contract: dict, reason: str) -> dict:
    incident = f"scheduled-{contract['stage_id']}-capability"
    resume = digest({"parent": parent["parent_run_id"], "incident": incident, "contract": digest(contract)})
    ceiling = parent["scheduled_contract"]["permission_ceiling"]
    work_control_ceiling = {"non-production-preview": "green", "green": "green", "amber": "amber", "red": "red"}.get(ceiling)
    if work_control_ceiling is None: raise ValueError("unsupported work-control permission ceiling")
    return {"parent_run_id": parent["parent_run_id"], "capability_incident_id": incident,
            "return_point": parent["scheduled_contract"]["work_control"]["return_point"],
            "resume_token": resume, "objective": parent["objective"],
            "acceptance_test": parent["scheduled_contract"]["completion_test"],
            "permission_ceiling": work_control_ceiling}


def invoke_work_control(parent: dict, contract: dict, reason: str, runner: Callable = subprocess.run) -> dict:
    wc = parent["scheduled_contract"]["work_control"]
    executable = Path(wc["path"])
    if hashlib.sha256(executable.read_bytes()).hexdigest() != wc["sha256"]: raise ValueError("work-control executable hash mismatch")
    payload = work_control_request(parent, contract, reason)
    argv = [DOCKER, "exec", "-i", "--user", CONTAINER_USER, CONTAINER, WORK_CONTROL_CONTAINER, "block"]
    done = runner(argv, input=json.dumps(payload, sort_keys=True, separators=(",", ":")), capture_output=True, text=True, timeout=60)
    if done.returncode: raise RuntimeError("work-control block failed")
    return payload


def snapshot_sources(paths: list[str], destination: Path, site: str) -> tuple[list[dict], list[str]]:
    """Copy only registered source bytes and derive same-property URLs on every run."""
    records, candidates = [], []
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    selected: list[Path] = []
    for raw in paths:
        source = Path(raw)
        selected.extend(sorted(p for p in source.iterdir() if p.name in {"rollout-state.md", "sitemap.json", "LHM-Proposed-Sitemap.html"})) if source.is_dir() else selected.append(source)
    for index, source in enumerate(selected):
        if source.is_symlink() or not source.is_file(): raise ValueError("canonical source is not a regular file")
        data = source.read_bytes(); target = destination / f"source-{index:02d}{source.suffix}"
        target.write_bytes(data); target.chmod(0o600)
        if target.read_bytes() != data: raise ValueError("canonical snapshot readback mismatch")
        records.append({"source_path": str(source), **artifact(target, f"canonical-source-{index:02d}")})
        candidates.extend(match.group(0) for match in URL.finditer(data.decode("utf-8", errors="ignore")))
    urls = normalise_urls(site, candidates)
    if not urls: raise ValueError("canonical sources yielded no registered-property URLs")
    return records, urls


def compare_and_swap_tracker(path: Path, expected_sha256: str, replacement: bytes) -> dict:
    """Perform the only tracker mutation, with precondition and full byte readback."""
    before = path.read_bytes()
    if hashlib.sha256(before).hexdigest() != expected_sha256: raise ValueError("tracker compare-and-swap conflict")
    if before == replacement:
        return {"before_sha256": expected_sha256, "after_sha256": expected_sha256, "readback": True, "mutation": "none"}
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle: handle.write(replacement); handle.flush(); os.fsync(handle.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777); os.replace(temporary, path)
    finally: Path(temporary).unlink(missing_ok=True)
    if path.read_bytes() != replacement: raise ValueError("tracker full readback mismatch")
    return {"before_sha256": expected_sha256, "after_sha256": hashlib.sha256(replacement).hexdigest(), "readback": True}


class ScheduledExecutor:
    def __init__(self, root: Path = DEFAULT_ROOT, *, runner: Callable = subprocess.run, test_mode: bool = False):
        self.root, self.runner, self.test_mode = root, runner, test_mode
        self.router = Router(root, self._public_keys())

    def _public_keys(self) -> dict:
        public = self.root / "public"
        return {p.name.removesuffix(".public.pem"): p for p in public.glob("*.public.pem")} if public.exists() else {}

    def _checkpoint(self, parent: str, value: dict) -> None:
        atomic_json(self.root / "scheduled-runs" / parent / "checkpoint.json", value)

    def _invoke(self, profile: str, run_dir: Path, request: Path, result: Path, contract: dict) -> dict:
        if self.root == DEFAULT_ROOT:
            metadata=probe_profile_metadata(profile,self.runner)
            atomic_json(run_dir/"profile-metadata.json",metadata)
        if self.root == DEFAULT_ROOT:
            os.chown(request, 10000, 10000)
            for candidate in run_dir.rglob("*"):
                if candidate.is_file() and not candidate.is_symlink(): os.chown(candidate, 10000, 10000)
                elif candidate.is_dir() and not candidate.is_symlink(): os.chown(candidate, 10000, 10000)
        request_value=json.loads(request.read_text()); request_sha256=canonical_sha(request_value)
        # Freshness is established by removing the prior file and materialising
        # only this invocation's bounded stdout. A deterministic retry is
        # allowed to reproduce byte-identical business output.
        result.unlink(missing_ok=True)
        container_dir=f"/opt/data/profiles/{PROFILE_NAMES[profile]}/dispatch/scheduled-executor/{contract['parent_run_id']}/{contract['child_run_id']}"
        stage_instruction = ("For this Context stage, validate only the source manifest paths and SHA-256 evidence "
                             "already contained in request.json. Do not open the referenced source files, perform "
                             "research, or use tools beyond reading request.json. Return an empty decision object. "
                             if contract["stage_id"] == "context" else
                             "For this independent Verifier stage, read each exact path in input_artifact_paths, "
                             "compute or compare its SHA-256 to the declared value, and accept only an exact match. "
                             "Return an empty decision object. " if contract["runtime"] == "verifier" else
                             "For this Research synthesis stage, read the exact immutable_connector_evidence path, "
                             "summarise only that read-only GSC evidence in decision, and do not request or mutate data. "
                             if contract["stage_id"] == "research" and request_value.get("phase") == "synthesis" else
                             "For this SEO acceptance stage, return a decision object with exactly content_required "
                             "(boolean), website_required (boolean), and reason (non-empty string). Base the flags only "
                             "on explicitly required downstream work; when no such work is available, set both false "
                             "and explain that no additional implementation was explicitly required. "
                             if contract["stage_id"] == "seo_accept" else "")
        prompt=(f"Read the exact absolute file {container_dir}/request.json. {stage_instruction}Print only one JSON object to stdout "
                f"with exactly these three keys: status, artifact_hashes, decision. Do not repeat identity or hashes "
                f"from the request and do not use markdown "
                "fences. If you read the request and complete the bounded stage, set status to the exact string "
                "accepted, artifact_hashes to a JSON array of SHA-256 strings (an empty array is allowed), and "
                "decision to a JSON object (an empty object is allowed). Never return null for these fields. Do not "
                "write files, access credentials or mutate systems.")
        done = self.runner(hermes_argv(profile, container_dir, prompt), capture_output=True, text=True, timeout=900)
        if done.returncode: raise RuntimeError("bounded Hermes role invocation failed")
        materialise_stdout_result(result, done.stdout, contract, request_sha256)
        return validate_closed_result(result, contract, request_sha256)

    def _wait_signed(self, contract: dict, envelope: dict, run_dir: Path) -> dict:
        registry_path = self.root / "artifact-registry.json"
        registry = json.loads(registry_path.read_text()) if registry_path.exists() else {}
        for item in envelope["outputs"]:
            prior = registry.get(item["artifact_id"])
            candidate = (Path(item["path"]) if item.get("path") else
                         Path(prior["path"]) if prior and contract["input_artifacts"] else
                         run_dir / "result.json")
            if not candidate.exists() or hashlib.sha256(candidate.read_bytes()).hexdigest()!=item["sha256"]:
                raise ValueError("artifact registry readback mismatch")
            registry[item["artifact_id"]] = {"path": str(candidate), "sha256": item["sha256"]}
        atomic_json(registry_path, registry, 0o640)
        if self.root == DEFAULT_ROOT: os.chown(registry_path,10004,10004)
        request = self.root / "org-signer-requests" / contract["owner"] / f"{contract['child_run_id']}.json"
        result = self.root / "org-signer-results" / contract["owner"] / request.name
        signer_envelope={**envelope,"outputs":[{k:v for k,v in item.items() if k!="path"} for item in envelope["outputs"]]}
        # A resumed idempotent child must wait for a receipt over its current
        # contract, never consume the prior attempt's result at the same path.
        result.unlink(missing_ok=True)
        atomic_json(request, signer_envelope, 0o640)
        deadline = time.monotonic() + (2 if self.test_mode else 120)
        while time.monotonic() < deadline:
            if result.exists():
                value = json.loads(result.read_text()); atomic_json(run_dir / "signed-receipt.json", value); return value
            time.sleep(0.01 if self.test_mode else 0.25)
        # The path-triggered signer can publish at the same instant as the main
        # deadline. Give that already-admitted request one bounded final grace
        # window so a valid receipt is not misclassified as unavailable.
        grace_deadline = time.monotonic() + (0.05 if self.test_mode else 2)
        while time.monotonic() < grace_deadline:
            if result.exists():
                value = json.loads(result.read_text()); atomic_json(run_dir / "signed-receipt.json", value); return value
            time.sleep(0.01 if self.test_mode else 0.05)
        raise TimeoutError(f"isolated signer unavailable: {contract['owner']}")

    def _block(self, parent: dict, contract: dict, reason: str) -> None:
        incident = f"scheduled-{contract['stage_id']}-capability"
        resume = digest({"parent": parent["parent_run_id"], "incident": incident, "contract": digest(contract)})
        wc = parent["scheduled_contract"]["work_control"]
        invoke_work_control(parent, contract, reason, self.runner)
        self._checkpoint(parent["parent_run_id"], {"status": "waiting_on_capability", "incident": incident, "return_point": wc["return_point"], "reason": reason, "resume_token_sha256": hashlib.sha256(resume.encode()).hexdigest()})

    def run_parent(self, parent: dict) -> dict:
        parent_id = parent["parent_run_id"]
        # Capability resumes must reopen the durable parent. Reinitialising an
        # existing parent would rewind its cursor and conflict with the signed
        # child-receipt ledger.
        if not self.router._path(parent_id).exists():
            try: self.router.initialise({key: parent[key] for key in ("source", "source_cron_id", "job_name", "prompt", "delivery", "triggered_at")}, parent_id)
            except KeyError:
                # Persisted ingress parents contain the already validated intake fields under their canonical names.
                self.router._atomic(self.router._path(parent_id), parent)
        while True:
            state = self.router.load(parent_id)
            if state["state"] == "closed": return state
            child = f"{parent_id}-{state['cursor']:02d}"
            contract = self.router.issue(parent_id, child)
            stage_profile = None
            if contract["runtime"] == "verifier":
                stage_profile = "lhm_verifier"
            elif contract["stage_id"] in BOT_STAGES:
                stage_profile = Path(parent["scheduled_contract"]["profile_aliases"][contract["owner"]]).name
            if self.root == DEFAULT_ROOT:
                profile_name = PROFILE_NAMES.get(stage_profile, "lhm_brain")
                run_dir = Path(f"/home/hermes/.hermes/profiles/{profile_name}/dispatch/scheduled-executor") / parent_id / child
            else:
                run_dir = self.root / "scheduled-runs" / parent_id / "children" / child
            run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(run_dir, 0o700)
            if self.root == DEFAULT_ROOT:
                os.chown(run_dir.parent, 0, 10000)
                os.chmod(run_dir.parent, 0o710)
                os.chown(run_dir, 10000, 10000)
            request_path, result_path = run_dir / "request.json", run_dir / "result.json"
            request = {"schema_version": 1, "contract": contract, "parent_run_id": parent_id, "permission_ceiling": contract["permission_ceiling"]}
            if contract["stage_id"] == "context":
                sources, urls = snapshot_sources(parent["scheduled_contract"]["canonical_sources"], run_dir / "sources", parent["scheduled_contract"]["gsc"]["property"])
                request.update(canonical_sources=sources, gsc={**parent["scheduled_contract"]["gsc"], "candidate_urls": urls})
            atomic_json(request_path, request)
            try:
                if contract["runtime"] == "verifier":
                    registry=json.loads((self.root / "artifact-registry.json").read_text())
                    private_inputs=[]
                    for index,item in enumerate(contract["input_artifacts"]):
                        record=registry.get(item["artifact_id"]); source=Path(record["path"]) if record else None
                        if not source or record["sha256"]!=item["sha256"] or hashlib.sha256(source.read_bytes()).hexdigest()!=item["sha256"]:
                            raise ValueError("verifier source artifact readback mismatch")
                        destination=run_dir / f"input-artifact-{index:02d}.json"
                        destination.write_bytes(source.read_bytes()); os.chown(destination,10000,10000); os.chmod(destination,0o600)
                        signing_dir=self.root / "verifier-signing-inputs" / parent_id / child
                        signing_dir.mkdir(parents=True,exist_ok=True,mode=0o750)
                        signing_copy=signing_dir / destination.name; signing_copy.write_bytes(source.read_bytes()); os.chmod(signing_copy,0o640)
                        if self.root == DEFAULT_ROOT:
                            for directory in (self.root / "verifier-signing-inputs", signing_dir.parent, signing_dir):
                                os.chown(directory,0,10004); os.chmod(directory,0o750)
                            os.chown(signing_copy,0,10004)
                        registry[item["artifact_id"]]={"path":str(signing_copy),"sha256":item["sha256"]}
                        private_inputs.append({**item,"path":f"/opt/data/profiles/lhm_verifier/dispatch/scheduled-executor/{parent_id}/{child}/{destination.name}"})
                    atomic_json(self.root / "artifact-registry.json",registry,0o640)
                    if self.root == DEFAULT_ROOT: os.chown(self.root / "artifact-registry.json",10004,10004)
                    verifier_request={**request, "independent_verification": True, "self_approval_forbidden": True,
                                      "input_artifact_paths":private_inputs}
                    atomic_json(request_path, verifier_request)
                    self._invoke("lhm_verifier", run_dir, request_path, result_path, contract)
                    outputs = contract["input_artifacts"]
                elif contract["stage_id"] in BOT_STAGES:
                    alias = stage_profile
                    if contract["stage_id"] == "research":
                        _,candidate_urls=snapshot_sources(parent["scheduled_contract"]["canonical_sources"],run_dir / "research-sources",parent["scheduled_contract"]["gsc"]["property"])
                        connector_request = registered_gsc_request(contract,parent["scheduled_contract"]["gsc"]["site_key"],parent["scheduled_contract"]["gsc"]["property"],candidate_urls[:25])
                        evidence_path = run_dir / "connector-evidence.json"
                        request_digest=canonical_sha(connector_request)
                        existing=json.loads(evidence_path.read_text()) if evidence_path.exists() else None
                        if (isinstance(existing,dict) and existing.get("request_sha256")==request_digest and
                                existing.get("receipt_sha256")==canonical_sha(existing.get("receipt"))):
                            connector_receipt=validate_registered_adapter_receipt(existing["receipt"],connector_request)
                        else:
                            connector_receipt = invoke_registered_adapter(connector_request, self.runner)
                            atomic_json(evidence_path, {"request_sha256": request_digest, "receipt": connector_receipt, "receipt_sha256": canonical_sha(connector_receipt)})
                        evidence=artifact(evidence_path,"gsc-connector-evidence")
                        evidence["path"]=f"/opt/data/profiles/{PROFILE_NAMES[alias]}/dispatch/scheduled-executor/{parent_id}/{child}/connector-evidence.json"
                        request = {**request, "phase": "synthesis", "immutable_connector_evidence": evidence}
                        atomic_json(request_path, request)
                        closed = self._invoke(alias, run_dir, request_path, result_path, contract)
                    else:
                        if contract["stage_id"] == "operations_write" and contract["permission_ceiling"] == "non-production-preview":
                            tracker=Path(parent["scheduled_contract"]["canonical_sources"][3])/"rollout-state.md"
                            current=tracker.read_bytes()
                            value={"schema_version":1,"parent_run_id":parent_id,"child_run_id":child,"role":contract["owner"],
                                   "request_sha256":canonical_sha(request),"status":"accepted","artifact_hashes":[],
                                   "decision":{"expected_previous_sha256":hashlib.sha256(current).hexdigest(),"replacement":current.decode()}}
                            atomic_json(result_path,value); closed={"value":value,"result_sha256":hashlib.sha256(result_path.read_bytes()).hexdigest()}
                        else:
                            closed = self._invoke(alias, run_dir, request_path, result_path, contract)
                    if contract["stage_id"] == "operations_write":
                        proposal=closed["value"]["decision"]
                        if set(proposal)!={"expected_previous_sha256","replacement"} or not isinstance(proposal["replacement"],str):
                            raise ValueError("operations returned invalid tracker replacement")
                        tracker=Path(parent["scheduled_contract"]["canonical_sources"][3])/"rollout-state.md"
                        cas=compare_and_swap_tracker(tracker,proposal["expected_previous_sha256"],proposal["replacement"].encode())
                        cas_path=run_dir/"tracker-cas-readback.json"; atomic_json(cas_path,cas)
                        outputs=[artifact(cas_path,"operations-tracker-cas")]
                    else:
                        outputs = [artifact(result_path, f"{contract['stage_id']}-result")]
                else:
                    atomic_json(result_path, {"status": "accepted", "stage_id": contract["stage_id"]})
                    outputs = [artifact(result_path, f"{contract['stage_id']}-result")]
                # Only SEO acceptance is authorised to change the remaining
                # route. Other role decisions remain evidence in result.json
                # but cannot become organisational routing instructions.
                decision = (json.loads(result_path.read_text()).get("decision", {})
                            if result_path.exists() and contract["stage_id"] == "seo_accept" else {})
                signed = self._wait_signed(contract, {"contract": contract, "outputs": outputs, "checks": ["artifact.readback_sha256"], "decision": decision}, run_dir)
                state = self.router.accept(parent_id, contract, signed)
                self._checkpoint(parent_id, {"status": state["state"], "cursor": state["cursor"], "child_run_id": child, "idempotency_key": contract["idempotency_key"], "signed_receipt_sha256": digest(signed)})
            except Exception as exc:
                checkpoint = self.root / "scheduled-runs" / parent_id / "checkpoint.json"
                previous = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
                if previous.get("failed_child") != child:
                    self._checkpoint(parent_id, {"status": "retrying", "failed_child": child, "safe_retry": 1, "reason": str(exc)})
                    continue
                self._block(parent, contract, str(exc)); return {"state": "incident", "parent_run_id": parent_id}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent", type=Path)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    parent = json.loads(args.parent.read_text())
    state = ScheduledExecutor(args.root, test_mode=os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1").run_parent(parent)
    print(json.dumps({"parent_run_id": parent["parent_run_id"], "business_state": state["state"]}, sort_keys=True))


if __name__ == "__main__": main()
