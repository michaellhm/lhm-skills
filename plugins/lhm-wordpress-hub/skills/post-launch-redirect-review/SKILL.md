---
name: post-launch-redirect-review
description: Monitor a launched WordPress or Astro website using Search Console, GA4, migration maps and HTTP checks; investigate 404s and soft 404s, prepare relevant redirect proposals and implement only approved exact mappings through the owning platform workflow. Use when the user asks for a post-launch website review, broken pages after launch, 404 analysis, GSC redirect fixes, or a scheduled post-launch redirect check.
---
# Post-launch redirect review

Own the evidence-to-decision loop after a website launch. Reuse `site-launch-qa` for launch acceptance, `analytics-tracking` for missing measurement, `rankmath-redirects` for approved WordPress mappings and `astro-build` for approved Astro changes. This skill is an analysis and orchestration workflow, not a new Google API or unattended publisher.

Read [client routing](../../references/obsidian-context-contract.md). Knowledge lives in the verified shared client record; reports and maps live in the verified Current Clients working folder under `post-launch-redirect-review/YYYY-MM/`. Never substitute the vault for an unavailable deliverables folder.

## Authority and modes

Default `review`: read evidence, check public URLs and save a proposal. Scheduled runs always use review unless an explicit, still-valid standing approval names the exact site, mapping scope, owning writer, limits and expiry. An old redirect approval does not approve later discovered URLs. A schedule does not grant writing, sending, production deployment or account-access authority.

`apply-approved`: refresh the exact approved source/target/status list and record its approval evidence and digest. Route through the platform owner; changed mappings require renewed approval. No blanket homepage redirects, guessed regex, mass deletion, automatic legal-page substitution or permissions changes. Preserve intended 404/410 responses where no relevant replacement exists.

## 1. Resolve the site and execution environment

Read the client's overview/profile, Goals, Current Projects and website project notes, current BasicOps task and full relevant discussion/replies, migration map, launch checklist and prior run. Verify production hostname, launch time/timezone, platform, repository/environment and deploy owner; distinguish staging from production. Resolve the GSC property and GA4 property/stream by verified hostname ownership, not similar display names. Record account bindings without credentials. Read the installed writer skills before using them.

Confirm the site has actually launched. If not, return `not_launched` and use pre-launch QA rather than schedule an imaginary post-launch monitor. Carry inherited mapping approvals forward with their exact scope; unresolved legacy URLs remain review items.

## 2. Collect evidence and declare coverage

Set explicit launch-relative dates and the site's timezone. Suggested manual pilot: last seven complete local days since launch, plus preceding comparable data where available. Short windows and recent data lag must be labelled. Record source date ranges, export times, pagination, sampling/thresholding, quotas and unavailable sources. A zero-row response is not a clean site when access or instrumentation is missing.

- **GSC Page indexing:** collect dated Not found (404) and Soft 404 examples through the authorised Search Console UI/export. The standard API exposes Search Analytics, Sitemaps, Sites and URL Inspection, not a bulk Page indexing error-list endpoint. Do not invent that endpoint. UI exports are examples/limited coverage, not an exhaustive crawl. If unavailable, ask for the export or mark this source missing; continue other evidence without claiming full GSC coverage.
- **GSC Search Analytics:** query/export page performance and paginate the chosen window; use it to prioritise known URLs and lost organic landing pages. It does not enumerate all 404s. URL Inspection adds indexed evidence for known candidates; it is not a live test and has quotas.
- **GA4:** discover supported metadata and the actual site's error instrumentation. Confirm the error-page title, a registered custom error dimension/event, or another evidenced signal before querying. Use compatible dimensions such as hostname/pageLocation or pagePathPlusQueryString/pageTitle and appropriate views/events/sessions metrics. Never assume a built-in HTTP-status dimension or a universal `404` event. Missing error-page tracking is an instrumentation gap, not zero errors. Do not install tracking under read-only authority.
- **Migration inventory:** reconcile approved pre-launch redirects, old and new sitemaps, internal-link crawl, and available server/CDN logs. Logs supplement GSC/GA4; do not pretend either tool sees every bot request. Exclude foreign hosts and isolate probing/scanner paths from genuine removed pages.
- **HTTP evidence:** check candidates on the verified public production host, recording status, Location chain, final URL, page title and canonical/indexability evidence. HEAD can differ from GET; verify relevant discrepancies with a bounded GET and rendered browser where needed. Distinguish real 404/410, soft 404 returning200, transient5xx, blocked403, existing correct redirects and valid live pages. Never turn failures/timeouts into404s.

