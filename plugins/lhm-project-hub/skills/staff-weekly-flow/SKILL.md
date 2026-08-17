---
name: staff-weekly-flow
description: Plan and run a personalised LHM weekly-to-daily work flow for Michael, Kristalyn, Aiya, Jaimee or Josephine. Use when an authorised person asks “what should I focus on this week?”, “what should I work on today?”, asks to review, clean up or triage all their BasicOps tasks or inbox, asks for a mini stand-up or WhatsApp-ready team update, asks specifically for business-growth or client-work priorities, wants to review or save their weekly priorities, or wants to configure their weekly/daily reminder time, timezone, channel, delivery mode, focus mode or priority limit. Read the person’s canonical Obsidian profile, verified BasicOps personal-board mapping, authorised project context and current weekly file; prepare a small realistic plan; save only after confirmation; and apply approved BasicOps mutations through basicops-task-manager with read-back verification.
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
   - the exact `basicops_sections` names and IDs, plus `basicops_section_mapping_status`.
4. Use only that person's authorised client/project scope. Do not expose another person's private preferences or unrelated client context.
5. Fail closed when the identity, profile, project ID or assignee ID is missing or contradictory.
6. Treat voice transcription and informal aliases as unverified until they resolve to one canonical
   person, client, project or BasicOps record. Ask one concise question when two records remain
   plausible, then preserve the confirmed correction in the weekly decision register.

Use the person's folder `22 People/<Person>/`. Store preferences in `Weekly Flow Preferences.md` and weekly plans in `YYYY-Www — Weekly Flow.md`.

## Choose the intent

### Weekly planning

Trigger on “What should I focus on this week?”, equivalent planning requests or a scheduled weekly reminder.

1. Read `22 People/<Person>/Weekly Flow Preferences.md`. If absent, use `80 Templates/Weekly Flow Preferences Template.md` to prepare a first-run proposal; do not invent or silently save a schedule.
2. Determine the ISO week in the person's confirmed timezone. If timezone is unconfirmed, ask one question before scheduling or dating a saved plan.
3. Complete the weekly intake across all four evidence areas before presenting a final timetable:
   - **fixed commitments** — meetings, appointments, deadlines and required preparation/follow-up;
   - **dependable capacity** — normal working hours, family/personal constraints and hard stops;
   - **project cascade** — approvals, artefacts and handoffs the person must provide to release
     another person or stage;
   - **personal task state** — the verified BasicOps board, including blockers, overdue decisions
     and reactive work.
   Ask one material question at a time. A user may provide these areas conversationally over several
   turns; do not mistake an early partial timetable for the final plan.
4. Read only the minimum relevant context:
   - the person's canonical profile and quarterly commitment, if present;
   - their previous and current weekly files, if present;
   - open work from their verified BasicOps personal project;
   - authorised tasks intentionally nested beneath client, onboarding or website parent tasks;
   - active projects where they are the named owner or next handoff;
   - relevant meetings or dependencies for the week;
   - explicit blockers and overdue tasks.
   - for Michael, Jaimee or Kristalyn, the canonical
     `60 Knowledge/Client Monthly Delivery Rhythm.md`; then read
     [client-monthly-delivery-rhythm.md](references/client-monthly-delivery-rhythm.md) and select
     only the active role stage, meeting follow-ups and missing evidence.
5. Treat BasicOps as live task state and Obsidian as canonical project context. Do not copy the full board into the weekly file.
   Read a valid `LHM metadata` description line when present, including source, handoff and client
   touchpoint fields. Treat older lines without touchpoint fields as valid legacy metadata.
   Treat `urgent=true` as a prompt for an
   explicit urgency and displacement review, not automatic priority one; verify the deadline or
   consequence from discussion or canonical context. Keep unclassified tasks in consideration.
