---
name: website-project-cockpit
description: Coordinate website project status and stage handoffs across Obsidian and BasicOps. Use when a user asks where a website project is at, what happens next, or asks to brief, assign or hand off Astro, WordPress, Decap, design, copy, development, SEO, QA or go-live work.
---

# Website Project Cockpit

Turn the client's canonical website project record into one operational answer or verified stage handoff. The user should not need to hunt through Obsidian and BasicOps to understand the next move.

## Operating model

Use three distinct layers:

1. **Obsidian project record** — durable source of truth for phases, evidence, approvals, completed work, decisions, blockers and the next action.
2. **Shared `*Web Projects` cockpit task** — one enduring project overview and dated transition trail. Its section and assignee show the current delivery stage and immediate owner.
3. **Personal-board task** — one current actionable brief in the verified owner's `Inbox`, linked from the shared cockpit.

Do not reproduce the full project plan in BasicOps. Do not create one BasicOps subtask per checklist item. Keep the checklist inside the personal task's Discussion. Create separate tasks only when work has a different owner, an independently trackable deliverable or a real approval gate.

## Resolve the client

1. Extract the client name from the request or recent conversation.
2. Search the vault's client area for a matching folder. Prefer `20 Clients/<Client>/` and tolerate a vault prefix such as `Local Health Marketing/20 Clients/<Client>/`.
3. If two plausible clients remain, ask one short clarification question. Never guess.

## Read the minimum canonical context

Read, when present:

1. `<client>/project-management/Website Rebuild.md`; otherwise `<client>/project-management/website.md`
2. `<client>/Current Projects.md`
3. `<client>/Copy Learning Guide.md` only when the current or next gate concerns scaled copy
4. A specifically linked evidence file only when needed to verify the active gate

Read BasicOps when a status question requires reconciling the current owner/task, or when preparing a handoff. Do not inspect the website repository, GitHub, WhatsApp, email, CMS, or live site unless the user explicitly asks for verification and an authorised tool is available. Report those states as unverified when the project note lacks evidence.

## Determine operational state

Use explicit fields and evidence before checkbox order. Determine:

- current phase
- active gate: the decision or evidence that must exist before dependent work should proceed
- gate state: `ready`, `waiting`, `blocked`, or `unverified`
- evidence: source, date, and version/link when recorded
- immediate owner
- one next action that advances the gate
- blockers and missing inputs
- schedule risk: `none recorded`, `watch`, or `at risk`, with a short reason
- prepared handoff: only when prerequisites are evidenced

Approval rules:

- Never infer client approval from “sent”, “reviewed”, a completed design, or an unticked task.
- Treat approval as verified only when the record contains an approval source and date; include version/link where applicable.
- Client approval does not grant merge, deployment, publishing, or launch authority.
- If the record and checklist conflict, state the contradiction and prefer the evidence-backed fact.
- The first incomplete checkbox is not automatically the next action; dependencies and gates decide priority.

## Response modes

Infer the mode from the request:

- **Status:** “Where is Alpha at?”
- **Attention:** “What website work needs my attention today?”
- **Blockers:** “What is holding Alpha up?”
- **Handoff:** “Is the next Alpha handoff ready?”

For one project, use this compact format:

```markdown
**<Client> — <phase>**

- Gate: <state> — <gate>
- Evidence: <source/date/version, or exactly what is missing>
- Owner: <person>
- Next action: <one concrete action>
- Blockers: <none, or concise list>
- Schedule: <none recorded | watch | at risk> — <reason if applicable>
- Handoff: <not ready | prepared for approval | ready under recorded authority>
```

Then add `Why this is next:` only when the dependency is not obvious. Keep a normal response under 180 words.

For an attention-across-projects request, scan only active website blocks in client `Current Projects.md` files, then return at most five items ordered by:

1. gate blocked or overdue
2. Kristalyn-owned action
3. external approval waiting without evidence
4. dependency that unlocks multiple downstream tasks

## Execute a website stage handoff

Follow this order:

1. Read the canonical Obsidian website project record and `Current Projects.md`.
2. Reconcile the user's update against recorded evidence. Tick or close only work supported by the update or a linked source; keep uncertain items open and name the gap.
3. Read or resolve the client's one enduring task on `*Web Projects`.
4. Determine the next stage, shared-board section, immediate human owner, one execution outcome and final handoff.
5. Reuse or create one overview task in that owner's verified personal-board `Inbox`. Keep it related to the shared cockpit task when BasicOps supports the cross-project parent relationship.
6. Put the outcome, ordered top-level checklist, dependencies, completion condition and next handoff in the personal task's Discussion.
7. Update the shared cockpit task's section and assignee. Add a short dated Discussion entry stating what finished, what starts now and a native link to the personal task.
8. Read both BasicOps tasks back and verify project, section, assignee, status, relationship, due date and Discussion link.
9. Route the durable Obsidian update through `lhm-project-hub:wp-project-manager`: record the stage transition, task links, immediate owner, evidence-backed completions, blockers and next action. Keep `Current Projects.md` aligned.

