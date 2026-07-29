---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files, sync follow-up work to BasicOps with context, and draft a team update email. Use this after any client call or meeting, or when the user says 'meeting wrap'. Pulls the Fathom transcript, extracts decisions and action items, updates goals.md, current-projects.md, client_profile.md, and the client's meeting notes folder, sweeps the whole client folder for artefacts the meeting's decisions invalidate, moves the client's BasicOps card to Follow Up with a Meeting Notes subtask, creates briefed follow-up subtasks under it, identifies and routes any follow-on work the meeting generates to the right specialist agent (research and drafts run automatically, live-system changes get a ready-to-run plan), and drafts a team summary email. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting', 'meeting wrap'."
---

# Post-Meeting Review

Debrief a client meeting and keep all client state current: files, BasicOps, and the team. Run this after every client call.

## Step 1: Get the transcript

**Option A. Fathom MCP (preferred)**
Use the Fathom MCP tool to retrieve the most recent meeting transcript for this client.
Search by client name or domain. If multiple meetings appear, ask the user which one.

`list_meetings` with `created_after` set to the last few days is enough to find "the meeting I had today." Reach for `search_meetings` only for topic lookups across history, not for locating a specific recent call.

**Option B. Manual (fallback)**
If Fathom MCP is not available or cannot find the meeting:
"Please paste the meeting transcript or notes and I'll work from that."

## Step 2: Extract from transcript

Read the full transcript and extract:

**Decisions made:**
- Concrete decisions the client or team agreed to

