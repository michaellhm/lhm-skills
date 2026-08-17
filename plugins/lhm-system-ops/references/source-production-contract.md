# Durable source-to-production contract

One request has one durable parent. Its manifest saves `parent_run_id`, current specialist role,
exact return point, `source_policy: all_required`, required source declarations, packaged production
worker, registered publisher and per-run allowlisted identifiers. Client names and identifiers belong
only in per-run manifests, never in the engine or persisted role instructions.

Hermes is an unprivileged orchestrator. It may create the manifest, inspect redacted receipts and
resume roles. It must never receive credential files, raw tokens, SSH, Docker, unrestricted file
access, arbitrary Drive identifiers or direct BasicOps mutation authority. Retrieval runs through the
bounded Claude research worker, which accepts only `google_drive_file` and `fathom_transcript`
declarations already allowlisted in the manifest. It returns content digests and verified retrieval
receipts; secrets and connector credentials remain outside Hermes.

Every required source must have a verified, identifier-bound receipt before evidence packaging,
drafting, completion or production. Unavailable retrieval creates a typed capability blocker, persists
the parent and routes the incident to `lhm-cto`. A matching `capability_restored` event is consumed
once and resumes the saved parent, role and return point. Publication alone is not restoration.

Head of Production accepts only a validated evidence package and invokes the manifest's selected
packaged skill/worker. Delivery uses `registered_google_drive_publisher` and succeeds only when a
full-content read-back digest equals the published-content digest. BasicOps is a separate handoff
through `lhm-project-hub:basicops-task-manager`; its failure cannot invalidate or fabricate delivery.

Chief of Staff owns the outcome but cannot substitute for specialist work. Context and Research owns
source acquisition and evidence validation. CTO owns capability incidents, not campaign drafting.
Head of Production owns packaged production and verified publishing. Every role fails closed under
`all_required` and preserves the same parent and handoff fields.
