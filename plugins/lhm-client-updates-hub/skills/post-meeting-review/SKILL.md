---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files, sync follow-up work to BasicOps with context, and draft a team update email. Use this after any client call or meeting, or when the user says 'meeting wrap'. Pulls the Fathom transcript, extracts decisions and action items, updates goals.md, current-projects.md, client_profile.md, and meetings/ folder, moves the client's BasicOps card to Follow Up with a Meeting Notes subtask, creates follow-up tasks with context, and drafts a Kristalyn/Michael summary email. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting', 'meeting wrap'."
---

# Post-Meeting Review

Debrief a client meeting and keep all client state current — files, BasicOps, and the team. Run this after every client call.

## Step 1: Get the transcript

**Option A — Fathom MCP (preferred)**
Use the Fathom MCP tool to retrieve the most recent meeting transcript for this client.
Search by client name or domain. If multiple meetings appear, ask the user which one.

**Option B — Manual (fallback)**
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
If significant changes: trigger `client-update` skill to propagate across all files.

### Save meeting notes
Save to `[client-folder]/meetings/YYYY-MM-DD-meeting-notes.md`:

```markdown
# Meeting Notes — [Client Name]
**Date:** YYYY-MM-DD
**Attendees:** [if noted in transcript]

## Decisions
-

## Action Items
### LHM
- [ ] [action] — due: [date if mentioned]

### Client
- [ ] [action]

## Client Updates
-

## Strategic Signals
-

## Recommended Next Steps
-
```

## Step 4: Sync to BasicOps

Board: `*Client Flow` (project ID `68655`). Sections: `Follow Up` (ID `107750`), `Meeting Week` (ID `107749`).

### 4a. Find the client card

Call `list_tasks_in_project` with `projectId: 68655` and `filter_title` set to the client's short/common name (e.g. "mhealth", not a long legal entity name). If nothing matches, call `list_tasks_in_project` again without `filter_title` and scan titles for a case-insensitive match.

- **No match:** skip to 4c. Tell the user: "No client card found in *Client Flow for [Client] — skipping the card move. You may want to create one."
- **One match:** that's the card — continue to 4b.
- **Multiple matches:** list them (title + URL from `link_to_task`) and ask the user which one is the client's card.

### 4b. Move the card and add the Meeting Notes subtask

1. `update_task` with `taskId: <card id>`, `section: 107750` — moves the card to Follow Up.
2. `create_task` with `projectId: 68655`, `parentTaskId: <card id>`, `section: 107750`, `title: "<Client Name> - Meeting Notes - <Month Day>"` (e.g. `"mhealth - Meeting Notes - 27 July"`), `description` set to a genuinely useful context brief — 3-6 sentences covering what was discussed, decisions made, wins/good news, and relevant background. This is the "why" behind the tasks created in 4c, not a transcript dump.

### 4c. Create standalone follow-up tasks

For each **LHM-owned** action item from Step 2 (client-owed action items stay in the meeting notes file only — do not push them to BasicOps):

1. `create_task` with `projectId: 68655`, `section: 107750`, `title: "<Client Name> — <task>"` (matches the existing `Client — task` convention already used on this board), `description` containing the ask plus the why (what was said or decided that produced this task).
2. `create_message_in_task` with `taskId: <new task id>`, `message` containing fuller context or a paraphrase/quote from the meeting, plus the Meeting Notes subtask's link (from `link_to_task` on the id created in 4b) and the local path `[client-folder]/meetings/YYYY-MM-DD-meeting-notes.md`.
3. Ask the user who should be assigned — don't assume. Once answered, call `update_task` with `taskId` and `assignee` set. (`@mentions` inside task messages aren't confirmed to trigger real BasicOps notifications — the `assignee` field is the reliable mechanism.)

If BasicOps MCP isn't authorized, skip this step entirely and tell the user: "BasicOps isn't connected — I've saved everything to the client files, but you'll need to add these to BasicOps manually."

## Step 5: Draft the team email

Use the Gmail `create_draft` tool — it only creates drafts (no send capability), so this always stops for a human to review and send.

1. Build the draft in chat first and ask: "Here's the team email — does this capture everything?"
   - **To:** kristalyn@localhealthmarketing.com.au
   - **Cc:** michael@localhealthmarketing.com.au
   - **Subject:** `Meeting wrap — <Client Name> — <Date>`
   - **Body** (internal audience — LHM shorthand/jargon is fine here, unlike `client-update-email`):
     - One line: "Michael met with <Client> on <date>."
     - A short synthesis of what was discussed, including context and wins — not just a task dump.
     - The list of tasks just added to BasicOps in Step 4, each with its task link (from `link_to_task`).
     - Anything the team should watch for.
   - Apply the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` per this plugin's `CLAUDE.md`.
2. On approval, call `create_draft` with the confirmed `to`, `cc`, `subject`, and `body`.
3. Tell the user the draft is ready in Gmail for review and sending.

If Gmail MCP isn't authorized, skip this step and tell the user the team email needs to be sent manually.

## Step 6: Flag skill triggers

After updating the files and syncing to BasicOps, list any recommended next actions:
"Based on this meeting, I'd recommend:
- [Specific skill] for [reason from meeting]
- [Specific skill] for [reason from meeting]

Want me to kick off any of these now?"

## Step 7: Self-improvement

If the meeting revealed anything about how this client works that isn't in the client profile: offer to add it.
