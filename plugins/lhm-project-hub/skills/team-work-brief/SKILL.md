---
name: team-work-brief
description: Turn a rough request, client email, message, meeting action or idea into a complete internal team brief and approved BasicOps handoff. Use for any LHM user—including Michael, Josephine, Kristalyn, Jaimee or Aiya—when they say "brief Aiya", "brief AR", "brief Jaimee", "brief Kristalyn", "brief Michael", "brief Josephine", "brief Chris", "hand this to the team", "create a brief", "delegate this", "turn this email into a task", or give feedback that a prior brief was missing context, access, a URL or another requirement. Reads requester, client, assignee and project context; asks one material question at a time; checks access, dependencies, evidence, authority, completion and review; then routes the approved task through lhm-project-hub:basicops-task-manager. Captures controlled person-, client- and process-level handoff learning in the Obsidian Brain.
---

# Team Work Brief

Convert incomplete human instructions into work another person can start and finish without reconstructing the request. Do not merely polish the request. Test whether it is ready.

This workflow is for every authorised LHM Hermes user. Resolve identity from the channel/profile; never assume the requester is Michael.

Read [readiness-and-learning.md](references/readiness-and-learning.md) before preparing or learning from a brief.

## 1. Establish the handoff

Identify:

- requester
- intended assignee
- client
- relevant project or workstream
- rough requested outcome
- source message, email, meeting action or link

Use conversation context first. Ask only for the first missing fact that changes what should be read or who should own the work. Usually resolve the client before asking detailed work questions.

Recognise aliases from canonical profiles. `AR` means Aiya only where the current LHM context establishes that alias; present her as **Aiya**, not AR. If a named person such as Chris Sloan has no canonical profile or clear client relationship, ask who they are and what role they have before assigning work.

## 2. Read minimum canonical context

Read only what applies:

1. `22 People/<Requester>.md`
2. `22 People/<Assignee>.md`, if internal
3. `20 Clients/<Client>/<Client>.md`
4. `20 Clients/<Client>/Current Projects.md`
5. the applicable file under `20 Clients/<Client>/project-management/`
6. a specifically relevant SOP, skill or knowledge note when the work type has non-obvious dependencies
7. source communication supplied by the requester

For an external contractor or client contact, prefer the client's `People.md`, overview, active project or other canonical relationship record. Do not invent their role, capability, access or authority.

Never expose unrelated protected information from a person or client profile. Use context only to improve the handoff.

For a direct-person brief, read the assignee profile's canonical BasicOps personal route: project
name/ID, semantic `inbox` section name/ID and assignee name/ID. The profile is the route basis; do
not infer a board or section from the person's name, another person's route or display order. Treat
the live BasicOps lookup as verification, not as permission to substitute a different route. If the
profile route is absent, incomplete, ambiguous, conflicts with another canonical source or does not
resolve live to that person's Inbox, stop before approval and report the exact routing mismatch.

## 3. Build the readiness model

Determine:

- **Outcome:** what must be true when the work is finished?
- **Owner fit:** is this inside the assignee's role and capability?
- **Scope:** what should change, and what must remain unchanged?
- **Work context:** which client, website project, parent task or workstream supplies the reason and
  durable project state?
- **Action destination:** which canonical BasicOps personal project and Inbox will hold this
  person's approved action?
- **Target:** which website, page, account, system, document or environment must change?
- **References:** current URL, staging link, source email, prototype, design, document or repository.
- **Access:** what login, permission or system access is required, and is access actually confirmed?
- **Dependencies:** approvals, assets, answers, upstream work or client decisions required first.
- **Authority:** may the requester decide this, or is scope, strategy, cost, production, publishing or client commitment approval missing?
- **Completion test:** how can the assignee and reviewer verify the outcome?
- **Next handoff:** who reviews, receives or approves the completed work?
- **Timing:** due date only when explicitly known.

Treat credentials safely: record that access exists, is missing or who must grant it. Never request or store passwords, tokens or secrets in Hermes, Obsidian or BasicOps. Refer to the approved password manager or access owner.

## 4. Sanity-check before questioning

Compare the rough request with the client, project, assignee and process context.

Classify each gap:

