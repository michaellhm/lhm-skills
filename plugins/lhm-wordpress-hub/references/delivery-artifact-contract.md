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
| Notifications | Link to the canonical artefact; never become the primary record |

If the exact destination is missing, stop the artefact write, preserve the result in the worker handoff and return `needs_review`. Do not guess.

## Worker responsibility

The specialist worker must save its deliverable, read it back and verify the observed URL/ID/path, parent/project and version or branch when relevant. A code change is not review-ready without the registered branch plus successful checks; a visual change is not review-ready without a verified preview/staging URL and evidence.

Saving a draft or preparing a branch does not approve publishing, merging or deployment. Keep those gates separate. If no durable artefact is useful, return `artefact_state: not_required` with a reason.

## Orchestrator responsibility

Hermes or the calling orchestrator records the run, evidence, work state, verified artefact reference and next owner in canonical state. It links to the worker artefact rather than recreating it.

## Required handoff

Return `run_result`, `work_state`, `artefact_state`, artefact type, canonical system, observed URL/ID/path, verification evidence, approval required, next owner and next action. Never report `completed` when a required artefact was not saved and verified.
