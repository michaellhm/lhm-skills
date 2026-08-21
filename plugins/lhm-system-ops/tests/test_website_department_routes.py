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


if __name__ == "__main__":
    unittest.main()