- `requester-answerable` — ask the requester.
- `client-answer-required` — prepare a plain-language client question; do not send it.
- `team-answer-required` — identify the internal person most likely to know.
- `access-required` — identify the system and access owner; never assume access.
- `wrong-or-uncertain-owner` — recommend or confirm the correct assignee.
- `approval-or-scope-required` — stop before task creation and identify the decision owner.
- `non-blocking` — record as a note or assumption only when safe and explicit.

Do not ask the requester to diagnose specialist requirements they are not expected to know. Consult the relevant project or specialist process, then ask in plain language. This is especially important for Josephine: help her discover the missing client question, access or technical dependency rather than expecting her to infer it.

Ask one material question at a time. Skip information already established by the Brain or source communication. Stop questioning when the task is genuinely startable, not when every imaginable detail is known.

## 5. Handle missing external information

When the client must answer, return:

```markdown
Before <assignee> can start, we still need:
- <missing fact or access confirmation>

Suggested client question:
“<short, plain-language draft>”
```

Client communication remains a draft. After the requester supplies the verified answer, continue the same brief and update canonical client/project context only through the authorised vault workflow.

## 6. Present the approval bundle

Show a compact bundle:

```markdown
**Brief ready for approval**

- Task: <LHM BasicOps title>
- Assignee: <person>
- Action destination: <canonical personal project / Inbox / assignee, with IDs>
- Retained work context: <client/workstream and originating parent name/ID/URL, or none>
- Outcome: <one sentence>
- References: <URLs or none>
- Access: <confirmed / missing / verification owner>
- Completion: <observable check>
- Next handoff: <person and action>
- Due: <date or unset>

**BasicOps discussion**
<short message addressed to the assignee>

**Still unresolved**
<none, or explicit non-blocking item>
```

Ask for approval of this exact brief, including both the action destination and retained work
context. A requester may approve their proposed brief, but BasicOps assignment authority still
belongs to `basicops-task-manager` under its plugin-wide authority contract. Approval is invalid if
the personal route, Inbox destination or originating parent/context is unresolved.

## 7. Create through the shared boundary

After the required approval, invoke `lhm-project-hub:basicops-task-manager` with:

- approved title
- client and workstream
- assignee
- route basis from the assignee's canonical profile
- canonical personal project, Inbox section and assignee names/IDs
- originating project/parent/context name, ID and URL (or an explicit `none` when no parent exists)
- useful URLs only for the description
- approved discussion
- due date or unset
- next handoff
- stable deduplication key

Never create or mutate BasicOps directly from this skill. Return the shared skill's verified URL and result.

An approved direct-person brief routes to the assignee's canonical personal **Inbox** while
retaining the originating parent/context through BasicOps' native parent relationship and verified
links/Discussion as applicable. A client, website or shared project remains work context; it is not
the action destination for a direct-person brief. Fail closed rather than creating or moving when
the route is absent, missing, ambiguous or conflicting, when the destination is not the canonical
Inbox, or when parent/context preservation cannot be stated exactly.

## 8. Learn from handoff feedback

Trigger learning when a requester or assignee says a brief was missing something, included unnecessary detail, used the wrong owner, lacked access, omitted a URL, or should work differently next time.

Apply the current-task correction immediately when authorised. Then classify the learning using [readiness-and-learning.md](references/readiness-and-learning.md):

- one-off task or client fact
- person-stated handoff preference
- candidate work-type/process requirement
- contradiction or authority change

Do not turn one comment into an agency-wide rule. A person may establish a preference for briefs they receive. Process-wide rules require Michael's explicit approval or materially equivalent recurrence in at least two independent sessions, following the vault's recurrence contract.

Use the authorised Obsidian workflow for durable writes. Re-read the target immediately before editing and preserve source/date. Never write credentials. The canonical destinations are:

- client/project fact → applicable client overview or project-management note
- assignee's own confirmed preference → `## Handoff preferences` in `22 People/<Person>.md`
- unproven reusable observation → the current sprint/meeting evidence with `Observe again`
- approved or recurrent cross-team requirement → `60 Knowledge/Team Briefing and Handoff Standard.md`, and update this skill or the relevant SOP when the requirement changes execution
- unresolved contradiction or authority decision → retain both positions and route to Michael only when his decision is genuinely required

After learning, tell the person what was updated, what is only being observed, and what Hermes will ask next time.
