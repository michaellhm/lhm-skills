---
name: meta-tag-refresh
description: "Data-driven title tag and meta description refresh for client websites (new builds, relaunches, or periodic refreshes), with GSC decline analysis, slug audit, and direct push to WordPress via the Rank Math REST API including 301 redirects for slug changes. Use this whenever the user wants to update, review, audit, or rewrite title tags, meta descriptions, SEO metas, or page slugs; mentions 'title tag refresh', 'meta refresh', 'new site metas', 'push metas to WordPress', 'which pages dropped off in GSC', 'declining pages', or 'slug cleanup'; or is launching a new/staging site that needs its metadata reviewed before go-live. Also use for standalone GSC period-over-period decline analysis even if no meta rewrite is requested."
---

# Meta Tag Refresh

Rewrite a site's title tags and meta descriptions from evidence, not guesswork: 12 months of paid conversion data, GSC organic performance including period-over-period declines, keyword volumes, and the ad copy angles that already earn clicks. Deliver as an approval spreadsheet, then push approved changes straight into WordPress through the Rank Math REST API, including slug changes with automatic 301 redirects.

The core belief behind this skill: a keyword that converts in paid search is a proven commercial-intent signal that outranks any volume estimate, and description copy that wins clicks in ads will win clicks in SERPs. Titles are written from what books appointments, not what a volume tool says.

## Phase 0 — Context

1. Read `[client-folder]/client_profile.md` and `[client-folder]/goals.md` if present. Determine whether this is a health client (AHPRA rules apply to every word you write — see `references/copy-rules.md`).
2. Find WP credentials: look for `[client-folder]/wp-access.md` (Site URL, Username, Application Password). If missing and a push is expected, create the file with placeholders and ask the user to fill it in. Never ask the user to paste credentials into chat.
3. Identify the GSC property (`list_properties`), the Google Ads account (check `[client-folder]/google_ads/` for account IDs in prior reports), and confirm which site to crawl (live vs staging — they often differ during a rebuild).
4. Scan `[client-folder]/seo/` for prior snapshots. If none exist, this session establishes the baseline — say so.

## Phase 1 — Crawl the site

Get every page plus its current title and meta description.

1. Try `GET {site}/wp-json/wp/v2/pages?per_page=100&_fields=id,link,title,parent` and `GET {site}/wp-json/wp/v2/types` to discover custom post types (location pages are often a CPT like `clinic_location`). Fetch each CPT's posts too. Record post IDs — you need them for the push phase.
2. Fetch each URL and parse `<title>` and `meta[name=description]`.
3. Staging hosts frequently block server-side fetches (empty responses with HTTP 200). If `web_fetch` returns empty bodies, switch to the Claude in Chrome browser tools and run the crawl via `javascript_tool` fetch calls from a tab on the site — the user is usually logged into WP admin there, which also sets up Phase 5 auth. See `references/wordpress-push.md` for working snippets.
4. Note anything unexpected: swapped metas between pages, missing descriptions, noindex flags (normal on staging, fatal in production — flag both directions), pages the user didn't mention.

## Phase 2 — Mine the data

Run these in parallel where possible. Full query recipes: `references/data-mining.md`.

**Google Ads (12 months):**
- Converting search terms segmented by `segments.conversion_action_name`. This matters because accounts often have soft conversion actions (booking page views, scroll events) inflating the default conversions column — segment so real bookings/leads are distinguishable from proxies.
- Top search terms by clicks/cost (volume signal).
- Ad-level CTR since the last copy refresh, and RSA asset texts by impressions. Asset-level clicks aren't reported by Google, so use ad-level CTR + conversion data to identify which description angles earn clicks.
- Check the client's `google_ads/` folder for prior RSA refresh reports — they often contain compliance decisions and proven angles you must honour.

**GSC (two pulls):**
- Standard: last 180 days, `query` and `page` dimensions. Gold to look for: high-impression low-CTR queries (title/description problem), page-two rankings for money terms (priority targets), brand variants (including misspellings/plurals people actually type), old-site URLs with traffic that need 301 mapping.
- **Decline analysis: last 6 months vs the prior 6 months.** Compare page-level clicks and impressions between the two windows. Rank pages by absolute impression and click loss. For each of the top 5-10 decliners, pull per-page queries for both windows and identify which specific queries dropped. Then classify each dropped query by intent: commercial/booking intent (treatment, clinic, cost, near me, book) vs informational. Pages losing commercial-intent queries are the top optimisation priority and should be called out as such in the deliverable — a blog post shedding informational long-tail matters far less than a service page sliding off page one for a money term.

