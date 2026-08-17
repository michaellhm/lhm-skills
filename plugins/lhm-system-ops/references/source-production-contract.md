# Executable source-to-production contract

Hermes submits one exact `all_required` manifest using `/opt/data/profiles/lhm_brain/bin/source-dispatch submit`. Identifiers are accepted only when a root-owned registration with the same run ID contains the exact Drive file, Fathom call and destination. Hermes receives status and content-addressed receipts, never connector credentials or source content.

The host runtime invokes the already authenticated Claude Drive and Fathom adapters, creates SHA-256-bound receipts, and stops before production if any required receipt is absent. Failure persists one parent blocker and invokes the existing `cto-dispatch` work-control path. Only an exact `capability_restored` event resumes the saved role and return point, once. Publication does not imply restoration.

Production receives the verified evidence package through `campaign_playbook_production`. The registered Drive publisher must return the complete published content; byte-equivalent SHA-256 read-back is mandatory before delivery.
