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
