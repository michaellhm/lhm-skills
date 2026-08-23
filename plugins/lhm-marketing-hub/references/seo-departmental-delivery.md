---
title: SEO Departmental Delivery Contract
description: The reusable Lead, specialist, QA, Production and persistence loop for bounded SEO delivery.
---

# SEO Departmental Delivery Contract

Use this contract for LHM and client SEO work. Pilot it on the LHM website rollout without embedding LHM-specific paths, owners or strategy in the reusable workflow.

## Ownership

- **Head of Production:** owns the parent goal, durable machine state, cross-department sequence, BasicOps parent and final acceptance.
- **SEO Lead (`start-seo`):** owns SEO judgement, the department goal, dynamic action register, dependencies, specialist selection and acceptance of QA-passed work.
- **SEO specialist:** uses one selected marketplace skill to produce one bounded outcome. The specialist owns its professional method.
- **SEO Delivery QA:** independently verifies the returned work. It does not repair the artefact or perform the specialist action.
- **Astro Lead:** receives only an accepted SEO implementation package through Head of Production.
- **BasicOps Task Manager:** is the only BasicOps mutation boundary.
- **Human approver:** owns consequential business decisions and production release authority.

## Goal hierarchy

Every dispatch carries all three levels:

1. `parent_goal`: the business result that remains stable across departments.
2. `department_goal`: SEO's contribution to the parent goal.
3. `objective`: the single observable result required from this invocation.

The completion test proves the objective. A broad goal does not authorise the worker to complete later actions.

## Non-negotiable invariant

`Select one ready action -> dispatch one specialist -> receive artefact -> independent QA -> Lead accepts -> persist -> read back -> select next action`

Do not dispatch dependent actions together. Research, briefs, writing, QA and implementation are separate invocations. Do not reveal a later action to a running worker as an invitation to continue. One bounded action may produce a coherent batch when the action contract explicitly defines the batch, but the Lead must consider worker capacity and should default to one page at a time for long-form content.

The specialist receives the accepted upstream artefact, not an orchestration summary that discards evidence.

## Production envelope

Head of Production supplies:

```yaml
seo_production_envelope:
  schema_version: 1
  parent_id: "stable-parent-id"
  dedupe_key: "client:seo:programme:wave"
  client:
    id: "canonical-client-id"
    name: "Verified client name"
  parent_goal: "Business result"
  department_goal: "Accepted SEO contribution"
  canonical_context:
    client_root: "Observed Obsidian client root"
    project_state: "Observed human-readable state path"
  accepted_context_pack: "Observed path or record ID"
  delivery_destinations:
    google_drive:
      folder_id: "Observed folder ID"
      folder_url: "Observed folder URL"
      source_record: "Where the destination was verified"
      relative_root: "seo"
    obsidian:
      project_root: "Observed project root"
    basicops:
      task_id: "Observed parent ID or null"
      task_url: "Observed URL or null"
  permission_ceiling: "research_and_prepare"
  completion_test: []
  available_capabilities: []
  production_return: "Head of Production"
```

Do not infer a Drive folder from a client name or from Claude Desktop's selected working folder. If `folder_id` is missing for a file-producing action, return `needs_context` with an exact owner and resume point.

## Reconcile and build a dynamic action register

Read the accepted context pack, canonical project state, prior accepted artefacts, existing BasicOps parent and current read-only evidence. Classify prior work as `verified_complete`, `complete_unverified`, `partially_complete`, `not_started`, `superseded` or `cannot_verify`.

Build only the actions needed to achieve the department goal. Do not impose a universal SEO checklist. Allocate stable IDs such as `SEO-01` and preserve them across resumes.

```yaml
- id: SEO-01
  title: "One plain action"
  objective: "One bounded result"
  required_output: "Observable artefact or decision"
  candidate_capability: "keyword_research"
  selected_skill: null
  accepted_inputs: []
  dependencies: []
  prior_state: not_started
  permission_ceiling: read_only
  execution_status: ready
  input_digest: "stable digest"
  version: 1
  completion_test: []
```

Existing accepted artefacts may satisfy an action when their source, version, scope, verification and input digest still match. Do not rerun them because a new cron wake or model turn began.

### Canonical state vocabulary

Use these canonical values in new machine state, action registers, QA handbacks and BasicOps milestone updates:

