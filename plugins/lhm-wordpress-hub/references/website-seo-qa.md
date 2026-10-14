# Website SEO QA — one section of completion QA

Use the coaching modes in `website-completion-qa.md`. Keep all results in the same completion report. These checks verify delivery quality; do not start a separate SEO strategy, keyword research or content rewrite project.

## Establish full coverage

Confirm the production origin, staging/live environment, approved URL conventions and pages intended for search. Build a deduplicated inventory from the approved sitemap/page list, accessible CMS/build route inventory, existing XML sitemaps (including child sitemaps) and internal links. Include public pages missing from the XML sitemap. Track redirect aliases and intentionally excluded pages separately. Do not crawl private/login URLs or uncontrolled parameter/calendar loops. If the list is large, process in batches and retain the complete inventory; never silently replace a full audit with samples.

For each in-scope HTML page, fetch HTTP status/headers and inspect the rendered page where needed. Record requested URL, final URL, canonical, source evidence and actual observations. Inaccessible routes, JavaScript rendering failures, unvisited URLs or unknown route coverage remain visible pending/blocked gaps. A sitemap alone is not proof of all-page coverage.

## Per-page checks

| Check | Required review |
|-------|-----------------|
| Status and redirects | Intended pages load successfully; catch broken/soft-404 pages, loops and unintended redirect chains. Check approved legacy redirects separately. |
| Title | Exactly one non-empty, descriptive `<title>` appropriate to the page and client; flag duplicates across the inventory and starter/default text. |
| Description | Exactly one non-empty, relevant meta description; flag duplicate descriptions across pages, placeholder text and conflicting tags. |
| H1 and headings | Apply LHM’s delivery convention: one visible, meaningful H1 per page, matching its purpose, with a logical H2/H3 structure. Record hidden template/duplicate H1s for review. This is a project QA convention, not a claim that Google penalises all multiple-H1 pages. |
| Canonical | One unambiguous intended canonical, normally an absolute production URL; validate approved exceptions, destination status, environment and consistency with redirects/sitemap. |
| Indexing | Check meta robots, X-Robots-Tag and effective robots.txt rules for this URL. Intended search pages must be eligible on production. Respect approved noindex exclusions and intentional staging restrictions. |
| Images | Check image requests and actual loading, including responsive/lazy-loaded images; inspect alt attributes for meaningful images, appropriate contextual descriptions and client-approved assets. Decorative images should have empty alt; do not demand keywords on every image. Image links/buttons need an accessible purpose. Review relevant CSS background imagery for loading and whether meaningful content has a text equivalent. |

Store one row per page with title/description values, H1 count/text, canonical, indexing observations, image issues, status and evidence links. Include cross-page duplicate groups and precise page/element locations for fixes. Character counts may be useful review hints, not arbitrary universal pass/fail limits. Do not mark image descriptions “updated” unless a change was actually made and verified.

## Sitemap validation and missing-sitemap repair

1. Discover sitemap URLs from robots.txt, the CMS/SEO plugin or build configuration, and common paths including `/wp-sitemap.xml`, `/sitemap_index.xml`, `/sitemap-index.xml` and `/sitemap.xml`. A single missing guessed path is not proof there is no sitemap.
2. Fetch and parse the actual XML response; a branded HTML error page returning 200 is not a sitemap. For indexes, validate every in-scope child sitemap. Check valid escaping/UTF-8, successful retrieval and protocol limits (50,000 URLs or 50 MB uncompressed per sitemap); split/index if needed.
3. Reconcile entries against intended indexable canonical URLs in the inventory. Use absolute URLs on the approved production origin. Flag missing intended pages, duplicates, staging hosts, redirects, broken URLs and unintended noindex/noncanonical/private URLs. Respect explicitly approved cross-site sitemap arrangements rather than silently changing them. Do not invent last-modified dates.
4. If missing, invalid or incomplete, **prepare a repair rather than merely reporting “missing”**. Inspect the platform and existing generator first. For WordPress, restore/configure the existing approved CMS/SEO sitemap mechanism; do not add a competing plugin or static file over a dynamic endpoint. For Astro, use the project’s existing sitemap integration/generator or prepare the appropriate build configuration; reconcile generated and dynamic routes and the production site URL. Verify current platform documentation when implementation details are needed. A small static site may use a generated XML file if no maintained generator exists and the project supports it; record how it will stay current.
5. Generate/configure against the verified route inventory in the authorised local/staging source, validate the result and show the exact proposed change. If no source/configuration access exists, prepare an implementation-ready handback with verified URL inventory and fix owner; keep repair blocked rather than fabricating files or claiming installation.
6. Apply only within the existing project permission ceiling. An explicit bounded “go ahead and fix it” can authorise the named repair within that ceiling. Deployment, live CMS/plugin changes, indexing-rule changes and GSC submission require their respective authority; ask only for the missing consequential step after preparing the concrete repair. Do not repeatedly ask for work already authorised. Back up changed settings/files and verify readback. Keep states distinct: missing/failing → prepared → applied → live-verified → submitted/processing.
7. After authorised deployment, fetch the production sitemap and revalidate contents and coverage. A local file or successful build alone cannot pass the live check.

## robots.txt review

Fetch the root robots.txt and inspect status, response type, relevant user-agent groups and effective Allow/Disallow matching for intended pages and rendering resources. Check unintended production blanket blocks, overly broad path rules, staging/domain mistakes and conflicting rules. Check a valid absolute Sitemap directive points to the verified production sitemap/index. An absent file may permit crawling, but remains a failed LHM delivery requirement until prepared/configured and verified; do not claim absence itself proves Google is blocked.

Propose the smallest environment-appropriate correction while preserving intentional restrictions. Do not replace the file with a generic “allow everything” template or add speculative crawler blocks. Robots.txt controls crawling; it is not access control or a reliable way to remove URLs from search. Do not add unsupported noindex directives there or block access to pages whose noindex Google needs to read. Keep staging restrictions until the authorised production launch, then verify the live configuration. Apply changes through the same bounded repair workflow as above.

## Close the sitemap → GSC loop

Confirm the correct verified GSC property covers the production URLs and the acting user has access. Compare existing submissions first: do not resubmit a correct unchanged sitemap merely to tick a box. For a new/repaired sitemap, prepare the exact live sitemap/index URL; submit through an authorised account/API operation or coach Jaimee through it when authorised. Record property, submitted URL, observed readback/status and any processing error. Pending processing remains pending; a successful request is not proof of successful processing or indexing. Missing GSC access is blocked independently of the site-side sitemap result. Recheck reported errors and representative URL indexing eligibility after launch; indexing itself may take time.

## Evidence and retest

Include inventory totals (expected, checked, excluded with reasons, unresolved), per-page results, sitemap coverage and validation, robots rules, prepared/applied repair links, live readback, GSC submission/processing evidence, owners and rechecks. Record fail/pending/blocked/not_applicable honestly. Delegate corrections to the builder/SEO owner where necessary, then repeat affected page checks and duplicate/coverage reconciliation. Do not return an overall completion pass with untested mandatory pages or incomplete required sitemap/GSC verification.

## Primary references

Consult current official docs when implementing a repair:

- [Google: build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: robots.txt introduction](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Google: image SEO best practices](https://developers.google.com/search/docs/appearance/google-images)
