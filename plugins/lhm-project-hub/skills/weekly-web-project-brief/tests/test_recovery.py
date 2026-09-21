import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import brief as b
import supervise as w
import weekly_runtime as r


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.at = datetime.fromisoformat('2026-09-21T13:00:00+10:00')

    def test_second_repair_gets_new_review(self):
        reviews = [{'accepted': False, 'issues': ['first']},
                   {'accepted': False, 'issues': ['second']},
                   {'accepted': True, 'issues': []}]
        repairs = []; checks = []
        result = r.reviewed_with_repairs(lambda n: reviews[n], repairs.append, lambda: checks.append(True))
        self.assertTrue(result['accepted']); self.assertEqual(len(checks), 2)
        self.assertEqual(len(repairs[1]['reviews']), 2)  # feedback snapshot before final review

    def test_retry_exhaustion_is_terminal(self):
        attempts = []; repairs = []
        def reject(n):
            attempts.append(n); return {'accepted': False, 'issues': ['missing source']}
        with self.assertRaisesRegex(RuntimeError, 'Independent review rejected'):
            r.reviewed_with_repairs(reject, repairs.append, lambda: None)
        self.assertEqual(attempts, [0, 1, 2]); self.assertEqual(len(repairs), 2)

    def test_validation_failure_stops_repairs(self):
        attempts = []
        def bad(): raise ValueError('material gap remains')
        with self.assertRaises(ValueError):
            r.reviewed_with_repairs(lambda n: attempts.append(n) or {'accepted':False}, lambda x: None, bad)
        self.assertEqual(attempts, [0])

    def test_queue_failure_exits_unsuccessfully_and_attempts_alert(self):
        cfg={'state':str(self.base),'watch_from_week':'2026-09-21'}
        config=self.base/'config.json';config.write_text(json.dumps(cfg))
        incoming=self.base/'incoming';incoming.mkdir()
        (incoming/'2026-09-21.json').write_text(json.dumps({'mode':'scheduled','week':'2026-09-21'}))
        with patch.object(r,'CONFIG',config), patch.object(sys,'argv',['runtime','queue']), \
             patch.object(r,'validate_request',return_value='2026-09-21'), \
             patch.object(r,'run',side_effect=RuntimeError('startup failure')), \
             patch.object(w,'check',return_value={'state':'attention_required'}) as watch:
            with self.assertRaises(SystemExit) as exc:r.main()
        self.assertEqual(exc.exception.code,1);watch.assert_called_once()
        self.assertTrue((self.base/'processed/2026-09-21.json').exists())
        self.assertEqual(json.loads((self.base/'runtime/2026-09-21/status.json').read_text())['state'],'failed')

    def test_alert_has_separate_intent_and_fixed_recipient(self):
        calls = []
        def mail(*args): calls.append(args); return {'id': '<alert-id>'}
        with patch.object(b, 'BASE', self.base), patch.object(b, 'now', return_value=self.at), patch.object(b, 'mailgun', side_effect=mail):
            b.alert('2026-09-21', 'quality_blocked'); b.alert('2026-09-21', 'timeout')
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1]['to'], 'support@localhealthmarketing.com.au')
            self.assertNotIn('cc', calls[0][1]); self.assertIn('failure notice', calls[0][1]['text'])
            self.assertTrue(b.receipt('2026-09-21','alert').exists())
            self.assertFalse(b.receipt('2026-09-21').exists())

    def test_uncertain_alert_never_resends(self):
        with patch.object(b, 'BASE', self.base), patch.object(b, 'now', return_value=self.at), patch.object(b, 'mailgun', side_effect=TimeoutError) as mail:
            with self.assertRaises(RuntimeError): b.alert('2026-09-21','worker_failed')
            b.alert('2026-09-21','worker_failed')
            self.assertEqual(mail.call_count,1)
            self.assertEqual(json.loads(b.receipt('2026-09-21','alert').read_text())['state'],'delivery_uncertain')

    def test_no_alert_after_delivered_and_no_stale_notice(self):
        with patch.object(b,'BASE',self.base), patch.object(b,'now',return_value=self.at), patch.object(b,'mailgun') as mail:
            b.save(b.receipt('2026-09-21'), {'state':'delivered'})
            self.assertEqual(b.alert('2026-09-21','quality_blocked')['state'],'brief_already_delivered')
            with self.assertRaises(ValueError):b.alert('2026-09-14','worker_failed')
            with self.assertRaises(ValueError):b.alert('2026-09-21','raw secret or exception')
            mail.assert_not_called()

    def test_watchdog_missed_start_and_dst(self):
        for stamp in ['2026-09-21T12:14:00+10:00','2026-10-05T12:14:00+11:00']:
            at=datetime.fromisoformat(stamp)
            self.assertIsNone(w.decision(at,{}, {}, 'inactive'))
            self.assertEqual(w.decision(at+timedelta(minutes=1),{}, {}, 'inactive'),'missed_start')

    def test_watchdog_worker_and_delivery_states(self):
        running={'state':'running','started_at':self.at.isoformat()}
        self.assertIsNone(w.decision(self.at,running,{},'activating'))
        self.assertEqual(w.decision(self.at,running,{},'inactive'),'interrupted')
        self.assertEqual(w.decision(self.at+timedelta(hours=3),running,{},'activating'),'timeout')
        self.assertEqual(w.decision(self.at,{'state':'failed','failure_reason':'quality_blocked'},{},'inactive'),'quality_blocked')
        for state,reason in [('failed','delivery_failed'),('delivery_uncertain','delivery_uncertain')]:
            self.assertEqual(w.decision(self.at,{}, {'state':state},'inactive'),reason)
        pending={'state':'queued','started_at':self.at.isoformat()}
        self.assertIsNone(w.decision(self.at,{},pending,'inactive'))
        self.assertEqual(w.decision(self.at+timedelta(minutes=20),{},pending,'inactive'),'delivery_pending')
        self.assertIsNone(w.decision(self.at,{'state':'failed'},{'state':'delivered'},'failed'))

    def test_reconcile_delivered_before_alert(self):
        receipt=self.base/'receipts/2026-09-21-brief.json';receipt.parent.mkdir()
        receipt.write_text(json.dumps({'state':'queued','message_id':'id','started_at':self.at.isoformat()}))
        def sender(action,week,reason=None):
            self.assertEqual(action,'verify');receipt.write_text(json.dumps({'state':'delivered'}))
        with patch.object(w,'sender',side_effect=sender) as call, patch.object(w.subprocess,'run') as run:
            run.return_value.stdout='inactive\n'
            result=w.check({'state':str(self.base),'watch_from_week':'2026-09-21'},self.at)
            self.assertEqual(result['state'],'healthy_or_in_progress');self.assertEqual(call.call_count,1)

if __name__=='__main__':unittest.main()
