#!/usr/bin/env python3
"""Check a client brain folder.

Usage: check_brain.py BRAIN_DIR     (exit 1 if there are problems)

Every note must exist, carry the frontmatter keys type/client/updated/sources,
and, unless it is navigation, state or log, either list at least one source or
admit a gap with a `> gap:` line. Overview.md must link to every note.
"""
import re
import sys
from pathlib import Path

NOTES = ["Overview", "Profile", "Project", "Services", "Staff", "What We Do",
         "Who We Serve", "Brand", "Content Rules", "Change Log"]
KEYS = ["type", "client", "updated", "sources"]
EXEMPT = {"Overview", "Project", "Change Log"}


def parse_frontmatter(text: str):
    """Return (fields, body). fields maps key -> raw value (str) or list for a
    block list. Returns (None, text) when there is no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, text
    fields = {}
    current = None
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and not line[0].isspace():
            current = m.group(1)
            fields[current] = m.group(2).strip()
            continue
        item = re.match(r"^\s+-\s+(\S.*)$", line)
        if item and current is not None:
            if not isinstance(fields[current], list):
                fields[current] = []
            fields[current].append(item.group(1).strip())
    return fields, "\n".join(lines[end + 1:])


def has_sources(value) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    value = (value or "").strip()
    if value.startswith("["):
        return bool(value.strip("[]").strip())
    return value not in ("", "null", "~")


def check_brain(brain_dir: Path) -> list[str]:
    brain_dir = Path(brain_dir)
    problems = []
    for name in NOTES:
        fname = f"{name}.md"
        path = brain_dir / fname
        if not path.is_file():
            problems.append(f"{fname}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        fields, body = parse_frontmatter(text)
        fields = fields or {}
        for key in KEYS:
            if key not in fields:
                problems.append(f"{fname}: missing frontmatter key {key}")
        if name == "Overview":
            for other in NOTES:
                link = f"]({other.replace(' ', '%20')}.md)"
                if other != "Overview" and link not in text and f"[[{other}]]" not in text:
                    problems.append(f"{fname}: missing link to {other}.md")
        if name == "Content Rules" and "Anti-AI writing" not in text:
            problems.append(f"{fname}: missing the Anti-AI writing section")
        if name in EXEMPT or "sources" not in fields:
            continue
        has_gap = any(l.lstrip().startswith("> gap:") for l in body.splitlines())
        if not has_sources(fields["sources"]) and not has_gap:
            problems.append(f"{fname}: facts without sources")
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: check_brain.py BRAIN_DIR", file=sys.stderr)
        return 2
    problems = check_brain(Path(argv[1]))
    for p in problems:
        print(p)
    if not problems:
        print("brain ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
