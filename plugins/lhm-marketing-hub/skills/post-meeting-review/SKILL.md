---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files. Use this after any client call or meeting. Pulls the Fathom transcript, extracts decisions and action items, and updates goals.md, current-projects.md, client_profile.md, and meetings/ folder. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting'."
---

# Post-Meeting Review

Debrief a client meeting and keep all client state files current. Run this after every client call.

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

## Step 4: Flag skill triggers

After updating the files, list any recommended next actions:
"Based on this meeting, I'd recommend:
- [Specific skill] for [reason from meeting]
- [Specific skill] for [reason from meeting]

Want me to kick off any of these now?"

## Step 5: Self-improvement

If the meeting revealed anything about how this client works that isn't in the client profile: offer to add it.
