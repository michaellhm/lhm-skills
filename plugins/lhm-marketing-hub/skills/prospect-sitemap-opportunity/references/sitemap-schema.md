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

`logo_url` and `phone` are optional. Without a logo the name renders as text; without a phone the green call button is omitted. Pick brand colours from the client's own site so the mock feels like theirs.

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

## Comparing versions

Keep each dated version of the spec. Passing an older one as `--since` renders a progress band and a change chip on every page that moved:

```bash
python scripts/build_sitemap_html.py sitemap.json out.html --since sitemap-2026-04.json
```

Nothing in the schema changes for this. The comparison reads `sections` → `cards` → `items` from both files and matches on `name`. `brand.date` from the older spec labels the band, so keep it filled in and accurate.
