# Local Health Marketing site contract

Recorded from Michael's Search Console repair session on 9 October 2026. Reconfirm current paths, Git state and report data at runtime; historical counts are not current targets.

## Identity and access

- Search Console property / canonical production host: `https://localhealthmarketing.com/` (not `.com.au`).
- Website source: `/Users/michaelcolman/Documents/Astro Projects/Local Health Marketing Website/local-health-marketing-astro` (older `/Users/michaelcolman/Documents/Projects/astro` is a symlink).
- Git origin: `michaellhm/local-health-marketing-astro`.
- Cloudflare Pages: `local-health-marketing-astro`; production follows the registered Git main route. Existing CLI authentication previously lacked the correct account/Pages permissions; the authenticated browser was usable. Recheck rather than changing permissions.
- Work root: `/Users/michaelcolman/Library/CloudStorage/GoogleDrive-michael@localhealthmarketing.com.au/Shared drives/Claude Workspace/LHM Internal/local health marketing`.
- Historical evidence: `seo-audit/2026-10/approved-legacy-redirects-2026-10-09.md`, corresponding CSV, `search-console-reported-urls-2026-10-09.json` and `indexing-fixes-2026-10-09.md` under that work root.

## Michael's approved retirement decisions

Use the existing redirect configuration and historical CSV as the exact source-to-target register. These are approved LHM migration decisions, not general client SEO policy.

- Old blog categories in the approved 1–17 list → `/blog`, rather than building category pages now.
- Retired WordPress feeds → `/blog`.
- Legacy WordPress resource URLs → `/`, retaining the specific old PDF-to-blog exception before broad wildcard rules.
- `/google-ads-health-thank-you` → existing `/thank-you`. That destination intentionally remains noindex and excluded from the sitemap. Verify conversion behaviour is preserved; do not change tracking.
- `/there-are-no-category-names-mentioned-in-the-provided-text` → `/blog`.
- No blanket redirect of all unknown 404s to home. New ambiguous mappings need a concrete disposition; keep existing approval context and avoid asking again for the exact known mappings.

Five historical crawled/not-indexed URLs lacked an explicit individual disposition in that repair: `/targeted-marketing/`, `/the-category-name-that-can-be-extracted-from-the-given-information-is-seo/`, `/webinar-2/`, `/webinar-booked/`, `/category/media/`. Recheck current behaviour and later decisions before proposing anything; do not treat this list as still broken automatically.

## Implementation details that matter

Astro uses non-trailing-slash canonicals (root excepted). Inspect `public/_redirects` and `functions/[slug].js` together. Cloudflare exact redirect rules required both slash forms; permanent slash normalization may use 308. Specific file rules precede broad `/wp-content/*` rules. WordPress emoji paths ignore the changing `ver` parameter when matching; preserved query strings can still have a correct clean homepage canonical.

Run `npm run build`, including the existing internal-link and `scripts/check-redirects.mjs` checks. These cover collisions, chains, built destinations, canonical agreement, noindex exceptions, slash-pair coverage, sitemap exclusions and rendered internal links. Preserve intentional `/thank-you`, `/appointment-booked` and email-signature exclusions.

## Historical acceptance baseline

On 9 October, all 125 URLs in the dated 404 report reached healthy destinations; the final 28 approved mappings comprised 24 to blog, three WordPress resource routes to home and one confirmation to thank-you. The 118 redirect and eight alternate-canonical report examples were healthy expected exclusions. All 99 sitemap URLs returned 200 with correct canonical/indexability. These figures describe that run only.

GSC's 404 report already showed validation started on 9 October; do not attribute that click to the agent or restart it blindly. The sitemap index was resubmitted through the browser after the connector returned insufficient permissions. Read the current status each month.

The monthly task authorises reviews and preparing/verifying bounded fixes using these dispositions. Preserve session release authority; if production release authority is absent in the scheduled context, complete the tested candidate and present it for approval rather than silently merging or deploying. Skill/plugin merge and installation are separate from website changes.
