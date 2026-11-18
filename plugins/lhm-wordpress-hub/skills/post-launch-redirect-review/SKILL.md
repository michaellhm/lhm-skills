---
name: post-launch-redirect-review
description: Monitor a launched WordPress or Astro website using Search Console, GA4, migration maps and HTTP checks; investigate 404s and soft 404s, automatically fix evidence-backed exact-match 404 redirects within an approved site scope, ask Jaimee about uncertain mappings, and verify the live result through the owning platform workflow. Use when the user asks for a post-launch website review, broken pages after launch, 404 analysis, GSC redirect fixes, or a scheduled post-launch redirect check.
---
# Post-launch redirect review

Own the evidence-to-decision loop after a website launch. Reuse `site-launch-qa` for launch acceptance, `analytics-tracking` for missing measurement, `rankmath-redirects` for approved WordPress mappings and `astro-build` for approved Astro changes. This skill coordinates evidence collection and redirect delivery through existing tools; it does not itself supply a Google connector or deployment script.

Read [client routing](../../references/obsidian-context-contract.md). Knowledge lives in the verified shared client record; reports and maps live in the verified Current Clients working folder under `post-launch-redirect-review/YYYY-MM/`. Never substitute the vault for an unavailable deliverables folder.

## Authority and modes

Default `review` applies when no site-specific execution authority exists. Under Michael's approved post-launch operating model, use `confident-auto`: fix qualifying exact 404 mappings automatically; bring uncertain mappings to Jaimee in chat, wait for her decision, then release approved changes and check them live. No repeated Michael approval is needed for changes within this recorded authority.

Before activating this mode for a site, bind production hostname, repository/branch, deployment route, accountable reviewer Jaimee (verified identity), report/chat destination, verified launch timestamp and the end of the 14-day daily-monitoring window. Record Michael's standing authorisation and Jaimee's setup acceptance. This authority covers scoped redirect-only commits, pushing/merging to main and the existing production deployment, followed by public verification. Do not broaden repository protections or credentials to obtain access. An unavailable/blocked release route is a capability gap, not permission to bypass it.

**Automatic eligibility requires all conditions:** source is a genuine current HTTP404 on the bound production host (not intentional removal, scanner path, transient failure or merely a historical report); one unique same-site equivalent200destination is supported by old content/approved migration inventory and matching page purpose; destination canonical is consistent and not a soft404; exact rule introduces no loop, chain, shadowing or existing-rule conflict. A model confidence score or similar slug alone is insufficient. Legal, booking, download, campaign and external-host mappings always go to Jaimee. No broad catches or regex. If no relevant replacement exists, explain why keeping404/410 may be appropriate.

`apply-approved`: show Jaimee the exact uncertain source, candidate target(s), evidence/reason and recommendation in the current chat or agreed review thread. Her explicit approval authorises that exact mapping and the bound redirect release route; do not ask her to approve a spreadsheet as a prerequisite. If a scheduled session cannot wait for her, persist `awaiting_jaimee` and resume only when the approval is available in the verified channel. Silence is not approval. Process independent qualifying matches without waiting for unrelated decisions. Never repeat pending questions each day unless evidence materially changes.

## 1. Resolve the site and execution environment

Read the client's overview/profile, Goals, Current Projects and website project notes, current BasicOps task and full relevant discussion/replies, migration map, launch checklist and prior run. Verify production hostname, launch time/timezone, platform, repository/environment and deploy owner; distinguish staging from production. Resolve the GSC property and GA4 property/stream by verified hostname ownership, not similar display names. Record account bindings without credentials. Read the installed writer skills before using them.

Confirm the site has actually launched. If not, return `not_launched` and use pre-launch QA rather than schedule an imaginary post-launch monitor. Carry inherited mapping approvals forward with their exact scope; unresolved legacy URLs remain review items.

## 2. Collect evidence and declare coverage

Set explicit launch-relative dates and the site's timezone. First manual run: 24 hours after verified launch. At that point collect all available post-launch evidence up to collection time, explicitly marking provisional/lagged GA4/GSC data. Later runs use the available last seven complete site-local days since launch plus the current live candidate checks; do not demand seven days of data before the first check. Short windows and recent data lag must be labelled. Record source date ranges, export times, pagination, sampling/thresholding, quotas and unavailable sources. A zero-row response is not a clean site when access or instrumentation is missing.

- **GSC Page indexing:** collect dated Not found (404) and Soft 404 examples through the authorised Search Console UI/export. The standard API exposes Search Analytics, Sitemaps, Sites and URL Inspection, not a bulk Page indexing error-list endpoint. Do not invent that endpoint. UI exports are examples/limited coverage, not an exhaustive crawl. If unavailable, ask for the export or mark this source missing; continue other evidence without claiming full GSC coverage.
- **GSC Search Analytics:** query/export page performance and paginate the chosen window; use it to prioritise known URLs and lost organic landing pages. It does not enumerate all 404s. URL Inspection adds indexed evidence for known candidates; it is not a live test and has quotas.
- **GA4:** discover supported metadata and the actual site's error instrumentation. Confirm the error-page title, a registered custom error dimension/event, or another evidenced signal before querying. Use compatible dimensions such as hostname/pageLocation or pagePathPlusQueryString/pageTitle and appropriate views/events/sessions metrics. Never assume a built-in HTTP-status dimension or a universal `404` event. Missing error-page tracking is an instrumentation gap, not zero errors. Do not install tracking under read-only authority.
- **Migration inventory:** reconcile approved pre-launch redirects, old and new sitemaps, internal-link crawl, and available server/CDN logs. Logs supplement GSC/GA4; do not pretend either tool sees every bot request. Exclude foreign hosts and isolate probing/scanner paths from genuine removed pages.
- **HTTP evidence:** check candidates on the verified public production host, recording status, Location chain, final URL, page title and canonical/indexability evidence. HEAD can differ from GET; verify relevant discrepancies with a bounded GET and rendered browser where needed. Distinguish real 404/410, soft 404 returning200, transient5xx, blocked403, existing correct redirects and valid live pages. Never turn failures/timeouts into404s.