Only fetch the verified public host and explicitly allowed destination hosts; reject private/local addresses, credentials in URLs and arbitrary destinations from exports. Inspect redirects before following across hosts. Cap checks at an agreed rate/batch; obey quotas and retry limits. Retain sensitive queries only in restricted raw evidence; remove personal data/tokens from reports and exclude sensitive URLs from automatic remediation.

## 3. Analyse before proposing

Normalise cautiously: keep host, case, trailing slash, encodings and meaningful query distinctions; do not silently merge different resources. Deduplicate by site + exact source + intended outcome, preserving provenance and the existing decision history.

For each candidate, explain likely cause and classify: already-resolved, fix-internal-link, restore-missing-content, redirect-to-equivalent, intentional404/410, investigate-soft404, transient-error, or needs-owner. Compare old content, approved sitemap and new target intent. A high-confidence match requires content/intent evidence, not slug similarity alone. Legal, booking, download, campaign and external-domain destinations require explicit owner review. Do not manufacture a replacement for removed content.

Prioritise actual affected users, organic clicks, internal links and business journeys; retain low-volume genuine failures. Do not invent affected-booking counts or equate views/sessions to patients. Show current status separately from historical GSC/GA4 evidence.

## 4. Deliver a review pack

Save a dated report, machine-readable exact mapping CSV and source/coverage manifest. Minimum map columns:
`site,source,target,proposed_status,classification,source_evidence,current_http,target_http,content_match_reason,priority,decision,approval_reference,verification_state`.

Include date ranges, known gaps, writer/platform, unresolved questions and approval digest. Leave targets blank for intentional removals or unresolved cases. Report numeric row totals and make summary counts reconcile with actual rows. Keep an applied/declined/deferred ledger so recurring runs do not re-propose unchanged decisions; revisit only after new evidence or the agreed date. A run with blocked sources is `partial` or `blocked_on_access`, never `clear`.

## 5. Apply only the approved map and verify

Refresh source/target evidence and existing redirect rules immediately before mutation. Snapshot/export original rules or record the repository base commit and exact diff for reversal. Avoid rules that shadow valid200pages; an exception requires explicit consolidation approval. Reject self-redirects, cycles, duplicate conflicting sources, missing/soft404 targets, chains and broad catches. Use exact301 mappings to the final relevant destination by default; respect approved query handling and platform matching semantics.

- WordPress/Rank Math: use `rankmath-redirects` and its dry-run/apply/verification route. Do not use it on Astro.
- Astro/Cloudflare: inspect the existing hosting mechanism first; `_redirects` is not assumed for Workers routes or every asset mode. Use `astro-build`/the site owner to stage an exact diff, run build/redirect checks and obtain the required deployment approval. Do not change DNS, remove Vercel or publish merely because mapping approval exists.

Verify every applied source publicly: expected permanent status, correct Location and query behaviour, bounded hop count, final relevant200page, no cycle and canonical consistency. Check representative untouched live pages and booking paths. A deployed rule is not verified until public checks pass; if not, record failure, perform only authorised rollback and stop further writes. GSC can lag after a fix; record live success separately from Google's later recrawl. Never promise rankings or immediate report clearance.

## 6. Handoff and recurrence

Return report/map links, coverage, reviewed/applied/verified counts, owner and next action. BasicOps owns executable work; update it only under task/comment authority using `basicops-task-manager`. Update existing client knowledge with evidenced changed status and durable links. Save the same run's cursor/ledger only after successful write/readback; report an unsaved delta on failure. Do not send a report or create a task merely because a scheduled run completed.

Use [scheduling and pilot](references/scheduling.md) and [acceptance cases](references/acceptance.md). Run a manual pilot before enabling recurrence; suggested daily review during the first two post-launch weeks, then weekly until the migration backlog is resolved. These are proposals, not approved schedules. Confirm actual cadence, timezone, site scope, owner and report destination. Never start monitoring before a verified launch or infer a schedule from this suggestion.
