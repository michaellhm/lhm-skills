---
name: seo-delivery-qa
description: Independently verify one bounded SEO specialist handback before the SEO Lead accepts and advances. Use after keyword research, content-gap analysis, page briefs, SEO writing, content refresh, metadata, technical SEO preparation or an SEO implementation package is returned.
---

# SEO Delivery QA

Read `${CLAUDE_PLUGIN_ROOT}/references/seo-departmental-delivery.md` and apply its evidence, Drive, approval and sequencing rules.

## Inputs

Require parent, action and version IDs; goal hierarchy; bounded objective; accepted input references; selected skill; completion test; permission ceiling; worker handback; returned artefacts; evidence; limitations; mutations or `none`; and Drive readback for every durable output. When the dispatch explicitly declares `required_output.type: non_durable`, require the observed result and explicit persistence rationale instead.

Return `needs_evidence` when the result cannot be judged. Do not recreate evidence, edit the artefact, perform the specialist method or choose the next SEO action.

## Checks

1. **Scope:** work answers only the bounded objective and uses the accepted page or batch scope.
2. **Goal fit:** the result contributes to the department and parent goals without treating the broad goal as extra authority.
3. **Evidence:** material recommendations trace to observed evidence; estimates and assumptions are labelled.
4. **History:** the result respects prior commitments, existing pages and the accepted input version.
5. **SEO quality:** intent, page purpose, keyword use, cannibalisation, internal links, metadata and technical requirements are fit for the artefact type.
6. **Content quality:** when copy is returned, confirm the accepted brief was followed and required long-form routing, brand, evidence, anti-AI and regulated-content rules were observed.
7. **Safety:** no permission expansion, live publication, destructive redirect, indexing change or consequential business decision was performed without authority.
8. **Artefact delivery:** every durable output exists in the dispatched Drive parent; observed ID, URL, name, parent and readback evidence are present. `artefact_state: not_required` passes only when the original dispatch explicitly declared a non-durable output and no reusable file/report/brief/copy/plan/export is required. Missing Drive access or readback is never `not_required`.
9. **Completeness:** every completion-test item has observed evidence. A plausible response is not completion.
10. **Handoff:** result names one exact next owner and does not execute the next production stage.

## Verdict

Return exactly one:

- `pass`
- `correction_required`
- `waiting_approval`
- `needs_evidence`
- `needs_context`
- `waiting_on_capability`
- `failed`

For `correction_required`, state one bounded correction to the same worker. Do not fail merely because another reasonable SEO strategy exists.

## Handback

```yaml
seo_qa_handback:
  schema_version: 1
  parent_id: "stable-parent-id"
  action_id: "SEO-01"
  action_version: 1
  verdict: pass
  checks:
    scope: pass
    goal_fit: pass
    evidence: pass
    history: pass
    seo_quality: pass
    content_quality: pass | not_applicable
    safety: pass
    artefact_delivery: pass
    completeness: pass
    handoff: pass
  material_findings: []
  bounded_correction: null
  verified_artefacts:
    - drive_file_id: "observed-id"
      drive_url: "observed-url"
      drive_parent_id: "observed-parent-id"
      readback: "observed verification"
  approval_gate: null
  next_owner: "SEO Lead"
  next_action: "Accept, persist, read back and only then select the next action"
```

Never mark the parent complete, update production, approve for the human, repair the worker file or dispatch Astro.

When checking a human-approved action, verify the approval record binds the named approver and decision scope to the current parent ID, action ID/version, input digest, artefact ID and artefact version or immutable content digest. Return `waiting_approval` when any material bound value changed. Record the prior approval as superseded; do not reinterpret it as approval of the revision.
