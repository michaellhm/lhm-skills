---
name: client-update
description: "Propagate a client data change across all client files. Use when a client's name, service offering, contact details, branding, or other core details have changed. Finds every reference in the client folder and updates them. Flags downstream strategic work needed. Triggers on: 'client changed their name', 'they rebranded', 'new contact', 'updated their services', 'client update', 'name change', 'Raise the Bar Psychology is now Raise the Bar Clinic'."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Moved

This skill has moved to the LHM Project Hub.

Invoke `lhm-project-hub:client-update` instead — it is the same workflow, now
writing to the client's project-management/ folder. If lhm-project-hub is
not installed, install it from the LHM marketplace, then re-run.
