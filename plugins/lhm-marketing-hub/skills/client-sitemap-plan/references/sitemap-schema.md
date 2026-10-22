# sitemap.json schema

The single data file that drives both generators. Assemble it from your research, then run the scripts. A complete worked example is in `assets/example-sitemap.json`.

## Top-level keys

| Key | Required | Purpose |
|---|---|---|
| `brand` | yes | Name, logo, phone, colours, credit line |
| `nav` | yes | The proposed top navigation (drives the header and dropdowns) |
| `opportunity` | prospect mode only | The impressions to clicks to leads model above the tree |
| `intro` | yes | Title and paragraph above the page tree |
| `stats` | no | The row of headline numbers under the intro |
| `sections` | yes | The colour-coded page tree, grouped by section, card, page |
| `footer` | no | Small print at the bottom |

### Mode switch

`opportunity` is what selects the mode:

- **Present** — prospect mode. The widget renders above the page tree, with its calculator JavaScript.
- **Absent or `null`** — client mode. No widget, no JavaScript, no lead estimates anywhere on the page. Everything else renders identically.

The `prospect-sitemap-opportunity` skill always includes it. The `client-sitemap-plan` skill always omits it.

## brand

```json
{
  "name": "My Garden Therapy",
  "logo_url": "https://…/logo.svg",
  "phone": "03 5215 9400",
  "primary": "#2E6B3E",
  "primary_dark": "#1F4D2C",
  "primary_light": "#E4EFE7",
  "accent": "#C8A44D",
  "prepared_by": "Local Health Marketing",
  "date": "July 2026"
}
```

`logo_url` and `phone` are optional. `panel_top` is also optional: the top colour of the dark widget and progress panels, which fade down to `primary_dark`. It defaults to deep green (`#12351f`); set a dark shade of the client's own colour so the panel matches their brand. Without a logo the name renders as text; without a phone the green call button is omitted. Pick brand colours from the client's own site so the mock feels like theirs.

## nav

An ordered list of top-level items. Three shapes:

```json
{"label": "About Us"}
{"label": "Who We Help", "new": true, "items": [ … ]}
{"label": "What We Do", "mega": true, "groups": [ … ]}
```

- `"new": true` on any item adds a red dot (a new top-level section, or a new page inside a dropdown).
- Simple dropdown `items`: `[{"label": "Gardening for Seniors", "new": true}, …]`
- Mega `groups`: `[{"title": "Garden Care", "items": [{"label": "…", "new": true}]}]`
- Grouped but not mega: use `groups` without `mega: true` for a single column with sub-headings, as used for "Getting Started".

Keep the nav to what fits on one row. The header does not wrap, and a wrapped nav is the most common visual defect in the finished page.

## opportunity

```json
{
  "imp_now": 1200,
  "imp_new": 6000,
  "ctr": 4,
  "conv": 4,
  "seo_max": 10,
  "seo_step_pct": 10,
  "seed": "…one line seeding ongoing SEO (HTML allowed)…",
  "composition_note": "…how imp_now and imp_new were derived (HTML allowed)…"
}
```

`title` and `sub` are also accepted and override the default headings. See `methodology.md` for how to choose these numbers defensibly.

## stats

```json
[{"n": "18", "label": "pages today"}, {"n": "~55", "label": "pages proposed"}]
```

## sections, cards, pages

```json
{
  "title": "What We Do — services",
  "pill": "All new",
  "note": "<b>On location pages:</b> …",
  "cards": [
    {
      "head": "Garden Care",
      "url": "/who-we-help/",
      "items": [
        {"name": "Garden Maintenance", "slug": "/how-can-we-help/garden-maintenance/",
         "status": "have", "vol": 140},
        {"name": "Lawn Mowing & Lawn Care", "slug": "/services/lawn-mowing/",
         "status": "new", "vol": 210},
        {"name": "Weeding & Mulching", "slug": "/services/weeding-mulching/",
         "status": "new", "vol": null, "bold": false}
      ]
    }
  ]
}
```

`pill`, `note` and `url` are optional. `note` and `pill` accept HTML.

### Page fields

| Field | Meaning |
|---|---|
| `name` | Page title shown to the client. Must be **distinct within the spec** — `--since` matches pages across versions on the name, so duplicates collapse into one entry |
| `slug` | Small mono URL or label under the name (optional) |
| `status` | `"have"` (green, exists) · `"enh"` (yellow, rebuild) · `"new"` (red) |
| `vol` | Monthly searches (int). Use `null` or `0` when there is no measured volume, which renders "n/a" |
| `bold` | `true` to bold the page name. Use sparingly, for the flagship pillars |

The status colour carries the whole argument. Only mark a page `have` if it genuinely exists on the live site today, `enh` if it exists but is weak, and `new` if it does not exist. Never blur these. The credibility of the mock rests on the client recognising their existing pages as green.

## Card grouping as a roadmap

Cards are just labelled groups, so they can carry sequencing as well as taxonomy. Tier and phase headings both work:

```json
{"head": "Tier 1 — build first", "items": [ … ]}
{"head": "Phase 2 — months 4-6", "items": [ … ]}
```

`client-sitemap-plan` leans on this to express build order, since it has no widget to carry the narrative.

## Packages: Foundation and Growth

Add a top-level `tiers` list to show one sitemap as cumulative packages, for example a Foundation website and a 12-month Growth programme on top of it. A switch under the header moves between them, and the page count, nav, stats and widget all follow.

```json
"tiers": [
  {"key": "Foundation", "label": "Foundation website", "short": "Foundation",
   "imp_new": 16400, "opp_label": "Foundation website · same rates",
   "composition_note": "…how this tier's searches were derived…"},
  {"key": "Growth", "label": "Foundation + 12-month Growth", "short": "Growth",
   "imp_new": 28100, "opp_label": "Foundation + Growth · same rates",
   "composition_note": "…"}
]
```

- Tag a page, card, section, nav item (top level or dropdown link) or stat with `"tier": "Growth"`. Tagged elements appear from that tier onwards. Untagged elements belong to the first tier and always show.
- A page tagged beyond the first tier shows a small chip with the tier's `short` name.
- `"count"` on a page sets how many pages the row stands for in the live total (default 1). Use it for a "21 clinician profiles" row, or `0` for a clean-up row that is not a page.
- A stat tagged with a tier shows only while that exact tier is selected, since headline numbers describe one package.
- In prospect mode, each tier's `imp_new` replaces the widget's "new searches" figure and `opp_label` relabels the middle column. Each tier's `composition_note` shows under the main one while that tier is selected.
- The workbook gains a Package column.
- Mark one tier `"default": true` to open on it; otherwise the page opens on the first tier.

## Comparing versions

Keep each dated version of the spec. Passing an older one as `--since` renders a progress band and a change chip on every page that moved:

```bash
python scripts/build_sitemap_html.py sitemap.json out.html --since sitemap-2026-04.json
```

Nothing in the schema changes for this. The comparison reads `sections` → `cards` → `items` from both files and matches on `name`. `brand.date` from the older spec labels the band, so keep it filled in and accurate.
