# Weekly delivery, archive and coaching contract

Michael approved the intended rhythm on 28 September 2026: prepare from Monday 07:00 and target
email release at **08:00 Australia/Melbourne**, then use the current shared weekly brief for his
early review and the team's Monday planning. The existing hourly native no-agent cron remains;
the DST-aware gate selects 07:00–07:59. The controller waits until 08:00 before submitting a ready
report. If preparation finishes later it sends then, with the actual cutoff/delivery time. This is
a target, not a guarantee of arrival at exactly 08:00. No duplicate/catch-up send on another day.

Verified useful updates should be sent with project-specific questions visibly disclosed. Preserve
uncertain commitments as confirmation actions with owner, impact and next step. Do not require the
team to answer every question before the email can go out. Actual false claims, wrong task links,
resurrected completed work, missing core source access and uncertain delivery still require repair.
The independent reviewer uses the same distinction. Never manufacture an acceptance or complete
coverage. The prior shared weekly note and its dated feedback are continuity evidence, not fresh
proof; reconcile them with current tasks and correspondence.

## Shared archive

The fixed controller, not the research worker, invokes `weekly_archive.py` after the receipt says
delivered. It verifies the approved payload's quality hashes and the exact delivered email hash,
then writes only `60 Knowledge/YYYY-Www — Web Projects.md` in shared drive `LHM Knowledge` through
the existing authenticated Hermes Google helper. It creates no client folders, changes no sharing
or credentials, and never writes private founder material.

The note contains the delivered project snapshot, owner actions, clarification notes, source cutoff
and delivery identity. A snapshot checksum marks the immutable part. Repeated archival is a no-op
only when that entire prefix still matches; appended team feedback is preserved. A differing
existing note or duplicate filename needs reconciliation, never overwrite. The host records an
archive receipt in `archive/<Monday>.json`; the existing watchdog retries a pending archive after
confirmed delivery without rerunning research or sending another email. Archive errors remain
visible there independently of the successful email receipt.

`60 Knowledge/Weekly Web Projects.md` is the stable team entry point. Its current-week links or
Obsidian query expose the dated files. Do not overwrite this human-maintained guide on each run.
Initial setup creates/updates the guide once under the authorised vault workflow. The staff flow
computes the current ISO week rather than trusting a stale “current” link. No hard-coded Week 40.

## Feedback

`staff-weekly-flow/references/weekly-web-coaching.md` owns the interactive coaching and feedback
contract. People can correct context, prepare client communications, confirm work, close last
week's commitments and explicitly authorise BasicOps changes in that flow. Append dated,
attributed feedback under **Team corrections after delivery**; preserve the sent snapshot and
other people's entries. Detailed execution remains in BasicOps; durable client decisions flow to
the canonical client project record. A chat draft, proposed date or unverified report never becomes
a sent message, confirmed deadline or completed task merely by being saved.

## Activation and rollback

Publish a scoped immutable release, validate it and obtain any required installation authority.
Install the updated weekly skill and staff-flow assets on their owning profiles; update only the
existing cron's display/prompt to describe 07:00 preparation and 08:00 delivery. Keep its ID,
hourly expression, no-agent mode and fixed recipient. Preserve receipts and previous skill links.
The installer must retain the existing watchdog; validate both winter and summer UTC mappings.
Confirm scheduled research does not run immediately during installation, and never send a test
without explicit test-send authority. Roll back to the recorded immutable links/config if needed.

Profile installation does not automatically update a ChatGPT project's instructions or a cached
desktop plugin. Report those destinations separately; the shared guide supports an explicit
"Run my Monday web-project planning" entry point where the required connectors are authorised.
