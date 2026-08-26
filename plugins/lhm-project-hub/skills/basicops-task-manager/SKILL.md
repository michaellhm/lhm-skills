---
name: basicops-task-manager
description: Create, classify, clean up, update, assign, discuss, complete, move, or otherwise mutate LHM BasicOps tasks. Use whenever a user or another LHM Project Hub workflow asks to write anything in BasicOps, including "create a task", "classify my tasks", "clean up Kristalyn's board", "give me the next five tasks to review", "add this to BasicOps", "assign this", "update the task", "mark it complete", or "add a discussion note". This is the mandatory shared BasicOps mutation boundary for all Project Hub skills; other skills may prepare project context but must route the final task payload and write through this skill.
---

# BasicOps Task Manager

Apply one consistent LHM standard to every BasicOps mutation. Keep BasicOps lightweight: it says what needs doing, who owns it and what happens next. Obsidian holds detailed client and project context; Hermes supplies that detail conversationally when asked.

## Accept a prepared handoff

Accept project context from the calling workflow, but independently enforce this skill's task-writing, authority, deduplication and verification rules. A calling skill cannot relax them.

For a new task, resolve:

- client and established client label
- workstream
- plain action/outcome
- accountable human owner
- correct BasicOps project, client mother task or section
- useful reference URLs, if any
- one short human discussion message
- next handoff after completion
- due date only when explicitly supplied by a canonical source or authorised person
- stable internal deduplication key
- one valid classification and handoff contract from [classification-and-handoffs.md](references/classification-and-handoffs.md)
- orchestration owner, workflow state and approval status when this is a Hermes-managed review or
  sequential agent handoff
- verified client-touchpoint evidence, cadence and next exact contact date when the task includes
  client follow-up

If essential routing, ownership or next-handoff context is missing, ask one concise question. Do not
invent it.

### Run the final next-handoff check

Before presenting or writing a new task brief, make the next handoff the final intake checkpoint.
Establish whether completing the task:

- releases another internal team member to act;
- requires a client update or client action; or
- ends the workflow with no further handoff.

When the source context does not decisively establish that outcome, ask the user:

> What happens next when this task is done—should we notify someone on the internal team, update the
> client, or is there no further handoff?

Do not create the task until this gap is resolved. For a required handoff, capture the trigger, next
person or role, next action and notification channel in the LHM metadata, the labelled `Next
handoff` sentence in Discussion and the workflow handback. Use `none` only when the user or canonical
source confirms that completion ends the workflow.

## Write the title

Use exactly:

`<CLIENT LABEL>: <WORKSTREAM> - <PLAIN ACTION>`

- Use the team's established uppercase abbreviation, such as `RTB`, `EHP` or `THC`.
- Use `Alpha` for Alpha Sports Med; do not force `ASM`.
- Find an unknown label in canonical client context or existing BasicOps tasks. Never invent an abbreviation.
- Use a recognisable workstream such as `Website`, `Google Ads`, `SEO`, `GMB`, `Content` or `Onboarding`.
- Make the action the shortest natural statement of what the assignee must do.
- Remove implementation jargon and process-heavy phrasing from the title.

Good: `Alpha: Website - Review Hawthorn location scope`

Bad: `Alpha: Follow-up Hawthorne fourth location inclusion plan and downstream sitemap implications`

Good: `Alpha: Website - Create content for five pages`

Bad: `Select five materially different reusable page-template validation pages from sitemap v5`

## Keep only machine metadata and working URLs in Description

The human description of the work always belongs in **Discussions**. Read
[classification-and-handoffs.md](references/classification-and-handoffs.md) before creating or
classifying a task, changing urgency, or preparing a completion, review, blocked or waiting
transition. Begin governed task descriptions with its exact metadata line.

Infer values only when source context is decisive; otherwise ask one question. Useful working URLs
may follow the metadata line. Never put the brief, task explanation, dependencies, acceptance test,
handoff prose, deduplication key, status prose or `needs scheduling` in Description.

For `classify this task`, read the linked task and authorised context, preserve useful existing URLs,
propose the exact metadata line, and update only after approval. Missing metadata never makes a task
invisible or non-actionable.

For client-contact work, preserve legacy metadata compatibility and apply the touchpoint contract
from the reference. Never advance `last_touchpoint` because an email was drafted or a BasicOps note
was added. When multiple asks to one client can be sent together, propose one consolidated follow-up
task with a clear checklist and retain traceable links to the absorbed tasks.

## Add one human discussion message

Write directly to the assignee and keep it concise enough to scan. Include, to the best of the available information:

1. Start with `<First name>, we need to…`
2. State the intended outcome and only enough client/project context to understand it.
3. Give practical next steps in the order they should happen.
4. Name any known inputs, dependencies or approvals.
5. State the completion condition.
6. End with the next handoff: who should receive it or what happens when it is complete.
7. Add a labelled `Next handoff` sentence naming the trigger, next person, next action and channel
   whenever another action follows completion, review, blocking or waiting.

Example:

