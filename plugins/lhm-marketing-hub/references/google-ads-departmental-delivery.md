---
title: Google Ads Departmental Delivery Contract
description: The Lead, worker, QA, Production and Learning Steward loop for approved Google Ads work.
---

# Google Ads Departmental Delivery Contract

Use this contract after a review identifies work, when Michael asks to work through an existing review, or when a specific Google Ads action must be prepared and verified.

## Ownership

- **Google Ads Lead (`google-ads` agent):** owns account judgement, the stable action register, dependencies, sequencing and strategic acceptance.
- **Worker:** Claude or another registered worker executes one bounded action through the named specialist skill. A skill is a procedure, not a persistent department role.
- **Google Ads Delivery QA:** independently checks the returned evidence, artefact, approval boundary and completion claim.
- **Head of Production:** owns the original production brief, durable execution state, cross-department routing and final acceptance against the brief.
- **BasicOps Task Manager:** is the only BasicOps mutation boundary. It is a shared skill, not a manager or source of technical judgement.
- **Learning Steward:** routes verified corrections, friction and decisions to client context, Knowledge, SOPs, skills or capability incidents and defines the next regression.
- **Chief of Staff:** receives only material strategic, commercial, capacity, scope or consequential approval exceptions. Normal accepted delivery bypasses Chief of Staff.

## Non-negotiable sequence

`Production brief → Lead reconciliation → Michael action decision → one worker action → QA → Lead record → next action → Production acceptance → BasicOps handoff → Learning Steward`

Do not dispatch two actions concurrently. Do not expose the next action while the current action is running, awaiting QA, awaiting Michael confirmation or being recorded.

## 1. Accept the production brief

Require the parent ID, objective, client, canonical service-file path, source review/report, BasicOps parent URL, permission ceiling, completion test, available capabilities and next handoff after Production acceptance.

If the run begins directly with Michael, create an internal parent ID and prepare the missing Production fields. Do not fabricate client goals, approvals, owners or destinations.

## 2. Reconcile before recommending

Read canonical client/service context, prior Drive review and implementation artefacts, current BasicOps parent/subtasks and live read-only Ads evidence. Query GA4 when measurement is suspicious.

Classify every relevant prior commitment as exactly one of:

- `verified_complete`
- `complete_unverified`
- `partially_complete`
- `not_started`
- `superseded`
- `cannot_verify`

Do not present `verified_complete` or `superseded` work as a new recommendation. A recurring `not_started` or `partially_complete` item is a delivery failure: preserve its history, owner and missing verification rather than rewriting it as a fresh insight.

## 3. Maintain one action register

Use stable IDs from the source review. If none exist, allocate `GA-01` onward once and preserve them.

```yaml
id: GA-01
title: "Plain action"
evidence: "Observed reason"
expected_outcome: "Observable success"
skill: keyword-optimizer
prior_commitment_state: not_started
dependencies: []
mutation_scope: read_only | prepare_only | approval_required
decision: pending | approved | modified | rejected | deferred
execution_status: not_started | running | qa | waiting_approval | complete | blocked
verification_method: "Exact readback, query or human confirmation"
```

Present no more than five proposed actions. Michael approves, modifies, rejects or defers at action level. Silence, report delivery and BasicOps creation are not approval.

## 4. Dispatch one action

Before dispatch, confirm approval and dependencies, then update the parent to executing and the action to running through BasicOps Task Manager.

```yaml
google_ads_action_dispatch:
  schema_version: 1
  parent_id: "ads-delivery-..."
  action_id: "GA-01"
  objective: "One bounded outcome"
  client_context: "Confirmed facts needed for this action"
  evidence_pack: []
  prior_commitment_state: not_started
  selected_skill: keyword-optimizer
  required_artefacts: []
  mutation_ceiling: prepare_only
  approval_state: approved_for_preparation
  verification_method: "How the result will be checked"
  required_return: "Evidence, artefacts, mutations or none, verification and next dependency"
```

The worker runs only the selected skill slice. It does not choose the next account priority.

## 5. Prepare implementation-ready work

| Action | Required preparation |
|---|---|
| Search terms / negatives | Categorised quoted TXT, one keyword per line; match-scope rationale; converting/valuable-query collision check |
| Keywords / match types | Google Ads Editor CSV plus before/after summary and collision check |
| Campaign / ad groups | Structure sheet, keywords, negatives, settings, naming and Editor-ready file where supported |
| RSA / assets | Final URLs, headlines, descriptions, pinning rationale, policy/AHPRA check and import/paste format |
| Bid / budget | Current and proposed values, economics, capacity/measurement dependencies, monitoring and rollback threshold |
| Conversion tracking | Current/proposed conversion matrix, system owner, exact UI/GTM/GA4 steps and observed verification method |
| Landing-page dependency | Department handoff containing requirement, reason, source campaign, event/URL details and acceptance test |
| PMax | Asset/audience/listing-group changes, excluded waste, evidence and implementation format supported by the owning skill |

Use the safest sufficient negative-keyword scope. Do not blindly decompose every poor query into single-word negatives; single words require evidence that they are categorically irrelevant across the client's valuable traffic.

## 6. QA before advancing

Dispatch the returned action to `google-ads-delivery-qa`. QA does not edit the artefact or rerun specialist analysis.

- `pass`: Lead records the result.
- `correction_required`: return one bounded correction to the same worker, then rerun QA.
- `waiting_approval`: stop at Michael's exact decision or live-mutation gate.
- `needs_evidence`: recover missing evidence without changing the recommendation.
- `blocked`: persist the dependency and return point through Head of Production.

After `pass`, update canonical client context and the BasicOps parent/action before selecting another action.

For manual Google Ads UI work, an implementation pack may pass QA while execution remains `waiting_approval` or `waiting_on_michael`. Mark it complete only after Michael confirms the change and the defined readback verifies it.

## 7. Complete the department handback

When every approved action is `complete`, `deferred`, `rejected` or `blocked` with an owner, return:

```yaml
google_ads_completion_dossier:
  schema_version: 1
  parent_id: "ads-delivery-..."
  client: "Client"
  original_outcome: "Production brief outcome"
  approved_scope: []
  completed_actions: []
  verified_artefacts: []
  mutations_performed: none
  deferred_or_rejected: []
  changed_assumptions: []
  unresolved_dependencies: []
  basicops_url: "verified URL"
  canonical_context_updated: true
  recommended_next_handoff:
    trigger: ready_for_production_acceptance
    owner: Head of Production
    action: "Compare dossier with original brief"
```

Head of Production returns `accepted` or one bounded `production_correction`. It owns formal routing of cross-department work; the Google Ads Lead supplies the technical brief but does not silently create another department's workload.

## 8. Learning Steward closeout

After Production acceptance, send:

```yaml
learning_steward_intake:
  parent_id: "ads-delivery-..."
  outcome_and_evidence: []
  michael_decisions: []
  reviewer_corrections: []
  repeated_manual_steps: []
  stale_or_wrong_recommendations: []
  client_specific_facts: []
  reusable_candidates: []
  capability_friction: []
  proposed_regression: "Next behaviour test"
```

Learning Steward chooses `Applied`, `Promote to Knowledge`, `Update SOP`, `Needs Michael` or `Observe again`. A skill or system change is not `Applied` until the named regression passes.

## State recovery

Persist parent ID, active action, action register, worker run ID, QA verdict, BasicOps URL and next owner after every transition. Resume the active action; never regenerate the review or submit a duplicate worker merely because the conversation or model turn changed.

