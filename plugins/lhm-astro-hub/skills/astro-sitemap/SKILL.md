---
name: astro-sitemap
description: "Build the approved sitemap for an Astro website project: the proposed page architecture as an interactive HTML sitemap, colour-coded for what exists, what gets rebuilt and what is still to be written, grouped in build order, with a primary keyword, secondary keywords, audience and intent recorded for every new or enhanced page. Use this when the user says 'sitemap', 'client sitemap', 'sitemap plan', 'content plan for the site', 'what pages do we still need', 'page roadmap', 'site structure', or 'map out the site' for an Astro build or rebuild. No sales widget and no lead estimates. The sitemap is not approvable while any new or enhanced page is missing keyword, audience or intent."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Astro Sitemap

This skill produces the sitemap for an Astro website project: one interactive page showing the site's full proposed architecture, colour-coded so everyone can see what is live, what needs rebuilding, and what is still to be written, grouped into the order it gets built.

Every new or enhanced page also carries its brief fields: primary keyword, secondary keywords, audience and intent. Later steps (prototype, page briefs, content rounds) read those fields, so the sitemap is where they are decided and approved.

There is no opportunity widget, no CTR or conversion inputs, and no lead estimates. The deliverable's job is planning and tracking, not persuasion.

The design is built into two generator scripts. Your job is the research and the judgement. Assemble one `sitemap.json` and run the scripts. Never hand-write the HTML.

---

## Before Starting

