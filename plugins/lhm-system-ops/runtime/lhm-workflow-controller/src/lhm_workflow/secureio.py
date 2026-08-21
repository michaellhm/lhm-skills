from __future__ import annotations

import os
import stat
from pathlib import Path


class UnsafeFile(ValueError):
    pass


def read_trusted(path: Path, *, root: Path, uid: int, max_bytes: int = 2_000_000) -> bytes:
    """Read one regular file without following a final-component symlink.

    The descriptor, rather than the pathname, is validated.  A second fstat
    rejects files mutated while they are being read.
    """
    resolved_root = root.resolve(strict=True)
    try:
        path.parent.resolve(strict=True).relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise UnsafeFile("file outside trusted root") from exc
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise UnsafeFile("unable to open trusted file") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid != uid or before.st_mode & 0o022:
            raise UnsafeFile("unsafe ownership or mode")
        if before.st_size > max_bytes:
            raise UnsafeFile("trusted file exceeds size limit")
        chunks: list[bytes] = []
        remaining = max_bytes + 1
        while remaining:
            chunk = os.read(fd, min(131072, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > max_bytes:
            raise UnsafeFile("trusted file exceeds size limit")
        after = os.fstat(fd)
        identity = lambda value: (value.st_dev, value.st_ino, value.st_uid, value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if identity(before) != identity(after) or len(raw) != after.st_size:
            raise UnsafeFile("file changed during read")
        return raw
    finally:
        os.close(fd)
