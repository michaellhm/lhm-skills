---
name: lhm-cto-source-handoff
description: Repair typed source capability incidents and emit bounded restoration events.
---

# CTO durable handoff

Follow `../../references/source-production-contract.md`. Accept only typed capability incidents with
the saved parent, specialist role and return point. Repair or review the bounded worker/connector
capability; do not retrieve campaign content into Hermes, draft production, deploy, or treat branch
publication as restoration.

Preserve `source_policy: all_required`; capability repair never waives or fabricates a receipt.

After capability verification, emit one `capability_restored` event matching the incident, parent,
role and return point. The resumer owns idempotent consumption. Release, merge and deployment remain
human-authorised operations.
