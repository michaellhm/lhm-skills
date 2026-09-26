---
name: inbox-tidy
description: Clean up stale threads in Michael's working-state labels (ONGOING TASKS, TO RESPOND, WAITING ON, MEETING WRAP). Inventories by age, proposes what to move to Done and archive, and applies only what Michael approves. Use when the user says 'tidy my inbox', 'clean up my labels', 'clear out ongoing tasks', 'inbox cleanup', 'archive old emails', or on a monthly schedule. Never trashes.
---

# Inbox tidy

Two passes: inventory, then approved changes. Never combine them in one step.

Read `${CLAUDE_PLUGIN_ROOT}/references/safety-rules.md` and `labels.md` first.

## Pass 1: Inventory

For each of `*** !MICHAEL-ONGOING TASKS`, `***!MICHAEL-TO RESPOND`, `*** 4.  WAITING ON`, `*** MEETING WRAP`:

Search with `newer_than:` windows so threads are bucketed by last activity, not thread start: last 30 days, 30 to 90, 90 to 180, older. Report counts per bucket per label.

Then propose, as a table Michael can strike lines from:

- ONGOING TASKS older than 90 days: Done + archive. Group by client or sender with counts; list individually only the 10 most recent per bucket.
- ONGOING TASKS 30 to 90 days: list individually, default Keep, mark the obvious closures (share notifications, auto-mails, subject says "completed", "thanks", "final invoice").
- ONGOING TASKS last 30 days: leave alone, list count only.
- TO RESPOND: list every thread with last sender, date, and whether Michael already replied (check sent mail on that thread). Already replied: remove the label. Not replied: leave the label and put it in the brief's Reply-today next run.
- WAITING ON older than 90 days: Done + archive. Anything in a personal thread: remove the work label and add nothing (personal threads are not this skill's business beyond that).
- MEETING WRAP: keep the latest per client, Done + archive the rest. Never touch a wrap whose client is still in onboarding.
- Drive/Docs/Dropbox share notifications, Cliniko, Twilio, BasicOps, Pabbly auto-mails in any of these labels: Done + archive regardless of age.

Present the proposal. Stop. Wait for Michael's edits and approval.

## Pass 2: Apply

Only on explicit approval, and only the lines that survived. For each thread: remove the working-state label, add `*** 9. Done`, remove INBOX. Do not touch starred threads. Do not touch anything with a message in the last 7 days. Log every change (thread, subject, from-label, to-label) and output the log so it can be reversed.

Batch in groups of 25 and report progress. If any call fails, stop the batch and report which threads were done.

## Baseline (26 Sep 2026 inventory)

333 threads across the four labels. Proposed: about 285 archivable. ONGOING TASKS 294 (200 with no activity in 90+ days; bulk is closed project history: Doors Replaced, Raise the Bar 2025, Marmot/KODA/Woodlands, Fenton Stephens, plus 17 share notifications). TO RESPOND 9 (2 live). WAITING ON 16 (3 live). MEETING WRAP 14 (6 live). Full detail in the project doc `email/label-inventory-2026-09-26.md`.
