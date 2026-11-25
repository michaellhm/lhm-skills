# Delivery Artefact and Handoff Contract

Apply this contract whenever a skill or agent produces material work for a client or LHM.

## Resolve the canonical destination

Read the client or project state before execution. Use the exact registered destination; do not infer one from a client name or silently substitute a local folder.

| Output | Canonical system |
|---|---|
| Reports, audits, briefs, copy, plans and client-facing files | Registered Google Drive client/project folder |
| Client state, decisions, run history and next executable stage | Canonical Obsidian service/project file |
| Website code and technical implementation | Registered repository and branch |
| Reviewable website implementation | Registered staging/preview environment plus evidence |
| Human actions, exceptions and handoffs | BasicOps discussion through the approved task workflow |
| Financial workbooks and sensitive financial evidence | Configured governed finance destination |
| Notifications | Link to the canonical artefact; never become the primary record |

If the exact destination is missing, stop the artefact write and preserve the result in the worker handoff. In a governed departmental run return canonical state `needs_context`, name the context owner and preserve the exact resume point. For a legacy non-departmental caller whose schema only supports the older vocabulary, project that state as `work_state: needs_review` while retaining `state: needs_context`. Do not guess.

Reusable skills define the destination fields but do not embed client-specific IDs. The calling context must resolve and pass destinations in this form (additional systems may be included):

```yaml
delivery_destinations:
  google_drive:
    folder_id: "exact registered parent ID"
    folder_url: "observed registered folder URL"
    relative_path: "optional governed subfolder"
    source_record: "canonical record used to resolve it"
```

Folder names and a desktop-selected working folder are not proof of the canonical destination. File-producing workers must use the exact supplied parent ID and return the observed parent ID on readback.

## Worker responsibility

The specialist worker that produces the deliverable must:

1. Save it to the canonical system before claiming completion or requesting approval for consequential execution.
2. Read the saved file, record or deployment metadata back.
3. Verify its name, parent/project, version/branch when relevant and observed URL or record ID.
4. For Google Drive, verify the file ID, URL and observed parent folder ID by readback.
5. Return the verified reference with canonical departmental `state` when applicable and the legacy `work_state` projection required by the caller.

Saving an internal draft or report is not approval to publish, deploy, send, merge or change a live advertising/account system. Keep those approval gates separate.

If the work produces no durable artefact, return `artefact_state: not_required` with a short reason. Do not create filler files.

## Orchestrator responsibility

Hermes or the calling orchestrator records the run, evidence, work state, verified artefact reference and next owner in the canonical state file. It notifies the human by linking to the artefact. It does not recreate the specialist's deliverable when the worker can save it.

## Required handoff

Return:

- `run_result`: `succeeded` or `failed`
- `work_state`: `completed`, `needs_review` or `failed`
- `artefact_state`: `verified`, `needs_review` or `not_required`
- `artefact_type`, `canonical_system`, observed URL/ID/path and verification evidence
- for Drive artefacts: `drive_file_id`, `drive_url`, `observed_parent_folder_id`, version/name and `upload_verified`
- approval required, next owner and next action

Never report `completed` when a required artefact was not saved and verified.
