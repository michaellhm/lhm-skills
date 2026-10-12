#!/usr/bin/env python3
"""Read-only acceptance check for a fresh monthly report before delivery."""
import json
import re
import sys
from pathlib import Path

FIELDS = {'light', 'status_reason', 'stage', 'highlights', 'next_action'}
LIGHTS = {'red', 'orange', 'yellow', 'blue', 'green', 'unknown'}


def normal(value):
    return re.sub(r'\s+', ' ', re.sub(r'[*_`]', '', value)).strip()


def section(report, title):
    match = re.search(r'^#{1,6}\s+' + title + r'\s*\n(.*?)(?=^#{1,6}\s|\Z)',
                      report, re.M | re.S | re.I)
    if not match:
        raise ValueError('Missing human section: ' + title)
    return normal(match.group(1))


def validate_report(report):
    blocks = re.findall(r'^```ads_digest[ \t]*\r?\n(.*?)^```[ \t]*$', report, re.M | re.S)
    # Reject other explicit digest candidates instead of selecting an arbitrary one.
    candidates = re.findall(r'^```(?:json[ \t]+)?ads_digest\b', report, re.M)
    envelopes = re.findall(r'^```json[ \t]*\r?\n(.*?)^```[ \t]*$', report, re.M | re.S)
    for body in envelopes:
        try:
            value = json.loads(body)
        except ValueError:
            if re.search(r'"ads_digest"\s*:', body):
                raise ValueError('Malformed additional digest envelope')
            continue
        if isinstance(value, dict) and 'ads_digest' in value:
            raise ValueError('Use one literal ads_digest fence, not an envelope')
    if len(blocks) != 1 or len(candidates) != 1:
        raise ValueError('Expected exactly one literal ads_digest fence')
    card = json.loads(blocks[0])
    if not isinstance(card, dict) or set(card) != FIELDS:
        raise ValueError('Expected exactly the five newsletter summary fields')
    for name in FIELDS - {'highlights'}:
        if not isinstance(card[name], str) or not card[name].strip():
            raise ValueError('Invalid newsletter field: ' + name)
    if card['light'] not in LIGHTS:
        raise ValueError('Invalid newsletter zone')
    highlights = card['highlights']
    if not isinstance(highlights, list) or not 1 <= len(highlights) <= 4 or any(
            not isinstance(v, str) or not v.strip() for v in highlights):
        raise ValueError('Expected one to four nonempty highlights')
    human_highlights = section(report, 'Highlights')
    human_start = section(report, 'Start here')
    if any(normal(v) not in human_highlights for v in highlights):
        raise ValueError('Newsletter highlight missing from human Highlights')
    if normal(card['next_action']) not in human_start:
        raise ValueError('Newsletter action missing from human Start here')
    return card


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report')
    args = parser.parse_args()
    try:
        validate_report(Path(args.report).read_text())
    except (ValueError, OSError) as exc:
        print(json.dumps({'state': 'correction_required', 'error': str(exc)}))
        return 1
    print(json.dumps({'state': 'report_format_passed', 'sending': False,
                      'limitation': 'Format and human-summary agreement only; evidence and arithmetic require QA.'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
