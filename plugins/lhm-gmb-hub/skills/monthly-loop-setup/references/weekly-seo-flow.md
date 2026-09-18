# Monday SEO reporting and work handoff

## Authority and selection

Hermes is a router only. All source research, diagnosis, report writing and delivery work runs through registered Claude CLI or Codex CLI workers. Hermes may read the canonical Client Flow selection table, submit/poll workers, preserve returned artefacts and receipts, and summarise verified results. Never fall back to native Hermes research, direct MCP analysis or report writing.

Use one portfolio schedule, Australia/Melbourne Monday morning (default 08:00, DST-aware). Read `20 Clients/Client Flow.md` every run: use **SEO week**, not Ads week; omit ads-only and unconfirmed-scope clients. Use the same verified four-week anchor as the live Ads scheduler; do not infer ordinal calendar weeks. Preserve explicit reschedules and due exceptions. Do not hard-code a permanent client list or assume four clients are always due. One client with multiple profiles produces one shared queue.

Before registration, inspect existing relevant schedules. Never repurpose the internal LHM website SEO rollout or an unrelated flow. Existing overlapping client automations must be identified, not silently deleted. Record candidate schedule, active/paused state, source commit, worker capability proof, rollback and next run in Obsidian.

## Worker contracts

1. Research worker loads `lhm-gmb-hub:monthly-cycle-report`, canonical goals/state, last report, each profile tracker, current meeting wraps/Fathom, client-flow card and relevant personal-board tasks/discussions, GA4, Search Console and Google Ads evidence. Return one-page overview, evidence, coach, source coverage, existing-task reconciliation and concise digest highlights. Sources may be unavailable; label them and continue only useful grounded analysis.
2. Delivery worker saves and reads back all files in the registered client `gmb/monthly-optimization/YYYY-MM/` directory, preserving IDs. It creates or reuses one review/work parent through `lhm-project-hub:basicops-task-manager`; reconcile existing actions and link them rather than creating duplicate execution subtasks. Use the verified human owner's Inbox unless an explicit route applies. Discussion contains highlights, ordered next steps, dependencies, done condition, next handoff and actual AI authorship. Description contains only governed metadata and URLs. No publishing, profile/account changes or automatic phase advancement.
3. Digest worker uses only verified returned highlights and BasicOps/Drive links. One email includes a short section per selected client: traffic light with reason, programme stage per relevant location, up to four useful highlights, next action and native BasicOps card link. Plain English; technical detail stays in Drive. Production recipient/CC come from the approved verified configuration, normally Jaimee with support copied. Do not infer an address from a name. No client recipients.

Use a durable run ledger: portfolio week, client, reporting period, source commit, research run ID, delivery run ID, file IDs, BasicOps ID, email message ID and state. Stable client-period keys deduplicate retries; retain existing parent IDs. Record intent before external writes and reconcile an uncertain outcome before retrying. Do not resend an email on a timeout. A task's existence is not a completed SEO pass. Failed clients remain visible in a partial digest; never label them green or omit them silently.

## Capability and activation gate

Prove that the selected worker can access each required system and exact destination before enabling unattended operation. An Ads-only worker is not an SEO research worker; a no-MCP specialist is only suitable for analysis of an explicitly supplied evidence pack. Do not rename such a route or claim it gathers live evidence. Existing Ads delivery cannot be used if it forces Ads folder/metadata or wrong recipients. Do not widen authentication or permission grants as an incidental fix.

Install from a clean immutable published commit with a recoverable prior copy and verify hashes. Keep research skills on workers; the Hermes-installed orchestration instructions only select, dispatch and verify. Register the Monday schedule paused when required research/delivery capabilities have not passed. Report the exact gap and owner; no native fallback.

## One-client test

An explicit test request may waive the time/rotation guard for one named client. Use a distinct test key, Michael's verified personal Inbox and Michael-only email when requested. Do not copy the production audience. Review sources/boards, generate the pack and card, send once and verify each result. State separately whether this was a full unattended VPS CLI test, a supplied-evidence worker test, or local Codex-assisted delivery. A local/manual success does not enable the unattended cron. Record reviewer feedback and activate only after the complete intended route passes and the pilot release is accepted.

## Acceptance checks

- Four-week rollover and DST select the intended SEO cohort; SEO-not-in-scope is omitted.
- Existing completed meeting action is not recreated; open linked work keeps its owner.
- Multiple locations share one parent and digest section, retaining distinct stages.
- Missing connector or failed child is visible, with no native Hermes fallback.
- Repeated test/run reuses its receipts and never creates duplicate tasks/email.
- Michael-only test cannot use production recipients.
- Report-only invocation cannot mutate boards or send email.
