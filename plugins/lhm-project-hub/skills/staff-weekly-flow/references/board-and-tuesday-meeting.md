# Reconcile the board and prepare Tuesday web

Use this contract during every staff weekly planning flow. Michael requested board organisation as
part of the flow: do not leave accepted work as a prose plan while the board remains stale. This is
not blanket authority to move all staff tasks during a portfolio review or to accept work for them.

## Decide and apply one item at a time

1. Read the person's live personal board, including both Working on this week and Current Projects
   To Progress On This Week where present. Reconcile these with the previous confirmed commitments,
   current brief and task discussions. Inspect all existing weekly items for a disposition; older
   cards are not automatically unfinished, closed or recommitted.
2. Verify exact source/destination IDs and semantic meaning against the profile and live sections.
   Correct a stale mapping only from verified evidence through the approved profile write route.
   Distinguish weekly actions from weekly projects. If the destination remains unclear, ask one
   focused question and leave the move pending. Do not invent sections or hard-code board IDs.
3. Show the named task/link, current section, proposed destination, outcome and any proposed status
   change before the person decides. Ask whether they accept it for this week or choose review,
   waiting, defer, help or completion. A clear acceptance of this exact preview authorises that
   bounded move. Do not ask again merely because the task-manager workflow is invoked. A general
   yes to a plan, silence or a manager's portfolio colour is not authority for unseen mutations.
4. Immediately route the accepted operation through `lhm-project-hub:basicops-task-manager`, using
   its identity, deduplication, classification, handoff/discussion and verification requirements.
   Preserve assignee, parent/project and due date unless explicitly included in the accepted change.
   Leave nested project tasks in their owning project; reuse/link an existing personal action rather
   than duplicating it or moving the parent to a personal board.
5. Read back project, section, assignee, status and due date. Save the chosen commitment/disposition
   and verified result incrementally in the existing shared person/week note. On failure, retain
   the decision and exact pending change; continue independent items and never claim success.
   On retry, re-read state and skip an already-applied move or existing handoff comment.

## Choose the honest destination

- Accepted, actionable work this week: verified weekly action or weekly project section.
- Finished production awaiting review: move out of active weekly work to the mapped internal-review
  or waiting section, name the reviewer and required output. Waiting on Michael or Kristalyn is
  internal review, not client review; use Review/With Client only if its verified board semantics
  cover that state. Do not call an unapproved build fully completed or live.
- Awaiting actual client feedback: verified client-review/waiting destination, contact owner and
  requested response. A sent handoff must have evidence; a prepared comment is not notification.
- Completed scope: verify or attribute the outcome, preview the appropriate completion/section
  operation, then apply the accepted change. Preserve any outstanding separate review/launch gate.
- Blocked, unclear, deferred or no longer actionable this week: use the mapped blocked/waiting/future
  destination after the exact disposition is accepted. Do not silently push due dates forward.

If no appropriate destination exists, leave the task in place and show the mapping gap in the
meeting document. Do not misfile it merely to make the weekly list look clean. Where one part is
blocked but another is actionable, define that smaller accepted outcome rather than moving the
whole project blindly. Every removed weekly item retains a traceable disposition and next owner.

Before the closing document, complete [project-context-handback.md](project-context-handback.md):
verify canonical client records and BasicOps destinations for every settled item.

## Required weekly-board closing check

Before closing, reconcile every accepted outcome and its specific executable task links against
live BasicOps. Include all agreed actionable tasks, even when several support one weekly outcome.
Record each as `moved and verified`, `already correctly placed and verified`, `linked in owning
project — verified`, or `pending — exact change, reason and next owner`. Apply every authorised
missing move; a saved Obsidian plan is not proof the board was updated. Preserve owning projects,
assignees and due dates unless their exact changes were accepted.

Inspect every card already in the weekly sections, not just newly selected work. Resolve each as
accepted this week, completed, awaiting review, waiting, deferred, or pending a decision. Preview
and apply accepted moves out of active weekly work; do not silently carry forward leftovers.
Keep unselected Inbox work available for future triage rather than forcing the whole Inbox into
this week. A missing section or failed write is a visible gap, not a reason to claim a clean board.

Finish with a concise receipt: plan saved/verified, tasks moved into this week, already correct,
linked project actions, items moved out, communications sent versus drafted, and exact pending
changes. Distinguish confirmed commitments from fully reconciled board state. If gaps remain,
report the board reconciliation as partial and retain the restart point in the same weekly note.

## Tuesday web meeting document

At the end, write a concise **Tuesday web meeting** section in the existing
`22 People/<Person>/YYYY-Www — Weekly Flow.md` and provide a direct link. This is the little meeting
document, not another task database or a duplicate weekly note. Use the four headings below:

1. **Completed last week** — outcome, task/deliverable link, completion date or unknown, and
   verified versus reported evidence. Never infer last-week completion from today's Complete status.
2. **Awaiting feedback or review** — deliverable, reviewer/client, requested response, next owner
   and known checkpoint. Include waiting on Michael or Kristalyn and any missing handoff.
3. **Working on this week** — only the person's accepted commitments, done condition and next
   handoff; distinguish applied board moves from pending writes.
4. **Blocked / decisions for Tuesday** — unclear scope, missing input, owner or route, exact question,
   person needed and what their answer releases. Include unresolved weekly-list cleanup/mapping gaps.

Unclear tasks that the person cannot progress belong on Tuesday's agenda; do not force a guess or
leave a vague 'blocked' label. If the person can resolve it with the coordinator sooner, record that
next action and retain it for the meeting only while unresolved. Do not create calendar events,
new tasks, send the document or contact clients merely because it appears in the meeting agenda.
Save confirmed portions even if the flow is interrupted, mark the document partial, and resume
from the same decisions. Empty sections say 'None reported' or 'Evidence unavailable', as appropriate.

## Acceptance checks

- Person accepts named C01 and its shown Inbox → weekly-actions move: invoke task manager once,
  verify the move, save C01, no redundant generic permission; an unseen C02 remains unchanged.
- Work awaits Michael: propose mapped internal-review/waiting, not automatically client review;
  remove from weekly work only after exact acceptance and show Michael's decision on Tuesday.
- Two weekly sections exist: use evidence to choose actions versus projects; unresolved ambiguity
  remains pending and is visible in the meeting document.
- Task is Complete today without a completion date: don't claim it was completed last week.
- Michael updates portfolio priorities: save shared corrections but don't manufacture staff
  acceptance or bulk-move their boards.
- A move fails or is retried: keep chosen commitment, report pending once, re-read before retry,
  avoid duplicate tasks/comments and preserve due dates and nested-task ownership.

- Three outcomes cover seven actionable tasks: verify all seven task placements, not only three
  representative cards; leave waiting parents in Waiting and link their selected follow-up action.
- One accepted move fails: save the commitment, report the exact pending move and partial board
  reconciliation; never report the weekly board clean solely because Obsidian was saved.
- A stale weekly card is not selected: obtain its disposition; do not silently carry or close it.
