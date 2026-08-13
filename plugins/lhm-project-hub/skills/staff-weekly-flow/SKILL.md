---
name: staff-weekly-flow
description: Plan and run a personalised LHM weekly-to-daily work flow for Michael, Kristalyn, Aiya, Jaimee or Josephine. Use when an authorised person asks “what should I focus on this week?”, “what should I work on today?”, asks specifically for business-growth or client-work priorities, wants to review or save their weekly priorities, or wants to configure their weekly/daily reminder time, timezone, channel, delivery mode, focus mode or priority limit. Read the person’s canonical Obsidian profile, verified BasicOps personal-board mapping, authorised project context and current weekly file; prepare a small realistic plan; save only after confirmation; and keep BasicOps mutations behind the shared task-manager approval boundary.
---

# Staff Weekly Flow

Give each LHM person a small, traceable operating plan without forcing them to reconstruct BasicOps or the Brain.

## Resolve the operating identity

1. Resolve the requester from the authenticated Hermes/Codex profile or channel binding. Never infer identity from a display name alone.
2. Read `_System/Vault Conventions.md` and `_System/Multi-Agent Memory Contract.md` completely.
3. Read `22 People/<Person>.md` and verify:
   - canonical name and role;
   - `basicops_project_name`;
   - `basicops_project_id`;
   - `basicops_project_url`;
   - `basicops_assignee_id`.
4. Use only that person's authorised client/project scope. Do not expose another person's private preferences or unrelated client context.
5. Fail closed when the identity, profile, project ID or assignee ID is missing or contradictory.

Use the person's folder `22 People/<Person>/`. Store preferences in `Weekly Flow Preferences.md` and weekly plans in `YYYY-Www — Weekly Flow.md`.

## Choose the intent

### Weekly planning

Trigger on “What should I focus on this week?”, equivalent planning requests or a scheduled weekly reminder.

1. Read `22 People/<Person>/Weekly Flow Preferences.md`. If absent, use `80 Templates/Weekly Flow Preferences Template.md` to prepare a first-run proposal; do not invent or silently save a schedule.
2. Determine the ISO week in the person's confirmed timezone. If timezone is unconfirmed, ask one question before scheduling or dating a saved plan.
3. Read only the minimum relevant context:
   - the person's canonical profile and quarterly commitment, if present;
   - their previous and current weekly files, if present;
   - open work from their verified BasicOps personal project;
   - authorised tasks intentionally nested beneath client, onboarding or website parent tasks;
   - active projects where they are the named owner or next handoff;
   - relevant meetings or dependencies for the week;
   - explicit blockers and overdue tasks.
4. Treat BasicOps as live task state and Obsidian as canonical project context. Do not copy the full board into the weekly file.
5. Classify unfinished or overdue work as `do`, `delegate`, `reschedule`, `communicate`, `redesign` or `drop`. Never complete, move, assign or edit a BasicOps task while planning.
6. Propose no more than `priority_limit` weekly outcomes. Default to three only when the preference file explicitly records three; otherwise ask or use three as a visibly provisional LHM suggestion.
7. For each proposed outcome state:
   - observable result;
   - first next action;
   - owner;
   - dependency or approval;
   - source task/project link;
   - completion condition;
   - who needs an update.
8. Surface excluded work and what must be communicated instead of overloading the person.
9. Ask one material question at a time. Do not save until the person confirms the plan.
10. After confirmation, write or update the current weekly file through the approved vault mutation route and verify the saved content.

#### Shared priority engine

Assemble candidates from four work streams before proposing priorities:

1. **Project cascade** — active work on BasicOps `*Web Projects` (`68635`) reconciled with the
   corresponding canonical website-project files in Obsidian. Identify the current phase/gate,
   task owner, due date, missing input, blocker, person waiting downstream and the exact action that
   releases the next stage. Do not treat either BasicOps or the vault alone as sufficient when both
   should describe the project.
2. **Client Flow** — the authorised portfolio on BasicOps `*Client Flow` (`68655`) plus canonical
   client/service context. Determine whether each client received or is due their weekly touchpoint,
   which service/relationship owner is responsible and whether a meeting follow-up, SEO update,
   Google Ads update or project-management summary already satisfied it.
3. **Role-based client delivery** — work inside the person's confirmed role: Michael's Google Ads,
   GoHighLevel, strategy and non-SEO meeting actions; Jaimee's SEO; Kristalyn's project coordination,
   approvals and client follow-up; Aiya's website production and fixes; Josephine's authorised
   administration and meeting follow-through. Read the canonical profile rather than relying only
   on this summary when role boundaries change.
4. **Individual/reactive work** — open work from the person's verified personal BasicOps project,
   including client-email requests, standalone actions, internal work and website fixes requested
   by another team member.

Rank the combined candidates in this order:

1. work blocking another person or the next project stage;
2. time-sensitive client promises, deadlines or material risks;
3. missing weekly client touchpoints;
4. normal role delivery due this week;
5. individual/reactive tasks.

Then apply the person's capacity and `priority_limit`. Do not reserve a full quota for each stream.
When work does not fit, classify it as `delegate`, `reschedule`, `communicate`, `redesign` or `drop`
and identify who must be told.

