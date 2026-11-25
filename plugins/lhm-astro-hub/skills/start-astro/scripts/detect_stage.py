#!/usr/bin/env python3
"""Detect which delivery stage a client repo is at.

repo_facts(repo) reads the repo; next_stage(facts) maps the facts to the next
stage. The sitemap stage is a work-folder artefact tracked by the internal
project file, so it is not detected here.

CLI: detect_stage.py REPO   prints {"facts": {...}, "next_stage": "..."} as JSON.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, SKILLS / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BRAIN_CREATED = re.compile(r"[\u2014-] Brain created\b")
LHM_OWED = {"needs-lhm", "changes-underway"}


def _brain_created(log: Path) -> bool:
    """build-brain writes `## YYYY-MM-DD — Brain created` once the draft is approved."""
    return log.is_file() and any(BRAIN_CREATED.search(l)
                                 for l in log.read_text(encoding="utf-8").splitlines())


def _has_gap(path: Path) -> bool:
    return any(l.lstrip().startswith("> gap:")
               for l in path.read_text(encoding="utf-8").splitlines())


def _register(repo: Path):
    p = repo / ".lhm-review" / "client-review.json"
    if not p.is_file():
        return [], 0, 0
    try:
        reg = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return [], 0, 0
    pages = {pg.get("id"): pg for pg in reg.get("pages", [])}
    rounds, awaiting, owed = [], set(), set()
    for rel in reg.get("releases", []):
        rounds.append(rel.get("id"))
        for pid in rel.get("page_ids", []):
            page = pages.get(pid)
            if not page:
                continue
            if page.get("status") == "awaiting-review":
                awaiting.add(pid)  # waiting on the client
            elif page.get("status") in LHM_OWED:
                owed.add(pid)  # waiting on LHM
    return rounds, len(awaiting), len(owed)


def _client_emails(repo: Path):
    p = repo / ".lhm-review" / "client-config.json"
    if not p.is_file():
        return []
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return []
    emails = (cfg.get("client_identity") or {}).get("commit_emails") or []
    return [e.strip().lower() for e in emails if isinstance(e, str) and e.strip()]


def _git_authors(repo: Path, marker):
    def run(rng):
        return subprocess.run(["git", "-C", str(repo), "log", "--no-merges", "--format=%ae", *rng],
                              capture_output=True, text=True)
    res = run([f"{marker}..HEAD"] if marker else [])
    if res.returncode != 0 and marker:
        res = run([])  # marker not in history: read everything rather than nothing
    if res.returncode != 0:
        return None
    return {l.strip().lower() for l in res.stdout.splitlines() if l.strip()}


def _unprocessed(repo: Path):
    emails = _client_emails(repo)
    if not emails or not (repo / ".git").exists():
        return None
    marker = None
    log = repo / "brain" / "Change Log.md"
    if log.is_file():
        marker = _load("brain_cursor", "update-content-brain/scripts/brain_cursor.py").last_processed(
            log.read_text(encoding="utf-8"))
    authors = _git_authors(repo, marker)
    if authors is None:
        return None
    return bool(authors & set(emails))


def repo_facts(repo: Path) -> dict:
    repo = Path(repo)
    brain = repo / "brain"
    brand = brain / "Brand.md"
    profile = brain / "Profile.md"
    rounds, awaiting, owed = _register(repo)
    brain_built = False
    if (brain / "Overview.md").is_file() and profile.is_file():
        problems = _load("check_brain", "build-brain/scripts/check_brain.py").check_brain(brain)
        # Honest gaps in Profile.md are expected; the approved brain-created entry is the signal.
        brain_built = not problems and _brain_created(brain / "Change Log.md")
    return {
        "brain_scaffolded": (brain / "Overview.md").is_file(),
        "brand_written": brand.is_file() and not _has_gap(brand),
        "site_built": (repo / "site" / "package.json").is_file(),
        "brain_built": brain_built,
        "rounds": rounds,
        "awaiting_review": awaiting,
        "lhm_owed": owed,
        "unprocessed_client_commits": _unprocessed(repo),
    }


def next_stage(facts: dict) -> str:
    if not facts.get("brain_scaffolded"):
        return "repo-setup"
    if not facts.get("brand_written"):
        return "prototype"
    if not facts.get("site_built"):
        return "astro-build"
    if not facts.get("brain_built"):
        return "build-brain"
    if facts.get("unprocessed_client_commits"):
        return "update-content-brain"
    if facts.get("lhm_owed", 0) > 0:
        return "lhm-fixes"
    if facts.get("awaiting_review", 0) > 0:
        return "client-review"
    return "content-round"


def main(argv):
    if len(argv) != 2:
        print("usage: detect_stage.py REPO", file=sys.stderr)
        return 2
    facts = repo_facts(Path(argv[1]))
    print(json.dumps({"facts": facts, "next_stage": next_stage(facts)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
