# Calendar → sales handover in Codex

An additive Hermes-host automation: read the primary calendar through Hermes' existing
Google Workspace connector; after an eligible onboarding meeting ends, open one saved
native Codex conversation on the already paired VPS. The reviewed sales-handover skill
and its routing references travel with the run. No new inference provider, credential,
remote-control pairing, BasicOps task or outbound notification is created.

## Trigger and result

- Exact verified calendar identity and organiser allowlist, plus an onboarding word in
  the title. The calendar owner must be invited and must not have declined.
- Timed, confirmed, non-private ordinary events only. Scheduled end + 3,600 absolute
  seconds; the host checks every five minutes, with up to 20 seconds of jitter.
- Fresh event read before dispatch handles cancellation/rescheduling. Calendar identity,
  stable recurring-instance identity, activation cutoff and seven-day maximum catchup
  are enforced. Historical onboarding is not replayed when the timer is installed.
- Read the relevant Fathom meeting through the existing authenticated read-only route.
  Retry transcript-not-ready at most three scans. Disclose access/ambiguity/final
  readiness gaps in the same chat; an unavailable source never becomes “no meeting”.
- A calendar appointment is not proof of attendance, a sale or completed discovery.
  Codex verifies evidence, checks newer emails/client records, and prepares the internal
  handover email first. It saves a complete editable draft and shows it in the chat.
  Remote bootstrapping may lack the desktop editor tool; open the linked draft in the
  desktop editor when reviewing. Subsequent client email and task proposals continue
  in that same chat. Each send/task batch retains its separate review and authority.
- No autonomous sending, Gmail draft writes, BasicOps changes, shared-file writes,
  tracking setup or website changes. Local output is staging, not delivered client work.

## Native integrations and boundary

`calendar_read.py` is deployed into the existing Hermes profile and uses its existing
Google OAuth route. `fathom_read.py` uses the existing codexworker Fathom MCP login;
it reads only meeting lists/transcripts. No credential is copied into packets, logs or
source. Codex's existing saved-session helper launches as uid 10001, with read-only
integrations and task-local file writes. The initial bootstrap never runs as root.
The deterministic supervisor is root-owned and launches only this fixed worker.

Event descriptions, locations, conference passwords and attachments are excluded from
the packet. Included source text is evidence, never instructions. All ledgers and
launch markers are durable. A timeout after launch requires reconciliation against
the original session; it never authorises a second chat. Starting a chat and finishing
the first draft are separately recorded.

## Configuration and installation

Supply an operator-only JSON config outside Git containing `calendar_id` (normally
`primary`), `calendar_identity`, `organizer_emails`, `enabled_from` (aware ISO timestamp),
`codex_host_id` (verified paired `remote-control:env_…`), `delay_seconds` (3600) and
`catchup_days` (7). The installer binds `source_commit`; do not put tokens in config.

Export the exact approved Git commit with this asset and `plugins/lhm-project-hub`.
Verify transfer hashes and run as the existing operator:

```sh
python3 plugins/lhm-system-ops/assets/calendar-sales-handover/install.py \
  --commit FULL_SOURCE_SHA --config-file /root/calendar-sales-handover-config.json
```

Installation is an explicit scoped deployment. It snapshots previous files, validates
the calendar identity in a no-dispatch preflight, installs an immutable release and
enables only `lhm-calendar-sales-handover.timer`. It refuses an active scan/bootstrap;
it does not restart the Hermes gateway or alter other cron jobs. Failure restores the
previous runtime link/config/units/adapter and timer enablement. Release directories,
ledgers and receipts remain for diagnosis; no existing conversations are deleted.

## Operator test and feedback

```sh
python3 /usr/local/libexec/lhm-calendar-sales-handover/runtime.py dry-run
python3 /usr/local/libexec/lhm-calendar-sales-handover/runtime.py test --event-id EXISTING_EVENT_ID
python3 /usr/local/libexec/lhm-calendar-sales-handover/runtime.py status
```

The explicit test reads one existing event without editing the calendar. It bypasses
only the activation cutoff, retains organiser/invitation/end-time checks, uses a
separate test ledger/run identity, and labels the packet as a test. Repeating it
reconciles the same chat. Give feedback in its returned `codex://threads/…` conversation.
`status` includes production/test chat links, initial-turn outcomes and exact gaps.
An `uncertain` launch with no session is operator attention, never a retry-to-create.

For a real calendar test, use a Marlon-organised onboarding invite with Michael invited,
let it end, and wait an hour plus the next five-minute scan. Cancel/move/decline tests
must produce no new chat. Old meetings remain excluded from production automatically.

## Validation and rollback

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/lhm-system-ops/tests -p 'test_calendar*py' -v
```

Check original calendar/Fathom identities, native saved chat UUID, readback URL, exact
skill digest, completed draft files and second-run deduplication on the installed host.
An initial model turn alone does not establish business onboarding completion.

Rollback: stop/disable the new timer (let existing bootstrap finish), restore the
previous runtime symlink and each backed-up file/owner/mode from
`/root/lhm-calendar-sales-handover-backups/FULL_SOURCE_SHA/before.json`, daemon-reload,
then restore the recorded timer enablement. Keep worker conversations, ledgers,
launch receipts and immutable releases for audit. Source publication is separate from
main-branch merge and from plugin-wide installation.
