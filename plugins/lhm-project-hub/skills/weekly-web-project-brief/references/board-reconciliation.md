# Monday board reconciliation — separate execution job

## Scheduling and dependency

Keep the Monday report read-only. Use two linked Hermes jobs: report generation and board reconciliation. The second job starts only after the same Melbourne ISO week's report has a verified delivery receipt and shared archive. A clock offset alone is not a dependency. If missing, failed, partial core coverage or uncertain delivery, stop reconciliation and report the dependency; do not generate another report or resend email. Scheduling and installing this job require separate deployment authority; these instructions do not install a cron.

The report covers website evidence, not complete onboarding coverage. Before changing or commenting on onboarding, independently read the complete live Client Onboarding board and canonical onboarding records. Resolve one enduring overview per project, paginate fully, deduplicate overlapping onboarding/website records, and keep their summaries specific to their respective stage. Never fan comments out across every personal task or closed historical card.

## Authority and identity

Michael authorises a weekly internal project-summary comment on each resolved active onboarding and website overview task. Verify Lily identity user_id=82484 before posting in her name. Missing identity or connector access blocks that write; never impersonate Lily through a human account. Route all mutations through basicops-task-manager, onboarding state through client-onboarding, and website transitions through website-project-cockpit/wp-project-manager. Re-read current discussions and records immediately before writing; the report is a starting point, not current-state authority.

Routine reconciliation may update a precisely evidenced stage or owner only when existing owning-skill authority permits the exact change. Otherwise record a proposed correction for Kristalyn. Preserve dates, original commitments, approval evidence and history. Do not infer completion or client approval. Never select personal weekly commitments, change deadlines, launch, publish, contact clients or dispatch production from this job. Staff Weekly Flow owns confirmed Working on This Week moves.

## One weekly summary per overview

Use key `lily-weekly:<Melbourne ISO week>:<board ID>:<task ID>`. Read existing Discussion before posting. If a matching summary exists, skip it; put material new evidence into the next authorised correction rather than duplicate the weekly snapshot. After an uncertain post, reconcile Discussion before retrying. Keep a receipt per task so partial retries visit only unverified items.

Write conversationally with these headings:

- Last week's wins: evidenced completed work, with dates and links; say none verified when appropriate.
- Decisions: what was agreed last week, who decided, and evidence; keep separate from work completed.
- This week: recorded due work and confirmed commitments. Label suggestions and estimates explicitly.
- Waiting on the client: exact input, named contact where verified, promised date and latest sent follow-up. A draft is not sent.
- Next: next stage, immediate owner, prerequisite and review link.
- Needs Kristalyn: missing owner, stale board, contradictory evidence or schedule risk requiring intervention.

Use concise relevant sources, not raw transcripts or private email content. For each task read back the comment and any changed project, section, owner and status. Update canonical project context only with verified changes. Return Updated / Proposed / Blocked with links, before/after state, authority, coverage and failed items. A comment receipt is not proof of a board move.

## Kristalyn's accountability

Kristalyn owns Client Onboarding and Web Projects board accuracy, exceptions, handoff readiness and milestone risks. Delivery owners record results; Lily assists with reconciliation. The shared project stage and immediate owner are distinct from each person's confirmed weekly work.
