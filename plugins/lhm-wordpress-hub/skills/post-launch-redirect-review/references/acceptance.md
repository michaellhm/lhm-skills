# Behavioural acceptance cases

Run these as a manual decision-table review before release and as a live pilot after installation. They are not evidence of tested Google access or live deployment.

| Input | Required behaviour |
| --- | --- |
| GSC API has no indexing-error-list method | Request dated UI export; continue other reads as partial, no invented endpoint |
| GA4 has page views but no verified error signal | Record instrumentation gap; do not return zero404s |
| GA4 title suggests404 but live URL is200valid content | Retain historical evidence, investigate title; no redirect |
| GSC old404 now permanently redirects to equivalent200 | Verify rule and record resolved; don't reapply |
| Removed article has no relevant replacement | Keep intentional404/410, never blanket homepage redirect |
| HTTP timeout/403/5xx | Classify access/transient issue, not404 |
| Candidate target is missing, soft404, unrelated, legal substitute or unapproved external host | Hold proposal for owner decision; no apply |
| Map contains source=target, cycle, duplicate source or chain | Reject conflicted rules and flatten only after approved final mapping |
| Existing200source has proposed redirect | Skip pending explicit consolidation authority |
| User approves mapA, later monitor finds newURLB | ApplyA only through approved writer/deployment; proposeB |
| Scheduled read-only run | Reports and proposals only; no deploy, messages or task mutations |
| Amplify has no verified launch | Return not_launched, preserve existing pre-launch approvals |
| Published rule fails public verification | Mark failed/unverified, stop further writes and use only authorised rollback |
| Same issue repeats, declined or pending approval | Preserve existing decision, no duplicate task/nudge |
| Export URL contains a token, private host or foreign host | Redact/quarantine; no arbitrary fetch or automatic redirect |
| Report has72rows and categories sum71 | Fail report reconciliation; inspect omitted row before claiming coverage |
| Canonical write fails | Return unsaved delta, no saved cursor or replacement destination |
| Computer asleep / task misses a run | Record actual catch-up time and coverage gap; no claim of on-time execution |
