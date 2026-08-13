---
name: basicops-task-manager
description: Create, classify, update, assign, discuss, complete, move, or otherwise mutate LHM BasicOps tasks. Use whenever a user or another LHM Project Hub workflow asks to write anything in BasicOps, including "create a task", "classify this task", "add this to BasicOps", "assign this", "update the task", "mark it complete", or "add a discussion note". This is the mandatory shared BasicOps mutation boundary for all Project Hub skills; other skills may prepare project context but must route the final task payload and write through this skill.
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

If essential routing or ownership is missing, ask one concise question. Do not invent it.

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

When a workflow creates subtasks:

1. Create the parent and subtasks in the governed project route.
2. Put each task's actionable explanation in its own Discussion; keep Description to valid LHM metadata and approved working URLs.
3. After the subtask IDs are verified, add a clearly labelled `Linked subtasks` message to the **parent task's Discussion** using native BasicOps task record links for every subtask.
4. Do not put the linked-subtasks list in the parent Description.
5. Preserve the parent's linked-subtasks discussion if subtasks are later moved to other projects.
6. After creation and verification, always ask the user in the current interface—Hermes, Chat, Codex or Claude: **Would you like me to move the subtasks to each assignee's individual board?**
7. Never move subtasks automatically. Wait for explicit user confirmation, then resolve each person's actual board and destination section through BasicOps before moving anything.

The question is mandatory even when the subtasks already have assignees. Creating subtasks and moving them to personal boards are separate mutations with separate authority.

## Prepare the exact payload

Before writing, prepare and, when approval is required, show:

- title
- assignee
- destination project and parent/section
- exact LHM metadata line and description URL(s)
- discussion message
- handoff trigger, next person/action and notification channel
- due date, or `unset`
- internal deduplication key

Use a stable key shaped like `basicops:<client-slug>:<workstream>:<outcome>`. Keep it in the workflow handback or canonical project record when needed; never expose it in the task title, description or discussion.

## Enforce authority

- A clear user instruction to create an exact task for themselves authorises that one payload.
- During the pilot, a task assigned to Kristalyn, Aiya, Jaimee or another team member requires that assignee's explicit approval unless the canonical workflow records Michael's explicit graduation of that routine task type.
- If the request is only conceptual or the payload is not exact, prepare it without writing.
- Never invent a due date.
- Task creation does not record client approval or authorise scope, strategy, client commitments, copy approval, merge, deployment, publishing or launch.
- Apply the same authority check to edits, reassignment, completion, movement and deletion. Do not broaden a permission from one mutation to another.

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

For team client work, prefer the client's mother task on `*Client Flow` (`68655`) when that is the established route, and resolve the actual assignee through BasicOps.

Existing-client website projects use this governed exception:

- Project: `*Web Projects` (`68635`)
- Initial section: `Onboarding & Briefing` (`107719`)
- Create or reuse a dedicated website parent task and place its milestones beneath it.
- Never leave the parent or newly created website subtasks in `None`.
- Add the verified native subtask links to the parent Discussion, not Description.
- Then ask whether the user wants the subtasks moved to the individual assignees' boards.

## Hand back to the calling workflow

Return:

- result: `created`, `existing`, `updated`, `prepared`, `blocked` or `mismatch`
- verified BasicOps URL when one exists
- final title and owner
- next handoff
- handoff notification result: `prepared`, `sent`, `not_required`, `blocked` or `not_approved`
- any missing approval or routing input
- when subtasks were created, the user's answer—or the still-outstanding question—about moving them to individual boards

Do not update Obsidian merely because a task was created. Let the owning Project Hub workflow record only the appropriate canonical project-state change under its own authority.
