# LHM Astro Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a self-contained `lhm-astro-hub` plugin that runs LHM's Astro website process from sitemap to prototype, build, client brain, content rounds, client review and brain updates.

**Architecture:** This is a new plugin folder, `plugins/lhm-astro-hub/`. It holds copied-and-adapted skills from `lhm-wordpress-hub`, `lhm-marketing-hub`, `lhm-project-hub` and the unmerged `feat/client-review-release` branch, plus new skills for the brain.

- **Agents:** one lead agent (`astro-lead`) routes the stages, and a copied `content` agent writes the pages.
- **Small Python scripts** handle the checkable parts: the sitemap fields, the client repo scaffold, the brain check, client commit discovery, stage detection and the inline-asset check. Each has `unittest` tests.
- **A plugin structure test** enforces that the plugin is self-contained: no paths into other plugins, every link resolves, and the frontmatter is valid.

**Tech Stack:** Markdown skills and agents (Claude Code plugin format), Python 3.10+ standard library only, `unittest` (pytest is not installed), git, `gh`, Astro, Cloudflare Pages.

**Spec:** `docs/superpowers/specs/2026-11-25-lhm-astro-hub-design.md`. Read it before any task. Every task argues from it.

## Global Constraints

- **Workspace.** Work in a fresh worktree on branch `feat/lhm-astro-hub`, cut from `main`. The main checkout has unrelated uncommitted work. Copy the spec into the worktree and commit it in Task 1.
- **Plugin name:** `lhm-astro-hub`. Location: `plugins/lhm-astro-hub/`.
- **Versions.** Task 1 creates version `0.1.0` in both `plugins/lhm-astro-hub/.claude-plugin/plugin.json` and the `.claude-plugin/marketplace.json` entry whose `"name"` is `lhm-astro-hub`. Match by name, never by index. Every later task bumps the patch in both places. The pre-commit hook `scripts/validate-plugin-versions.py --bump-check` blocks the commit otherwise. Task 12 sets `1.0.0`. Do not touch `metadata.version`.
- **Self-contained.** No file in `plugins/lhm-astro-hub/` may reference `lhm-marketing-hub`, `lhm-wordpress-hub`, `lhm-project-hub` or `lhm-client-updates-hub`, either as a path (`../lhm-…`) or as a skill name (`lhm-marketing-hub:content`). The only outside plugin a skill may call by name is `ui-ux-pro-max`.
- **No other plugin is changed.** Leave `lhm-wordpress-hub`, `lhm-marketing-hub` and the rest as they are. The repo-level edits allowed are `marketplace.json`, `README.md` and `CLAUDE.md`. There is one exception, in Task 12: a catalogue line in `plugins/lhm-marketing-hub/agents/marketing-assistant.md` plus that plugin's version bump, because the CLAUDE.md checklist requires it.
- **No CMS.** Nothing about Decap CMS is carried over.
- **Client repo layout:** `README.md`, `brain/`, `skills/` and `site/`, exactly as in the spec. Cloudflare Pages builds from `site/`.
- **Brain notes**, with these exact file names: `Overview.md`, `Profile.md`, `Project.md`, `Services.md`, `Staff.md`, `What We Do.md`, `Who We Serve.md`, `Brand.md`, `Content Rules.md`, `Change Log.md`.
- **Push to `main`.** During staging, content rounds and client edits push to `main`. There are no round or review branches.
- **The brain learns only from the client.** It learns only from commits made by the client's GitHub identity.
- **Copy rules** carried from the source skills: Australian English, no em or en dashes in customer copy, `anti-ai-writing-guidelines.json`, the 8-pass engine for page copy, no invented facts, prices, staff or results, and AHPRA rules where they apply.
- **Approval stops**, from the spec's list: sitemap, prototype, production deploy, brain draft, each round's page list and template plus the mock-up-or-batch choice, each client email before sending, and each brain update proposal.
- **Every `SKILL.md`** carries frontmatter `name` equal to its folder name, and a `description` that contains trigger phrases ("Use this when …").
- **Every copied skill gets a clean `LEARNED.md`.** First fold any useful entries from the source `LEARNED.md` into the new `SKILL.md`, then reset `LEARNED.md` to:
  ```
  # Learned

  <!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
  ```
- **Test runner.** Skill folders have hyphens, so they can't be packages, and `discover` won't recurse into them. Run each `tests/` folder on its own:
  ```bash
  for d in plugins/lhm-astro-hub/tests plugins/lhm-astro-hub/skills/*/tests; do python3 -m unittest discover -s "$d" -p 'test_*.py' || exit 1; done
  ```
  Below, "run the tests" means this loop. A task's own folder can be run alone with `-s plugins/lhm-astro-hub/skills/<skill>/tests`. Tests import their scripts by file path with `importlib.util.spec_from_file_location`, the same pattern as the existing `test_review_release.py`. Task 8's and Task 11's tests import `scaffold_client_repo.py` and `check_brain.py` the same way.

## Review Focus

