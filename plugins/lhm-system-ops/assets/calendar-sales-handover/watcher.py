#!/usr/bin/env python3
"""Deterministic calendar-to-chat gate. Adapters own Google and Codex transport.

Calendar adapter: identity(), list_events(start_iso, end_iso), get_event(event_id).
Dispatch adapter: callable(payload) -> {thread_id, chat_url}. An uncertain retry
has reconcile_only=True and MUST only look up the original dispatch_key.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

UTC = timezone.utc
TITLE = re.compile(r"\bon[\s-]?boarding\b", re.I)


class DispatchNotStarted(Exception):
    """Transport proved no chat creation was attempted; safe to retry later."""


def instant(value: str | datetime) -> datetime:
    at = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return at.astimezone(UTC)


def clean(value: Any, limit: int) -> str:
    return "".join(c for c in str(value or "") if c.isprintable())[:limit]


def email(value: Any) -> str:
    value = str(value or "").strip().lower()
    if len(value) > 254 or not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", value):
        return ""
    return value


@dataclass(frozen=True)
class Config:
    calendar_id: str
    calendar_identity: str
    organizer_emails: tuple[str, ...]
    enabled_from: datetime
    delay_seconds: int = 3600
    catchup_days: int = 7

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        calendar_id = str(data.get("calendar_id", "primary"))
        identity = email(data.get("calendar_identity"))
        organizers = tuple(email(x) for x in data.get("organizer_emails", []))
        delay = data.get("delay_seconds", 3600)
        days = data.get("catchup_days", 7)
        if not identity or not organizers or not all(organizers):
            raise ValueError("Verified calendar identity and organizer email allowlist required")
        if not calendar_id or len(calendar_id) > 254:
            raise ValueError("Invalid calendar ID")
        if type(delay) is not int or not 0 <= delay <= 86400:
            raise ValueError("delay_seconds must be an integer from 0 to 86400")
        if type(days) is not int or not 1 <= days <= 7:
            raise ValueError("catchup_days must be an integer from 1 to 7")
        return cls(calendar_id, identity, organizers, instant(data["enabled_from"]), delay, days)


def event_end(event: dict) -> datetime:
    return instant(event["end"]["dateTime"])


def exclusion(event: dict, config: Config) -> str | None:
    if event.get("status") != "confirmed":
        return "not_confirmed"
    if event.get("visibility") == "private":
        return "private"
    if event.get("eventType", "default") != "default":
        return "special_event"
    if not event.get("id") or not event.get("start", {}).get("dateTime") or not event.get("end", {}).get("dateTime"):
        return "untimed_or_missing_id"
    try:
        if event_end(event) <= instant(event["start"]["dateTime"]):
            return "invalid_interval"
    except (KeyError, TypeError, ValueError):
        return "invalid_interval"
    if email(event.get("organizer", {}).get("email")) not in config.organizer_emails:
        return "other_organizer"
    if not TITLE.search(str(event.get("summary", ""))):
        return "other_title"
    self_attendees = [a for a in event.get("attendees", []) if a.get("self") or email(a.get("email")) == config.calendar_identity]
    if not self_attendees:
        return "not_invited"
    if any(a.get("responseStatus") == "declined" for a in self_attendees):
        return "declined"
    if event_end(event) < config.enabled_from:
        return "before_enabled"
    return None


def event_key(event: dict, config: Config) -> str:
    original = event.get("originalStartTime", {})
    original_start = instant(original["dateTime"]).isoformat() if original.get("dateTime") else ""
    identity = [config.calendar_id, event.get("recurringEventId") or event["id"], original_start]
    return hashlib.sha256(json.dumps(identity, separators=(",", ":")).encode()).hexdigest()


def event_payload(event: dict, config: Config, key: str) -> dict:
    url = str(event.get("htmlLink", ""))
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in ("calendar.google.com", "www.google.com")
            or not parsed.path.startswith("/calendar/") or parsed.username or parsed.password or len(url) > 4096):
        url = ""
    attendees = []
    for attendee in event.get("attendees", [])[:100]:
        address = email(attendee.get("email"))
        if address:
            attendees.append({"email": address, "name": clean(attendee.get("displayName"), 120)})
    return {
        "dispatch_key": key,
        "workflow": "lhm-project-hub:sales-handover",
        "calendar_id": config.calendar_id,
        "calendar_identity": config.calendar_identity,
        "event_id": clean(event["id"], 1024),
        "summary": clean(event.get("summary"), 500),
        "start": instant(event["start"]["dateTime"]).isoformat(),
        "end": event_end(event).isoformat(),
        "event_url": url,
        "organizer": email(event.get("organizer", {}).get("email")),
        "attendees": attendees,
        "attendance": "unverified; scheduled end is not attendance evidence",
        "reconcile_only": False,
    }


class Watcher:
    def __init__(self, db_path: str | Path, config: Config, calendar: Any, dispatch: Any):
        self.path = Path(db_path)
        self.config, self.calendar, self.dispatch = config, calendar, dispatch
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS handovers (dispatch_key TEXT PRIMARY KEY, event_id TEXT NOT NULL, state TEXT NOT NULL, payload TEXT NOT NULL, receipt TEXT, error_type TEXT, updated_at TEXT NOT NULL)")
        self.path.chmod(0o600)

    def _db(self):
        return sqlite3.connect(self.path, timeout=10)

    def status(self) -> list[dict]:
        with self._db() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT dispatch_key,event_id,state,receipt,error_type,updated_at FROM handovers ORDER BY updated_at DESC")]

    def _save(self, key: str, event_id: str, state: str, payload: dict, at: datetime, receipt=None, error=None):
        with self._db() as db:
            db.execute("INSERT INTO handovers VALUES (?,?,?,?,?,?,?) ON CONFLICT(dispatch_key) DO UPDATE SET state=excluded.state,payload=excluded.payload,receipt=excluded.receipt,error_type=excluded.error_type,updated_at=excluded.updated_at", (key, event_id, state, json.dumps(payload), json.dumps(receipt) if receipt else None, error, at.isoformat()))

    def run(self, now: datetime | None = None, dry_run: bool = False) -> dict:
        at = instant(now or datetime.now(UTC))
        with self.path.with_suffix(self.path.suffix + ".lock").open("a+") as lock:
            os.fchmod(lock.fileno(), 0o600)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {"state": "already_running", "created": [], "errors": []}
            if email(self.calendar.identity()) != self.config.calendar_identity:
                raise RuntimeError("Calendar identity mismatch")
            since = max(self.config.enabled_from, at - timedelta(days=self.config.catchup_days))
            # Fully materialise before mutation: pagination/read errors cannot look like no matches.
            events = list(self.calendar.list_events(since.isoformat(), at.isoformat()))
            report = {"state": "dry_run" if dry_run else "ok", "created": [], "errors": [], "candidates": [], "skipped": {}}
            for listed in events:
                reason = exclusion(listed, self.config)
                if reason:
                    report["skipped"][reason] = report["skipped"].get(reason, 0) + 1
                    continue
                if event_end(listed) < since:
                    report["skipped"]["outside_catchup"] = report["skipped"].get("outside_catchup", 0) + 1
                    continue
                key = event_key(listed, self.config)
                with self._db() as db:
                    row = db.execute("SELECT state,payload FROM handovers WHERE dispatch_key=?", (key,)).fetchone()
                if row and row[0] == "created":
                    report["skipped"]["already_created"] = report["skipped"].get("already_created", 0) + 1
                    continue
                # Fresh read catches cancellations and moved meeting times before chat creation.
                try:
                    event = self.calendar.get_event(listed["id"])
                    reason = exclusion(event, self.config)
                    if reason:
                        report["skipped"]["fresh_" + reason] = report["skipped"].get("fresh_" + reason, 0) + 1
                        continue
                    if event_key(event, self.config) != key:
                        raise ValueError("Fresh event identity changed")
                    due = event_end(event) + timedelta(seconds=self.config.delay_seconds)
                    if event_end(event) < since:
                        report["skipped"]["fresh_outside_catchup"] = report["skipped"].get("fresh_outside_catchup", 0) + 1
                        continue
                    if due > at:
                        report["skipped"]["not_due"] = report["skipped"].get("not_due", 0) + 1
                        continue
                    payload = event_payload(event, self.config, key)
                    payload["reconcile_only"] = bool(row and row[0] in ("dispatching", "uncertain"))
                    report["candidates"].append({"dispatch_key": key, "event_id": event["id"], "due": due.isoformat(), "reconcile_only": payload["reconcile_only"]})
                    if dry_run:
                        continue
                    self._save(key, event["id"], "dispatching", payload, at)
                    try:
                        result = self.dispatch(payload)
                    except DispatchNotStarted:
                        # A previously uncertain create cannot be cleared by a transport outage.
                        state = "uncertain" if payload["reconcile_only"] else "pending"
                        self._save(key, event["id"], state, payload, at, error="DispatchNotStarted")
                        raise
                    except Exception as exc:
                        self._save(key, event["id"], "uncertain", payload, at, error=type(exc).__name__)
                        raise
                    if not isinstance(result, dict) or not (result.get("thread_id") or result.get("threadId")) or not (result.get("chat_url") or result.get("url")):
                        self._save(key, event["id"], "uncertain", payload, at, error="InvalidDispatchReceipt")
                        raise ValueError("Invalid dispatch receipt")
                    receipt = {"thread_id": str(result.get("thread_id") or result["threadId"]), "chat_url": str(result.get("chat_url") or result["url"])}
                    self._save(key, event["id"], "created", payload, at, receipt=receipt)
                    report["created"].append({"dispatch_key": key, **receipt})
                except Exception as exc:
                    report["errors"].append({"dispatch_key": key, "error_type": type(exc).__name__})
            if report["errors"]:
                report["state"] = "incomplete"
            return report
