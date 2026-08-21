import json
import hashlib
import os
import subprocess
import sys
from pathlib import Path
import pytest

from integration.lhm_claude_trusted_supervisor import Transcript, verify_gsc_readback, validate_provenance, persist_rejected_evidence, run
from lhm_workflow.host_bridge import BridgeRoots, process_manifest


def event(use_id, name, data):
    return json.dumps({"type":"assistant","message":{"content":[{"type":"tool_use","id":use_id,"name":name,"input":data}]}})


def result(use_id, error=False, content="ok"):
    return json.dumps({"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":use_id,"is_error":error,"content":content}]}})


def test_skill_requires_correlated_successful_result():
    t=Transcript(); t.feed(event("a","Skill",{"skill":"lhm-marketing-hub:seo-audit"}))
    assert t.skills()==[]
    t.feed(result("a")); assert t.skills()==["lhm-marketing-hub:seo-audit"]


def test_failed_skill_result_is_not_provenance():
    t=Transcript(); t.feed(event("a","Skill",{"skill":"wanted"})); t.feed(result("a",True))
    assert t.skills()==[]


@pytest.mark.parametrize("lines", [
    ["worker prose pretending to be stream json"],
    [event("a","Skill",{"skill":"wanted"}), event("a","Skill",{"skill":"wanted"})],
    [result("missing")],
])
def test_malformed_duplicate_or_orphan_stream_fails_closed(lines):
    t=Transcript()
    for line in lines: t.feed(line)
    assert t.malformed or not t.skills()


def gsc_transcript(prop, urls):
    t=Transcript()
    calls=[
      ("1","mcp__gscServer__list_sites",{}),
      ("2","mcp__gscServer__batch_url_inspection",{"siteUrl":prop,"urls":urls}),
      ("3","mcp__gscServer__search_analytics",{"siteUrl":prop}),
      ("4","mcp__gscServer__list_sitemaps",{"siteUrl":prop}),
    ]
    for ident,name,data in calls:
        content = json.dumps({"sites":[prop]}) if ident == "1" else json.dumps({"urls":urls}) if ident == "2" else json.dumps({"rows":[]}) if ident == "3" else json.dumps({"sitemaps":[]})
        t.feed(event(ident,name,data)); t.feed(result(ident, content=content))
    return t


def test_gsc_capability_requires_successful_scoped_readbacks():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]
    proof=verify_gsc_readback(gsc_transcript(prop,urls),prop,urls)
    assert proof["capability"]=="google_search_console.property_read"
    assert proof["mutation_state"]=="none"


@pytest.mark.parametrize("payload",[
    {"siteEntry":[{"siteUrl":"https://localhealthmarketing.com/","permissionLevel":"siteOwner"}]},
    {"siteEntries":[{"siteUrl":"https://localhealthmarketing.com/"}]},
    {"sites":[{"siteUrl":"https://localhealthmarketing.com/"}]},
])
def test_gsc_list_sites_normalizes_known_structured_shapes(payload):
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["1"]["content"]=json.dumps(payload)
    assert verify_gsc_readback(t,prop,urls)["property"]==prop


def test_rejected_tool_evidence_is_persisted_and_redacted(tmp_path):
    t=Transcript(); t.feed(event("1","mcp__gscServer__list_sites",{"authorization":"bearer secret"}))
    t.feed(result("1",content=json.dumps({"siteEntry":[{"siteUrl":"sc-domain:example.test"}],"token":"secret"})))
    path=persist_rejected_evidence(tmp_path/"run","child-1",t,"property absent")
    value=json.loads(path.read_text()); raw=path.read_text()
    assert value["status"]=="rejected" and value["reason"]=="property absent"
    assert "bearer secret" not in raw and value["tool_calls"][0]["input"]["authorization"]=="[REDACTED]"
    assert path.stat().st_mode & 0o777 == 0o600


def test_gsc_inspection_aggregates_coverage_across_successful_calls():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/",prop+"services/"]
    t=gsc_transcript(prop,[urls[0]])
    t.feed(event("5","mcp__gscServer__batch_url_inspection",{"siteUrl":prop,"inspectionUrls":[urls[1]]}))
    t.feed(result("5",content=json.dumps({"urls":[urls[1]]})))
    proof=verify_gsc_readback(t,prop,urls)
    assert proof["urls"]==urls


def test_gsc_inspection_incomplete_aggregate_fails_closed():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/",prop+"services/"]
    with pytest.raises(ValueError,match="omitted an admitted URL across"):
        verify_gsc_readback(gsc_transcript(prop,[urls[0]]),prop,urls)