1. **A client repo that already has files.** Running setup or install twice, or on a repo with an existing README, must never overwrite client content. It must refuse, or add only what's missing. Task 4 and Task 5 cover this.
2. **Commits from the client mixed with LHM's on `main`.** The brain must ignore LHM's commits even when they are interleaved, and must ignore merge commits. Task 9 covers this.
3. **A Change Log with no "last processed" marker**, which is the first brain update. All of the client's commits should be read, not none and not a crash. Task 9 covers this.
4. **A sitemap page missing keyword or audience fields.** It must be reported by name before a brief is seeded, not silently given empty fields. Task 3 covers this.
5. **A prototype with inline `style=` or `<script>` blocks.** It must fail the check, and say which file and line. Task 6 covers this.

---

## File structure

```
plugins/lhm-astro-hub/
  .claude-plugin/plugin.json
  agents/astro-lead.md                       Task 11
  agents/content.md                          Task 10
  commands/start-astro.md                    Task 11
  learnings/{content,seo}-learned.md         Task 2
  references/                                Task 2
    obsidian-context-contract.md  astro-build-standard.md  anti-ai-writing-guidelines.json
    8-pass-writing-engine.md  content-departmental-delivery.md  seo-departmental-delivery.md
    delivery-artifact-contract.md  agent-orchestration-contract.md  website-departmental-delivery.md
    context-preamble.md  self-improvement-protocol.md  lhm-philosophy/{content,seo}.md
  tests/test_plugin_structure.py             Task 1 (grows in later tasks)
  skills/
    astro-sitemap/        Task 3   (from marketing-hub client-sitemap-plan)
    client-repo-setup/    Task 4   (new + repo-init)
    client-review-release/Task 5   (from feat/client-review-release)
    astro-prototype/      Task 6   (from html-prototype + start-prototype)
    astro-build/ astro-form/ site-launch-qa/ website-delivery-qa/   Task 7
    build-brain/          Task 8   (new)
    update-content-brain/ Task 9   (new)
    content-rollout/ seo-page-brief/ seo-content-writer/ copywriting/
      content-quality-auditor/ seo-delivery-qa/ keyword-research/
      taya-question-discovery/ client-update-email/            Task 10
    start-astro/          Task 11
```

---

### Task 1: Plugin skeleton and structure test

**Files:**
- Create: `plugins/lhm-astro-hub/.claude-plugin/plugin.json`
- Create: `plugins/lhm-astro-hub/tests/test_plugin_structure.py`
- Modify: `.claude-plugin/marketplace.json`, adding an entry with `"name": "lhm-astro-hub"` and `"source": "./plugins/lhm-astro-hub"`
- Modify: `CLAUDE.md`. Section 1 lists the plugins and is out of date: list every folder in `plugins/` that has a `plugin.json`, including `lhm-astro-hub`, and drop the word "nine".
- Add: `docs/superpowers/specs/2026-11-25-lhm-astro-hub-design.md` and this plan, copied into the worktree.

**Interfaces:**
- Produces: `test_plugin_structure.py` with module constants that later tasks extend:
  - `FORBIDDEN = ["lhm-marketing-hub", "lhm-wordpress-hub", "lhm-project-hub", "lhm-client-updates-hub"]`
  - `REQUIRED_MENTIONS: dict[str, list[str]] = {}`, which maps a path relative to the plugin root to the strings that file must contain.

- [ ] **Step 1: Write the failing tests** in `test_plugin_structure.py`. Each test must pass on an empty `skills/` folder and fail with the offending file named.
  - `test_manifest_matches_marketplace`: `plugin.json` has `name == "lhm-astro-hub"`, and its version equals the marketplace entry's version.
  - `test_skill_frontmatter`: for each `skills/*/SKILL.md`, the frontmatter `name` equals the folder name, and `"Use this when"` or `"Use when"` appears in `description`.
  - `test_self_contained`: no text file under the plugin contains any `FORBIDDEN` string. Exclude only `tests/test_plugin_structure.py` itself.
  - The checks find their files by walking `plugins/lhm-astro-hub/` with `Path.rglob`, not by importing the skills.
  - `test_links_resolve`: every `${CLAUDE_PLUGIN_ROOT}/<path>` resolves under the plugin root, and every relative Markdown link `](../…)` or `](references/…)` resolves from the file's own folder.
  - `test_required_mentions`: for each `REQUIRED_MENTIONS` key, the file exists and contains every listed string.
  - `test_learned_clean`: every `LEARNED.md` equals the clean template from Global Constraints, after stripping whitespace.
- [ ] **Step 2: Run** `python3 -m unittest discover -s plugins/lhm-astro-hub -p 'test_*.py'`. Expected: FAIL, because `plugin.json` is missing.
- [ ] **Step 3: Create `plugin.json`.** Set version `0.1.0`, author `LHM Digital`, keywords `astro, cloudflare, website-builder, client-brain, agency`, and description "Astro website delivery: sitemap, UI UX Pro Max prototype, Astro build, client brain, content rounds and client review." Add the marketplace entry and make the `CLAUDE.md` edit.
- [ ] **Step 4: Run the tests and `python3 scripts/validate-plugin-versions.py`.** Expected: both pass.
- [ ] **Step 5: Commit**: `feat(astro-hub): plugin skeleton and structure test`.

### Task 2: Shared references

**Files:**
- Create, copying from the sources below: every file listed under `references/` and `learnings/` in the file structure.
  - From `plugins/lhm-wordpress-hub/references/`: `obsidian-context-contract.md`, `astro-build-standard.md` and `website-departmental-delivery.md`.
  - From `plugins/lhm-marketing-hub/references/`: everything else.
  - `learnings/content-learned.md` and `learnings/seo-learned.md` come from `plugins/lhm-marketing-hub/learnings/`.