If the user requests only status or a prepared brief, stay read-only. A clear instruction from an authorised current team member to create or update the handoff authorises ordinary operational BasicOps and Obsidian project-state changes within the named client scope. It does not authorise scope, client commitments, copy approval, merge, deployment, publishing or launch.

## BasicOps payloads

BasicOps owns assigned work; Obsidian remains the durable project and approval record.

Every BasicOps creation or mutation must route through `lhm-project-hub:basicops-task-manager`. This cockpit prepares the website-specific context, readiness, blockers and next handoff; the shared skill owns the final wording, approval check, deduplication, mutation and read-back verification. Do not write to BasicOps directly from this skill.

Prepare two coordinated payloads:

**Shared cockpit transition**

- existing `*Web Projects` task ID and URL
- destination stage section
- immediate assignee
- short dated Discussion update
- native personal-task link

**Personal execution task**

- stable deduplication key using `website:<client-slug>:<phase-or-gate>:<outcome>`
- concise outcome-based title using the LHM naming convention below
- accountable human owner
- source Obsidian note
- one short human discussion message containing the context and next handoff
- verified personal project and `Inbox` section
- description containing only governed metadata and useful working URLs
- readiness and blockers
- due date, or `needs scheduling`

Do not bundle different owners or outcomes into one task. Once prerequisites are evidenced as complete, their result can be summarised in the next owner's overview task rather than retained as open execution subtasks.

### Website payload guidance

Use this title shape:

`<CLIENT LABEL>: <WORKSTREAM> - <PLAIN ACTION>`

- Use the team's established uppercase client abbreviation: `RTB`, `EHP`, `THC`.
- Use `Alpha` for Alpha Sports Med; do not force `ASM`.
- If a client label is not recorded, inspect existing BasicOps tasks or canonical client context. Never invent an abbreviation.
- Use a recognisable workstream such as `Website`, `Google Ads`, `SEO` or `GMB`.
- Write the action as the shortest natural summary of what the person must do. Avoid process language such as “materially different template-validation pages from sitemap v5” in the title.
- Example: `Alpha: Website - Create content for five pages`.

Keep the BasicOps description limited to the governed `LHM metadata` line and useful reference links such as a Fathom recording, website, prototype, staging page, working document or repository URL. Do not put internal context, dependencies, acceptance tests, deduplication keys or `needs scheduling` prose in the description.

After creation, add one discussion message written directly to the assignee:

1. Start with `<First name>, we need to…`
2. Give only enough project context to understand the outcome.
3. End with what happens next and who receives the handoff.

Keep the message conversational and scannable. A short top-level checklist is appropriate; the task is still an action prompt, not a copy of the full project plan. If the assignee asks for more context, read the client project note and relevant approved source material rather than bloating the task.

### Approval

- Show the exact payload before creation unless the user's current message already clearly authorises that exact task.
- Michael may approve a task assigned to Michael. A clear request such as “create a task in Michael's BasicOps to select the five pages” is approval for that one payload.
- Apply the shared BasicOps authority model: Michael and authenticated current LHM team members may authorise ordinary operational work for a verified teammate within client scope. Keep the cross-person change visible and reversible in Discussion.
- Never invent a due date. Leave it unset when none is recorded.
- Task creation never records project approval or authorises copy, merge, deployment, publishing, or launch.

### Shared creation and verification

Pass the approved payload to `lhm-project-hub:basicops-task-manager`. The following routes are website-specific inputs to that shared skill:

Michael's personal route is fixed:

- Project: `Michael Tasks` (`49020`)
- Section: `INBOX` (`74627`)
- Assignee: Michael (`36398`)

For existing-client website work, use the enduring parent on `*Web Projects` (`68635`) as the shared cockpit and the current owner's verified personal-board `Inbox` for the execution task. Do not route the execution task to `*Client Flow`.

### Still prohibited

- Do not record approval merely because a task was created. After a verified handoff, update only the evidence-backed project state through `wp-project-manager`.
- Do not contact the client/team, alter CMS content, commit, merge, deploy, publish or launch through this workflow.
- Complete or reassign tasks only when the user's instruction and verified stage evidence authorise that exact transition. Do not delete material task history.
- When an action exceeds the recorded authority, say what is prepared and name the approval or authorised workflow needed next.

End status answers with one natural prompt such as: `Want me to prepare that handoff for review?` Do not offer several competing next steps.
