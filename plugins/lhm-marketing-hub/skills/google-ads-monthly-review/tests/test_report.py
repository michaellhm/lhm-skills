import importlib.util
import json
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/'scripts/validate-report.py'
s=importlib.util.spec_from_file_location('report_check',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.card={'light':'yellow','status_reason':'Under pacing','stage':'Current versus prior; confidence low','highlights':['Bookings fell; tracking remains unverified.'],'next_action':'Verify the recorded booking definition.'}
    def report(self, card=None, fence='ads_digest'):
        return '## Highlights\n- **Bookings fell; tracking remains unverified.**\n\n## Start here\n1. Verify the recorded booking definition.\n\n## Summary receipt\n```'+fence+'\n'+json.dumps(self.card if card is None else card)+'\n```\n'
    def test_valid_human_summary(self):self.assertEqual(m.validate_report(self.report()),self.card)
    def test_heading_with_json_is_not_labelled_receipt(self):
        with self.assertRaisesRegex(ValueError,'literal'):m.validate_report(self.report(fence='json').replace('Summary receipt','ads_digest'))
    def test_analytics_object_is_not_newsletter(self):
        with self.assertRaisesRegex(ValueError,'five'):m.validate_report(self.report({'zone':'orange','budget':600,'actions':[]}))
    def test_duplicate_and_envelope_rejected(self):
        for tail in [self.report(),'```json\n'+json.dumps({'ads_digest':self.card})+'\n```\n','```json ads_digest\n'+json.dumps(self.card)+'\n```\n']:
            with self.assertRaises(ValueError):m.validate_report(self.report()+tail)
    def test_highlight_and_action_must_match_human_sections(self):
        for key,value in [('highlights',['Unverified new claim.']),('next_action','Increase budget.')]:
            c={**self.card,key:value}
            with self.assertRaises(ValueError):m.validate_report(self.report(c))
    def test_missing_human_section_rejected(self):
        with self.assertRaises(ValueError):m.validate_report(self.report().replace('## Start here','## Actions'))
    def test_invalid_fields_rejected(self):
        for key,value in [('light','amber'),('highlights',[]),('highlights',['x']*5),('stage',False),('status_reason','')]:
            with self.assertRaises(ValueError):m.validate_report(self.report({**self.card,key:value}))
    def test_preserve_zone_and_caveat(self):
        c=m.validate_report(self.report());self.assertEqual(c['light'],'yellow');self.assertIn('unverified',c['highlights'][0]);self.assertIn('low',c['stage'])

if __name__=='__main__':unittest.main()