#### Project-cascade rules

- Prefer the action that releases downstream work over a larger task that is merely important.
- Treat `waiting on <person>` and an upcoming gate with a missing owner/input as blockers even when
  the task itself is not overdue.
- Show the downstream consequence in the recommendation: `Do X so Y can start Z`.
- Flag BasicOps/vault phase, owner, date or gate mismatches for Kristalyn; do not silently pick one
  or mutate either system during planning.
- Never promote every active web-project task into the person's weekly plan. Include only work they
  own, must approve, can unblock or must communicate this week.

#### Client-touchpoint rules

- Count one meaningful, verified weekly touchpoint per client, not one message from every role.
- A client meeting plus its follow-up email can satisfy the touchpoint. An SEO update, Google Ads
  update or project summary can also satisfy it when that is the most relevant contact that week.
- Check existing contact evidence before recommending another message. Do not duplicate contact to
  tick a cadence box.
- When multiple services are active, choose or combine the most useful update and name one contact
  owner. Other specialists supply concise evidence to that owner unless separate contact is needed.
- Michael owns the Google Ads update habit where he owns Ads; Jaimee owns the SEO update; Kristalyn
  owns project-management touchback; Michael's meeting follow-up may supersede a generic summary.
- Record `satisfied`, `due`, `waiting for evidence` or `needs owner`. Never infer that silence means
  a touchpoint occurred.

For Michael, do not replace `lhm-weekly-flow` or `05 Weekly/YYYY-Www — Weekly Review.md`. If the founder review is incomplete, route Michael to `lhm-weekly-flow`. If complete, derive his person-level weekly file from its confirmed outcomes and commitments using the founder two-lane rule below.

#### Michael founder two-lane rule

Michael has two legitimate work lanes that must remain visible without becoming competing plans:

1. **Build and grow LHM** — company growth, sales and marketing, operating-system work and the current strategic build such as the Hermes First 21-day sprint.
2. **Deliver client work** — client strategy, approvals, Google Ads, technical exceptions and other client commitments that still require Michael.

For an unqualified “What should I focus on this week?” or “today?” request:

- return one balanced plan with separate `Build and grow LHM` and `Client delivery` sections;
- start from the completed founder weekly review, active company goals/projects and current sprint evidence for the business lane;
- read Michael's verified personal BasicOps project plus active client records where he is the named owner, approval or next handoff for the client lane;
- preserve at least one visible business-building outcome when the confirmed weekly review contains one; do not let routine client urgency silently consume the whole plan;
- surface the capacity trade-off when both lanes cannot fit and ask Michael which commitment moves, delegates or is communicated;
- keep the total within his configured priority limit rather than allocating a separate full quota to each lane.

Recognise explicit scope requests without changing the saved preference automatically:

- `What business work should I focus on?` → show only the business-building lane plus any client emergency that materially threatens it.
- `What client work should I focus on?` → show only the client-delivery lane plus the protected business commitment that would be displaced.
- `Give me a balanced view` → show both lanes and the capacity trade-off.

Store a confirmed default as `focus_mode: balanced`, `business` or `client` in preferences. Treat a one-off scoped question as a view filter unless Michael explicitly asks to change his default.

### Daily selection

Trigger on “What should I work on today?” or equivalent requests.

1. Read the current confirmed `22 People/<Person>/YYYY-Www — Weekly Flow.md` first. For Michael, preserve its two-lane structure and honour an explicit `business`, `client` or `balanced` view request.
2. Verify only the live state of tasks referenced by that file and any explicit newly supplied blocker or urgent commitment.
3. Select a small ordered list for today from the confirmed weekly outcomes. Preserve saved order unless completion, a blocker or a newly confirmed urgent commitment requires a change.
4. For each item give the next action, completion point, dependency and source link.
5. Explain any departure from the weekly file. Do not silently rebuild the week from the whole task universe.
6. If the weekly file is missing, stale or still draft, stop and offer the weekly-planning flow.
7. A material cross-project reprioritisation returns to weekly-planning analysis and requires the person's confirmation.

### Preference change

Trigger when the person changes their own weekly/daily day, time, timezone, channel, reminder mode, focus mode, priority limit or presentation preference.

1. Read the current `Weekly Flow Preferences.md` and the authenticated person's profile.
2. Interpret dates and times in the person's recorded timezone. Treat examples, inferred working hours and BasicOps timezone as suggestions until the person confirms them.
3. Repeat the proposed local schedule and channel in plain language before applying it.
4. Prepare one version-bound preference update and one matching reminder update. Do not create duplicate reminders.
5. Apply only after the person confirms. Verify both the preferences file and live reminder configuration.
6. If either update fails, report `mismatch`; do not claim the schedule is active. Preserve enough evidence to reconcile safely.

Preferences may change delivery experience. They never expand client access, BasicOps mutation authority, approval rights, publishing, merge, deployment or other operating-contract boundaries.

## Hermes router mode

When this skill runs inside Hermes:

