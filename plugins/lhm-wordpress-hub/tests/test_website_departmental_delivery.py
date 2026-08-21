import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebsiteDepartmentalDeliveryTest(unittest.TestCase):
    def test_each_route_has_lead_entry_skill_and_qa_contract(self):
        contract = (ROOT / "references/website-departmental-delivery.md").read_text()
        for route in ("prototype", "astro", "wordpress"):
            lead = (ROOT / f"agents/{route}-lead.md").read_text()
            entry = (ROOT / f"skills/start-{route}/SKILL.md").read_text()
            self.assertIn(f"start-{route}", contract)
            self.assertIn(f"start-{route}", lead)
            self.assertIn("website-delivery-qa", lead)
            self.assertIn("website-delivery-qa", entry)

    def test_prototype_route_requires_sitemap_architect_and_publish_receipt(self):
        entry = (ROOT / "skills/start-prototype/SKILL.md").read_text()
        contract = (ROOT / "references/website-departmental-delivery.md").read_text()
        self.assertIn("sitemap-architect", entry)
        self.assertIn("observed commit SHA and URL", contract)


if __name__ == "__main__":
    unittest.main()
