---
name: start-website
description: "Safely sync and open this local website. Use when the client asks to start website, check their website or continue this review workflow."
---
# Start Website

Locate this repository's root by its .lhm-review/workflows.md, not by assuming the current working directory. Read repository instructions, brain/Project.md first, then .lhm-review/workflows.md, .lhm-review/client-config.json and .lhm-review/client-review.json when present. Follow the **start-website** section of the shared workflow, including its commit identity check: compare `git config user.email` with `client_identity.commit_emails` in `.lhm-review/client-config.json`, and if it does not match, explain why it matters and ask the client before setting it (suggest their GitHub noreply address; repository-local setting only). Missing setup or records are a gap: ask LHM, do not invent review scope.

Preserve local edits, require explicit page approvals, keep publication separate and respect actual tool permissions. Do not fabricate browser/editor access, deployment URLs or sent emails. End with verified progress, blockers and the exact next step.
