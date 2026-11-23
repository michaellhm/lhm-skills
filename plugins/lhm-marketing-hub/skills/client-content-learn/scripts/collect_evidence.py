#!/usr/bin/env python3
"""Collect bounded, explicit client-content evidence. No AI inference or repo writes."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def safe_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or not p.parts or p.parts[0] == ".git":
        raise ValueError(f"Unsafe source path: {value}")
    if p.suffix.lower() not in {".json", ".md", ".mdx", ".astro", ".html", ".txt", ".yaml", ".yml", ".tsx", ".jsx", ".ts", ".js"}:
        raise ValueError(f"Source must be an explicitly selected text file: {value}")
    return str(p)


def collect(repo, manifest, since, head, emails):
    repo = Path(repo).resolve()
    if git(repo, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("Tracked worktree changes exist; use a clean evidence checkout.")
    head = git(repo, "rev-parse", "--verify", f"{head}^{{commit}}").strip()
    since = git(repo, "rev-parse", "--verify", f"{since}^{{commit}}").strip()
    subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", since, head], check=True)
    pages = manifest.get("pages", [])
    if not pages:
        raise ValueError("Manifest needs approved pages with explicit evidence.")
    corpus, seen, paths = [], set(), set()
    for page in pages:
        route = page["route"]
        if route in seen:
            raise ValueError(f"Duplicate route: {route}")
        seen.add(route)
        if not page.get("approval_evidence") or not page.get("sources"):
            raise ValueError(f"Missing approval evidence or sources: {route}")
        approved = git(repo, "rev-parse", "--verify", f"{page['approved_revision']}^{{commit}}").strip()
        subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", approved, head], check=True)
        sources = []
        for raw in page["sources"]:
            path = safe_path(raw)
            # Reject symlink objects rather than following references to unrelated files.
            mode = git(repo, "ls-tree", head, "--", path).split()[0]
            if mode != "100644" and mode != "100755":
                raise ValueError(f"Not a regular source file: {path}")
            current = git(repo, "show", f"{head}:{path}")
            old = git(repo, "show", f"{approved}:{path}")
            if "\x00" in current or "\x00" in old:
                raise ValueError(f"Binary source rejected: {path}")
            sources.append({"path": path, "sha256": hashlib.sha256(current.encode()).hexdigest(),
                            "matches_approved": current == old, "text": current})
            paths.add(path)
        corpus.append({"route": route, "approved_revision": approved,
                       "approval_evidence": page["approval_evidence"],
                       "eligible": all(s["matches_approved"] for s in sources), "sources": sources})
    candidates = []
    commits = git(repo, "rev-list", "--reverse", f"{since}..{head}").splitlines()
    identities = {e.lower() for e in emails}
    for commit in commits:
        author = git(repo, "show", "-s", "--format=%ae", commit).strip()
        if author.lower() not in identities:
            continue
        patch = git(repo, "show", "--format=", "--no-ext-diff", "--no-renames", "--unified=3", commit, "--", *sorted(paths))
        if patch.strip():
            candidates.append({"commit": commit, "author_email": author,
                               "attribution": "author-match candidate; corroborate client intent",
                               "subject": git(repo, "show", "-s", "--format=%s", commit).strip(),
                               "patch": patch})
    return {"schema_version": 1, "head": head, "comparison_baseline": since,
            "candidate_client_emails": sorted(identities), "pages": corpus,
            "candidate_client_changes": candidates,
            "coverage": {"routes": len(corpus), "eligible": sum(p["eligible"] for p in corpus),
                         "source_paths": sorted(paths), "commits_in_range": len(commits),
                         "candidate_content_commits": len(candidates)},
            "limits": ["Only manifest text paths; media, review discussions and agency-authored client changes need separate inspection.",
                       "Eligibility compares explicitly supplied approved revisions; approval evidence must be verified by the operator."]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--since", required=True)
    p.add_argument("--head", default="HEAD")
    p.add_argument("--client-email", action="append", default=[])
    p.add_argument("--output", required=True)
    a = p.parse_args()
    output = Path(a.output).resolve()
    repo = Path(a.repo).resolve()
    if output.is_relative_to(repo):
        relative = output.relative_to(repo)
        if relative.parts[0] != "docs" or relative.parts[:2] != ("docs", "website-content"):
            raise ValueError("Repo evidence must be under docs/website-content, never a public/static route.")
    result = collect(repo, json.loads(Path(a.manifest).read_text()), a.since, a.head, a.client_email)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), **result["coverage"]}))


if __name__ == "__main__":
    main()
