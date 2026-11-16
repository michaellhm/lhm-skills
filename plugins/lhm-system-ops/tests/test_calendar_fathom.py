"""Regression checks for bounded recording selection; no connector/model required."""
import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / 'assets/calendar-sales-handover/fathom_read.py'
SPEC = importlib.util.spec_from_file_location('calendar_fathom_read', SOURCE)
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)


def listing(rows):
    return ('Found ' + str(len(rows)) + ' meeting(s). Each entry has recording_id and url.\n\n'
            + '\n'.join('- ' + title + ' | 2026-11-11 | id: ' + str(identifier)
                + ' | url: https://fathom.video/calls/' + str(identifier)
                + ' | recorded by Operator | ' + attendees
                for identifier, title, attendees in rows))


class FakeClient:
    rows = [(1, 'Website Onboarding Meeting with Alice, Partner and Operator', 'Alice Example, Partner')]
    calls = []
    transcript = 'Alice: ' + 'Confirmed onboarding conversation. ' * 40

    def call(self, name, arguments):
        self.calls.append((name, arguments))
        return listing(self.rows) if name == 'list_meetings' else self.transcript

    def close(self):
        pass


class RecordingSelectionTests(unittest.TestCase):
    def setUp(self):
        FakeClient.calls = []
        self.packet = {'start': '2026-11-11T13:45:00+11:00',
            'summary': 'Website Onboarding Meeting with Alice, Partner and Operator',
            'calendar_identity': 'operator@agency.test', 'organizer': 'partner@partner.test',
            'attendees': [{'email': 'alice@clinic.test', 'name': 'Alice Example'},
                          {'email': 'operator@agency.test', 'name': 'Operator'},
                          {'email': 'partner@partner.test', 'name': 'Partner'}]}

    def test_unique_recording_and_external_participant_are_required(self):
        result = reader.collect(self.packet, FakeClient)
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['match_evidence'], 'invitee_name')
        self.assertEqual(result['recording_id'], 1)
        self.assertEqual(FakeClient.calls[0][1]['created_after'], '2026-11-11T00:45:00+00:00')
        self.assertEqual(FakeClient.calls[0][1]['created_before'], '2026-11-11T04:45:00+00:00')

    def test_shared_internal_attendees_do_not_match_another_client(self):
        class WrongClient(FakeClient):
            rows = [(2, 'Website Onboarding Meeting with Bob, Partner and Operator',
                     'Bob Other, Partner, operator@agency.test')]
        result = reader.collect(self.packet, WrongClient)
        self.assertEqual(result['status'], 'not_ready')
        self.assertEqual(len(FakeClient.calls), 1)

    def test_duplicate_recordings_are_ambiguous_before_transcript(self):
        class Duplicate(FakeClient):
            rows = FakeClient.rows + [(2, FakeClient.rows[0][1], FakeClient.rows[0][2])]
        result = reader.collect(self.packet, Duplicate)
        self.assertEqual(result['status'], 'ambiguous')
        self.assertEqual(result['matching_recordings'], 2)
        self.assertEqual(len(FakeClient.calls), 1)

    def test_name_only_fallback_is_labelled(self):
        packet = {**self.packet, 'attendees': [{'email': 'alice@clinic.test'}]}
        result = reader.collect(packet, FakeClient)
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['match_evidence'], 'title_named_invitee_only')

    def test_incomplete_pagination_and_unknown_format_fail_closed(self):
        for text in [listing(FakeClient.rows) + '\nnext_cursor: opaque',
                     listing(FakeClient.rows).replace('Found 1', 'Found 2'), 'Unexpected provider output']:
            with self.subTest(text=text):
                with self.assertRaises(reader.SourceUnavailable):
                    reader.parse_meetings(text)

    def test_source_error_is_unavailable_and_redacted(self):
        class Broken(FakeClient):
            def call(self, *args):
                raise RuntimeError('sensitive authentication material')
        result = reader.collect(self.packet, Broken)
        self.assertEqual(result['status'], 'unavailable')
        self.assertNotIn('sensitive', str(result))

    def test_unready_transcript_is_retried_without_claiming_evidence(self):
        class Pending(FakeClient):
            transcript = 'Transcript is not ready'
        self.assertEqual(reader.collect(self.packet, Pending)['status'], 'not_ready')

    def test_unicode_transcript_output_is_bounded_by_bytes(self):
        class Large(FakeClient):
            transcript = '界' * 120000
        result = reader.collect(self.packet, Large)
        self.assertTrue(result['transcript_truncated'])
        self.assertLess(len(result['transcript'].encode()), reader.MAX_TRANSCRIPT + 100)


if __name__ == '__main__':
    unittest.main()
