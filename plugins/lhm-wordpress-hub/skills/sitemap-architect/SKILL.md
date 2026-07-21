---
name: sitemap-architect
description: "Build the site information architecture — keyword map, sitemap, page hierarchy, and 301 redirect map. Use this when the user says 'plan the sitemap', 'site structure', 'information architecture', 'IA planning', 'page hierarchy', 'keyword mapping', 'site map', or 'audit the live site before the rebuild'. Phase 2 of the website build. Requires client profile from Phase 1."
---

# Sitemap Architect

Build the site information architecture: keyword map, sitemap hierarchy, page list, and (for rebuilds) the full live-site reconciliation and 301 redirect map.

**The single most common failure in this skill is auditing an incomplete picture of the live site.** Step 1 exists to prevent it. Do not skip it on a rebuild, and do not treat `page-sitemap.xml` as the site.

---

## Before Starting

1. **Read client context** — all files in `/client/` (especially `client_profile.md`, `services.md`, `locations.md`)
2. **Check for existing SEO work** — if `/seo/keyword_map.md` or `/seo/sitemap.md` exist, read them and build on them
3. **Run the intake questions** — see `references/intake-questions.md`. Do this *before* any research. Five minutes here saves a full rebuild of the architecture later.

If client context is insufficient, say what's missing and offer to run Client Context Intake first.

---

## Step 0: Intake Questions (do this first)

Load `references/intake-questions.md` and put the questions to the user via `AskUserQuestion`.

These are not administrative. Each one has, in a real project, changed the architecture after the fact when it went unasked. The programmatic-pages question alone has caused a 26-page miss.

Record the answers in the PM doc before proceeding.

---

## Step 1: Live Site Reconciliation (rebuilds only)

Skip only for genuinely greenfield sites with no existing domain.

### 1a. Enumerate every sitemap, not one

```
Fetch: https://[domain]/sitemap_index.xml   (fall back to /sitemap.xml, then /robots.txt)
```

The index lists sub-sitemaps. **Fetch every one.** A typical WordPress site running Rank Math or Yoast splits into:

| Sub-sitemap | Usually contains | Commonly missed? |
|---|---|---|
| `page-sitemap.xml` | Standard pages | No — this is the one everyone reads |
| `post-sitemap.xml` | Blog posts | Underestimated (assumed "a few", often 70+) |
| `category-sitemap.xml` | Taxonomy archives | **Yes** |
| `[cpt]-sitemap.xml` | Custom post types | **Yes — the big one** |
| `local-sitemap.xml` | `locations.kml`, geo assets | **Yes** |
| `author-sitemap.xml` | Author archives | Yes |

Custom post types are where the damage happens. Real examples seen in the wild: `staff`, `locations`, `education_hub`, `testimonials`, `case-studies`, `products`, `team`, `projects`. Each is a content type invisible to `page-sitemap.xml`.

**Report the live URL total against your architecture total.** If the architecture covers meaningfully fewer URLs than the site has, you are not finished.

### 1b. Crawl if available

Screaming Frog via the GMB hub MCP (`crawl_site`) catches what sitemaps cannot: orphan pages, `noindex` directives, redirect chains, and pages excluded from XML sitemaps entirely.

If the CLI is unavailable, sitemap enumeration is a workable substitute for structure — but note in the PM doc that a rendered crawl is still outstanding before launch.

### 1c. Classify every live URL

Every URL needs one of: **Keep** / **Merge** / **Redirect** / **Drop** / **Migrate as-is**.

> **Before writing any redirect, confirm what the source URL actually is.**
>
> A URL that looks like a dead or duplicate location page may be a deliberate programmatic page that is ranking. Redirecting it destroys a working asset and folds its equity into a page that was never competing for those terms. If a URL pattern appears many times (`/locations/*`, `/areas/*`, `/[service]-[suburb]/`), that is a programmatic set — ask before touching any of it.

### Output: `/seo/live-site-audit-v[n].md`

Include: the sitemap index table with per-sitemap counts, live total vs architecture total, each missing content type with a recommendation, cannibalisation collisions, and anything requiring a client decision.

---

## Step 2: Keyword Research

