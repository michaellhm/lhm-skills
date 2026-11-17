#!/usr/bin/env python3
"""Trace a small raster logo into a crisp two-tone SVG.

Clients often only have a tiny PNG logo (Better Backs had 200x93), which looks
soft and squashed on retina screens. This upscales the PNG, splits it into one
mask per brand colour, traces each mask with potrace and writes:

  logo.svg        brand colours, for light headers
  logo-white.svg  white + light accent, for dark footers

Usage:
  python3 trace_logo.py logo.png OUT_DIR --colour "#2E3590" --colour "#2BA8E0"
  (pass the main colour first; optional --white-accent "#7FD0F2")

Requires: potrace (brew install potrace), numpy, and macOS `sips` for resizing.
Always look at the result zoomed in. Thin light-coloured strokes may need a
lower --tolerance or a higher --min-coverage. Treat the output as an interim
prototype logo and ask the client for their original vector files.
"""
import argparse, os, re, struct, subprocess, sys, tempfile
import numpy as np


def hex_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def read_bmp(path):
    b = open(path, 'rb').read()
    off = struct.unpack('<I', b[10:14])[0]
    w, h = struct.unpack('<ii', b[18:26])
    bpp = struct.unpack('<H', b[28:30])[0]
    row = ((w * bpp // 8) + 3) // 4 * 4
    a = np.frombuffer(b[off:off + row * abs(h)], np.uint8).reshape(abs(h), row)
    a = a[:, :w * bpp // 8].reshape(abs(h), w, bpp // 8)
    if h > 0:
        a = a[::-1]
    B, G, R = (a[..., i].astype(float) for i in range(3))
    A = a[..., 3].astype(float) if bpp == 32 else np.full(B.shape, 255.0)
    f = A / 255
    rgb = np.stack([R * f + 255 * (1 - f), G * f + 255 * (1 - f), B * f + 255 * (1 - f)], -1)
    return rgb


def smooth(mask, k=2, need=11):
    p = np.pad(mask, k)
    acc = sum(p[k + dy:k + dy + mask.shape[0], k + dx:k + dx + mask.shape[1]].astype(int)
              for dy in range(-k, k + 1) for dx in range(-k, k + 1))
    return acc >= need


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('png')
    ap.add_argument('out_dir')
    ap.add_argument('--colour', action='append', required=True, help='brand colour, main colour first')
    ap.add_argument('--white-accent', default='#7FD0F2')
    ap.add_argument('--scale', type=int, default=8)
    ap.add_argument('--tolerance', type=float, default=40, help='max RGB distance from the brand-colour-to-white line')
    ap.add_argument('--min-ink', type=float, default=0.25, help='how far from white (0-1) a pixel must be to count')
    ap.add_argument('--min-coverage', type=int, default=11, help='of 25 neighbours, to keep a pixel')
    a = ap.parse_args()

    tmp = tempfile.mkdtemp()
    w0, h0 = (int(x) for x in re.findall(r'pixel(?:Width|Height): (\d+)',
              subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', a.png],
                             capture_output=True, text=True).stdout))
    big, bmp = os.path.join(tmp, 'big.png'), os.path.join(tmp, 'big.bmp')
    subprocess.run(['sips', '-z', str(h0 * a.scale), str(w0 * a.scale), a.png, '--out', big], check=True, capture_output=True)
    subprocess.run(['sips', '-s', 'format', 'bmp', big, '--out', bmp], check=True, capture_output=True)
    rgb = read_bmp(bmp)
    H, W, _ = rgb.shape

    # Anti-aliased edges sit on the line between a brand colour and the white
    # background, so measure each pixel's distance to that line (not to the
    # colour itself). This stops navy edges being read as the light accent.
    p = rgb - 255.0
    dists, inks = [], []
    for c in a.colour:
        v = hex_rgb(c) - 255.0
        t = np.clip((p @ v) / (v @ v), 0, 1)
        dists.append(np.linalg.norm(p - t[..., None] * v, axis=-1))
        inks.append(t)
    dist, ink_amt = np.stack(dists, -1), np.stack(inks, -1)
    nearest = dist.argmin(-1)
    groups = []
    for i, c in enumerate(a.colour):
        m = (nearest == i) & (dist[..., i] < a.tolerance) & (ink_amt[..., i] > a.min_ink)
        m = smooth(m, need=a.min_coverage)
        pbm, svg = os.path.join(tmp, f'l{i}.pbm'), os.path.join(tmp, f'l{i}.svg')
        with open(pbm, 'wb') as o:
            o.write(b'P4\n%d %d\n' % (W, H))
            o.write(np.packbits(m, axis=1).tobytes())
        subprocess.run(['potrace', '-s', '--flat', '-t', '30', '-a', '1.2', '-O', '0.5', pbm, '-o', svg], check=True)
        g = re.search(r'(<g transform="[^"]*")\s*fill="#000000" stroke="none">(.*?)</g>', open(svg).read(), re.S)
        groups.append((c, g.group(1), g.group(2).strip()))
        print(f'{c}: {int(m.sum())} px traced')

    def build(fills):
        body = '\n'.join(f'{t} fill="{f}">{p}</g>' for (c, t, p), f in zip(groups, fills))
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Logo">\n{body}\n</svg>\n'

    os.makedirs(a.out_dir, exist_ok=True)
    open(os.path.join(a.out_dir, 'logo.svg'), 'w').write(build(a.colour))
    white = ['#FFFFFF'] + [a.white_accent] * (len(a.colour) - 1)
    open(os.path.join(a.out_dir, 'logo-white.svg'), 'w').write(build(white))
    print('wrote logo.svg and logo-white.svg to', a.out_dir)


if __name__ == '__main__':
    sys.exit(main())
