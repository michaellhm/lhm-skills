#!/usr/bin/env python3
"""
Read the brief fields for one page out of sitemap.json, or check that every new or
enhanced page has them.

Usage:
    python3 page_brief_seed.py sitemap.json "<page name>"   print the seed as JSON
    python3 page_brief_seed.py sitemap.json --check         list missing fields, exit 1 if any

A page needs primary_keyword, audience and intent when its status is "new" or "enh".
A page with no status is treated as "new", which matches build_sitemap_html.py.
"""
import json
import sys

REQUIRED = ("primary_keyword", "audience", "intent")
NEEDS_BRIEF = ("new", "enh")


def _pages(spec):
    """Yield (section title, page) for every page in every section and card."""
    for section in spec.get("sections", []):
        for card in section.get("cards", []):
            for page in card.get("items", []):
                yield section.get("title", ""), page


def missing_brief_fields(spec):
    missing = []
    for _title, page in _pages(spec):
        if page.get("status", "new") not in NEEDS_BRIEF:
            continue
        for field in REQUIRED:
            if not page.get(field):
                missing.append(f"{page.get('name', '?')}: {field}")
    return missing


def seed(spec, page_name):
    for title, page in _pages(spec):
        if page.get("name") == page_name:
            return {
                "page": page["name"],
                "slug": page.get("slug"),
                "primary_keyword": page.get("primary_keyword"),
                "secondary_keywords": list(page.get("secondary_keywords") or []),
                "audience": page.get("audience"),
                "intent": page.get("intent"),
                "h1": page.get("h1"),
                "template": page.get("template"),
                "section": title,
            }
    raise KeyError(f"Page not found in sitemap: {page_name}")


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        spec = json.load(f)
    if argv[2] == "--check":
        missing = missing_brief_fields(spec)
        if missing:
            print("Missing brief fields:")
            for line in missing:
                print(f"  {line}")
            return 1
        print("All new and enhanced pages have keyword, audience and intent.")
        return 0
    try:
        print(json.dumps(seed(spec, argv[2]), indent=2, ensure_ascii=False))
    except KeyError as e:
        print(e.args[0], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
