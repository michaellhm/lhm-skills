#!/usr/bin/env python3
"""Fail a prototype folder that has inline CSS or JavaScript.

Flags, in every .html file under the folder:
  - a <style> tag                       -> inline style block
  - a style="..." attribute             -> inline style attribute
  - a <script> tag with no src          -> inline script
<script type="application/ld+json"> is allowed.

Usage: check_no_inline.py <prototype_dir>
Exit 1 and print "<file>:<line>: <reason>" per finding, else exit 0.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path


class _Scanner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.found = []  # (line, reason)

    def _check(self, tag, attrs):
        line = self.getpos()[0]
        names = {k.lower(): (v or "") for k, v in attrs}
        if tag == "style":
            self.found.append((line, "inline style block"))
        elif tag == "script":
            if "src" not in names and names.get("type", "").strip().lower() != "application/ld+json":
                self.found.append((line, "inline script"))
        if "style" in names:
            self.found.append((line, "inline style attribute"))

    def handle_starttag(self, tag, attrs):
        self._check(tag.lower(), attrs)

    def handle_startendtag(self, tag, attrs):
        self._check(tag.lower(), attrs)


def find_inline(prototype_dir):
    root = Path(prototype_dir)
    findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() != ".html":
            continue
        scanner = _Scanner()
        scanner.feed(path.read_text(encoding="utf-8", errors="replace"))
        scanner.close()
        rel = path.relative_to(root).as_posix()
        findings.extend(f"{rel}:{line}: {reason}" for line, reason in scanner.found)
    return findings


def main(argv):
    if len(argv) != 2:
        print("usage: check_no_inline.py <prototype_dir>", file=sys.stderr)
        return 2
    findings = find_inline(argv[1])
    if findings:
        print("\n".join(findings))
        return 1
    print("No inline CSS or JavaScript found.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
