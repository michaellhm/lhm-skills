---
name: post-meeting-review
description: "Work through a client meeting's follow-up: update client state files, sweep the client folder for stale artefacts, turn action items into assigned BasicOps subtasks, and draft a team update email. This skill has moved — invoke `lhm-project-hub:post-meeting-review` instead, which reads the meeting record `lhm-project-hub:client-meeting-email` saves rather than pulling Fathom itself, and works through follow-up tasks one at a time instead of auto-dispatching them. Triggers on: 'meeting wrap', 'work through the follow-ups', 'post-meeting review', 'meeting follow-ups', 'client call debrief'."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Moved

This skill has moved to the LHM Project Hub.

Invoke `lhm-project-hub:post-meeting-review` instead — it is the same workflow, now
writing to the client's project-management/ folder. If lhm-project-hub is
not installed, install it from the LHM marketplace, then re-run.
