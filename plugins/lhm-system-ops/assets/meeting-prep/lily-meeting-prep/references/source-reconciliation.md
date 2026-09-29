# Last-wrap and missing-work reconciliation

## 1. Establish the baseline from Gmail

For every verified client on the supplied calendar, resolve Michael's actual
meeting-wrap label with Gmail labels.list. Michael may call it
`MICHAEL: MEETING WRAP`; at the 2026-09-30 verification its actual name was
`*** MEETING WRAP`. Resolve it each run; do not create, rename or relabel anything.
If several labels could match, record ambiguity rather than silently choosing.

In Hermes, the existing authenticated helper supports `gmail labels`,
`gmail search --help` and `gmail get --help` at the path in runtime.md. Use only
read operations. Search the resolved label plus the client's verified names,
domain and aliases, before the upcoming meeting. Start at 90 days; use one
bounded older search if needed. Page far enough to establish the newest relevant
wrap, documenting bounds. Read the full wrap and newer replies; snippets and
Lily's preparation emails are not a substitute. Confirm the meeting/client/date
and distinguish the sent wrap from an unsent draft or an old forwarded quotation.
If no labelled wrap matches, search sent mail for the client's meeting-summary
or action-items email; record that fallback explicitly and its actual labels.
No match after a completed search is `not_found`; authentication, transport or
pagination failures are `unavailable`/incomplete, never proof of no prior wrap.

Extract all in-scope actions and decisions, with source links and any explicit
owners/deadlines. Preserve strategic ideas as ideas rather than invented tasks.
Skip excluded-topic sections and personal/patient content entirely; do not copy
those portions into receipts or the shared email. A wrap is the starting promise
ledger, not proof an action is still outstanding or has been completed.

## 2. Sweep BasicOps and newer correspondence

First search workspace-wide using verified client names/domain/abbreviations;
shared staff boards and Client Flow may hold the actual work. Then search specific
words and synonyms for EVERY wrap commitment. Include parent/child tasks and
completed work, not just open tasks. Read the newest relevant discussions and
any handoff/approval/delivery evidence; reconcile newer email replies as well.

Give every commitment one disposition: `tracked`, `complete`, `superseded`,
`deferred`, `no_matching_task_found` or `search_incomplete`. Record the source
that supports the disposition and the current next actor. An old task status
cannot outweigh a newer substantive handoff. `complete` requires outcome evidence,
not merely a board label. A missing match requires successful bounded searches,
including query and pagination evidence. Phrase it as “No matching BasicOps task
found in the checked scope”, not a claim that no task exists or someone forgot.
When a connector/page limit prevents the sweep, use `search_incomplete` and a
verification action. Do not turn unsearched commitments into missing-task claims.

Keep the full ledger in the private research receipt. Surface only material
meeting decisions, actions or gaps in the concise email, once per issue.
Do not create tasks, comments, due dates, notes or other source-system changes.

## 3. Check shared Obsidian context

Resolve the active shared LHM Knowledge mirror. The verified Hermes mount is
`/opt/data/profiles/lhm_brain/vault-lhm-knowledge`; check availability each run.
Resolve the actual folder under `20 Clients/` from names plus overview/domain
identity, preserving its existing name. Never invent a folder, traverse symlinks
outside the shared root, or fall back to `vault`, the retired combined vault,
Michael's private vault or a local desktop path.

Read the existing overview/profile, Goals, Current Projects and relevant recent
meeting/project-management notes. Paths and capitalisation vary: discover the
actual files. Search the shared `50 Meetings/` only for this verified client when
relevant. Record paths, dated source evidence and available sync/freshness evidence.
A filesystem modification date alone does not prove note content is current.
Check for promises/goals not represented in the wrap or BasicOps, and conflicts
between notes and the newest source messages. Stale notes are context, not current
execution state. Missing files after a successful search are `not_found`; an
unmounted or unreadable root is `unavailable`. Disclose a material freshness gap.

## 4. Fathom availability and evidence

Use the profile's existing authenticated MCP, with a tight client/date lookup,
then the latest two or three relevant meetings as needed. Read the transcript
before attributing a specific promise; a wrap can be cited as an email source
without claiming the underlying recording was checked. Never scrape public
Fathom URLs, borrow another profile's credentials or use Codex's connector as
proof that the scheduled profile works.

On 2026-09-30 the profile logs showed `OAuthNonInteractiveError`: the scheduled
Fathom connection required interactive browser authorisation. Tool-search absence
alone did not explain the cause. Retry discovery once, record the actual failure
if available, and scope the limitation: “Fathom needs reconnection on the server;
this brief uses the last wrap, current tasks/email and available shared notes.”
Only claim those other checks if they were actually performed. Reauthorisation
is an operator step (`hermes -p lhm_brain mcp login fathom`) with the account
owner completing consent; the briefing must not alter authentication. If the
cause is unknown, report session unavailability without inventing an auth failure.

## Receipt contract

`source_coverage` has five independent entries: `basicops`, `fathom`, `gmail`,
`meeting_wrap`, `obsidian`. Each includes `status` and concrete `evidence` (queries,
message/note identifiers, date/page bounds or the exact safe failure class).
Use `checked` or `unavailable`; wrap/Obsidian also allow `not_found` after search.
If clients differ, describe each in evidence; record partial failures honestly.
Any unavailable source requires the visible limitation sentence in runtime.md.

`meeting_wrap_checks` has one entry per calendar `client_key`:

- `client_key`, `status` (`found`, `not_found`, `unavailable`), `search_evidence`.
- When found: `message_id`, `thread_id`, `sent_at`, `url`, `label_name` (actual
  label or explicit sent-mail fallback), and `extraction_evidence` describing the
  full message read and how all in-scope commitments were accounted for.
- `commitments`: array, empty only if no in-scope commitments or no wrap found.
  Each item has `commitment_id`, concise `summary`, `disposition`, `evidence`,
  `basicops_queries` and `search_complete`. `tracked`/`complete` also require
  `task_urls`. A no-match result requires `search_complete: true` and evidence of
  the checked bounds. Include next actor and linked issue_key where useful.

The wrapper validates coverage and prevents missing/incomplete evidence from
being silently treated as a successful check. It cannot independently prove
that a model's summary faithfully reflects a source. The final editorial check
must still compare included claims with the newest source messages.
