"""Structure tests for the lhm-astro-hub plugin.

Later tasks extend REQUIRED_MENTIONS (path relative to plugin root -> strings
that file must contain). Files are found by walking the plugin folder, never
by importing the skills.
"""
import json
import re
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
PLUGIN_NAME = "lhm-astro-hub"

FORBIDDEN = ["lhm-marketing-hub", "lhm-wordpress-hub", "lhm-project-hub", "lhm-client-updates-hub"]

REQUIRED_MENTIONS: dict = {
    "skills/astro-prototype/SKILL.md": ["ui-ux-pro-max", "brain/Brand.md", "lhm-prototype", "check_no_inline.py"],
    "skills/astro-build/SKILL.md": ["site/", "astro-build-standard.md", "astro-form"],
    "skills/astro-form/SKILL.md": ["GoHighLevel", "D1", "Turnstile"],
    "skills/astro-form/references/gohighlevel.md": ["GHL_WEBHOOK_URL", "never commit"],
}

TEXT_SUFFIXES = {".md", ".json", ".py", ".yaml", ".yml", ".txt", ".html", ".css", ".js"}
SELF = Path(__file__).resolve()
CLEAN_LEARNED = (
    "# Learned\n\n"
    "<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->"
)


def plugin_files(pattern="*"):
    return sorted(p for p in PLUGIN_ROOT.rglob(pattern) if p.is_file())


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm, key, buf = {}, None, []
    for line in m.group(1).split("\n"):
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            if key:
                fm[key] = " ".join(buf).strip()
            key, buf = km.group(1), [km.group(2)]
        elif key:
            buf.append(line.strip())
    if key:
        fm[key] = " ".join(buf).strip()
    return fm


def strip_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


class PluginStructure(unittest.TestCase):
    def test_manifest_matches_marketplace(self):
        manifest = json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], PLUGIN_NAME)
        market = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
        entries = [p for p in market["plugins"] if p["name"] == PLUGIN_NAME]
        self.assertEqual(len(entries), 1, "marketplace.json needs exactly one entry for " + PLUGIN_NAME)
        self.assertEqual(entries[0]["source"], "./plugins/" + PLUGIN_NAME)
        self.assertEqual(manifest["version"], entries[0]["version"])

    def test_skill_frontmatter(self):
        for skill in plugin_files("SKILL.md"):
            if skill.parent.parent.name != "skills":
                continue
            fm = frontmatter(skill.read_text())
            self.assertIsNotNone(fm, f"{skill}: missing frontmatter")
            self.assertEqual(fm.get("name"), skill.parent.name, f"{skill}: name must match folder")
            desc = fm.get("description", "")
            self.assertTrue("Use this when" in desc or "Use when" in desc,
                            f"{skill}: description needs 'Use this when' / 'Use when'")

    def test_self_contained(self):
        for f in plugin_files():
            if f.suffix not in TEXT_SUFFIXES or f.resolve() == SELF:
                continue
            text = f.read_text(errors="ignore")
            for bad in FORBIDDEN:
                self.assertNotIn(bad, text, f"{f} references {bad}")

    def test_links_resolve(self):
        link_re = re.compile(r"\]\(([^)\s]+)\)")
        root_re = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s)\"'`]+)")
        for f in plugin_files("*.md"):
            text = strip_fences(f.read_text(errors="ignore"))
            for target in link_re.findall(text):
                if target.startswith(("http://", "https://")):
                    continue
                if target.startswith("${CLAUDE_PLUGIN_ROOT}/"):
                    continue
                if not target.startswith(("../", "references/")):
                    continue
                path = target.split("#", 1)[0]
                self.assertTrue((f.parent / path).exists(), f"{f}: broken link {target}")
            for rel in root_re.findall(text):
                rel = rel.split("#", 1)[0].rstrip(".,;:")
                self.assertTrue((PLUGIN_ROOT / rel).exists(), f"{f}: broken plugin-root path {rel}")

    def test_required_mentions(self):
        for rel, needles in REQUIRED_MENTIONS.items():
            path = PLUGIN_ROOT / rel
            self.assertTrue(path.is_file(), f"{rel}: required file missing")
            text = path.read_text()
            for needle in needles:
                self.assertIn(needle, text, f"{rel}: missing required text {needle!r}")

    def test_learned_clean(self):
        for f in plugin_files("LEARNED.md"):
            self.assertEqual(f.read_text().strip(), CLEAN_LEARNED, f"{f}: LEARNED.md is not clean")


if __name__ == "__main__":
    unittest.main()