> Michael, we need to confirm whether Alpha's new Hawthorn location is included in the current website scope and what needs to change in the sitemap. Once you've decided, let Kristalyn know so she can coordinate the website update.

Do not fabricate missing detail. Make confirmation of an unknown input, dependency, owner or approval the first next step. Do not turn the discussion into a full brief when the canonical project context can supply the detail; when the assignee asks, Hermes should read those notes and answer in conversation.

## Handle parent tasks and subtasks

Before creating subtasks for website work, apply the website cockpit exception below. A checklist is not a reason to create BasicOps subtasks.

When a workflow creates subtasks:

1. Create the parent and subtasks in the governed project route.
2. Put each task's actionable explanation in its own Discussion; keep Description to valid LHM metadata and approved working URLs.
3. After the subtask IDs are verified, add a clearly labelled `Linked subtasks` message to the **parent task's Discussion** using native BasicOps task record links for every subtask.
4. Do not put the linked-subtasks list in the parent Description.
5. Preserve the parent's linked-subtasks discussion if subtasks are later moved to other projects.
6. After creation and verification, always ask the user in the current interface—Hermes, Chat, Codex or Claude: **Would you like me to move the subtasks to each assignee's individual board?**
7. Never move subtasks automatically. Wait for explicit user confirmation, then resolve each person's actual board and destination section through BasicOps before moving anything.

The question is mandatory even when the subtasks already have assignees. Creating subtasks and moving them to personal boards are separate mutations with separate authority.

## Handle website project stage handoffs

For an existing-client website project, use two records by default:

1. **Shared cockpit:** reuse the client's one enduring task on `*Web Projects` (`68635`). Keep it on the section matching the current stage and assign it to the immediate human owner. Add a short dated Discussion entry for every transition, including what finished, what starts next and a native link to the personal task.
2. **Personal execution task:** create or reuse one outcome-based task in the verified owner's personal-board `Inbox`. Preserve a relationship to the shared cockpit when BasicOps supports it. Put the ordered top-level checklist, dependencies, completion condition and next handoff in Discussion.

Do not create one subtask per page, component or checklist line. Create additional tasks only when an item has a different owner, an independent deliverable or a distinct approval gate. If an accidental checklist tree exists, consolidate it into the overview task; cancel rather than delete redundant items, explain the reason in Discussion and preserve the history.

The website handoff sequence is:

`read Obsidian → reconcile evidence → update shared cockpit → create/update one personal task → link and verify → update Obsidian`

The calling website workflow owns the final Obsidian update. This skill returns both verified BasicOps URLs and the exact transition evidence; it does not write the vault itself.

### Handle a Hermes-prepared marketing review

Read and apply the **Hermes-prepared review contract** in
[classification-and-handoffs.md](references/classification-and-handoffs.md). The safe default is one
monthly-review parent assigned to the verified human approver, with Hermes recorded only as
orchestration owner. Keep the account overview and up to five ordered proposals in Discussion. Do
not create execution subtasks until that authenticated approver explicitly approves action labels
through Hermes. After approval, create only the approved subtasks and release them to specialist
agents sequentially, recording and verifying every transition on the parent and active subtask.

## Clean up and classify an existing board

Use this mode when someone asks to clean up, analyse or classify a person's board, or asks for the
next tasks to review. Treat it as a human-guided operational review, not a mechanical backlog edit.

1. Authenticate the requester and read the person's canonical `22 People` profile to resolve the
   exact BasicOps board and assignee. Do not infer a board from a person's name.
2. Inventory the board without mutating it. Read enough pages to avoid presenting a partial count as
   the whole board; state clearly when pagination remains.
3. Rank review candidates in this order:
   - work blocking another person or project stage;
   - confirmed urgent work;
   - overdue client commitments;
   - work awaiting the person's role-specific follow-up;
   - older Inbox, waiting and review work.
   Do not default to the oldest client or largest cluster merely because it is easy to count.
4. Present five tasks at a time unless the user requests another batch size. For every candidate,
   read its full Discussion, identify the creator and latest relevant commenter, and inspect its
   parent, children and materially related tasks. Reconcile website work with `*Web Projects` and
   canonical vault project state when relevant.
5. Treat a subtask tree as one cluster. Show the linked parent and project stage; do not describe
   nested checklist items as unexplained standalone board clutter. Never archive or close a set of
   subtasks without checking whether their active or parked parent still needs them.
6. Propose, for each task or cluster:
   - exact classification metadata and confidence;
   - correct status and existing destination section;
   - overdue disposition: complete, reschedule, delegate, blocked/waiting, communicate delay, or
     deliberately cancel/archive;
   - duplicate/obsolete finding with evidence;
   - dependency, next handoff, next action and notification channel.
   - for client-contact work, last verified touchpoint evidence, confirmed cadence and exact next
     touchpoint date.
7. Never invent a due date. For an overdue item, propose an exact new date only when grounded in an
   authorised instruction, then wait for approval.