6. Classify unfinished or overdue work as `do`, `delegate`, `reschedule`, `communicate`, `redesign` or `drop`. Never complete, move, assign or edit a BasicOps task while planning.
   For each overdue task, also ask whether its commitment is still valid and whether it should be
   rescheduled, delegated, marked blocked/waiting, communicated or dropped. Never invent a new due
   date or silently carry an overdue date forward.
7. Separate dependable capacity from opportunistic capacity. Optional early-morning work, travel
   downtime or incidental focus windows may advance the plan but must not be required for the
   confirmed outcomes to fit unless the person explicitly commits that time.
8. Propose no more than `priority_limit` weekly outcomes. Default to three only when the preference file explicitly records three; otherwise ask or use three as a visibly provisional LHM suggestion.
9. For each proposed outcome state:
   - observable result;
   - first next action;
   - owner;
   - dependency or approval;
   - source task/project link;
   - completion condition;
   - who needs an update.
10. Surface excluded work and what must be communicated instead of overloading the person.
11. Before asking for confirmation, reconcile every active project mentioned during intake against
    the proposed timetable. Each included project must show its required approval or artefact, the
    downstream person, the handoff action and a realistic work block; otherwise mark it explicitly
    deferred, delegated, waiting or communicated.
12. Ask one material question at a time. Do not save until the person confirms the plan.
13. After confirmation, write or update the current weekly file through the approved vault mutation route and verify the saved content.

#### Workload negotiation

When committed, overdue or newly arrived work cannot fit:

1. Identify the task requester, operational owner and client/account contact owner from verified
   evidence. Do not assume the assignee is authorised to reset a client promise.
2. State the capacity conflict and downstream consequence plainly.
3. Propose a realistic disposition: `ask for help`, `delegate`, `reschedule`, `blocked`, `waiting`,
   `communicate`, `redesign` or `drop`.
4. If rescheduling is proposed, ask for or present one exact new date. Keep the current date visible
   until the authorised person approves the change.
5. Draft an internal pushback request to the requester/account owner containing: the task, why it
   will not fit, proposed timing, client consequence and the exact client expectation that needs to
   be reset. The team member may state their capacity; client contact remains with the authorised
   owner.
6. Keep client messages as drafts unless a separate authorised sending workflow is invoked.
7. Record the decision and who must communicate it in the weekly file. Do not represent a draft as
   sent or a proposed date as agreed.

#### Personal-board section rules

- Read the exact semantic section map from the person's profile. Never infer a section ID from its
  display order or assume boards share names.
- Recommend `inbox` → a confirmed `this_week`/`working_now` section only after weekly commitment;
  recommend `waiting` when an external input or review is pending; recommend `blocked` only where
  the person's verified map contains one. Use a confirmed `future`/backlog section for deliberately
  deferred work.
- Some boards have two valid this-week meanings (for example actions versus projects). Ask which
  applies when task evidence does not make it clear.
- If the profile says a semantic section is absent or the live board contradicts the saved map,
  stop and ask; do not create a section or choose the nearest name.
- A recommendation is not a mutation. Present task, source section, destination section and any due
  date/status change as an exact preview. Apply only through `basicops-task-manager` after approval,
  then read back project, section, assignee, due date and status.

#### Overwhelmed mode

Trigger on “I'm overwhelmed”, “this is too much”, “I can't fit this in” and equivalent language.
This is a temporary view unless the person explicitly changes a preference.

1. Acknowledge briefly and avoid returning the full board.
2. Show at most three things: one essential delivery commitment, one action that releases another
   person or project stage, and one important communication. Use fewer when that is more realistic.
3. Put everything else into `ask for help`, `push back`, `park` or `drop`; expose client promises and
   overdue items that cannot safely disappear.
4. Draft the highest-value help or pushback message and ask one decision at a time.
5. Do not move tasks, change dates, send messages or permanently lower the priority limit without
   the relevant explicit approval.
6. When workload distress needs a human decision on staffing, scope or wellbeing, recommend a
   direct conversation with the person's manager rather than trying to automate the judgment.

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

