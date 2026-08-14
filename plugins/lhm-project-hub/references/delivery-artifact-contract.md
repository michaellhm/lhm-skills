# Delivery Artefact and Handoff Contract

Apply this contract whenever a project workflow produces or receives material work.

The specialist worker owns its deliverable and must save and verify it in the registered canonical system. Project Hub owns routing and state: Obsidian for client/project decisions and history, BasicOps discussion for human actions and handoffs, and notifications that link to rather than duplicate canonical artefacts.

Before recording completion, require the worker handoff to include `run_result`, `work_state`, `artefact_state`, artefact type, canonical system, observed URL/ID/path, verification evidence, approval required, next owner and next action. A required artefact that was not saved and verified is `needs_review`, not `completed`.

Do not recreate a specialist report, copy deck, audit or implementation in BasicOps. Put actionable context in Discussion and include the verified working URL where useful. If no durable artefact is useful, accept `artefact_state: not_required` with a reason.

Saving internal working material never implies approval to publish, send, merge, deploy or mutate a live advertising/account system.