Only fetch the verified public host and explicitly allowed destination hosts; reject private/local addresses, credentials in URLs and arbitrary destinations from exports. Inspect redirects before following across hosts. Cap checks at an agreed rate/batch; obey quotas and retry limits. Retain sensitive queries only in restricted raw evidence; remove personal data/tokens from reports and exclude sensitive URLs from automatic remediation.

## 3. Analyse before proposing

Normalise cautiously: keep host, case, trailing slash, encodings and meaningful query distinctions; do not silently merge different resources. Deduplicate by site + exact source + intended outcome, preserving provenance and the existing decision history.

For each candidate, explain likely cause and classify: already-resolved, fix-internal-link, restore-missing-content, redirect-to-equivalent, intentional404/410, investigate-soft404, transient-error, or needs-owner. Compare old content, approved sitemap and new target intent. A high-confidence match requires content/intent evidence, not slug similarity alone. Legal, booking, download, campaign and external-domain destinations require Jaimee’s explicit mapping review. Do not manufacture a replacement for removed content.

Prioritise actual affected users, organic clicks, internal links and business journeys; retain low-volume genuine failures. Do not invent affected-booking counts or equate views/sessions to patients. Show current status separately from historical GSC/GA4 evidence.

## 4. Keep evidence and ask in chat

Keep a dated evidence report, machine-readable exact mapping CSV and source/coverage manifest for audit and recovery. These support the work, not a mandatory review-list deliverable. Present only uncertain choices to Jaimee in chat; summarise automatic fixes and verified results afterward. Minimum map columns:
`site,source,target,proposed_status,classification,source_evidence,current_http,target_http,content_match_reason,priority,decision,approval_reference,verification_state`.

Include date ranges, known gaps, writer/platform, unresolved questions and approval digest. Leave targets blank for intentional removals or unresolved cases. Report numeric row totals and make summary counts reconcile with actual rows. Keep an applied/declined/deferred ledger so recurring runs do not re-propose unchanged decisions; revisit only after new evidence or the agreed date. A run with blocked sources is `partial` or `blocked_on_access`, never `clear`.

## 5. Release qualifying or Jaimee-approved mappings and verify

Refresh source/target evidence and existing redirect rules immediately before mutation. Snapshot/export original rules or record the repository base commit and exact diff for reversal. Avoid rules that shadow valid200pages; an exception requires explicit consolidation approval. Reject self-redirects, cycles, duplicate conflicting sources, missing/soft404 targets, chains and broad catches. Use exact301 mappings to the final relevant destination by default; respect approved query handling and platform matching semantics.

- WordPress/Rank Math: use `rankmath-redirects` and its dry-run/apply/verification route. Do not use it on Astro.
- Astro/Cloudflare: inspect the existing hosting mechanism first; `_redirects` is not assumed for Workers routes or every asset mode. Use `astro-build`/the site owner to prepare a redirect-only diff on an isolated branch/worktree, run build and redirect checks, commit and push, then merge/push to main via the repository’s supported release route under the bound authority above. Respect required checks/protections; exclude unrelated dirty work. Wait for the existing production deployment and verify the deployed commit before live checks. On WordPress use the registered writer rather than inventing a Git step. Do not change DNS, remove hosting or grant permissions. If no authorised deployment route exists, report the exact blocker and keep changes prepared, not falsely live.

Verify every applied source publicly: expected permanent status, correct Location and query behaviour, bounded hop count, final relevant200page, no cycle and canonical consistency. Check representative untouched live pages and booking paths. A deployed rule is not verified until public checks pass; if not, record failure, revert only this run’s redirect changes through the same authorised release route, verify restored behaviour and stop further writes. GSC can lag after a fix; record live success separately from Google's later recrawl. Never promise rankings or immediate report clearance.

## 6. Handoff and recurrence

Return report/map links, coverage, reviewed/applied/verified counts, owner and next action. BasicOps owns executable work; update it only under task/comment authority using `basicops-task-manager`. Update existing client knowledge with evidenced changed status and durable links. Save the same run's cursor/ledger only after successful write/readback; report an unsaved delta on failure. Do not send a report or create a task merely because a scheduled run completed.

Use [scheduling and pilot](references/scheduling.md) and [acceptance cases](references/acceptance.md). Run the first manual check **24 hours after verified go-live**, then schedule daily checks for **two weeks** using `confident-auto` within the bound site authority. Record timezone and first/last run; stop writes after the window expires and ask Jaimee whether weekly follow-up is useful. Do not silently continue a permanent schedule. No monitor begins before launch. The pilot and schedule setup belong to Jaimee; this skill does not independently create another schedule.