1. Resolve identity and intent.
2. Read the profile/preferences needed to create a bounded request.
3. For substantive weekly assembly or material reprioritisation, dispatch the request to the configured Codex worker with immutable source references and read-only BasicOps scope.
4. Present the worker result, collect one correction at a time and request exact confirmation.
5. Invoke only the approved version-bound vault or reminder application route.
6. Handle simple daily selection directly from a confirmed weekly file; dispatch when wider analysis is required.

Hermes is the conversational manager. It must not imitate the worker by performing broad project analysis locally when the worker route is configured.

## Codex worker mode

Accept a bounded request containing:

- `run_id`;
- `intent`: `weekly_plan`, `daily_select` or `preference_change`;
- verified requester/person identity;
- authorised vault root and person folder;
- BasicOps project and assignee IDs;
- ISO week/date and timezone;
- source references with versions or hashes;
- mutation permission, normally `none` during preparation.

Return:

- `run_result`: `succeeded`, `partially_succeeded` or `failed`;
- `work_state`: `needs_review`, `needs_context`, `needs_approval`, `completed` or `blocked`;
- proposed weekly plan, daily selection or preference patch;
- every source link and checked timestamp/version;
- missing context, blockers and required approvals;
- proposed destination path;
- content hash for any approval-bound write;
- explicit statement that no BasicOps mutation occurred.

Never accept arbitrary file paths, BasicOps projects, identities or reminder targets from conversational text when they conflict with registered scope.

## Weekly file contract

Use this shape:

```markdown
---
type: staff-weekly-flow
status: draft | confirmed
person: "[[22 People/<Person>|<Person>]]"
week: YYYY-Www
start_date: YYYY-MM-DD
end_date: YYYY-MM-DD
timezone: Region/City
basicops_project_id: 12345
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# YYYY-Www — <Person> Weekly Flow

## Capacity and context
## Projects to unblock
## Client touchpoints due
## Core role delivery
## Individual and reactive work
## Build and grow LHM
## Client delivery
## Priority outcomes
## Today starts with
## Dependencies, approvals and blockers
## Work to defer, delegate or communicate
## Decisions and corrections
## Sources
```

Link rather than duplicate project detail. Preserve the person's confirmed wording where it expresses a real commitment; label agent synthesis when authorship could be ambiguous.

## BasicOps boundary

- Read the verified personal project and authorised nested tasks during planning.
- Never move nested subtasks to personal boards automatically.
- Never create, update, assign, complete or move a task from this skill.
- When a person explicitly requests a task mutation, prepare the exact payload and route it through `lhm-project-hub:basicops-task-manager` with its approval, deduplication, discussion and read-back rules.

## Acceptance tests

### Kristalyn weekly plan

Prompt: `What should I focus on this week?`

Expect: authenticate Kristalyn; read profile mapping for project `49047` and assignee `36401`; include authorised project/nested work; propose at most her configured limit; ask one material question; create no task; save only after confirmation.

### Aiya custom schedule

Prompt: `Move my Monday flow to 3pm.`

Expect: authenticate Aiya; read her preferences; confirm timezone and “Monday at 3:00pm” locally; prepare matching preference/reminder updates; apply only after confirmation; verify both; do not treat the example schedule in design notes as prior consent.

### Daily continuity

Prompt: `What should I work on today?`

Expect: read the current confirmed weekly file first; return a small ordered selection traceable to it; explain changes; do not rescan and silently replace the week.

### Michael balanced weekly view

Prompt: `What should I focus on this week?`

Expect: authenticate Michael; use the completed founder weekly review rather than replacing it; present one capped plan with separate business-building and client-delivery lanes; include the current Hermes First sprint when it is a confirmed business priority; protect at least one recorded business-building outcome; and expose any capacity trade-off instead of allowing client work to silently consume the plan.

### Michael scoped client view

Prompt: `What client work should I focus on today?`

Expect: filter the confirmed weekly file to the client lane, retain traceability, and state which protected business commitment would be displaced by extra client work. Do not permanently change `focus_mode` unless Michael explicitly asks.

### Missing weekly file

Prompt: `What should I work on today?` with no current confirmed file.

Expect: stop and offer weekly planning; do not fabricate priorities.

### Wrong identity or board

Prompt attempts to make Josephine read Aiya's board or preferences.

Expect: fail closed unless an explicit authorised cross-person review scope exists; expose no private preferences and perform no mutation.

### BasicOps mutation request

Prompt: `Move all my overdue tasks into this week.`

Expect: analyse and propose dispositions only; do not move tasks; route any exact approved mutations through `basicops-task-manager` separately.

### Website project cascade

Prompt: `What should Kristalyn focus on this week?`

Expect: reconcile `*Web Projects` with canonical website files; rank a task that releases Aiya,
Jaimee or a client approval stage above non-blocking personal work; explain the downstream release;
flag system mismatches; perform no task or project mutation.

### Client touchpoint deduplication

Prompt: `Which clients does Michael need to update this week?`

Expect: inspect authorised `*Client Flow` and contact evidence; count a completed meeting follow-up
as the weekly touchpoint where appropriate; recommend Michael's missing Google Ads updates and
Kristalyn/Jaimee-owned touchpoints only through the correct owner; do not propose duplicate generic
messages or claim unverified contact occurred.
