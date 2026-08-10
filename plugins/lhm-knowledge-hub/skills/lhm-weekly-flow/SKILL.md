---
name: lhm-weekly-flow
description: Run Local Health Marketing's conversational weekly review and planning interview using its Obsidian vault, WeekFlow context and operating systems. Use when Michael says “start the weekly flow”, “run the weekly review”, “plan the week”, “review last week”, “what needs my attention?”, or asks to prepare, continue, improve or complete an LHM weekly planning session. Begin with a personal check-in, use evidence to help recall the week, review time and unfinished work, then update Obsidian with decisions, three weekly outcomes and commitments.
---

# LHM Weekly Flow

Run an evidence-led weekly operating review for Local Health Marketing. Use the vault for continuity across conversations and save progress after each interview section.

## Locate and load context

1. Find the vault directory containing `.obsidian`. Prefer `/Users/michaelcolman/Documents/Obsidian/Local Health Marketing/Local Health Marketing` when accessible.
2. Read `_System/Vault Conventions.md` and `_System/Multi-Agent Memory Contract.md` completely and follow them.
3. Detect the official Obsidian CLI. When available and Obsidian is running, use it for recent files, backlinks, unresolved links, open tasks and contextual search; otherwise use `rg` and direct Markdown reads without blocking the review.
4. Read these notes completely:
   - `01 Inbox/Inbox.md` and every unprocessed capture in `01 Inbox`
   - `05 Weekly/Weekly Flow.md`
   - `05 Weekly/Attention Queue.md`
   - `10 Goals/Goals.md` and active goal notes
   - `30 Projects/Projects.md` and active project notes
   - `25 Marketing/Marketing.md` and current linked strategy notes
5. Find and read the most recent completed weekly review, if one exists.
6. Find and read every AI conversation-capture note created since the previous weekly review, including legacy `Claude Conversation Capture` notes. Collect lessons marked `Needs Michael`, `Promote to Knowledge`, `Update SOP`, or `Observe again`, plus every unresolved recurrence or contradiction.
7. Search the vault for unresolved checkboxes, explicit blockers, `Still to define`, `Open decisions`, `alignment issue`, and recent material changes. Do not automatically copy ordinary project tasks into the Attention Queue.
8. When accessible, review the previous week's completed and unfinished WeekFlow tasks. Treat WeekFlow as evidence about Michael's time and work, not as the canonical home for business decisions.
9. Use Australia/Melbourne dates and ISO week numbers.

Do not ask Michael for information already available in the vault. Briefly surface relevant existing context and ask only for changes, results or judgments that cannot be discovered.

## Prepare the weekly note

1. Determine the current ISO week and filename: `YYYY-Www — Weekly Review.md`.
2. If the note already exists, read it and resume from the first incomplete section.
3. Otherwise create it in `05 Weekly` using `80 Templates/Weekly Review Template.md`.
4. Set `status: draft`, the correct week, Monday start date, Sunday end date, and current `created` and `updated` dates.
5. Prefill links to active goals and projects. Prefill verified facts only; never invent missing metrics.
6. Do not pre-commit priority outcomes, commitments or commercial decisions before the interview. Existing suggestions must remain visibly provisional until Michael confirms them.

## Open the session

Start as a human conversation before presenting the operating briefing. Ask one natural check-in such as:

> How are you doing coming into the week? How is your energy, and is anything sitting in your head that you want to get out first?

Let the answer influence the tone, depth and ambition of the review. Record relevant capacity context without turning private reflection into an operational fact Michael did not approve.

Then give a compact briefing:

- The current week and date range
- The most relevant unfinished outcomes from the previous week
- Urgent Attention Queue items
- Active project changes already visible in the vault
- New AI-captured lessons, knowledge candidates and operational blockers since the previous review
- Missing scorecard data that may need to be supplied

Before the wins review, route the Monday intake in this order:

1. Review every unprocessed `01 Inbox` capture and decide whether to discard it, merge it into a canonical note, convert it into an action, or flesh it out into a structured Idea.
2. Review structured `seed` ideas that are relevant now; do not force parked or unrelated ideas into the week.
3. Review unresolved lessons, recurrences and contradictions from new AI conversation captures.
4. Surface only urgent Michael-level decisions from the Attention Queue.

When an Inbox thought is worth developing, ask focused questions one at a time. Move it to `40 Ideas` only after it states the problem or opportunity, potential value, evidence or rationale and smallest next test. Aim to leave no unclassified Inbox item older than seven days.

Then run the interview one section at a time. Ask one main question per message; use up to three tightly related prompts only when they are naturally answered together. Do not dump the entire questionnaire on Michael.

## Interview sequence

### 1. Wins

Ask what went well in the previous week. Do not rely on unaided recall. Offer brief evidence-based memory prompts from the vault, campaign data and WeekFlow across:

- Sales, leads and cash
- Client launches, results and positive feedback
- Marketing progress
- Systems, AI tools and the LHM Brain
- Team delegation and completed work

Probe for concrete outcomes and evidence rather than activity alone.

After the answer:

- Reflect the important wins concisely.
- Identify any result that should update a project, goal or marketing note.
- Write the wins into the weekly note before continuing.

### 2. Losses and friction

Ask what failed, stalled, took too long or required too much of Michael. Distinguish symptoms from root causes.

After the answer:

- Record losses and friction.
- Extract lessons or operating changes.
- Add a new Attention Queue item only if Michael's decision, approval or intervention is genuinely required.

### 3. Time and unfinished work

Review the previous week's completed and unfinished WeekFlow tasks when accessible. Use the review to understand where Michael's time went, not to copy a task list into Obsidian.

Workshop only material unfinished work using one disposition:

