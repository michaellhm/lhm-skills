from __future__ import annotations

import importlib.machinery
import importlib.util
import os
from pathlib import Path

import pytest


def candidate():
    loader = importlib.machinery.SourceFileLoader("site_change_launcher_candidate", "/tmp/lhm-site-change-launcher.candidate")
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec); loader.exec_module(module)
    return module


def envelope():
    return {
        "child_run_id": "child-astro-1",
        "required_skills": ["lhm-wordpress-hub:start-astro", "lhm-wordpress-hub:astro-build"],
        "expected_mutation_state": "feature_branch",
    }


def test_missing_required_skill_asset_fails_before_any_skill_attestation(tmp_path, monkeypatch):
    launcher = candidate(); calls = []
    run = tmp_path / "child-astro-1"; run.mkdir(); (run / "prompt.txt").write_text("base prompt")
    skills = tmp_path / "skills"; skills.mkdir()
    monkeypatch.setattr(launcher, "GOVERNED_SKILL_ROOT", skills)
    monkeypatch.setattr(launcher, "TRUSTED_ROOT_UID", os.getuid())
    monkeypatch.setattr(launcher, "hook", lambda *args: calls.append(args))
    with pytest.raises(FileNotFoundError):
        launcher.supply_governed_skills(run, envelope())
    assert calls == []
    assert (run / "prompt.txt").read_text() == "base prompt"


def test_exact_skill_assets_are_supplied_but_not_attested_until_success(tmp_path, monkeypatch):
    launcher = candidate(); calls = []
    run = tmp_path / "child-astro-1"; run.mkdir(); (run / "prompt.txt").write_text("base prompt")
    skills = tmp_path / "skills"
    for name in ("start-astro", "astro-build"):
        root = skills / name; root.mkdir(parents=True); (root / "SKILL.md").write_text(f"instructions for {name}")
        (root / "SKILL.md").chmod(0o600)
    monkeypatch.setattr(launcher, "GOVERNED_SKILL_ROOT", skills)
    monkeypatch.setattr(launcher, "TRUSTED_ROOT_UID", os.getuid())
    monkeypatch.setattr(launcher.os, "chown", lambda *args: None)
    monkeypatch.setattr(launcher, "hook", lambda *args: calls.append(args))
    digest=launcher.supply_governed_skills(run, envelope())
    prompt = (run / "prompt.txt").read_text()
    assert "instructions for start-astro" in prompt and "instructions for astro-build" in prompt
    assert calls == []
    launcher.observe_successful_skill_execution(run,envelope(),digest,worker_ok=True)
    assert calls == [
        ("skill", "child-astro-1", "lhm-wordpress-hub:start-astro"),
        ("skill", "child-astro-1", "lhm-wordpress-hub:astro-build"),
    ]


def test_missing_branch_or_preview_readback_never_attests(tmp_path, monkeypatch):
    launcher = candidate(); calls = []
    monkeypatch.setattr(launcher, "hook", lambda *args: calls.append(args))
    with pytest.raises(ValueError, match="remote readback mismatch"):
        launcher.observe_branch_readback("child-astro-1", "wrong", "expected")
    with pytest.raises(ValueError, match="preview readback is incomplete"):
        launcher.observe_preview_readback("child-astro-1", {"status": "ready", "url": "https://preview", "noindex_verified": False}, {"project_name":"p","environment":"preview","aliases":["https://preview"],"source":{"branch":"b","commit_hash":"c"}}, project="p",branch="b",commit="c")
    assert calls == []


def test_positive_readbacks_emit_only_host_capabilities(monkeypatch):
    launcher = candidate(); calls = []
    monkeypatch.setattr(launcher, "hook", lambda *args: calls.append(args))
    launcher.observe_branch_readback("child-astro-1", "abc", "abc")
    launcher.observe_preview_readback("child-astro-1", {"status": "ready", "url": "https://preview", "noindex_verified": True}, {"project_name":"p","environment":"preview","aliases":["https://preview"],"source":{"branch":"b","commit_hash":"c"}}, project="p",branch="b",commit="c")
    assert calls == [
        ("capability", "child-astro-1", "git.feature_branch_write"),
        ("capability", "child-astro-1", "cloudflare.preview_readback"),
    ]


def test_terminal_normalization_requires_both_readbacks(tmp_path, monkeypatch):
    launcher = candidate(); calls = []
    monkeypatch.setattr(launcher, "hook", lambda *args: calls.append(args))
    with pytest.raises(ValueError, match="lacks branch or preview readback"):
        launcher.complete_governed(tmp_path, envelope(), [], ["check"], tmp_path / "patch", "branch", "commit", {"status": "unavailable", "noindex_verified": False})
    assert calls == []

def test_failed_worker_or_mutated_prompt_never_attests_skills(tmp_path,monkeypatch):
    launcher=candidate(); calls=[]; run=tmp_path/"child-astro-1"; run.mkdir(); (run/"prompt.txt").write_text("immutable")
    monkeypatch.setattr(launcher,"hook",lambda *args:calls.append(args))
    digest=__import__('hashlib').sha256((run/"prompt.txt").read_bytes()).hexdigest()
    with pytest.raises(ValueError): launcher.observe_successful_skill_execution(run,envelope(),digest,worker_ok=False)
    (run/"prompt.txt").write_text("changed")
    with pytest.raises(ValueError): launcher.observe_successful_skill_execution(run,envelope(),digest,worker_ok=True)
    assert calls==[]

def test_cloudflare_metadata_must_bind_project_branch_commit_and_alias(monkeypatch):
    launcher=candidate(); calls=[]; monkeypatch.setattr(launcher,"hook",lambda *a:calls.append(a))
    preview={"status":"ready","url":"https://alias.pages.dev","noindex_verified":True}
    bad={"project_name":"p","environment":"preview","aliases":[preview["url"]],"source":{"branch":"b","commit_hash":"wrong"}}
    with pytest.raises(ValueError,match="metadata binding mismatch"):
        launcher.observe_preview_readback("c",preview,bad,project="p",branch="b",commit="sha")
    assert calls==[]

def test_git_execution_uses_fixed_binary_and_sanitized_environment(monkeypatch):
    launcher=candidate(); captured={}
    class Done: stdout=""
    def run(command,**kwargs): captured.update(command=command,kwargs=kwargs); return Done()
    monkeypatch.setattr(launcher.subprocess,"run",run)
    launcher.run_as_worker(["git","status"])
    assert captured["command"][:5] == ["/usr/sbin/runuser","-u","codexworker","--","/usr/bin/git"]
    env=captured["kwargs"]["env"]
    assert env["PATH"] == "/usr/bin:/bin" and env["GIT_CONFIG_GLOBAL"] == "/dev/null"
    assert "IdentitiesOnly=yes" in env["GIT_SSH_COMMAND"] and len(env) == 7
