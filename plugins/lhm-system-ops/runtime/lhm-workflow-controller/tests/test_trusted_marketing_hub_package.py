import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile

import pytest

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "packaging/trusted-marketing-hub-package.py"
spec = importlib.util.spec_from_file_location("trusted_marketing_package", SOURCE)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def test_build_is_deterministic_and_closed_over_complete_seo_runtime(tmp_path):
    repo = ROOT.parents[3]
    one = tmp_path / "one.tar"; two = tmp_path / "two.tar"
    assert package.build(repo, one) == package.build(repo, two)
    assert one.read_bytes() == two.read_bytes()
    digest = hashlib.sha256(one.read_bytes()).hexdigest()
    manifest, files = package._validate_archive(one, digest)
    required = {
        ".claude-plugin/plugin.json",
        "agents/seo.md",
        "commands/start-seo.md",
        "skills/start-seo/SKILL.md",
        "skills/seo-page-brief/SKILL.md",
        "skills/seo-delivery-qa/SKILL.md",
        "skills/keyword-research/SKILL.md",
        "skills/seo-content-writer/SKILL.md",
        "references/seo-departmental-delivery.md",
        "references/delivery-artifact-contract.md",
        "references/agent-orchestration-contract.md",
    }
    assert required <= set(files)
    assert manifest["file_count"] == len(files) > len(required)
    assert json.loads(files[".claude-plugin/plugin.json"])["version"] == "2.2.2"


def malicious_archive(path, name, data=b"x", *, kind=None):
    with tarfile.open(path, "w") as archive:
        item = tarfile.TarInfo(name); item.size = len(data); item.mtime = 0
        if kind == "symlink": item.type = tarfile.SYMTYPE; item.linkname = "/etc/passwd"; item.size = 0
        archive.addfile(item, None if kind else io.BytesIO(data))


@pytest.mark.parametrize("name,kind", [
    (f"{package.PREFIX}/../escape", None),
    (f"{package.PREFIX}/link", "symlink"),
    ("wrong-prefix/file", None),
])
def test_rejects_traversal_links_and_wrong_prefix(tmp_path, name, kind):
    archive = tmp_path / "bad.tar"; malicious_archive(archive, name, kind=kind)
    with pytest.raises(ValueError):
        package._validate_archive(archive, hashlib.sha256(archive.read_bytes()).hexdigest())


def test_install_is_immutable_and_refuses_existing_target(tmp_path, monkeypatch):
    repo = ROOT.parents[3]; archive = tmp_path / "release.tar"
    digest = package.build(repo, archive); target_root = tmp_path / "plugins"
    monkeypatch.setenv("LHM_PACKAGE_TEST_MODE", "1")
    target = package.install(archive, target_root, digest)
    assert target.name == package.PREFIX
    assert not target.is_symlink()
    assert all(not item.is_symlink() for item in target.rglob("*"))
    assert all((item.stat().st_mode & 0o222) == 0 for item in target.rglob("*") if item.is_file())
    with pytest.raises(FileExistsError): package.install(archive, target_root, digest)


def test_hostile_umask_cannot_weaken_tree_and_postrename_tamper_is_detected(tmp_path, monkeypatch):
    repo = ROOT.parents[3]; archive = tmp_path / "release.tar"; digest = package.build(repo, archive)
    monkeypatch.setenv("LHM_PACKAGE_TEST_MODE", "1")
    previous = os.umask(0)
    try:
        target = package.install(archive, tmp_path / "safe", digest)
    finally:
        os.umask(previous)
    assert (target.stat().st_mode & 0o777) == 0o755
    assert all((p.stat().st_mode & 0o777) == 0o755 for p in target.rglob("*") if p.is_dir())
    assert all((p.stat().st_mode & 0o777) == 0o444 for p in target.rglob("*") if p.is_file())
    target_root = tmp_path / "tampered"; real_replace = package.os.replace
    def replace_then_tamper(source, destination):
        real_replace(source, destination)
        victim = Path(destination) / "skills/start-seo/SKILL.md"; victim.chmod(0o644); victim.write_text("tampered"); victim.chmod(0o444)
    monkeypatch.setattr(package.os, "replace", replace_then_tamper)
    with pytest.raises(ValueError, match="installed file metadata|installed member hash"):
        package.install(archive, target_root, digest)


def test_install_rejects_linked_archive_and_target_root(tmp_path, monkeypatch):
    repo = ROOT.parents[3]; archive = tmp_path / "release.tar"
    digest = package.build(repo, archive); monkeypatch.setenv("LHM_PACKAGE_TEST_MODE", "1")
    archive_link = tmp_path / "archive-link.tar"; archive_link.symlink_to(archive)
    with pytest.raises(ValueError, match="linked"):
        package.install(archive_link, tmp_path / "plugins-one", digest)
    real = tmp_path / "real"; real.mkdir(); root_link = tmp_path / "plugins-link"; root_link.symlink_to(real)
    with pytest.raises(ValueError, match="linked"):
        package.install(archive, root_link, digest)


def test_provisioner_never_reads_mutable_claude_cache():
    script = (ROOT / "packaging/provision-trusted-claude.sh").read_text()
    supervisor = (ROOT / "integration/lhm_claude_trusted_supervisor.py").read_text()
    assert "/.claude/plugins/cache/" not in script
    assert "lhm-marketing-hub-2.2.2.tar" in script
    assert "61b46faa9105e45c517bdd6d1de78ebee458887896ac7b31eb92c46b959df7ac" in script
    assert "lhm-marketing-hub-2.2.2" in supervisor
