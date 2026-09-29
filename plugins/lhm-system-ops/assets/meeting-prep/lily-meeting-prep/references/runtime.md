# Deployed runtime

Hermes profile: `/opt/data/profiles/lhm_brain`. The existing Lily daily meeting
prep job remains hourly. Its deterministic `meeting-prep-runner.py` script runs
the existing skill in a bounded child CLI process: 60 turns, 25-minute agent
budget, 27.5-minute hard stop. This does not alter other profile jobs or models.

## Recovery and outcome

The initial next-day briefing remains due at 13:00 Australia/Melbourne. An
unfinished batch can retry hourly through 18:00, or 07:00–10:00 on the meeting
day if its saved calendar exists. There are at most three research attempts per
date. A per-date lock prevents overlapping attempts. Explicit recovery accepts
`--date YYYY-MM-DD`; never backdate evidence or alter send receipts.

The runner supplies the meeting date, current calendar file, attempt number and
output directory. Do not rediscover setup or delegate. It persists
`run-state.json`, private per-attempt logs, and the exact prompt. Partial research
is retained between attempts. A failed calendar read or incomplete research is a
nonzero cron failure, not an empty calendar or a successful briefing.

## Research and outputs

Use native read-only BasicOps/Fathom tools. For Gmail use a separate process:

`HERMES_HOME=/opt/data/.hermes /opt/data/.venv/bin/python /opt/data/skills/productivity/google-workspace/scripts/google_api.py gmail --help`

Never change the parent profile or expose credentials. Exclude Lily-generated
briefs from factual evidence. Read BasicOps, Fathom and Gmail before deepening
any one source, and reserve ten turns for reconciliation and saving. Resume
from saved evidence after checking for newer material discussion/replies.

Normal outputs are under
`/opt/data/profiles/lhm_brain/workspace/meeting-prep-daily/runs/<meeting_date>/`.
Save `email.json` containing exactly `subject` and `body`, freshly written each
attempt, plus `research-receipt.json` containing:

- `meeting_date`, `attempt`, `status` (`ready`, `incomplete`, or `no_client_meetings`).
- `calendar_classification`: one entry per supplied event with `event_id`,
  `classification` (`client`, `excluded`, `uncertain`) and a reason.
- `source_coverage`: `basicops`, `fathom`, `gmail`, each with `status` (`checked`
  or `unavailable`) and `evidence` describing searches, latest reads, pagination
  bounds or the exact failure. An unattempted source is not unavailable.
- `issues`: the skill's per-issue evidence and handoff records.
- `limitation_sentence` when any source is unavailable; include that exact
  sentence in the email body so the reader can judge the gap.

Save partial `status: incomplete` checkpoints after each source, including the
first unfinished step. A source failure allows one retry; after that a useful
brief may proceed with an explicit limitation. An exhausted budget alone never
proves evidence was checked. No useful evidence means incomplete, not ready.
For no client meetings, account for every event as excluded and save
`no_client_meetings`; no email is needed. Ambiguous events cannot be silently
classified as an empty client calendar.

## Delivery ownership

In runner-driven research mode, the child must NOT send or verify email. The
deterministic parent validates the current-attempt files and uses the existing
fixed-recipient sender, preserving To Michael, CC Kristalyn, From Lily,
Reply-To Michael and the original date/recipient/kind dedup key.

The existing `meeting_prep.py send` and `verify` interface remains for explicitly
authorised one-off tests. Tests must use `--kind test` for both operations.
Never edit/delete delivery receipts, call another sender or resend an uncertain
outcome. An existing receipt triggers verification only. Both recipient delivery
events must be confirmed before the runner returns `delivered`. Pending, failed
and uncertain delivery produce an explicit failure requiring reconciliation.
Review/feedback alone does not authorise a replacement email.
