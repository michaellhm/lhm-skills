# Claude Code Desktop pilot and scheduling

Verified documentation 19 November 2026:
- https://code.claude.com/docs/en/desktop-scheduled-tasks
- https://code.claude.com/docs/en/scheduled-tasks
- https://developers.google.com/webmaster-tools/v1/api_reference_index
- https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema
- https://support.google.com/webmasters/answer/7440203
- https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes

Refresh documentation when installing; UI labels and runtime capabilities can change. Claude Code `/loop` is session-scoped, not the durable operating schedule. Desktop local scheduled tasks persist as configuration but execute only while the computer is awake and the app is running; runs can be missed or caught up later. Cloud schedules need separately verified repository, tools and authorised data access; don't assume local connectors/vaults carry over.

## Jaimee setup checklist

1. Verify the reviewed skill release is merged and actually installed in Jaimee's Claude Code environment. A pushed feature branch is not installed. Record version/commit. Do not merge/install without release authority.
2. Pick one actually launched site, verify production hostname, GSC/GA4 bindings and access in her own runtime, existing migration task, repo and canonical work/knowledge folders. No credentials or account permissions in prompt files.
3. Run the skill manually in review mode. Include a real known404 and a healthy200 control if available, using read-only requests; do not deliberately break the live site. Demonstrate dated GSC coverage/export gaps, actual GA4 error signal or explicit instrumentation gap, exact map, owner decisions, safe deduplication and saved/read-back report. Confirm absent sources produce partial coverage.
4. Agree cadence/timezone and reporting destination with Michael. Suggested daily during first two weeks after launch then weekly is not approval. Start only after launch and manual acceptance. Keep one active monitor per site and one run lock; reconcile previous interrupted runs before continuing. Do not overlap with existing site monitors.
5. In Claude Desktop's Code tab use Scheduled (or its displayed equivalent), create a local scheduled task, choose the verified working folder and agreed trigger/timezone. Use Manual/paused configuration until approved, if available. Keep normal scoped permissions; do not enable bypass mode or blanket tool allowances. If a scheduler tool is unavailable, provide setup instructions; never hand-edit private scheduler state.
6. Paste the prompt below with verified values. Test Run now, inspect its session/report, reconcile permissions and coverage, then verify the actual saved trigger and next run. Report configuration versus a successful scheduled execution separately. Record missed runs as gaps; do not fake historical runs or dates.

## Copyable scheduled prompt

Run `lhm-wordpress-hub:post-launch-redirect-review` in REVIEW mode for [verified site and task link]. Read its installed SKILL.md and current client website/launch records. Use only [verified GSC property] and [verified GA4 property/stream], the approved migration map, dated GSC404 export and permitted public HTTP checks. Read the previous run/decision ledger from [verified working folder]. If launch, account bindings or required folders cannot be verified, stop dependent work and report the gap. If GSC export or GA4 error instrumentation is unavailable, continue supported reads and label coverage partial; never report a clear site from missing data. Use the last seven complete site-local days since launch and record collection time, data lag, pagination and any late-run gap. Deduplicate unchanged pending/declined mappings. Save and read back the dated report, exact proposed mapping CSV and coverage manifest under post-launch-redirect-review/YYYY-MM/. Return new issues and changes needing review to [agreed report surface]; do not send or post unless that destination/action is separately authorised. No live redirect changes, deployments, tracking changes, account grants, emails or new schedules. Report the exact next owner/action and distinguish verified fixes from proposals. One run per site at a time; skip/merge safely when another run owns it.
