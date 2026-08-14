# Acceptance tests

## Direct Michael task

Prompt: `Create a task in Michael's BasicOps to review whether Alpha's new Hawthorn location is included in the website scope.`

Expected:

- Title: `Alpha: Website - Review Hawthorn location scope`
- Michael Tasks / INBOX / Michael
- Blank description
- Human discussion beginning `Michael, we need to…` and ending with the Kristalyn handoff
- No invented due date
- Duplicate search, read-back and verified URL

## Context-heavy source

Prompt contains sitemap versions, scope implications, dependencies and acceptance tests.

Expected: preserve useful detail in Hermes/project context; do not place it in the title or description. Discussion remains under 100 words.

## Team assignment during pilot

Prompt: `Create a task for Kristalyn to coordinate Alpha's five-page copy batch.`

Expected: prepare the exact task and request Kristalyn's explicit approval before assignment unless the canonical workflow records graduation for this routine task type.

## Duplicate request

Repeat an already-created task request with different wording.

Expected: find the materially equivalent open task and return its URL without creating another.

## Unknown client label

Prompt names a client with no recorded abbreviation.

Expected: inspect canonical client context or existing BasicOps tasks; never invent an abbreviation.

## Reference URL

Prompt includes a Fathom or staging URL.

Expected: description contains only the useful URL; context and next handoff remain in discussion.

## Universal discussion invariant

Calling workflow supplies a detailed brief, dependencies, completion test and mother-task relationship inside the proposed Description.

Expected: reject that field placement; keep Description blank except for approved working URLs and move every human explanation, relationship, dependency, completion test and handoff into Discussions before writing.

## Actionable next steps

Prompt supplies an outcome, source document, approval dependency and downstream handoff.

Expected: the task Discussion states the outcome, practical ordered next steps, known inputs/dependencies, completion condition and next handoff. Missing details are identified rather than invented. Description remains blank except for approved working URLs.

## Existing-client website routing

Prompt asks to create a new website project for an existing client.

Expected:

- `*Web Projects` (`68635`)
- `Onboarding & Briefing` (`107719`), never `None`
- Dedicated website parent task with milestones beneath it
- Working context in Discussions, not Descriptions

## Parent links to created subtasks

A workflow creates a parent task and three subtasks.

Expected:

- Each task receives its actionable context in Discussion
- Parent Description remains blank except for separately approved working URLs
- Parent Discussion receives one clearly labelled `Linked subtasks` message containing native BasicOps record links to all three verified subtasks
- Read-back verifies that every link appears in the parent Discussion

## Individual-board confirmation

A workflow successfully creates and links subtasks assigned to several team members.

Expected: after verification, ask `Would you like me to move the subtasks to each assignee's individual board?` in the active interface. Do not move anything until the user explicitly confirms. If confirmed, resolve each destination board and section through BasicOps before moving.

## Staff board cleanup trigger

Prompt: `Help me clean up Kristalyn's board and give me the next five tasks.`

Expected:

- Authenticate the requester and resolve Kristalyn's canonical board and assignee from `22 People`
- Inventory read-only before recommending changes
- Present five linked tasks or task clusters, ranked by blockers, confirmed urgency, overdue client commitments and role follow-up before generic old backlog
- Read Discussion history, creator/latest relevant commenter, parent/subtasks and related project context
- Show exact proposed metadata, status/list, overdue disposition and next handoff
- Make no mutation until the user approves the batch

## Nested checklist protection

A board inventory surfaces many generic build checklist tasks that are subtasks of active or parked website parents.

Expected: group the subtasks beneath each linked parent, explain the project stage and do not recommend bulk archival merely because the subtasks are hidden or assigned to another person. Reconcile active website parents with `*Web Projects` and vault state before proposing closure or archival.

## Overdue workload negotiation

An overdue task cannot fit this week and another person or client is waiting on it.

Expected: propose one explicit disposition and, where needed, prepare a pushback or expectation-reset message naming the correct owner and channel. Do not invent a due date or claim that a BasicOps comment sent an external notification.

## Approved cleanup batch

The authenticated requester approves exact changes for three of five reviewed tasks.

Expected: mutate only those three, add traceable Discussion notes, preserve accountable owners, read each changed task back and verify all relevant fields, then offer the next five.

## Client touchpoint cadence

Prompt: `Classify this fortnightly client follow-up. The last verified email was sent on 3 August
2026 and the next is due 17 August 2026.`

Expected: retain the underlying work type; use `service=client-comms`; include
`last_touchpoint=2026-08-03`, `touchpoint_cadence=fortnightly` and
`next_touchpoint=2026-08-17`; cite sent-email evidence in Discussion; do not treat a draft or task
comment as contact; seek approval before writing.

## Consolidated client follow-up

Three tasks for the same client require one email asking for related project inputs.

Expected: propose one consolidated follow-up checklist, preserve links to absorbed tasks, keep the
underlying project classification, and never send or mark contact complete without separate
approval and evidence.
