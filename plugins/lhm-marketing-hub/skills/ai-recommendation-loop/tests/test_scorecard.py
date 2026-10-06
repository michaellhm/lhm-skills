import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('scorecard', Path(__file__).parents[1] / 'scripts/scorecard.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(question='d', repeat=1, status='valid', businesses=None, citations=None, **changes):
    result = dict(engine='test-engine', surface='consumer-ui', model='test-model', panel_version='v1',
                  language='en', location='AU', search_setting='auto', session_conditions='fresh',
                  question_id=question, repeat=repeat, status=status, raw_answer_reference='fixture-only',
                  businesses=businesses or [], citations=citations or [])
    result.update(changes)
    return result


def business(recommended=False, accuracy='unknown', position=None):
    return dict(canonical_name='Example', mentioned=True, recommended=recommended, accuracy=accuracy,
                accuracy_evidence='fixture-only' if accuracy != 'unknown' else None, position=position)


def calculate(rows):
    return module.calculate(dict(client_name='Example', tracked_businesses=['Competitor'], repetitions=3,
        questions=[dict(question_id='d', cohort='discovery', intent='recommendation'),
                   dict(question_id='b', cohort='branded', intent='verification')], observations=rows))['groups']


class ScorecardTests(unittest.TestCase):
    def test_branded_discovery_separation(self):
        groups = calculate([row(), row('b', businesses=[business()])])
        self.assertEqual(groups[0]['metrics']['mention_rate']['percent'], 0)
        self.assertEqual(groups[1]['metrics']['mention_rate']['percent'], 100)
        self.assertEqual(groups[1]['metrics']['recommendation_rate']['percent'], 0)

    def test_failed_run_excluded_and_missing_reported(self):
        metrics = calculate([row(businesses=[business()]), row(repeat=2), row(repeat=3, status='failed')])[0]['metrics']
        self.assertEqual(metrics['mention_rate'], dict(count=1, denominator=2, percent=50))
        self.assertEqual(metrics['coverage']['failed'], 1)
        self.assertEqual(metrics['coverage']['missing'], 0)
        self.assertEqual(metrics['coverage']['incomplete_questions'], ['d'])

    def test_no_valid_runs_unavailable(self):
        metrics = calculate([row(status='failed')])[0]['metrics']
        self.assertIsNone(metrics['mention_rate']['percent'])
        self.assertEqual(metrics['coverage']['missing'], 2)

    def test_citations_distinct_from_recommendations_and_deduplicated(self):
        metrics = calculate([row(citations=[dict(url='https://www.example.com/a', client_owned=True),
                                           dict(url='https://example.com/b', client_owned=True)])])[0]['metrics']
        self.assertEqual(metrics['site_citation_rate']['count'], 1)
        self.assertEqual(metrics['recommendation_rate']['count'], 0)
        self.assertEqual(metrics['cited_domain_frequency'], {'example.com': 1})

    def test_inaccurate_recommendation_and_unordered_position(self):
        metrics = calculate([row(businesses=[business(True, 'inaccurate')])])[0]['metrics']
        self.assertEqual(metrics['recommendation_rate']['count'], 1)
        self.assertEqual(metrics['accurate_recommendation_rate']['count'], 0)
        self.assertEqual(metrics['misdescription_rate']['count'], 1)
        self.assertIsNone(metrics['mean_position'])
        self.assertEqual(metrics['unordered_mentions'], 1)

    def test_model_change_creates_separate_series(self):
        groups = calculate([row(), row(model='other-model')])
        self.assertEqual(len(groups), 4)
        self.assertEqual({g['series']['model'] for g in groups}, {'test-model', 'other-model'})

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            calculate([row(), row()])
        with self.assertRaises(ValueError):
            calculate([row(businesses=[business(), business()])])

    def test_evidence_and_classification_validation(self):
        with self.assertRaises(ValueError):
            calculate([row(raw_answer_reference='')])
        with self.assertRaises(ValueError):
            calculate([row(businesses=[dict(business(), accuracy='accurate', accuracy_evidence=None)])])
        with self.assertRaises(ValueError):
            calculate([row(businesses=[dict(business(), recommended=True, mentioned=False)])])


if __name__ == '__main__':
    unittest.main()
