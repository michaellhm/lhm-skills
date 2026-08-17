---
name: prospect-sitemap-opportunity
description: "Build a client-ready proposed website sitemap plus opportunity model to win a website rebuild. Crawls the prospect's live site, researches search demand, designs the expanded architecture (unbundled service pages, location pages, audience and funding pages, blog clusters), and generates an interactive HTML sitemap with a live impressions-to-leads widget and ongoing-SEO slider, plus an optional spreadsheet. Use when the user says 'prospect sitemap', 'proposed sitemap', 'sitemap for the pitch', 'website proposal', 'map out the site for a prospect', 'show them what pages we should build', 'website opportunity', or is preparing a pitch for a new website or rebuild. For an existing client where no sales widget is wanted, use client-sitemap-plan instead. For the build-phase IA inside a live website project, use the WordPress hub sitemap-architect skill."
---

# Prospect Sitemap and Opportunity

This skill produces the deliverable that wins website rebuild work: one interactive page showing a prospect's *current* site structure against a *proposed* expanded one, colour-coded so the gaps jump out, topped by an editable opportunity model that turns structure into an estimated monthly-leads number.

The design and maths are already built into two generator scripts. Your job is the research and the judgement: understand the business, find the demand, design the architecture. Then assemble one `sitemap.json` and run the scripts. Never hand-write the HTML. The script guarantees consistent styling and a working widget every time.

**Use this skill for prospects.** For an existing client, where a lead-estimate widget would be the wrong tone, use `client-sitemap-plan` instead.

---

## Before Starting

1. **Client context** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. Load `client_profile.md` and any existing `services.md` / `locations.md`. For a cold prospect there will be no profile; work from the live site and the discovery call instead, and do not create a blank profile.
2. **Delivery contract** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before producing the artefact. Resolve the canonical destination *before* you generate. Do not guess a folder.
3. **Agency learnings** — read `${CLAUDE_PLUGIN_ROOT}/learnings/seo-learned.md` and apply any relevant entries.
4. **Writing rules** — read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` to every piece of client-facing text you write into the JSON (intro paragraph, section notes, composition note, footer). No em dashes. Australian spelling throughout.

---

## Two entry points, same workflow

- **Opportunity / pitch** — a prospect has a live site and wants a rebuild. Audit what exists, then show the expansion. This is the common case.
- **Greenfield** — a discovery phase, or a business with little or no site. Design the architecture from scratch and mark everything `new`.

---

## Step 1: Understand the business and its market

Identify the services, the audiences, how customers pay (private, NDIS, Home Care Packages, Support at Home for Australian aged care), the primary city and any second market, and the brand colours. Pull the colours from the prospect's own site so the mock feels like theirs. This one detail does more for the pitch than anything else on the page.

## Step 2: Audit the current site

Fetch `‹domain›/sitemap_index.xml`, and if that 404s, `/sitemap.xml`. Fetch the homepage. Inventory the existing pages.

Do not treat a single `page-sitemap.xml` as the whole site. Enumerate every child sitemap the index lists.

Note which services are bundled onto shared pages, whether high-demand themes live only in the blog, and whether any location pages exist. Every existing page becomes a `have` (green) or `enh` (yellow) row. Everything you propose that is not there is `new` (red).

## Step 3: Research demand

Use the Keywords Everywhere MCP (`get_keyword_data`, `get_related_keywords`) for monthly search volumes. Pull, at minimum:

- each service plus the prospect's main city
- "near me" variants
- the funding terms for the vertical
- the wellbeing and differentiator terms
- the second town or market, if there is one

For a cold prospect you will not have Search Console access. Treat the figures as **demand, not rankings**, and say so on the page. If this is a warm prospect who has granted GSC access, layer in current rankings to sharpen priorities.

## Step 4: Design the architecture

Read `references/methodology.md` and apply it: un-bundle services into one page each, add audience and funding pillars, build location pages in tiers, and fold the blog into clusters that feed the money pages.

## Step 5: Assemble sitemap.json

Read `references/sitemap-schema.md` and build the spec. `assets/example-sitemap.json` is a full worked example (the My Garden Therapy build) — copy its shape.

Set the opportunity numbers conservatively and defensibly per the methodology, and always write the `composition_note` explaining how `imp_now` and `imp_new` were derived.

## Step 6: Generate the deliverables

```bash
python scripts/build_sitemap_html.py sitemap.json "‹Client›-Proposed-Sitemap.html"
```

```bash
python scripts/build_workbook.py sitemap.json "‹Client›-Proposed-Sitemap.xlsx"
```

The HTML is the hero. The workbook is an optional sortable companion and needs `openpyxl`.

Save outputs to the canonical destination resolved in step 2 of *Before Starting*. Where a local working copy is also wanted, use `client/prospect-sitemap-opportunity/YYYY-MM/`.

## Step 7: Verify before handing over

Do not report this as complete until you have checked all four:

- Open the HTML. The nav sits on one row, dropdowns preview correctly, and the widget recalculates when you edit an input or drag the slider.
- Spot-check that every `have` and `enh` page genuinely exists on the live site. Mislabelling an existing page as "new", or the reverse, is the fastest way to lose the room.
- The opportunity numbers are defensible and `composition_note` is present.
- The artefact is saved to the canonical destination and read back, per the delivery contract.

---

## What each generator does

- `scripts/build_sitemap_html.py sitemap.json out.html` — the interactive page: branded header plus proposed nav (red "new" dots and a 3-column mega menu), colour-coded page tree, and the opportunity widget with editable CTR/conversion and the ongoing-SEO slider (each step = +N% impressions and conversion, CTR held flat).
- `scripts/build_workbook.py sitemap.json out.xlsx` — a two-tab workbook (Proposed Sitemap, Keyword Demand) from the same JSON.

Both are pure Python. Never hand-edit an output file. If something needs to change, change the JSON and re-run, so the deliverable stays consistent and regenerable.

The HTML generator switches mode on the presence of the `opportunity` key. This skill always includes it. `client-sitemap-plan` omits it, which drops the widget and its JavaScript entirely.

---

## Related skills

- `client-sitemap-plan` — same architecture work for an existing client, without the sales widget.
- `keyword-research` — deeper demand research if the volumes need more than a single Keywords Everywhere pass.
- `seo-audit` — technical and on-page diagnostics of the existing site.
- `programmatic-seo` — how to build the location and service page templates at scale once the work is won.
- WordPress hub `sitemap-architect` — the Phase 2 build IA, including the 301 redirect map. This skill feeds it: the approved proposed sitemap becomes its starting input.

## Optional companions

The same research supports two short one-pagers that pair well with the sitemap in a proposal: a non-salesy "why upgrade" case, and a keyword-evidence summary. Write these as Markdown if the prospect wants them. The scripts do not generate them.
