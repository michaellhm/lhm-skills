---
name: website-project-cockpit
description: Use for website status, gates and BasicOps handoffs.
---

# Website Project Cockpit

Turn the client's canonical website project record into one operational answer. The user should not need to hunt through Obsidian, GitHub, BasicOps, WhatsApp, or email to understand the next move. Website status is read-only; the only pilot mutation is approval-gated BasicOps task creation under the rules below.

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

Do not inspect the website repository, GitHub, BasicOps, WhatsApp, email, CMS, or live site unless the user explicitly asks for verification and an authorised tool is available. Report those states as unverified when the project note lacks evidence.

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

## BasicOps handoffs and authority

BasicOps owns assigned work; Obsidian remains the durable project and approval record. `*Web Projects`
remains the home for shared website project state, dedicated parents and milestones. A
direct-person website action is distinct from that shared state: once approved, it may live in the
assignee's canonical personal Inbox while retaining its native website-parent link and context.

Every BasicOps creation or mutation must route through `lhm-project-hub:basicops-task-manager`. This cockpit prepares the website-specific context, readiness, blockers and next handoff; the shared skill owns the final wording, approval check, deduplication, mutation and read-back verification. Do not write to BasicOps directly from this skill.

Before offering or creating a task, prepare this exact payload:

- stable deduplication key using `website:<client-slug>:<phase-or-gate>:<outcome>`
- concise outcome-based title using the LHM naming convention below
- accountable human owner
- source Obsidian note
- one short human discussion message containing the context and next handoff
- description only when a useful working URL belongs on the task
- readiness and blockers
- due date, or `needs scheduling`

Do not bundle different owners or outcomes into one task. For Alpha's five-page learning batch, Michael's selection of five materially different template pages is a separate prerequisite from Kristalyn's copy-production task and Aiya's build task.

### Website payload guidance

Use this title shape:

`<CLIENT LABEL>: <WORKSTREAM> - <PLAIN ACTION>`

- Use the team's established uppercase client abbreviation: `RTB`, `EHP`, `THC`.
- Use `Alpha` for Alpha Sports Med; do not force `ASM`.
- If a client label is not recorded, inspect existing BasicOps tasks or canonical client context. Never invent an abbreviation.
- Use a recognisable workstream such as `Website`, `Google Ads`, `SEO` or `GMB`.
- Write the action as the shortest natural summary of what the person must do. Avoid process language such as “materially different template-validation pages from sitemap v5” in the title.
- Example: `Alpha: Website - Create content for five pages`.

Keep the BasicOps description blank by default. Put only useful reference links there, such as a Fathom recording, website, prototype, staging page, working document or repository URL. Do not put internal context, dependencies, acceptance tests, deduplication metadata or `needs scheduling` prose in the description.

After creation, add one discussion message written directly to the assignee:

1. Start with `<First name>, we need to…`
2. Give only enough project context to understand the outcome.
3. End with what happens next and who receives the handoff.

Keep the message conversational and normally under 100 words. The task is an action prompt, not the full project brief. If the assignee asks for more context, use Hermes to read the client project note, approved client context and relevant LHM knowledge, then answer in conversation without bloating the task.

### Approval

- Show the exact payload before creation unless the user's current message already clearly authorises that exact task.
- Michael may approve a task assigned to Michael. A clear request such as “create a task in Michael's BasicOps to select the five pages” is approval for that one payload.
- Use `basicops-task-manager`'s plugin-wide authority contract for every exact task creation or move.
  Do not add a cockpit-specific assignee-approval rule or infer authority from preparation.
- Never invent a due date. Leave it unset when none is recorded.
- Task creation never records project approval or authorises copy, merge, deployment, publishing, or launch.

### Shared creation and verification

Pass the approved payload to `lhm-project-hub:basicops-task-manager`. The following routes are website-specific inputs to that shared skill:

Michael's personal route is fixed:

- Project: `Michael Tasks` (`49020`)
- Section: `INBOX` (`74627`)
- Assignee: Michael (`36398`)

For shared team website state, keep the dedicated parent and milestones in `*Web Projects`
(`68635`). For an approved direct-person website brief, read the assignee's canonical profile and
pass its personal project/Inbox/assignee route plus the originating website parent name/ID/URL to
the shared skill. The action may route to that personal Inbox only when the native website-parent
link and context remain attached and can be verified.

Fail closed when the website parent is unresolved, the personal route is absent or ambiguous, the
profile and live route disagree, the destination is not the canonical Inbox, or the move would
detach the action from the `*Web Projects` topology. Do not substitute `*Client Flow`, `None` or a
similarly named personal section.

### Still prohibited

- Do not edit the Obsidian project note or record approval as part of task creation.
- Do not contact the client/team, alter CMS content, commit, merge, deploy, publish, launch, complete, reassign or delete tasks.
- When an action exceeds the pilot, say what is prepared and name the approval or authorised workflow needed next.

End status answers with one natural prompt such as: `Want me to prepare that handoff for review?` Do not offer several competing next steps.