For Michael, Jaimee and Kristalyn, assemble the recurring role-delivery candidates from
`60 Knowledge/Client Monthly Delivery Rhythm.md`. The matrix replaces generic Week 1–4 reminder
cards as the recurring calendar. Actual saved meetings independently trigger a seven-day Michael
follow-up review. Require dated completion evidence and surface missed monthly passes using
[client-monthly-delivery-rhythm.md](references/client-monthly-delivery-rhythm.md).

Rank the combined candidates in this order:

1. work blocking another person or the next project stage;
   this includes completed/ready work whose required handoff has not been verified;
2. time-sensitive client promises, deadlines or material risks;
3. missing weekly client touchpoints;
4. normal role delivery due this week;
5. individual/reactive tasks.

Then apply the person's capacity and `priority_limit`. Do not reserve a full quota for each stream.
When work does not fit, classify it as `delegate`, `reschedule`, `communicate`, `redesign` or `drop`
and identify who must be told.

When a real delivery commitment is a suitable seed for a reusable Hermes workflow, schedule the
delivery outcome first and capture its evidence, corrections and handoff as workflow-learning input.
Do not create a separate unbounded skill-building project that competes with the delivery it is
supposed to improve.

#### Project-cascade rules

- Prefer the action that releases downstream work over a larger task that is merely important.
- Treat a missing completion, review, blocked or waiting notification as a broken handoff. Name the
  person waiting, the message/action required and what it releases.
- Treat `waiting on <person>` and an upcoming gate with a missing owner/input as blockers even when
  the task itself is not overdue.
- Show the downstream consequence in the recommendation: `Do X so Y can start Z`.
- Flag BasicOps/vault phase, owner, date or gate mismatches for Kristalyn; do not silently pick one
  or mutate either system during planning.
- Never promote every active web-project task into the person's weekly plan. Include only work they
  own, must approve, can unblock or must communicate this week.
- Run a final cascade reconciliation before confirmation: for each project named during intake,
  verify that the timetable shows the artefact or approval, downstream person, handoff action and
  work block, or an explicit disposition explaining why it is not scheduled.

#### Cross-person attention rules

- Surface any item where one person needs a decision, input, approval or artefact from another.
- State `who needs whom`, the exact requirement, who is currently waiting, the downstream work it
  releases and the authorised notification channel.
- A BasicOps comment or weekly-file entry does not prove the other person was notified.
- Reuse verified personal/project attention records when they exist. Treat a new shared attention
  queue as a system-design proposal requiring separate approval; do not silently create another
  queue during weekly planning.

#### Client-touchpoint rules

- Count one meaningful, verified weekly touchpoint per client, not one message from every role.
- A client meeting plus its follow-up email can satisfy the touchpoint. An SEO update, Google Ads
  update or project summary can also satisfy it when that is the most relevant contact that week.
- In meeting-heavy weeks, schedule each client cluster as preparation, meeting, consolidated
  follow-up and downstream handoff. Do not make those four parts compete as unrelated priorities,
  and do not omit the preparation/follow-up load when calculating capacity.
- Check existing contact evidence before recommending another message. Do not duplicate contact to
  tick a cadence box.
- When multiple services are active, choose or combine the most useful update and name one contact
  owner. Other specialists supply concise evidence to that owner unless separate contact is needed.
- Michael owns the Google Ads update habit where he owns Ads; Jaimee owns the SEO update; Kristalyn
  owns project-management touchback; Michael's meeting follow-up may supersede a generic summary.
- Record `satisfied`, `due`, `waiting for evidence` or `needs owner`. Never infer that silence means
  a touchpoint occurred.
- For each active client-contact task, read `last_touchpoint`, `touchpoint_cadence` and
  `next_touchpoint` when present. A touchpoint is due when its explicit next date falls within the
  planning week or is overdue; cadence alone never proves the next date.
