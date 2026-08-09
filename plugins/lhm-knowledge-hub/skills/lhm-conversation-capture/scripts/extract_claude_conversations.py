#!/usr/bin/env python3
"""Extract text conversations from local Claude Code JSONL history."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ZONE = ZoneInfo("Australia/Melbourne")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Inclusive local date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="Exclusive local date (YYYY-MM-DD)")
    parser.add_argument("--history-root", default="~/.claude/projects")
    parser.add_argument("--output", help="Write JSON here instead of stdout")
    parser.add_argument("--max-message-chars", type=int, default=12000)
    return parser.parse_args()


def text_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    chunks: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            value = block.get("text")
            if isinstance(value, str):
                chunks.append(value.strip())
    return "\n\n".join(chunk for chunk in chunks if chunk)


def parse_timestamp(raw: Any) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(ZONE)
    except ValueError:
        return None


def is_noise(text: str) -> bool:
    stripped = text.lstrip()
    return (
        not stripped
        or stripped.startswith("<system-reminder>")
        or stripped.startswith("<local-command-")
        or stripped.startswith("<command-name>")
    )


def truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit].rstrip() + "\n[truncated]", True


def extract_file(path: Path, start: datetime, end: datetime, limit: int) -> dict[str, Any] | None:
    messages: list[dict[str, Any]] = []
    session_id = ""
    cwd = ""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("isSidechain") is True:
                continue
            role = record.get("type")
            message = record.get("message")
            if role not in {"user", "assistant"} or not isinstance(message, dict):
                continue
            if message.get("role") != role:
                continue
            stamp = parse_timestamp(record.get("timestamp"))
            if stamp is None or not (start <= stamp < end):
                continue
            content = text_content(message.get("content"))
            if is_noise(content):
                continue
            content, was_truncated = truncate(content, limit)
            session_id = str(record.get("sessionId") or session_id)
            cwd = str(record.get("cwd") or cwd)
            messages.append(
                {
                    "timestamp": stamp.isoformat(),
                    "role": role,
                    "text": content,
                    "truncated": was_truncated,
                    "line": line_number,
                }
            )
    if not messages or not any(item["role"] == "user" for item in messages):
        return None
    return {
        "session_id": session_id or path.stem,
        "source_path": str(path),
        "cwd": cwd,
        "first_timestamp": messages[0]["timestamp"],
        "last_timestamp": messages[-1]["timestamp"],
        "messages": messages,
    }


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

    root = Path(args.history_root).expanduser()
    if not root.is_dir():
        raise SystemExit(f"History root not found: {root}")
    start = datetime.combine(start_date, time.min, ZONE)
    end = datetime.combine(end_date, time.min, ZONE)
    sessions: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.jsonl")):
        if "subagents" in path.parts:
            continue
        session = extract_file(path, start, end, args.max_message_chars)
        if session:
            sessions.append(session)
    sessions.sort(key=lambda item: item["first_timestamp"])

    result = {
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