- Modify: `plugin.json` and `marketplace.json`, bumping to 0.1.1.

- [ ] **Step 1: Copy the files.** Run the tests. Expected: FAIL at `test_self_contained`, or at `test_links_resolve` wherever the copies point into other plugins or at WordPress-only references.
- [ ] **Step 2: Edit the copies** until both tests pass.
  - Replace cross-plugin paths with `${CLAUDE_PLUGIN_ROOT}/references/…`.
  - In `website-departmental-delivery.md` and `agent-orchestration-contract.md`, remove the WordPress lead and lane routing, and name `astro-lead` as the website lead.
  - Remove any Decap CMS mention from `astro-build-standard.md`.
- [ ] **Step 3: Run the tests.** Expected: PASS.
- [ ] **Step 4: Commit**: `feat(astro-hub): shared references`.

### Task 3: `astro-sitemap` with keyword and audience fields

**Files:**
- Create: `skills/astro-sitemap/`, copied from `plugins/lhm-marketing-hub/skills/client-sitemap-plan/` (`SKILL.md`, `assets/`, `references/` and `scripts/`).
- Create: `skills/astro-sitemap/scripts/page_brief_seed.py`
- Modify: `scripts/build_sitemap_html.py` (`page_li`) and `scripts/build_workbook.py` (`build`)
- Modify: `references/sitemap-schema.md`, adding the new page fields to the table.
- Test: `skills/astro-sitemap/tests/test_sitemap_fields.py`

These scripts are a deliberate fork. Do **not** add them to `PARITY_GROUPS` in `scripts/validate-script-parity.py`.

**Interfaces:**
- New page fields in `sitemap.json`:
  - `primary_keyword: str`
  - `secondary_keywords: list[str]`
  - `audience: str`
  - `intent: "informational" | "commercial" | "transactional"`
  - `h1: str`, optional. `content-rollout`, which is built on `website-content-agent`, uses it as the intended H1. When it's absent, the primary keyword is the H1.
  - `template: str`, optional: the prototype page this page is built from
- Produces, in `page_brief_seed.py`:
  - `missing_brief_fields(spec: dict) -> list[str]` returns `"<page name>: <field>"` for each page whose `status` is `new` or `enh` and that lacks `primary_keyword`, `audience` or `intent`.
  - `seed(spec: dict, page_name: str) -> dict` returns `{"page": name, "slug", "primary_keyword", "secondary_keywords", "audience", "intent", "h1", "template", "section": section title}`. It raises `KeyError` naming the page when the name isn't found.
  - CLI: `python3 page_brief_seed.py sitemap.json "<page name>"` prints the seed as JSON. With `--check`, it prints the missing fields and exits 1 if there are any.

- [ ] **Step 1: Write the failing tests.**
  - `test_missing_fields_named`: a spec with one `new` page that lacks `audience` returns `["<name>: audience"]`. A `have` page with no fields returns `[]`.
  - `test_seed_returns_fields`: the values from `assets/example-sitemap.json` come back as listed.
  - `test_seed_unknown_page`: raises `KeyError`.
  - `test_html_shows_keyword`: `build_sitemap_html.build(spec)` contains `class="kw"` and the primary keyword text for a page that has one, and stays unchanged for a page without one.
  - `test_workbook_columns`: the first sheet's header row contains `Primary keyword`, `Secondary keywords`, `Audience` and `Intent`. Skip this test if `openpyxl` is not installed.
- [ ] **Step 2: Run the tests.** Expected: FAIL.
- [ ] **Step 3: Implement.**
  - In `page_li`, add `<span class="kw">{primary_keyword}</span>` after the slug when it's present, and add the `.kw` CSS beside `.u2`.
  - In the workbook, add the four columns after Volume. Join `secondary_keywords` with `", "`.
  - Write `page_brief_seed.py`.
  - Add keyword, audience and intent to every `new` or `enh` page in `assets/example-sitemap.json`.
