---
name: client-sitemap-plan
description: "Build a visual website content plan for an existing client: the proposed page architecture as an interactive HTML sitemap, colour-coded for what exists, what gets rebuilt, and what is still to be written, grouped in build order. No sales widget and no lead estimates. Use when the user says 'client sitemap', 'sitemap plan', 'content plan for the site', 'what pages do we still need', 'page roadmap', 'site structure for an existing client', or wants to map or expand a current client's site. For a prospect pitch that needs the impressions-to-leads opportunity model, use prospect-sitemap-opportunity instead. For the build-phase IA and 301 redirect map inside a live website project, use the WordPress hub sitemap-architect skill."
---

# Client Sitemap Plan

This skill produces a working reference for an existing client: one interactive page showing the site's full proposed architecture, colour-coded so everyone can see what is live, what needs rebuilding, and what is still to be written, grouped into the order it gets built.

It is the same architecture work as `prospect-sitemap-opportunity`, with the sales layer removed. There is no opportunity widget, no CTR or conversion inputs, and no lead estimates. An existing client is already bought in, so the deliverable's job is planning and tracking, not persuasion.

The design is built into two generator scripts. Your job is the research and the judgement. Assemble one `sitemap.json` and run the scripts. Never hand-write the HTML.

---

## Before Starting

1. **Client context** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. Load `client_profile.md`, `services.md` and `locations.md`. For an existing client these should exist; if they do not, say so rather than inventing the business.
2. **Delivery contract** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before producing the artefact. Resolve the canonical destination first.
3. **Agency learnings** — read `${CLAUDE_PLUGIN_ROOT}/learnings/seo-learned.md` and apply any relevant entries.
4. **Writing rules** — read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` to every piece of client-facing text you write into the JSON. No em dashes. Australian spelling throughout.
5. **Existing work** — check for a prior `sitemap.json` for this client, from an earlier run or from a `prospect-sitemap-opportunity` pitch that has since been won. If one exists, update it rather than starting again, and drop the `opportunity` block when you do.

---

## Step 1: Establish the current state accurately

For an existing client this step carries more weight than it does in a pitch, because the output becomes the working plan.

Fetch `‹domain›/sitemap_index.xml`, and if that 404s, `/sitemap.xml`. Enumerate **every** child sitemap the index lists. Do not treat a single `page-sitemap.xml` as the site.

Cross-check against what the client folder says has been built. Where the two disagree, the live site wins, and note the discrepancy.

Mark every page honestly:

- `have` (green) — live and fine as it is
- `enh` (yellow) — live but weak, and scheduled for a rebuild
- `new` (red) — not written yet

Because this file will be used to track delivery, a wrong colour becomes a missed page. Verify rather than assume.

## Step 2: Layer in performance data

An existing client usually has Search Console and Analytics access. Use them.

- Pull GSC query and page data to see which existing pages already earn impressions, and which rank on page two where a rebuild would pay off fastest. That evidence should drive which pages are marked `enh`.
- Use the Keywords Everywhere MCP (`get_keyword_data`, `get_related_keywords`) for demand on pages that do not exist yet.

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

## Step 5: Assemble sitemap.json

Read `references/sitemap-schema.md` and build the spec. `assets/example-sitemap.json` is a full worked example in client mode.

**Omit the `opportunity` key entirely.** Its absence is what removes the widget and its JavaScript. Do not include it with zeroed values, and do not include it commented out.

## Step 6: Generate the deliverables

```bash
python scripts/build_sitemap_html.py sitemap.json "‹Client›-Website-Content-Plan.html"
```

```bash
python scripts/build_workbook.py sitemap.json "‹Client›-Website-Content-Plan.xlsx"
```

The script prints which mode it rendered. Confirm it says **client (no widget)**.

The workbook is genuinely useful here, more so than in a pitch, because the client can sort and annotate it as pages get written. It needs `openpyxl`.

Save outputs to the canonical destination resolved in *Before Starting*. Where a local working copy is also wanted, use `client/client-sitemap-plan/YYYY-MM/`.

## Step 7: Verify before handing over

Do not report this as complete until you have checked all five:

- Open the HTML. The nav sits on one row and dropdowns preview correctly.
- There is **no** opportunity widget, no CTR or conversion inputs, no SEO slider and no lead numbers anywhere on the page.
- Every `have` and `enh` page genuinely exists on the live site, and every `new` page genuinely does not.
- The phase grouping matches what has actually been agreed with the client.
- The artefact is saved to the canonical destination and read back, per the delivery contract.

---

## What each generator does

- `scripts/build_sitemap_html.py sitemap.json out.html` — the interactive page: branded header plus proposed nav, and the colour-coded page tree. With no `opportunity` key in the JSON, the widget and its calculator JavaScript are not emitted at all.
- `scripts/build_workbook.py sitemap.json out.xlsx` — a two-tab workbook (Proposed Sitemap, Keyword Demand) from the same JSON. It reads only the page tree, so its output is identical in either mode.

Both are pure Python. Never hand-edit an output file. Change the JSON and re-run, so the plan stays regenerable as pages get delivered.

The scripts in this skill are identical copies of the ones in `prospect-sitemap-opportunity`. If you fix one, fix both. This is enforced: `scripts/validate-script-parity.py` runs in the pre-commit and pre-push hooks and blocks the commit if the copies diverge, or if you fix both but stage only one.

---

## Keeping it current

This deliverable is worth regenerating, and the regenerated version is where most of its value sits after the first hand-over.

Keep every version of `sitemap.json`, dated. As pages go live, flip their `status` from `new` to `have` and re-run against the previous file:

```bash
python scripts/build_sitemap_html.py sitemap.json "‹Client›-Website-Content-Plan.html" --since sitemap-2026-04.json
```

That adds a **progress band** where the prospect version puts its widget, plus a change chip on every page that moved:

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

- `prospect-sitemap-opportunity` — the same architecture work for a pitch, with the impressions-to-leads widget.
- `content-gap-analysis` — finds the topic gaps that justify the pages in the plan.
- `keyword-research` — deeper demand research when a single Keywords Everywhere pass is not enough.
- `service-page-generator` and `seo-content-writer` — write the pages once the plan is agreed.
- `programmatic-seo` — templating for the location and service pages at scale.
- WordPress hub `sitemap-architect` — the Phase 2 build IA and 301 redirect map inside a live website project.
