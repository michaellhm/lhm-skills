import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SKILLS = SKILL.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class DetectStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scaffold = load("scaffold_client_repo", SKILLS / "client-repo-setup" / "scripts" / "scaffold_client_repo.py")
        cls.detect = load("detect_stage", SKILL / "scripts" / "detect_stage.py")

    def repo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.scaffold.scaffold(root, "Woodlands Physio", "woodlands-physio", "lhm-test")
        return root

    def strip_gaps(self, root, names):
        for n in names:
            p = root / "brain" / n
            p.write_text("\n".join(l for l in p.read_text().splitlines()
                                   if not l.lstrip().startswith("> gap:")) + "\n")

    def stage(self, root, **override):
        facts = self.detect.repo_facts(root)
        facts.update(override)
        return self.detect.next_stage(facts)

    def test_empty_folder_needs_repo_setup(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.detect.next_stage(self.detect.repo_facts(Path(d))), "repo-setup")

    def test_scaffolded_needs_prototype(self):
        root = self.repo()
        facts = self.detect.repo_facts(root)
        self.assertTrue(facts["brain_scaffolded"])
        self.assertFalse(facts["brand_written"])
        self.assertEqual(self.detect.next_stage(facts), "prototype")

    def test_brand_written_needs_build(self):
        root = self.repo()
        self.strip_gaps(root, ["Brand.md"])
        self.assertEqual(self.stage(root), "astro-build")

    def test_site_built_needs_build_brain(self):
        root = self.repo()
        self.strip_gaps(root, ["Brand.md"])
        (root / "site").mkdir(exist_ok=True)
        (root / "site" / "package.json").write_text("{}")
        facts = self.detect.repo_facts(root)
        self.assertTrue(facts["site_built"])
        self.assertEqual(self.detect.next_stage(facts), "build-brain")

    def test_brain_built_with_unprocessed_commits(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=[], awaiting_review=2, unprocessed_client_commits=True)
        self.assertEqual(self.detect.next_stage(facts), "update-content-brain")

    def test_awaiting_review(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=["r1"], awaiting_review=1, unprocessed_client_commits=False)
        self.assertEqual(self.detect.next_stage(facts), "client-review")

    def test_content_round(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=["r1"], awaiting_review=0, unprocessed_client_commits=False)
        self.assertEqual(self.detect.next_stage(facts), "content-round")

    def test_none_identity_skips_brain_update(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=[], awaiting_review=0, unprocessed_client_commits=None)
        self.assertEqual(self.detect.next_stage(facts), "content-round")

    def test_order_not_built_brain_before_client_commits(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=False,
                     rounds=[], awaiting_review=0, unprocessed_client_commits=True)
        self.assertEqual(self.detect.next_stage(facts), "build-brain")

    def test_register_rounds_and_awaiting(self):
        root = self.repo()
        (root / ".lhm-review").mkdir()
        reg = {"schema_version": 1,
               "pages": [{"id": "a", "route": "/a/", "status": "approved"},
                         {"id": "b", "route": "/b/", "status": "awaiting-review"},
                         {"id": "c", "route": "/c/", "status": "changes-underway"}],
               "releases": [{"id": "r1", "page_ids": ["a", "b"]}, {"id": "r2", "page_ids": ["c"]}]}
        (root / ".lhm-review" / "client-review.json").write_text(json.dumps(reg))
        facts = self.detect.repo_facts(root)
        self.assertEqual(facts["rounds"], ["r1", "r2"])
        self.assertEqual(facts["awaiting_review"], 1)
        self.assertEqual(facts["lhm_owed"], 1)

    def test_lhm_owed_counts_needs_lhm_and_changes_underway(self):
        root = self.repo()
        (root / ".lhm-review").mkdir()
        reg = {"schema_version": 1,
               "pages": [{"id": "a", "route": "/a/", "status": "needs-lhm"},
                         {"id": "b", "route": "/b/", "status": "changes-underway"},
                         {"id": "c", "route": "/c/", "status": "approved"}],
               "releases": [{"id": "r1", "page_ids": ["a", "b", "c"]}]}
        (root / ".lhm-review" / "client-review.json").write_text(json.dumps(reg))
        facts = self.detect.repo_facts(root)
        self.assertEqual(facts["lhm_owed"], 2)
        self.assertEqual(facts["awaiting_review"], 0)

    def test_lhm_fixes_before_client_review(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=["r1"], awaiting_review=3, lhm_owed=1, unprocessed_client_commits=False)
        self.assertEqual(self.detect.next_stage(facts), "lhm-fixes")

    def test_client_commits_before_lhm_fixes(self):
        facts = dict(brain_scaffolded=True, brand_written=True, site_built=True, brain_built=True,
                     rounds=["r1"], awaiting_review=0, lhm_owed=1, unprocessed_client_commits=True)
        self.assertEqual(self.detect.next_stage(facts), "update-content-brain")

    def built_site(self):
        root = self.repo()
        self.strip_gaps(root, ["Brand.md"])
        brand = root / "brain" / "Brand.md"
        brand.write_text(brand.read_text().replace("sources: []", "sources: [prototype v1]"))
        (root / "site").mkdir(exist_ok=True)
        (root / "site" / "package.json").write_text("{}")
        return root

    def add_changelog_entry(self, root, heading):
        log = root / "brain" / "Change Log.md"
        log.write_text(log.read_text().replace("(none yet)\n", heading + "\n\nSources: test.\n"))

    def test_clean_brain_without_changelog_entry_is_not_built(self):
        root = self.built_site()
        facts = self.detect.repo_facts(root)
        self.assertFalse(facts["brain_built"])
        self.assertEqual(self.detect.next_stage(facts), "build-brain")

    def test_brain_created_entry_with_profile_gaps_is_built(self):
        root = self.built_site()
        self.add_changelog_entry(root, "## 2026-11-25 — Brain created")
        self.assertIn("> gap:", (root / "brain" / "Profile.md").read_text())
        facts = self.detect.repo_facts(root)
        self.assertTrue(facts["brain_built"])
        self.assertEqual(self.detect.next_stage(facts), "content-round")

    def test_brain_created_hyphen_variant_accepted(self):
        root = self.built_site()
        self.add_changelog_entry(root, "## 2026-11-25 - Brain created")
        self.assertTrue(self.detect.repo_facts(root)["brain_built"])

    def test_brain_created_entry_needs_clean_check_brain(self):
        root = self.built_site()
        self.add_changelog_entry(root, "## 2026-11-25 — Brain created")
        (root / "brain" / "Staff.md").unlink()
        self.assertFalse(self.detect.repo_facts(root)["brain_built"])

    def test_no_register(self):
        facts = self.detect.repo_facts(self.repo())
        self.assertEqual(facts["rounds"], [])
        self.assertEqual(facts["awaiting_review"], 0)

    def test_no_identity_is_none(self):
        self.assertIsNone(self.detect.repo_facts(self.repo())["unprocessed_client_commits"])

    def git_repo(self, emails):
        root = self.repo()
        git(root, "init", "-q")
        git(root, "config", "user.name", "t")
        (root / ".lhm-review").mkdir(exist_ok=True)
        (root / ".lhm-review" / "client-config.json").write_text(
            json.dumps({"client_identity": {"github_login": "c", "commit_emails": emails}}))
        return root

    def commit(self, root, name, email):
        (root / name).write_text(name)
        git(root, "add", name)
        git(root, "-c", f"user.email={email}", "commit", "-q", "-m", name)

    def test_unprocessed_true_with_no_marker(self):
        root = self.git_repo(["Client@Example.com"])
        self.commit(root, "a.txt", "lhm@lhm.test")
        self.commit(root, "b.txt", "client@example.com")
        self.assertIs(self.detect.repo_facts(root)["unprocessed_client_commits"], True)

    def test_unprocessed_false_when_only_lhm(self):
        root = self.git_repo(["client@example.com"])
        self.commit(root, "a.txt", "lhm@lhm.test")
        self.assertIs(self.detect.repo_facts(root)["unprocessed_client_commits"], False)

    def test_marker_limits_range(self):
        root = self.git_repo(["client@example.com"])
        self.commit(root, "a.txt", "client@example.com")
        sha = git(root, "rev-parse", "HEAD")
        (root / "brain" / "Change Log.md").write_text(f"# Change Log\n\n<!-- last-processed: {sha} -->\n")
        self.commit(root, "b.txt", "lhm@lhm.test")
        self.assertIs(self.detect.repo_facts(root)["unprocessed_client_commits"], False)
        self.commit(root, "c.txt", "client@example.com")
        self.assertIs(self.detect.repo_facts(root)["unprocessed_client_commits"], True)

    def test_empty_emails_is_none(self):
        root = self.git_repo([])
        self.commit(root, "a.txt", "client@example.com")
        self.assertIsNone(self.detect.repo_facts(root)["unprocessed_client_commits"])

    def test_not_git_repo_is_none(self):
        root = self.repo()
        (root / ".lhm-review").mkdir(exist_ok=True)
        (root / ".lhm-review" / "client-config.json").write_text(
            json.dumps({"client_identity": {"commit_emails": ["x@y.com"]}}))
        self.assertIsNone(self.detect.repo_facts(root)["unprocessed_client_commits"])


if __name__ == "__main__":
    unittest.main()
