---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files, sync follow-up work to BasicOps with context, and draft a team update email. Use this after any client call or meeting, or when the user says 'meeting wrap'. Pulls the Fathom transcript, extracts decisions and action items, updates goals.md, current-projects.md, client_profile.md, and the client's meeting notes folder, sweeps the whole client folder for artefacts the meeting's decisions invalidate, moves the client's BasicOps card to Follow Up with the meeting context posted to it directly, creates briefed follow-up subtasks under it (client-owed items get their own subtask too, always routed to Kristalyn for follow-up), identifies and routes any follow-on work the meeting generates to the right specialist agent (research and drafts run automatically, live-system changes get a ready-to-run plan you can resume in a fresh session), and drafts a team summary email. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting', 'meeting wrap'."
---

# Moved

This skill has moved to the LHM Project Hub.

Invoke `lhm-project-hub:post-meeting-review` instead — it is the same workflow, now
writing to the client's project-management/ folder. If lhm-project-hub is
not installed, install it from the LHM marketplace, then re-run.
