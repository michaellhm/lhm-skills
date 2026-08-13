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
