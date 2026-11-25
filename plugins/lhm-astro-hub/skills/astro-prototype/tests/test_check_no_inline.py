import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_no_inline.py"
spec = importlib.util.spec_from_file_location("check_no_inline", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def run(files):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return mod.find_inline(root)


CLEAN = """<!DOCTYPE html>
<html lang="en-AU">
<head>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<p>Hello</p>
<script src="assets/js/main.js"></script>
</body>
</html>
"""


class CheckNoInlineTest(unittest.TestCase):
    def test_clean_prototype_passes(self):
        self.assertEqual(run({"index.html": CLEAN}), [])

    def test_inline_style_attr_flagged(self):
        html = '<html>\n<body>\n<p style="color:red">Hi</p>\n</body>\n</html>\n'
        self.assertEqual(run({"index.html": html}), ["index.html:3: inline style attribute"])

    def test_style_attr_case_insensitive(self):
        html = "<body>\n<P STYLE='x:y'>Hi</P>\n</body>\n"
        self.assertEqual(run({"index.html": html}), ["index.html:2: inline style attribute"])

    def test_style_block_flagged(self):
        html = "<head>\n<style>\nbody{margin:0}\n</style>\n</head>\n"
        self.assertEqual(run({"index.html": html}), ["index.html:2: inline style block"])

    def test_inline_script_flagged(self):
        html = "<body>\n<script>\nalert(1)\n</script>\n</body>\n"
        self.assertEqual(run({"index.html": html}), ["index.html:2: inline script"])

    def test_script_with_src_allowed(self):
        self.assertEqual(run({"index.html": '<script src="a.js"></script>\n'}), [])

    def test_jsonld_allowed(self):
        html = '<head>\n<script type="application/ld+json">{"@context":"x"}</script>\n</head>\n'
        self.assertEqual(run({"index.html": html}), [])

    def test_nested_file_reported_relative(self):
        html = "<p>\n<p style=\"a:b\">\n"
        self.assertEqual(run({"about/index.html": html}), ["about/index.html:2: inline style attribute"])

    def test_non_html_ignored(self):
        self.assertEqual(run({"assets/css/style.css": "<style>", "notes.txt": 'style="x"'}), [])

    def test_multiple_findings_sorted(self):
        res = run({"b.html": "<style>\n", "a.html": "<script>\n</script>\n"})
        self.assertEqual(res, ["a.html:1: inline script", "b.html:1: inline style block"])


if __name__ == "__main__":
    unittest.main()