- [ ] **Step 4: Update `SKILL.md`.**
  - Set the name to `astro-sitemap`.
  - Remove prospect and opportunity mode.
  - Add a step: research and record the four fields for each new or enhanced page, using `keyword-research` (Task 10) for demand.
  - Add a step: run `page_brief_seed.py --check` before asking for sitemap approval. The sitemap isn't approvable while the check reports missing fields.
  - Make the output path follow the routing contract.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): astro-sitemap with brief fields`.

### Task 4: `client-repo-setup` and the client repo scaffold

**Files:**
- Create: `skills/client-repo-setup/SKILL.md`, adapted from `plugins/lhm-wordpress-hub/skills/repo-init/SKILL.md`. It creates **one** repo, `<client-slug>`, not `-site` plus `-prototype`.
- Create: `skills/client-repo-setup/scripts/scaffold_client_repo.py`
- Create: `skills/client-repo-setup/assets/`
  - `README.md`
  - `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`
  - `brain/<each of the 10 notes>.md`
  - `site/.gitkeep` and `skills/.gitkeep`
- Test: `skills/client-repo-setup/tests/test_scaffold.py`

**Interfaces:**
- Produces: `scaffold(root: Path, client_name: str, client_slug: str) -> list[str]`, which returns the relative paths it wrote. Templates replace `{{client_name}}` and `{{client_slug}}`. If any target file already exists, it raises `FileExistsError` listing every existing path, and writes nothing.
- CLI: `python3 scaffold_client_repo.py --root PATH --client-name NAME --client-slug SLUG`
- Every brain note template starts with this frontmatter:
  ```yaml
  ---
  type: <overview|profile|project|services|staff|what-we-do|who-we-serve|brand|content-rules|change-log>
  client: "{{client_name}}"
  updated: YYYY-MM-DD
  sources: []
  ---
  ```
  It is followed by headed sections whose bodies are `> gap: not yet captured`.
  - `Overview.md` links every other note with `[[Note Name]]`.
  - `Change Log.md` ends with `<!-- last-processed: none -->`.
- `README.md` is addressed to an AI assistant. In under 60 lines it gives:
  - what the repo is
  - prerequisites (Git, the Node version in `site/package.json`, Python 3.10+)
  - steps for Mac and Windows to clone and run `site/`
  - one short block each for ChatGPT (Codex app), Claude (Claude Code or desktop) and Gemini (Gemini CLI)
  - a pointer to `brain/Overview.md` and to `skills/`
  - a rule never to paste passwords or tokens into chat
- `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` each say in under 10 lines: read `README.md`, read `brain/Overview.md` before any content work, follow `brain/Content Rules.md` when writing, and find the skills in `skills/`.

- [ ] **Step 1: Write the failing tests.**
  - `test_scaffold_writes_layout`: on an empty temp dir, the call returns paths that include `README.md`, all 10 brain notes, `site/.gitkeep`, `skills/.gitkeep`, `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`. `{{client_name}}` is replaced everywhere.
  - `test_overview_links_every_note`: `brain/Overview.md` contains `[[X]]` for each of the other 9 notes.
  - `test_existing_file_refused`: pre-create `README.md`, then the call raises `FileExistsError` mentioning `README.md`, and no other file was written.
  - `test_changelog_marker`: `Change Log.md` contains `<!-- last-processed: none -->`.
- [ ] **Step 2: Run the tests.** Expected: FAIL.
- [ ] **Step 3: Write the templates and `scaffold()`.**
- [ ] **Step 4: Write `SKILL.md`.**
  1. `gh auth status`.
  2. Confirm the GitHub owner and slug with the user.
  3. `gh repo create <owner>/<slug> --private`.
  4. Clone to `~/Documents/Projects/<client>/<slug>/`.
  5. Run the scaffold.
  6. Commit and push to `main`.
  7. Record the repo URL in the internal vault client overview, per the routing contract.

  The skill runs at project start, before the prototype.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): client repo setup and scaffold`.

### Task 5: `client-review-release` adapted to the new layout

**Files:**
- Create: `skills/client-review-release/`. Copy it from branch `feat/client-review-release`, path `plugins/lhm-wordpress-hub/skills/client-review-release/`, using `git show feat/client-review-release:<path>` or `git checkout feat/client-review-release -- <path>`, then move it. Take only this folder.
- Modify: `scripts/review_release.py`:
  - `REGISTER = '.lhm-review/client-review.json'`
  - `PROJECT = 'brain/Project.md'`
  - `render_project`
- Modify: `scripts/install_kit.py`, `references/client-workflows.md`, `references/client-invitation.md`, `assets/skills/*/SKILL.md` and `assets/README-client.md`
- Test: `skills/client-review-release/tests/test_review_release.py`, copied then updated.

**Interfaces:**
- Consumes: the brain note frontmatter from Task 4. `render_project` writes `brain/Project.md` with `type: project` frontmatter.
- Produces:
  - `render_project(reg) -> str` groups pages under `## Round <release id>` headings, in release order. Each line reads `- [x] <route> — approved` or `- [ ] <route> — awaiting client review`.
  - `install(root, approval_evidence)` writes the canonical client skills to `skills/<name>/SKILL.md`. It writes a 3-line pointer `SKILL.md` to `.claude/skills/<name>/` and `.agents/skills/<name>/` that says "Read and follow `skills/<name>/SKILL.md`". It no longer writes its own README section, because `README.md` comes from Task 4.

- [ ] **Step 1: Update the tests.** Change every `CLIENT-REVIEW.md` path to `brain/Project.md` and every `client-review.json` path to `.lhm-review/client-review.json`, then add:
  - `test_project_grouped_by_round`: two applied releases, `round-1` and `round-2`, render two `## Round` headings in order, each listing its own routes.
  - `test_install_canonical_skills_folder`: after `install`, `skills/review-website/SKILL.md` exists, and `.claude/skills/review-website/SKILL.md` contains `skills/review-website/SKILL.md`.
  - `test_install_keeps_existing_project_md`: an existing `brain/Project.md` written by the scaffold is replaced only by `apply`, never by `install`.
