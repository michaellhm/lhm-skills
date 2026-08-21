#!/usr/bin/env python3
"""Root-owned Claude execution and provenance boundary.

The worker's prose is never accepted as provenance.  The root supervisor owns
the Claude pipe, correlates tool_use IDs with non-error tool_results, and only
then calls the protected Hermes workflow hook.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pwd
import re
import subprocess
import tempfile
from urllib.parse import urlparse
from dataclasses import dataclass, field
from pathlib import Path

CLAUDE = Path("/opt/lhm-workflow/claude/2.1.232/claude")
CLAUDE_SHA256 = "61d23f8749136907d586d5b11831ea8a5234d4c1dea40a5e55c33b52e204c6d1"
CLAUDE_HOME = Path("/home/claudeworker")
# Keep the provenance hook byte-aligned with the versioned supervisor release.
# Tests may still override this path explicitly through `_test_override`.
HOOK = Path(__file__).resolve().with_name("hermes_workflow_hook.py")
GSC_CONFIG = Path("/home/claudeworker/.config/lhm-bridge/seo-gsc-readonly.mcp.json")
PLUGIN = Path("/opt/lhm-workflow/claude/plugins/lhm-marketing-hub-2.2.0")
RUNS = Path("/home/hermes/.hermes/profiles/lhm_brain/dispatch/claude/runs")
SAFE_CHILD = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")
GSC_TOOLS = {
    "mcp__gscServer__list_sites",
    "mcp__gscServer__batch_url_inspection",
    "mcp__gscServer__search_analytics",
    "mcp__gscServer__list_sitemaps",
    "mcp__gscServer__get_sitemap",
}


def _test_override(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    if value and os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
        raise SystemExit(f"{name} override requires test mode")
    return Path(value) if value else default


def _blocks(event: dict):
    message = event.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), list):
        yield from message["content"]
    if isinstance(event.get("content"), list):
        yield from event["content"]


def _tool_result_error(block: dict) -> bool:
    if block.get("is_error") is True or block.get("error") is not None:
        return True
    content = block.get("content")
    if isinstance(content, dict) and (content.get("isError") is True or content.get("error") is not None):
        return True
    return False


@dataclass
class Transcript:
    uses: dict[str, dict] = field(default_factory=dict)
    results: dict[str, dict] = field(default_factory=dict)
    final: str | None = None
    malformed: bool = False

    def feed(self, line: str) -> None:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            self.malformed = True
            return
        if not isinstance(event, dict):
            self.malformed = True
            return
        for block in _blocks(event):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                call_id = block.get("id")
                if not isinstance(call_id, str) or not call_id or call_id in self.uses:
                    self.malformed = True
                else:
                    self.uses[call_id] = block
            elif block.get("type") == "tool_result":
                call_id = block.get("tool_use_id")
                if (not isinstance(call_id, str) or not call_id or call_id in self.results
                        or call_id not in self.uses):
                    self.malformed = True
                else:
                    self.results[call_id] = block
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            if self.final is not None:
                self.malformed = True
            self.final = event["result"].strip()

    def successful(self, call_id: str) -> bool:
        result = self.results.get(call_id)
        return result is not None and not _tool_result_error(result)

    def skills(self) -> list[str]:
        answer = []
        for call_id, use in self.uses.items():
            if use.get("name") == "Skill" and self.successful(call_id):
                skill = use.get("input", {}).get("skill") if isinstance(use.get("input"), dict) else None
                if isinstance(skill, str):
                    answer.append(skill)
        return answer

    def successful_tools(self) -> list[dict]:
        return [use for call_id, use in self.uses.items() if self.successful(call_id)]

    def result_text(self, call_id: str) -> str:
        block = self.results.get(call_id, {})
        content = block.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        if isinstance(content, dict):
            return json.dumps(content, sort_keys=True)
        return ""


def verify_gsc_readback(transcript: Transcript, site_property: str, urls: list[str]) -> dict:
    """Prove scoped, non-mutating GSC reads from the root-owned transcript."""
    observed = []
    admitted_urls=set(urls); requested_urls=set(); returned_urls=set()
    def within_property(url):
        if not isinstance(url,str): return False
        if site_property.startswith("sc-domain:"):
            host=urlparse(url).hostname or ""; domain=site_property.removeprefix("sc-domain:").lower().rstrip(".")
            return host.lower()==domain or host.lower().endswith("."+domain)
        return url.startswith(site_property)
    def parsed_result(call_id):
        try: value=json.loads(transcript.result_text(call_id))
        except (json.JSONDecodeError,TypeError) as exc: raise ValueError("GSC readback was not structured JSON") from exc
        if not isinstance(value,(dict,list)) or not value: raise ValueError("GSC readback was empty")
        def active_error(error_value):
            # GSC sitemap entries legitimately expose an `errors` count. Zero
            # means no sitemap errors; only a meaningful/non-zero payload is
            # an application-level failure.
            if error_value is None or error_value is False or error_value == 0 or error_value == "": return False
            if error_value == "0": return False
            if isinstance(error_value,(list,dict)) and not error_value: return False
            return True
        def has_error(item):
            if isinstance(item,dict):
                if any(str(key).lower() in {"error","errors"} and active_error(child) for key,child in item.items()): return True
                if item.get("isError") is True: return True
                return any(has_error(child) for child in item.values())
            return isinstance(item,list) and any(has_error(child) for child in item)
        if has_error(value): raise ValueError("GSC readback contained an error")
        return value
    def url_fields(item):
        answer=[]
        if isinstance(item,dict):
            for key,value in item.items():
                if str(key).lower() in {"url","urls","inspectionurl","inspectionurls","inspectedurl","inspectedurls"}:
                    values=[value] if isinstance(value,str) else value
                    if not isinstance(values,list) or not all(isinstance(entry,str) for entry in values):
                        raise ValueError("GSC response URL field was malformed")
                    answer.extend(values)
                else: answer.extend(url_fields(value))
        elif isinstance(item,list):
            for child in item: answer.extend(url_fields(child))
        return set(answer)
    def listed_properties(item):
        # Google Search Console's native response is `siteEntry` objects; some
        # MCP releases normalize that collection to `sites`/`siteEntries`.
        if not isinstance(item,dict): return set()
        collection=None
        for key in ("siteEntry","siteEntries","sites"):
            if key in item: collection=item[key]; break
        if not isinstance(collection,list): return set()
        answer=set()
        for entry in collection:
            if isinstance(entry,str): answer.add(entry)
            elif isinstance(entry,dict) and isinstance(entry.get("siteUrl"),str): answer.add(entry["siteUrl"])
        return answer
    for call_id, use in transcript.uses.items():
        if not transcript.successful(call_id):
            continue
        name = use.get("name")
        if name not in GSC_TOOLS:
            continue
        data = use.get("input")
        if not isinstance(data, dict):
            raise ValueError("GSC tool input missing")
        if name != "mcp__gscServer__list_sites" and data.get("siteUrl") != site_property:
            raise ValueError("GSC read escaped the admitted property")
        try:
            result_value=parsed_result(call_id)
        except ValueError:
            raw_result=transcript.result_text(call_id).strip()
            # Claude Code may replace an oversized, otherwise successful
            # Search Analytics response with a local-file overflow pointer.
            # It is not evidence and is ignored; another bounded structured
            # Search Analytics read is still mandatory below.
            if (name=="mcp__gscServer__search_analytics" and raw_result.startswith("Error: result (")
                    and "exceeds maximum allowed tokens" in raw_result):
                continue
            raise
        if name == "mcp__gscServer__list_sites" and site_property not in listed_properties(result_value):
            raise ValueError("admitted property absent from GSC site readback")
        if name == "mcp__gscServer__batch_url_inspection":
            supplied=data.get("inspectionUrls",data.get("urls",data.get("inspectionUrl",data.get("url",[]))))
            supplied=[supplied] if isinstance(supplied,str) else supplied
            if not isinstance(supplied,list) or not supplied or not all(isinstance(url,str) for url in supplied):
                raise ValueError("GSC inspection URL scope missing")
            supplied_set=set(supplied)
            if not all(within_property(url) for url in supplied_set):
                raise ValueError("GSC inspection escaped the admitted property")
            result_urls=url_fields(result_value)
            if not all(within_property(url) for url in result_urls): raise ValueError("GSC response escaped the admitted property")
            if result_urls-supplied_set: raise ValueError("GSC response included an unrequested inspection URL")
            requested_urls.update(supplied_set); returned_urls.update(result_urls)
        observed.append(name)
    required = {
        "mcp__gscServer__list_sites",
        "mcp__gscServer__batch_url_inspection",
        "mcp__gscServer__search_analytics",
        "mcp__gscServer__list_sitemaps",
    }
    missing = sorted(required - set(observed))
    if missing:
        raise ValueError(f"missing successful GSC readbacks: {missing}")
    if len(requested_urls)>25 or len(returned_urls)>25:
        raise ValueError("GSC diagnostic URL expansion exceeded the bounded limit")
    if not admitted_urls.issubset(requested_urls) or not admitted_urls.issubset(returned_urls):
        raise ValueError("GSC inspection omitted an admitted URL across structured readbacks")
    return {"capability": "google_search_console.property_read", "property": site_property,
            "urls": urls, "observed_urls":sorted(requested_urls), "successful_tools": observed, "mutation_state": "none"}


def persist_rejected_evidence(run_dir: Path, child: str, transcript: Transcript, reason: str) -> Path:
    """Persist bounded, secret-redacted tool evidence without worker prose."""
    sensitive=re.compile(r"token|secret|password|credential|authorization|cookie|api.?key",re.I)
    def clean(value,key=""):
        if sensitive.search(key): return "[REDACTED]"
        if isinstance(value,dict): return {str(k):clean(v,str(k)) for k,v in list(value.items())[:100]}
        if isinstance(value,list): return [clean(item,key) for item in value[:100]]
        if isinstance(value,str): return value[:2048]
        return value if value is None or isinstance(value,(bool,int,float)) else repr(value)[:256]
    calls=[]
    for call_id,use in transcript.uses.items():
        result=transcript.results.get(call_id)
        result_content=result.get("content") if result else None
        if isinstance(result_content,str):
            try: result_content=json.loads(result_content)
            except json.JSONDecodeError: result_content=result_content[:2048]
        calls.append({"call_id":call_id,"tool":use.get("name"),"input":clean(use.get("input")),
                      "successful":transcript.successful(call_id),"result":clean(result_content)})
    run_dir.mkdir(mode=0o750,parents=False,exist_ok=True)
    path=run_dir/"rejected-tool-evidence.json"
    payload={"schema_version":1,"child_run_id":child,"status":"rejected","reason":str(reason)[:500],"tool_calls":calls}
    path.write_text(json.dumps(payload,sort_keys=True)+"\n",encoding="utf-8"); os.chmod(path,0o600)
    return path


def validate_provenance(transcript: Transcript, required_skills: list[str], profile: str) -> list[str]:
    observed_skills = transcript.skills()
    if observed_skills != required_skills:
        raise ValueError(f"successful Skill sequence mismatch: {observed_skills}")
    allowed = {"Skill"} | (GSC_TOOLS if profile == "seo_gsc_readonly" else set())
    unexpected = [use.get("name") for use in transcript.successful_tools() if use.get("name") not in allowed]
    if unexpected:
        raise ValueError(f"successful tool outside allowlist: {unexpected}")
    return observed_skills


def _drop_to_worker() -> None:
    worker = pwd.getpwnam("claudeworker")
    os.setgroups([])
    os.setgid(worker.pw_gid)
    os.setuid(worker.pw_uid)


def run(request: dict, child: str, run_dir: Path) -> dict:
    if os.geteuid() != 0 and os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
        raise SystemExit("root supervisor only")
    if not SAFE_CHILD.fullmatch(child) or run_dir.resolve().parent != _test_override("LHM_CLAUDE_RUNS", RUNS).resolve():
        raise SystemExit("invalid run directory")
    # The root supervisor owns this governed boundary. Create the bounded child
    # directory itself before validating ownership; callers must not need to
    # prepare a worker-writable path first.
    run_dir.mkdir(mode=0o750, parents=False, exist_ok=True)
    if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
        st = run_dir.stat(follow_symlinks=False)
        if st.st_uid != 0 or st.st_mode & 0o022 or run_dir.is_symlink():
            raise SystemExit("governed run directory is not root-controlled")
    required_skills = request.get("required_skills")
    if not isinstance(required_skills, list) or not required_skills or not all(isinstance(x, str) for x in required_skills):
        raise SystemExit("required_skills must be non-empty")
    claude = _test_override("LHM_CLAUDE_BINARY", CLAUDE)
    hook = _test_override("LHM_WORKFLOW_HOOK", HOOK)
    gsc_config = _test_override("LHM_GSC_CONFIG", GSC_CONFIG)
    plugin = _test_override("LHM_CLAUDE_PLUGIN", PLUGIN)
    if not claude.is_file() or not os.access(claude, os.X_OK):
        raise SystemExit("fixed Claude executable unavailable")
    if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
        st = claude.stat(follow_symlinks=False)
        if st.st_uid != 0 or st.st_mode & 0o022 or hashlib.sha256(claude.read_bytes()).hexdigest() != CLAUDE_SHA256:
            raise SystemExit("fixed Claude executable failed ownership or digest verification")
        for relative, expected in {
            ".claude-plugin/plugin.json": "187a2f0e9be99f9694b1809ab97563ac629e9bc4b5ede02c568e5c4d6dfe6fb0",
            "skills/seo-audit/SKILL.md": "4986f41bf86c8721c4b1c78d4ff3be26e48afce007f647130a26121fa0654abe",
            "skills/seo-content-writer/SKILL.md": "c0ea7634d3ee8664791d704787b2e53b9a2cc68ac4921a5a49445d1faee06d1f",
        }.items():
            item = plugin / relative
            item_st = item.stat(follow_symlinks=False)
            if item_st.st_uid != 0 or item_st.st_mode & 0o022 or hashlib.sha256(item.read_bytes()).hexdigest() != expected:
                raise SystemExit(f"pinned skill namespace failed verification: {relative}")
    prompt = request.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        objective = request.get("objective")
        if not isinstance(objective, str) or not objective.strip():
            raise SystemExit("prompt or objective required")
        prompt = ("This is a bounded review-only workflow. Invoke every required skill through the Skill tool. "
                  "Use only the allowlisted tools, make no mutations, and return a self-contained evidence handback.\n"
                  f"Required skills: {json.dumps(required_skills)}\nObjective: {objective}")
        if request.get("profile") == "seo_gsc_readonly":
            prompt += (f"\nSearch Console property: {request.get('site_property')}"
                       f"\nExact URLs: {json.dumps(request.get('urls', []))}"
                       "\nUse list_sites, batch_url_inspection, search_analytics and list_sitemaps.")
    profile = request.get("profile")
    allowed = ["Skill"]
    # `--bare` explicitly ignores `--plugin-dir`, which prevents the pinned
    # governed skills from loading. Suppress ambient user/project settings
    # instead, while loading only the root-owned explicit plugin directory.
    command = [str(claude), "--setting-sources", "", "--plugin-dir", str(plugin), "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--no-session-persistence", "--tools", "Skill", "--allowedTools"]
    if profile == "seo_gsc_readonly":
        allowed += sorted(GSC_TOOLS)
    command.append(",".join(allowed))
    if profile == "seo_gsc_readonly":
        command += ["--strict-mcp-config", "--mcp-config", str(gsc_config)]
    env = {"HOME": str(CLAUDE_HOME), "PATH": "/home/claudeworker/.local/bin:/usr/local/bin:/usr/bin:/bin"}
    kwargs = {} if os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1" else {"preexec_fn": _drop_to_worker}
    completed = subprocess.run(command, text=True, capture_output=True, timeout=int(request.get("timeout_seconds", 600)), env=env, **kwargs)
    transcript = Transcript()
    for line in completed.stdout.splitlines():
        transcript.feed(line)
    if completed.returncode or transcript.malformed or not transcript.final:
        diagnostic = completed.stderr.strip().splitlines()[-1] if completed.stderr.strip() else "no stderr"
        raise SystemExit(f"Claude stream was unsuccessful or malformed: {diagnostic[:300]}")
    # Persist before evaluating worker-controlled result structure. Successful
    # validation removes it; any exception/crash leaves bounded diagnostics.
    rejected_path=persist_rejected_evidence(run_dir,child,transcript,"validation pending")
    try:
        observed_skills = validate_provenance(transcript, required_skills, profile)
        capability = verify_gsc_readback(transcript, request["site_property"], request.get("urls", [])) if profile == "seo_gsc_readonly" else None
    except ValueError as exc:
        persist_rejected_evidence(run_dir,child,transcript,str(exc))
        raise SystemExit(str(exc)) from exc
    rejected_path.unlink(missing_ok=True)
    if not run_dir.exists():
        run_dir.mkdir(mode=0o750, parents=False)
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise SystemExit("run directory must be canonical and non-linked")
    artifact = run_dir / "result.md"
    artifact.write_text(transcript.final + "\n", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    candidate = {"child_run_id": child, "status": "candidate",
                 "evidence": [{"kind": "artifact", "path": str(artifact), "sha256": digest}],
                 "checks": ["root_owned_claude_stream", "successful_skill_tool_results"],
                 "mutation_audit": {"mutation_state": "none", "successful_tools": [use.get("name") for use in transcript.successful_tools()]}}
    candidate_path = run_dir / "workflow-candidate.json"
    candidate_path.write_text(json.dumps(candidate, sort_keys=True) + "\n", encoding="utf-8")
    for path in (artifact, candidate_path):
        os.chmod(path, 0o640)
        if os.geteuid() == 0:
            if os.environ.get("LHM_WORKFLOW_TEST_MODE") == "1": os.chown(path,os.getuid(),os.getgid())
            else: os.chown(path, 10002, 10000)
    for skill in required_skills:
        subprocess.run([str(hook), "skill", child, skill], check=True)
    if capability:
        subprocess.run([str(hook), "capability", child, capability["capability"]], check=True)
    subprocess.run([str(hook), "complete", child, str(candidate_path)], check=True)
    return {"skills": observed_skills, "capability": capability, "candidate": str(candidate_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("child")
    parser.add_argument("request", type=Path)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    if os.environ.get("LHM_WORKFLOW_TEST_MODE") != "1":
        st = args.request.stat(follow_symlinks=False)
        if st.st_uid != 0 or st.st_mode & 0o022 or args.request.is_symlink():
            raise SystemExit("supervisor request is not root-controlled")
    request = json.loads(args.request.read_text(encoding="utf-8"))
    print(json.dumps(run(request, args.child, args.run_dir), sort_keys=True))


if __name__ == "__main__":
    main()
