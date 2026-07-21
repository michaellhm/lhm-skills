# Project Rules

## Pre-Push Checklist

Before committing and pushing any changes that add, modify, or remove a skill, you MUST complete every item on this checklist. Do not push until all items are verified.

### 1. Version Bump

This repo ships **six plugins** (`lhm-marketing-hub`, `lhm-wordpress-hub`, `lhm-gmb-hub`, `lhm-content-engine`, `lhm-finance-hub`, `lhm-learn`), each independently versioned. For **every plugin you added, modified, or removed a skill/agent/command in**, bump its patch version (e.g. 1.1.1 → 1.1.2) in **both** locations:

- `plugins/<plugin-name>/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → the `plugins[]` entry whose `"name"` matches `<plugin-name>` → `version`

**Match the marketplace entry by its `name` field, never by array position.** Plugin order in `marketplace.json` has been reshuffled before (`lhm-marketing-hub` used to be `plugins[0]`, it is now last) — editing "index 0" instead of the entry with the right `name` is exactly how these versions have drifted out of sync in the past.

`.claude-plugin/marketplace.json` → `metadata.version` (the top-level marketplace version) tracks **`lhm-marketing-hub` specifically**, as the flagship plugin. Only bump it when `lhm-marketing-hub` itself changes, and keep it equal to `lhm-marketing-hub`'s `plugin.json` version.

**This is enforced automatically, not just by this checklist.** `scripts/validate-plugin-versions.py` checks version consistency across all six plugins, and a pre-commit hook (`.githooks/pre-commit`, installed via `scripts/install-git-hooks.sh`) will **block the commit** if any plugin's staged changes aren't accompanied by a version bump, or if `plugin.json` and `marketplace.json` versions disagree for any plugin. A pre-push hook re-checks consistency as a safety net. If a commit gets blocked, the error message names the exact file and field to fix. Run `python3 scripts/validate-plugin-versions.py` manually any time to check the current state.

### 2. Update README.md

- Update the **skill count** in the "What This Is" paragraph
- Update the **skill count** in the directory structure comment (`# All N skills`)
- Add or remove the skill entry in the **directory structure** tree
- Add or update the skill in the **Skills Catalog** section under the correct category

### 3. Update Marketing Assistant Agent

Add or update the skill entry in `plugins/lhm-marketing-hub/agents/marketing-assistant.md` under the correct category in the **Skill Catalog** section. Format: `` `skill-folder-name` — Short description ``

### 4. Validate SKILL.md Frontmatter

Every skill must have YAML frontmatter with:

- `name` — matches the folder name
- `description` — detailed enough for Claude to trigger on it. Must include trigger phrases (e.g. "Use this when the user mentions 'campaign playbook', 'sales playbook'...")

### 5. Review and Absorb LEARNED.md Files

Before pushing, check every LEARNED.md file across all skills for accumulated learnings:

1. **Scan** all LEARNED.md files for entries: `plugins/*/skills/*/LEARNED.md`
2. **For each file with entries**:
   - Read the entries
   - Decide which learnings should be permanently baked into the skill's SKILL.md (update instructions, add warnings, adjust workflow steps, etc.)
   - Update the SKILL.md with those improvements
   - Present the changes to the user for approval
3. **Reset** each LEARNED.md back to its clean state after absorbing:
   ```
   # Learned

   <!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
   ```
4. **Skip** any LEARNED.md files that are already empty/clean

The goal: learnings get baked into the skill permanently, LEARNED.md files go to git clean, and skills get smarter with every push.

### 6. Clean Up Scaffolding

Remove any placeholder/boilerplate files before committing:

- `scripts/example.py`
- `assets/example_asset.txt`
- `references/api_reference.md` (if still contains placeholder text)

Only commit files with real content.

### 7. Don't Commit Personal Files

Never stage or commit files like `to-do.md`, `.env`, or other personal/local files.

## General Rules

- Do not fabricate metrics, client data, or file contents
- Prefer editing existing files over creating new ones
- All skill outputs go to `client/skill_name/YYYY-MM/` structure
