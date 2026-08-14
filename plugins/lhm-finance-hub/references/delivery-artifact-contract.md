# Delivery Artefact and Handoff Contract

Apply this contract whenever a finance skill or agent produces material work.

Use only the configured governed finance destination for workbooks, forecasts, reports and sensitive evidence. Never place financial artefacts into an ordinary client Drive folder, Obsidian note, BasicOps description or notification unless that destination and disclosure are explicitly authorised. Store only minimal state, decisions and non-sensitive references outside the finance system.

The producing worker must save the artefact, read it or its metadata back, verify the observed URL/ID/path and version, then return that reference. If the destination, permission or verification is unavailable, preserve the result in the secure worker handoff, return `needs_review` and identify the blocker. Do not silently fall back to a less protected location.

If no durable artefact is useful, return `artefact_state: not_required` with a reason. Otherwise return `run_result`, `work_state`, `artefact_state`, artefact type, canonical system, observed reference, verification evidence, approval required, next owner and next action. Never report `completed` when a required artefact was not saved and verified.
