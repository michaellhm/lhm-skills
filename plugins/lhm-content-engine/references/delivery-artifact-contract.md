# Delivery Artefact and Handoff Contract

Apply this contract whenever a skill or agent produces material work for a client or LHM.

Read canonical client/project state and use its exact registered destination. Reports, briefs, copy and client-facing files belong in the registered Drive folder; state and run history belong in Obsidian; publishing belongs in its approved CMS/Google Docs destination; human actions belong in BasicOps discussion.

The producing worker must save the deliverable, read it or its metadata back, verify the observed URL/ID and parent, then return that reference. Saving a draft does not approve client sending or publishing. If publishing is blocked, preserve the reviewed draft in the approved fallback destination and return `needs_review`; do not silently use an arbitrary local folder.

If no durable artefact is useful, return `artefact_state: not_required` with a reason. Otherwise return `run_result`, `work_state`, `artefact_state`, artefact type, canonical system, observed URL/ID/path, verification evidence, approval required, next owner and next action. Never report `completed` when a required artefact was not saved and verified.

Hermes or the calling orchestrator records and links the verified worker artefact in canonical state. It does not recreate the deliverable.
