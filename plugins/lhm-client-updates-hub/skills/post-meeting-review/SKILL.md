---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files, sync follow-up work to BasicOps with context, and draft a team update email. Use this after any client call or meeting, or when the user says 'meeting wrap'. Pulls the Fathom transcript, extracts decisions and action items, updates goals.md, current-projects.md, client_profile.md, and the client's meeting notes folder, sweeps the whole client folder for artefacts the meeting's decisions invalidate, moves the client's BasicOps card to Follow Up with a Meeting Notes subtask, creates briefed follow-up subtasks under it, and drafts a team summary email. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting', 'meeting wrap'."
---

# Post-Meeting Review

Debrief a client meeting and keep all client state current: files, BasicOps, and the team. Run this after every client call.

## Step 1: Get the transcript

**Option A. Fathom MCP (preferred)**
Use the Fathom MCP tool to retrieve the most recent meeting transcript for this client.
Search by client name or domain. If multiple meetings appear, ask the user which one.

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

**6. Come back and finish.** The handoff is a detour, not an exit. When `client-update` completes, return here and continue at Step 4. Steps 4 through 7 have not run yet. Hold `client-update`'s downstream implications from its own Step 4 and fold them into Step 6 below, so the user gets one set of recommendations rather than two nearly identical prompts.

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
2. `create_task` with `projectId: 68655`, `parentTaskId: <card id>`, `section: 107750`, `title: "<Client Name> - Meeting Notes - <Month Day>"` (e.g. `"mhealth - Meeting Notes - 27 July"`). Put a single line in `description` (e.g. "Digital catch-up with Nick and Steve, 27 July") and nothing more.
3. `create_message_in_task` on the new subtask with the actual briefing. This is where the substance goes: what was discussed, decisions made and why, wins and good news, relevant background, and the Fathom link plus the local meeting notes path. Write it as prose for a colleague who wasn't in the room, not as a transcript dump. This is the "why" behind the tasks created in 4c.
4. `create_message_in_task` on the **client card itself** (`taskId: <card id>`) with a session trace covering decisions and their trade-offs, open risks, what is now in progress, and anything parked. The card then carries its own history, so anyone landing on it later can see how the project got here without reading back through six months of meeting notes.

### 4c. Create follow-up subtasks

For each **LHM-owned** action item from Step 2. Client-owed action items stay in the meeting notes file only; do not push them to BasicOps.

1. `create_task` with `projectId: 68655`, **`parentTaskId: <card id>`**, `section: 107750`, `title: "<Client Name> — <task>"` (matches the existing `Client — task` convention already used on this board). These are **subtasks under the client card**, not standalone tasks floating in the section. The card is the client's home and everything hangs off it. Put at most one line in `description`.
2. `create_message_in_task` with `taskId: <new task id>` containing the full briefing: why it matters (with the relevant quote or decision from the meeting), the background they need, what done looks like, and which judgement calls to surface rather than decide alone. Brief them like a capable colleague who wasn't in the room. Include the Meeting Notes subtask's link (from `link_to_task` on the id created in 4b) and the local path to the meeting notes file.
3. Ask the user who should be assigned, rather than assuming. Batch this into a single `AskUserQuestion` with the tasks grouped into sensible clusters instead of asking once per task. Once answered, call `update_task` with `taskId` and `assignee` set. (`@mentions` inside task messages aren't confirmed to trigger real BasicOps notifications, so the `assignee` field is the reliable mechanism.)
4. **Answers carry instruction beyond a name more often than not.** Real examples: "fold this into the landing page build", "X should be notified even though it isn't theirs", "they already have access, go through my account", "this one's urgent, the rest can wait". The `assignee` field loses all of that. Post it as a follow-up discussion message on the task.

**If you mis-parent a task,** `update_task` with `parentTaskId` re-parents it and preserves the assignee, description, and discussion. No need to delete and recreate.

**No-card mode.** If 4a found no card and the user declined to create one, drop `parentTaskId` and create the tasks directly in section `107750`. Everything else in 4c still applies: the full briefing still goes in the discussion, and the assignment question is still asked. Omit the Meeting Notes subtask link, since 4b did not run, and point at the local meeting notes path instead.

If BasicOps MCP isn't authorized, skip this step entirely and tell the user: "BasicOps isn't connected. I've saved everything to the client files, but you'll need to add these to BasicOps manually."

## Step 5: Draft the team email

Default to the Gmail `create_draft` tool. It only creates drafts (no send capability), so this always stops for a human to review and send, and replies thread back to the sender's own address.

If the user asks for a different channel (Mailgun via Zapier, for example), warn them what changes before doing it: the From address must sit on the connected Mailgun domain, so the mail will not come from their own address and will not appear in their Sent folder. Mailgun also sends on the spot rather than drafting. Fall back to Gmail without argument if it fails.

1. Build the draft in chat first and ask: "Here's the team email. Does this capture everything?"
   - **To:** kristalyn@localhealthmarketing.com.au, plus anyone assigned a task in Step 4c
   - **Cc:** michael@localhealthmarketing.com.au
   - **Subject:** `Meeting wrap — <Client Name> — <Date>`
   - **Body.** Internal audience, so LHM shorthand and jargon are fine here, unlike `client-update-email`:
     - One line: "Michael met with <Client> on <date>."
     - A short synthesis of what was discussed, including context and wins, rather than a task dump.
     - The list of tasks just added to BasicOps in Step 4, each with its task link (from `link_to_task`).
     - Anything the team should watch for.
   - Apply the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` per this plugin's `CLAUDE.md`.
2. On approval, call `create_draft` with the confirmed `to`, `cc`, `subject`, and `body`.
3. Tell the user the draft is ready in Gmail for review and sending.

If Gmail MCP isn't authorized, skip this step and tell the user the team email needs to be sent manually.

## Step 6: Flag skill triggers

After updating the files and syncing to BasicOps, list any recommended next actions. If Step 3.5 handed off to `client-update`, merge its downstream implications into this single list rather than presenting them separately:
"Based on this meeting, I'd recommend:
- [Specific skill] for [reason from meeting]
- [Specific skill] for [reason from meeting]

Want me to kick off any of these now?"

## Step 7: Self-improvement

Two things to offer at the end of the run:

1. **Client facts.** If the meeting revealed anything about how this client works that isn't in `client_profile.md` (systems they use, who does what, standing constraints, compliance posture), offer to add it.
2. **Skill learnings.** If anything went wrong in this run, or the user corrected you, offer to run `/lhm-learn:learn` so it lands in this skill's `LEARNED.md` rather than being lost. Tool quirks, output format corrections, workflow steps that needed adjusting, and anything the user had to tell you twice all belong there.