- Parent/workflow: `planned`, `ready`, `worker_running`, `qa`, `correction_required`, `waiting_on_dependency`, `waiting_on_capacity`, `needs_context`, `needs_approval`, `waiting_on_capability`, `review_ready`, `completed`, `failed`, `stopped`.
- Action execution: `waiting`, `ready`, `worker_running`, `qa`, `correction_required`, `accepted`, `cancelled`, `obsolete`, `failed`.
- Prior-work reconciliation: `verified_complete`, `complete_unverified`, `partially_complete`, `not_started`, `superseded`, `cannot_verify`.
- QA verdict: `pass`, `correction_required`, `waiting_approval`, `needs_evidence`, `needs_context`, `waiting_on_capability`, `failed`.

Legacy values are input aliases only. Normalise them before persistence or comparison:

| Legacy value | Canonical value |
|---|---|
| `running`, `in_progress` | `worker_running` |
| `awaiting_qa`, `verifying`, `testing` | `qa` |
| `needs_review`, `review_pending` | `review_ready` when the work is complete and awaits ordinary review; `needs_approval` when a named consequential decision is required |
| `waiting_approval` | `needs_approval` at parent/action level; retain `waiting_approval` only as the QA verdict |
| `needs_more_research`, `needs_evidence` | `needs_context` at parent/action level; retain `needs_evidence` only as the QA verdict |
| `blocked` | Do not map mechanically. Classify from evidence as `waiting_on_dependency`, `waiting_on_capacity`, `needs_context`, `needs_approval`, `waiting_on_capability` or `failed`; retain `blocked` only in imported history |
| `closed`, `done`, `accepted` (parent) | `completed` only after the parent completion test and required readbacks pass |

Never use reconciliation classifications as execution states. Preserve the observed legacy value in migration evidence, but write only the canonical value to current state.

## Capability-based skill selection

Select the best installed specialist by capability, inputs, output contract and authority. Soft routing examples include:

| Required capability | Skills to consider |
|---|---|
| Keyword and intent evidence | `keyword-research` |
| Content opportunity gaps | `content-gap-analysis` |
| Page briefs | `seo-page-brief` |
| New page content | `seo-content-writer` |
| Existing page improvement | `content-refresher` |
| Technical diagnosis | `seo-audit` or the applicable technical skill |
| Independent department QA | `seo-delivery-qa` |

These are candidates, not a rigid sequence. Let the specialist skill own method. The Lead supplies the goal, bounded objective, accepted evidence, permissions, required output and completion test.

If no installed skill can satisfy the action, return `waiting_on_capability`. Do not let the Lead silently perform specialist work.

## Action dispatch and handback

```yaml
seo_action_dispatch:
  schema_version: 1
  parent_id: "stable-parent-id"
  action_id: "SEO-01"
  action_version: 1
  parent_goal: "Business result"
  department_goal: "SEO result"
  objective: "One bounded outcome"
  accepted_inputs: []
  selected_skill: "keyword-research"
  constraints: []
  permission_ceiling: "read_only"
  required_output:
    type: markdown
    filename: "keyword-research-topic.md"
    drive_parent_id: "observed-folder-id"
    drive_relative_path: "seo/YYYY-MM/"
    obsidian_path: "observed project path"
  completion_test: []
  return_to: "SEO Lead"
```

The producing specialist must follow the delivery artefact contract: save to the registered Drive destination, read it or its metadata back, verify the observed parent and return the file ID and URL. The canonical Obsidian file holds state, decisions and run history; do not treat an unregistered local draft as delivery.

```yaml
seo_worker_handback:
  schema_version: 1
  parent_id: "stable-parent-id"
  action_id: "SEO-01"
  action_version: 1
  run_result: succeeded
  work_state: completed
  artefact_state: verified
  artefacts:
    - type: markdown
      drive_file_id: "observed-id"
      drive_url: "observed-url"
      drive_parent_id: "observed-parent-id"
      obsidian_path: "observed-state-or-project-path"
      version: 1
      readback_evidence: "Observed name, parent and content/metadata"
  evidence: []
  limitations: []
  mutations: none
  approval_required: false
  next_owner: "SEO Delivery QA"
```

`artefact_state` is `verified` for every durable output. `artefact_state: not_required` is allowed only when the dispatch explicitly declares `required_output.type: non_durable` and its completion test requires no file, report, brief, copy, plan, export or other reusable artefact. The handback must then include the observed non-durable result and why persistence is not required. A worker may not use `not_required` because Drive access or readback failed.

## QA, acceptance and corrections

Every specialist handback goes to `seo-delivery-qa`. The Lead advances only after `pass`.