**Treat client briefs as input, not gospel.** Volume data validates or overrides proposed structure. Clients propose pages with no demand and miss high-opportunity ones.

For each potential page: primary keyword, secondaries, intent, volume, competition.

Use `mcp__keywords-everywhere__get_keyword_data` with the correct country and currency. Batch 20 terms per call.

### Intent-check anything that looks unexpectedly good

A high suburb-level volume on a service you offer is not automatically an opportunity. Check what the searcher actually wants.

> Worked example: "pilates [suburb]" returned 140–210/mo across three clinics. Tempting. But the intent is studio and reformer classes, while the client offers *clinical* pilates on GP referral. Different search, different buyer, and a page targeting it would have competed with gyms and lost. Rejected on intent despite the volume.

Tells that volume is the wrong intent: competition score far above the client's other terms, and a SERP dominated by a business model the client isn't in.

### Validate ambiguous place names

Australian (and UK, and US) suburb names repeat across states. "Newport" exists in VIC, NSW, and QLD. A national volume figure may be splitting across all of them.

Check in GSC before treating a suburb figure as local. If GSC access is unavailable, flag the number as unvalidated in the sitemap rather than silently trusting it.

### Output: `/seo/keyword_map.md`

```markdown
# Keyword Map

## [Page Name]
| Keyword | Type | Intent | Volume | Competition | Notes |
|---------|------|--------|--------|-------------|-------|
```

---

## Step 3: Sitemap Architecture

Design the hierarchy. Principles:

- Most pages within 2–3 clicks of home
- Silo related content under topic clusters
- **Merge thin pages.** Symptom pages sharing a root cause belong on one comprehensive page; separate thin pages cannibalise each other
- **Hubs need a head term.** Only create a hub if the hub concept has its own search demand. If the children *are* the head terms, group them in navigation and leave them standalone
- **Branded/proprietary product pages** have near-zero organic volume when the brand is unknown. Build them for conversion, not discovery, and say so

### Content types to place deliberately

Decide each of these explicitly rather than defaulting:

| Type | Default position |
|---|---|
| **Staff / practitioner / author profiles** | **Keep as a CPT.** These are E-E-A-T assets carrying real equity. Collapsing 15 profiles into one team page discards 15 ranking pages and the author authority behind them. The team page becomes an *index*, not a replacement |
| **Programmatic / area / proximity pages** | Migrate as-is, no URL change. Keep out of primary nav (they overwhelm a dropdown); reach via hub and footer. Map each to its nearest real location for CTA and NAP |
| **Legacy CPTs duplicating newer structures** | Retire and 301 into the newer structure. **Salvage the copy first** — harvest usable explanatory content into destination pages rather than discarding it |
| **Category / taxonomy archives** | Usually noindex, especially where archive names duplicate planned page names. Keep a curated few if genuinely useful |
| **Geo assets (`locations.kml`)** | Carry across or regenerate. These feed local pack signals and vanish silently in a stack migration |

---

## Step 4: Service × Location Validation (multi-location clients)

When a client has multiple locations and multiple services, the tempting move is a full matrix. **Do not build the matrix. Validate every cell.**

### Method

1. Pull suburb-level volume for **every** service × location combination
2. Identify each location's *dominant* modality — it differs by location and is often not the client's flagship service
3. Dominant modality stays on the main location page
4. Build a dedicated `[location]/[service]/` page only for secondary cells clearing roughly **90–100/mo**
5. Everything else links to the metro-level service page

> Worked example (3 clinics × 10 services = 30 possible cells). Exercise Physiology and Dietetics returned **zero** volume at all three clinics. Myotherapy registered only at one (70). Six cells cleared the threshold. The matrix would have produced 24 pages targeting nothing.
>
> The dominant modality also varied by clinic: osteopathy at one, physiotherapy at another, chiropractic at the third. Assuming the flagship service leads everywhere would have mis-optimised two of three location pages.

### Service box linking rule

On each location page, service boxes link to the local service×location page **where one exists**, and fall through to the metro service page where it does not. Never create an empty page for the sake of link consistency.

### Two caveats to state explicitly

