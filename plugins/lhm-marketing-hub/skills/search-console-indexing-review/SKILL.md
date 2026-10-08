---
name: search-console-indexing-review
description: Review Google Search Console Page indexing, diagnose live URLs, implement authorised fixes and verify Google validation. Use when the user mentions "pages aren't indexed", "404s", "page with redirect", "alternate page with proper canonical tag", "crawled currently not indexed", or a "monthly Search Console indexing review".
---

# Search Console indexing review

Run a URL-level review, separating Google's dated report from current website behaviour. Success means intended canonical pages are accessible and eligible for indexing, with verified fixes and an honest Google validation status. Excluded URL totals need not reach zero.

## Establish scope and evidence

1. Confirm the exact Search Console property, canonical host, registered website source, publishing route and authority from the user/client record. Preserve unrelated website changes. Read repository instructions and Git status before editing.
2. Read the previous run and outstanding decisions. For Local Health Marketing, read [the site contract](references/local-health-marketing.md). Its dispositions belong to that site; do not apply them to other clients.
3. Prefer available connectors for supported operations. Page indexing exports and URL Inspection may require the user's authenticated browser. Read the current UI before acting. If a connector lacks permission, use an already authorised browser route; do not broaden account permissions or invent results.
4. Capture report date, indexed/excluded totals, each exclusion reason, available URL examples and validation status. Export all available rows for 404, redirects, alternate canonicals, crawled/discovered not indexed and noindex. State export limits; examples are not necessarily the full population. Keep source URLs and query strings intact.
5. Save dated raw evidence and a URL action table under the verified client work root at `search-console-indexing-review/YYYY-MM/`. Include reported reason, live first response, redirect hops, final URL/status, HTML canonical, meta robots, X-Robots-Tag, intended disposition, proposed/implemented action and verification time. Retain prior runs for comparison.

## Diagnose live behaviour

Fetch each reported URL and follow redirects with a bounded hop limit. Inspect destinations, not just the initial status. Fetch the sitemap index and child sitemaps and check current canonical URLs. Use a descriptive user agent and distinguish a client-specific 403 from evidence Googlebot is blocked. Respect server capacity with modest concurrency and timeouts; record failures separately.

- **404:** Restore accidentally missing current content, or permanently redirect a moved page to its verified closest replacement. A genuinely retired page without a replacement can remain 404/410. Never infer a replacement from a similar slug alone. Prepare concrete unresolved mappings for the user. No blanket homepage catch-all. Honour previously approved site-specific retirement dispositions without asking again.
- **Page with redirect:** Usually expected. Fix broken targets, loops, unnecessary chains and internal/sitemap links pointing at old URLs. Prefer a single permanent hop to the final canonical page. Keep valid redirects; do not force the old URL into the index.
- **Alternate page with proper canonical tag:** Verify the canonical resolves to an indexable 200 page, matches intended content and agrees with sitemap/internal links. Correct actual conflicts. Keep intentional duplicates, query variants and slash alternatives consolidated. Do not remove valid canonical tags to index every variant.
- **Crawled - currently not indexed:** First distinguish retired migration URLs from current canonical content. Resolve migration URLs using authorised mappings. For current pages, inspect Google's selected canonical and live render, response headers, robots access, noindex, sitemap inclusion, internal discoverability, duplicate/near-duplicate content and whether the page provides useful unique information. Rank important service/content pages first. Recommend specific improvements supported by evidence; no arbitrary word-count requirement, automatic rewriting, or promise of indexing. Semantic consolidation, new category architecture and substantial content changes require recorded scope or a concrete user decision.
- **Discovered - currently not indexed:** Check accessibility, sitemap and useful internal links, then inspect crawl evidence for important pages. Being accessible does not prove Google has crawled/indexed the page.
- **Noindex:** Preserve intentional confirmations, private utilities and other deliberately excluded pages. Fix accidental noindex only on intended public search pages. Keep intentional noindex pages out of sitemaps.

Canonical comparison must normalize the bare origin/root slash and ignore harmless query preservation when the page's canonical correctly points to the clean destination. Do not strip meaningful parameters from recorded source evidence or assume all query variants are equivalent.

## Implement and verify

Apply reversible technical fixes within existing authority: confirmed legacy mappings, exact redirect rules, incorrect internal links, sitemap references and proven canonical/noindex mistakes. Do not change production access, domain configuration, tracking, forms or unrelated content. Prepare unapproved semantic choices for review while completing independent authorised fixes.

Before publishing, check exact slash/non-slash paths where the host matches them separately; query behaviour; wildcard ordering; collisions across static redirects and functions; missing targets; loops/chains; self-canonicals; noindex exceptions; and internal/sitemap URLs. Run the repository's relevant build and checks. Commit only scoped files when authorised and use the registered release route; production release requires authority from the session/standing site contract. Do not infer release authority merely from this skill existing.

After deployment, recheck every changed URL on the production domain: intended permanent response, final 200 and expected canonical/robots. Check current sitemap URLs and relevant internal links. A preview build or pushed commit alone is not evidence the live fix shipped. Record commit, deployment and before/after results; retain a recoverable rollback point.

## Google validation and monthly handoff

Read current validation status first. Preserve an already running validation; do not start duplicate requests. Start validation only for genuinely repaired issues after live verification and when the covered URL population is ready. Leave valid redirects, alternate canonicals, intentional noindex and deliberate removals excluded. Submit an updated sitemap when warranted; record confirmed submission separately from attempted requests. Request indexing selectively for important improved canonical pages using available supported tools; do not repeatedly request every URL.

Report separately: live fix verified, Google validation pending/passed/failed, and indexing observed. Google's counts lag; never claim indexed from a 200 response or successful live test. Compare monthly runs, identifying new issues and outstanding decisions without replaying completed fixes. Save current status, next action and resume point even if access is unavailable. A missing report is an access failure, not a clean bill of health.

Before giving new technical SEO advice, verify relevant current official Google guidance:
- https://support.google.com/webmasters/answer/7440203
- https://support.google.com/webmasters/answer/9012289
- https://support.google.com/webmasters/answer/2445990
- https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

For an automated run, finish authorised bounded work, capture concrete decisions requiring Michael and avoid duplicating schedules. Use the host's native scheduler only when requested. Never send client/team messages without explicit messaging authority.
