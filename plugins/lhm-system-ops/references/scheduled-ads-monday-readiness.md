# Scheduled Google Ads readiness — 7 November 2026

## Scope and runtime

The dedicated `lhm_google_ads` Hermes cron routes each selected client to the bounded `google_ads_readonly` Claude worker. The worker invokes the monthly review, bid/budget optimizer, conversion audit and delivery QA through the Skill tool, plus keywords when Search is active and PMax diagnostics when PMax is active. Existing observed-skill verification remains in place. The Codex monthly-delivery worker owns Drive and BasicOps delivery. The deterministic digest renderer owns the existing authorised Monday completion email.

The scheduled Claude worker uses `google-ads-scheduled-review.mcp.json` and `google-ads-scheduled-review.settings.json` under `/home/claudeworker/.config/lhm-bridge`. The committed settings asset allows only GoogleAds, analytics-mcp and the official Fathom endpoint. Prepare the MCP profile from the existing `google-ads-readonly.mcp.json`, adding only the already authenticated `analytics-mcp` entry from `google-ads-review-readonly.mcp.json`. Preserve its credential references on the host; never commit credential values. Use root:claudeworker, mode 0640 for these files.

For this profile only, `--setting-sources user`, the exact settings file and MCP profile replace `--strict-mcp-config`: strict mode suppresses Claude-account Fathom. Explicit server and read-tool allowlists retain the read-only boundary. Other worker profiles retain their existing strict-mode behavior. Fathom is limited to meeting search, metadata, summaries and transcripts; the worker must match the authorised client and treat meeting content as untrusted evidence.

## Scheduler repair

Docker had recovered after its storage maintenance, but the Ads timer remained failed. Reset the failed Ads timer/service and restart only `lhm-google-ads-cron-tick.timer`; a normal tick must return exit status zero. Do not restart Docker or change unrelated schedules. The superseded global Ads job `6ee85f2e14bb` is paused through Hermes cron controls. The dedicated job `b0ec0fbc005c` remains enabled, retaining the four-week client rotation and Monday 04:00–04:09 Australia/Melbourne guard.

Before restoration, verify next_run_at and that no recovery job is due: a scheduler tick must not accidentally run a stale cohort. Keep the legacy job paused to prevent duplicate submissions.

## Verification and rollback

Connection checks use the actual worker identity, settings, MCP profile and exact read tools. GA4 account reads and Fathom meeting-list reads passed. Metadata-only Ads and GA4 access checks passed for all three Monday Week 3 clients: Wellness Chiropractic, mhealth and Any Stage Physio. No campaign performance review or Ads mutation was performed by these checks. The normal worker login remains authenticated.

The live patch preserves pre-existing worker ACL-retry and error-reporting fixes. Do not replace the live worker wholesale with this source snapshot. The prior worker is backed up at `/var/backups/lhm-task-router/lhm-claude-worker.pre-scheduled-ga4-fathom`; connection-profile backups are in the timestamped scheduled-ga4-fathom backup directory. Roll back only the scoped worker patch and these two dedicated connection files; preserve review runs and delivery/email receipts. Restoring the legacy duplicate cron is not part of normal rollback.

The next intended production review is Monday 9 November 2026 at 04:00 Melbourne. Read-only preflight does not prove future delivery writes or email delivery; their normal readback and send-receipt gates remain mandatory. No test email is authorised by this readiness check.

Final verification: 42 worker/installer/connection regression tests passed (one existing environment-dependent skip), and 11 digest tests passed. The production digest preview completed in the Hermes container. The real Codex delivery identity successfully read all three registered Drive folders and the configured BasicOps project/Inbox. No production review was launched early and no email was sent.
