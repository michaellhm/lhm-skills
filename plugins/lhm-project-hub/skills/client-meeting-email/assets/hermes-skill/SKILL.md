---
name: josephine-post-meeting
description: Route Michael or Josephine meeting wraps to Codex.
---

# Josephine Post-Meeting Router

Hermes is the manager for this workflow, never the meeting analyst.

## Preparation flow

1. Resolve the named client to a registered `client_id`. Verify its knowledge source is the active shared LHM Knowledge vault or its registered mirror. The separate deliverables root is Claude Workspace/Current Clients/<verified client folder>. Never invent a folder or fall back to legacy work-folder profiles.
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
`vault_applied`, including the exact files. Reconcile the meeting record, overview/profile, goals, current-project index and affected service/project notes against the reviewed bundle; report each as updated, unchanged or blocked. A missing registered context file or partial application remains a visible gap. Report Gmail success only when the
approval is `gmail_draft_queued` and the draft result is `draft_created`.
If the helper or a status command fails, stop and report the exact error.

Never accept email subject, body, recipients, file paths or file contents from
the conversational request. The host retrieves the exact reviewed artifacts by
run ID and hash. Never send. BasicOps is disabled.

## Subsequent BasicOps meeting wrap

Email preparation remains read-only with respect to BasicOps. Josephine's explicit
request to save the reviewed wrap authorises a separate `post-meeting-review`
operation through `basicops-task-manager`: create or reuse one top-level
`<Client name> meeting <day> <month>` card on Client Flow, assigned to Michael.
Put the full reviewed email, recording/source link and **Proposed actions — awaiting
Michael's review** in Discussion. Description holds metadata and working URLs only.
Do not create separate action cards, nested meeting notes, delegate or start work.
Preserve the distinction between reviewed/drafted and verified-sent email.

Next handoff: Michael runs `meeting-to-action` against the card to reconcile
existing work, resolve decisions and approve tasks and delegation. Kristalyn then
coordinates assigned delivery. Email approval alone does not release actions.
A request to do both stages must explicitly authorise the task/delegation stage.
Use the authenticated BasicOps connector if available; do not change permissions
or route BasicOps through the read-only meeting-dispatch worker. If unavailable,
return the ready-to-save card and precise connector gap without claiming creation.
The controlling rules are `basicops-task-manager/references/meeting-wrap.md`.
