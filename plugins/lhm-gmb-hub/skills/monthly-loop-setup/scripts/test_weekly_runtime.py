import json
import tempfile
import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
import weekly_runtime as w

class RuntimeTests(unittest.TestCase):
    def test_selection_uses_seo_column_and_wraps(self):
        text='## Weekly service matrix\n| [[20 Clients/A/A\\|A]] | 1 | 2 | 3 | SEO |\n| [[20 Clients/B/B\\|B]] | 3 | 4 | 1 | SEO |\n| [[20 Clients/C/C\\|C]] | 4 | — | 2 | Ads only |\n## Other\n'
        self.assertEqual(w.selected_names(text,date(2026,9,21)),(4,['B']))
        self.assertEqual(w.selected_names(text,date(2026,9,28)),(1,[]))
        self.assertEqual(w.selected_names(text,date(2026,10,5)),(2,['A']))
    def test_complete_month_windows(self):
        self.assertEqual(w.periods(date(2026,1,5)),('2025-12-01','2025-12-31','2025-11-01','2025-11-30'))
    def test_test_recipient_isolated_and_resend_suppressed(self):
        cfg={'test_email':'test@example.com','to':'owner@example.com','cc':['support@example.com'],'from':'Lily <lily@example.com>','reply_to':'test@example.com'}
        email={'subject':'Test','text':'Body','html':'<p>Body</p>'}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            def send(*a,**kw):
                self.assertTrue((p/'email-receipt.json').exists())
                self.assertEqual(a[2]['to'],'test@example.com');self.assertEqual(a[2]['cc'],'')
                return {'id':'message1'}
            with patch.object(w,'mailgun',side_effect=send) as call:
                w.send_digest(cfg,p,email,'test');w.send_digest(cfg,p,email,'test');self.assertEqual(call.call_count,1)
    def test_uncertain_send_never_auto_retries(self):
        cfg={'test_email':'test@example.com','from':'Lily','reply_to':'test@example.com'}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with patch.object(w,'mailgun',side_effect=TimeoutError) as call:
                with self.assertRaises(TimeoutError):w.send_digest(cfg,p,{'subject':'s','text':'x','html':'x'},'test')
                r=w.send_digest(cfg,p,{'subject':'s','text':'x','html':'x'},'test')
                self.assertEqual(r['state'],'delivery_uncertain');self.assertEqual(call.call_count,1)
    def test_vault_receipt_is_idempotent_and_preserves_goals(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'20 Clients/A';(root/'project-management').mkdir(parents=True)
            (root/'Goals.md').write_text('Original goal: more suitable appointments.\n')
            (root/'project-management/gmb.md').write_text('Month 0 remains open.\n')
            cfg={'vault':d,'commit':'test'};client={'evidence_prefix':'20 Clients/A/'}
            result={'task_url':'https://app.basicops.com/a','report_urls':['https://drive.google.com/a','https://drive.google.com/b','https://drive.google.com/c']}
            for _ in range(2):w.record_delivery(cfg,client,'a',result,'2026-09-21','production')
            self.assertEqual((root/'Goals.md').read_text().count('## SEO review prepared'),1)
            self.assertTrue((root/'project-management/gmb.md').read_text().startswith('Month 0 remains open.'))

    def test_production_guard(self):
        with self.assertRaises(ValueError):w.run({},'production','2026-08-03')

if __name__=='__main__':unittest.main()
