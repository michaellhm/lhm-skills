# Acceptance tests

## Full personal inbox review

Prompt: `I've got too many tasks in my BasicOps inbox. Can we go through all of them?`

Expected:

- Resolve the authenticated person's verified project, assignee and section IDs.
- Paginate through every open inbox task and state the active count.
- Present a compact client-risk rescue list followed by stale/likely closure, suggested delegate,
  suggested keep and needs-decision groups; omit empty groups.
- Link every mentioned task and label uncertain recommendations `likely` or `confirm first`.
- Do not mutate BasicOps during the first analysis pass.

## Natural-language decision batch

The person approves two closures, keeps one task, asks for one exact due-date change and proposes
delegating one task to a teammate.

Expected:

- Reflect an exact decision register before writing.
- Apply the authorised closures and own-task due-date change through `basicops-task-manager`.
- Require the teammate's approval unless a canonical graduated route applies.
- Add discussion context where the decision or next handoff would otherwise be unclear.
- Read every changed task back and return its verified BasicOps link.

## Ambiguous date

The person says: `Put that back on my radar next week.`

Expected: ask for one exact date before changing the due date; do not invent Monday.

## Stale is not complete

A task is old and has no recent activity, but there is no evidence it was completed, superseded,
duplicated or deliberately abandoned.

Expected: label it `stale / likely closure — confirm first`; do not close it without confirmation.

## Write surface unavailable

The person approves mutations but BasicOps write tools cannot be called.

Expected:

- Preserve the exact pending mutation register.
- State that BasicOps remains unchanged.
- Do not claim that a vault note completed the work.
- Resume from the pending register when the authorised write route is available.

## Overwhelmed daily view versus full review

Prompt: `I'm overwhelmed. What should I do today?`

Expected: show at most three items under overwhelmed mode and offer the full inbox review; do not
dump the whole board unless the person accepts.

## Kristalyn client-follow-up batch

Prompt: `What should Kristalyn focus on this week?` with ten client-contact tasks whose exact
`next_touchpoint` dates fall in the week.

Expected: show one **Client follow-ups** work block listing every client, exact ask, source task,
channel and downstream release; combine same-client asks when sensible; do not consume ten weekly
priority slots; do not send emails or mutate BasicOps during planning.

## Touchpoint evidence and cadence

A task says `touchpoint_cadence=fortnightly` but has no `next_touchpoint`, while another has a next
date conflicting with its BasicOps due date.

Expected: label the first `waiting for evidence` and the second `needs owner`; do not calculate or
silently choose a date. Advance `last_touchpoint` only from verified sent-email, meeting or canonical
contact evidence.

## Four-part weekly intake

The person first supplies meetings, later supplies family hard stops, then gives a website-project
rundown and finally reviews their BasicOps board.

Expected: treat the early timetable as provisional; complete all four intake areas before asking for
final confirmation; preserve one material question at a time; do not omit project handoffs merely
because they lack a current due date.

## Opportunistic capacity

Prompt: `I sometimes start at 5am when I wake up early, but I don't want to commit to it.`

Expected: record the early block as optional bonus capacity; make the confirmed outcomes fit inside
dependable hours; do not silently turn the optional block into a recurring preference or commitment.

## Meeting-cluster capacity

The person has three client meetings on one day.

Expected: reserve bounded preparation, the meetings, one consolidated follow-up block and required
handoffs; do not present each component as a separate weekly priority or ignore their capacity cost.

## Project-cascade reconciliation

The person mentions active Alpha, EHP and ASP handoffs during intake, but only Alpha appears in the
first proposed timetable.

Expected: catch the omission before confirmation and add or explicitly disposition EHP and ASP;
for each project show the artefact/approval, downstream person, handoff action and realistic block.

## Live delivery as workflow evidence

Prompt: `I need to create two client sitemaps, and this should become a Hermes skill.`

Expected: schedule the client sitemap outcomes first and capture the runs as reusable workflow
evidence; do not add a separate unbounded skill-building project that overloads the week.

## Voice alias correction

Voice input says `IPV`, while the authorised board contains `IPB` and another plausible client name.

Expected: ask one concise disambiguation question before linking or mutating records, then preserve
the confirmed alias in the weekly decision register.

## Cross-person attention

Michael needs Aiya to decide a website dependency that blocks a client and downstream production.

Expected: show who needs whom, the exact decision/input, person waiting, downstream release and
notification channel; do not claim notification from a planning note or create a new shared queue
without separate approval.
