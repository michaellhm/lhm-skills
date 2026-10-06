#!/usr/bin/env python3
"""Calculate auditable rates from captured observations; never collect or infer answers."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

SERIES = ('engine', 'surface', 'model', 'panel_version', 'language', 'location',
          'search_setting', 'session_conditions')


def calculate(data):
    client = data['client_name']
    tracked = set(data['tracked_businesses']) | {client}
    questions = {q['question_id']: q for q in data['questions']}
    if len(questions) != len(data['questions']) or not questions:
        raise ValueError('Question IDs must be unique and the panel must be nonempty')
    for q in questions.values():
        if q['cohort'] not in ('discovery', 'branded'):
            raise ValueError('Question cohort must be discovery or branded')
    repeats = data.get('repetitions', 3)
    if type(repeats) is not int or repeats < 1:
        raise ValueError('Repetitions must be a positive integer')
    groups = defaultdict(list)
    seen = set()
    for obs in data['observations']:
        qid = obs['question_id']
        if qid not in questions:
            raise ValueError('Unknown question ID')
        key = tuple(obs[field] for field in SERIES)
        if any(not isinstance(v, str) or not v for v in key):
            raise ValueError('Series fields must be nonempty strings; use unknown where appropriate')
        repeat = obs['repeat']
        if type(repeat) is not int or not 1 <= repeat <= repeats:
            raise ValueError('Repeat is outside the configured panel')
        identity = (key, qid, repeat)
        if identity in seen:
            raise ValueError('Duplicate question/repeat in one series')
        seen.add(identity)
        if obs['status'] not in ('valid', 'failed', 'missing'):
            raise ValueError('Invalid observation status')
        if obs['status'] == 'valid' and not obs.get('raw_answer_reference'):
            raise ValueError('Valid observations require raw answer evidence')
        groups[key].append(obs)
    output = []
    for key, rows in sorted(groups.items()):
        series = dict(zip(SERIES, key))
        for cohort in ('discovery', 'branded'):
            panel = {qid: q for qid, q in questions.items() if q['cohort'] == cohort}
            if not panel:
                continue
            cohort_rows = [row for row in rows if row['question_id'] in panel]
            output.append({'series': series, 'cohort': cohort,
                           'metrics': summarize(cohort_rows, panel, repeats, client, tracked),
                           'by_intent': {intent: summarize(
                               [row for row in cohort_rows if panel[row['question_id']]['intent'] == intent],
                               {qid: q for qid, q in panel.items() if q['intent'] == intent},
                               repeats, client, tracked)
                               for intent in sorted({q['intent'] for q in panel.values()})}})
    return {'tracked_businesses': sorted(tracked), 'groups': output,
            'comparison': 'Compare only equivalent series and question coverage; no automatic causal attribution.'}


def summarize(rows, panel, repeats, client, tracked):
    valid = [row for row in rows if row['status'] == 'valid']
    n = len(valid)
    counts = Counter()
    coverage = Counter(row['question_id'] for row in valid)
    mentions = Counter()
    domains = Counter()
    positions = []
    for row in valid:
        businesses = {}
        for business in row.get('businesses', []):
            name = business['canonical_name']
            if name in businesses:
                raise ValueError('Business observations must be deduplicated within a run')
            if type(business.get('mentioned')) is not bool or type(business.get('recommended')) is not bool:
                raise ValueError('Mentioned and recommended must be booleans')
            if business['recommended'] and not business['mentioned']:
                raise ValueError('A recommendation must also be a mention')
            if business.get('accuracy') not in ('accurate', 'inaccurate', 'unknown'):
                raise ValueError('Accuracy must be accurate, inaccurate or unknown')
            if business['accuracy'] != 'unknown' and not business.get('accuracy_evidence'):
                raise ValueError('Verified accuracy classifications require evidence')
            position = business.get('position')
            if position is not None and (type(position) is not int or position < 1 or not business['mentioned']):
                raise ValueError('Position must be a positive integer for a mention or null')
            businesses[name] = business
        for name in tracked:
            if businesses.get(name, {}).get('mentioned'):
                mentions[name] += 1
        b = businesses.get(client, {})
        if b.get('mentioned'):
            counts['mentions'] += 1
            if b.get('position') is None:
                counts['unordered_mentions'] += 1
            else:
                positions.append(b['position'])
            if b.get('accuracy') == 'inaccurate':
                counts['misdescriptions'] += 1
        if b.get('recommended'):
            counts['recommendations'] += 1
            if b.get('accuracy') == 'accurate':
                counts['accurate_recommendations'] += 1
            elif b.get('accuracy') == 'unknown':
                counts['unknown_accuracy_recommendations'] += 1
        run_domains = set()
        owned = False
        for citation in row.get('citations', []):
            parsed = urlparse(citation['url'])
            if parsed.scheme not in ('http', 'https') or not parsed.hostname:
                raise ValueError('Citation must be an absolute web URL')
            if type(citation['client_owned']) is not bool:
                raise ValueError('client_owned must be a verified boolean')
            run_domains.add(parsed.hostname.lower().removeprefix('www.'))
            owned |= citation['client_owned']
        domains.update(run_domains)
        counts['site_citations'] += int(owned)
    def rate(field):
        return {'count': counts[field], 'denominator': n,
                'percent': round(100 * counts[field] / n, 2) if n else None}
    expected = len(panel) * repeats
    total_mentions = sum(mentions.values())
    return {'coverage': {'expected': expected, 'valid': n,
                         'failed': sum(row['status'] == 'failed' for row in rows),
                         'missing': expected - n - sum(row['status'] == 'failed' for row in rows),
                         'per_question': {qid: coverage[qid] for qid in sorted(panel)},
                         'incomplete_questions': [qid for qid in sorted(panel) if coverage[qid] < repeats]},
            'mention_rate': rate('mentions'), 'recommendation_rate': rate('recommendations'),
            'accurate_recommendation_rate': rate('accurate_recommendations'),
            'misdescription_rate': rate('misdescriptions'), 'site_citation_rate': rate('site_citations'),
            'unknown_accuracy_recommendations': counts['unknown_accuracy_recommendations'],
            'mean_position': sum(positions) / len(positions) if positions else None,
            'ranked_mentions': len(positions), 'unordered_mentions': counts['unordered_mentions'],
            'competitor_share_of_mentions': {name: {'count': mentions[name], 'denominator': total_mentions,
                'percent': round(100 * mentions[name] / total_mentions, 2) if total_mentions else None}
                for name in sorted(tracked)}, 'cited_domain_frequency': dict(sorted(domains.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text()))
    except (KeyError, ValueError, TypeError) as error:
        parser.error(str(error))
    rendered = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