- Require sent-email, completed-meeting or canonical contact evidence before marking a touchpoint
  satisfied or advancing `last_touchpoint`. A draft or BasicOps planning comment is insufficient.
- Flag missing or conflicting cadence data as `waiting for evidence` or `needs owner`; never invent
  a rhythm or silently resolve a conflict with the task due date.

#### Client-context batching rules

Reduce avoidable context switching without turning one client action into an uncontrolled backlog
sweep.

1. After a primary client task or meeting block is selected, inspect the person's other authorised
   open work for that same client.
2. Offer a small **Same-client quick wins** batch only for adjacent tasks that:
   - are genuinely due, overdue, blocking progress or release a current handoff;
   - use substantially the same open systems, files, account access or client context;
   - can fit within approximately 15–20 additional minutes in total;
   - do not displace a confirmed priority or extend past a hard stop;
   - have a clear completion point and source task link.
3. Present the execution order as `primary task → same-client quick wins → stop condition`. Keep the
   primary task visible and do not consume a separate weekly priority slot for each tiny adjacent
   action.
4. Prefer two or three small actions over a general instruction to “work through the client.” Stop
   when the time box expires, the shared context closes, a task becomes uncertain, or the next item
   requires a different specialist workflow or approval.
5. Do not pull in the client's full backlog, stale meeting-wrap history, unrelated future work or
   tasks owned by another person merely because the client name matches. Preserve role scope,
   approvals, due-date rules and BasicOps mutation boundaries.

#### Kristalyn client-follow-up batch

For Kristalyn, group due client-contact actions into one scannable **Client follow-ups** work block
without hiding their source tasks.

1. Select tasks whose exact `next_touchpoint` falls in the week or is overdue, plus confirmed
   one-off client chases due this week. Keep unclassified but clearly due contact work visible.
2. Combine multiple asks to the same client into one proposed email where that is operationally
   sensible. List each client, exact ask, source task, channel and downstream work released.
3. Present the batch as one weekly execution block while retaining every underlying BasicOps link.
   It may contain many quick emails without consuming one priority slot per email.
4. Draft or prepare the emails only when requested. Never claim they were sent without a separate
   authorised sending route and approval.
5. After verified sending, propose through `basicops-task-manager`: update `last_touchpoint`, compute
   and store the exact `next_touchpoint` from the confirmed cadence, and move reply-dependent tasks
   to Kristalyn's verified waiting section. Do not mutate during planning.

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
4. For each selected client item, apply the **Client-context batching rules**: verify same-client
   adjacent candidates, offer at most a 15–20 minute quick-win batch, and state the stop condition.
   Do not scan or return the client's full backlog.
5. For each item give the next action, completion point, dependency and source link.
6. Explain any departure from the weekly file. Do not silently rebuild the week from the whole task universe.
7. If the weekly file is missing, stale or still draft, stop and offer the weekly-planning flow.
8. A material cross-project reprioritisation returns to weekly-planning analysis and requires the person's confirmation.
9. After presenting the daily plan, offer the optional mini stand-up. Do not require it to receive a
   daily answer and do not repeat the offer after the person declines in the same interaction.

### Full BasicOps inbox review

Trigger when the authenticated person asks to review, clean up, prioritise or work through all
tasks in their BasicOps inbox or personal board. Also offer this flow when daily planning reveals a
large mixed backlog that is itself causing overwhelm. Do not run it merely because one overdue task
exists.

1. Resolve the person's verified project, assignee and semantic section IDs from their profile.
   Read every open task in the requested inbox or board, following pagination until complete. Exclude
   completed, cancelled and declined tasks from the active count, but retain enough evidence to spot
   duplicates or already-resolved work.
2. Read the valid `LHM metadata` line, task discussion, useful URLs, status, due date, section and
   recent activity. Cross-check canonical client/project context only where needed to judge a live
   risk, dependency, apparent completion, duplication or safe routing. Do not infer urgency from an
   old due date alone.
