"""Crash-safe storage primitives for the LHM workflow controller."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,119}$")
FaultHook = Callable[[str], None]


@dataclass(frozen=True)
class StorageConfig:
    state_root: Path = Path("/var/lib/lhm-workflow")
    executable: Path = Path("/usr/local/libexec/lhm-workflow")
    expected_uid: int = 10004
    expected_gid: int = 10004
    test_mode: bool = False

    @classmethod
    def for_test(cls, root: Path) -> "StorageConfig":
        root = root.resolve()
        return cls(root, root / "lhm-workflow", os.getuid(), os.getgid(), True)

    def validate(self) -> None:
        if not self.state_root.is_absolute() or not self.executable.is_absolute():
            raise ValueError("storage paths must be absolute")
        if not self.test_mode and (self.state_root != Path("/var/lib/lhm-workflow") or self.executable != Path("/usr/local/libexec/lhm-workflow")):
            raise ValueError("production paths are fixed")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


class Storage:
    def __init__(self, config: StorageConfig):
        config.validate()
        self.config = config
        self.parents = config.state_root / "parents"
        self.wal = config.state_root / "wal"
        self.locks = config.state_root / "locks"
        for directory in (config.state_root, self.parents, self.wal, self.locks):
            if config.test_mode:
                directory.mkdir(parents=True, exist_ok=True, mode=0o750)
                os.chmod(directory, 0o750)
                continue
            info = directory.stat()
            if not directory.is_dir() or info.st_uid != config.expected_uid or info.st_gid != config.expected_gid or info.st_mode & 0o027:
                raise PermissionError(f"unsafe production storage directory: {directory}")

    def _id(self, value: str) -> str:
        if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
            raise ValueError("unsafe workflow id")
        return value

    def _path(self, directory: Path, workflow_id: str, suffix: str) -> Path:
        workflow_id = self._id(workflow_id)
        path = (directory / f"{workflow_id}{suffix}").resolve()
        if path.parent != directory.resolve():
            raise ValueError("path escaped storage root")
        return path

    @contextmanager
    def lock(self, workflow_id: str) -> Iterator[None]:
        path = self._path(self.locks, workflow_id, ".lock")
        with path.open("a+b") as handle:
            os.chmod(path, 0o640)
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def atomic_json(self, path: Path, value: object) -> None:
        if path.parent.resolve() not in {self.parents.resolve(), self.config.state_root.resolve()}:
            raise ValueError("atomic target outside writable state")
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(canonical(value)); handle.flush(); os.fsync(handle.fileno())
            os.chmod(temporary, 0o640)
            os.replace(temporary, path)
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try: os.fsync(directory_fd)
            finally: os.close(directory_fd)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)

    def _append_wal(self, workflow_id: str, record: dict) -> None:
        path = self._path(self.wal, workflow_id, ".jsonl")
        with path.open("ab") as handle:
            handle.write(canonical(record)); handle.flush(); os.fsync(handle.fileno())
        os.chmod(path, 0o640)

    def read_parent(self, workflow_id: str) -> dict | None:
        path = self._path(self.parents, workflow_id, ".json")
        return json.loads(path.read_text()) if path.exists() else None

    def transact(self, workflow_id: str, new_parent: dict, *, expected_hash: str | None, tx_id: str, fault: FaultHook | None = None) -> None:
        self._id(tx_id)
        with self.lock(workflow_id):
            current = self.read_parent(workflow_id)
            current_hash = digest(current) if current is not None else None
            if current_hash != expected_hash:
                raise ValueError("parent hash mismatch")
            new_hash = digest(new_parent)
            prepared = {"tx_id": tx_id, "phase": "prepared", "old_hash": current_hash, "new_hash": new_hash, "parent": new_parent}
            self._append_wal(workflow_id, prepared)
            if fault: fault("after_prepared")
            self.atomic_json(self._path(self.parents, workflow_id, ".json"), new_parent)
            if fault: fault("after_parent")
            self._append_wal(workflow_id, {"tx_id": tx_id, "phase": "applied", "new_hash": new_hash})
            if fault: fault("after_applied")
            self._append_wal(workflow_id, {"tx_id": tx_id, "phase": "committed", "new_hash": new_hash})

    def reconcile(self, workflow_id: str) -> None:
        with self.lock(workflow_id):
            path = self._path(self.wal, workflow_id, ".jsonl")
            if not path.exists(): return
            records = [json.loads(line) for line in path.read_text().splitlines() if line]
            phases: dict[str, list[dict]] = {}
            for record in records: phases.setdefault(record["tx_id"], []).append(record)
            for tx_id, entries in phases.items():
                names = {entry["phase"] for entry in entries}
                if "committed" in names: continue
                prepared = next(entry for entry in entries if entry["phase"] == "prepared")
                current = self.read_parent(workflow_id)
                current_hash = digest(current) if current is not None else None
                if current_hash == prepared["old_hash"]:
                    self.atomic_json(self._path(self.parents, workflow_id, ".json"), prepared["parent"])
                    current_hash = prepared["new_hash"]
                if current_hash != prepared["new_hash"]: raise RuntimeError("WAL parent hash conflict")
                if "applied" not in names: self._append_wal(workflow_id, {"tx_id": tx_id, "phase": "applied", "new_hash": current_hash, "reconciled": True})
                self._append_wal(workflow_id, {"tx_id": tx_id, "phase": "committed", "new_hash": current_hash, "reconciled": True})
