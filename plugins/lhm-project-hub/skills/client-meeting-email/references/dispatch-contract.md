# Client meeting capture dispatch contract

The dispatcher accepts only versioned, typed jobs. It never accepts arbitrary
paths, commands or prompts.

## Request

- `workflow_id`: `client_meeting_capture`
- `workflow_version`: `1`
- `run_id`: unique safe identifier
- `worker_route`: `codex`
- `client_id`: registered client ID
- `meeting_locator`: exactly one of a Fathom call URL/ID or bounded date/title hints
- `founder_context`: transcript, inclusions, exclusions and internal-only notes
- `requested_outputs`: email, meeting record, proposed state updates and delegation pack flags
- `permissions`: Fathom/client reads and artifact staging only during preparation
- `approval_stage`: `review_only`
- `success_test`: bounded list
- `timeout_seconds`: host-profile bounded

The host resolves `client_id` through its root-owned registry. The request cannot
supply a filesystem path.

## Response

The worker returns the strict schema in `output-schema.json`. The dispatcher
calculates the authoritative `content_hash` over the canonical JSON of
`email_draft`, `meeting_record`, and `proposed_mutations` after validating the
response. Any edit changes the hash and invalidates approval.

Preparation always ends at `needs_review`. It never creates a draft or writes a
file. Later vault and Gmail operations must cite the exact `run_id`, workflow
version and content hash they apply.

## Idempotency and conflicts

- Artifact idempotency key: `client_id + Fathom call ID + artifact type`.
- Proposed mutations carry an expected prior SHA-256; application fails closed
  when it no longer matches.
- A new file may use `expected_sha256: null` only beneath an allowlisted existing
  client root and only when that path does not exist.
- The worker never proposes or creates a client root.
- Fathom ambiguity, missing connector access or a client-registry miss stops the
  run with an actionable question; the system does not infer from stale vault data.
