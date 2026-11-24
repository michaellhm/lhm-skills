#!/usr/bin/env python3
"""Initialise a local interview bundle or export only its explicitly indexed pages."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
import zipfile

SKILL = Path(__file__).resolve().parents[1]


def initialise(root, pages_file):
    if root.exists():
        raise ValueError('Output folder already exists. Resume it; do not initialise again.')
    pages = json.loads(pages_file.read_text(encoding='utf-8'))
    if not isinstance(pages, list) or not pages:
        raise ValueError('Page list must be a non-empty JSON array.')
    seen = set()
    for page in pages:
        slug, title = page.get('slug', ''), page.get('title', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('Page slugs must be unique lowercase names without paths.')
        if not isinstance(title, str) or not title.strip() or any(c in title for c in '\n\r|[]'):
            raise ValueError('Each page needs a single-line title without table/link delimiters.')
        seen.add(slug)
    template = (SKILL / 'assets/page-template.md').read_text(encoding='utf-8')
    root.mkdir(parents=True)
    (root / 'pages').mkdir()
    index = ['# Support page interviews', '',
             'Proposed page list. Confirm scope with the clinician; these entries do not confirm services offered.', '',
             '| Page | Status |', '| --- | --- |']
    for page in pages:
        filename = f"{page['slug']}.md"
        (root / 'pages' / filename).write_text(template.replace('{{title}}', page['title']), encoding='utf-8')
        index.append(f"| [{page['title']}](pages/{filename}) | Not started |")
    index += ['', '## Deliberately skipped or excluded pages', '',
              'None recorded.', '', '## Next session', '', 'Start with Children, or choose another page.', '']
    (root / '00-index.md').write_text('\n'.join(index), encoding='utf-8')
    return root / '00-index.md'


def export_bundle(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Choose a real bundle directory, not a symlink.')
    index = root / '00-index.md'
    if index.is_symlink() or not index.is_file():
        raise ValueError('A real 00-index.md file is required.')
    links = re.findall(r'\]\(([^)]+)\)', index.read_text(encoding='utf-8'))
    files = [index]
    for link in links:
        if not re.fullmatch(r'pages/[a-z0-9]+(?:-[a-z0-9]+)*\.md', link):
            raise ValueError(f'Index contains an unsupported path: {link}')
        page = root / link
        if page.is_symlink() or (root / 'pages').is_symlink() or not page.is_file():
            raise ValueError(f'Indexed page is missing or a symlink: {link}')
        if page.resolve().parent != root.resolve() / 'pages':
            raise ValueError('Indexed page is outside the bundle.')
        if page not in files:
            files.append(page)
    if len(files) == 1:
        raise ValueError('Index must link at least one page.')
    output = root.parent / f"support-page-handback-{datetime.now():%Y%m%d-%H%M%S-%f}.zip"
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED) as archive:
        for page in files:
            archive.write(page, str(Path('support-page-interview') / page.relative_to(root)))
    with zipfile.ZipFile(output) as archive:
        expected = {str(Path('support-page-interview') / p.relative_to(root)): p.read_bytes() for p in files}
        if set(archive.namelist()) != set(expected) or any(archive.read(n) != b for n, b in expected.items()):
            raise ValueError('Export verification failed; do not send the ZIP.')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'export'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--pages', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'init' and args.pages is None:
            parser.error('init requires --pages')
        result = initialise(args.root, args.pages) if args.command == 'init' else export_bundle(args.root)
        print(result)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f'Not completed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
