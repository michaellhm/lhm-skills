import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_roles_share_fail_closed_handoff_contract():
    names = ["lhm-chief-of-staff-source-handoff", "lhm-context-research-source-handoff",
             "lhm-cto-source-handoff", "lhm-head-of-production-source-handoff"]
    texts = [(ROOT / "skills" / name / "SKILL.md").read_text() for name in names]
    assert all("source-production-contract.md" in text for text in texts)
    assert all("all_required" in text for text in texts)
    combined = "\n".join(texts)
    for boundary in ("credentials", "BasicOps", "Head of Production", "capability"):
        assert boundary in combined


def test_bounded_route_has_no_hermes_privilege_expansion():
    route = json.loads((ROOT / "references" / "bounded-claude-research-route.json").read_text())
    assert route["accepted_source_kinds"] == ["google_drive_file", "fathom_transcript"]
    assert route["identifier_policy"] == "exact_manifest_allowlist"
    assert set(route["denied_to_hermes"]) == {"credential_files", "raw_tokens", "ssh", "docker",
                                                "unrestricted_filesystem", "arbitrary_drive_ids", "basicops_mutation"}


def test_replay_is_redacted_and_generic():
    text = (ROOT / "tests" / "fixtures" / "campaign-master-playbook-replay.json").read_text()
    assert "redacted" in text
    assert "fixture-drive-id" in text and "fixture-fathom-id" in text
