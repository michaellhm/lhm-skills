---
name: multi-stage-delivery-brief
description: Convert a rough LHM request that spans two or more delivery roles or systems into one approved, resumable execution plan before specialist work begins. Use for cross-domain outcomes such as analysis followed by content, website implementation, QA and human review. Do not use for a single governed personal-operation or one-role task.
---

# Multi-Stage Delivery Brief

Create one enforceable parent workflow from an outcome-based request. Planning is not delivery: no specialist worker, external mutation or implementation may begin until the plan reaches its required approval state.

## Entry test

Use this workflow when the request requires at least two of: research, a delivery-domain specialist, an external worker, an artefact handoff, QA, project-state mutation or human review. Route a single human task through `team-work-brief`; route a single specialist read through its domain workflow.

## Build the parent plan

Resolve from conversation and canonical context:

- requester, subject/client, intended business outcome and completion condition;
- canonical project/goal and the human review owner;
- stages in dependency order, with one accountable role per stage;
- required inputs, evidence, artefact output and acceptance test for each stage;
- approval boundary, permission ceiling and explicitly excluded mutations;
- operational destination for the parent plan and final review action;
- stable parent ID and deduplication key.

Represent every stage with: `stage_id`, `owner_role`, `state`, `depends_on`, `inputs`, `output_contract`, `acceptance_test`, `permission_ceiling`, `return_point` and `next_owner`. Initial stage states are `planned` or `waiting_on_dependency`; none is `ready_to_dispatch` before approval.

## Separate evidence states

Label inputs as `live_verified`, `dated_canonical`, `unverified` or `missing`. A missing live capability becomes a dependency stage or CTO incident; it does not silently turn dated evidence into current evidence and does not prevent independent planning.

## Present the approval bundle

Show one compact plan containing:

- outcome and completion condition;
- ordered stages, roles and observable outputs;
- known dependencies and evidence gaps;
- proposed BasicOps parent/review structure;
- consequential approvals and safe reversible work;
- what will remain unchanged;
- final reviewer and handback.

Ask the requester to approve or amend this exact plan. Before approval, BasicOps may receive only an explicitly approved planning record; do not create execution subtasks or dispatch specialists.

## Persist through Project Manager

After approval, hand the complete plan to the Project Manager. It routes any authorised BasicOps write through `basicops-task-manager`, verifies the resulting parent URL and returns the parent ID plus approved plan to Head of Production. Keep AI worker children in machine state; BasicOps contains meaningful human/project gates, not internal bot activity.

## Execute through Production

Head of Production converts approved stages into the dependency graph and routes domain judgment to the matching persistent specialist bot. A downstream stage can become `ready_to_dispatch` only when every dependency output exists and passes its acceptance test.

For every handoff preserve parent ID, stage ID, evidence/artefact references, permission ceiling, idempotency key, acceptance test, next owner, return point and resume token. A capability failure creates a linked CTO child and leaves the business parent resumable. A verified repair resumes the first incomplete stage automatically.

## Review and completion

After implementation, require independent or domain QA appropriate to the risk. A technical branch, request ID or claimed preview is not completion. Project Manager creates or updates the final human review action only after the review bundle contains the verified artefacts, tests, branch/preview where applicable, material risks and exact approval requested.

Chief of Staff returns one consolidated result. Close only when the original completion condition is verified or the parent is durably awaiting a genuinely consequential human decision.

## Required invariants

- One parent ID across the entire workflow.
- No specialist execution before plan approval.
- No downstream dispatch before its artefact gate passes.
- No invented owner, deadline, identifier, access or destination.
- No production merge, deploy, publish, external send, spend or account mutation without its own authority.
- No “ask Michael to resume” for ordinary waits or repaired capabilities.
- BasicOps and Obsidian writes use their existing governed mutation boundaries and are read back.