def test_gsc_inspection_rejects_unadmitted_url_in_any_call():
    prop="https://localhealthmarketing.com/"; admitted=[prop+"seo/"]; t=gsc_transcript(prop,admitted)
    escaped="https://evil.invalid/x"
    t.feed(event("5","mcp__gscServer__batch_url_inspection",{"siteUrl":prop,"urls":[escaped]}))
    t.feed(result("5",content=json.dumps({"urls":[escaped]})))
    with pytest.raises(ValueError,match="escaped the admitted property"):
        verify_gsc_readback(t,prop,admitted)


def test_gsc_allows_bounded_read_only_diagnostic_expansion_inside_property():
    prop="https://localhealthmarketing.com/"; admitted=[prop+"blog/target"]
    related=[prop+"blog/",prop+"blog/related"]
    t=gsc_transcript(prop,admitted)
    t.feed(event("5","mcp__gscServer__batch_url_inspection",{"siteUrl":prop,"inspectionUrls":related}))
    t.feed(result("5",content=json.dumps({"urls":related})))
    proof=verify_gsc_readback(t,prop,admitted)
    assert set(proof["observed_urls"])==set(admitted+related)


def test_gsc_rejects_property_hidden_in_unstructured_field():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.uses["3"]["input"]={"property":"https://evil.invalid/","note":prop}
    with pytest.raises(ValueError,match="escaped the admitted property"):
        verify_gsc_readback(t,prop,urls)


@pytest.mark.parametrize("ident,payload",[("3",{"rows":[],"meta":{"error":"denied"}}),("4",{}),("4",{"sitemaps":[],"errors":["denied"]})])
def test_gsc_rejects_parsed_errors_and_empty_required_results(ident,payload):
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results[ident]["content"]=json.dumps(payload)
    with pytest.raises(ValueError,match="error|empty"):
        verify_gsc_readback(t,prop,urls)


def test_gsc_sitemap_zero_error_count_is_not_a_failure():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["4"]["content"]=json.dumps({"sitemap":[{"path":"sitemap.xml","errors":0},{"path":"posts.xml","errors":"0"}]})
    assert verify_gsc_readback(t,prop,urls)["property"]==prop


def test_gsc_sitemap_nonzero_error_count_fails_closed():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["4"]["content"]=json.dumps({"sitemap":[{"path":"sitemap.xml","errors":1}]})
    with pytest.raises(ValueError,match="contained an error"):
        verify_gsc_readback(t,prop,urls)


def test_gsc_ignores_redundant_search_analytics_overflow_when_structured_read_exists():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.feed(event("5","mcp__gscServer__search_analytics",{"siteUrl":prop}))
    t.feed(result("5",content="Error: result (123,547 characters) exceeds maximum allowed tokens. Output has been saved locally."))
    assert verify_gsc_readback(t,prop,urls)["property"]==prop


def test_gsc_overflow_alone_does_not_satisfy_required_search_analytics_read():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["3"]["content"]="Error: result (123,547 characters) exceeds maximum allowed tokens. Output has been saved locally."
    with pytest.raises(ValueError,match="missing successful GSC readbacks"):
        verify_gsc_readback(t,prop,urls)


def test_gsc_rejects_unadmitted_url_returned_under_structured_field():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["2"]["content"]=json.dumps({"results":[{"inspectionUrl":urls[0]},{"inspectionUrl":"https://evil.invalid/x"}]})
    with pytest.raises(ValueError,match="response escaped"):
        verify_gsc_readback(t,prop,urls)


def test_gsc_wrong_property_fails_closed():
    prop="https://localhealthmarketing.com/"; t=gsc_transcript("https://evil.invalid/",["https://evil.invalid/x"])
    with pytest.raises(ValueError,match="escaped|absent"): verify_gsc_readback(t,prop,[prop+"seo/"])


def test_gsc_missing_or_failed_readback_fails_closed():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.results["3"]["is_error"]=True
    with pytest.raises(ValueError,match="missing successful"): verify_gsc_readback(t,prop,urls)


def test_mutating_or_unlisted_tool_never_satisfies_gsc_boundary():
    prop="https://localhealthmarketing.com/"; urls=[prop+"seo/"]; t=gsc_transcript(prop,urls)
    t.feed(event("5","mcp__gscServer__submit_sitemap",{"siteUrl":prop})); t.feed(result("5"))
    proof=verify_gsc_readback(t,prop,urls)
    assert "submit_sitemap" not in " ".join(proof["successful_tools"])