- `Complete personally`
- `Delegate`
- `Systemise or outsource through a skill`
- `Redesign the approach`
- `Drop deliberately`

Record decisions or operating lessons in the relevant project or weekly note. Keep executable personal tasks in WeekFlow or BasicOps.

### 4. Knowledge and lessons

Before the scorecard, review material lessons captured since the previous weekly review. Skip lessons already applied that require no validation; mention them briefly in the opening context instead.

For each unresolved lesson, ask Michael only when judgment is needed, then assign one disposition:

- `Applied`
- `Promote to Knowledge`
- `Update SOP`
- `Needs Michael`
- `Observe again`

Record the decision under `Knowledge and lessons` in the weekly note. Immediately update the canonical Knowledge, SOP, project or Attention Queue note when the disposition requires it. Do not promote a one-off project fact into `60 Knowledge`.

Explain an unclear lesson in plain language before asking Michael for a disposition. Do not promote a lesson merely because its wording sounds generally useful.

### 5. Founder scorecard

State the exact reporting period before discussing figures. The weekly review note is Monday–Sunday, while the company scorecard may use a different reporting week; never mix periods without labelling them.

Review the founder-level scorecard. State values already known, then ask only for missing measures that help Michael steer the business:

- Scheduled sales calls
- First-paying clients
- Call-to-first-payment conversion
- Marketing spend
- Google Ads spend and scheduled calls
- Organic and other-source scheduled calls
- Cash or pipeline changes that materially affect the week
- Michael's capacity, delegation and systemisation where meaningfully measurable
- Whether the LHM Brain reduced manual coordination or revealed a blocker

Website launches or delivery exceptions may be included when they are material business outcomes. Keep routine client-delivery activity and vague counts such as `proactive client work completed` in the service-delivery operating system, not the founder weekly review.

Do not force meaningless zeros or collect metrics that are not yet measurable. Mark unavailable data as `not tracked` and flag tracking setup only when it merits attention.

### 6. Attention Queue

Review only urgent or genuinely blocking items. Before discussing an item, apply this routing test:

1. Does Michael need to decide, approve, authorise or intervene now? Keep it in the Attention Queue.
2. Is it bounded implementation or definition work? Put it in BasicOps or the relevant project backlog.
3. Is it an idea without a committed outcome and owner? Put it in `40 Ideas` or the parking lot.

For each selected Attention item, ask for a decision, defer it with a reason/date, or identify what information is needed.

When Michael resolves an item:

1. Update its canonical project, strategy or goal note with the decision.
2. Mark the Attention Queue item complete.
3. Add `Resolved: YYYY-MM-DD — <decision>`.
4. Move it to the `Resolved` section during finalisation.

Do not treat every queue item as a priority for the current week.

When Michael asks an agent to create a personal BasicOps task, use the `Michael Tasks` board, `INBOX` section and Michael as assignee unless he explicitly requests different routing. Always return the task link.

### 7. Active projects and opportunities

Summarise the health and next milestone of each material active project. Ask what changed, what is blocked and whether any project should start, stop, continue or change scope.

Capture emerging ideas without letting them silently expand the week. Route each idea to this week's outcomes, a BasicOps task, a project backlog, `40 Ideas`, or the parking lot. Capture new time-bound work as a project only after its outcome and owner are clear.

### 8. Plan the coming week

Ask what would make the coming week successful. Develop possible outcomes from goals, project milestones, attention items and Michael's answer.

Challenge:

- Vague activity phrased as an outcome
- More than three primary priorities
- Commitments without an owner or due date
- Work that does not advance a goal, unblock delivery or protect a live campaign
- Workload that exceeds known capacity

Use Michael's opening energy and capacity check when judging workload. A free week permits deeper work, but still turn broad intentions such as `smash through the Brain` into one or more observable deliverables.

Agree on no more than three primary outcomes. Each outcome must be observable by the end of the week.

### 9. Commitments and final check

Turn each outcome into the minimum necessary commitments with owner and due date. End conversationally by asking what could derail the week, what should deliberately not be worked on, and what Michael is most interested in starting first.

Confirm the final plan with Michael before marking the review complete.

## Save progressively

After each answer:

1. Update the relevant section of the current weekly note.
2. Update the note's `updated` date.
3. Preserve incomplete sections for resumption.
4. Update linked canonical notes when a real decision or status change has occurred.

If the session stops early, leave `status: draft` and tell Michael which section will resume next time.

## Finalise

When Michael confirms the plan:

1. Ensure the weekly note contains wins, losses, lesson dispositions, available scorecard data, reviewed attention items, active project changes, three or fewer outcomes, commitments, decisions and parking-lot items.
2. Move completed attention items to `Resolved`; keep deferred items in `Waiting` with a reason and review date.
3. Add newly discovered Michael-level decisions using the next unused stable `ATT-nnn` identifier.
4. Update canonical goal, marketing and project notes without duplicating detailed task lists.
5. Set the weekly note to `status: complete`.
6. Check internal links and avoid duplicate weekly notes.
7. Finish with a short brief: prior-week result, this week's three outcomes, Michael's decisions, blockers and the first action.

## Guardrails

- Treat the vault as the continuity layer; do not rely on conversation memory alone.
- Preserve Michael-written reflection as his voice. Label new agent interpretations as analysis instead of blending them into first-person reflection.
- Preserve Michael's wording where it captures intent, while turning vague statements into testable outcomes through discussion.
- Do not silently resolve contradictions or make commercial decisions for Michael.
- Do not overload the Attention Queue with ordinary tasks.
- Do not rewrite detailed external trackers into Obsidian. Link to their canonical locations and capture only strategic context, decisions and next milestones.
- Do not mark a weekly review complete until Michael confirms the plan.
