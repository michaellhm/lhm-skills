import importlib.util
import json
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('validate_report', Path(__file__).parents[1] / 'scripts/validate-report.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class ReportValidation(unittest.TestCase):
    def setUp(self):
        self.card = dict(light='green', status_reason='CPA meets target', stage='30 complete days; medium confidence', highlights=['Bookings rose.'], next_action='Check call overlap.')
    def report(self, body=None, fence='ads_digest'):
        return '## Highlights\n- Bookings rose.\n## Start here\nCheck call overlap.\n## Evidence\nDetails.\n```'+fence+'\n'+json.dumps(self.card if body is None else body)+'\n```\n'
    def test_accepts_all_zones_and_human_agreement(self):
        for zone in v.LIGHTS:
            self.card['light']=zone
            self.assertEqual(v.validate_report(self.report()), self.card)
    def test_rejects_three_observed_production_failures(self):
        for report in [self.report({'ads_digest':self.card},'json'), self.report(dict(self.card, customer_id='123')), self.report(fence='json ads_digest')]:
            with self.assertRaises(ValueError): v.validate_report(report)
    def test_rejects_missing_duplicate_or_unmatched_summary(self):
        for report in ['## Highlights\nNo summary', self.report()+self.report(), self.report().replace('Bookings rose.','Bookings fell.',1), self.report().replace('Check call overlap.','Change budget.',1)]:
            with self.assertRaises(ValueError): v.validate_report(report)
    def test_rejects_excess_highlights_and_invalid_zone(self):
        for card in [dict(self.card, highlights=['Bookings rose.']*5),dict(self.card,light='purple')]:
            with self.assertRaises(ValueError): v.validate_report(self.report(card))
if __name__ == '__main__': unittest.main()