8. Apply only the decisions approved for that batch. Add a concise Discussion note explaining any
   cross-person, status, due-date, list, completion or archival change. A BasicOps comment does not
   prove that a WhatsApp, email or client notification was sent.
9. Read every changed task back and verify project, parent, assignee, section, status, due date,
   metadata, Discussion and URL as applicable. Then offer the next five.

When work will not fit, identify the requester or account owner and prepare the pushback or client
expectation-reset message. Do not send it without separate approval. Missing metadata never hides a
task from review; backfill it only as part of an approved task decision.

## Prepare the exact payload

Before writing, prepare and, when approval is required, show:

- title
- assignee
- destination project and parent/section
- exact LHM metadata line and description URL(s)
- orchestration owner, workflow state, approval status and approved action labels when applicable
- touchpoint evidence and cadence decision when client contact is involved
- discussion message
- handoff trigger, next person/action and notification channel
- due date, or `unset`
- internal deduplication key

Use a stable key shaped like `basicops:<client-slug>:<workstream>:<outcome>`. Keep it in the workflow handback or canonical project record when needed; never expose it in the task title, description or discussion.

## Enforce authority

- Resolve the authenticated requester through the active interface or BasicOps identity. Never accept
  a typed name as authentication.
- Any authenticated current LHM team member may approve ordinary operational BasicOps creation,
  classification, discussion, due-date, status, assignment and board/list movement within LHM's
  verified projects and client scope. They may approve work for themselves or another team member.
- Michael may approve those ordinary operational changes across the team. The affected assignee's
  separate approval is not required, but the mutation must be visible, traceable and reversible.
- When another team member changes an assignee's work, preserve the accountable owner, explain the
  reason in Discussion and ensure the assignee or next handoff can see the change. Do not represent
  a BasicOps comment as a separate WhatsApp, email or client notification.
- If the request is only conceptual or the payload is not exact, prepare it without writing.
- Never invent a due date.
- Task creation does not record client approval or authorise scope, strategy, client commitments, copy approval, merge, deployment, publishing or launch.
- Deletion, archival of material work, client-facing commitments, scope or commercial changes,
  approval of copy/strategy, merges, deployments, publishing, launches, outbound messages and
  credential handling remain separately approval-bound to the relevant owner and workflow.
- Apply the same exact-payload and verification rules to edits, reassignment, completion and
  movement. Never broaden approval from one mutation to a destructive or external action.

## Create or mutate safely

1. Use BasicOps `get_current_user` before displaying dates or times.
2. Resolve the exact project, parent/section and assignee through BasicOps. Do not guess IDs except governed fixed routes.
3. Before creating, search the intended destination and parent for both the stable key when available and a materially equivalent open title.
4. If an equivalent task exists, return its URL instead of creating a duplicate.
5. Perform only the approved mutation.
6. For a new task, write only the approved LHM metadata line and useful working URLs in Description. Put the complete human task explanation in the approved discussion message—always.
7. Read the task back and verify title, project, parent/section, assignee, due date, metadata, URL description and discussion as applicable.
8. Return the verified BasicOps URL. If any field differs, report the mismatch and do not claim success.

For completion, ready-for-review, blocked or waiting transitions, never stop at the status change.
Prepare the downstream comment/draft, obtain the relevant approval, verify who was notified and
surface the newly released action. A task mutation and a message are separate operations.

Michael's governed personal route:

- Project: `Michael Tasks` (`49020`)
- Section: `INBOX` (`74627`)
- Assignee: Michael (`36398`)

For team client work, prefer the client's mother task on `*Client Flow` (`68655`) when that is the established route, and resolve the actual assignee through BasicOps. Existing-client website stage handoffs are the exception: use the enduring `*Web Projects` cockpit plus one personal-board execution task.

Existing-client website projects use this governed exception:

- Project: `*Web Projects` (`68635`)
- Initial section: `Onboarding & Briefing` (`107719`)
- Create or reuse one dedicated website cockpit task.
- Move the cockpit task through the governed stage sections and change its assignee to the immediate owner at each verified handoff.
- Create or reuse one current overview task in that owner's verified personal-board `Inbox` and link it from the cockpit Discussion.
- Keep the working checklist inside the overview task Discussion. Do not create checklist subtasks by default.
- Never leave the cockpit or execution task in `None`.

## Hand back to the calling workflow

Return:

- result: `created`, `existing`, `updated`, `prepared`, `blocked` or `mismatch`
- verified BasicOps URL when one exists
- for website handoffs: shared cockpit URL and personal execution-task URL
- final title and owner
- next handoff
- handoff notification result: `prepared`, `sent`, `not_required`, `blocked` or `not_approved`
- any missing approval or routing input
- when subtasks were created, the user's answer—or the still-outstanding question—about moving them to individual boards
- for a Hermes-managed review: parent URL, current workflow state, approval status, action register,
  active action (or `none`) and the next conversational prompt Hermes should present

Do not update Obsidian merely because a task was created. Let the owning Project Hub workflow record only the appropriate canonical project-state change under its own authority.