- `pass`: Lead may accept and record the action.
- `correction_required`: return one bounded correction to the same specialist and rerun QA.
- `waiting_approval`: persist the exact decision and version requiring approval.
- `needs_evidence`: recover the missing evidence without rewriting the recommendation.
- `needs_context`: route the missing canonical fact to Context & Research.
- `waiting_on_capability`: preserve the return point for capability recovery.
- `failed`: preserve the last accepted checkpoint and recovery evidence.

The Lead records an explicit `accepted` decision. A successful worker invocation and a QA pass are not themselves persistence.

## Transactional checkpoint

After acceptance:

1. Write machine state with parent, action, version, input digest, run ID, QA verdict, verified artefacts and next owner.
2. Read back and validate that checkpoint.
3. Update the human-readable project state when the milestone is material, then read it back.
4. Update the single BasicOps parent through BasicOps Task Manager.
5. Only then select another action.

If any required write or readback fails, do not advance or claim completion. Resume at the failed persistence step.

Use the canonical state vocabulary above. Reserve `blocked` for imported history describing a genuine external condition with no authorised next action; classify every active workflow into a canonical resumable or terminal state.

## One BasicOps parent

Use one parent for the delivery outcome. Do not create a subtask for each skill call. If the production envelope has `delivery_destinations.basicops.task_id: null`, SEO Lead must return a `basicops_parent_create_required` request to Head of Production. Head of Production sends it through BasicOps Task Manager using the parent dedupe key, intended outcome, milestone list, ordered actions, completion condition and final `Next handoff:` block. SEO execution pauses at `waiting_on_dependency` with return point `reconcile_basicops_parent`; it does not create the task directly. Resume only after BasicOps Task Manager returns the observed task ID and URL and Head of Production reads the parent back and places those verified values in the production envelope. A duplicate wake must search by the same dedupe key and reuse the verified parent.

When a verified parent exists, its discussion contains short blocks for:

- intended outcome and goal;
- milestone checklist;
- ordered actions with department, selected skill and status;
- accepted Drive artefact links;
- dependencies, approvals and completion condition;
- a final `Next handoff:` block.

Update only at meaningful checkpoints: plan established, department artefact accepted, correction or approval required, cross-department handoff, or verified completion.

## Approval boundaries

SEO Lead may accept routine research, briefs, copy, recommendations, QA and preparation that stay within approved scope and do not mutate production.

Require named human approval for consequential positioning, offers, pricing, guarantees, regulated claims, market priority, destructive consolidation, unresolved brand decisions or scope expansion. Approval belongs to an exact artefact version.

Persist approval as a bound record containing `approval_id`, named approver, decision, scope, parent ID, action ID, action version, input digest, artefact ID, artefact version or immutable content digest, and approval timestamp. Resume only when all bound values match the current action and observed artefact. Any material change to the approved copy, claims, offer, route, scope, accepted inputs or artefact digest invalidates the approval, returns the action to `needs_approval`, records the superseded approval ID and requires a new approval. Formatting-only changes may retain approval only when QA proves the immutable semantic/content digest and approved scope are unchanged.

Require production authority for merge, deploy, publish, redirects, indexing/canonical changes, indexing requests, client communications and consequential live marketing changes. Preparation and noindex preview do not grant production authority.

## Astro handoff

After all SEO actions are accepted, return an implementation package to Head of Production. Head of Production, not SEO Lead, formally dispatches Astro Lead.

```yaml
seo_completion_dossier:
  schema_version: 1
  parent_id: "stable-parent-id"
  parent_goal: "Business result"
  department_goal: "Accepted SEO result"
  completed_actions: []
  verified_drive_artefacts: []
  page_routes: []
  internal_link_requirements: []
  metadata_and_schema_requirements: []
  changed_assumptions: []
  unresolved_dependencies: []
  permission_ceiling_observed: true
  basicops_url: "observed-url"
  recommended_next_handoff:
    trigger: ready_for_astro
    owner: "Head of Production"
    action: "Accept the SEO dossier and dispatch Astro Lead"
```

Head of Production accepts the dossier against the original brief or returns one bounded production correction. Astro implementation, website QA and a noindex preview remain separate staged actions.

## Resumption and reconciliation

Use stable parent and action dedupe keys. Before dispatch, check for an accepted action with matching version, input digest, verified Drive artefact and QA verdict. Resume the first incomplete transition, not the beginning of the SEO analysis.

On every wake, reconcile machine state, Drive artefacts, the BasicOps parent and human-readable project state. Repair stale representations from verified acceptance evidence. Never trust a completion claim when Drive or state readback fails.
