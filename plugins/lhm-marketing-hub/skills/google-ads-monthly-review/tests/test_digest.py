import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('digest',SCRIPTS/'ads-weekly-digest.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DigestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.run=self.base/'monthly-delivery-20260920-01';self.run.mkdir()
        self.registry={'test-client':{'name':'Example <script>'}}
        self.manifest={'week':'2026-09-21','selected_clients':['test-client'],'clients':[{'client':'test-client','state':'complete','delivery_run_id':self.run.name}]}
        self.summary={'light':'yellow','status_reason':'Under target <verified>','stage':'30 days; confidence medium','highlights':['Spend declined 10% & enquiries steady'],'next_action':'Check the selected item'}
        self.receipt={'client':'test-client','delivery_status':'complete','readback_verified':True,'verified_drive_url':'https://drive.google.com/file/d/example/view','verified_basicops_url':'https://app.basicops.com/123?l=example'}
        (self.run/'request.json').write_text(json.dumps({'client':'test-client'}))
        (self.run/'final.json').write_text(json.dumps({'exit_code':0,'status':'needs_review'}))
        self.write()
    def write(self):
        (self.run/'prompt.txt').write_text('REPORT CONTENT\n---\n```ads_digest\n'+json.dumps(self.summary)+'\n```')
        (self.run/'result.md').write_text('```ads_delivery\n'+json.dumps(self.receipt)+'\n```')
    def render(self):return m.assemble(self.manifest,self.registry,self.base)
    def test_all_zones_and_escaping(self):
        for zone in ['red','orange','yellow','blue','green','unknown']:
            self.summary['light']=zone;self.write();r=self.render()
            self.assertEqual(r['html'].count('href='),1)
            self.assertIn('&lt;script&gt;',r['html']);self.assertNotIn('<script>',r['html'])
        self.assertNotIn('drive.google.com',r['html'])
    def test_failed_and_missing_clients_visible(self):
        (self.run/'result.md').unlink();r=self.render()
        self.assertIn('Report or delivery incomplete',r['text']);self.assertNotIn('href=',r['html'])
        self.manifest['clients'][0]={'client':'test-client','state':'failed','error':'Live Ads unavailable'}
        self.assertIn('Live Ads unavailable',self.render()['text'])
    def test_unsafe_link_rejected(self):
        self.receipt['verified_basicops_url']='https://app.basicops.com.evil.test/123?l=example';self.write()
        self.assertNotIn('href=',self.render()['html'])
    def test_readback_required(self):
        self.receipt['readback_verified']=False;self.write()
        self.assertIn('Verified delivery receipt missing',self.render()['text'])
    def test_missing_card_not_success(self):
        self.receipt['verified_basicops_url']='';self.write()
        self.assertIn('Verified BasicOps card URL missing',self.render()['text'])
    def test_stale_run_rejected(self):
        self.manifest['week']='2026-09-28'
        self.assertIn('Stale delivery',self.render()['text'])
    def test_missing_cohort_and_running_rejected(self):
        self.manifest['clients'][0]['state']='running'
        with self.assertRaises(ValueError):self.render()
        self.manifest['clients']=[]
        with self.assertRaises(ValueError):self.render()
    def test_empty(self):
        self.manifest.update(selected_clients=[],clients=[])
        self.assertIsNone(self.render())
    def test_uncertain_send_never_retried(self):
        calls=[]
        def fail(*args):calls.append(args);raise TimeoutError()
        at=datetime(2026,9,21,5,tzinfo=ZoneInfo('Australia/Melbourne'))
        for _ in range(2):
            r=m.send_once('2026-09-21',self.render(),fail,self.base/'receipts',at)
            self.assertEqual(r['state'],'delivery_uncertain')
        self.assertEqual(len(calls),1)
    def test_success_dedupe_and_fixed_audience(self):
        calls=[]
        def mail(*args):calls.append(args);return {'id':'example'}
        at=datetime(2026,9,21,5,tzinfo=ZoneInfo('Australia/Melbourne'))
        for _ in range(2):m.send_once('2026-09-21',self.render(),mail,self.base/'receipts',at)
        self.assertEqual(len(calls),1);self.assertEqual(calls[0][1]['to'],m.RECIPIENT)
        self.assertNotIn('cc',calls[0][1])
    def test_supported_receipt_encodings(self):
        for text in ['```ads_digest\n'+json.dumps(self.summary)+'\n```',
                     '```json ads_digest\n'+json.dumps(self.summary)+'\n```',
                     '```json ads_digest\n'+json.dumps(self.summary)+'\n',
                     '```json\n'+json.dumps({'ads_digest':self.summary})+'\n```']:
            (self.run/'prompt.txt').write_text('REPORT CONTENT\n---\n'+text)
            self.assertIn(self.summary['highlights'][0],self.render()['text'])
            self.assertEqual(self.render()['html'].count('href='),1)
    def legacy(self):
        return {'performance_zone':'blue','measurement_confidence':'low',
                'measurement_confidence_reason':'Conversion events are not verified patients.',
                'period':{'current':{'start':'2026-08-22','end':'2026-09-20'},
                          'prior':{'start':'2026-07-23','end':'2026-08-21'}},
                'metrics':{'conversions_current':4,'conversions_prior':8,'cpa_current':90,'cpa_prior':45},
                'actions':[{'title':'Check conversion settings','status':'approved'}]}
    def test_legacy_analytical_schemas(self):
        for shape in ['metrics','totals','account_metrics']:
            d=self.legacy()
            if shape=='totals':
                del d['metrics'];d['totals']={'current':{'conversions':4,'cpa_aud':90},'prior':{'conversions':8,'cpa_aud':45}}
            elif shape=='account_metrics':
                del d['metrics'];d['account_metrics']={'conversions':4,'conversions_prior':8,'cpa':90,'cpa_prior':45}
                d['current_window']=d['period']['current'];d['prior_window']=d.pop('period')['prior']
                d['zone_caution']='Alternate budget changes the zone; decision required.'
            card=m.digest_card(d)
            self.assertEqual(card['light'],'blue')
            self.assertIn('4 current; 8 prior',card['highlights'][0])
            self.assertEqual(card['next_action'],'Review proposed action: Check conversion settings')
            self.assertNotIn('approved',json.dumps(card))
            self.assertIn('2026-08-22',card['stage'])
            if shape=='account_metrics':self.assertEqual(card['status_reason'],d['zone_caution'])
    def test_duplicate_and_malformed_receipts_fail_closed(self):
        one='```ads_digest\n'+json.dumps(self.summary)+'\n```'
        for text in [one+'\n```json\n'+json.dumps({'ads_digest':self.summary})+'\n```',
                     '```json\n{"ads_digest": broken}\n```',
                     '```ads_digest\n[]\n```',
                     '```json ads_digest\n{"light":',
                     '```json ads_digest\n'+json.dumps(self.summary)+'\nUnrelated trailing prose']:
            with self.assertRaises(ValueError):m.block(text,'ads_digest')
    def test_incomplete_legacy_data_never_invents_summary(self):
        for key in ['performance_zone','measurement_confidence','period','actions','metrics']:
            d=self.legacy();del d[key]
            with self.assertRaises(ValueError):m.digest_card(d)
        d=self.legacy();d['light']='green'
        with self.assertRaises(ValueError):m.digest_card(d)
        d=self.legacy();d['performance_zone']='unsupported'
        with self.assertRaises(ValueError):m.digest_card(d)
    def test_malformed_types_become_visible_gap(self):
        self.summary['highlights']='not a list';self.write()
        self.assertIn('Invalid email highlights',self.render()['text'])

    def test_time_guard(self):
        for at in [datetime(2026,9,21,3),datetime(2026,9,22,5)]:
            with self.assertRaises(ValueError):m.send_once('2026-09-21',self.render(),None,self.base/'receipts',at)

if __name__=='__main__':unittest.main()