- **These SERPs are local-pack heavy.** Suburb-service pages compete for below-pack organic and feed GBP relevance. Do not model their performance on metro-term behaviour
- **Thin-content risk.** These pages are only defensible if they carry site-specific substance: the named practitioners delivering that service at that site (pulled from the staff CPT), rooms, equipment, parking, local club links. A suburb name swapped into a template is doorway content

---

## Step 5: Cannibalisation & Redirect Map

### Cross-type cannibalisation audit

Check planned pages against **every live content type**, not just pages. Collisions hide across types: a planned condition page, a legacy CPT article, and a blog post can all target one term without any of them appearing in `page-sitemap.xml` together.

Build the collision table before writing redirects.

### Redirect timing for performing content

A recent, ranking blog post that duplicates a planned page is a real asset. Redirecting it at launch into a page that does not exist yet trades something known for something unproven.

**Stage these post-launch:** redirect only once the destination page is live and indexed. Say so in the redirect map rather than lumping them in with the launch-day 301s.

### Output: `/seo/sitemap.md` → 301 Redirect Map section

Split into **launch-day redirects** and **staged post-launch redirects**, with a one-line reason per staged item.

---

## Step 6: Deliverables

Three artefacts, always:

1. **`/seo/sitemap.md`** — full hierarchy, nav structure, internal linking strategy, redirect map, validation notes, and every decision with the evidence behind it
2. **`/seo/keyword_map.md`** — keyword assignments
3. **Colour-coded spreadsheet** — run `scripts/build_sitemap_sheet.py`

### The spreadsheet

`scripts/build_sitemap_sheet.py` generates a four-tab `.xlsx`:

| Tab | Contents |
|---|---|
| **Sitemap** | Full hierarchy, colour-coded by nav depth, indented to read as a tree |
| **Programmatic** | Area/template pages, colour-grouped by parent location |
| **Decisions** | Open items with a "blocks sign-off?" column |
| **Legend** | Colour key + live counts |

Colour rules that survived review: dark anchor colour for L1 only, **very pale** tints for L2 and L3 (a saturated mid-tone across dozens of rows reads as noise), grey for utility, amber for pending decisions.

**Put pending decisions inside the main Sitemap tab as well as on the Decisions tab.** Anyone reviewing the hierarchy should see that a content type is missing without clicking through.

Google Sheets note: uploading via the Drive connector requires base64 and is failure-prone at this file size. Writing the `.xlsx` into the client's synced Drive folder is more reliable — it opens in Sheets with formatting intact.

---

## Step 7: Approval Gate

Present the sitemap, keyword map, and spreadsheet. Use `AskUserQuestion`:

> "Proposed architecture: X pages (Y editorial + Z programmatic). Live site has N URLs. Approved — proceed to Page Briefs?"

Options: "Approved — generate page briefs" / "Changes needed" / "Add more pages"

### Do not present for sign-off while any of these are true

- Live URL total materially exceeds architecture total with no disposition for the gap
- Any content type discovered in Step 1 has no decision recorded
- Any redirect points a live, ranking URL at a page that does not exist yet, with no staging note
- Any hub exists without a head term justifying it

**Hold sign-off explicitly in the PM doc** when a blocker appears — mark the step `[!]` with a pointer to the audit file, rather than letting it look complete.

### Record decisions with their evidence

In the PM doc, log *why*, not just *what*. "Matrix rejected" is not useful in three months. "Matrix rejected: EP and Dietetics returned zero suburb volume at all three clinics; six of thirty cells cleared threshold" is.

---

## Validation Checklist

Before finalising:

1. Every sub-sitemap in the index has been fetched and reconciled
2. Every live URL has a disposition
3. Every service in `/client/services.md` has a page (or a documented reason it does not)
4. Every location has a page; every programmatic page is accounted for
5. No orphan pages
6. No keyword cannibalisation — across *all* content types
7. Depth ≤ 3 for important pages
8. Thin pages merged
9. Every hub has a head term
10. Every content type from Step 1 has an explicit decision
11. Redirect map splits launch-day from staged
12. Ambiguous place-name volumes flagged or validated
13. Client asked whether the live site is still being edited

---

## Next Step

Once approved, offer the **Page Brief Generator** skill.
