import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
import subprocess
import stat
import sys
import types
from pathlib import Path
import pytest


PLUGIN = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((PLUGIN / "references/shared-claude-gateway-release.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_shared_gateway_sources_match_verified_inventory():
    assert MANIFEST["capability_id"] == "CAP-015"
    assert MANIFEST["release_version"] == "0.9.11"
    for name in MANIFEST["assets"]:
        item = MANIFEST["assets"][name]
        source = PLUGIN / item["source"]
        assert source.is_file()
        if "size_bytes" in item:
            assert source.stat().st_size == item["size_bytes"]
        assert digest(source) == item["sha256"]


def test_shared_gateway_destinations_are_exact_and_distinct_from_evidence_bridge():
    assets = MANIFEST["assets"]
    assert assets["dispatcher"]["destination"] == "/usr/local/libexec/lhm-claude-dispatcher"
    assert assets["worker"]["destination"] == "/usr/local/libexec/lhm-claude-worker"
    assert "lhm-evidence-claude" not in assets["dispatcher"]["destination"]
    assert "lhm-evidence-claude" not in assets["worker"]["destination"]
    assert assets["dispatcher"]["mode"] == assets["worker"]["mode"] == "0755"


def test_container_client_is_governed_at_exact_bind_mount_target():
    client = MANIFEST["assets"]["container_client"]
    assert client["destination"] == "/home/hermes/.hermes/profiles/lhm_brain/bin/claude-dispatch"
    assert client["container_destination"] == "/opt/data/profiles/lhm_brain/bin/claude-dispatch"
    assert client["previous_sha256"] == "e11acaa73629e5841811237a16339832b834d5c51741afb256205dc6d182df66"
    assert client["owner"] == client["group"] == 10000
    assert client["mode"] == "0755"


def test_container_client_uses_collision_safe_ids_and_bounded_google_ads_timeout():
    client = PLUGIN / MANIFEST["assets"]["container_client"]["source"]
    repaired = client.read_bytes()
    submitted_timeout = (
        b"'profile': 'google_ads_readonly', 'agent_id': 'lhm-marketing-hub:google-ads', "
        b"'client': client, 'objective': objective, 'timeout_seconds': 600, "
    )
    assert repaired.count(submitted_timeout) == 1
    assert repaired.count(b"next_run_id('claude-gads')") == 1
    assert repaired.count(b"next_run_id('claude-mktg')") == 1
    assert b"for bucket in ('incoming', 'processed', 'runs', 'failed')" in repaired
    assert b"'profile': 'google_ads_readonly'" in repaired
    assert b"'timeout_seconds': 600" in repaired


def test_dispatcher_contains_current_bounded_worker_contract():
    text = (PLUGIN / MANIFEST["assets"]["dispatcher"]["source"]).read_text()
    assert "ensure_worker_traversal" in text
    assert "configure_worker_run_dir" in text
    assert "'/usr/sbin/runuser', '--user', 'claudeworker'" in text
    assert "/usr/local/libexec/lhm-claude-worker" in text
    assert "google_ads_readonly" in text
    assert "Path('/home/hermes/.hermes')," in text
    assert "Path('/home/hermes/.hermes/profiles/lhm_brain')," in text
    assert "'u:claudeworker:rwx', str(run_dir)" in text
    assert "setfacl', '-R'" not in text
    assert "def load_google_ads_evidence(client):" in text
    assert "expected_prefix = client['evidence_prefix']" in text
    assert "registered evidence pack exceeds total limit" in text
    assert "prompt['evidence_pack'] = load_google_ads_evidence(client)" in text
    assert "required_timeout = admitted_timeout_seconds(profile)" in text
    assert "def durable_registry_backup():" in text
    assert "def governed_registry_backup_dir():" in text
    assert "os.O_EXCL" in text
    assert "getattr(os, 'O_DIRECTORY', 0)" in text
    assert "os.fsync(handle.fileno())" in text
    assert "def durable_registry_restore(backup):" in text
    assert "restored registry readback mismatch" in text
    assert "registry backup failed" in text
    assert "with HANDBACK_REGISTRY.open('w'" in text
    assert "registry update failed and backup restored with readback" in text


def test_dispatch_unit_grants_only_exact_registry_write_path():
    unit = (PLUGIN / MANIFEST["assets"]["dispatch_unit"]["source"]).read_text()
    assert "ReadWritePaths=/home/hermes/.hermes/profiles/lhm_brain/dispatch/claude" in unit
    assert "ReadWritePaths=/home/hermes/.hermes/profiles/lhm_brain/config/client-handback-targets.json" in unit
    assert "ReadWritePaths=/home/hermes/.hermes/profiles/lhm_brain/config\n" not in unit


def test_google_ads_profile_admits_only_extended_bounded_timeout():
    dispatcher = load_dispatcher()
    assert dispatcher.admitted_timeout_seconds("google_ads_readonly") == 600
    assert 300 != dispatcher.admitted_timeout_seconds("google_ads_readonly")
    assert dispatcher.admitted_timeout_seconds("handback_target_registration") == 30
    assert dispatcher.admitted_timeout_seconds("html_artifact_producer") == 1200


def test_google_ads_runtime_extension_preserves_readonly_tool_and_budget_ceiling():
    worker = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "max_turns, budget = ('24', '4.00')" in worker
    assert "if is_marketing else 'Skill'" in worker
    assert "google-ads-readonly.mcp.json" in worker
    assert "mcp__GoogleAds__execute_gaql" in worker
    for forbidden in ("mcp__GoogleAds__mutate", "Bash", "WebFetch", "WebSearch"):
        assert forbidden not in worker


def test_google_ads_worker_enters_canonical_command_and_verifies_real_skill_calls():
    worker = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "/lhm-marketing-hub:start-googleads" in worker
    assert "'--output-format', output_format" in worker
    assert "output_format = 'stream-json' if is_observed_skill_profile else 'json'" in worker
    assert "block.get('type') == 'tool_use' and block.get('name') == 'Skill'" in worker
    assert "'lhm-marketing-hub:google-ads-monthly-review'" in worker
    assert "'lhm-marketing-hub:bid-budget-optimizer'" in worker
    assert "'lhm-marketing-hub:google-ads-conversion-audit'" in worker
    assert "'lhm-marketing-hub:google-ads-delivery-qa'" in worker
    assert "skill-provenance.json" in worker
    assert "missing required Skill tool calls" in worker


def test_connector_client_waits_past_the_worker_timeout_without_returning_running():
    client = (PLUGIN / MANIFEST["assets"]["container_client"]["source"]).read_text()
    for profile_call in (
        "submit_drive_file", "submit_basicops_discussion",
        "submit_basicops_baton", "observe_basicops_human",
    ):
        start = client.index(f"def {profile_call}")
        end = client.find("\ndef ", start + 5)
        assert "max_wait_seconds=610" in client[start:end]


def test_root_owned_contract_table_pins_every_live_workflow_and_route():
    dispatcher = load_dispatcher()
    expected = {
        "google_ads_readonly": ("google-ads-monthly-review", (
            "lhm-marketing-hub:google-ads-monthly-review",
            "lhm-marketing-hub:bid-budget-optimizer",
            "lhm-marketing-hub:google-ads-conversion-audit",
            "lhm-marketing-hub:google-ads-delivery-qa",
        ), ("google_ads.account_read",)),
        "marketing_orchestrator_readonly": ("marketing-review", ("lhm-marketing-hub:start",), ("google_ads.account_read",)),
        "seo_gsc_readonly": ("seo-gsc-review", ("lhm-marketing-hub:seo-audit",), ("google_search_console.property_read",)),
        "google_drive_client_file_create": ("google-drive-file-publish", ("google-drive:google-drive",), ("google_drive.file_create", "google_drive.file_readback")),
        "basicops_task_discussion_update": ("basicops-task-discussion-update", ("lhm-project-hub:basicops-task-manager",), ("basicops.task_read", "basicops.discussion_create", "basicops.discussion_readback")),
        "basicops_task_baton_transition": ("basicops-task-baton-transition", ("lhm-project-hub:basicops-task-manager",), ("basicops.task_read", "basicops.task_update", "basicops.discussion_create", "basicops.discussion_readback")),
        "basicops_human_decision_observe": ("basicops-human-decision-observe", (), ("basicops.task_read", "basicops.discussion_readback")),
        "handback_target_registration": ("handback-target-registration", ("lhm-connector-repair:handback-target-registration",), ()),
        "html_artifact_producer": ("html-artifact-production", ("lhm-marketing-hub:content",), ()),
    }
    for profile, contract in expected.items():
        assert dispatcher.admitted_contract(profile) == contract
    for route, skill in dispatcher.SPECIALIST_SKILLS.items():
        assert dispatcher.admitted_contract("specialist_readonly", route) == (
            f"{route}-review", (skill,), ())
    assert dispatcher.admitted_contract("specialist_readonly", "unknown") is None


def test_seo_lead_route_is_distinct_and_preserves_existing_seo_contracts():
    dispatcher = load_dispatcher()
    assert dispatcher.SPECIALIST_ROUTES["seo-lead"] == ("lhm-marketing-hub:seo", "seo")
    assert dispatcher.SPECIALIST_SKILLS["seo-lead"] == "lhm-marketing-hub:start-seo"
    assert dispatcher.SPECIALIST_ROUTES["keyword-research"] == ("lhm-marketing-hub:seo", "seo")
    assert dispatcher.SPECIALIST_SKILLS["keyword-research"] == "lhm-marketing-hub:keyword-research"
    assert dispatcher.SPECIALIST_ROUTES["seo-delivery-qa"] == ("lhm-marketing-hub:seo", "seo")
    assert dispatcher.SPECIALIST_SKILLS["seo-delivery-qa"] == "lhm-marketing-hub:seo-delivery-qa"
    assert dispatcher.admitted_contract("specialist_readonly", "seo-lead") == (
        "seo-lead-review", ("lhm-marketing-hub:start-seo",), ())
    assert dispatcher.SPECIALIST_ROUTES["seo"] == ("lhm-marketing-hub:seo", "seo")
    assert dispatcher.SPECIALIST_SKILLS["seo"] == "lhm-marketing-hub:seo-audit"
    assert dispatcher.admitted_contract("seo_gsc_readonly") == (
        "seo-gsc-review", ("lhm-marketing-hub:seo-audit",),
        ("google_search_console.property_read",))


def test_project_production_plan_route_is_closed_and_preserves_team_brief_route():
    dispatcher = load_dispatcher()
    assert dispatcher.SPECIALIST_ROUTES["project"] == (
        "lhm-project-hub:pm-orchestrator", "pm-orchestrator")
    assert dispatcher.SPECIALIST_SKILLS["project"] == "lhm-project-hub:team-work-brief"
    assert dispatcher.SPECIALIST_ROUTES["project-production-plan"] == (
        "lhm-project-hub:pm-orchestrator", "pm-orchestrator")
    assert dispatcher.SPECIALIST_SKILLS["project-production-plan"] == (
        "lhm-project-hub:hermes-production-plan")
    assert dispatcher.admitted_contract("specialist_readonly", "project-production-plan") == (
        "project-production-plan-review", ("lhm-project-hub:hermes-production-plan",), ())


def test_container_client_submits_exact_seo_lead_contract(monkeypatch):
    client_path = PLUGIN / MANIFEST["assets"]["container_client"]["source"]
    spec = importlib.util.spec_from_loader(
        "shared_client", SourceFileLoader("shared_client", str(client_path)))
    client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client)
    captured = []
    monkeypatch.setattr(client, "next_run_id", lambda prefix: "claude-delegate-20260824-01")
    monkeypatch.setattr(client, "enqueue_and_wait", captured.append)
    client.submit_specialist("seo-lead", "internal", "marketing", "Run the seven-page modality SEO review.")
    assert captured == [{
        "schema_version": 1,
        "run_id": "claude-delegate-20260824-01",
        "profile": "specialist_readonly",
        "agent_id": "lhm-marketing-hub:seo",
        "route": "seo-lead",
        "subject_type": "internal",
        "subject_name": "marketing",
        "objective": "Run the seven-page modality SEO review.",
        "approval_state": "review_only",
        "timeout_seconds": 600,
        "workflow_id": "seo-lead-review",
        "required_skills": ["lhm-marketing-hub:start-seo"],
        "required_capabilities": [],
    }]


def test_container_client_selects_production_plan_for_exact_pm_skill(monkeypatch):
    client_path = PLUGIN / MANIFEST["assets"]["container_client"]["source"]
    spec = importlib.util.spec_from_loader(
        "shared_client_project_plan", SourceFileLoader("shared_client_project_plan", str(client_path)))
    client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client)
    captured = []
    monkeypatch.setattr(client, "next_run_id", lambda prefix: "claude-delegate-20260826-01")
    monkeypatch.setattr(client, "enqueue_and_wait", captured.append)
    client.submit_specialist(
        "project", "general", "page-copy",
        "Invoke lhm-project-hub:hermes-production-plan and select the canonical SOP.")
    assert captured[0]["route"] == "project-production-plan"
    assert captured[0]["workflow_id"] == "project-production-plan-review"
    assert captured[0]["required_skills"] == ["lhm-project-hub:hermes-production-plan"]


