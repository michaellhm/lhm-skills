#!/usr/bin/env python3
"""Scaffold a client repo: README, agent files, brain/ notes, site/ and skills/.

Refuses (FileExistsError, nothing written) if any target file already exists,
so it can never overwrite client content.
"""
import argparse
import datetime
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def _templates():
    return sorted(p for p in ASSETS.rglob("*") if p.is_file())


def scaffold(root, client_name, client_slug):
    root = Path(root)
    today = datetime.date.today().isoformat()
    plan = []
    for src in _templates():
        rel = src.relative_to(ASSETS).as_posix()
        plan.append((rel, src))
    existing = [rel for rel, _ in plan if (root / rel).exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing files: " + ", ".join(existing))
    written = []
    for rel, src in plan:
        text = src.read_text(encoding="utf-8")
        text = (text.replace("{{client_name}}", client_name)
                    .replace("{{client_slug}}", client_slug)
                    .replace("{{date}}", today))
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append(rel)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--client-name", required=True)
    ap.add_argument("--client-slug", required=True)
    args = ap.parse_args(argv)
    try:
        written = scaffold(Path(args.root), args.client_name, args.client_slug)
    except FileExistsError as exc:
        print(exc, file=sys.stderr)
        return 1
    print("\n".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
