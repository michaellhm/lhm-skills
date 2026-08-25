import hashlib
import json
import os
import stat
from types import SimpleNamespace
from pathlib import Path

import pytest

from lhm_workflow.scheduled_executor import (
    ADAPTER, CONTAINER_USER, PROFILE_NAMES, canonical_sha, compare_and_swap_tracker, hermes_argv,
    invoke_registered_adapter, invoke_work_control, materialise_stdout_result, metadata_probe_argv,
    registered_gsc_request, snapshot_sources, validate_closed_result, work_control_request,
)


def test_canonical_sources_drive_absolute_same_property_urls(tmp_path):
    project = tmp_path / "project.md"; project.write_text("Plan /services/seo and https://localhealthmarketing.com/about")
    operating = tmp_path / "operating.md"; operating.write_text("Canonical /contact")
    rollout = tmp_path / "rollout.md"; rollout.write_text("Next /blog/health")
    directory = tmp_path / "rollout"; directory.mkdir()
    (directory / "rollout-state.md").write_text("State /ahpra")
    (directory / "sitemap.json").write_text('{"url":"/locations/sydney"}')
    (directory / "LHM-Proposed-Sitemap.html").write_text('<a href="/services/web">Web</a>')
    records, urls = snapshot_sources([str(project), str(operating), str(rollout), str(directory)], tmp_path / "snapshots", "https://localhealthmarketing.com/")
    assert len(records) == 6
    assert "https://localhealthmarketing.com/services/seo" in urls
    assert "https://localhealthmarketing.com/locations/sydney" in urls
    assert all(url.startswith("https://localhealthmarketing.com/") for url in urls)
    assert all(Path(record["path"]).is_file() and len(record["sha256"]) == 64 for record in records)


def test_tracker_compare_and_swap_and_full_readback(tmp_path):
    tracker = tmp_path / "rollout-state.md"; tracker.write_bytes(b"old")
    expected = hashlib.sha256(b"old").hexdigest()
    receipt = compare_and_swap_tracker(tracker, expected, b"new")
    assert receipt["readback"] and tracker.read_bytes() == b"new"
    with pytest.raises(ValueError, match="conflict"):
        compare_and_swap_tracker(tracker, expected, b"duplicate")
    unchanged = hashlib.sha256(b"new").hexdigest()
    receipt = compare_and_swap_tracker(tracker, unchanged, b"new")
    assert receipt == {"before_sha256": unchanged, "after_sha256": unchanged, "readback": True, "mutation": "none"}


def test_registered_configuration_is_readonly_and_native(tmp_path):
    import json
    registry = json.loads((Path(__file__).parents[1] / "integration" / "scheduled-workflows.json").read_text())
    definition = registry["workflows"]["local-health-marketing-seo"]
    assert definition["gsc"]["route"] == "seo_gsc_readonly"
    assert definition["gsc"]["site_key"] == "lhm-main"
    assert "request_indexing" not in definition["gsc"]["allowed_actions"]
    assert definition["profile_aliases"]["lhm_head_of_production"].endswith("/lhm_production")
    assert definition["profile_aliases"]["lhm_seo_lead"].endswith("/lhm_seo")
    assert definition["permission_ceiling"] == "non-production-preview"
    assert "lhm_operations" in definition["profile_aliases"]


def contract():
    return {"parent_run_id": "parent-1", "child_run_id": "child-1", "owner": "lhm_researcher", "stage_id": "research"}


def closed_result(request_sha="a" * 64, **changes):
    value = {"schema_version": 1, "parent_run_id": "parent-1", "child_run_id": "child-1", "role": "lhm_researcher", "request_sha256": request_sha, "status": "accepted", "artifact_hashes": ["b" * 64], "decision": {}}
    value.update(changes); return value


def test_all_hermes_argv_are_numeric_uid_gid_and_profile_allowlisted():
    for profile in ("lhm_chief_of_staff", "lhm_production", "lhm_seo", "lhm_researcher", "lhm_content", "lhm_website", "lhm_verifier", "lhm_operations", "lhm_learning_steward"):
        argv = hermes_argv(profile, f"/opt/data/profiles/{PROFILE_NAMES[profile]}/dispatch/scheduled-executor/p/c", "closed")
        assert argv[3:6] == ["--user", "10000:10000", "hermes"]
        assert "1000:1000" not in argv
        assert metadata_probe_argv(profile)[3:6] == ["--user", CONTAINER_USER, "hermes"]
        assert "--skills" not in argv
        assert argv[11:13] == ["-t", "file,code_execution" if profile == "lhm_verifier" else "file"]
    assert hermes_argv("lhm_operations", "/opt/data/profiles/lhm_operations_connector/dispatch/scheduled-executor/p/c", "closed")[8] == "lhm_operations_connector"
    with pytest.raises(ValueError, match="unregistered"):
        hermes_argv("lhm_shell", "/opt/data/profiles/lhm_brain/dispatch/scheduled-executor/p/c", "x")


