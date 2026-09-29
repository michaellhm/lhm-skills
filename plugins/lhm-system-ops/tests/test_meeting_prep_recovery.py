import importlib.util
import json
import fcntl
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, Mock

ASSETS = Path(__file__).resolve().parents[1]/'assets/meeting-prep'
sys.path.insert(0, str(ASSETS))
import meeting_prep as runtime
spec = importlib.util.spec_from_file_location('meeting_runner', ASSETS/'meeting-prep-runner.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.patch = patch.object(runtime, 'BASE', self.base)
        self.patch.start()
        self.date = '2026-09-30'
        self.directory = self.base/'runs'/self.date
        self.directory.mkdir(parents=True)
        self.calendar = self.directory/'calendar.json'
        runtime.save(self.calendar, {'events': [{'id': 'one'}]})

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def at(self, text):
        return datetime.fromisoformat(text).replace(tzinfo=runtime.TZ)

    def research(self, attempt=1, status='ready'):
        return {'meeting_date': self.date, 'attempt': attempt, 'status': status,
                'calendar_classification': [{'event_id':'one', 'classification':'client', 'reason':'verified alias'}],
                'source_coverage': {s:{'status':'checked','evidence':'latest source read'} for s in ('basicops','fathom','gmail')},
                'email_opening':'Meeting preparation.',
                'issues': [{'issue_key':'review', 'latest_evidence_at':'2026-09-30',
                    'evidence_urls':['https://example.org/task'], 'next_actor':'reviewer',
                    'next_action':'review draft', 'owner_basis':'explicit',
                    'confidence':'high','included':True,'email_entry':'Review the delivered draft.'}]}

    def gate(self, **kwargs):
        return {'wakeAgent':True, 'calendar_file':str(self.calendar)}

    def write_outputs(self, prompt, directory, attempt):
        runtime.save(directory/'research-receipt.json', self.research(attempt))
        runtime.save(directory/'email.json', {'subject':'Meeting preparation','body':'Meeting preparation.\n\nReview the delivered draft.\n\nLily'})
        return 0

    def test_untracked_body_claim_is_rejected(self):
        data=self.research()
        with self.assertRaisesRegex(ValueError,'outside the reconciled'):
            runner.validate_email(data, {'subject':'Brief', 'body':'Meeting preparation.\n\nReview the delivered draft.\n\nUnverified invoice overdue.\n\nLily'})

    def test_task_status_without_discussion_evidence_is_rejected(self):
        data=self.research();data['issues'][0]['evidence_urls']=['https://app.basicops.com/task']
        with self.assertRaisesRegex(ValueError,'latest discussion'):
            runner.validate_email(data, {'subject':'Brief','body':'Meeting preparation.\n\nReview the delivered draft.\n\nLily'})

    def test_recovery_windows_and_dst(self):
        for stamp, expected in [('2026-09-29T13:00','2026-09-30'),
                                ('2026-09-29T18:00','2026-09-30'),
                                ('2026-09-29T19:00',None),
                                ('2026-09-30T07:00','2026-09-30'),
                                ('2026-10-05T13:00','2026-10-06'),
                                ('2026-10-05T07:00',None)]:
            self.assertEqual(runner.selected_date(self.at(stamp)), expected)

    def test_calendar_credential_home_does_not_leak_to_child(self):
        with patch.dict(os.environ,{'HERMES_HOME':'/opt/data/.hermes','HERMES_PROFILE':'wrong'}), patch.object(runner.subprocess,'Popen') as launch:
            launch.return_value.wait.return_value=0
            self.assertEqual(runner.child_run('prepare',self.directory,1),0)
            self.assertEqual(launch.call_args.kwargs['env']['HERMES_HOME'],'/opt/data')
            self.assertNotIn('HERMES_PROFILE',launch.call_args.kwargs['env'])

    def test_budget_exhaustion_fails_and_can_resume(self):
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',return_value=0), patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(ValueError,'receipt'):
                runner.run(self.date)
            send.assert_not_called()
        state=runner.read(self.directory/'run-state.json')
        self.assertEqual(state['status'],'failed')
        self.assertTrue(state['retry_allowed'])
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',side_effect=self.write_outputs), patch.object(runtime,'send') as send, patch.object(runtime,'verify',return_value={'state':'delivered','receipt':'receipt'}):
            self.assertEqual(runner.run(self.date)['state'],'delivered')
            send.assert_called_once()
        self.assertEqual(runner.read(self.directory/'run-state.json')['attempts'],2)

    def test_three_failed_attempts_are_bounded(self):
        with patch.object(runtime,'gate',side_effect=RuntimeError('Calendar unavailable')) as gate, patch.object(runner,'child_run') as child:
            for _ in range(3):
                with self.assertRaisesRegex(RuntimeError,'Calendar unavailable'):runner.run(self.date)
            with self.assertRaisesRegex(RuntimeError,'attempt limit'):runner.run(self.date)
            self.assertEqual(gate.call_count,3)
            child.assert_not_called()

    def test_uncertain_send_never_repeats_research_or_send(self):
        runtime.save(runtime.receipt(self.date),{'state':'delivery_uncertain'})
        with patch.object(runner,'child_run') as child, patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(RuntimeError,'no resend'):runner.run(self.date)
            child.assert_not_called();send.assert_not_called()
        self.assertEqual(runner.read(self.directory/'run-state.json')['status'],'delivery_attention')

    def test_queued_send_is_verified_without_resend(self):
        runtime.save(runtime.receipt(self.date),{'state':'queued','message_id':'existing'})
        def delivered(date):runtime.save(runtime.receipt(date),{'state':'delivered','message_id':'existing'})
        with patch.object(runtime,'verify',side_effect=delivered) as verify, patch.object(runtime,'send') as send, patch.object(runner,'child_run') as child:
            self.assertEqual(runner.run(self.date)['state'],'delivered')
            verify.assert_called_once();send.assert_not_called();child.assert_not_called()

    def test_stale_research_cannot_send(self):
        runtime.save(self.directory/'research-receipt.json',self.research(attempt=0))
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',return_value=0), patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(ValueError,'current-attempt'):runner.run(self.date)
            send.assert_not_called()

    def test_missing_source_is_not_checked(self):
        data=self.research();del data['source_coverage']['gmail']
        with self.assertRaisesRegex(ValueError,'gmail coverage'):runner.validate_research(data,self.date,1)

    def test_overlapping_run_does_not_start_child(self):
        with (self.directory/'.run.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch.object(runner,'child_run') as child:
                self.assertEqual(runner.run(self.date)['reason'],'existing_attempt_running')
                child.assert_not_called()

    def test_missing_calendar_event_prevents_send(self):
        def outputs(prompt,directory,attempt):
            self.write_outputs(prompt,directory,attempt)
            data=self.research(attempt);data['calendar_classification'][0]['event_id']='different'
            runtime.save(directory/'research-receipt.json',data)
            return 0
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',side_effect=outputs), patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(ValueError,'every calendar event'):runner.run(self.date)
            send.assert_not_called()

    def test_prior_attempt_email_cannot_be_sent(self):
        email=self.directory/'email.json';runtime.save(email,{'subject':'Old','body':'Old content'})
        os.utime(email,(1000,1000))
        def outputs(prompt,directory,attempt):
            runtime.save(directory/'research-receipt.json',self.research(attempt));return 0
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',side_effect=outputs), patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(ValueError,'current attempt'):runner.run(self.date)
            send.assert_not_called()

    def test_source_failure_requires_visible_limitation(self):
        def outputs(prompt,directory,attempt):
            self.write_outputs(prompt,directory,attempt)
            data=self.research(attempt);data['source_coverage']['gmail']={'status':'unavailable','evidence':'one retry failed'}
            runtime.save(directory/'research-receipt.json',data);return 0
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',side_effect=outputs), patch.object(runtime,'send') as send:
            with self.assertRaisesRegex(ValueError,'Source gap'):runner.run(self.date)
            send.assert_not_called()

    def test_no_client_completion_does_not_exhaust_retries(self):
        def outputs(prompt,directory,attempt):
            data=self.research(attempt,'no_client_meetings')
            data['calendar_classification'][0]['classification']='excluded'
            runtime.save(directory/'research-receipt.json',data)
            return 0
        with patch.object(runtime,'gate',side_effect=self.gate), patch.object(runner,'child_run',side_effect=outputs) as child, patch.object(runtime,'send') as send:
            for _ in range(5):self.assertFalse(runner.run(self.date)['wakeAgent'])
            child.assert_called_once();send.assert_not_called()

    def test_explicit_date_gate_uses_today_not_tomorrow(self):
        service=Mock();service.calendars.return_value.get.return_value.execute.return_value={'id':runtime.TO}
        service.events.return_value.list.return_value.execute.return_value={'items':[]}
        google=Mock();google.build_service.return_value=service
        with patch.object(runtime,'google',return_value=google):
            out=runtime.gate(self.at('2026-09-30T06:00'),force=True,date=self.date)
        self.assertEqual(out['meeting_date'],self.date)
        self.assertIn('2026-09-30T00:00:00',service.events.return_value.list.call_args.kwargs['timeMin'])

    def test_original_sender_preserves_dedup_and_uncertainty(self):
        with patch.object(runtime,'mailgun',side_effect=TimeoutError('uncertain')) as network:
            with self.assertRaises(TimeoutError):runtime.send(self.date,'Brief','Useful verified body')
            self.assertEqual(runtime.send(self.date,'Brief','Useful verified body')['status'],'deduplicated')
            network.assert_called_once()
        self.assertEqual(runner.read(runtime.receipt(self.date))['state'],'delivery_uncertain')

    def test_both_recipient_events_required(self):
        runtime.save(runtime.receipt(self.date),{'state':'queued','message_id':'<one>'})
        events=[{'event':'delivered','recipient':runtime.TO,'message':{'headers':{'message-id':'one'}}}]
        with patch.object(runtime,'mailgun',return_value={'items':events}):
            self.assertEqual(runtime.verify(self.date)['state'],'queued')
            events.append({'event':'delivered','recipient':runtime.CC,'message':{'headers':{'message-id':'one'}}})
            self.assertEqual(runtime.verify(self.date)['state'],'delivered')


if __name__ == '__main__':unittest.main()
