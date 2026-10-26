#!/usr/bin/env python3
"""Bounded HTML/asset smoke check for existing static prototypes (not an Astro build)."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class Assets(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'img', 'script', 'source', 'video'} and attrs.get('src'):
            self.urls.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet' and attrs.get('href'):
            self.urls.append(attrs['href'])


def check(root):
    root = Path(root).resolve()
    pages = sorted(root.rglob('*.html'))
    if not pages or not (root / 'index.html').is_file():
        raise ValueError('Static prototype requires index.html and readable HTML pages')
    missing = []
    for page in pages:
        parser = Assets(); parser.feed(page.read_text(encoding='utf-8'))
        for value in parser.urls:
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            target = root / unquote(url.path.lstrip('/')) if url.path.startswith('/') else page.parent / unquote(url.path)
            if not target.resolve().is_relative_to(root) or not target.is_file():
                missing.append({'page': str(page.relative_to(root)), 'asset': value})
    return {'type': 'static-html-smoke', 'pages': len(pages), 'missing_assets': missing, 'passed': not missing}


if __name__ == '__main__':
    result = check(sys.argv[1]); print(json.dumps(result))
    raise SystemExit(0 if result['passed'] else 1)
