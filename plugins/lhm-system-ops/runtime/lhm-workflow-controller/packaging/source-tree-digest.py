#!/usr/bin/env python3
"""Deterministic digest of the controller release tree, excluding its self-referential manifest."""
from __future__ import annotations

import hashlib
import os
import stat
import sys
from pathlib import Path


def digest(root: Path) -> str:
    root = root.resolve(strict=True)
    records = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative == "release-manifest.json" or any(part in {".git", ".pytest_cache", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        state = path.lstat()
        if stat.S_ISLNK(state.st_mode) or not (stat.S_ISDIR(state.st_mode) or stat.S_ISREG(state.st_mode)):
            raise SystemExit(f"unsupported release member: {relative}")
        if stat.S_ISREG(state.st_mode):
            records.append(f"f {state.st_mode & 0o777:04o} {relative} {hashlib.sha256(path.read_bytes()).hexdigest()}\n")
        else:
            records.append(f"d {state.st_mode & 0o777:04o} {relative}\n")
    return hashlib.sha256("".join(records).encode()).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: source-tree-digest.py ROOT")
    print(digest(Path(sys.argv[1])))