def test_dispatcher_rejects_forged_contract_before_any_worker_run(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    incoming = tmp_path / "incoming"
    failed = tmp_path / "failed"
    incoming.mkdir()
    failed.mkdir()
    monkeypatch.setattr(dispatcher, "FAILED", failed)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    base = {
        "schema_version": 1,
        "run_id": "claude-delegate-20260823-01",
        "profile": "specialist_readonly",
        "agent_id": "lhm-marketing-hub:seo",
        "route": "seo",
        "subject_type": "internal",
        "subject_name": "Local Health Marketing",
        "objective": "Review the bounded SEO opportunity and return evidence.",
        "approval_state": "review_only",
        "timeout_seconds": 600,
        "workflow_id": "seo-review",
        "required_skills": ["lhm-marketing-hub:seo-audit"],
        "required_capabilities": [],
    }
    mutations = (
        {"workflow_id": "content-review"},
        {"required_skills": ["lhm-marketing-hub:content-strategy"]},
        {"required_skills": ["lhm-marketing-hub:seo-audit", "lhm-marketing-hub:seo-audit"]},
        {"required_capabilities": ["google_ads.account_read"]},
    )
    for sequence, changes in enumerate(mutations, 1):
        request = dict(base)
        request["run_id"] = f"claude-delegate-20260823-{sequence:02d}"
        request.update(changes)
        queued = incoming / f"request-{sequence}.json"
        queued.write_text(json.dumps(request))
        dispatcher.process(queued)
        assert not queued.exists()
        error = (failed / f"request-{sequence}.error").read_text()
        assert "contract does not match" in error


def test_seo_lead_forgery_is_rejected_before_worker_launch(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    incoming = tmp_path / "incoming"
    failed = tmp_path / "failed"
    incoming.mkdir()
    failed.mkdir()
    monkeypatch.setattr(dispatcher, "FAILED", failed)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    launched = []
    monkeypatch.setattr(dispatcher.subprocess, "run", lambda *args, **kwargs: launched.append(args))
    base = {
        "schema_version": 1, "run_id": "claude-delegate-20260824-01",
        "profile": "specialist_readonly", "agent_id": "lhm-marketing-hub:seo",
        "route": "seo-lead", "subject_type": "internal", "subject_name": "marketing",
        "objective": "Run the bounded seven-page modality SEO review.",
        "approval_state": "review_only", "timeout_seconds": 600,
        "workflow_id": "seo-lead-review",
        "required_skills": ["lhm-marketing-hub:start-seo"], "required_capabilities": [],
    }
    mutations = (
        {"workflow_id": "seo-review"},
        {"required_skills": ["lhm-marketing-hub:seo-audit"]},
        {"required_skills": ["lhm-marketing-hub:start-seo", "lhm-marketing-hub:seo-audit"]},
        {"required_skills": ["lhm-marketing-hub:seo-audit", "lhm-marketing-hub:start-seo"]},
        {"required_capabilities": ["google_search_console.property_read"]},
        {"agent_id": "lhm-marketing-hub:start"},
        {"approval_state": "approved"},
        {"unknown": "field"},
    )
    for sequence, changes in enumerate(mutations, 1):
        request = dict(base)
        request["run_id"] = f"claude-delegate-20260824-{sequence:02d}"
        request.update(changes)
        queued = incoming / f"forged-{sequence}.json"
        queued.write_text(json.dumps(request))
        dispatcher.process(queued)
        assert (failed / f"forged-{sequence}.error").is_file()
    assert launched == []


def test_specialist_skill_invocation_is_observed_not_self_attested():
    worker = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "is_observed_skill_profile = is_google_ads or is_specialist" in worker
    assert "required_observed_skills" in worker
    assert "required_observed_skills.issubset(set(skill_calls))" in worker
    assert "'workflow_id': prompt_data.get('workflow_id')" in worker
    assert "'skill_provenance': prompt_data.get('skill_provenance_mode'" in worker


@pytest.mark.parametrize("observed_skill, expected_status", [
    ("lhm-marketing-hub:start-seo", "needs_review"),
    (None, "failed"),
    ("lhm-marketing-hub:seo-audit", "failed"),
])
def test_seo_lead_worker_requires_real_start_seo_skill_call(
        tmp_path, observed_skill, expected_status):
    worker_source = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    fake_claude = tmp_path / "fake-claude"
    events = []
    if observed_skill is not None:
        events.append({
            "type": "assistant", "message": {"content": [{
                "type": "tool_use", "name": "Skill", "input": {"skill": observed_skill},
            }]},
        })
    events.append({
        "type": "result",
        "result": "Invoked lhm-marketing-hub:start-seo and completed the review.",
    })
    fake_claude.write_text(
        "#!/usr/bin/env python3\nimport json\n" +
        "events = " + repr(events) + "\n" +
        "for event in events: print(json.dumps(event))\n")
    fake_claude.chmod(0o755)
    worker = tmp_path / "worker.py"
    worker.write_text(worker_source.replace(
        "'/home/claudeworker/.local/bin/claude'", repr(str(fake_claude))).replace(
        "cwd=worker_home", "cwd=" + repr(str(tmp_path))))
    run_dir = tmp_path / ("run-" + (observed_skill or "prose").split(":")[-1])
    run_dir.mkdir()
    (run_dir / "events.jsonl").write_text("")
    (run_dir / "prompt.json").write_text(json.dumps({
        "profile": "specialist_readonly",
        "agent_id": "lhm-marketing-hub:seo",
        "claude_agent": "seo",
        "route": "seo-lead",
        "subject_type": "internal",
        "subject_name": "marketing",
        "objective": "Run the seven-page modality SEO review.",
        "approval_state": "review_only",
        "workflow_id": "seo-lead-review",
        "required_skills": ["lhm-marketing-hub:start-seo"],
        "required_capabilities": [],
        "skill_provenance_mode": "observed",
    }))
    completed = subprocess.run(
        [sys.executable, str(worker), str(run_dir), "30"], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    final = json.loads((run_dir / "final.json").read_text())
    assert final["status"] == expected_status
    provenance = run_dir / "skill-provenance.json"
    if expected_status == "needs_review":
        assert json.loads(provenance.read_text())["observed_skill_calls"] == [
            "lhm-marketing-hub:start-seo"]
    else:
        assert not provenance.exists()
        assert "missing required Skill tool calls" in (run_dir / "error.txt").read_text()


def test_worker_persists_terminal_artifacts_inside_supplied_run_directory():
    text = (PLUGIN / MANIFEST["assets"]["worker"]["source"]).read_text()
    assert "run_dir = Path(sys.argv[1]).resolve()" in text
    assert "(run_dir / 'result.md').write_text" in text
    assert "(run_dir / 'final.json').write_text" in text
    assert "--strict-mcp-config" in text
    assert "The evidence pack is host-validated reference material" in text
    assert "Canonical reconciliation evidence supplied by Hermes" in text
    assert "provisioned_tools = 'Agent,Skill' if is_marketing else 'Skill'" in text


def test_google_ads_evidence_pack_is_bounded_hashed_and_client_scoped(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    vault = tmp_path / "vault"
    allowed = vault / "20 Clients/Any Stage Physio/project-management/Google Ads.md"
    allowed.parent.mkdir(parents=True)
    allowed.write_text("canonical commitments\n")
    monkeypatch.setattr(dispatcher, "VAULT", vault)
    client = {
        "name": "Any Stage Physio",
        "evidence_prefix": "20 Clients/Any Stage Physio/",
        "evidence_files": ["20 Clients/Any Stage Physio/project-management/Google Ads.md"],
    }
    pack = dispatcher.load_google_ads_evidence(client)
    assert pack == [{
        "path": "20 Clients/Any Stage Physio/project-management/Google Ads.md",
        "sha256": hashlib.sha256(b"canonical commitments\n").hexdigest(),
        "content": "canonical commitments\n",
    }]

    client["evidence_files"] = ["20 Clients/Another Client/project-management/Google Ads.md"]
    other = vault / client["evidence_files"][0]
    other.parent.mkdir(parents=True)
    other.write_text("wrong client\n")
    # Registry validation is the first scope boundary; the loader independently
    # remains confined to the vault root for already validated registrations.
    monkeypatch.setattr(dispatcher, "CLIENT_REGISTRY", tmp_path / "clients.json")
    dispatcher.CLIENT_REGISTRY.write_text(json.dumps({"clients": {"any-stage-physio": {
        "name": "Any Stage Physio", "customer_id": "5308308105", "manager_id": "3947361921",
        "evidence_prefix": "20 Clients/Any Stage Physio/",
        "evidence_files": client["evidence_files"],
    }}}))
    try:
        dispatcher.load_clients()
    except SystemExit as exc:
        assert "outside registered scope" in str(exc)
    else:
        raise AssertionError("cross-client evidence registration was accepted")


def test_evidence_prefix_is_independent_of_client_display_name(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    registry = tmp_path / "clients.json"
    registry.write_text(json.dumps({"clients": {"mhealth": {
        "name": "mhealth", "customer_id": "2228366786", "manager_id": "3947361921",
        "evidence_prefix": "20 Clients/Mhealth/",
        "evidence_files": ["20 Clients/Mhealth/project-management/Google Ads.md"],
    }}}))
    monkeypatch.setattr(dispatcher, "CLIENT_REGISTRY", registry)
    assert dispatcher.load_clients()["mhealth"]["evidence_prefix"] == "20 Clients/Mhealth/"


def test_release_mapping_tracks_current_units_without_live_install_side_effects():
    for name in ("dispatch_unit", "gateway_acl_dropin"):
        item = MANIFEST["assets"][name]
        assert (PLUGIN / item["source"]).is_file()
        assert item["owner"] == item["group"] == "root"
        assert item["mode"] == "0644"


def load_dispatcher():
    path = PLUGIN / MANIFEST["assets"]["dispatcher"]["source"]
    spec = importlib.util.spec_from_loader("shared_dispatcher", SourceFileLoader("shared_dispatcher", str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registration_fixture(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    base = tmp_path / "dispatch"
    runs = base / "runs"
    processed = base / "processed"
    incoming = base / "incoming"
    for directory in (runs, processed, incoming):
        directory.mkdir(parents=True, exist_ok=True)
    vault = tmp_path / "vault"
    (vault / "30 Projects/LHM Growth").mkdir(parents=True)
    registry = tmp_path / "client-handback-targets.json"
    registry.write_text(json.dumps({"schema_version": 1, "clients": {}}))
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher, "PROCESSED", processed)
    monkeypatch.setattr(dispatcher, "BASE", base)
    monkeypatch.setattr(dispatcher, "VAULT", vault)
    monkeypatch.setattr(dispatcher, "HANDBACK_REGISTRY", registry)
    monkeypatch.setattr(dispatcher, "BACKUP_UID", os.getuid())
    monkeypatch.setattr(dispatcher, "BACKUP_GID", os.getgid())
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    monkeypatch.setattr(dispatcher.os, "fchown", lambda *args: None)
    return dispatcher, incoming, runs, registry


def registration_request(run_id="claude-register-20260823-01", **changes):
    request = {
        "schema_version": 1,
        "run_id": run_id,
        "profile": "handback_target_registration",
        "agent_id": "lhm-connector-repair",
        "target_type": "internal",
        "client": "local-health-marketing",
        "name": "Local Health Marketing",
        "vault_prefix": "30 Projects/LHM Growth/",
        "drive_folder_id": "1abcdefghijklmno",
        "basicops_task_ids": ["2199999"],
        "timeout_seconds": 30,
        "workflow_id": "handback-target-registration",
        "required_skills": ["lhm-connector-repair:handback-target-registration"],
        "required_capabilities": [],
    }
    request.update(changes)
    return request


def test_internal_handback_registration_is_exactly_bounded(tmp_path, monkeypatch):
    dispatcher, incoming, runs, registry = registration_fixture(tmp_path, monkeypatch)
    request = registration_request()
    queued = incoming / "request.json"
    queued.write_text(json.dumps(request))
    dispatcher.complete_registration(queued, request)
    final = json.loads((runs / request["run_id"] / "final.json").read_text())
    assert final["status"] == "completed", json.dumps(final, sort_keys=True)
    target = json.loads(registry.read_text())["clients"]["local-health-marketing"]
    assert target == {
        "type": "internal",
        "name": "Local Health Marketing",
        "vault_prefix": "30 Projects/LHM Growth/",
        "drive_folder_query": "exact folder with folder ID 1abcdefghijklmno",
        "basicops_task_ids": ["2199999"],
    }
    assert final["workflow_contract"]["skill_provenance"] == "declared_only_no_worker"


def test_existing_handback_target_allows_only_additive_task_ids(tmp_path, monkeypatch):
    dispatcher, incoming, runs, registry = registration_fixture(tmp_path, monkeypatch)
    first = registration_request(run_id="claude-register-first", basicops_task_ids=["2199999"])
    queued = incoming / "first.json"; queued.write_text(json.dumps(first)); dispatcher.complete_registration(queued, first)
    second = registration_request(run_id="claude-register-second", basicops_task_ids=["2199999", "2193760"])
    queued = incoming / "second.json"; queued.write_text(json.dumps(second)); dispatcher.complete_registration(queued, second)
    final = json.loads((runs / second["run_id"] / "final.json").read_text())
    assert final["status"] == "completed"
    assert final["verification"]["action"] == "task_ids_extended"
    assert json.loads(registry.read_text())["clients"]["local-health-marketing"]["basicops_task_ids"] == ["2199999", "2193760"]
    removal = registration_request(run_id="claude-register-removal", basicops_task_ids=["2193760"])
    queued = incoming / "removal.json"; queued.write_text(json.dumps(removal)); dispatcher.complete_registration(queued, removal)
    assert json.loads((runs / removal["run_id"] / "final.json").read_text())["status"] == "failed"


def test_registry_backup_fsyncs_base_on_first_creation_and_backup_dir_every_time(tmp_path, monkeypatch):
    dispatcher, _, _, _ = registration_fixture(tmp_path, monkeypatch)
    real_fsync = dispatcher.os.fsync
    directory_syncs = []

    def observe_fsync(fd):
        info = os.fstat(fd)
        if stat.S_ISDIR(info.st_mode):
            directory_syncs.append(info.st_ino)
        real_fsync(fd)

    monkeypatch.setattr(dispatcher.os, "fsync", observe_fsync)
    base_inode = dispatcher.BASE.stat().st_ino
    first = dispatcher.durable_registry_backup()
    backup_dir_inode = first.parent.stat().st_ino
    first_backup_dir_syncs = directory_syncs.count(backup_dir_inode)
    assert first_backup_dir_syncs >= 1
    second = dispatcher.durable_registry_backup()
    assert first != second
    assert directory_syncs.count(base_inode) == 1
    assert directory_syncs.count(backup_dir_inode) == first_backup_dir_syncs + 1


def test_registry_backup_rejects_link_nondirectory_and_wrong_mode(tmp_path, monkeypatch):
    for sequence, setup in enumerate(("symlink", "file", "mode"), 1):
        dispatcher, _, _, _ = registration_fixture(tmp_path / str(sequence), monkeypatch)
        backup_dir = dispatcher.BASE / "registry-backups"
        if setup == "symlink":
            target = dispatcher.BASE / "elsewhere"
            target.mkdir()
            backup_dir.symlink_to(target, target_is_directory=True)
        elif setup == "file":
            backup_dir.write_text("not a directory")
        else:
            backup_dir.mkdir(mode=0o755)
        with pytest.raises(OSError):
            dispatcher.durable_registry_backup()


def test_registration_post_write_failure_restores_bytes_metadata_and_readback(tmp_path, monkeypatch):
    dispatcher, incoming, runs, registry = registration_fixture(tmp_path, monkeypatch)
    original = registry.read_bytes()
    request = registration_request("claude-register-20260823-09")
    queued = incoming / "request.json"
    queued.write_text(json.dumps(request))
    def fail_registry_chown(path, uid, gid):
        if Path(path) == registry:
            raise OSError("injected post-write chown failure")
    monkeypatch.setattr(dispatcher.os, "chown", fail_registry_chown)
    dispatcher.complete_registration(queued, request)
    final = json.loads((runs / request["run_id"] / "final.json").read_text())
    assert final["status"] == "failed"
    assert "backup restored with readback" in final["verification"]["error"]
    assert registry.read_bytes() == original
    assert registry.stat().st_mode & 0o777 == 0o640
    backups = list((dispatcher.BASE / "registry-backups").glob("client-handback-targets.json.backup-*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original
    assert backups[0].stat().st_mode & 0o777 == 0o600


def test_canonical_client_handback_scope_is_strict_and_bounded():
    dispatcher = load_dispatcher()
    client = {
        "name": "Example Health",
        "evidence_prefix": "20 Clients/Example Health/",
        "drive_folder_url": "https://drive.google.com/drive/folders/1abcdefghijklmno",
        "basicops_task_ids": [123, "456"],
    }
    assert dispatcher.canonical_client_handback_target(client) == {
        "type": "client",
        "name": "Example Health",
        "vault_prefix": "20 Clients/Example Health/",
        "drive_folder_query": "exact folder with folder ID 1abcdefghijklmno",
        "basicops_task_ids": ["123", "456"],
    }
    for changes in (
        {"name": "x"},
        {"evidence_prefix": "30 Projects/LHM Growth/"},
        {"drive_folder_url": "https://example.com/folders/1abcdefghijklmno"},
        {"basicops_task_ids": ["1", "1"]},
        {"basicops_task_ids": [str(value) for value in range(21)]},
    ):
        candidate = dict(client)
        candidate.update(changes)
        with pytest.raises(SystemExit):
            dispatcher.canonical_client_handback_target(candidate)


def test_canonical_and_explicit_handback_disagreement_fails_closed(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    incoming = tmp_path / "incoming"
    failed = tmp_path / "failed"
    incoming.mkdir()
    failed.mkdir()
    client_registry = tmp_path / "clients.json"
    handback_registry = tmp_path / "handbacks.json"
    client_registry.write_text(json.dumps({"clients": {"example": {
        "name": "Example Health", "customer_id": "1234567890", "manager_id": "0987654321",
        "evidence_prefix": "20 Clients/Example Health/",
        "evidence_files": ["20 Clients/Example Health/project-management/Google Ads.md"],
        "drive_folder_url": "https://drive.google.com/drive/folders/1abcdefghijklmno",
        "basicops_task_ids": ["123"],
    }}}))
    handback_registry.write_text(json.dumps({"clients": {"example": {
        "type": "client", "name": "Example Health",
        "vault_prefix": "20 Clients/Example Health/",
        "drive_folder_query": "exact folder with folder ID 1differentfolder",
        "basicops_task_ids": ["123"],
    }}}))
    monkeypatch.setattr(dispatcher, "CLIENT_REGISTRY", client_registry)
    monkeypatch.setattr(dispatcher, "HANDBACK_REGISTRY", handback_registry)
    monkeypatch.setattr(dispatcher, "FAILED", failed)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    request = {
        "schema_version": 1, "run_id": "claude-basicops-20260823-01",
        "profile": "basicops_task_discussion_update", "agent_id": "lhm-connector-repair",
        "client": "example", "task_id": "123", "discussion": "A bounded verified discussion message.",
        "timeout_seconds": 600, "workflow_id": "basicops-task-discussion-update",
        "required_skills": ["lhm-project-hub:basicops-task-manager"],
        "required_capabilities": ["basicops.task_read", "basicops.discussion_create", "basicops.discussion_readback"],
    }
    queued = incoming / "request.json"
    queued.write_text(json.dumps(request))
    dispatcher.process(queued)
    assert "canonical client and handback target conflict" in (failed / "request.error").read_text()


def test_internal_handback_registration_rejects_other_slug_or_prefix(tmp_path, monkeypatch):
    for sequence, changes, error in (
        (2, {"client": "another-internal"}, "restricted to local-health-marketing"),
        (3, {"vault_prefix": "30 Projects/LHM Growth/Other/"}, "exact governed LHM Growth prefix"),
    ):
        dispatcher, incoming, runs, _ = registration_fixture(tmp_path / str(sequence), monkeypatch)
        request = registration_request(f"claude-register-20260823-0{sequence}", **changes)
        queued = incoming / "request.json"
        queued.write_text(json.dumps(request))
        dispatcher.complete_registration(queued, request)
        final = json.loads((runs / request["run_id"] / "final.json").read_text())
        assert final["status"] == "failed"
        assert error in final["verification"]["error"]


@pytest.mark.skipif(sys.platform != "linux", reason="Linux POSIX ACL rehearsal requires setfacl")
def test_mask_reset_mid_run_is_repaired_and_terminal_artifacts_persist(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-99"
    ancestor_a = tmp_path / "hermes"
    ancestor_b = ancestor_a / "brain"
    run_dir.mkdir(parents=True)
    ancestor_b.mkdir(parents=True)
    (run_dir / "prompt.json").write_text(json.dumps({"profile": "google_ads_readonly", "agent_id": "lhm-marketing-hub:google-ads"}))
    (run_dir / "events.jsonl").write_text("{}\n")
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher, "WORKER_TRAVERSAL_ANCESTORS", (ancestor_a, ancestor_b))
    monkeypatch.setattr(dispatcher, "ACL_POLL_SECONDS", 0)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    calls = {"ensure": 0}
    real_run = subprocess.run

    def ensure():
        calls["ensure"] += 1
        if calls["ensure"] == 3:
            real_run(["setfacl", "-m", "m::---", str(ancestor_a), str(ancestor_b)], check=True)
        # This workspace filesystem permits mask mutation but not named-user ACLs;
        # the tracked-command assertions above cover the exact claudeworker entry.
        real_run(["setfacl", "-m", "m::--x", str(ancestor_a), str(ancestor_b)], check=True)

    class Worker:
        def __init__(self):
            self.polls = 0
        def poll(self):
            self.polls += 1
            if self.polls < 4:
                return None
            (run_dir / "result.md").write_text("honest result\n")
            (run_dir / "final.json").write_text('{"status":"needs_review"}\n')
            with (run_dir / "events.jsonl").open("a") as handle:
                handle.write('{"event":"completed"}\n')
            return 0
        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(dispatcher, "ensure_worker_traversal", ensure)
    monkeypatch.setattr(dispatcher, "subprocess", types.SimpleNamespace(
        Popen=lambda command: Worker(), CalledProcessError=subprocess.CalledProcessError,
        TimeoutExpired=subprocess.TimeoutExpired))
    assert dispatcher.supervise_worker(run_dir, 300) == 0
    assert calls["ensure"] >= 4
    acl = real_run(["getfacl", "--absolute-names", str(ancestor_a), str(ancestor_b)], check=True, capture_output=True, text=True).stdout
    assert acl.count("mask::--x") == 2
    assert (run_dir / "result.md").read_text() == "honest result\n"
    assert json.loads((run_dir / "final.json").read_text())["status"] == "needs_review"
    assert '"event":"completed"' in (run_dir / "events.jsonl").read_text()


def test_acl_repair_failure_terminates_worker_and_persists_explicit_failure(tmp_path, monkeypatch):
    dispatcher = load_dispatcher()
    runs = tmp_path / "runs"
    run_dir = runs / "claude-gads-20260820-98"
    run_dir.mkdir(parents=True)
    (run_dir / "prompt.json").write_text(json.dumps({"profile": "google_ads_readonly", "agent_id": "lhm-marketing-hub:google-ads"}))
    (run_dir / "events.jsonl").write_text("{}\n")
    monkeypatch.setattr(dispatcher, "RUNS", runs)
    monkeypatch.setattr(dispatcher, "ACL_POLL_SECONDS", 0)
    monkeypatch.setattr(dispatcher.os, "chown", lambda *args: None)
    calls = {"ensure": 0}
    def ensure():
        calls["ensure"] += 1
        if calls["ensure"] > 1:
            raise subprocess.CalledProcessError(1, ["setfacl"])
    class Worker:
        def poll(self): return None
        def terminate(self): pass
        def wait(self, timeout=None): return -15
    monkeypatch.setattr(dispatcher, "ensure_worker_traversal", ensure)
    monkeypatch.setattr(dispatcher, "subprocess", types.SimpleNamespace(
        Popen=lambda command: Worker(), CalledProcessError=subprocess.CalledProcessError,
        TimeoutExpired=subprocess.TimeoutExpired))
    assert dispatcher.supervise_worker(run_dir, 300) == 1
    final = json.loads((run_dir / "final.json").read_text())
    assert final["status"] == "failed"
    assert "failed closed" in final["error"]
