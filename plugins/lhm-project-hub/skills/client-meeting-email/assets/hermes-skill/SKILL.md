---
name: josephine-post-meeting
description: Route Michael or Josephine meeting wraps to Codex.
---

# Josephine Post-Meeting Router

Hermes is the manager for this workflow, never the meeting analyst.

## Preparation flow

1. Resolve the named client to a registered `client_id`. Never invent a folder.
2. Use authenticated Fathom tools to locate the meeting and retrieve metadata,
   summary and complete transcript. If ambiguous, ask one focused question.
3. Treat Michael's voice-note transcription as founder context: extract explicit
   inclusions, exclusions and internal-only material. It may be brief; Fathom is
   the full evidence source.
4. Build the closed `client_meeting_capture` v1 request from the canonical
   `request-schema.json`. During the current compatibility phase include the
   Fathom evidence package and exact SHA-256 hashes. Permissions must be exactly:
   read Fathom/client context and stage artifacts; no vault, Gmail or BasicOps.
5. Submit the JSON on stdin with:

   `/opt/data/profiles/lhm_brain/bin/meeting-dispatch submit`

6. Poll `meeting-dispatch status <run_id>`. Retrieve only a completed result with
   `meeting-dispatch result <run_id>`.
7. Present the Codex bundle and its `content_hash` for Michael to approve, revise
   or reject. Do not independently rewrite or complete the specialist work.

If the dispatcher, worker, client registration, skill or connector is missing,
fail closed and report the exact missing route. Do not load the Project Hub
execution skill locally and do not analyse the transcript inside Hermes.

## Mutations

Preparation authorises no mutations. After Michael explicitly approves both
the vault changes and Gmail draft for an exact reviewed run and content hash,
run exactly one command:

`/opt/data/profiles/lhm_brain/bin/meeting-approve approve-both '<run_id>' '<content_hash>' '<Michael exact approval text>'`

Do not inspect or reconstruct approval JSON schemas. The helper validates the
request, creates both closed requests and returns three IDs plus exact status
commands. Run those returned commands. Report vault success only for
`vault_applied`, including the exact files. Report Gmail success only when the
approval is `gmail_draft_queued` and the draft result is `draft_created`.
If the helper or a status command fails, stop and report the exact error.

Never accept email subject, body, recipients, file paths or file contents from
the conversational request. The host retrieves the exact reviewed artifacts by
run ID and hash. Never send. BasicOps is disabled.
