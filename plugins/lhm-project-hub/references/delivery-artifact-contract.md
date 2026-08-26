# Delivery Artefact and Handoff Contract

Apply this contract whenever a project workflow produces or receives material work.

The specialist worker owns producing the deliverable in its registered staging boundary. Head of Production owns durable delivery. For client files, invoke `lhm-project-hub:drive-artifact-delivery` through the registered publisher after producer QA and before final verification. Project Hub owns routing and state: Obsidian for client/project decisions and history, BasicOps discussion for human actions and handoffs, and notifications that link to rather than duplicate canonical artefacts.

Before recording completion, require the handoff to include `run_result`, `work_state`, `artefact_state`, artefact type, canonical system, observed URL/ID/path, verification evidence, approval required, next owner and next action. A required client artefact is `delivered` only when its registered Drive receipt proves exact file ID, parent folder ID, file name, byte count and content SHA-256 through readback. Otherwise it is `delivery_incomplete`, never `completed`.

A VPS path, `/tmp` file, Hermes workspace, container path, log, BasicOps attachment or Kanban file is staging only. It must never satisfy a client delivery requirement or appear as the only artefact link in a completion handback.

Each file-producing plan and worker handoff must declare either `delivery_required`, with the exact registered canonical destination and expected manifest, or `artefact_state: not_required`, with a task-specific reason accepted in the approved plan.

Do not allow a leaf skill to implement ad hoc Drive logic. The shared delivery skill owns exact-name duplicate handling, bounded file creation and readback. Missing or broken Drive delivery routes to client onboarding or CTO while preserving the production return point.

Do not recreate a specialist report, copy deck, audit or implementation in BasicOps. Put actionable context in Discussion and include the verified Drive working URL. If no durable artefact is useful, accept `artefact_state: not_required` only with the approved task-specific reason.

Saving internal working material never implies approval to publish, send, merge, deploy or mutate a live advertising/account system.