def test_supervisor_rejects_extra_or_reordered_successful_skills(tmp_path, monkeypatch):
    t=Transcript()
    for ident,skill in (("1","second"),("2","first")):
        t.feed(event(ident,"Skill",{"skill":skill})); t.feed(result(ident))
    with pytest.raises(ValueError,match="sequence mismatch"):
        validate_provenance(t,["first","second"],"specialist_readonly")


def test_supervisor_rejects_successful_tool_outside_allowlist():
    t=Transcript(); t.feed(event("1","Skill",{"skill":"wanted"})); t.feed(result("1"))
    t.feed(event("2","Bash",{"command":"true"})); t.feed(result("2"))
    with pytest.raises(ValueError,match="outside allowlist"):
        validate_provenance(t,["wanted"],"specialist_readonly")


def test_hook_to_bridge_end_to_end(tmp_path, monkeypatch):
    base=tmp_path/"state"; runs=tmp_path/"runs"; runs.mkdir(); child="c-seo-1"
    contract={"parent_run_id":"p1","child_run_id":child,"workflow_id":"seo-content-astro-v1","stage_id":"seo_evidence",
      "idempotency_key":"a"*64,"worker":{"runtime":"claude","identity":"lhm-marketing-hub:seo","run_id":child},
      "required_skills":["lhm-marketing-hub:seo-audit"],"required_capabilities":["google_search_console.property_read"],"expected_mutation_state":"none"}
    outbox=base/"controller-outgoing"; outbox.mkdir(parents=True); source=outbox/f"{child}.json"
    source.write_text(json.dumps(contract,sort_keys=True,separators=(",",":"))+"\n"); source.chmod(0o600)
    fake=tmp_path/"claude"; prop="https://localhealthmarketing.com/"; url=prop+"seo/"
    lines=[event("s","Skill",{"skill":"lhm-marketing-hub:seo-audit"}),result("s")]
    for ident,name,data,content in [
      ("1","mcp__gscServer__list_sites",{},json.dumps({"sites":[prop]})),
      ("2","mcp__gscServer__batch_url_inspection",{"siteUrl":prop,"inspectionUrls":[url]},json.dumps({"urls":[url]})),
      ("3","mcp__gscServer__search_analytics",{"siteUrl":prop},json.dumps({"rows":[]})),
      ("4","mcp__gscServer__list_sitemaps",{"siteUrl":prop},json.dumps({"sitemaps":[]}))]:
        lines += [event(ident,name,data),result(ident,content=content)]
    lines.append(json.dumps({"type":"result","result":"trusted seo evidence"}))
    fake.write_text(f"#!{sys.executable}\nimport json\nfor line in {lines!r}: print(line)\n"); fake.chmod(0o755)
    hook=Path(__file__).parents[1]/"integration/hermes_workflow_hook.py"
    monkeypatch.setenv("LHM_WORKFLOW_TEST_MODE","1"); monkeypatch.setenv("LHM_WORKFLOW_ROOT",str(base))
    monkeypatch.setenv("LHM_CLAUDE_RUNS",str(runs)); monkeypatch.setenv("LHM_CLAUDE_BINARY",str(fake))
    monkeypatch.setenv("LHM_WORKFLOW_HOOK",str(hook)); monkeypatch.setenv("LHM_CLAUDE_PLUGIN",str(tmp_path/"plugin"))
    monkeypatch.setenv("LHM_GSC_CONFIG",str(tmp_path/"gsc.json"))
    subprocess.run([str(hook),"admit",str(source),child],check=True)
    request={"profile":"seo_gsc_readonly","required_skills":contract["required_skills"],"required_capabilities":contract["required_capabilities"],
      "objective":"Inspect the admitted URLs with live read-only evidence.","site_property":prop,"urls":[url],"timeout_seconds":30}
    run(request,child,runs/child)
    manifest=base/"bridge-incoming"/f"{child}.json"
    roots=BridgeRoots(base/"issued-contracts",base/"host-events",base/"worker-results",base/"adapter-source",base/"processed"/"bridge",base/"quarantine"/"bridge")
    output=process_manifest(manifest,roots,root_uid=os.getuid(),worker_uids={"claude":os.getuid()},adapter_gid=os.getgid())
    receipt=json.loads(output.read_text())
    assert receipt["status"]=="candidate"
    assert receipt["host_provenance"]["observed_skill_calls"]==contract["required_skills"]
