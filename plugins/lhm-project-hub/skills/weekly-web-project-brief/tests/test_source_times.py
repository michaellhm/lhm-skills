import io
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import read_audit as a
import brief
import weekly_runtime as runtime
from test_quality import QualityTest


class CaptureTests(unittest.TestCase):
    def test_retained_receipts_bind_the_observed_time_and_native_target(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory);out=work/'output';out.mkdir()
            (out/'access-receipt.json').write_text(json.dumps({'sources':{'basicops':{'status':'passed'}}}))
            (out/'research-receipt.json').write_text(json.dumps({'evidence_files':[]}))
            event={'type':'item.completed','item':{'id':'item_1','type':'mcp_tool_call',
                   'server':'basicops','tool':'get_task','arguments':{'taskId':123},
                   'status':'completed','result':{'title':'Example'}}}
            with (work/'events.jsonl').open('w') as log:
                a.capture_events([json.dumps(event)],log,
                                 lambda:datetime.fromisoformat('2026-11-21T12:00:00.123456+11:00'))
            runtime.retain_raw_reads(work,out)
            access=json.loads((out/'access-receipt.json').read_text())
            read=access['sources']['basicops']['reads'][0]
            self.assertEqual(read['read_at'],'2026-11-21T12:00:00.123456+11:00')
            self.assertEqual(read['target'],{'taskId':123})
            before=(out/access['controller_read_receipts']['path']).read_bytes()
            runtime.retain_raw_reads(work,out)
            self.assertEqual(before,(out/access['controller_read_receipts']['path']).read_bytes())

    def test_each_live_result_gets_its_own_observation(self):
        stamps = iter([datetime.fromisoformat(x) for x in
                       ('2026-11-21T12:00:00.123456+11:00', '2026-11-21T12:00:01.654321+11:00')])
        stream = io.StringIO()
        a.capture_events([json.dumps({'type':'item.completed','item':{'id':str(n)}})+'\n'
                          for n in range(2)], stream, lambda: next(stamps))
        events = [json.loads(x) for x in stream.getvalue().splitlines()]
        self.assertNotEqual(events[0]['controller_read_at'], events[1]['controller_read_at'])
        self.assertTrue(all(a.precise_time(x['controller_read_at']) for x in events))

    def test_old_or_failed_reads_cannot_acquire_times_during_replay(self):
        record={'id':'1','type':'mcp_tool_call','server':'basicops','tool':'get_task',
                'status':'completed','result':{'title':'Example'}}
        self.assertIsNone(a.read_entry(record,'events.jsonl','raw.json'))
        record.update(controller_read_at='2026-11-21T12:00:00+11:00',error='access denied')
        self.assertIsNone(a.read_entry(record,'events.jsonl','raw.json'))

    def test_broker_commands_and_meeting_sources_keep_exact_targets(self):
        item={'type':'command_execution','command':
              '/bin/bash -lc "python3 /skill/source_read.py vault-read \'50 Meetings/a.md\'"'}
        self.assertEqual(a.source_identity(item),('meetings','vault-read','50 Meetings/a.md'))
        item['command']='python3 /skill/source_read.py gmail-get abc123'
        self.assertEqual(a.source_identity(item),('gmail','gmail-get','abc123'))


class TimestampQualityTests(QualityTest):
    def test_cutoff_prose_is_not_a_source_read_timestamp(self):
        self.change('access-receipt.json',lambda d:d.pop('controller_read_receipts'))
        with self.assertRaisesRegex(ValueError,'Controller source read timestamps'):
            __import__('quality').validate(self.p,require_review=False)

    def test_changed_receipt_timestamp_does_not_match_native_result(self):
        audit=json.loads((self.p/'source-times.json').read_text())
        audit['reads'][0]['read_at']='2026-09-21T08:00:00+10:00'
        self.write('source-times.json',audit)
        q=__import__('quality')
        self.change('research-receipt.json',lambda d:next(f for f in d['evidence_files']
                    if f['path']=='source-times.json').update(sha256=q.digest(self.p/'source-times.json')))
        self.change('access-receipt.json',lambda d:d['controller_read_receipts'].update(sha256=q.digest(self.p/'source-times.json')))
        with self.assertRaisesRegex(ValueError,'differs from controller'):
            q.validate(self.p,require_review=False)


class NewProjectTests(unittest.TestCase):
    def sample(self):
        return {'week':'2026-11-16','evidence_cutoff':'2026-11-21T12:00:00+11:00',
                'new_projects':[{'project':'Example','event_type':'handover','event_date':'2026-11-16',
                'text':'Strategy handover','url':'https://example.com','evidence':'source.json'}]}

    def test_real_dated_handover_is_visible(self):
        self.assertIn('handover 2026-11-16',brief.new_project_items(self.sample())[0]['text'])

    def test_prototype_send_and_revisions_are_not_new_projects(self):
        for event in ('prototype_sent','revision','interview_booked'):
            d=self.sample();d['new_projects'][0]['event_type']=event
            with self.assertRaisesRegex(ValueError,'kickoff or handover'):brief.new_project_items(d)
        d=self.sample();d['new_projects']=['Prototype sent today']
        with self.assertRaises(ValueError):brief.new_project_items(d)

    def test_missing_evidence_and_out_of_window_dates_fail(self):
        for field,value in [('event_date','2026-11-01'),('event_date','2026-11-22'),('evidence','')]:
            d=self.sample();d['new_projects'][0][field]=value
            with self.assertRaises(ValueError):brief.new_project_items(d)


if __name__ == '__main__':
    unittest.main()
