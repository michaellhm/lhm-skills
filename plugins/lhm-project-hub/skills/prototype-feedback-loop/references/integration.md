# Integration and release contract

## Approved stages

Onboarding & Briefing; Prototype; Prototype Feedback; Astro Build; Development & Content Entry; GMB; SEO; QA; Go Live; Post-live Review.

Inspect existing sections and task counts before updating. Preserve section IDs and task placements where a label is a genuine rename. Never relabel a populated mixed-purpose stage so its tasks acquire a false stage. Create new stages as necessary and report tasks needing classification. Do not delete sections or bulk-move projects without a grounded mapping. Store verified IDs, not label guesses.

## Routing configuration

Store site ID, cockpit/task ID, Gmail account, exact thread IDs, allowed senders, review-window start, reviewer and canonical project reference in a governed project record. Keep repository/prototype URLs visible as pointers. Resolve actual source and publication authority through the governed host route. Support both a dedicated site repository and a bounded client subtree in the shared prototype repository; do not force shared prototypes through dedicated-site registration. The shared prototype route uses the standing prototype authority and independent QA/root-owned publisher. Keep operational thread/sender mappings separate from the closed LHM classification metadata schema; use a labelled Discussion block until custom fields are verified supported.

## Adapter boundaries

The local queue accepts extracted packets; it does not authenticate, fetch Gmail, interpret images or prove BasicOps stage membership. A trusted host adapter must perform those checks and supply eligible=True only from a fresh live board read. Never take this boolean or routing configuration from a client email.

1. Read complete live board and registered project configuration.
2. Read full Gmail MIME and materialise private image files with verified hashes.
3. Extract feedback and route uncertain items, then enqueue validated packets. Acknowledge no-op email IDs separately in the host scan ledger.
4. Persist a unique owner token for this poller before claiming a batch. Claim one queued batch per site; a different owner receives busy and must not create or dispatch anything. After a crash, verify the former process has stopped and reconcile its remote outcomes before recovering its original persisted owner token. Do not share one owner token across live processes or invent an expiring lease that replays remote writes. Recheck stage before both create and submit. Preserve the claimed batch and persisted owner while ineligible; resume that same batch only after a new live stage check. Never dispatch merely because an older claim exists.
5. Before remote task creation, search the cockpit and execution destination for the stable batch key. After a timeout, reconcile by this key before retrying. Store the resulting task ID and verify Discussion/owner readback.
6. Submit through the existing central router with its own stable request ID and authenticated delegated authority. After a timeout, query the same request ID; never submit a fresh run to compensate. Store run ID and saved chat.
7. Observe the existing worker's result. `ready_for_review` requires the verified preview/checks/task handback. Retain the active slot for blocked/failed work until resolved or deliberately abandoned; do not allow subsequent batches to write over unfinished changes.
8. Post/verify review notification once using batch ID plus ready transition as delivery key. Retry only delivery if it fails.

Queue checkpoint writes cannot make remote APIs exactly-once. The adapter's search/readback and the router's idempotency are mandatory. Uncertain remote outcomes remain reconciling, never blindly replayed. Keep the queue database in a trusted service-owned directory on persistent host storage, access restricted to its service account, with backups. Do not install a second completion poller or replace the existing router.

## Live acceptance and rollout

Read actual installed source/version before deployment; the development base may differ from live independent repairs. Integrate only this change. Confirm the worker runtime loads `prototype-revisions`; adding it to desktop skills alone is insufficient. Install scoped assets atomically, retain prior hashes/config and avoid restarting active workers.

Verify BasicOps connector, Gmail account and attachments, delegated router entry, client source registration, preview publisher and existing desktop notification route in their actual execution environments. No new credentials, identities or permissions are included here.

Run pilot manually with scheduling disabled. Verify duplicate checks after a process restart, failure after task creation and after dispatch, new feedback during active work, unreadable image, unrelated separate email, wrong site/sender, stage exit, busy repository and notification failure. Enable a two-hour job only after the live acceptance passes. Record job ID, exact configuration, first-run evidence and pause/rollback route. Rollback disables intake first, preserves queued records and active runs, then restores prior scoped assets.

No live connector adapters, schedule, board changes, notification delivery or installation are proved by local queue tests.

Queue checkpoints distinguish `handback_receipt` (verified BasicOps result, required before ready_for_review) from `notification_receipt` (delivery to the reviewer, recorded after readiness). A notification retry must never reopen or re-execute a revision.

## Adapter implementation

`scripts/adapters.py` supplies injectable Gmail MIME/byte intake, BasicOps stage/readback, durable uncertain-effect reconciliation, Ted dispatch receipt checks, a reviewed-message ledger and independent completion/notification checks. Bind each callable to the existing authenticated runtime; these classes alone do not install those bindings. Unknown remote outcomes require reconciliation and are never blindly retried. BasicOps Description is compared as canonical saved HTML; persist the actual readback form.

The optional `feedback_authority.py` router hook accepts only an operator-owned exact-message-bound grant. It never treats AI text posted as Michael as personal approval. New admission rechecks the live cockpit; verified host-admitted runs may return after stage exit. The pilot scope is the actual repository subtree `luminary-counselling/`; `/prototypes/` is a public URL prefix, not a repository directory. Keep authority registries and private feedback out of Git.
