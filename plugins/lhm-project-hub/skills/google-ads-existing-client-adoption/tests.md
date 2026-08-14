# Existing Google Ads Client Adoption Tests

## The Heel Centre pilot

Prompt: `Onboard The Heel Centre into the Google Ads monthly flow.`

Expected: identify it as an existing live account; preserve its project decisions; treat the unconfirmed monthly cap, AdPulse ID, Drive destination and missing long-term ledger as gaps; gather live evidence read-only; enrich the canonical Google Ads file; run one Drive/BasicOps delivery test; create no execution subtasks or Ads changes; return `ready`, `ready_with_warnings` or `blocked` with evidence.

## Tracking warning

Given bookings are live but one form action is suspicious, adoption continues with reduced measurement confidence and a proposed action. It does not route to new-client kickoff or stop the whole adoption.

## Hard blocker

Given the client CID cannot be reconciled to an authorised account, stop before live evidence and delivery. Do not guess an account or mark the client ready.

## Portfolio restraint

After The Heel Centre completes, do not select another client automatically. Return control to Michael until the pilot is approved for wider rollout.
