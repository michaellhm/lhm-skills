import importlib.util
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
NOTES = ["Overview", "Profile", "Project", "Services", "Staff", "What We Do",
         "Who We Serve", "Brand", "Content Rules", "Change Log"]


def load():
    spec = importlib.util.spec_from_file_location("scaffold_client_repo", SKILL / "scripts" / "scaffold_client_repo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ScaffoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()

    def run_scaffold(self, root):
        return self.mod.scaffold(root, "Woodlands Physio", "woodlands-physio", "lhm-test")

    def test_scaffold_writes_layout(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            written = self.run_scaffold(root)
            expected = ["README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "site/.gitkeep", "skills/.gitkeep"]
            expected += [f"brain/{n}.md" for n in NOTES]
            for rel in expected:
                self.assertIn(rel, written)
                self.assertTrue((root / rel).is_file(), rel)
            for rel in written:
                self.assertNotIn("{{", (root / rel).read_text(encoding="utf-8"), rel)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("Woodlands Physio", readme)
            self.assertIn("woodlands-physio", readme)

    def test_frontmatter_and_date(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.run_scaffold(root)
            for n in NOTES:
                text = (root / "brain" / f"{n}.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\ntype: "), n)
                self.assertIn('client: "Woodlands Physio"', text)
                self.assertRegex(text, r"updated: \d{4}-\d{2}-\d{2}\n")
                self.assertIn("sources: []", text)
                if n not in ("Overview", "Project", "Change Log"):
                    self.assertIn("> gap: not yet captured", text, n)

    def test_overview_links_every_note(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.run_scaffold(root)
            text = (root / "brain" / "Overview.md").read_text(encoding="utf-8")
            for n in NOTES:
                if n != "Overview":
                    self.assertIn(f"[[{n}]]", text)

    def test_existing_file_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("client content", encoding="utf-8")
            (root / "brain").mkdir()
            (root / "brain" / "Brand.md").write_text("mine", encoding="utf-8")
            with self.assertRaises(FileExistsError) as cm:
                self.run_scaffold(root)
            self.assertIn("README.md", str(cm.exception))
            self.assertIn("Brand.md", str(cm.exception))
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "client content")
            self.assertEqual(sorted(p.name for p in root.rglob("*") if p.is_file()), ["Brand.md", "README.md"])

    def test_owner_in_readme(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.run_scaffold(root)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("github.com/lhm-test/woodlands-physio.git", readme)
            self.assertNotIn("OWNER", readme)

    def test_stray_dotfiles_skipped(self):
        stray = SKILL / "assets" / ".DS_Store"
        stray.write_text("x", encoding="utf-8")
        try:
            with tempfile.TemporaryDirectory() as d:
                written = self.run_scaffold(Path(d))
                self.assertNotIn(".DS_Store", written)
                self.assertIn("site/.gitkeep", written)
        finally:
            stray.unlink()

    def test_changelog_marker(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.run_scaffold(root)
            text = (root / "brain" / "Change Log.md").read_text(encoding="utf-8")
            self.assertTrue(text.rstrip().endswith("<!-- last-processed: none -->"))

    def test_short_agent_files_and_readme(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.run_scaffold(root)
            for f in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
                text = (root / f).read_text(encoding="utf-8")
                self.assertLess(len(text.splitlines()), 10)
                for needle in ("README.md", "brain/Overview.md", "brain/Content Rules.md", "skills/"):
                    self.assertIn(needle, text, f)
            self.assertLess(len((root / "README.md").read_text(encoding="utf-8").splitlines()), 60)


if __name__ == "__main__":
    unittest.main()
