# Executable source-to-production contract

Hermes submits one exact `all_required` manifest using `/opt/data/profiles/lhm_brain/bin/source-dispatch submit`. Identifiers are accepted only when a root-owned registration with the same run ID contains the exact Drive file, Fathom call and destination. Hermes receives status and content-addressed receipts, never connector credentials or source content.

The host runtime invokes the already authenticated Claude Drive and Fathom adapters, creates SHA-256-bound receipts, and stops before production if any required receipt is absent. Failure persists one parent blocker and invokes the existing `cto-dispatch` work-control path. Only an exact `capability_restored` event resumes the saved role and return point, once. Publication does not imply restoration.

Production receives the verified evidence package through `campaign_playbook_production`. The registered Drive publisher must return the complete published content; byte-equivalent SHA-256 read-back is mandatory before delivery.

The researcher first reads `Local Health Marketing/20 Clients/<Client>/<Client>.md` (Hermes canonical mirror `/home/hermes/.hermes/profiles/lhm_brain/vault/20 Clients/<Client>/<Client>.md`) and parses only its `Systems and files` section. Only when no folder link is recorded may exact-client-name Drive folder search run; exactly one folder must pass ID, name and folder MIME metadata verification before the bridge appends only the verified link. Zero or multiple results emit the existing `waiting_on_capability` incident and resume contract.

Operational logs contain only status, exact IDs, byte counts and SHA-256 hashes. Raw Drive, Fathom and produced content exists only as mode-0640 bounded run artifacts. The four persisted request/result pairs under `references/evidence-bridge` are authoritative; unknown fields fail closed.
