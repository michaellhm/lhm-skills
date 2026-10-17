#!/usr/bin/env python3
"""List the images and videos a client's pages use, with pixel sizes, so the best photos are easy to find.

Usage:
    python3 scan_site_assets.py https://www.example.com.au/ https://www.example.com.au/physiotherapy/ [--min-width 500]

It reads each page's HTML (including lazy-load attributes), skips thumbnail size variants such as -300x200,
downloads each candidate once to measure it, and prints width x height, bytes and URL, largest first.
Needs macOS `sips` for image sizes; videos are listed without dimensions.
"""
import argparse
import os
import re
import subprocess
import tempfile
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
ASSET = re.compile(r'https?://[^"\'\s)>,]+?\.(?:jpe?g|png|webp|avif|mp4|webm)', re.I)
THUMB = re.compile(r'-\d+x\d+\.(?:jpe?g|png|webp|avif)$', re.I)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def size_of(path):
    try:
        out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path],
                             capture_output=True, text=True).stdout
        w = int(re.search(r'pixelWidth: (\d+)', out).group(1))
        h = int(re.search(r'pixelHeight: (\d+)', out).group(1))
        return w, h
    except Exception:
        return 0, 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pages', nargs='+')
    ap.add_argument('--min-width', type=int, default=0)
    a = ap.parse_args()

    urls = set()
    for page in a.pages:
        html = fetch(page).decode('utf-8', 'ignore').replace('\\/', '/')
        urls.update(u for u in ASSET.findall(html) if not THUMB.search(u))

    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for u in sorted(urls):
            if u.lower().endswith(('.mp4', '.webm')):
                rows.append((0, 0, 0, u))
                continue
            try:
                data = fetch(u)
            except Exception:
                continue
            p = os.path.join(tmp, 'img' + os.path.splitext(u)[1])
            with open(p, 'wb') as fh:
                fh.write(data)
            w, h = size_of(p)
            if w >= a.min_width:
                rows.append((w, h, len(data), u))

    for w, h, b, u in sorted(rows, key=lambda r: -r[0]):
        dims = f'{w}x{h}' if w else 'video'
        print(f'{dims:>11}  {b:>9}  {u}')


if __name__ == '__main__':
    main()
