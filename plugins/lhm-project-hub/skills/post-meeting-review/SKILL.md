---
name: post-meeting-review
description: "Process a client meeting's follow-up after client-meeting-email: update client state files, detect stale artefacts, create a compact Client Flow action register, route linked BasicOps tasks to owners' Inbox sections, and draft the team update. Reads saved meeting notes and wrap email, with Fathom/manual fallback. Explicit meeting owners win; otherwise current Obsidian staff profiles resolve a clear role match, with questions only for genuine ambiguity. Client-owed items route to Kristalyn. Use when the user says meeting wrap, process the meeting follow-up, work through the actions, post-meeting review, meeting follow-ups, or client call debrief. All BasicOps writes route through basicops-task-manager."
---

# Post-Meeting Review

Route every BasicOps creation or mutation through `lhm-project-hub:basicops-task-manager`. This skill prepares the meeting-action payload; the shared skill owns wording, approval, deduplication, mutation and verification.

Work through a client meeting's follow-up and keep all client state current:
files, BasicOps, and the team. Run this after `lhm-project-hub:client-meeting-email`
has captured the meeting.

## Step 1: Get the meeting record

**Option A. Saved meeting record (preferred)**
Look for `[client-folder]/project-management/meetings/YYYY-MM-DD-meeting-notes.md`
and the matching `-client-wrap-email.md`, saved by `lhm-project-hub:client-meeting-email`
when it ran right after the meeting. This is the primary path — no Fathom call
needed, since `client-meeting-email` already extracted everything, including the
recording URL in the notes header.

