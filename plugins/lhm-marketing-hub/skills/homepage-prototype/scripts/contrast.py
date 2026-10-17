#!/usr/bin/env python3
"""Print WCAG contrast ratios for colour pairs.

Usage:
    python3 contrast.py "#FFFFFF" "#3B7D23"            one pair
    python3 contrast.py "#FFFFFF" "#3B7D23" "#161E1D" "#65CA48"   several pairs

Normal text needs 4.5:1 (AA); large text (24px, or about 19px bold) needs 3:1.
"""
import sys


def luminance(hex_colour):
    h = hex_colour.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(a, b):
    hi, lo = sorted([luminance(a), luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main(args):
    if len(args) < 2 or len(args) % 2:
        sys.exit(__doc__)
    for fg, bg in zip(args[0::2], args[1::2]):
        r = ratio(fg, bg)
        verdict = 'AA text' if r >= 4.5 else ('large text only' if r >= 3 else 'FAILS')
        print(f'{fg} on {bg}: {r:.2f}:1  {verdict}')


if __name__ == '__main__':
    main(sys.argv[1:])
