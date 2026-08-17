---
name: lhm-head-of-production-source-handoff
description: Produce from a complete evidence package and verify registered Drive delivery.
---

# Head of Production durable handoff

Follow `../../references/source-production-contract.md`. Reject work without a validated evidence
package containing verified receipts for every required source. Invoke only the packaged skill/worker
selected by the manifest. Publish only through `registered_google_drive_publisher` to the manifest's
allowlisted destination.

Treat `source_policy: all_required` as fail-closed and immutable throughout production.

Require full-content read-back and equal published/read-back digests before reporting delivery.
Report BasicOps separately and route any mutation through `lhm-project-hub:basicops-task-manager`;
never use direct credentials or claim delivery from a task update.
