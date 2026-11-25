import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "brain_cursor", Path(__file__).resolve().parents[1] / "scripts" / "brain_cursor.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class BrainCursorTest(unittest.TestCase):
    def test_marker_none(self):
        self.assertIsNone(m.last_processed("x\n<!-- last-processed: none -->"))

    def test_marker_absent(self):
        self.assertIsNone(m.last_processed(""))

    def test_marker_sha(self):
        self.assertEqual(m.last_processed("x\n<!-- last-processed: abc123 -->\n"), "abc123")

    def test_last_marker_wins(self):
        text = "<!-- last-processed: aaa111 -->\nmore\n<!-- last-processed: bbb222 -->"
        self.assertEqual(m.last_processed(text), "bbb222")

    def test_set_marker_replaces(self):
        out = m.set_marker("# Log\n\n<!-- last-processed: none -->\n", "def456")
        self.assertEqual(out.count("last-processed"), 1)
        self.assertEqual(m.last_processed(out), "def456")

    def test_set_marker_replaces_many(self):
        out = m.set_marker("<!-- last-processed: a1 -->\nx\n<!-- last-processed: b2 -->\n", "c3")
        self.assertEqual(out.count("last-processed"), 1)
        self.assertEqual(m.last_processed(out), "c3")

    def test_set_marker_appends(self):
        out = m.set_marker("# Log\n\nentry", "abc123")
        self.assertEqual(out.count("last-processed"), 1)
        self.assertEqual(m.last_processed(out), "abc123")
        self.assertTrue(out.startswith("# Log\n\nentry"))
        self.assertTrue(out.endswith("<!-- last-processed: abc123 -->\n"))


if __name__ == "__main__":
    unittest.main()
