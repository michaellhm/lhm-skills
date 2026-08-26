---
name: lhm-head-of-production-source-handoff
description: Produce from verified source packages and require shared Google Drive delivery with exact readback before completion.
---
# Head of Production source handoff
Accept only the SHA-256-bound evidence package reported by `source-dispatch`. The host runtime dispatches the selected producer and the registered `google-drive-file-publish` route; do not reconstruct either inside Hermes.

For every file-producing child, require an explicit manifest and `delivery_required` or an approved task-specific `artefact_state: not_required`. After producer QA passes, invoke `lhm-project-hub:drive-artifact-delivery`. Treat every VPS, container, local-worker and Kanban path as staging only. Completion requires every retrieval receipt, production child, Drive file/parent/name/byte/content-hash readback receipt and independent final QA. A missing or failed delivery returns `waiting_on_capability` to this role with the original parent and exact delivery return point; route the bounded publisher incident to CTO and resume automatically after verified repair.
