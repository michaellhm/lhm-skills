# Meeting wraps: Josephine captures, Michael delegates

This is the meeting-wrap exception to generic BasicOps title, parent, Description,
next-handoff and production rules. It governs `post-meeting-review`, Lily and any
caller writing a meeting card. Other task types keep their existing conventions.

## Capture and review

- Use one top-level task in `*Client Flow` for each client and meeting date. Title:
  `<Client name> meeting <day> <month>` (add year only to disambiguate). Never nest
  the meeting beneath an enduring client card or create a second meeting-notes card.
- Search client + exact meeting date before creating; inspect parentage and reuse the
  matching meeting card. Never rename an enduring multi-meeting client tracker into
  a single meeting. Promote an existing nested meeting only with a supported tool;
  if unavailable, report that specific limitation instead of guessing a parent ID.
- Josephine's capture creates or reuses exactly one meeting card assigned to Michael
  for review. Do not create action cards or a nested meeting-notes card at this stage.
- Put the full reviewed wrap email in **Discussion**, preserving its wording,
  formatting, recording and confirmed next-meeting details. Use the exact reviewed
  email artifact; do not silently substitute a team email for a client email or vice
  versa. Record whether it is reviewed, drafted or verified sent, with its source link.
- Add **Proposed actions — awaiting Michael's review** in that Discussion. Preserve
  explicit meeting commitments and owners as evidence, but distinguish them from
  internal execution assignments. Link existing tasks when verified; do not invent
  IDs or create one card per bullet. Flag missing scope, owner or client guidance.
- Description contains only the normal LHM metadata and verified working URLs.
  The capture handoff is Michael / ready-for-review / BasicOps. Use no invented due
  date. A legacy email or task register in Description remains valid evidence: read
  both fields, preserve it, and put subsequent corrections and the current register
  in Discussion. Do not mass-migrate older cards.
- Review the actions together before routing. Verify disputed commitments against
  the transcript and current work: a discussion is not a build order, existing work
  is checked before being rebuilt, and client-owned work stays client-owned. Group
  related client inputs into one coordinator task with a checklist and a copy-ready,
  unsent client email when requested. Do not manufacture independent commitments.
- Michael then runs `meeting-to-action`: reconcile current work, resolve decisions
  interactively, and approve which outcomes to retain, update, delegate or drop.
  Only that authorised review creates or updates action cards and complete briefs
  through `basicops-task-manager`; use the appropriate service/project route.
- Preserve the original wrap; append corrections and the live linked action register
  in Discussion. Do not silently rewrite the email when a decision changes.
- Saving the wrap, approving wording, a Gmail label or a generic “looks good” does
  not authorise delegation or production. Explicit delegation in Michael's current
  request is sufficient; do not require another invocation or a Lily-only phrase.
- Once all reviewed actions have verified task links/owners or an explicit retained,
  deferred or dropped disposition, the meeting review card can be completed. Record
  the downstream links and unresolved decisions on their owning tasks. Completing
  this review does not complete delivery. Kristalyn coordinates assigned delivery.

## Explicit distribution only

“Lily, disperse/disburse these tasks”, “distribute the approved meeting tasks” and equivalent
explicit instructions authorise routing the specified reviewed actions. They do not
authorise production. Resolve the actual task IDs and reviewed scope from the source
meeting; if the instruction identifies only a subset, route only that subset.

1. Read the current meeting Discussion, legacy Description, corrections and linked tasks. Use the
   reviewed named human owner; resolve any genuinely missing owner before routing
   that action. Client requests stay with the named internal coordinator.
2. Reuse existing action IDs; create only approved actions still missing cards.
   Resolve each person's actual board and Inbox section through BasicOps.
3. Assign the human and move the task to their Inbox. Keep the meeting top-level on
   Client Flow. Preserve status and existing due dates unless explicitly authorised
   otherwise; do not mark work In Progress just because it has been distributed.
   If an approved scheduling rule exists, use its confirmed meeting date; do not
   invent dates or silently backdate overdue targets.
4. Read back each task's assignee, board and section. Update the Discussion action
   register and post one concise routing receipt with verified links. Retry only failed
   items; repeating the instruction must not create duplicate cards or queue work.
5. STOP after routing. Do not assign Ted, call Chief of Staff, create a production
   plan or execution queue, emit production lifecycle markers, start research,
   prepare deliverables or report work ready for human review. TED is a separately
   requested future stage. Existing production skills apply only when a later user
   instruction actually requests production, never from distribution alone.

Use Lily's authenticated account when available. Do not impersonate her from a
human account: label AI-written receipts with the actual assistant identity when
using that account. Do not send client email as part of this workflow.

## Read-back acceptance

For a test meeting, verify: one top-level card; full reviewed email in Discussion;
Tasks list with resolved links and owners; review-only leaves boards unchanged;
distribution moves only selected actions into human Inboxes; a repeated request
reuses the same IDs; no Ted assignment, production event or run is created.

## Distribution execution and legacy cards

Distribution must run as a finite loop over every approved action, not stop after
listing the tasks. Build a manifest of task ID, human, personal project and Inbox;
write `assignee`, `projectId` and `section` together with `update_task`; read each
record back and require all three fields to match. Count moved, already routed and
unresolved separately. Never say done while any intended destination is unverified.
When a legacy meeting lacks a Description register, inspect its subtasks and the
reviewed links/corrections in Discussion. Reuse them; do not manufacture tasks from
summary coverage gaps. Explicitly approved missing actions still require deduplication.
Post the verified links and destination board/Inbox in the meeting's Discussion as
well as preserving any legacy Description register. A follow-up asking for those links is
not proof the move happened: verify actual destinations before describing them as
already dispersed. The BasicOps webhook entry skill contains this loop directly;
it must not depend on an un-preloaded production router to enforce distribution.