def test_closed_result_binds_request_and_rejects_stale_malformed_and_self_approval(tmp_path):
    path = tmp_path / "result.json"; path.write_text(json.dumps(closed_result()))
    accepted = validate_closed_result(path, contract(), "a" * 64)
    with pytest.raises(ValueError, match="stale"):
        validate_closed_result(path, contract(), "a" * 64, prior_result_sha256=accepted["result_sha256"])
    path.write_text("not-json")
    with pytest.raises(ValueError, match="malformed"): validate_closed_result(path, contract(), "a" * 64)
    path.write_text(json.dumps(closed_result(role="lhm_verifier")))
    with pytest.raises(ValueError, match="binding"): validate_closed_result(path, contract(), "a" * 64)


def test_host_materialises_only_strict_json_stdout(tmp_path):
    path = tmp_path / "result.json"
    model_result = {"status":"accepted","artifact_hashes":["b"*64],"decision":{}}
    materialise_stdout_result(path, json.dumps(model_result), contract(), "a"*64)
    assert json.loads(path.read_text()) == closed_result()
    path.unlink()
    materialise_stdout_result(path, json.dumps({**model_result, "status":"completed"}), contract(), "a"*64)
    assert json.loads(path.read_text()) == closed_result()
    path.unlink()
    for synonym in ("complete", "validated", "success", "succeeded"):
        materialise_stdout_result(path, json.dumps({**model_result, "status":synonym}), contract(), "a"*64)
        assert json.loads(path.read_text()) == closed_result()
        path.unlink()
    materialise_stdout_result(path, "transport noise\n"+json.dumps(model_result)+"\nend noise", contract(), "a"*64)
    assert json.loads(path.read_text()) == closed_result()
    path.unlink()
    with pytest.raises(ValueError, match="one closed JSON"):
        materialise_stdout_result(path, json.dumps(model_result)+json.dumps(model_result), contract(), "a"*64)


def test_deterministic_retry_may_reproduce_identical_closed_result(tmp_path):
    path = tmp_path / "result.json"
    value = closed_result()
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")
    path.unlink()
    materialise_stdout_result(
        path,
        json.dumps({"status": "accepted", "artifact_hashes": ["b" * 64], "decision": {}}),
        contract(),
        "a" * 64,
    )
    assert validate_closed_result(path, contract(), "a" * 64)["value"] == value


def test_registered_gsc_gateway_contract_and_failures():
    urls = ["https://localhealthmarketing.com/about", "https://localhealthmarketing.com/services/seo"]
    request = registered_gsc_request(contract(), "lhm-main", "https://localhealthmarketing.com/", urls)
    assert request["argv"][1] == "submit-seo-gsc-readonly"
    assert request["argv"][2] == "lhm-main"
    assert request["binding"]["operations"] == ["list_sites", "batch_url_inspection", "search_analytics", "list_sitemaps"]
    assert request["argv"][2:4] == ["lhm-main", ",".join(urls)]
    with pytest.raises(ValueError, match="property"):
        registered_gsc_request(contract(), "evil", "https://evil.example/", ["https://evil.example/a"])
    def good(argv, **kwargs):
        evidence="GSC terminal evidence\n"; result={"completion":{"status":"needs_review","profile":"seo_gsc_readonly"},"evidence":evidence,"evidence_sha256":hashlib.sha256(evidence.encode()).hexdigest()}; receipt={"schema_version":1,"operation":"claude_dispatch","binding":request["binding"],"result":result,"receipt_sha256":canonical_sha(result)}
        assert argv == [ADAPTER] and kwargs["input"] == json.dumps(request, sort_keys=True, separators=(",", ":"))
        return SimpleNamespace(returncode=0, stdout=json.dumps(receipt))
    assert invoke_registered_adapter(request, good)["result"]["completion"]["status"] == "needs_review"
    def running(argv, **kwargs):
        result={"status":"running","follow_up_required":True}; receipt={"schema_version":1,"operation":"claude_dispatch","binding":request["binding"],"result":result,"receipt_sha256":canonical_sha(result)}
        return SimpleNamespace(returncode=0, stdout=json.dumps(receipt))
    with pytest.raises(ValueError, match="terminal evidence"):
        invoke_registered_adapter(request, running)
    with pytest.raises(RuntimeError, match="connector failed"):
        invoke_registered_adapter(request, lambda *a, **k: SimpleNamespace(returncode=1, stdout=""))