1. **Client context** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. Load `client_profile.md`, `services.md` and `locations.md`. If they do not exist, say so rather than inventing the business.
2. **Delivery contract** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before producing the artefact. Resolve the canonical destination first.
3. **Agency learnings** — read `${CLAUDE_PLUGIN_ROOT}/learnings/seo-learned.md` and apply any relevant entries.
4. **Writing rules** — read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` to every piece of client-facing text you write into the JSON. No em dashes. Australian spelling throughout.
5. **Existing work** — check for a prior `sitemap.json` for this client. If one exists, update it rather than starting again.
6. **Own learnings** — read `LEARNED.md` in this skill folder and apply any entries.

---

## Step 1: Establish the current state accurately

This step carries real weight, because the output becomes the working plan.

Fetch `‹domain›/sitemap_index.xml`, and if that 404s, `/sitemap.xml`. Enumerate **every** child sitemap the index lists. Do not treat a single `page-sitemap.xml` as the site.

Cross-check against what the client's knowledge records say has been built. Where the two disagree, the live site wins, and note the discrepancy.

Mark every page honestly:

- `have` (green) — live and fine as it is
- `enh` (yellow) — live but weak, and scheduled for a rebuild
- `new` (red) — not written yet

Because this file will be used to track delivery, a wrong colour becomes a missed page. Verify rather than assume.

## Step 2: Layer in performance data

Where the client has Search Console and Analytics access, use it. For a brand-new site there is no live data: say so, and rely on `keyword-research`.

- Pull GSC query and page data to see which existing pages already earn impressions, and which rank on page two where a rebuild would pay off fastest. That evidence should drive which pages are marked `enh`.
- Use the `keyword-research` skill for demand and intent on pages that do not exist yet. Where a single pass is enough, the Keywords Everywhere MCP (`get_keyword_data`, `get_related_keywords`) will do.

Record volume per intended page in `vol`. Never fabricate a figure. Where there is no measured volume, use `null` so it renders "n/a".

## Step 3: Design the architecture

Read `references/methodology.md` and apply it: un-bundle services into one page each, add audience and funding pillars, build location pages in tiers, and fold the blog into clusters that feed the money pages.

## Step 4: Group the tree in build order

This is what replaces the widget as the page's narrative. Card headings carry the sequence:

```json
{"head": "Phase 1 — build first", "items": [ … ]}
{"head": "Phase 2 — months 4-6", "items": [ … ]}
{"head": "Phase 3 — backlog", "items": [ … ]}
```

Sequence on evidence, not on tidiness. Pages with existing impressions and pages carrying real demand come first. Say why in the section `note`.

## Step 5: Record the brief fields for every new or enhanced page

For each page with status `new` or `enh`, research and record:

- `primary_keyword` — the one term the page targets, from the `keyword-research` output or GSC. Not a guess.
- `secondary_keywords` — a short list of supporting terms and close variants.
- `audience` — who the page is for, in plain words (for example "older homeowners and their adult children").
- `intent` — `informational`, `commercial` or `transactional`.
- `h1` (optional) — only when the intended H1 should differ from the primary keyword. When absent, the primary keyword is the H1.
- `template` (optional) — the prototype page this page is built from, once one exists.

One page, one primary keyword. If two pages share a primary keyword, merge them or re-target one. Never invent a keyword or a volume to fill a gap: leave `vol` as `null` and say where demand could not be measured.

## Step 6: Assemble sitemap.json

Read `references/sitemap-schema.md` and build the spec. `assets/example-sitemap.json` is a full worked example.

**Never write an `opportunity` key.** Its absence is what keeps the widget and its JavaScript out of the page.

## Step 7: Check the brief fields before asking for approval

```bash
python3 scripts/page_brief_seed.py sitemap.json --check
```

It lists every `new` or `enh` page missing `primary_keyword`, `audience` or `intent`, as `<page name>: <field>`, and exits 1 if there are any. Fix them and run it again. **The sitemap is not approvable while the check reports missing fields.** Do not present it for approval, and do not seed a brief from a page that fails the check.

## Step 8: Generate the deliverables

```bash
python scripts/build_sitemap_html.py sitemap.json "‹Client›-Website-Content-Plan.html"
```

```bash
python scripts/build_workbook.py sitemap.json "‹Client›-Website-Content-Plan.xlsx"
```

The script prints which mode it rendered. Confirm it says **client (no widget)**.

The approval stop is the sitemap. Present the HTML and the passing `--check` result, and wait for the user to approve before any later step uses it.

The workbook is genuinely useful, because the client can sort and annotate it as pages get written. It needs `openpyxl`. On a Mac with an externally managed system Python, `pip install` is refused: create a virtual environment (`python3 -m venv <scratch>/venv && <scratch>/venv/bin/pip install openpyxl`) and run both scripts with that interpreter. Both generated pages carry `noindex` and no em dashes, so they can be published to lhmstaging as they are.

Save outputs under the verified work root from the routing contract, in `astro-sitemap/YYYY-MM/` inside the client's folder, and keep `sitemap.json` beside them. Resolve that destination first, as the contract describes. Do not write to the current directory or the plugin folder.

## Step 9: Verify before handing over

Do not report this as complete until you have checked all of these:

- Open the HTML. The nav sits on one row and dropdowns preview correctly.
- There is **no** opportunity widget, no CTR or conversion inputs, no SEO slider and no lead numbers anywhere on the page.
- Every `have` and `enh` page genuinely exists on the live site, and every `new` page genuinely does not.
- The phase grouping matches what has actually been agreed with the client.
- `page_brief_seed.py --check` exits 0.
- The artefact is saved to the canonical destination and read back, per the delivery contract.

---

## What each generator does

- `scripts/build_sitemap_html.py sitemap.json out.html` — the interactive page: branded header plus proposed nav, and the colour-coded page tree. With no `opportunity` key in the JSON, the widget and its calculator JavaScript are not emitted at all. Each page shows its primary keyword under the name. Match the header to the client's real site: if it shows booking or referral buttons beside the phone, add them as `brand.ctas`. With more than about five top-level nav items, also set `brand.cta_position: "strip"` so the buttons sit in a band above the nav; inline buttons beside a long nav need roughly 1550px and scroll sideways on a laptop. Set `brand.careers_link: false` when the client doesn't want the Careers link. Check the page at 1280px wide for one nav row and no horizontal scroll. See `references/sitemap-schema.md`.
- `scripts/build_workbook.py sitemap.json out.xlsx` — a two-tab workbook (Proposed Sitemap, Keyword Demand) from the same JSON. The first tab carries Primary keyword, Secondary keywords, Audience and Intent after the search volume.
- `scripts/page_brief_seed.py sitemap.json "<page name>"` — prints one page's brief fields as JSON for the page-brief step. With `--check` it reports missing fields instead.

Both are pure Python. Never hand-edit an output file. Change the JSON and re-run, so the plan stays regenerable as pages get delivered.

These scripts are a deliberate fork of the marketing sitemap scripts. They are not kept in parity with any other copy, so change them here.

---

## Keeping it current

This deliverable is worth regenerating, and the regenerated version is where most of its value sits after the first hand-over.

Keep every version of `sitemap.json`, dated. As pages go live, flip their `status` from `new` to `have` and re-run against the previous file:

```bash
python scripts/build_sitemap_html.py sitemap.json "‹Client›-Website-Content-Plan.html" --since sitemap-2026-04.json
```

That adds a **progress band** in place of a widget, plus a change chip on every page that moved:

| Chip | Meaning |
|---|---|
| Shipped | was `new`, now live |
| Rebuilt | was `enh`, now live |
| Built | was `new`, now `enh` (exists, still weak) |
| Flagged | was live, now marked for rebuild |
| Reopened | was live, now `new` again |
| Added | not in the previous plan |
| Moved | same status, different section |

Pages removed since the previous version are listed in the band, and the bar shows how many of the planned pages are live.

Pages are matched on their **name**, not their slug, because slugs in these specs are often annotations rather than URLs, and a page that moves section keeps its name. Two consequences worth knowing:

- Give every page a distinct name. Duplicates collapse into one entry in the comparison.
- Renaming a page reads as a delete plus an add. If you rename one, say so in the review rather than letting the band imply churn that did not happen.

For a monthly or quarterly review, `--since` the version you presented last time. That answers "what changed" instead of re-presenting the whole tree.

## Related skills

- `keyword-research` — demand, intent and keyword choice for each new or enhanced page.
- `taya-question-discovery` — finds the buyer questions that justify the pages in the plan.
