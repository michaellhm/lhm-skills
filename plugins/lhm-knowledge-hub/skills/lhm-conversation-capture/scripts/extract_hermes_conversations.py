#!/usr/bin/env python3
"""Extract text conversations from a read-only snapshot of Hermes state.db."""

from __future__ import annotations

import argparse
import base64
import json
import re
import shlex
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ZONE = ZoneInfo("Australia/Melbourne")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Inclusive local date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Exclusive local date (YYYY-MM-DD)")
    parser.add_argument("--db", default="~/.hermes/state.db")
    parser.add_argument("--ssh-host", help="Read Hermes remotely over SSH, for example root@example")
    parser.add_argument("--remote-db", default="/home/hermes/.hermes/state.db")
    parser.add_argument("--output", help="Write JSON here instead of stdout")
    parser.add_argument("--max-message-chars", type=int, default=12000)
    return parser.parse_args()


def text_content(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    stripped = value.strip()
    if not stripped:
        return ""
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped
    if isinstance(parsed, str):
        return parsed.strip()
    if isinstance(parsed, list):
        chunks: list[str] = []
        for block in parsed:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
        return "\n\n".join(chunks)
    if isinstance(parsed, dict):
        text = parsed.get("text") or parsed.get("content")
        return text.strip() if isinstance(text, str) else ""
    return ""


def snapshot_database(source: Path, target_dir: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(f"Hermes database not found: {source}")
    target = target_dir / "state.db"
    shutil.copy2(source, target)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(source) + suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, Path(str(target) + suffix))
    return target


def truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit].rstrip() + "\n[truncated]", True


SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
)


def redact(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result


def extract(db_path: Path, start: datetime, end: datetime, limit: int) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="lhm-hermes-snapshot-") as temp_name:
        snapshot = snapshot_database(db_path, Path(temp_name))
        connection = sqlite3.connect(snapshot)
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(
                """
                SELECT id, source, title, cwd, started_at, ended_at
                FROM sessions
                WHERE started_at >= ? AND started_at < ?
                  AND source != 'subagent'
                ORDER BY started_at, id
                """,
                (start.timestamp(), end.timestamp()),
            ).fetchall()
            for row in rows:
                message_rows = connection.execute(
                    """
                    SELECT role, content, timestamp
                    FROM messages
                    WHERE session_id = ?
                      AND COALESCE(active, 1) = 1
                      AND role IN ('user', 'assistant')
                    ORDER BY timestamp, id
                    """,
                    (row["id"],),
                ).fetchall()
                messages: list[dict[str, Any]] = []
                for message in message_rows:
                    content = text_content(message["content"])
                    if not content:
                        continue
                    content, was_truncated = truncate(redact(content), limit)
                    stamp = datetime.fromtimestamp(float(message["timestamp"]), ZONE)
                    messages.append(
                        {
                            "timestamp": stamp.isoformat(),
                            "role": message["role"],
                            "text": content,
                            "truncated": was_truncated,
                        }
                    )
                if not any(item["role"] == "user" for item in messages):
                    continue
                sessions.append(
                    {
                        "source": "hermes",
                        "session_id": row["id"],
                        "source_path": str(db_path),
                        "channel": row["source"],
                        "title": row["title"] or "",
                        "cwd": row["cwd"] or "",
                        "first_timestamp": messages[0]["timestamp"],
                        "last_timestamp": messages[-1]["timestamp"],
                        "messages": messages,
                    }
                )
        finally:
            connection.close()
    return sessions


REMOTE_QUERY = r'''import json, sqlite3, sys
db, start, end = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
connection = sqlite3.connect("file:" + db + "?mode=ro", uri=True)
connection.row_factory = sqlite3.Row
result = []
for session in connection.execute("SELECT id, source, title, cwd, started_at, ended_at FROM sessions WHERE started_at >= ? AND started_at < ? AND source != 'subagent' ORDER BY started_at, id", (start, end)):
    messages = [dict(row) for row in connection.execute("SELECT role, content, timestamp FROM messages WHERE session_id = ? AND COALESCE(active, 1) = 1 AND role IN ('user', 'assistant') ORDER BY timestamp, id", (session['id'],))]
    result.append({'session': dict(session), 'messages': messages})
connection.close()
print(json.dumps(result, ensure_ascii=False))
'''


def extract_remote(host: str, remote_db: str, start: datetime, end: datetime, limit: int) -> list[dict[str, Any]]:
    encoded = base64.b64encode(REMOTE_QUERY.encode("utf-8")).decode("ascii")
    bootstrap = f"import base64;exec(base64.b64decode('{encoded}'))"
    remote_command = " ".join(
        shlex.quote(value)
        for value in ("python3", "-c", bootstrap, remote_db, str(start.timestamp()), str(end.timestamp()))
    )
    completed = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, remote_command],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"SSH exited {completed.returncode}"
        raise OSError(f"Hermes remote export failed: {detail}")
    try:
        raw_sessions = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise OSError("Hermes remote export returned invalid JSON") from exc

    sessions: list[dict[str, Any]] = []
    for item in raw_sessions:
        row = item["session"]
        messages: list[dict[str, Any]] = []
        for message in item["messages"]:
            content = text_content(message.get("content"))
            if not content:
                continue
            content, was_truncated = truncate(redact(content), limit)
            stamp = datetime.fromtimestamp(float(message["timestamp"]), ZONE)
            messages.append(
                {
                    "timestamp": stamp.isoformat(),
                    "role": message["role"],
                    "text": content,
                    "truncated": was_truncated,
                }
            )
        if not any(message["role"] == "user" for message in messages):
            continue
        sessions.append(
            {
                "source": "hermes",
                "session_id": row["id"],
                "source_path": f"ssh://{host}{remote_db}",
                "channel": row.get("source") or "",
                "title": row.get("title") or "",
                "cwd": row.get("cwd") or "",
                "first_timestamp": messages[0]["timestamp"],
                "last_timestamp": messages[-1]["timestamp"],
                "messages": messages,
            }
        )
    return sessions


def main() -> int:
    args = parse_args()
    try:
        start_date = date.fromisoformat(args.start)
        end_date = date.fromisoformat(args.end)
    except ValueError as exc:
        raise SystemExit(f"Invalid date: {exc}") from exc
    if end_date <= start_date:
        raise SystemExit("--end must be after --start")
    if args.max_message_chars < 500:
        raise SystemExit("--max-message-chars must be at least 500")

    start = datetime.combine(start_date, time.min, ZONE)
    end = datetime.combine(end_date, time.min, ZONE)
    try:
        if args.ssh_host:
            sessions = extract_remote(args.ssh_host, args.remote_db, start, end, args.max_message_chars)
        else:
            sessions = extract(Path(args.db).expanduser(), start, end, args.max_message_chars)
    except (FileNotFoundError, OSError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        raise SystemExit(str(exc)) from exc
    result = {
        "source": "hermes",
        "timezone": str(ZONE),
        "period_start": start.isoformat(),
        "period_end_exclusive": end.isoformat(),
        "session_count": len(sessions),
        "sessions": sessions,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
