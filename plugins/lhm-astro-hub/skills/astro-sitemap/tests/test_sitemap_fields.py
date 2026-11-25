import importlib.util
import json
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_example():
    return json.loads((SKILL / "assets" / "example-sitemap.json").read_text(encoding="utf-8"))


def spec_with(*pages):
    return {"brand": {"name": "Test Clinic"}, "nav": [{"label": "Home"}], "intro": {"title": "Plan", "text": "x"},
            "sections": [{"title": "Services", "cards": [{"head": "Core", "items": list(pages)}]}]}


class SitemapFieldsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_mod = load("page_brief_seed", SKILL / "scripts" / "page_brief_seed.py")
        cls.html_mod = load("build_sitemap_html", SKILL / "scripts" / "build_sitemap_html.py")

    def _html(self, spec):
        out = self.html_mod.build(spec)
        return out[0] if isinstance(out, tuple) else out

    def test_missing_fields_named(self):
        spec = spec_with(
            {"name": "Lawn Mowing", "status": "new", "primary_keyword": "lawn mowing geelong", "intent": "commercial"},
            {"name": "About Us", "status": "have"},
        )
        self.assertEqual(self.seed_mod.missing_brief_fields(spec), ["Lawn Mowing: audience"])

    def test_have_page_without_fields_is_fine(self):
        spec = spec_with({"name": "About Us", "status": "have"})
        self.assertEqual(self.seed_mod.missing_brief_fields(spec), [])

    def test_missing_defaults_to_new_and_enh_checked(self):
        spec = spec_with({"name": "A"}, {"name": "B", "status": "enh"})
        self.assertEqual(
            self.seed_mod.missing_brief_fields(spec),
            [f"{n}: {f}" for n in ("A", "B") for f in ("primary_keyword", "audience", "intent")],
        )

    def test_example_has_no_missing_fields(self):
        self.assertEqual(self.seed_mod.missing_brief_fields(load_example()), [])

    def test_seed_returns_fields(self):
        spec = load_example()
        page = next(
            p for s in spec["sections"] for c in s["cards"] for p in c["items"]
            if p.get("status") in ("new", "enh") and p.get("primary_keyword")
        )
        got = self.seed_mod.seed(spec, page["name"])
        self.assertEqual(got["page"], page["name"])
        self.assertEqual(got["primary_keyword"], page["primary_keyword"])
        self.assertEqual(got["audience"], page["audience"])
        self.assertEqual(got["intent"], page["intent"])
        self.assertEqual(got["secondary_keywords"], page.get("secondary_keywords", []))
        self.assertEqual(got["slug"], page.get("slug"))
        self.assertTrue(got["section"])
        self.assertEqual(
            set(got),
            {"page", "slug", "primary_keyword", "secondary_keywords", "audience", "intent", "h1", "template", "section"},
        )

    def test_seed_defaults_for_absent_optional(self):
        spec = spec_with({"name": "X", "primary_keyword": "k", "audience": "a", "intent": "commercial"})
        got = self.seed_mod.seed(spec, "X")
        self.assertEqual(got["secondary_keywords"], [])
        self.assertIsNone(got["h1"])
        self.assertIsNone(got["template"])
        self.assertEqual(got["section"], "Services")

    def test_seed_unknown_page(self):
        with self.assertRaises(KeyError) as cm:
            self.seed_mod.seed(load_example(), "No Such Page")
        self.assertIn("No Such Page", str(cm.exception))

    def test_html_shows_keyword(self):
        spec = spec_with(
            {"name": "Lawn Mowing", "status": "new", "primary_keyword": "lawn mowing geelong"},
            {"name": "About Us", "status": "have"},
        )
        out = self._html(spec)
        self.assertIn('class="kw"', out)
        self.assertIn("lawn mowing geelong", out)

    def test_html_unchanged_without_keyword(self):
        out = self._html(spec_with({"name": "About Us", "status": "have"}))
        self.assertNotIn('<span class="kw">', out)
        with_kw = self._html(spec_with({"name": "About Us", "status": "have", "primary_keyword": "k"}))
        self.assertEqual(with_kw.replace('<span class="kw">k</span>', ""), out)

    def test_html_escapes_keyword(self):
        out = self._html(spec_with({"name": "P", "primary_keyword": "a <b> & c"}))
        self.assertIn("a &lt;b&gt; &amp; c", out)

    def test_cli_check_exit_codes(self):
        import subprocess, sys, tempfile
        script = str(SKILL / "scripts" / "page_brief_seed.py")
        with tempfile.TemporaryDirectory() as t:
            bad = Path(t) / "bad.json"
            bad.write_text(json.dumps(spec_with({"name": "Z", "status": "new"})))
            r = subprocess.run([sys.executable, script, str(bad), "--check"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("Z: audience", r.stdout)
            good = SKILL / "assets" / "example-sitemap.json"
            r = subprocess.run([sys.executable, script, str(good), "--check"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            r = subprocess.run([sys.executable, script, str(bad), "Z"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout)["page"], "Z")
            r = subprocess.run([sys.executable, script, str(bad), "Nope"], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)

    @unittest.skipUnless(importlib.util.find_spec("openpyxl"), "openpyxl not installed")
    def test_workbook_columns(self):
        import tempfile
        import openpyxl
        wbmod = load("build_workbook", SKILL / "scripts" / "build_workbook.py")
        spec = load_example()
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "out.xlsx"
            wbmod.build(spec, str(out))
            ws = openpyxl.load_workbook(out).worksheets[0]
            header = [c.value for c in ws[2]]
        for col in ("Primary keyword", "Secondary keywords", "Audience", "Intent"):
            self.assertIn(col, header)
        self.assertEqual(header.index("Primary keyword"), header.index("Searches/mo") + 1)


if __name__ == "__main__":
    unittest.main()
