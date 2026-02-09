# Project Rules

## Pre-Push Checklist

Before committing and pushing any changes that add, modify, or remove a skill, you MUST complete every item on this checklist. Do not push until all items are verified.

### 1. Version Bump

Bump the patch version (e.g. 1.1.1 → 1.1.2) in **all three locations**:

- `plugins/lhm-marketing-hub/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `metadata.version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

All three must match.

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

### 5. Clean Up Scaffolding

Remove any placeholder/boilerplate files before committing:

- `scripts/example.py`
- `assets/example_asset.txt`
- `references/api_reference.md` (if still contains placeholder text)

Only commit files with real content.

### 6. Don't Commit Personal Files

Never stage or commit files like `to-do.md`, `.env`, or other personal/local files.

## General Rules

- Do not fabricate metrics, client data, or file contents
- Prefer editing existing files over creating new ones
- All skill outputs go to `client/skill_name/YYYY-MM/` structure
