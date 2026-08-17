#!/usr/bin/env python3
"""
Fails when files that are meant to be byte-identical across skills have drifted.

Some skills ship the same generator so that each skill folder stays self-contained.
A comment in the file saying "change both" is not enforcement, so this is.

Usage:
    python3 scripts/validate-script-parity.py            # check the working tree
    python3 scripts/validate-script-parity.py --staged   # check what is staged (pre-commit)

--staged compares the blobs git would actually commit, which is the case that
matters: fixing both copies but staging only one would otherwise slip through.

To register a new set of files that must stay identical, add a group below.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

PARITY_GROUPS = [
    {
        "name": "sitemap HTML generator",
        "reason": "prospect-sitemap-opportunity and client-sitemap-plan ship the same "
                  "generator; the mode is chosen by the JSON, not by the code.",
        "files": [
            "plugins/lhm-marketing-hub/skills/prospect-sitemap-opportunity/scripts/build_sitemap_html.py",
            "plugins/lhm-marketing-hub/skills/client-sitemap-plan/scripts/build_sitemap_html.py",
        ],
    },
    {
        "name": "sitemap workbook generator",
        "reason": "same workbook builder in both sitemap skills.",
        "files": [
            "plugins/lhm-marketing-hub/skills/prospect-sitemap-opportunity/scripts/build_workbook.py",
            "plugins/lhm-marketing-hub/skills/client-sitemap-plan/scripts/build_workbook.py",
        ],
    },
]


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True)
    return Path(out.stdout.strip())


def read_staged(root: Path, rel: str):
    """Blob content from the index, or None when the path is not staged/tracked."""
    r = subprocess.run(["git", "show", f":{rel}"], cwd=root, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def read_worktree(root: Path, rel: str):
    p = root / rel
    return p.read_bytes() if p.is_file() else None


def main() -> int:
    staged = "--staged" in sys.argv
    root = repo_root()
    read = read_staged if staged else read_worktree
    where = "index" if staged else "working tree"

    failures = []
    for group in PARITY_GROUPS:
        digests = {}
        for rel in group["files"]:
            blob = read(root, rel)
            if blob is None:
                failures.append(
                    f"{group['name']}: {rel} is missing from the {where}.\n"
                    f"    Every file in a parity group must be present and staged together."
                )
                continue
            digests[rel] = hashlib.sha256(blob).hexdigest()

        if len(set(digests.values())) > 1:
            lines = [f"{group['name']}: copies have diverged in the {where}.",
                     f"    {group['reason']}"]
            for rel, d in digests.items():
                lines.append(f"    {d[:12]}  {rel}")
            canonical = group["files"][0]
            others = " ".join(f'"{f}"' for f in group["files"][1:])
            lines.append("    Fix by copying the intended version over the others, e.g.:")
            lines.append(f'      for f in {others}; do cp "{canonical}" "$f"; done')
            if staged:
                lines.append("    Then stage every copy before committing.")
            failures.append("\n".join(lines))

    if failures:
        print("Script parity check failed.\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}\n", file=sys.stderr)
        return 1

    n = sum(len(g["files"]) for g in PARITY_GROUPS)
    print(f"Script parity OK ({n} files in {len(PARITY_GROUPS)} groups, {where}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