**Find the record yourself — don't make the user point at it.** If the user
just said "meeting wrap" without naming a client or meeting, sweep the
workspace's client folders for `project-management/meetings/*-meeting-notes.md`
files from the last 14 days whose header says `Triaged: no` (or has no
`Triaged:` line — older captures predate the marker). Present what you found,
newest first ("Found an untriaged meeting for Raise the Bar captured yesterday —
work through that one?"), and confirm before proceeding. Only ask the user to
identify the meeting when the sweep finds nothing or several equally-recent
candidates.

**Never ask for a Fathom link, transcript, or client re-introduction when a
saved record exists** — every fact this skill needs is in the meeting-notes
file and its matching wrap email. Asking again for what the capture step
already saved is the exact failure this split exists to prevent.

**Option B. Fathom MCP (fallback)**
If no saved meeting-notes file exists for this meeting — meaning
`client-meeting-email` hasn't run yet for it, not that today's meeting is
unusual — use the Fathom MCP tool to retrieve the transcript. Search by client
name or domain; `list_meetings` with `created_after` set to the last few days is
enough to find "the meeting I had today." Then extract the same fields Step 2.5
of `client-meeting-email` extracts: decisions made, action items (LHM vs.
client), client updates, strategic signals, compliance signals, and skill
triggers. Watch for compliance signals in anecdotes and asides, not just stated
decisions — they seldom arrive announced as decisions, and they're often the
most valuable thing in the meeting. Save the result to `meeting-notes.md`, using the exact template in
`client-meeting-email`'s Step 4, so the rest of this skill proceeds the same
way regardless of which option supplied it.

**Option C. Manual (fallback of the fallback)**
If Fathom MCP is not available or cannot find the meeting:
"Please paste the meeting transcript or notes and I'll work from that." Extract
the same fields as Option B and save `meeting-notes.md` the same way.

## Step 2: Update client state files

Everything below reads from the meeting record established in Step 1 (the saved
`meeting-notes.md`, or the equivalent extraction Step 1's Option B/C just
produced) rather than a live transcript.

### Update `goals.md`

Resolve this as the canonical goals record inside the Obsidian client root. **If it doesn't exist, do not create a blank template in this workflow.** Record the precise missing record, preserve goals explicitly evidenced by the meeting, and route creation through the owning client-onboarding/client-update workflow before a write. Continue the remaining review without inventing targets.

If any KPIs, budgets, or targets changed and the canonical file exists: update the relevant sections. Do not add placeholders for anything the meeting did not cover. Add a dated note:
```
<!-- Updated YYYY-MM-DD from meeting: [one-line summary of what changed] -->
```

### Update `current-projects.md`

Resolve this as the canonical active-project record inside the Obsidian client root. **If it doesn't exist, do not create a blank template in this workflow.** Preserve projects explicitly evidenced by the meeting and route creation through the owning kickoff/project-manager workflow. Continue the remaining review and report the gap.

When the canonical file exists, update it with real projects from this meeting. Do not add placeholder rows.

- Mark completed projects as completed (with date)
- Add new projects from action items
- Update status of existing projects if discussed
- Add new items to backlog if raised but not yet started

### Update `client_profile.md`
If any client details changed (name, services, contacts, business details): update the profile.

Do not trigger `client-update` from here. Propagation beyond the state files is handled in Step 3, which gathers the context `client-update` needs before invoking it.

### Resolve the client acronym

Runs every time, regardless of whether anything else in the profile changed — every BasicOps task title from Step 5 onward needs this.

Check `client_profile.md` for an `Acronym:` field.

- **Present:** use it as-is. No questions asked.
- **Missing:** derive one from the client's display name (first letter of each significant word, uppercase — "Your Story Physio" → `YSP`, "Australian Sports Physio" → `ASP`). Confirm with the user before proceeding (e.g. "Use YSP as the BasicOps short-code for Your Story Physio?"), since a bad auto-derivation is annoying to unwind once it's on ten task titles. Once confirmed, or the user gives a different value, write `Acronym: <value>` to `client_profile.md` so every future run just reads it.
- **`client_profile.md` doesn't exist yet:** derive an acronym for this run only, tell the user it wasn't saved because the profile doesn't exist, and don't block the rest of the skill on it.

## Step 3: Propagation sweep

**Do not skip this.** Updating the state files is not the same as propagating a decision. A service discontinued in a meeting will be sitting in sitemaps, keyword maps, redirect maps, briefs, GBP plans, and landing page copy, none of which Step 2 touches.

This step **detects**. It does not edit. `client-update` owns the editing.

**1. Grep the whole client folder** for every entity the meeting changed, discontinued, renamed, or added.

**2. Sort the hits into forward-looking artefacts and historical records,** using the pile definitions in `client-update`'s Step 2b. That table is the single source of truth for the split; do not restate it here. Forward-looking artefacts need updating. Historical records stay untouched, because editing them rewrites history and destroys the audit trail.

**3. Check for reversed decisions.** Search the forward-looking pile for anything marked *confirmed*, *signed off*, *decided*, or *approved* that the new decision invalidates. This is the failure mode that matters most, because a meeting can overturn work someone signed off days earlier without anyone noticing. When you find one, capture the original reasoning and who made the call, and carry both into the handoff. Do not resolve it yourself.

**4. For regulated services, check live advertising surfaces too**, not just the website. Google Business Profile categories, service lists, business descriptions and directory entries are all advertising. A compliance breach there is live exposure independent of any rebuild in progress.

**5. Hand off to `client-update`.** Invoke the skill and pass it four things: the change (and whether it is a substitution or a removal), the sorted file list, the conflicts found in item 3, and anything flagged in item 4. `client-update` picks up at its **Step 2e**, presents the whole picture to the user for confirmation, and only then edits. Nothing in the client folder changes until the user has signed off inside `client-update`.

**6. Come back and finish.** The handoff is a detour, not an exit. When `client-update` completes, return here and continue at Step 4. Steps 4 through 7 have not run yet. Hold `client-update`'s downstream implications from its own Step 4 and fold them into Step 5's task list below, alongside the meeting record's skill triggers, so the user gets one set of routed follow-on work rather than two nearly identical prompts.

**If nothing came back from the grep,** say so in a line and move on. No sweep findings is a normal outcome for a meeting that changed no entities.

## Step 4: Find the client card

Board: `*Client Flow` (project ID `68655`). Sections: `Follow Up` (ID `107750`), `Meeting Week` (ID `107749`).

`client-meeting-email` already found or created the client card, moved it to Follow Up, and posted the meeting-summary discussion note during capture. This step locates that card and treats it as the mother task — Step 5 creates the linked standalone action tasks and writes their register back to the card. **Meeting-wrap trackers stay in Client Flow. Never create or move a meeting-wrap tracker onto Michael's personal task board.** Client Flow is the portfolio view for seeing each client's follow-up progress.

Call `list_tasks_in_project` with `projectId: 68655` and `filter_title` set to the client's short/common name (e.g. "mhealth", not a long legal entity name). If nothing matches, call `list_tasks_in_project` again without `filter_title` and scan titles for a case-insensitive match.

- **No match:** this means `client-meeting-email` was skipped for this meeting, not just that Step 1's fallback transcript path is being used. Tell the user "No client card found in *Client Flow for [Client]. Want me to create one as the meeting-wrap tracker, or should the follow-ups go in unlinked?" Creating the card is usually right, because it keeps the action register together. If they decline, run Step 5 in **no-card mode** and route every task directly to its owner's board.
- **One match:** that's the card.
- **Multiple matches:** list them (title + URL from `link_to_task`) and ask the user which one is the client's card.

If BasicOps MCP isn't authorized, skip this step and Step 5's BasicOps writes entirely and tell the user: "BasicOps isn't connected. I've saved everything to the client files, but you'll need to add these to BasicOps manually."

## Step 5: One task at a time — create, assign, and act

Build one combined list before starting the loop: every action item from the meeting record (LHM-owned and client-owed), plus every follow-on task identified below (5a), plus anything Step 3 handed back from a `client-update` detour. Work through the combined list one task at a time, in whatever order it was identified — there's no separate pass for action items versus follow-on work.

Before creating anything, run a **compactness gate** over the combined list:

- Create a task only when there is a concrete next action, an owner, and a recognisable finish line. Keep observations, risks, parked ideas, and background in the saved meeting record; they are not tasks by themselves.
- Merge items that are steps of the same deliverable. Put the steps into that task's short `Detail` bullets instead of creating one task per step.
- Merge client inputs that one person will chase in the same conversation into one clearly named client-follow-up task, unless different due dates or owners make them genuinely independent.
- Prefer 3–8 meaningful tasks. More than 10 is a warning that the meeting has been decomposed too finely; pause and consolidate before writing to BasicOps. Do not enforce an artificial maximum when the meeting truly produced more than 10 independent commitments.
- Use plain-language titles that state the outcome. Avoid encoding meeting commentary, status, or a mini-brief in the title.

### BasicOps field rules (read before writing anything)

- **The client card is the meeting-wrap tracker (the "mother task").** Post its compact action register as a discussion message made from live BasicOps task record-links. Keep Description blank except for useful working URLs. Do not paste the meeting transcript, strategic analysis, or a second email into either field.
- **Action tasks are standalone linked tasks, not BasicOps subtasks.** The two reference meeting wraps (`2060773` and `2117845`) return no subtasks from `list_subtasks_in_task`; their task relationships are live BasicOps record-links. Create action tasks without `parentTaskId`, assign them, and move them to the owner's project/board when the owner is confirmed. Link them back to the mother task in the first discussion message. This lets the work live on the assignee's board without disappearing from the meeting wrap.
- **Put every action task's human brief in Discussions—always.** The first discussion message contains the `Mother task` record-link, then `Detail` with 1–4 terse bullets. Add `Done when` only when the finish line is not obvious. Keep Description blank except for useful working URLs.
- **Keep later discussions for change over time:** research results, plan/resume prompts, judgment calls, blockers, or a short completion/update note. A newly created task gets one concise briefing discussion, not a wall of commentary.
- **Use BasicOps record-links, not ordinary URL links, for task-to-task relationships.** Record-links carry the task state in BasicOps, so completed work is crossed off in the mother task and the relationship survives moving the task between boards. Use task table id `3936` and the created task id. Do not copy the SVG/checkbox markup from an old task; BasicOps owns the status rendering.
- **Discussion messages take raw HTML.** Do not escape it to entities, because `&lt;p&gt;` renders as literal text. If you get it wrong, `delete_message` with the returned id and repost.
- **Task titles take a plain `&`,** not `&amp;`, which renders as the literal entity.

### Formatting discussion messages

Structure every labeled message as short, scannable HTML — dot points, not paragraphs, and no more fields than the task needs. Each labeled field gets its own `<p><strong>Label:</strong></p>` followed by a `<ul>` of terse bullets, even when there's only one point to make:

```html
<p><strong>Label:</strong></p>
<ul>
<li>item</li>
<li>item</li>
</ul>
```

**Research-dispatch and plan-summary messages carry exactly two labeled fields: Why it matters and What done looks like.** Nothing else goes in this message. Fold whatever background is essential into the Why it matters bullets rather than adding a third field, and keep the bullets short — this is a briefing, not a transcript.

**Judgment calls get their own message, not a third field.** When there's a decision the assignee should surface rather than make alone, post it as a separate discussion message straight after the briefing — a plain bullet list under `<p><strong>Judgment calls:</strong></p>`, nothing else. Skip the message entirely when there's nothing to flag; don't manufacture one to fill the slot.

This applies to every structured message this skill posts: Step 5's research results, plan summaries, judgment-call flags, and Briefly Prep output. There's no separate meeting-briefing or session-trace message in this skill anymore — `client-meeting-email` already posted the one meeting-summary note during capture. Keep any new post-meeting material focused on the work, not a retelling of the meeting.

### 5a. Identify follow-on tasks

For everything in the meeting record's "Skill triggers" list, plus any downstream implications Step 3 handed back, turn the trigger into a specific, actionable task, not a category. "SEO review" becomes "investigate why /services/knee-pain isn't ranking, per the client's comment about losing traffic." Carry the meeting context (the actual quote or decision) forward — 5d needs it for the dispatch briefing.

### 5a.5. Cross-check follow-on tasks against the meeting's action items

Before adding a follow-on task to the combined list, check whether it describes the same underlying work as one of the meeting record's own action items. Action items and skill triggers come from two separate extraction buckets, and the same meeting decision can land in both — "we need a new blog post about the new service" is naturally both an action item and a content trigger. Skipping this check produces two tasks for the same piece of work.

If a match is found, don't list it twice — treat it as one entry in the combined list, tagged with whatever Type 5b assigns it. If no match, it's a new entry in its own right.

### 5b. Classify

Two questions decide how a task gets handled:

1. **Does it need a specialist agent's judgment, or can Claude do it directly with tools already connected in this session** (Analytics MCP, GSC MCP, etc.)?
2. **Does the task's output mutate a live client-facing system** (a live WordPress page, a live Ads campaign, a live GBP listing), **or does it only produce an artifact** (a document, a CSV, a draft, an answer)?

| | Artifact / answer only | Mutates a live system |
|---|---|---|
| **No agent needed** | **Direct** — answer it now, in this session | (does not occur — live mutations always need a specialist agent) |
| **Needs a specialist agent** | **Auto-run** — offer to dispatch a specialist agent and wait for the result | **Handoff-prompt** — offer to prepare a plan and a prompt; a human executes elsewhere |

Tiering is **per task, not per agent** — the same agent can produce both an Auto-run task and a Handoff-prompt task depending on what's being asked. `google-ads` is the clearest example: keyword research and ad copy drafting for a new ad group is Auto-run (the output is a CSV, nothing in the account changes); submitting that ad group or changing a budget is Handoff-prompt.

**Routing table:**

| Trigger type | Agent | Typical tier | Title type |
|---|---|---|---|
| GA/GSC stat questions, quick performance checks | *(none — Claude direct)* | Direct | `Analytics` |
| Keyword research, ad copy drafting for a new ad group/service/location | `lhm-marketing-hub:google-ads` | Auto-run | `GAds` |
| Live Ads account changes (submit campaign, adjust budget, pause/activate) | `lhm-marketing-hub:google-ads` | Handoff-prompt | `GAds` |
| Keyword research, ranking/content strategy analysis | `lhm-marketing-hub:seo` | Auto-run | `SEO` |
| Blog post, page copy draft, content brief | `lhm-marketing-hub:content` | Auto-run | `Blog Article` / `Landing Page` / `Content Brief` / `Page Copy` — whichever fits the specific task |
| Client briefing committed on upcoming content ("we'll do a briefly"), usually a blog post | `lhm-marketing-hub:seo` (keyword research only, when it's a blog post) | Auto-run | `Briefly Prep` |
| Live page edits on the client site | `lhm-wordpress-hub:site-extension` | Handoff-prompt | `Page Edit` |

**Briefly prep.** When the meeting commits to briefing the client on upcoming content rather than committing to the content itself, the task isn't to draft anything — it's to prepare what the human needs walking into that briefing. If a blog post is involved, run keyword research first (what's worth ranking for) and let it ground the topic; if it's some other content type, skip straight to the topic. The deliverable is exactly two things, nothing more:

1. **The proposed article topic** (informed by the keyword research when there was one).
2. **Three questions to ask the client in the briefly** — the input only the client can supply that keyword data can't (their angle, patient stories or case specifics, service nuance, whatever this topic actually needs from them).

Do not dispatch the `content` agent for this trigger. Writing the actual brief or draft happens after the client conversation, using what it surfaces, not before it. Post the topic and three questions to the task discussion in 5f exactly as produced (formatted per the discussion-message rule: the topic as its own paragraph, the three questions as a `<ul>`); this is the complete output, not a draft of one.

**No match.** If a task doesn't cleanly fit the table or Direct, fall back to a plain-text recommendation line in the email (Step 6). No BasicOps task, no dispatch. Do not force a task into a tier it doesn't belong in.

### 5c. Create the linked action task

For each entry in the combined list that doesn't already have a BasicOps task (action items almost never do yet; a 5a.5 match already does):

Create the task **without `parentTaskId`**. Initially use `projectId: 68655` and `section: 107750` only while the owner is unresolved. Once 5d confirms the owner, move the task to that person's task project/board and specifically its **Inbox** section. Every staff task board has an Inbox; resolve its actual section ID via BasicOps rather than assuming one board's ID applies to another. Use title `"<Acronym> - Action - <task>"` for an LHM-owned action item, `"<Acronym> - Client - <task>"` for a client-owed action item, or `"<Acronym> - <Type> - <task>"` (`<Type>` from 5b) for a follow-on task. `<Acronym>` per Step 2's acronym resolution.

After creation, post this compact first discussion message (raw HTML):

```html
<p><strong>Mother task:</strong> [BasicOps record-link to the client card]</p>
<p><strong>Detail:</strong></p>
<ul>
<li>Essential context or instruction</li>
<li>Second point only if needed</li>
</ul>
<p><em>Questions? Ask Hermes first — it can check the linked meeting wrap, Fathom notes, and client/LHM knowledge. If the answer is not recorded, flag whether Michael or the client needs to answer.</em></p>
```

If the finish line needs clarification, add one short `<p><strong>Done when:</strong> ...</p>`. Never add meeting-summary prose, routing rationale, or duplicated background. The BasicOps Description remains blank unless it contains only useful working URLs.

After every action task has been created, post one numbered action-register discussion message on the client card. Each item contains the live BasicOps record-link, up to 1–3 concise detail bullets, and the confirmed owner. Do not duplicate the entire action-task discussion. Target roughly 4–8 lines per action, and omit empty labels. This one register replaces both a forest of subtasks and a long task dump.

```html
<p><strong>Recording:</strong> [link]</p>
<p><strong>Task 1:</strong> [BasicOps record-link]</p>
<ul><li>Why/what, in one terse point</li></ul>
<p>Assigned to: <strong>Name</strong></p>
```

If the client card already has an action-register discussion for this meeting, update that message rather than posting a duplicate. Preserve unrelated user-authored content. Do not move existing contextual prose into Description.

### 5c.5. Hermes context and knowledge-gap loop

Keep each action task concise because Hermes is the context layer, not because context is disposable. The `Mother task` record-link is the route back to the meeting wrap; Hermes should use it to locate the client and meeting before answering a staff question.

When staff ask Hermes about an action task, Hermes should check, in order:

1. The action task and linked Client Flow mother task.
2. The saved meeting notes and Fathom recording/transcript for the meeting.
3. The client's current profile, goals, projects, and other client knowledge.
4. LHM knowledge, SOPs, skills, and relevant historical decisions.

If those sources answer the question, Hermes gives the answer with a short source pointer and does not create more BasicOps noise.

If they do not, Hermes must classify the missing answer before escalating:

- **Michael decision / LHM knowledge gap:** strategy, LHM process, scope interpretation, prioritisation, or a decision only Michael can make. Post one concise question on the action task for Michael, explicitly label it `LHM knowledge gap`, and say which LHM knowledge file or workflow should be updated once answered.
- **Client fact / client knowledge gap:** facts, preferences, approvals, access, clinical/service nuance, or business information only the client can supply. Post one concise question on the action task, assign the follow-up to Kristalyn when a separate chase is needed, explicitly label it `Client knowledge gap`, and say which client knowledge file should be updated once answered.

Do not guess, silently block the task, or ask both Michael and the client the same vague question. Capture the eventual answer in the identified knowledge source so Hermes can answer it next time, then add a short resolution note to the action task.

### 5d. Resolve the owner and route to their Inbox

For every task on the combined list, in turn:

Resolve ownership in this order:

1. **Explicit meeting owner wins.** If the saved meeting record or verified transcript clearly assigns the action to a current LHM staff member, assign it automatically—no confirmation question. This includes Michael: an action explicitly owned by Michael is assigned to Michael and moved to the **INBOX** section of Michael Tasks. Do not reinterpret a clear meeting commitment merely because another person's profile also fits the work.
2. **Client-owed items route to Kristalyn.** Apply the standing rule below without asking.
3. **Sweep the canonical staff profiles for unowned LHM actions.** Read every current person profile directly under the Brain's `22 People/` folder (for example `Michael Colman.md`, `Kristalyn.md`, `Aiya.md`, `Jaimee.md`, and `Josephine.md`). Use `status: current`, `Outcomes owned`, `Current responsibilities`, `Decision authority`, `Inputs, outputs and handoffs`, and `Capacity and continuity`. Also cross-check `60 Knowledge/Team Roster.md` and this skill's `references/team-roster.md`.
   - Do not use files in `22 People/Job Descriptions/` as routing authority; they preserve source interviews and may contain proposals.
   - Do not treat a `Proposed`, `Desired transition`, `Still to confirm`, or unapproved quarterly commitment as current authority.
   - Match the outcome and required judgment, not just a keyword in the task title.
   - Respect explicit exclusions and escalation boundaries. Routine difficulty alone is not a reason to send work to Michael.
4. **One strong profile match:** assign that person automatically and record a terse internal routing basis, e.g. `Owner basis: Jaimee — routine technical SEO is in her current responsibilities.` Do not add this rationale to the BasicOps task unless it would help the assignee understand a non-obvious handoff.
5. **Ambiguous, conflicting, or unsupported match:** ask one scoped ownership question with the best-supported recommendation as the default. Explain the conflict in one sentence. Do not batch multiple ambiguous tasks into one question.

After resolving the owner, resolve their BasicOps task project and Inbox section, then `update_task` with `taskId`, `assignee`, `projectId`, and `section` set to those exact values. Assigned meeting actions always enter **Inbox**, including client-follow-up tasks routed to Kristalyn; the owner can triage them onward. The live record-link on the Client Flow card remains valid after this move. (`@mentions` inside task messages aren't confirmed to trigger real BasicOps notifications, so the `assignee` field is the reliable mechanism.)

**User overrides carry instruction beyond a name more often than not.** Real examples: "fold this into the landing page build", "X should be notified even though it isn't theirs", "they already have access, go through my account", "this one's urgent, the rest can wait". The `assignee` field loses all of that—post it as a follow-up discussion message on the task.

**Direct tier:** skip the owner question — there's no one to assign, Claude answers now. Run the check immediately and hold the answer for 5f. If the tool this needs isn't connected, note "needs manual check" for Step 6's email instead of blocking the rest of this step.

**Client-owed items** (the `<Acronym> - Client - <task>` tasks from 5c): skip the owner question entirely. `update_task` with `assignee` set to Kristalyn (`kristalyn@localhealthmarketing.com.au`; if the `assignee` field needs a BasicOps user id rather than an email, resolve it via `list_users` first) and move it to the **Inbox** section of Kristalyn's task board. Chasing clients for outstanding items is always Kristalyn's, every meeting — that was never a real choice, so it doesn't get a question.

**No-card mode.** If Step 4 found no card and the user declined to create one, create and route standalone tasks as above, but omit the `Mother task` link and action-register update.

### 5e. Offer research or a handoff plan, in the same turn as the assignment question

Immediately after 5d's assignment question for an **Auto-run** task, ask whether to run the research now: e.g. "This needs keyword research before Aiya can start — want me to run that now?"

- **Yes:** dispatch the specialist agent via the Agent tool with `run_in_background: false` (the Agent tool backgrounds by default, so this must be passed explicitly, not just omitted). Wait for it to return before moving to the next task — do not move on with it still running, and do not dispatch several tasks' research in parallel and come back for the answers later. One task's full cycle (assign, ask, research, post the result) completes before the next task starts.
- **No:** leave the task assigned with no research attached. Nothing dispatches silently, ever.

For a **Handoff-prompt** task, ask instead whether to prepare the plan now: e.g. "This changes a live Ads budget — want me to put together a plan and a resume prompt for whoever runs it?"

- **Yes:** write the plan file to `[client-folder]/project-management/meetings/YYYY-MM-DD/<slug>-plan.md`:

  ```markdown
  # Plan — <task title>
  **Client:** <name>  **Date:** YYYY-MM-DD  **Agent:** <e.g. lhm-marketing-hub:google-ads>

  ## Why
  [The meeting context/quote that triggered this]

  ## Background
  [What the agent needs to know: current state, relevant history]

  ## What done looks like
  [Concrete success criteria]

  ## Judgment calls to flag, not decide alone
  [Anything the human running this should surface rather than assume]
  ```

  Keep every section to short bullet points, not prose — this file gets inlined into the Resume prompt verbatim, so wordiness here becomes wordiness in what the human pastes into a fresh session. Then build the Resume prompt: plain text, ready to paste into a fresh Claude Code or ChatGPT session, coaching-framed so the human keeps their own hands on anything touching a live client system, with the plan file's contents inlined in full, not just linked (ChatGPT can't read the local filesystem, and the prompt needs to work identically on either platform):

  ```
  I now need to [concrete next action] for [Client].

  Here's what's already done: [one-line summary of the plan already produced].

  [Plan file contents inlined]

  Coach me through doing this myself, step by step — don't do it for me.
  ```

- **No:** leave the task assigned with no plan attached.

**No match** tasks from 5b skip 5d and this step entirely — they get a plain-text recommendation line in Step 6's email instead, no BasicOps task.

### 5f. Post the result

Whatever 5e produced, post it to the action task's discussion as soon as it's ready — before moving to the next task:

- **Direct:** post the answer to the action task discussion. Nothing further to track.
- **Auto-run, research run:** the compact brief is already the task's first discussion, so post the agent's actual output as the next discussion message. If the agent failed instead of completing, put what was attempted and what broke into the result message. Attach any generated files (keyword CSVs, ad copy CSVs, content drafts) via `add_file_to_task`, save a copy to `[client-folder]/project-management/meetings/YYYY-MM-DD/`, and add a one-line result pointer beside that task in the client card's action register.

  Also judge whether the completed output implies a concrete, specific next live-system step: keyword research and ad copy drafting naturally continues into "push these live"; a pure research or competitive-analysis task usually doesn't have one. If it does, post one more discussion message with a Resume prompt in the same coaching-framed shape 5e uses for Handoff-prompt tasks, referencing the actual deliverable that just landed:

  ```
  I now need to [concrete next action] for [Client].

  Here's what's already done: [one-line summary of the artifact that just landed, e.g. "keyword research and RSA copy are ready in the attached CSV"].

  [Reference to the attached file, or its contents inlined if the target platform can't read the local filesystem]

  Coach me through doing this myself, step by step — don't do it for me.
  ```

  Skip this entirely when there's no clear next step rather than inventing one.

- **Auto-run, research declined:** nothing further to post — the task is assigned, that's it.
- **Handoff-prompt, plan prepared:** post up to three discussion messages. First, the plan summary — **Why it matters** and **What done looks like** only, each a short bullet list, plus the local path to the plan file. Second, if the plan flags a judgment call, a **Judgment calls** message — a plain bullet list under `<p><strong>Judgment calls:</strong></p>`, nothing else; skip it if there isn't one. Third, the Resume prompt built in 5e, wrapped in a `<pre>` block so the raw-HTML field preserves line breaks and spacing, with the plan's angle-bracket placeholders HTML-escaped first so they don't get swallowed as unrecognized tags. Keeping the prompt its own message means it can be selected and copied without scrolling past the rest.
- **Handoff-prompt, plan declined:** nothing further to post.

**Briefly prep** (from 5b): post the topic and three questions exactly as produced — the topic as its own paragraph, the three questions as a `<ul>`. This is the complete output, not a draft of one.

If BasicOps isn't connected, skip 5c–5f's BasicOps writes and tell the user which tasks would have been routed and need manual tracking — the underlying work (Direct answers, dispatched research, plan files) still happens, only the BasicOps sync is skipped.

## Step 6: Draft the team email

Default to the Gmail `create_draft` tool. It only creates drafts (no send capability), so this always stops for a human to review and send, and replies thread back to the sender's own address.

If the user asks for a different channel (Mailgun via Zapier, for example), warn them what changes before doing it: the From address must sit on the connected Mailgun domain, so the mail will not come from their own address and will not appear in their Sent folder. Mailgun also sends on the spot rather than drafting. Fall back to Gmail without argument if it fails.

1. Build the draft in chat first and ask: "Here's the team email. Does this capture everything?"
   - **To:** kristalyn@localhealthmarketing.com.au, plus anyone assigned a task in Step 5
   - **Cc:** michael@localhealthmarketing.com.au
   - **Subject:** `Meeting wrap — <Client Name> — <Date>`
   - **Body.** Internal audience, so LHM shorthand and jargon are fine here, unlike `client-update-email`:
     - One line: "Michael met with <Client> on <date>."
     - A short synthesis of what was discussed, including context and wins, rather than a task dump.
     - The list of tasks created in Step 5, each with its task link (from `link_to_task`). Direct tasks and Auto-run tasks with research run get an inline summary of the actual outcome (e.g. "Organic traffic is up 12% MoM — details in the task"; "Keyword research and ad copy for the new Riverside location — ready in the task"); Handoff-prompt tasks with a plan prepared are noted as ready for hand-off (e.g. "Ads investigation — plan ready, prompt waiting in the task"); anything left assigned with no research or plan attached is just noted as assigned.
     - Anything the team should watch for.
   - Apply the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.
2. On approval, call `create_draft` with the confirmed `to`, `cc`, `subject`, and `body`.
3. Tell the user the draft is ready in Gmail for review and sending.

If Gmail MCP isn't authorized, skip this step and tell the user the team email needs to be sent manually.

**Mark the meeting triaged.** Update the meeting-notes file's header line from
`**Triaged:** no` to `**Triaged:** YYYY-MM-DD` (add the line if the file
predates the marker). This is how the next bare "meeting wrap" run and the
pm-orchestrator's cadence check know this meeting is done.

## Step 7: Self-improvement

Three things to offer at the end of the run:

1. **Client facts.** If the meeting revealed anything about how this client works that isn't in `client_profile.md` (systems they use, who does what, standing constraints, compliance posture), offer to add it.
2. **Skill learnings.** If anything went wrong in this run, or the user corrected you, offer to run `/lhm-learn:learn` so it lands in this skill's `LEARNED.md` rather than being lost. Tool quirks, output format corrections, workflow steps that needed adjusting, and anything the user had to tell you twice all belong there.
3. **Canonical context gaps.** If `goals.md` or `current-projects.md` was missing, remind the user which owning Project Hub workflow it was routed to; do not claim a blank state file was created.

## Rules

- Folder contract: read references/folder-convention.md (lhm-project-hub).
