---
name: digital-audit
description: "Runs the GA4-checkable portion of the client's Digital Audit — confirms GA4 is receiving data, lists conversion/key events, checks the Google Ads link, writes a report to the client's Drive folder, and files a BasicOps checklist task (including manual GTM/GSC items). Use this when the user says 'digital audit', 'audit analytics', 'check GA4 setup', 'check tracking', 'verify conversions', or 'digital audit for [client]'. Step 4 of the web project onboarding flow — GA4 checks are automated, GTM and Search Console stay manual (no connector exists for either)."
---

# Digital Audit

Automates what's checkable via the connected Google Analytics tool for Step 4 (Digital Audit) of the team's onboarding flow: confirms the property is live and receiving data, lists whatever conversion/key events are marked, and checks the Google Ads link. GTM and Search Console have no connector available, so those checks stay a manual BasicOps checklist item rather than being skipped.

Design rationale: `${CLAUDE_PLUGIN_ROOT}/../../docs/brainstorms/2026-07-31-digital-audit-brainstorm.md`

## Scope

Only the GA4-automatable part of Step 4. GTM container/tag checks and Search Console setup verification are listed as manual BasicOps subtasks, not automated — no MCP connector exists for either as of this writing.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/digital-audit/LEARNED.md` if it exists and apply any relevant entries.

No dependency on `client-data-collection` having run first. If GA4 access hasn't been granted yet, the property simply won't be found — report that plainly rather than blocking.

## Tool Access

The Google Analytics connector is a fixed server name (`analytics-mcp`) and can be referenced directly: `get_account_summaries`, `get_property_details`, `run_report`, `list_google_ads_links`. BasicOps and Google Drive are connection-specific — use `ToolSearch` to locate them by capability (see `client-data-collection`'s Tool Access section for the same pattern).

## Step 1: Identify the Client and GA4 Property

1. Ask (if not already known): business name and domain.
2. Call `get_account_summaries` and search the returned `property_summaries` for a `display_name` matching the client's domain.
3. If no match is found: note this plainly in the report and BasicOps task (see Steps 3–4) rather than stopping — GA4 access may simply not have been granted yet.

## Step 2: Run the Automated Checks

For the matched `property_id`:

1. **Receiving data**: `run_report` with `date_ranges: [{start_date: "30daysAgo", end_date: "today"}]`, `dimensions: ["date"]` (this tool rejects a dimension-less request — a pure-metrics call errors out even though the underlying GA4 Data API allows it), `metrics: ["activeUsers", "sessions"]`, `order_bys` on `sessions` descending, `limit: 1`. Pass if `row_count` is non-zero and the top row's metrics are non-zero.
2. **Conversion / key events**: `run_report` with `dimensions: ["eventName"]`, `metrics: ["eventCount", "conversions"]`, same date range. Rows where the `conversions` metric is greater than zero are the actual marked key events (this is how GA4's Data API distinguishes key events from regular events — the `conversions` metric only counts events marked as key events). List them by name. Flag if none exist.
3. **Google Ads link**: `list_google_ads_links` for the property. Pass if at least one link exists — note this is only relevant if the client runs Google Ads (check `client_profile.md` or ask if unsure).

## Step 3: Write the Report

Create a Google Doc titled `[Client Name] | Digital Audit` in the client's Drive folder (same folder as their Properties and Access sheet — find it by searching, don't hardcode). Structure:

- **GA4 Status**: property found (or not), receiving data (pass/fail with the actual numbers)
- **Conversion / Key Events**: list of what's marked, or "none marked" if empty
- **Google Ads Link**: linked / not linked / not applicable
- **Manual Checks Needed** (unchecked, for Kristalyn to verify by hand): GTM container installed and firing correctly, Search Console verified and sitemap submitted

## Step 4: Create the BasicOps Task

1. Create a task titled `Digital Audit — [Client Name]` in `*Web Projects → Onboarding & Briefing` (project id `68635`, section id `107719` as of 2026-07-31 — confirm live, don't hardcode blindly).
2. Add subtasks for each check, with status set based on the result:
   - `GA4 Receiving Data` — mark **Complete** if the check passed, leave **New** if it failed or the property wasn't found
   - `Conversion / Key Events Tracked` — mark **Complete** if at least one key event exists, leave **New** otherwise
   - `Google Ads Linked` — mark **Complete** if linked or not applicable, leave **New** if the client runs Ads but isn't linked
   - `GTM Container Check (manual)` — always starts **New**, no connector to verify this automatically
   - `GSC Setup Check (manual)` — always starts **New**, same reason
3. Link the Drive report in the task description.

## Step 5: Report Back

Tell the user:

- Pass/fail summary of the three automated checks
- The Drive report link
- The BasicOps task link
- Which items (if any) still need manual follow-up

## Rules

- Never guess a property match — if the domain doesn't clearly match a `display_name`, ask the user to confirm rather than picking the closest one
- Facts only in the report — state what the data shows, don't speculate about causes
- Don't mark a BasicOps subtask Complete unless the corresponding automated check actually passed
