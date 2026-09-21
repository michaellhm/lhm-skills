import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parents[1]/'scripts'))
import brief
import weekly_runtime as runtime
from test_quality import QualityTest

class BlockerTest(QualityTest):
    def disclose(self):
        b={'id':'example-record','project':'Example','issue':'Record <missing> & unverified','impact':'Approval date unknown','owner':'Michael','next_step':'Confirm the canonical record'}
        self.change('brief.json',lambda d:d.update(blockers=[b]))
        self.change('research-receipt.json',lambda d:d.update(project_gaps=[{'id':b['id'],'scope':'project','project':'Example','source':'obsidian','evidence':['source.txt']}]))
        self.change('research-receipt.json',lambda d:d['project_source_coverage'][0]['obsidian'].update(status='limited',gap_id=b['id']))
        label=brief.blocker_text(b)
        self.write('email.json',{'html':'Blockers and information needed '+brief.html.escape(label),'text':'Blockers and information needed '+label})
        self.review()
        return b
    def test_disclosed_gap_passes_without_false_complete(self):
        self.disclose();self.assertEqual(__import__('quality').validate(self.p)['state'],'quality_passed')
    def test_undisclosed_gap_fails(self):
        self.disclose();self.change('brief.json',lambda d:d.update(blockers=[]))
        with self.assertRaisesRegex(ValueError,'visible blocker'):__import__('quality').validate(self.p)
    def test_disclosure_must_be_in_both_email_parts(self):
        self.disclose();self.change('email.json',lambda d:d.update(text='Missing disclosure'))
        with self.assertRaisesRegex(ValueError,'blocker section'):__import__('quality').validate(self.p)
    def test_gap_search_evidence_must_be_bound(self):
        self.disclose();self.change('research-receipt.json',lambda d:d['project_gaps'][0].update(evidence=['unbound.txt']))
        with self.assertRaisesRegex(ValueError,'search evidence'):__import__('quality').validate(self.p)
    def test_core_failure_not_excused(self):
        self.disclose();self.change('research-receipt.json',lambda d:d['coverage']['basicops'].update(status='incomplete'))
        with self.assertRaisesRegex(ValueError,'Incomplete research'):__import__('quality').validate(self.p)
    def test_regression_not_excused(self):
        self.disclose();self.change('comparison.json',lambda d:d.update(unresolved_regressions=['Dropped date']))
        with self.assertRaisesRegex(ValueError,'factual regression'):__import__('quality').validate(self.p)
    def test_brief_changed_after_review_fails(self):
        self.disclose();d=json.loads((self.p/'brief.json').read_text());d['projects'][0]['name']='Changed';self.write('brief.json',d)
        # A consistent source change still needs a new independent review.
        r=json.loads((self.p/'research-receipt.json').read_text());r['project_source_coverage'][0]['project']='Changed';r['project_source_coverage'][0]['obsidian']['status']='complete';self.write('research-receipt.json',r)
        with self.assertRaisesRegex(ValueError,'Review invalidated'):__import__('quality').validate(self.p)
    def test_render_blockers_near_bottom_escaped(self):
        b=self.disclose()
        d={'week':'2026-09-21','intro':'Updates','projects':[{'name':'Example','light':'orange','state':'Approval unconfirmed','target':'To confirm','next':'Confirm record','url':'https://example.com'}],'owners':[],'priorities':[],'new_projects':[],'blockers':[b],'cutoff':'21 September'}
        e=brief.render(d)
        self.assertLess(e['html'].index('Blockers and information needed'),e['html'].index('Updates or corrections?'))
        self.assertIn('&lt;missing&gt; &amp;',e['html']);self.assertIn('Record <missing> &',e['text'])
    def test_recovery_refuses_existing_receipt(self):
        (self.p/'receipts').mkdir();(self.p/'receipts/2026-09-21-brief.json').write_text('{}')
        with patch.object(runtime,'datetime') as dt:
            dt.now.return_value=datetime(2026,9,21,14,tzinfo=runtime.TZ)
            with self.assertRaisesRegex(ValueError,'receipt requires reconciliation'):
                runtime.run({'state':str(self.p)},'2026-09-21','recover','2026-09-21')
    def test_recovery_refuses_other_week(self):
        with patch.object(runtime,'datetime') as dt:
            dt.now.return_value=datetime(2026,9,21,14,tzinfo=runtime.TZ)
            with self.assertRaisesRegex(ValueError,'current Monday'):
                runtime.run({'state':str(self.p)},'2026-09-14','recover','2026-09-14')

if __name__=='__main__':unittest.main()
