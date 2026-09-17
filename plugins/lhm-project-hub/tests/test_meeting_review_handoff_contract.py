import re
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "references/meeting-review-handoff-contract.md").read_text()
WORDS = " ".join(CONTRACT.split())


def review_target(next_meeting, timezone_name):
    """Contract fixture: calendar-date subtraction in a validated requester timezone."""
    ZoneInfo(timezone_name)
    return date.fromisoformat(next_meeting) - timedelta(days=14)


class MeetingReviewHandoffContractTests(unittest.TestCase):
    def test_label_and_read_state_are_not_approval(self):
        self.assertIn("None is approval", CONTRACT)
        self.assertIn("approved task IDs", CONTRACT)
        self.assertIn("material scope change", CONTRACT)

    def test_existing_work_is_not_duplicated(self):
        self.assertIn("Existing callback", WORDS)
        self.assertIn("not a duplicate build", WORDS)
        self.assertIn("Separate recorded decisions from suggestions", WORDS)

    def test_client_inputs_are_consolidated_but_not_sent(self):
        self.assertIn("one human-owned follow-up", CONTRACT)
        self.assertIn("traceable checklist or linked subtasks", CONTRACT)
        self.assertIn("copy-ready email", CONTRACT)
        self.assertIn("remains unsent", CONTRACT)

    def test_calendar_target_and_timezone_fixture(self):
        self.assertIn("14 calendar days", CONTRACT)
        self.assertIn("Australia/Melbourne", CONTRACT)
        self.assertIn("2026-10-14", CONTRACT)
        self.assertIn("2026-09-30", CONTRACT)
        self.assertIn("not evidence of a client-contact cadence", WORDS)
        self.assertEqual(review_target("2026-10-14", "Australia/Melbourne"), date(2026, 9, 30))
        self.assertEqual(review_target("2027-03-10", "Australia/Melbourne"), date(2027, 2, 24))
        before = datetime(2026, 10, 3, 12, tzinfo=ZoneInfo("Australia/Melbourne")).utcoffset()
        after = datetime(2026, 10, 5, 12, tzinfo=ZoneInfo("Australia/Melbourne")).utcoffset()
        self.assertNotEqual(before, after)

    def test_blocked_item_does_not_block_ready_item(self):
        self.assertIn("Do not dispatch a task whose required client input", CONTRACT)
        self.assertIn("unaffected, input-ready approved task may proceed independently", WORDS)

    def test_lily_and_ted_ids_and_chain_are_exact(self):
        self.assertRegex(CONTRACT, r"Lily.*`82484`")
        self.assertRegex(CONTRACT, r"Ted \(`82491`\)")
        for role in ("Chief of Staff", "Context & Research", "Head of Production", "specialist", "independent final QA"):
            self.assertIn(role, CONTRACT)

    def test_replay_review_and_completion_guards(self):
        self.assertIn("idempotency key", CONTRACT)
        self.assertIn("without duplicating it", CONTRACT)
        self.assertIn("native review request", CONTRACT)
        self.assertIn("`Under Review`", CONTRACT)
        self.assertIn("Never automatically mark it `Complete`", WORDS)

    def test_identity_and_permission_ceiling(self):
        self.assertIn("verify the actual sender/actor", CONTRACT)
        self.assertIn("label the message as AI-written by that actor", WORDS)
        self.assertIn("Never spoof", CONTRACT)
        self.assertNotRegex(CONTRACT, re.compile(r"password|api[_ -]?key|access[_ -]?token", re.I))


if __name__ == "__main__":
    unittest.main()
