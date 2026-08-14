---
name: google-ads-existing-client-adoption
description: Adopt an established Google Ads client into LHM's governed monthly review system without treating it as a new campaign build. Use when Michael asks to onboard, adopt, migrate, prepare, or make an existing Ads client monthly-flow-ready, including a one-client pilot before portfolio rollout.
---

# Existing Google Ads Client Adoption

Prepare one live client account for repeatable Hermes-led monthly reviews. Preserve existing strategy and history. This workflow is read-only in Google Ads and creates no execution subtasks or campaign changes.

Do not invoke `google-ads-kickoff` unless the client is genuinely starting a new account or campaign build. Tracking concerns lower confidence and create actions; they do not block adoption by themselves.

## 1. Resolve canonical context

Hermes resolves and reads the client overview, `client_profile.md`, goals, current projects and `project-management/Google Ads.md`. Load the active LHM Google Ads optimisation framework supplied in the context envelope. Never create blank files beside the plugin.

Confirm the client is an existing live account. Work on exactly one client per run.

## 2. Build the readiness register

Classify every item as `verified`, `gap`, `warning` or `blocked`:

- canonical client identity and established label
- Google Ads CID and MCC
- account owner and compliance regime
- business objective and capacity constraint
- primary, secondary and excluded conversion definitions
- monthly budget, business CPA/ROAS targets and AdPulse budget ID
- clinic locations, service area, exclusions and presence/interest policy
- live campaign map, budgets, bidding, conversion goals and destinations
- 3-, 6- and 12-month baselines where account age supports them
- canonical Google Drive Ads folder
- existing BasicOps client/review route
- current position in the Month 0/1/2/3 optimisation loop
- latest experiment, prior commitments and unresolved decisions

Hard blockers are limited to unresolved client/account identity, lack of authorised read access, or a missing canonical destination needed for delivery. Missing budget, AdPulse, conversion or tracking evidence is normally a visible gap or warning that the first review can help resolve.

## 3. Gather live evidence

Route a bounded read-only pull through the Google Ads specialist. Fetch only evidence needed to populate the readiness register and baselines. Reconcile live state against the existing project file; never overwrite a documented decision merely because a current setting differs.

When conversion evidence is suspicious, request the available GA4 cross-check. Record unavailable evidence explicitly and continue where supported.

## 4. Enrich the canonical project file

Hermes updates `project-management/Google Ads.md` in place. Preserve useful history and add or complete these sections rather than replacing the note:

- account and ownership
- objectives, economics and capacity
- conversion framework
- geography and exclusions
- campaign strategy and live map
- budget, targets and AdPulse
- performance snapshot and monthly ledger
- 90-day loop position and current experiment
- commitments, decisions and guardrails
- Drive and BasicOps delivery registry
- adoption readiness and exact gaps
- run history and next handoff

Link the agency optimisation framework; do not copy its full checklist into every client note.

## 5. Run the first delivery test

Prepare the first read-only monthly review using `lhm-marketing-hub:google-ads-monthly-review`. Hermes sends the finished report to the configured ChatGPT/Codex monthly-review delivery bridge. The worker saves and verifies the Drive report and creates or updates the BasicOps review parent through `lhm-project-hub:basicops-task-manager`.

Require both verified URLs. Do not create execution subtasks. If either is absent, record `analysis complete; delivery incomplete` with the resumable delivery run ID.

## 6. Mark readiness

Set `monthly_flow_status` in the project file:

- `ready` — identity, access and destinations verified; first Drive and BasicOps delivery verified
- `ready_with_warnings` — delivery works but named evidence/measurement gaps remain
- `blocked` — a hard blocker prevents a trustworthy first review or delivery

Return a compact handoff containing the project-file path, verified Drive and BasicOps URLs, readiness state, remaining gaps and the exact next question for Michael. Stop for his direction; do not execute proposed Ads actions.

## Portfolio boundary

This skill adopts one client only. A later portfolio orchestrator may invoke it sequentially, but it must wait for the current client's verified handoff before selecting the next client. Never auto-roll the pilot outcome across all clients.
