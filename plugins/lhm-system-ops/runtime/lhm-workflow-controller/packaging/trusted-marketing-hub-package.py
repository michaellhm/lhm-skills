#!/usr/bin/env python3
"""Build and install the immutable Marketing Hub used by trusted Claude.

The builder reads only Git-indexed bytes.  The installer accepts only the
closed, deterministic archive produced here and never reads Claude's mutable
plugin cache.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
import tempfile

PLUGIN = "lhm-marketing-hub"
VERSION = "2.2.2"
PREFIX = f"{PLUGIN}-{VERSION}"
MAX_FILES = 512
MAX_FILE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 16_000_000
MAX_PATH_BYTES = 240


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE
    ).stdout


def indexed_members(root: Path) -> list[tuple[str, bytes]]:
    base = f"plugins/{PLUGIN}/"
    names = [n for n in _git(root, "ls-files", "-z", "--", base).split(b"\0") if n]
    if not names or len(names) > MAX_FILES:
        raise ValueError("invalid tracked member count")
    members: list[tuple[str, bytes]] = []
    total = 0
    for raw in names:
        source_name = raw.decode("utf-8", "strict")
        rel = source_name.removeprefix(base)
        safe_member(rel)
        mode = _git(root, "ls-files", "-s", "--", source_name).split(None, 1)[0]
        if mode not in {b"100644", b"100755"}:
            raise ValueError(f"non-regular tracked member: {rel}")
        data = _git(root, "show", f":{source_name}")
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(f"member exceeds size limit: {rel}")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ValueError("package exceeds total size limit")
        members.append((rel, data))
    return sorted(members)


def safe_member(name: str) -> PurePosixPath:
    if not name or len(name.encode()) > MAX_PATH_BYTES or "\\" in name:
        raise ValueError("unsafe archive path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("unsafe archive path")
    return path


def reject_linked_components(path: Path) -> None:
    current = path.absolute()
    while current != current.parent:
        if current.is_symlink():
            raise ValueError("package path contains linked component")
        current = current.parent


def verify_installed_tree(target: Path, files: dict[str, bytes], expected_uid: int) -> None:
    expected_directories = {PurePosixPath(".")}
    for rel in files:
        parent = PurePosixPath(rel).parent
        while str(parent) != ".":
            expected_directories.add(parent); parent = parent.parent
    seen_files: set[str] = set(); seen_directories = {PurePosixPath(".")}
    root_state = target.lstat()
    if not stat.S_ISDIR(root_state.st_mode) or root_state.st_uid != expected_uid or stat.S_IMODE(root_state.st_mode) != 0o755:
        raise ValueError("installed root metadata mismatch")
    for directory, dirs, names in os.walk(target, topdown=True, followlinks=False):
        base = Path(directory); relbase = base.relative_to(target)
        for name in dirs:
            item = base / name; state = item.lstat()
            if not stat.S_ISDIR(state.st_mode) or state.st_uid != expected_uid or stat.S_IMODE(state.st_mode) != 0o755:
                raise ValueError("installed directory metadata mismatch")
            seen_directories.add(PurePosixPath((relbase / name).as_posix()))
        for name in names:
            item = base / name; state = item.lstat(); rel = (relbase / name).as_posix()
            if rel == ".": rel = name
            if not stat.S_ISREG(state.st_mode) or state.st_nlink != 1 or state.st_uid != expected_uid or stat.S_IMODE(state.st_mode) != 0o444:
                raise ValueError("installed file metadata mismatch")
            data = item.read_bytes()
            if rel not in files or len(data) != len(files[rel]) or sha(data) != sha(files[rel]):
                raise ValueError("installed member hash mismatch")
            seen_files.add(rel)
    if seen_files != set(files) or seen_directories != expected_directories:
        raise ValueError("installed tree is not closed over manifest")


def build(repo: Path, output: Path) -> str:
    members = indexed_members(repo)
    plugin = json.loads(dict(members)[".claude-plugin/plugin.json"])
    if plugin.get("name") != PLUGIN or plugin.get("version") != VERSION:
        raise ValueError("plugin identity/version mismatch")
    manifest = {
        "schema_version": 1,
        "plugin": PLUGIN,
        "version": VERSION,
        "file_count": len(members),
        "total_bytes": sum(len(data) for _, data in members),
        "members": {name: {"sha256": sha(data), "size": len(data)} for name, data in members},
    }
    manifest_data = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw, tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in [("TRUSTED-MANIFEST.json", manifest_data), *members]:
            info = tarfile.TarInfo(f"{PREFIX}/{name}")
            info.size = len(data); info.mtime = 0; info.uid = 0; info.gid = 0
            info.uname = "root"; info.gname = "root"; info.mode = 0o444
            archive.addfile(info, io.BytesIO(data))
    return sha(output.read_bytes())


def _validate_archive(archive_path: Path, expected_sha256: str) -> tuple[dict, dict[str, bytes]]:
    reject_linked_components(archive_path)
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ValueError("package absent or linked")
    if archive_path.stat().st_size > MAX_TOTAL_BYTES + 2_000_000:
        raise ValueError("archive exceeds size limit")
    if sha(archive_path.read_bytes()) != expected_sha256:
        raise ValueError("package digest mismatch")
    files: dict[str, bytes] = {}
    with tarfile.open(archive_path, "r:") as archive:
        entries = archive.getmembers()
        if len(entries) > MAX_FILES + 1:
            raise ValueError("archive member limit exceeded")
        for entry in entries:
            if not entry.isfile() or entry.issym() or entry.islnk():
                raise ValueError("archive contains non-regular member")
            full = safe_member(entry.name)
            if len(full.parts) < 2 or full.parts[0] != PREFIX:
                raise ValueError("archive prefix mismatch")
            rel = str(PurePosixPath(*full.parts[1:]))
            safe_member(rel)
            if rel in files or entry.size > MAX_FILE_BYTES:
                raise ValueError("duplicate or oversized archive member")
            source = archive.extractfile(entry)
            if source is None:
                raise ValueError("unreadable archive member")
            data = source.read(MAX_FILE_BYTES + 1)
            if len(data) != entry.size:
                raise ValueError("archive member size mismatch")
            files[rel] = data
    manifest = json.loads(files.pop("TRUSTED-MANIFEST.json"))
    if manifest.get("plugin") != PLUGIN or manifest.get("version") != VERSION:
        raise ValueError("manifest identity/version mismatch")
    declared = manifest.get("members")
    if not isinstance(declared, dict) or set(declared) != set(files):
        raise ValueError("archive is not closed over manifest")
    if manifest.get("file_count") != len(files) or manifest.get("total_bytes") != sum(map(len, files.values())):
        raise ValueError("manifest aggregate mismatch")
    for name, data in files.items():
        if declared[name] != {"sha256": sha(data), "size": len(data)}:
            raise ValueError(f"manifest member mismatch: {name}")
    return manifest, files


def install(archive: Path, target_root: Path, expected_sha256: str) -> Path:
    if os.geteuid() != 0 and os.environ.get("LHM_PACKAGE_TEST_MODE") != "1":
        raise PermissionError("root required")
    _, files = _validate_archive(archive, expected_sha256)
    reject_linked_components(target_root)
    if target_root.is_symlink():
        raise ValueError("target root is linked")
    root_existed = target_root.exists()
    target_root.mkdir(parents=True, mode=0o755, exist_ok=True)
    if not root_existed:
        os.chmod(target_root, 0o755)
        if os.geteuid() == 0: os.chown(target_root, 0, 0)
    if target_root.is_symlink():
        raise ValueError("target root is linked")
    expected_uid = 0 if os.geteuid() == 0 else os.geteuid()
    root_state = target_root.stat()
    if root_state.st_uid != expected_uid or root_state.st_mode & 0o022:
        raise ValueError("target root has unsafe ownership or mode")
    target = target_root / PREFIX
    if target.exists() or target.is_symlink():
        raise FileExistsError("trusted plugin target already exists")
    stage = Path(tempfile.mkdtemp(prefix=f".{PREFIX}.", dir=target_root))
    try:
        os.chmod(stage, 0o755)
        for rel, data in files.items():
            destination = stage.joinpath(*PurePosixPath(rel).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() or destination.is_symlink():
                raise ValueError("staging path collision")
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
            with os.fdopen(fd, "wb") as handle:
                handle.write(data); handle.flush(); os.fsync(handle.fileno())
            os.chmod(destination, 0o444)
            if os.geteuid() == 0: os.chown(destination, 0, 0)
        for directory, dirs, _ in os.walk(stage, topdown=False):
            for child in dirs:
                child_path = Path(directory) / child; os.chmod(child_path, 0o755)
                if os.geteuid() == 0: os.chown(child_path, 0, 0)
            os.chmod(directory, 0o755)
            if os.geteuid() == 0: os.chown(directory, 0, 0)
        os.replace(stage, target)
        parent_fd = os.open(target_root, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(parent_fd)
        finally: os.close(parent_fd)
        verify_installed_tree(target, files, expected_uid)
    except BaseException:
        # A failed stage is private and contains no mutable live target.  Leave it
        # for root inspection rather than recursively deleting an untrusted path.
        raise
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build_p = commands.add_parser("build"); build_p.add_argument("repo", type=Path); build_p.add_argument("output", type=Path)
    install_p = commands.add_parser("install"); install_p.add_argument("archive", type=Path); install_p.add_argument("target_root", type=Path); install_p.add_argument("expected_sha256")
    args = parser.parse_args()
    if args.command == "build": print(build(args.repo.resolve(), args.output.absolute()))
    else: print(install(args.archive.absolute(), args.target_root.absolute(), args.expected_sha256))


if __name__ == "__main__":
    main()