**Keywords Everywhere:** volumes/CPC for every candidate title keyword (country set to the client's market). Critical calibration: KE reports zero for most suburb-level and low-volume local terms that GSC and Ads prove are real and converting. First-party data always wins the argument; use KE only to size head terms and spot trends (a term whose 12-month trend is climbing deserves weight beyond its average).

## Phase 3 — Slug audit

For every page crawled, evaluate the slug:
- Flag slugs longer than ~5 words or ~60 characters, slugs with stop-word padding, dates, or redundant phrasing (blog posts are the usual offenders).
- Recommend a shorter keyword-focused slug only when the gain is real. A slug change on a page with existing rankings/backlinks is a cost (redirect dilution, re-crawl lag) — recommend it only when the current slug is genuinely bad, and say why.
- Every slug recommendation goes in the spreadsheet with a "301 required" column set to yes. Slug changes are never pushed without explicit approval, and never without the redirect created in the same operation.

## Phase 4 — Write and deliver

Read `references/copy-rules.md` before writing a single title. It covers: length limits, brand placement, the clinic-vs-treatment converting-language pattern, description angle selection from ad data, AHPRA constraints for health clients, and formatting rules (no em dashes anywhere).

Build one spreadsheet (xlsx skill; use LEN() formulas for character counts so the user can edit copy and see counts update; run recalc before delivering):

| Sheet | Contents |
|---|---|
| New Meta Tags | URL, page, current title/description, NEW title (+live char count), NEW description (+live char count), primary keywords/signals, rationale citing the data |
| Keyword Data | KE volumes + CPC, conversion signal from Ads, calibration notes |
| Converting Search Terms | top converting terms 12m, conversion types, where each maps on the site |
| GSC Opportunities | high-imp/low-CTR queries, positions, action taken |
| GSC Declines | pages ranked by 6mo-vs-6mo loss, dropped queries per page, intent classification, priority flag |
| Slug Recommendations | current slug, proposed slug, reason, 301 required |
| Notes & Launch Checklist | data sources + windows, compliance rules applied, issues found in crawl, redirect mapping needs, phase-2 page recommendations (keywords with volume that deserve dedicated pages) |

Save the spreadsheet and a session summary markdown to `[client-folder]/seo/YYYY-MM/`. The summary doubles as the ranking baseline for the next session — include current positions for the target terms.

**Stop here and get explicit approval before touching WordPress.**

## Phase 5 — Push to WordPress

Full tested recipes with auth fallbacks: `references/wordpress-push.md`. Summary:

1. Authenticate: try the Application Password (Basic auth) against `GET /wp-json/wp/v2/pages/{id}?context=edit`. Many hosts strip the Authorization header (symptom: 401 `rest_forbidden_context` despite correct credentials) — fall back to the user's logged-in browser session using `wpApiSettings.nonce` from any wp-admin page. Tell the user which path worked; if Basic auth failed, suggest they ask the host to enable the HTTP_AUTHORIZATION rewrite.
2. Meta updates: `POST /wp-json/rankmath/v1/updateMeta` with `{objectType:'post', objectID, meta:{rank_math_title, rank_math_description}}` per page. Works for pages, posts, and CPTs alike.
3. Approved slug changes: first create the 301 via `POST /wp-json/rankmath/v1/updateRedirection`, then update the slug via `POST /wp-json/wp/v2/{rest_base}/{id}` with `{slug}`. If the user's `rank-math-301-redirect` skill is installed (WordPress hub), prefer delegating redirect creation to it.
4. Update one page first, verify it renders on the frontend, then batch the rest.

## Phase 6 — Verify and log

- Re-fetch every updated page (cache-busting query param) and compare rendered title and description against the approved spreadsheet, exact match. Report N/N.
- For slug changes: confirm the new URL resolves 200 and the old URL 301s to it.
- Append an implementation note to the session summary: what was pushed, auth path used, verification result, anything deferred.
- Suggest a re-check of rankings 6-8 weeks out against the baseline snapshot.

## Deferral notes

- Full site restructure / information architecture → WordPress hub `sitemap-architect`.
- Writing new page content (not just metas) → content agent / `service-page-generator`.
- Ongoing local SEO and GMB → GMB hub.