3. Lead with a compact overview and use these evidence-labelled groups:
   - **Client-risk rescue** — broken live journeys, payment/access failures, live ad or tracking
     risk, explicit client promises, or work blocking another person/project stage;
   - **Stale / likely closure candidates** — old, silent, superseded, duplicated or apparently
     completed work that needs confirmation before closure;
   - **Suggested delegate** — bounded work that fits another confirmed role, with assignee approval
     or a graduated route still required;
   - **Suggested keep** — valid strategic, current or personally owned work that should remain;
   - **Needs a decision** — insufficient or contradictory evidence.
4. For every recommendation include the task link, why it is in that group and a proposed
   disposition: `do`, `close`, `delegate`, `reschedule`, `waiting`, `blocked`, `communicate`,
   `redesign` or `drop`. Say `likely` or `confirm first` when the evidence is not decisive.
5. Work through one group at a time. Prefer this sequence unless the person chooses another:
   client-risk rescue → stale/closure → delegate → keep/reschedule → needs decision. Accept natural
   language or voice feedback and reflect it back as an exact decision register before writing.
6. Translate each confirmed decision into an exact mutation preview containing task, current state,
   proposed status/section/assignee/due date, required discussion message, downstream handoff and
   any separate communication draft. Never invent a date, owner, completion claim or client
   communication. A direction such as “next week” is not an exact due date; ask one concise question.
7. A clear authenticated instruction about the person's own tasks authorises only the exact stated
   mutations. Reassignment to another team member still requires that assignee's approval unless a
   canonical graduated route applies. Closing a task requires the person to confirm it is completed,
   deliberately abandoned, duplicated or superseded; silence and age are not completion evidence.
8. Route every approved task mutation through `basicops-task-manager`. Apply changes in small,
   recoverable batches. Add the approved discussion message when the decision or handoff would
   otherwise be unclear. Read each task back and verify project, section, assignee, due date, status,
   metadata and discussion. Return the BasicOps link and report any mismatch without claiming
   success.
9. After each batch, show `applied`, `unchanged`, `needs approval` and `failed/mismatch`. Continue to
   the next group unless a failed write makes further mutations unsafe. If write tools are
   unavailable, preserve an exact pending mutation register and say plainly that BasicOps remains
   unchanged; do not treat a vault note as completion.
10. Finish with a reduced active count, today's rescue list, deliberately retained backlog,
    delegated/approval-pending work and the next review date if the person supplied one. Update the
    weekly file only when the triage materially changes the confirmed plan; keep detailed task state
    in BasicOps.

Use the presentation pattern `client-risk rescue`, `stale / likely closure`, `suggested delegate`,
`suggested keep` and `needs a decision` consistently, but omit empty groups and keep the first view
scannable. Never dump the full raw task payload into chat.

### Mini Hermes stand-up and WhatsApp draft

Trigger after daily selection or when the person asks for a stand-up, check-in or team update. Keep
it asynchronous and focused on coordinating the next working day, not reporting activity to a
manager.

1. Ask for or derive only confirmed, traceable information under four headings:
   - **Progress since yesterday** — up to three meaningful wins or completions, especially work
     that released another person. Use zero when none is confirmed; never manufacture wins.
   - **Today's commitments** — up to three outcomes from the confirmed daily selection. These are
     outcomes, not a list of every activity.
   - **Blocks and help needed** — up to three blockers. For each name what is blocked, the person or
     input needed, who should respond and whether a client expectation may need resetting.
   - **Team impact** — one short statement naming who is released, waiting or needs an update.
2. Treat “three” as a ceiling, never a quota. In overwhelmed mode prefer one commitment, one
   unblocker and one communication.
3. When a reported win would complete a task or a blocker would change the weekly plan, verify it
   and seek the relevant approval before updating BasicOps or the weekly file.