- [ ] **Step 2: Run the tests.** Expected: the new and renamed tests FAIL.
- [ ] **Step 3: Implement the constant, render and install changes.**
- [ ] **Step 4: Rewrite the workflow text.**
  - `share-preview` and `finish-review` commit and push to `main` while the site is in staging. There are no review branches.
  - `start-website` and `review-website` read `brain/Project.md` first.
  - `finish-review` drafts the email to LHM.
  - Remove every "review branch" and "PR" instruction.
  - Keep: never reset or force-push, preserve unfinished changes, and never infer approval.
  - Use `client-invitation.md` for the client email prompt that the content round sends.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): client review toolkit on brain/Project.md`.

### Task 6: `astro-prototype` with UI UX Pro Max

**Files:**
- Create: `skills/astro-prototype/SKILL.md`, merging `plugins/lhm-wordpress-hub/skills/html-prototype/SKILL.md` and `start-prototype/SKILL.md`.
- Create: `skills/astro-prototype/scripts/check_no_inline.py`
- Test: `skills/astro-prototype/tests/test_check_no_inline.py`

**Interfaces:**
- Produces:
  - `find_inline(prototype_dir: Path) -> list[str]` returns `"<relative file>:<line>: <reason>"` for each of these in any `.html` file:
    - a `<style` tag
    - a ` style="` attribute
    - a `<script` tag without `src=`

    It ignores `<script type="application/ld+json">`.
  - CLI: exit 1 and print the findings if there are any.
- Adds `REQUIRED_MENTIONS["skills/astro-prototype/SKILL.md"] = ["ui-ux-pro-max", "brain/Brand.md", "lhm-prototype", "check_no_inline.py"]`.

- [ ] **Step 1: Write the failing tests.**
  - `test_clean_prototype_passes`: `index.html` linking `assets/css/style.css` and `assets/js/main.js` returns `[]`.
  - `test_inline_style_attr_flagged`: returns `index.html:3: inline style attribute`.
  - `test_style_block_flagged`.
  - `test_inline_script_flagged`.
  - `test_jsonld_allowed`.
- [ ] **Step 2: Run the tests.** Expected: FAIL.
- [ ] **Step 3: Implement `find_inline` and the CLI.**
- [ ] **Step 4: Write `SKILL.md`.**
  1. Read the approved sitemap (Task 3).
  2. **Required:** run UI UX Pro Max's design-system step (`ui-ux-pro-max` skill, `search.py --design-system`). Record an adopt, override or reject table. For existing clients, keep their established brand tokens. For AHPRA-regulated clients, reject testimonial and social-proof patterns. This absorbs the `html-prototype` LEARNED entries.
  3. Build plain HTML, with every page as `<slug>/index.html` (or `v1.html`, `v2.html` and so on), plus `assets/css/`, `assets/js/` and `assets/images/`.
  4. Run `check_no_inline.py`. It must pass.
  5. Write the UI UX Pro Max style guide (colours, type, spacing, components, do's and don'ts, and the adopt/override/reject table) to the client repo as `brain/Brand.md`, keeping its frontmatter, then commit and push.
  6. Push the prototype to `github.com/michaellhm/lhm-prototype` under `<client>/`, after explicit approval to publish.
  7. Stop for client approval of the prototype and its copy.

  Add `REQUIRED_MENTIONS` to the structure test.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): astro-prototype with UI UX Pro Max and inline check`.

### Task 7: Astro build, form and QA

**Files:**
- Create: copy each of these from `plugins/lhm-wordpress-hub/skills/` and adapt:
  - `skills/astro-build/`
  - `skills/site-launch-qa/` (keep only `references/checklist-astro.md`)
  - `skills/website-delivery-qa/`
- Create: `skills/astro-form/`, copied from `contact-form-submissions/` (all its references), plus a new `references/gohighlevel.md`.
- Modify: `tests/test_plugin_structure.py`, adding the `REQUIRED_MENTIONS` below.

**Interfaces:**
- `REQUIRED_MENTIONS`:
  - `skills/astro-build/SKILL.md`: `["site/", "astro-build-standard.md", "astro-form"]`
  - `skills/astro-form/SKILL.md`: `["GoHighLevel", "D1", "Turnstile"]`
  - `skills/astro-form/references/gohighlevel.md`: `["GHL_WEBHOOK_URL", "never commit"]`

- [ ] **Step 1: Add the mentions.** Run the tests. Expected: FAIL, because the files are missing.
- [ ] **Step 2: Adapt `astro-build`.**
  - The project lives in `site/` of the client repo, not `<client>-site`.
  - The platform check against `client_profile.md` is removed, because this plugin is Astro only.
  - The Cloudflare Pages root directory is `site`.
  - Ask the form question and call `astro-form`.
  - No CMS step.
  - Deploy to production only after approval.
  - Copy `astro-build`'s LEARNED entries into the `SKILL.md`.
- [ ] **Step 3: Adapt the QA skills.** In `site-launch-qa` and `website-delivery-qa`, drop the WordPress checklist and the WordPress and project-hub routing, and point the paths at `site/`.
- [ ] **Step 4: Write `astro-form`.**
  1. Ask: "Does the client have a GoHighLevel account?"
  2. **If yes:** Turnstile-checked Pages Function → POST JSON to the GoHighLevel inbound webhook. The client's Workflow uses the "Inbound Webhook" trigger. The URL lives in Cloudflare secret `GHL_WEBHOOK_URL`, which is set with `wrangler pages secret put`. Never commit it. Fallback: if the client's plan lacks inbound webhooks, use API v2 contact upsert with secret `GHL_PRIVATE_TOKEN`.
  3. **If no:** the existing D1 flow.
  4. **Both paths:** the thank-you page and GA tracking.
  5. LHM does the GoHighLevel setup. The client never does.

  Write this flow in `references/gohighlevel.md`. Merge in `contact-form-submissions`' LEARNED entries.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): astro build, form and QA`.

