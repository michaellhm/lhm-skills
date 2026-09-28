import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import weekly_archive as a
import weekly_runtime as r
import brief as b


class WeeklyArchiveTests(unittest.TestCase):
    def fixture(self):
        brief = {'week': '2026-09-28', 'cutoff': '28 September, 07:45 Melbourne', 'priorities': ['Review'],
                 'new_projects': [], 'projects': [], 'owners': [{'name': 'Aiya', 'actions': ['Confirm remaining work']}],
                 'blockers': [{'project':'Example', 'issue':'Completion unclear', 'impact':'Plan may change',
                               'owner':'Aiya', 'next_step':'Confirm the deliverable'}]}
        receipt = {'week':brief['week'], 'kind':'brief', 'state':'delivered',
                   'recipients':['support@localhealthmarketing.com.au'], 'message_id':'<fixture>'}
        return brief, receipt

    def service(self, existing=None, body=None):
        s = Mock(); s.drives.return_value.get.return_value.execute.return_value = {'id':a.DRIVE,'name':'LHM Knowledge'}
        s.files.return_value.list.return_value.execute.side_effect = [
            {'files':[{'id':'folder','mimeType':'application/vnd.google-apps.folder'}]},
            {'files':existing or []}]
        s.files.return_value.get_media.return_value.execute.return_value = body
        return s

    def test_iso_year_and_missing_delivery(self):
        self.assertEqual(a.identity('2026-12-28')[0], '2026-W53')
        self.assertEqual(a.identity('2027-01-04')[0], '2027-W01')
        brief, receipt = self.fixture()
        for state in ('queued', 'sending', 'failed'):
            receipt['state'] = state
            with self.assertRaises(ValueError): a.snapshot(brief,receipt)

    def test_snapshot_preserves_question_and_owner(self):
        name, text, marker = a.snapshot(*self.fixture())
        self.assertEqual(name,'2026-W40 — Web Projects.md')
        self.assertIn('Completion unclear',text); self.assertIn('**Aiya:** Confirm the deliverable',text)
        self.assertIn('## Team corrections after delivery',text); self.assertIn(marker,text)

    def test_retry_preserves_appended_feedback_without_write(self):
        name,text,marker = a.snapshot(*self.fixture())
        s = self.service([{'id':'existing'}], (text+'\nKristalyn: review complete.').encode())
        result = a.publish(s,name,text,marker,Mock())
        self.assertTrue(result['unchanged']); s.files.return_value.create.assert_not_called()

    def test_conflicting_note_and_duplicate_never_overwritten(self):
        name,text,marker = a.snapshot(*self.fixture())
        for rows,body in [([{'id':'x'}], b'Human existing note'),([{'id':'x'},{'id':'y'}],b'')]:
            s=self.service(rows,body)
            with self.assertRaises(ValueError): a.publish(s,name,text,marker,Mock())
            s.files.return_value.create.assert_not_called()

    def test_create_readback_and_wrong_drive(self):
        name,text,marker=a.snapshot(*self.fixture()); s=self.service(body=text.encode())
        s.files.return_value.create.return_value.execute.return_value={'id':'new'}
        self.assertEqual(a.publish(s,name,text,marker,Mock())['file_id'],'new')
        s=self.service();s.drives.return_value.get.return_value.execute.return_value={'id':'wrong','name':'LHM Knowledge'}
        with self.assertRaises(ValueError):a.publish(s,name,text,marker,Mock())

    def test_uncertain_creation_cannot_create_duplicate(self):
        name,text,marker=a.snapshot(*self.fixture())
        with tempfile.TemporaryDirectory() as tmp:
            intent=Path(tmp)/'intent.json';s=self.service()
            s.files.return_value.create.return_value.execute.side_effect=TimeoutError
            with self.assertRaises(TimeoutError):a.publish(s,name,text,marker,Mock(),intent)
            self.assertTrue(intent.exists())
            retry=self.service()
            with self.assertRaisesRegex(ValueError,'uncertain'):a.publish(retry,name,text,marker,Mock(),intent)
            retry.files.return_value.create.assert_not_called()

    def test_no_archive_before_delivery_and_retry_failure_is_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'archive').mkdir();(p/'receipts').mkdir()
            (p/'archive/2026-09-28.json').write_text(json.dumps({'run':'2026-09-28','state':'awaiting_delivery'}))
            with patch.object(a.subprocess,'run') as run:
                self.assertEqual(a.reconcile({'state':tmp},'2026-09-28')['state'],'awaiting_delivery');run.assert_not_called()
                (p/'receipts/2026-09-28-brief.json').write_text(json.dumps({'state':'delivered'}))
                run.side_effect=a.subprocess.TimeoutExpired('archive',90)
                self.assertEqual(a.reconcile({'state':tmp},'2026-09-28')['state'],'archive_pending')
                self.assertEqual(json.loads((p/'receipts/2026-09-28-brief.json').read_text())['state'],'delivered')

    def test_release_at_eight_both_dst_offsets_and_no_early_send(self):
        for offset in ('+10:00','+11:00'):
            # Use dates whose actual Melbourne offset matches the supplied instant.
            day='2026-09-28' if offset=='+10:00' else '2026-10-05'
            stamps=iter([datetime.fromisoformat(day+'T07:59:30'+offset),datetime.fromisoformat(day+'T08:00:00'+offset)])
            waits=[];r.wait_for_delivery(day,lambda:next(stamps),waits.append);self.assertEqual(waits,[30])
        with patch.object(b,'now',return_value=datetime.fromisoformat('2026-09-28T07:59:00+10:00')), patch.object(b,'submit_message') as send:
            with self.assertRaises(ValueError):b.send('2026-09-28',{'week':'2026-09-28','subject':'x','text':'x','html':'<table>Updates or corrections?'})
            send.assert_not_called()

    def test_delivery_cannot_roll_to_tuesday(self):
        with self.assertRaises(ValueError):r.wait_for_delivery('2026-09-28',lambda:datetime.fromisoformat('2026-09-29T08:00:00+10:00'))


if __name__ == '__main__': unittest.main()
