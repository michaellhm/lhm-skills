---
name: google-ads-delivery-qa
description: Verify a bounded Google Ads action before the Google Ads Lead advances. Use after a worker returns keyword, negative, RSA, bid/budget, PMax, landing-page, conversion-tracking or implementation-pack work; when checking whether evidence supports the recommendation; or when Head of Production needs an action-level QA verdict.
---

# Google Ads Delivery QA

Read `${CLAUDE_PLUGIN_ROOT}/references/google-ads-departmental-delivery.md` and apply its approval and evidence rules.

## Inputs

Require the parent and action IDs, bounded objective, expected outcome, source windows, evidence references, worker skill, returned artefacts, approval ceiling, mutations performed or `none`, worker verification and relevant prior-commitment state.

Return `needs_evidence` when a required input is absent. Do not reconstruct missing evidence or rerun the specialist task inside QA.

## Check

1. **Scope:** the worker answered only the dispatched action and did not expand permissions.
2. **Evidence:** every material recommendation is traceable to observed, date-bounded evidence. Flag irreproducible figures and conflicts with canonical context.
3. **History:** the action is not stale, already complete or contradicted by a prior commitment. Describe partial implementation as partial.
4. **Strategy:** the proposed change supports the stated business outcome and does not optimise a distorted conversion definition.
5. **Safety:** approval boundaries were observed. A prepared file is not permission for a live mutation.
6. **Artefact:** the output is implementation-ready for its type:
   - negatives are reviewed against converting and strategically important queries, use the safest sufficient match scope and are delivered quoted one per line;
   - Editor CSVs use valid headers and represent the intended before/after state;
   - RSAs meet platform, policy, client-positioning and AHPRA constraints;
   - budget/bid recommendations state current value, proposed value, rationale and measurement/capacity dependency;
   - tracking work states the current definition, proposed definition, systems affected and verification event/query;
   - landing-page dependencies state the owning department, exact requirement and acceptance test.
7. **Verification:** completion is supported by live readback, an observed artefact readback, or explicit human confirmation for a manual UI action. Instructions alone are not completion.
8. **Next state:** the result has one exact next owner, action and handoff trigger.

## Verdict

Return exactly one:

- `pass` — evidence and artefacts satisfy the action contract; the Lead may record the outcome.
- `correction_required` — return one bounded correction to the same worker.
- `waiting_approval` — evidence is sufficient but a consequential decision or live mutation still requires approval.
- `needs_evidence` — the result cannot be judged from the returned evidence.
- `blocked` — an external dependency or missing capability prevents completion.

Do not issue a second opinion merely because another strategy is possible. Fail only for a material evidence, scope, safety, artefact or completion defect.

## Handback

```yaml
google_ads_qa_handback:
  schema_version: 1
  parent_id: "ads-delivery-..."
  action_id: "GA-01"
  verdict: pass | correction_required | waiting_approval | needs_evidence | blocked
  checks:
    scope: pass | fail
    evidence: pass | fail
    history: pass | fail
    strategy: pass | fail
    safety: pass | fail
    artefact: pass | fail
    verification: pass | fail
    handoff: pass | fail
  material_findings: []
  bounded_correction: null
  verified_artefacts: []
  mutations_verified: none
  next_owner: "Google Ads Lead"
  next_action: "Record accepted outcome and select the next approved action"
```

Never change the Ads account, edit the worker artefact, approve strategy for Michael or mark the parent complete.