### Task 8: `build-brain`

**Files:**
- Create: `skills/build-brain/SKILL.md`
- Create: `skills/build-brain/references/extraction-categories.md`, built from the extraction categories in `plugins/lhm-marketing-hub/skills/campaign-playbook-generator/SKILL.md` Step 2, each mapped to its target note.
- Create: `skills/build-brain/scripts/check_brain.py`
- Test: `skills/build-brain/tests/test_check_brain.py`

**Interfaces:**
- Consumes: the note names and frontmatter from Task 4.
- Produces: `check_brain(brain_dir: Path) -> list[str]` returns problems, each prefixed with the file name. A note is a problem when it:
  - is missing
  - is missing a frontmatter key (`type`, `client`, `updated`, `sources`)
  - has an empty `sources` list when its body has no `> gap:` line, meaning it claims facts without a source

  `Overview.md` is also a problem when it is missing a `[[link]]` to any note.

  `Overview.md`, `Project.md` and `Change Log.md` are exempt from the "facts without sources" rule. They are navigation, state and log, not facts.

  CLI: exit 1 if there are problems. Task 9 and Task 11 also call it.

- [ ] **Step 1: Write the failing tests.**
  - `test_scaffolded_brain_passes`: run `scaffold()` from Task 4 into a temp dir, then `check_brain` returns `[]`.
  - `test_missing_note`: delete `Staff.md`, and the result includes `Staff.md: missing`.
  - `test_unsourced_facts`: replace `Services.md`'s gap with text and keep `sources: []`, and the result includes `Services.md: facts without sources`.
  - `test_overview_missing_link`.
- [ ] **Step 2: Run the tests.** Expected: FAIL.
- [ ] **Step 3: Implement `check_brain`.** Parse the frontmatter with a small hand parser between the `---` lines. The standard library has no YAML module.
- [ ] **Step 4: Write `SKILL.md`.** It reads:
  - the client's Fathom calls (Fathom connector: `search_meetings`, `get_meeting_transcript`)
  - the approved prototype copy
  - `brain/Brand.md`
  - the internal vault overview

  Then it fills the notes per `extraction-categories.md`:
  - mission, vision, values, founder story and positioning → `Profile.md`
  - voice notes → `Content Rules.md`
  - `Change Log.md` gets a "brain created" entry
  - `Project.md` is left to Task 5's `apply`

  Every fact lists its source in `sources`. Unknowns stay `> gap:`. Show the draft, stop for approval, then run `check_brain`, commit and push. Afterwards, add a link to the brain in the internal vault client overview, with no copied facts.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): build-brain and brain check`.

### Task 9: `update-content-brain` (from `client-content-learn`)

**Source:** `plugins/lhm-marketing-hub/skills/client-content-learn/` on `main`. This is the existing skill that learns a client's writing guide from approved pages and client GitHub edits. Copy it and retarget its output to the brain.

**Files:**
- Create: `skills/update-content-brain/`
  - copied from `client-content-learn/`: `SKILL.md`, `references/output-contract.md`, `scripts/collect_evidence.py` and `tests/test_collect_evidence.py`
- Create: `skills/update-content-brain/scripts/brain_cursor.py`
- Test: `skills/update-content-brain/tests/test_brain_cursor.py`

**Interfaces:**
- `collect_evidence.py` is unchanged in behaviour. Its copied tests must pass as-is, and its `collect(repo, manifest, since, head, emails)` and CLI are kept.
- Produces, in `brain_cursor.py`:
  - `last_processed(changelog_text: str) -> str | None` reads the final `<!-- last-processed: <sha|none> -->` marker. `none`, or no marker, returns `None`.
  - `set_marker(changelog_text: str, sha: str) -> str` replaces the marker, or appends one if there's none. Exactly one marker remains.

- [ ] **Step 1: Copy the four files.** Write `test_brain_cursor.py` with these tests:
  - `test_marker_none`: `last_processed` of `"x\n<!-- last-processed: none -->"` is `None`.
  - `test_marker_absent`: `last_processed("")` is `None`.
  - `test_marker_sha`: returns `"abc123"`.
  - `test_set_marker_replaces`: only one marker remains, and it holds the new SHA.
  - `test_set_marker_appends`.
- [ ] **Step 2: Run the update-content-brain tests.** Expected: the copied collector tests PASS, and the cursor tests FAIL.
- [ ] **Step 3: Implement `brain_cursor.py`.**
- [ ] **Step 4: Retarget `SKILL.md`** (name `update-content-brain`). Keep its evidence discipline: approval evidence, client identities, semantic diffs, rule statuses, dedupe, the healthcare caveat and the "no new evidence means no change" rule. Change where its output goes:
  - **Writing lessons** go to `brain/Content Rules.md`, not `how-to-write.md` or `client-learnings.md`. Each rule keeps a stable ID, scope, status (`confirmed instruction`, `observed pattern`, `proposed` or `superseded`), the before/after evidence with its SHA, and the implication. Update `output-contract.md` to match.
  - **Scoped facts** (staff, prices, services, hours) update the matching brain note, with the SHA and date in `sources`.
  - **Presentation and functionality preferences** go in their own section of `Content Rules.md`.
  - **Each run** adds a `brain/Change Log.md` entry, and its cursor is the `<!-- last-processed: <sha> -->` marker, maintained through `brain_cursor.py`.
  - **Approvals** come from the register `.lhm-review/client-review.json` (Task 5). The client identity comes from `.lhm-review/client-config.json`.
  - **Only the client's commits** count as learning evidence: only commits by the client's GitHub identity, per Michael's decision.
  - **The detailed evidence pack** goes to the registered client work root, not the client repo.
  - **Process:** show the proposed brain changes and stop for approval. Then write them, run `check_brain` (Task 8), commit as LHM, push to `main` and update the internal vault project file.
  - Replace the references to `website-content-agent` with `content-rollout`.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): update-content-brain from client-content-learn`.

