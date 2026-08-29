from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/lhm-skill-maintainer/SKILL.md"
CONTRACT = ROOT / "skills/lhm-skill-maintainer/references/release-contract.md"


def test_skill_maintainer_preserves_source_and_authority_boundaries():
    text = SKILL.read_text(encoding="utf-8")
    assert "installed Hermes, Claude or Codex copy is runtime evidence" in text
    assert "Direct pushes to protected `main` are forbidden" in text
    assert "require explicit publication/deployment approval" in text
    assert "must never enter Git" in text
    assert "Never declare a hotfix durable while Git and production differ" in text


def test_skill_maintainer_requires_end_to_end_restoration_evidence():
    text = SKILL.read_text(encoding="utf-8")
    assert "verify installed hashes/versions on every named destination" in text
    assert "Run the original regression" in text
    assert "do not close at “merged” or “installed.”" in text


def test_release_contract_uses_bounded_publication_and_deployment():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "michaellhm/lhm-skills" in text
    assert "bounded branch publisher" in text
    assert "approved root-owned installer" in text
    assert "Install atomically with a recoverable backup" in text
    assert "never push protected `main` directly" in text
