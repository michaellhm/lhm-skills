# Landing Page Campaign Reference

Shared reference for the lp-* skill set. All six skills read from and write to the same `/lp/lp_state.md` file in the client's project folder.

## Skill Sequence

```
lp-subsite-setup  → Configure WP multisite subsite (theme, branding, CPTs)
lp-copy           → Write campaign brief + copy files per ad group
lp-prototype      → Build HTML/CSS prototype per ad group
lp-deploy-1       → Push primary landing page as Gutenberg HTML blocks
lp-deploy-2       → Convert HTML blocks to native Gutenberg blocks
lp-deploy-3       → Deploy all remaining ad group landing pages
```

Skills can run in any order where prerequisites allow. The minimum prerequisite chain is:
- `lp-subsite-setup` before any deploy skill
- `lp-copy` before `lp-prototype`
- `lp-prototype` before `lp-deploy-1`
- `lp-deploy-1` before `lp-deploy-2`
- `lp-deploy-1` before `lp-deploy-3`

## Folder Structure

Inside the client's project folder:

```
lp/
  lp_state.md                         Campaign + subsite state (all skills read/write)
  campaign_brief.md                   Ad groups + keywords (written by lp-copy)
  copy/
    [ad-group-slug]-copy.md           Copy per ad group (written by lp-copy)
  prototype/
    [ad-group-slug]/
      index.html                      Self-contained HTML/CSS prototype
  deploy/
    [ad-group-slug]-content.html      HTML blocks version (for WP push)
    [ad-group-slug]-content-blocks.html  Native block version (after lp-deploy-2)
    page-index.md                     Quick-reference list of all deployed pages
  assets/
    logo.png                          Client logo (for prototype)
    favicon.png                       Client favicon
```

## lp_state.md Format

```markdown
# Landing Page Campaign State

## Multisite Config
- **WP Base URL**: [e.g. http://localhost:8083/]
- **Subsite URL**: [e.g. http://localhost:8083/clinic-slug/]
- **Subsite ID**: [integer]
- **Theme**: [theme-slug]
- **Container**: [docker container name, e.g. wp-wordpress-1]

## Subsite Setup
| Item | Status | Notes |
|------|--------|-------|
| Subsite created | ✅ / ⏳ | ID: [N] |
| Theme activated | ✅ / ⏳ | [theme-slug] |
| Logo | ✅ / ⏳ | Attachment ID: [N] |
| Site title + tagline | ✅ / ⏳ | |
| Favicon | ✅ / ⏳ | Attachment ID: [N] |
| Brand colours | ✅ / ⏳ | |
| Social proof | ✅ / ⏳ | |
| Social media URLs | ✅ / ⏳ | |
| Locations CPT | ✅ / ⏳ | [N] locations created |

## Campaign
- **Brief**: /lp/campaign_brief.md
- **Ad Groups**:
  - [slug-1]: /lp/copy/[slug-1]-copy.md ✅
  - [slug-2]: /lp/copy/[slug-2]-copy.md ✅

## Pages Built
| Ad Group | Copy File | Prototype | HTML Push | Blocks File | Post ID | Status |
|----------|-----------|-----------|-----------|-------------|---------|--------|
| [name] | /lp/copy/[slug]-copy.md | /lp/prototype/[slug]/index.html | /lp/deploy/[slug]-content.html | /lp/deploy/[slug]-content-blocks.html | [ID] | Blocks Live |

## Deployment Summary
- **Total pages deployed**: [N]
- **Pages in native blocks**: [N]
- **Pages as HTML blocks**: [N]
- **Date**: [YYYY-MM-DD]
```

## Status Values

| Status | Meaning |
|--------|---------|
| Copy ready | lp-copy complete, prototype not yet built |
| Prototype ready | lp-prototype complete, not yet deployed |
| HTML Live | lp-deploy-1 complete, blocks not yet converted |
| Blocks Live | lp-deploy-2 complete, page fully editable |
| HTML Live — block conversion pending | lp-deploy-3 ran, block conversion skipped for this page |

## Industry → Theme Mapping

| Industry | Theme Slug |
|----------|-----------|
| Healthcare, allied health, physiotherapy, chiropractic, podiatry, psychology | `lhm-health` |
| (future) Dental | TBD |
| (future) Cosmetic | TBD |

Add new entries to this table and to LEARNED.md of the relevant skill when a new theme is created.

## WP-CLI Multisite Pattern

All commands require `--url` pointing to the subsite:

```bash
docker exec $CONTAINER wp --allow-root [command] --url=[SUBSITE_URL]
```

When passing file content, copy the file in first:
```bash
docker cp [local-path] $CONTAINER:/tmp/[filename]
docker exec $CONTAINER wp --allow-root post create \
  --post_content="$(docker exec $CONTAINER cat /tmp/[filename])" \
  --url=[SUBSITE_URL]
```

## Landing Page Section Classes

These class names are locked. lp-prototype uses them, lp-deploy-2 maps them to blocks. Do not rename.

| Section | Class |
|---------|-------|
| Sticky header | `.site-header` |
| Hero | `.hero-section` |
| Trust bar | `.trust-bar` |
| Pain points | `.pain-points-section` |
| Solution intro | `.solution-section` |
| Service features | `.features-section` |
| Testimonials | `.testimonials-section` |
| How it works | `.process-section` |
| FAQ | `.faq-section` |
| Locations / Booking CTA | `.locations-section` |
| Footer | `.site-footer` |