### Task 10: Content writing chain and `content-rollout`

**Files:**
- Create: `agents/content.md`, copied from `plugins/lhm-marketing-hub/agents/content.md`.
- Create: copy each of these and adapt:
  - from `plugins/lhm-marketing-hub/skills/`: `seo-page-brief/`, `seo-content-writer/`, `copywriting/`, `content-quality-auditor/`, `seo-delivery-qa/`, `keyword-research/` and `taya-question-discovery/`
  - from `plugins/lhm-project-hub/skills/`: `client-update-email/`
- Create: `skills/content-rollout/`, copied from `plugins/lhm-marketing-hub/skills/website-content-agent/` (`SKILL.md` and `references/project-state.md` and `references/agent-handoffs.md`). That is the existing content flow, and it already asks for the template page and takes SEO from the sitemap. Add the deploy-verify and email steps from `plugins/lhm-marketing-hub/skills/lhm-page-rollout/SKILL.md`.
- Modify: `tests/test_plugin_structure.py`

**Interfaces:**
- Consumes:
  - `page_brief_seed.py` (Task 3)
  - `review_release.py scan/apply` (Task 5)
  - `client-invitation.md` (Task 5)
  - `check_no_inline.py` is not used here
- `REQUIRED_MENTIONS`:
  - `agents/content.md`: `["brain/Content Rules.md"]`
  - `skills/content-rollout/SKILL.md`: `["brain/Content Rules.md", "page_brief_seed.py", "review_release.py", "brain/Project.md", "client-update-email", "mock-up"]`
  - `skills/seo-content-writer/SKILL.md` and `skills/copywriting/SKILL.md`: `["brain/Content Rules.md"]`

- [ ] **Step 1: Add the mentions.** Run the tests. Expected: FAIL.
- [ ] **Step 2: Copy and adapt the chain.**
  - Rewrite `lhm-marketing-hub:` skill names to the local names.
  - Point the paths at `${CLAUDE_PLUGIN_ROOT}/references/` and `${CLAUDE_PLUGIN_ROOT}/learnings/`.
  - In `content.md`, `seo-content-writer` and `copywriting`, add the first context step: "Read `brain/Overview.md`, `brain/Profile.md` and `brain/Content Rules.md` from the client repo; every rule in Content Rules is mandatory." The brain replaces `client_profile.md` and `playbook.md` as the voice source.
  - Absorb the LEARNED entries, and write clean `LEARNED.md` files.
- [ ] **Step 3: Adapt `content-rollout/SKILL.md`** (name `content-rollout`). Keep `website-content-agent`'s template selection, SEO-from-sitemap rules, staged subagent handoffs, editor and healthcare review, and recovery tracking. Then make these changes:
  - The client-facing checklist is `brain/Project.md`, rendered by `review_release.py`. The internal state files (`project.md`, `content-plan.json` and `.md`, `action-plan.md`, `templates/` and `pages/<page-key>/`) live in the registered client work root, not the client repo.
  - `how-to-write.md` and `client-learnings.md` are replaced by `brain/Content Rules.md`.
  - Run `update-content-brain` first if client commits exist past the Change Log cursor.
  - Publishing pushes to `main` during staging.

  The round flow is:
  1. Ask which pages this round covers and which template, meaning a prototype page such as a service overview or condition page.
  2. Run `page_brief_seed.py --check` for those pages, and fix any gaps first.
  3. Propose the round: N pages, in order, with the template.
  4. Ask: "Would you like me to make the first page as a mock-up for you to approve, or batch the lot?"
  5. **For each page**, through `agents/content.md`:
     - seed → brief (`seo-page-brief`) → write (8-pass) → `content-quality-auditor` → integrate into `site/` → `npm run build` → push to `main` → wait for a successful Cloudflare deploy → curl each URL for 200
  6. Run `review_release.py scan`, show the proposal and get approval, then run `apply` with release id `round-<n>`. This updates `brain/Project.md`.
  7. Draft the client email with `client-update-email` and `client-invitation.md`. It includes the preview links and the copyable prompt to run `review-website`. **Draft only**: send only on explicit approval.
  8. Update the internal vault project file.

  Carry over from `lhm-page-rollout`:
  - the FAQ format
  - the internal links rules
  - the image reuse rules
  - the verify-after-deploy rules
  - the pitfalls

  Remove the LHM-specific repo facts. For brain gaps, use fallback wording and add the question to the email. Never invent.
- [ ] **Step 4: Run the tests.** Expected: PASS.
- [ ] **Step 5: Commit**, with a patch bump: `feat(astro-hub): content chain and content-rollout`.