def test_work_control_exact_stdin_after_hash_verification(tmp_path):
    executable=tmp_path/"work-control"; executable.write_bytes(b"#!/bin/false\n"); executable.chmod(0o700)
    parent={"parent_run_id":"parent-1","objective":"repair","scheduled_contract":{"permission_ceiling":"non-production-preview","completion_test":"passes","work_control":{"path":str(executable),"sha256":hashlib.sha256(executable.read_bytes()).hexdigest(),"return_role":"head_of_production","return_point":"scheduled_parent_ready_before_chief_intake"}}}
    captured={}
    def runner(argv, **kwargs): captured.update(argv=argv, stdin=kwargs["input"]); return SimpleNamespace(returncode=0, stdout="{}")
    expected=work_control_request(parent, contract(), "connector unavailable")
    assert invoke_work_control(parent, contract(), "connector unavailable", runner) == expected
    assert set(expected) == {"parent_run_id", "capability_incident_id", "return_point", "resume_token", "objective", "acceptance_test", "permission_ceiling"}
    assert expected["permission_ceiling"] == "green"
    assert captured == {"argv":["/usr/bin/docker", "exec", "-i", "--user", "10000:10000", "hermes", "/opt/data/profiles/lhm_brain/bin/work-control", "block"], "stdin":json.dumps(expected, sort_keys=True, separators=(",", ":"))}
    executable.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"): invoke_work_control(parent, contract(), "x", runner)


def test_profile_metadata_fixture_requires_numeric_owner_and_0700(tmp_path):
    profile=tmp_path/"lhm_researcher"; profile.write_text("fixture"); profile.chmod(0o700)
    observed={"uid":10000,"gid":10000,"mode":stat.S_IMODE(profile.stat().st_mode)}
    assert observed == {"uid":10000,"gid":10000,"mode":0o700}
    assert {**observed,"uid":1000} != observed


def test_safe_retry_interruption_and_scheduler_business_separation_are_persisted_contracts():
    source=(Path(__file__).parents[1]/"src/lhm_workflow/scheduled_executor.py").read_text()
    runtime=(Path(__file__).parents[1]/"integration/lhm-scheduled-work-runtime").read_text()
    assert '"safe_retry": 1' in source and 'previous.get("failed_child") != child' in source
    assert source.count("result.unlink(missing_ok=True)") >= 2
    assert 'contract["stage_id"] == "seo_accept" else {}' in source
    assert 'if contract["stage_id"] == "context" else' in source
    assert 'prior and contract["input_artifacts"]' in source
    assert '"input_artifact_paths":private_inputs' in source
    assert 'os.chown(registry_path,10004,10004)' in source
    assert 'self.root / "verifier-signing-inputs"' in source
    assert 'candidate_urls[:25]' in source and 'request_value.get("phase") == "synthesis"' in source
    assert 'GSC connector did not return terminal evidence' in source
    assert 'connector_receipt=validate_registered_adapter_receipt(existing["receipt"],connector_request)' in source
    assert 'contract["stage_id"] == "operations_write" and parent["scheduled_contract"]["permission_ceiling"] == "non-production-preview"' in source
    assert 'contract["stage_id"] == "operations_readback" and parent["scheduled_contract"]["permission_ceiling"] == "non-production-preview"' in source
    assert 'outputs=contract["input_artifacts"]' in source
    dispatch=(Path(__file__).parents[1]/"integration/claude-dispatch.live-reference").read_text()
    assert 'max_wait_seconds=540' in dispatch and 'def enqueue_and_wait(request, max_wait_seconds=240)' in dispatch
    adapter=(Path(__file__).parents[1]/"integration/lhm-workflow-registered-adapter").read_text()
    assert adapter.index('completion = json.loads(lines[0])') < adapter.index('result = json.loads(lines[-1])')
    assert 'if not self.router._path(parent_id).exists()' in source
    assert '"scheduler": "accepted"' in runtime and '"business": business' in runtime
    assert "shutil.move(path, PROCESSED / path.name)" in runtime
