import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebsiteDepartmentRoutesTest(unittest.TestCase):
    def test_dispatcher_and_worker_allow_explicit_department_leads(self):
        dispatcher = (ROOT / "assets/gateways/lhm-shared-claude-dispatcher").read_text()
        worker = (ROOT / "assets/gateways/lhm-shared-claude-worker").read_text()
        for route in ("prototype", "astro", "wordpress"):
            self.assertIn(f"'{route}': ('lhm-wordpress-hub:{route}-lead', '{route}-lead')", dispatcher)
            self.assertIn(f"'lhm-wordpress-hub:{route}-lead'", worker)
        self.assertIn("Entry skill invoked", worker)

    def test_wordpress_rest_routes_to_wordpress_lead_and_operator_skill(self):
        dispatcher = (ROOT / "assets/gateways/lhm-shared-claude-dispatcher").read_text()
        client = (ROOT / "assets/container/claude-dispatch").read_text()
        self.assertIn("'wordpress-rest': ('lhm-wordpress-hub:wordpress-lead', 'wordpress-lead')", dispatcher)
        self.assertIn("'wordpress-rest': 'lhm-wordpress-hub:wp-rest-operator'", dispatcher)
        self.assertIn("'wordpress-rest': 'lhm-wordpress-hub:wp-rest-operator'", client)
        profile_skill = (ROOT.parent / "lhm-wordpress-hub/assets/hermes-profile/lhm-website-dispatch/SKILL.md").read_text()
        self.assertIn("through Claude Code CLI", profile_skill)
        self.assertIn("submit-specialist-readonly wordpress-rest", profile_skill)
        self.assertIn("review-only", profile_skill)


if __name__ == "__main__":
    unittest.main()