**Action items:**
- Who needs to do what by when (note if it's a client action or LHM action)

**Client updates:**
- Any changes to client details, services, branding, contacts
- Any changes to goals, budgets, or targets
- Any problems or complaints raised

**Strategic signals:**
- Anything that changes priorities (new competitor, budget cut, new service launch, etc.)

**Compliance signals:**
- Anything with regulatory consequence (AHPRA, TGA, advertising standards, privacy)
- Watch for these in anecdotes and asides, not just in stated decisions. They seldom arrive announced as decisions, and they are often the most valuable thing in the meeting.
- A service discontinued, a practitioner departed, a claim the client wants to make, a testimonial they want to use: all compliance signals. Record the reasoning, not just the outcome, and write it into `client_profile.md` as standing posture.

**Skill triggers:**
- Anything that should prompt running a skill (poor Ads performance → zone check, content not ranking → SEO review, etc.)

## Step 3: Update client state files

### Update `goals.md`
If any KPIs, budgets, or targets changed: update the relevant sections. Add a dated note:
```
<!-- Updated YYYY-MM-DD from meeting: [one-line summary of what changed] -->
```

### Update `current-projects.md`
- Mark completed projects as completed (with date)
- Add new projects from action items
- Update status of existing projects if discussed
- Add new items to backlog if raised but not yet started

### Update `client_profile.md`
If any client details changed (name, services, contacts, business details): update the profile.

Do not trigger `client-update` from here. Propagation beyond the state files is handled in Step 3.5, which gathers the context `client-update` needs before invoking it.

### Resolve the client acronym

Runs every time, regardless of whether anything else in the profile changed — every BasicOps task title from Step 4 onward needs this.

Check `client_profile.md` for an `Acronym:` field.

- **Present:** use it as-is. No questions asked.
- **Missing:** derive one from the client's display name (first letter of each significant word, uppercase — "Your Story Physio" → `YSP`, "Australian Sports Physio" → `ASP`). Confirm with the user before proceeding (e.g. "Use YSP as the BasicOps short-code for Your Story Physio?"), since a bad auto-derivation is annoying to unwind once it's on ten subtask titles. Once confirmed, or the user gives a different value, write `Acronym: <value>` to `client_profile.md` so every future run just reads it.
- **`client_profile.md` doesn't exist yet:** derive an acronym for this run only, tell the user it wasn't saved because the profile doesn't exist, and don't block the rest of the skill on it.

### Save meeting notes

**Check for an existing meetings folder before creating one.** The convention varies by client. mhealth uses `client-meetings/`, others use `meetings/`. List the client folder and match what is already there. Only create `meetings/` if no equivalent exists.

Save to `[client-folder]/[meetings-folder]/YYYY-MM-DD-meeting-notes.md`:

```markdown
# Meeting Notes — [Client Name]
**Date:** YYYY-MM-DD
**Attendees:** [if noted in transcript]

## Decisions
-

## Action Items
### LHM
- [ ] [action] (due: [date if mentioned])

### Client
- [ ] [action]

## Client Updates
-

## Strategic Signals
-

## Recommended Next Steps
-
```

## Step 3.5: Propagation sweep

**Do not skip this.** Updating the four state files is not the same as propagating a decision. A service discontinued in a meeting will be sitting in sitemaps, keyword maps, redirect maps, briefs, GBP plans, and landing page copy, none of which Step 3 touches.

This step **detects**. It does not edit. `client-update` owns the editing.

**1. Grep the whole client folder** for every entity the meeting changed, discontinued, renamed, or added.

**2. Sort the hits into forward-looking artefacts and historical records,** using the pile definitions in `client-update`'s Step 2b. That table is the single source of truth for the split; do not restate it here. Forward-looking artefacts need updating. Historical records stay untouched, because editing them rewrites history and destroys the audit trail.

**3. Check for reversed decisions.** Search the forward-looking pile for anything marked *confirmed*, *signed off*, *decided*, or *approved* that the new decision invalidates. This is the failure mode that matters most, because a meeting can overturn work someone signed off days earlier without anyone noticing. When you find one, capture the original reasoning and who made the call, and carry both into the handoff. Do not resolve it yourself.

**4. For regulated services, check live advertising surfaces too**, not just the website. Google Business Profile categories, service lists, business descriptions and directory entries are all advertising. A compliance breach there is live exposure independent of any rebuild in progress.

**5. Hand off to `client-update`.** Invoke the skill and pass it four things: the change (and whether it is a substitution or a removal), the sorted file list, the conflicts found in item 3, and anything flagged in item 4. `client-update` picks up at its **Step 2e**, presents the whole picture to the user for confirmation, and only then edits. Nothing in the client folder changes until the user has signed off inside `client-update`.

**6. Come back and finish.** The handoff is a detour, not an exit. When `client-update` completes, return here and continue at Step 4. Steps 4 through 8 have not run yet. Hold `client-update`'s downstream implications from its own Step 4 and fold them into Step 5's task list below, alongside Step 2's skill triggers, so the user gets one set of routed follow-on work rather than two nearly identical prompts.

**If nothing came back from the grep,** say so in a line and move on. No sweep findings is a normal outcome for a meeting that changed no entities.

## Step 4: Sync to BasicOps

Board: `*Client Flow` (project ID `68655`). Sections: `Follow Up` (ID `107750`), `Meeting Week` (ID `107749`).

### BasicOps field rules (read before writing anything)

- **Never put task detail in the `description` field.** All context, briefing detail, links, and "what done looks like" go into the task discussion via `create_message_in_task`. The description stays empty or holds a single line at most. This is a hard rule from this plugin's `CLAUDE.md` and applies to every write, every client, no exceptions.
- **Discussion messages take raw HTML.** Do not escape it to entities, because `&lt;p&gt;` renders as literal text. If you get it wrong, `delete_message` with the returned id and repost.
- **Task titles take a plain `&`,** not `&amp;`, which renders as the literal entity.

### 4a. Find the client card

Call `list_tasks_in_project` with `projectId: 68655` and `filter_title` set to the client's short/common name (e.g. "mhealth", not a long legal entity name). If nothing matches, call `list_tasks_in_project` again without `filter_title` and scan titles for a case-insensitive match.

- **No match:** tell the user "No client card found in *Client Flow for [Client]. Want me to create one, or should the follow-ups go in as standalone tasks?" Creating the card is usually right, because everything in this board hangs off it. If they decline, skip 4b and run 4c in **no-card mode** (see the note at the end of 4c).
- **One match:** that's the card. Continue to 4b.
- **Multiple matches:** list them (title + URL from `link_to_task`) and ask the user which one is the client's card.

### 4b. Move the card and add the Meeting Notes subtask

1. `update_task` with `taskId: <card id>`, `section: 107750`, which moves the card to Follow Up.
2. `create_task` with `projectId: 68655`, `parentTaskId: <card id>`, `section: 107750`, `title: "<Acronym> - Meeting Notes - <Month Day>"` (e.g. `"YSP - Meeting Notes - 27 July"` — `<Acronym>` is the client's short-code from `client_profile.md`, resolved in Step 3). Put a single line in `description` (e.g. "Digital catch-up with Nick and Steve, 27 July") and nothing more.
3. `create_message_in_task` on the new subtask with the actual briefing. This is where the substance goes: what was discussed, decisions made and why, wins and good news, relevant background, and the Fathom link plus the local meeting notes path. Write it as prose for a colleague who wasn't in the room, not as a transcript dump. This is the "why" behind the tasks created in 4c.
4. `create_message_in_task` on the **client card itself** (`taskId: <card id>`) with a session trace covering decisions and their trade-offs, open risks, what is now in progress, and anything parked. The card then carries its own history, so anyone landing on it later can see how the project got here without reading back through six months of meeting notes.

### 4c. Create follow-up subtasks

For each **LHM-owned** action item from Step 2. Client-owed action items get their own subtask too, but in 4d, not here, with a different owner and framing.

1. `create_task` with `projectId: 68655`, **`parentTaskId: <card id>`**, `section: 107750`, `title: "<Acronym> - Action - <task>"` (`<Acronym>` per Step 3 — this replaces the board's older `Client — task` title convention). These are **subtasks under the client card**, not standalone tasks floating in the section. The card is the client's home and everything hangs off it. Put at most one line in `description`.
2. `create_message_in_task` with `taskId: <new task id>` containing the full briefing: why it matters (with the relevant quote or decision from the meeting), the background they need, what done looks like, and which judgement calls to surface rather than decide alone. Brief them like a capable colleague who wasn't in the room. Include the Meeting Notes subtask's link (from `link_to_task` on the id created in 4b) and the local path to the meeting notes file.
3. Ask the user who should be assigned, rather than assuming. Batch this into a single `AskUserQuestion` with the tasks grouped into sensible clusters instead of asking once per task. Once answered, call `update_task` with `taskId` and `assignee` set. (`@mentions` inside task messages aren't confirmed to trigger real BasicOps notifications, so the `assignee` field is the reliable mechanism.)
4. **Answers carry instruction beyond a name more often than not.** Real examples: "fold this into the landing page build", "X should be notified even though it isn't theirs", "they already have access, go through my account", "this one's urgent, the rest can wait". The `assignee` field loses all of that. Post it as a follow-up discussion message on the task.

**No-card mode.** If 4a found no card and the user declined to create one, drop `parentTaskId` and create the tasks directly in section `107750`. Everything else in 4c still applies: the full briefing still goes in the discussion, and the assignment question is still asked. Omit the Meeting Notes subtask link, since 4b did not run, and point at the local meeting notes path instead.

### 4d. Create client follow-up subtasks

For each **client-owed** action item from Step 2 — these used to stay in the meeting notes file only; now they also get a BasicOps trail so someone is actually chasing them.

1. `create_task` with `projectId: 68655`, `parentTaskId: <card id>`, `section: 107750`, `title: "<Acronym> - Client - <task>"`. Put at most one line in `description`.
2. `create_message_in_task` with the briefing: what's needed from the client (the specific asset, document, or approval), why it matters (what it's blocking), and the meeting context. Frame it as "chase the client for X," not "do X" — Kristalyn's job here is follow-up, not execution.
3. `update_task` with `taskId: <new task id>`, `assignee` set to Kristalyn (`kristalyn@localhealthmarketing.com.au`; if the `assignee` field needs a BasicOps user id rather than an email, resolve it via `list_users` first). No assignment question for these, unlike 4c and Step 6 — chasing clients for outstanding items is always Kristalyn's, every meeting.

**No-card mode.** Same as 4c: if 4a found no card and the user declined to create one, drop `parentTaskId` and create these directly in section `107750`.

**If you mis-parent a task,** `update_task` with `parentTaskId` re-parents it and preserves the assignee, description, and discussion. No need to delete and recreate. Applies to 4c and 4d alike.

If BasicOps MCP isn't authorized, skip this step entirely and tell the user: "BasicOps isn't connected. I've saved everything to the client files, but you'll need to add these to BasicOps manually."

## Step 5: Identify & route follow-on work

For every item in Step 2's "Skill triggers" list, plus any downstream implications Step 3.5 handed back from a `client-update` detour, identify the concrete task, classify it, and act on that classification. There is no approval gate in this step: the classification itself is the safety mechanism (see 5b). If there is nothing to route, say so in one line and move to Step 6.

This step is about doing the work, or kicking it off. BasicOps bookkeeping — subtasks, discussion messages, file attachments, assignment — all happens in Step 6, once this step knows what it's dealing with.

### 5a. Identify the task

Turn the trigger into a specific, actionable task, not a category. "SEO review" becomes "investigate why /services/knee-pain isn't ranking, per the client's comment about losing traffic." Carry the meeting context (the actual quote or decision) forward; Step 6 needs it for the briefing.

### 5a.5 Cross-check against Step 4's action items

Before classifying, check whether this task describes the same underlying work as an LHM-owned action item Step 4 already turned into a subtask. Action items and skill triggers come from two separate extraction buckets in Step 2, and the same meeting decision can land in both — "we need a new blog post about the new service" is naturally both an action item and a content trigger. Skipping this check produces two subtasks for the same piece of work: an empty one from Step 4 and a routed, dispatched one from here.

If a match is found, do not create a second subtask in Step 6. Carry the matched Step 4 subtask id forward, act on the task as normal in 5c, then in Step 6 post the briefing, dispatch note, or handoff prompt to that existing subtask's discussion instead of creating a new one. If no match, treat it as a new task.

### 5b. Classify

Two questions decide where a task lands:

1. **Does it need a specialist agent's judgment, or can Claude do it directly with tools already connected in this session** (Analytics MCP, GSC MCP, etc.)?
2. **Does the task's output mutate a live client-facing system** (a live WordPress page, a live Ads campaign, a live GBP listing), **or does it only produce an artifact** (a document, a CSV, a draft, an answer)?

| | Artifact / answer only | Mutates a live system |
|---|---|---|
| **No agent needed** | **Direct** — do it now, in this session | (does not occur — live mutations always need a specialist agent) |
| **Needs a specialist agent** | **Auto-run** — dispatch a background specialist agent | **Handoff-prompt** — prepare a plan and a prompt, a human executes elsewhere |

Tiering is **per task, not per agent** — the same agent can produce both an auto-run task and a handoff-prompt task depending on what's being asked. `google-ads` is the clearest example: keyword research and ad copy drafting for a new ad group is auto-run (the output is a CSV, nothing in the account changes); submitting that ad group or changing a budget is handoff-prompt.

**Routing table:**

| Trigger type | Agent | Typical tier | Title type |
|---|---|---|---|
| GA/GSC stat questions, quick performance checks | *(none — Claude direct)* | Direct | `Analytics` |
| Keyword research, ad copy drafting for a new ad group/service/location | `lhm-marketing-hub:google-ads` | Auto-run | `GAds` |
| Live Ads account changes (submit campaign, adjust budget, pause/activate) | `lhm-marketing-hub:google-ads` | Handoff-prompt | `GAds` |
| Keyword research, ranking/content strategy analysis | `lhm-marketing-hub:seo` | Auto-run | `SEO` |
| Blog post, page copy draft, content brief | `lhm-marketing-hub:content` | Auto-run | `Blog Article` / `Landing Page` / `Content Brief` / `Page Copy` — whichever fits the specific task |
| Live page edits on the client site | `lhm-wordpress-hub:site-extension` | Handoff-prompt | `Page Edit` |

**No match.** If a task doesn't cleanly fit the table or Direct, fall back to a plain-text recommendation line in the email (Step 7). No subtask, no dispatch. Do not force a task into a tier it doesn't belong in.

### 5c. Act on the classification

- **Direct:** run the check now and hold the answer for Step 6 to record. If the tool this needs isn't connected, note "needs manual check" for Step 7's email instead of blocking the rest of this step.
- **Auto-run:** dispatch the specialist agent via the Agent tool with `run_in_background: true`. Dispatch every auto-run task for the meeting in parallel, in a single message. The agent keeps running after this step ends; its result lands later (Step 6) as a follow-up message on its subtask, whenever it finishes.
- **Handoff-prompt:** write the plan file to `[client-folder]/meeting-wraps/YYYY-MM-DD/<slug>-plan.md`:

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

Then build the handoff prompt: plain text, ready to paste into a fresh Claude Code or ChatGPT session, with the plan file's contents inlined in full, not just linked (ChatGPT can't read the local filesystem, and the prompt needs to work identically on either platform):

```
I'm ready to work on this: [task title] for [Client].

Act as the [agent name] specialist. Here's the plan:

[Plan file contents inlined]
```

Nothing is dispatched for handoff-prompt tier. A human runs this elsewhere.

## Step 6: Sync follow-on work to BasicOps

Same shape as Step 4, applied to Step 5's output instead of the meeting's action items. For every task from Step 5 that did not match an existing Step 4 subtask (per 5a.5): `create_task` with `projectId: 68655`, `parentTaskId: <card id>` (the client card found in Step 4a), `section: 107750`, title `"<Acronym> - <Type> - <task>"` (`<Acronym>` per Step 3, `<Type>` from 5b's routing table), one line in `description`, full detail via `create_message_in_task` in the discussion. Tasks that matched an existing Step 4 subtask post there instead of creating a new one. Same BasicOps field rules as Step 4: nothing but a single line in `description`, raw HTML in discussion messages, a plain `&` in titles.

**Direct tier:** post the answer, already in hand from 5c, to the subtask discussion. Nothing further to track; there's no pending work to follow up on.

**Auto-run tier:** post the dispatch briefing to the discussion when the subtask is created (why it matters, background, what done looks like — the same fields 4c already uses), noting the agent is running in the background.

Posting the agent's actual output is not part of this step's own execution; it happens whenever the agent finishes, which may be well after Steps 6 through 8 have run and this skill invocation has ended. When that notification arrives: append the output as a follow-up message on the same subtask, attach any generated files (keyword CSVs, ad copy CSVs, content drafts) via `add_file_to_task`, save a copy to `[client-folder]/meeting-wraps/YYYY-MM-DD/`, and add a one-line pointer on the client card so a finished result isn't buried under other subtask threads. If the agent fails instead of completing, post what was attempted and what broke to the subtask discussion rather than losing it silently. This depends on the session staying reachable long enough to catch the completion notification; there is no separate fallback if it doesn't, and a result could go unposted with nothing surfacing that fact. Accepted as a known risk for now rather than solved with a dedicated dispatcher agent.

**Handoff-prompt tier:** post the plan summary and the full handoff prompt built in 5c (plan file contents inlined, not just linked) to the discussion, wrapped in a `<pre>` block so the raw-HTML field preserves line breaks and spacing, with the plan's angle-bracket placeholders HTML-escaped first so they don't get swallowed as unrecognized tags.

**Assignment:** once all of this step's new subtasks exist, batch-ask who's assigned, same `AskUserQuestion` pattern Step 4c already uses. This only covers this step's own new subtasks; Step 4's are assigned within Step 4 itself and are not revisited here. Tasks that matched an existing Step 4 subtask (5a.5) keep that subtask's existing assignee.

If BasicOps isn't connected, skip this step entirely and tell the user which Step 5 items would have been routed and that they need manual tracking — Step 5's work (Direct answers, dispatched agents, plan files) still happened, only the BasicOps sync is skipped. If Step 4a found no client card and the user declined to create one, drop `parentTaskId` and create these subtasks directly in section `107750`, the same no-card mode Step 4c uses.

## Step 7: Draft the team email

Default to the Gmail `create_draft` tool. It only creates drafts (no send capability), so this always stops for a human to review and send, and replies thread back to the sender's own address.

If the user asks for a different channel (Mailgun via Zapier, for example), warn them what changes before doing it: the From address must sit on the connected Mailgun domain, so the mail will not come from their own address and will not appear in their Sent folder. Mailgun also sends on the spot rather than drafting. Fall back to Gmail without argument if it fails.

1. Build the draft in chat first and ask: "Here's the team email. Does this capture everything?"
   - **To:** kristalyn@localhealthmarketing.com.au, plus anyone assigned a task in Step 4c or Step 6
   - **Cc:** michael@localhealthmarketing.com.au
   - **Subject:** `Meeting wrap — <Client Name> — <Date>`
   - **Body.** Internal audience, so LHM shorthand and jargon are fine here, unlike `client-update-email`:
     - One line: "Michael met with <Client> on <date>."
     - A short synthesis of what was discussed, including context and wins, rather than a task dump.
     - The list of tasks added to BasicOps in Steps 4 and 6, each with its task link (from `link_to_task`). For any task Step 5 routed — including one that reused an existing Step 4 subtask via 5a.5 — note the tier: Direct tier gets its answer inline (e.g. "Organic traffic is up 12% MoM — details in the task"); auto-run tier is noted as running (e.g. "Keyword research for the new Riverside location — running now, results will land in the task"); handoff-prompt tier is noted as ready for hand-off (e.g. "Ads investigation — plan ready, prompt waiting in the task"), so the assignee knows to go get the prompt rather than expecting the work is already done.
     - Anything the team should watch for.
   - Apply the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` per this plugin's `CLAUDE.md`.
2. On approval, call `create_draft` with the confirmed `to`, `cc`, `subject`, and `body`.
3. Tell the user the draft is ready in Gmail for review and sending.

If Gmail MCP isn't authorized, skip this step and tell the user the team email needs to be sent manually.

## Step 8: Self-improvement

Two things to offer at the end of the run:

1. **Client facts.** If the meeting revealed anything about how this client works that isn't in `client_profile.md` (systems they use, who does what, standing constraints, compliance posture), offer to add it.
2. **Skill learnings.** If anything went wrong in this run, or the user corrected you, offer to run `/lhm-learn:learn` so it lands in this skill's `LEARNED.md` rather than being lost. Tool quirks, output format corrections, workflow steps that needed adjusting, and anything the user had to tell you twice all belong there.
