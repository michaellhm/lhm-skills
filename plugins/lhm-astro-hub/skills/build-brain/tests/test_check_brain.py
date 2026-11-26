import importlib.util
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SETUP = SKILL.parent / "client-repo-setup"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CheckBrainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = load("scaffold_client_repo", SETUP / "scripts" / "scaffold_client_repo.py")
        cls.check = load("check_brain", SKILL / "scripts" / "check_brain.py")

    def make_brain(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.scaffold.scaffold(root, "Woodlands Physio", "woodlands-physio", "lhm-test")
        return root / "brain"

    def test_scaffolded_brain_passes(self):
        self.assertEqual(self.check.check_brain(self.make_brain()), [])

    def test_missing_note(self):
        brain = self.make_brain()
        (brain / "Staff.md").unlink()
        self.assertIn("Staff.md: missing", self.check.check_brain(brain))

    def test_missing_brain_dir(self):
        with tempfile.TemporaryDirectory() as d:
            problems = self.check.check_brain(Path(d) / "nope")
            self.assertIn("Staff.md: missing", problems)

    def test_missing_frontmatter_key(self):
        brain = self.make_brain()
        p = brain / "Staff.md"
        p.write_text(p.read_text().replace("updated:", "changed:", 1))
        self.assertIn("Staff.md: missing frontmatter key updated", self.check.check_brain(brain))

    def test_no_frontmatter(self):
        brain = self.make_brain()
        (brain / "Staff.md").write_text("# Staff\n\n> gap: x\n")
        problems = self.check.check_brain(brain)
        for key in ("type", "client", "updated", "sources"):
            self.assertIn(f"Staff.md: missing frontmatter key {key}", problems)

    def test_unsourced_facts(self):
        brain = self.make_brain()
        (brain / "Services.md").write_text(
            '---\ntype: services\nclient: "X"\nupdated: 2026-11-25\nsources: []\n---\n\n# Services\n\nWe offer physio.\n')
        self.assertIn("Services.md: facts without sources", self.check.check_brain(brain))

    def test_inline_sources_pass(self):
        brain = self.make_brain()
        (brain / "Services.md").write_text(
            '---\ntype: services\nclient: "X"\nupdated: 2026-11-25\nsources: [fathom-123, site]\n---\n\n# Services\n\nWe offer physio.\n')
        self.assertEqual(self.check.check_brain(brain), [])

    def test_block_list_sources_pass(self):
        brain = self.make_brain()
        (brain / "Services.md").write_text(
            '---\ntype: services\nclient: "X"\nupdated: 2026-11-25\nsources:\n  - fathom call 2026-11-01\n  - prototype copy\n---\n\n# Services\n\nWe offer physio.\n')
        self.assertEqual(self.check.check_brain(brain), [])

    def test_empty_block_list_is_unsourced(self):
        brain = self.make_brain()
        (brain / "Services.md").write_text(
            '---\ntype: services\nclient: "X"\nupdated: 2026-11-25\nsources:\n---\n\n# Services\n\nWe offer physio.\n')
        self.assertIn("Services.md: facts without sources", self.check.check_brain(brain))

    def test_overview_missing_link(self):
        brain = self.make_brain()
        p = brain / "Overview.md"
        p.write_text(p.read_text().replace("- [Staff](Staff.md)\n", ""))
        self.assertIn("Overview.md: missing link to Staff.md", self.check.check_brain(brain))

    def test_exempt_notes_with_facts_and_no_sources(self):
        brain = self.make_brain()
        (brain / "Project.md").write_text(
            '---\ntype: project\nclient: "X"\nupdated: 2026-11-25\nsources: []\n---\n\n# Project\n\n## Round 1\n\n- [ ] Home\n')
        p = brain / "Change Log.md"
        p.write_text(p.read_text().replace("(none yet)", "2026-11-25 brain created"))
        self.assertEqual(self.check.check_brain(brain), [])

    def test_cli_exit_codes(self):
        import subprocess, sys
        brain = self.make_brain()
        script = str(SKILL / "scripts" / "check_brain.py")
        self.assertEqual(subprocess.run([sys.executable, script, str(brain)], capture_output=True).returncode, 0)
        (brain / "Staff.md").unlink()
        r = subprocess.run([sys.executable, script, str(brain)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Staff.md: missing", r.stdout)


if __name__ == "__main__":
    unittest.main()
