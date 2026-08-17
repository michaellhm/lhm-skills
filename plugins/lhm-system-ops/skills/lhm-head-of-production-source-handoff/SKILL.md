---
name: lhm-head-of-production-source-handoff
description: Produce and publish only from verified source packages.
---
# Head of Production source handoff
Accept only the SHA-256-bound evidence package reported by `source-dispatch`. The host runtime dispatches `campaign_playbook_production` and `registered_google_drive_publisher`; do not reconstruct either inside Hermes. Completion requires every required retrieval receipt, a production child, and a full-content Drive read-back digest equal to the published digest.
