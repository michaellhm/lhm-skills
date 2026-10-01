# Lily meeting-prep profile asset

Canonical source for the previously profile-only `lily-meeting-prep` skill and
fixed-recipient runtime. This is an explicit deployed profile-asset package,
not an additional desktop catalogue skill. Source was reconciled from the
existing `lhm_brain` installation for Michael's 30 September 2026 recovery fix.
Client-specific historical examples are replaced by reusable editorial rules.
No credentials, source emails, client evidence or delivery receipts belong here.

## Incident and acceptance

The previous scheduled run reached the profile's 20-turn ceiling before Gmail
and Fathom research or delivery. Hermes marked its normal textual exit OK.
The 13:00-only gate skipped every later hour, so there was no recovery.

The repaired job uses Hermes' native no-agent script mode to run the same
profile and skill with process-local `--max-turns 60 --run-budget 1500`.
Research writes current-attempt artefacts, and the parent validates coverage,
preserves send dedup and requires both recipient delivery events. Missing
research, calendar errors, exhausted retries and incomplete delivery exit
nonzero. Recovery windows and attempt limits are in the runtime reference.
No model, credentials, recipient, permissions or other profile limit changes.

## Validation

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/lhm-system-ops/tests -p test_meeting_prep_recovery.py -v`

Tests cover budget exhaustion, continuation, bounded calendar failures, DST,
stale artefacts, all-source coverage, no-client outcomes, send uncertainty,
queued reconciliation and both recipient events. Live acceptance is the
original missed briefing delivered to both existing recipients, with the cron
still enabled and its hourly schedule preserved.

## Install and rollback

Export this directory from the reviewed immutable feature commit, verify the
export hashes, then as root run `python3 install.py --commit FULL_SHA`. Michael's
instruction to fix the named production incident authorises this scoped
profile repair; it does not merge the feature branch or install other plugins.
The installer backs up every prior file, mode/owner and target job, writes only
the six allowlisted files, and uses native `cron.jobs.update_job` for the one
job. Installation readback verifies content hashes and unchanged cadence,
delivery target, enabled state, skills and working directory. No gateway restart.

The backup is `/root/lhm-meeting-prep-recovery/FULL_SHA/`. If live acceptance
fails because of this release, restore files using `metadata.json`, removing
only a new file marked null, and restore `script`, `no_agent`, `prompt` from
`job-before.json` with `cron.jobs.update_job`. Preserve all run and send receipts.
Installation failure performs this rollback automatically.

An authorised recovery uses the installed runner with `--date YYYY-MM-DD` under
the existing Hermes user/profile. Use a durable supervisor; retain its exit
state and verify the fixed sender's recipient events. Do not claim success
from a queued run or a child's final prose.

## Preparation sources

The current flow reconciles the latest client meeting-wrap email against every
in-scope commitment in BasicOps, newer correspondence and shared Obsidian notes.
Fathom gaps retain their actual cause; server reauthorisation is an operator step.
See the skill source-reconciliation reference for bounded searches, receipt
fields and the distinction between no match and an incomplete search.