4. End with: `Would you like me to prepare a WhatsApp-ready team update?`
5. If accepted, prepare a concise copy-ready draft in this structure, omitting empty headings:

```text
Morning team — my focus today:

✅ Progress
• <meaningful completion or handoff>

🎯 Today
• <outcome 1>
• <outcome 2>

🚧 Blocked / need help
• <blocker> — need <person/input> by <confirmed timing>

🔄 Team impact
• <who this unblocks or who needs an update>
```

6. Preserve the person's natural voice and use only information they have confirmed or that is
   traceable to the current weekly/daily plan. Do not expose client-sensitive detail unnecessarily.
7. The output is a draft. Do not post to WhatsApp, send through another channel or claim it was sent
   without a separate explicit approval and an authorised messaging route.

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
- `intent`: `weekly_plan`, `daily_select`, `basicops_inbox_review`, `standup_draft` or `preference_change`;
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
## Client follow-ups
## Core role delivery
## Individual and reactive work
## Build and grow LHM
## Client delivery
## Priority outcomes
## Monthly client-delivery passes
## Today starts with
## Dependencies, approvals and blockers
## Work to defer, delegate or communicate
## Overdue decisions
## Pushbacks and help requests
## Board moves awaiting approval
## Decisions and corrections
## Sources
```

Link rather than duplicate project detail. Preserve the person's confirmed wording where it expresses a real commitment; label agent synthesis when authorship could be ambiguous.

## BasicOps boundary

- Read the verified personal project and authorised nested tasks during planning.
- Never move nested subtasks to personal boards automatically.
- Never create, update, assign, complete or move a task from this skill.
- When a person explicitly requests a task mutation, prepare the exact payload and route it through `lhm-project-hub:basicops-task-manager` with its approval, deduplication, discussion and read-back rules.
- Route metadata creation, correction and urgency removal through the same approval boundary.

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

### Optional stand-up offer

Prompt: `What should I work on today?`

Expect: return the traceable daily selection first, then offer an optional mini stand-up and
WhatsApp-ready draft; do not force the check-in, create filler or send a message.

### Mini stand-up

Prompt: `Run my mini stand-up: I finished the Alpha brief, today I am reviewing Ads and the DES
handoff, and I am waiting on Kristalyn for approval.`

Expect: preserve the confirmed win; select no more than three daily outcomes; state what approval is
needed and the team impact; ask whether to prepare the WhatsApp draft; do not complete the Alpha
task or mark the DES work blocked without separate verification and approval.

### WhatsApp-ready update

Prompt: `Yes, make the WhatsApp post.`

Expect: return a concise copy-ready draft with only non-empty Progress, Today, Blocked/help and Team
impact headings; protect client-sensitive detail; label it as a draft; do not send it.

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

### Overdue reschedule

Prompt: `These overdue tasks won't fit. Move them out a week.`

Expect: show each current due date and exact proposed new date; identify any client promise and who
must reset it; request approval for a bounded set rather than moving everything; route approved
changes through `basicops-task-manager`; verify the resulting dates and sections.

### Aiya pushback

Prompt: `Jaimee's new website task won't fit this week.`

Expect: identify Jaimee as requester only when evidence supports it; draft an internal message with
the proposed timing and client consequence; keep client contact with the authorised owner; do not
change the date, section or send either message automatically.

### Personal section mapping

Prompt: `Move my confirmed work out of Inbox and into this week.`

Expect: use the authenticated person's exact saved section IDs; distinguish Aiya's actions versus
projects when required; fail closed for Michael's missing general this-week section; preview and
approve exact moves separately; read back the result.

### Overwhelmed mode

Prompt: `I'm feeling overwhelmed.`

Expect: avoid a full-board dump; show no more than one essential commitment, one unblocker and one
communication; classify the rest as help, pushback, park or drop; draft the most useful request;
perform no task, date or message mutation.

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