### Task 11: `astro-lead`, `start-astro` and stage detection

**Files:**
- Create: `agents/astro-lead.md`, built from `plugins/lhm-wordpress-hub/agents/astro-lead.md` and `website-build-orchestrator.md`, with the WordPress routing removed.
- Create: `commands/start-astro.md`, which loads `agents/astro-lead.md` (same pattern as `plugins/lhm-marketing-hub/commands/start-content.md`).
- Create: `skills/start-astro/SKILL.md`
- Create: `skills/start-astro/scripts/detect_stage.py`
- Test: `skills/start-astro/tests/test_detect_stage.py`

**Interfaces:**
- Consumes: `check_brain` (Task 8), and the register at `.lhm-review/client-review.json` (Task 5).
- Produces: `repo_facts(repo: Path) -> dict` with:
  - `"brain_scaffolded": bool`: `brain/Overview.md` exists
  - `"brand_written": bool`: `Brand.md` has no `> gap:` lines
  - `"site_built": bool`: `site/package.json` exists
  - `"brain_built": bool`: `check_brain` is clean and `Profile.md` has no gaps
  - `"rounds": [release ids]`
  - `"awaiting_review": int`
  - `"unprocessed_client_commits": bool | None`: `None` when no client identity is recorded

  `next_stage(facts: dict) -> str` returns the first true condition in this order:

  | Condition | Returns |
  |---|---|
  | not `brain_scaffolded` | `repo-setup` |
  | not `brand_written` | `prototype` |
  | not `site_built` | `astro-build` |
  | not `brain_built` | `build-brain` |
  | `unprocessed_client_commits` | `update-content-brain` |
  | `awaiting_review > 0` | `client-review` |
  | otherwise | `content-round` |

  The sitemap stage is not in this table, because the sitemap is a work-folder artefact and the internal project file tracks it. Before `repo-setup`, `astro-lead` checks the internal file for an approved sitemap.

- [ ] **Step 1: Write the failing tests.** Build temp repos with `scaffold()` and assert `next_stage` for each row of the table. Also:
  - `test_none_identity_skips_brain_update`: `unprocessed_client_commits=None`, with everything else done, returns `content-round`.
- [ ] **Step 2: Run the tests.** Expected: FAIL.
- [ ] **Step 3: Implement `repo_facts`, `next_stage` and a CLI** that prints both as JSON.
- [ ] **Step 4: Write `astro-lead.md` and `start-astro/SKILL.md`.**
  - **Read:**
    - the internal LHM Knowledge vault `20 Clients/<client>/project-management/` and `Current Projects.md`, via `obsidian-context-contract.md`
    - the client repo, via `detect_stage.py`
    - `brain/Project.md`
  - **Report:** the stage, what's done and what's next.
  - **Flag conflicts** between the internal file and the repo, and don't pick one.
  - **Run the stage's skill:**

    | Stage | Skill |
    |---|---|
    | sitemap | `astro-sitemap` |
    | repo-setup | `client-repo-setup` |
    | prototype | `astro-prototype` |
    | astro-build | `astro-build` |
    | build-brain | `build-brain` |
    | content-round | `content-rollout` |
    | client-review | wait for the client and remind them via `client-update-email` |
    | update-content-brain | `update-content-brain` |

  - **Hand all writing** to `agents/content.md`.
  - **After each stage,** update the internal project file with what was done, what's next and any blockers.
  - **Stop at every approval point** in Global Constraints.
- [ ] **Step 5: Run the tests.** Expected: PASS.
- [ ] **Step 6: Commit**, with a patch bump: `feat(astro-hub): astro-lead, start-astro and stage detection`.

### Task 12: Catalogue, README and release

**Files:**
- Modify: `README.md` at the repo root. Add an `lhm-astro-hub` section to "What This Is", the directory tree and the Skills Catalog, and update the skill counts.
- Modify: `plugins/lhm-marketing-hub/agents/marketing-assistant.md`. The CLAUDE.md checklist requires a catalogue entry. Add one line under a "Website (Astro)" category: `` `lhm-astro-hub` — Astro website delivery: sitemap, prototype, build, client brain, content rounds (start with /lhm-astro-hub:start-astro) ``. This changes `lhm-marketing-hub`, so bump its patch in `plugin.json`, its marketplace entry **and** `metadata.version`, per CLAUDE.md.
- Modify: `plugins/lhm-astro-hub/.claude-plugin/plugin.json` and its marketplace entry, setting `1.0.0`.

- [ ] **Step 1: Make the README and catalogue edits.**
- [ ] **Step 2: Run all of these.** Expected: all pass, with no errors.
  ```bash
  for d in plugins/lhm-astro-hub/tests plugins/lhm-astro-hub/skills/*/tests; do python3 -m unittest discover -s "$d" -p 'test_*.py' || exit 1; done
  python3 scripts/validate-plugin-versions.py
  python3 scripts/validate-script-parity.py
  ```
- [ ] **Step 3: Check that no other plugin's files changed** apart from the one marketing-assistant line and its version bump. Expected: only that file and its `plugin.json`.
  ```bash
  git diff --stat main -- plugins/ ':!plugins/lhm-astro-hub'
  ```
- [ ] **Step 4: Commit**: `feat(astro-hub): catalogue, README and 1.0.0`.
