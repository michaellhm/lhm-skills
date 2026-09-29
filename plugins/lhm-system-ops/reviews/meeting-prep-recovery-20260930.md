# Meeting-prep recovery — 30 September 2026

## Research

The affected hourly job is `43c5187a2005` in `lhm_brain`. Its 13:00 run
exhausted `agent.max_turns: 20` before required evidence and delivery. The
calendar gate rejected every later hour. A normal model return was recorded
as OK despite no email or send receipt. The profile skill/runtime existed only
on the host; this change establishes an explicit canonical profile-asset package.

Native Hermes supports `chat --max-turns`, `--run-budget`, no-agent cron scripts,
nonzero script failure reporting and atomic `cron.jobs.update_job`. The repair
uses these supported interfaces; it does not patch Hermes core or global config.

## Engineering

The runner owns a per-date lock, three bounded research attempts, current-attempt
evidence validation, original fixed-recipient sending and recipient verification.
Research uses the same profile, model and skill with a process-local 60-turn /
25-minute budget. Partial checkpoints survive and later eligible hours retry.
Existing send receipts always stop a resend; queued sends are only verified.
No-client classification must account for every supplied event.

## QA

Sixteen behavioural tests cover successful recovery after budget exhaustion,
bounded calendar failure, overlapping attempts, stale research/email rejection,
source coverage, disclosed source failures, calendar completeness, no-client
outcomes, DST/window selection, Calendar credential-home isolation, uncertain sends and both-recipient verification.
Plugin version, script parity, System Ops validation and frontmatter checks pass.
LEARNED.md files were scanned and contained no unabsorbed entries. Desktop skill
counts and existing maintainer catalogue entry remain accurate; this package is
a profile asset rather than another desktop routing skill.

## Security and reliability

No credential, model, capability, recipient or global profile configuration
change. No source-system writes during research. The sender's persisted-before-
network dedup key, excluded-topic guard and Mailgun route are preserved. The
installer only replaces five allowlisted assets and three fields on one job,
with pre-install backup, ownership/mode retention, hash readback and automatic
rollback on installation failure. No gateway restart is required.

## Release and live acceptance

Michael authorised fixing this named production incident and recovering the
missed briefing. Publish and deploy the exact feature commit through the scoped
root-owned profile installer; do not merge main or install unrelated plugins.
Live acceptance requires the original missed meeting-date brief and both
recipient delivery events. Keep the installation and send receipts on the host;
never put client research or credentials into Git. The feature commit alone is
not evidence of live delivery.
