# Agent orchestration contract

Use this contract whenever an agent receives work from Hermes or delegates to another plugin agent or skill.

## Context intake

Accept a preloaded context envelope when supplied. Do not repeat discovery questions for confirmed fields.

Required fields:
- `request_id`
- `objective`
- `client_id` or explicit `null`
- `known_context` containing confirmed facts only
- `constraints`
- `approval_state`
- `available_capabilities`
- `requested_output`

Existing envelopes that satisfy the fields above remain valid. New staged departmental envelopes should additionally supply:
- `parent_goal` (the durable business outcome)
- `department_goal` (the department's contribution to that outcome)

For staged departmental work, also accept when supplied:
- `action_id` and a stable idempotency key
- `accepted_inputs` containing only upstream artefacts already accepted by the owning Lead
- `delivery_destinations`, including the exact registered Google Drive folder ID and URL for file-producing work
- `completion_test`
- `return_to` and the durable resume point

Treat missing capabilities as unavailable. Never claim an MCP read or mutation without a successful tool result.

## Delegation

Choose the smallest approved combination of specialist agents and skills that can satisfy the objective. A clear single-domain request may enter its specialist directly. General, ambiguous, or cross-domain work enters the hub orchestrator.

Departmental Leads must dispatch exactly one bounded, dependency-ready action at a time. Do not combine research, briefing, writing, QA and implementation into one child prompt. Receive the child artefact, validate it, persist and read back the acceptance checkpoint, and only then select or dispatch the next action. The specialist owns its professional method; the Lead supplies the goal, bounded objective, accepted inputs, authority boundary, output contract and completion test without micromanaging the method.

For every child call, pass:
- the parent `request_id`
- a bounded child objective
- the unchanged parent goal and relevant department goal
- the child `action_id`
- relevant confirmed context
- accepted upstream artefact references (not a reconstructed summary when the artefacts are available)
- permitted capabilities
- mutation and approval boundaries
- the required return fields
- the exact registered delivery destination for any durable artefact

Use installed agent or skill identifiers, not filesystem paths into another plugin. Do not replace a child workflow with an improvised prompt. If an approved target is unavailable, use canonical departmental state `waiting_on_capability` with the missing target and resume point.

An unavailable specialist capability is not permission for a Lead to perform the specialist work itself. Return the required capability, expected output contract and resume point so the same parent can continue once the route is restored.

### Customer-facing copy boundary

When a child finding requires new or materially revised customer-facing copy, the originating Lead must return an accepted `content_brief` under `content-departmental-delivery.md`. Do not pass audit suggestions, candidate headlines or a strategy report directly to a developer or publisher.

Content Lead returns a verified `implementation_ready_copy` artefact after writing and independent editorial QA. Head of Production may dispatch implementation only when that artefact contains one selected replacement per field and its approval state is `approved_for_implementation`. A `review_ready` variant set remains a human decision, not executable work.

Outside a staged Lead action register, independent read-only children may run in parallel when supported. Within any staged departmental Lead loop, never dispatch multiple register actions in parallel, even when they appear read-only: dispatch exactly the first dependency-ready action, accept and persist it, then select again. Run dependent or mutation-capable work sequentially. Never let a child expand its own permissions.

## Approval

Reads and analysis may proceed within the registered policy. Any external write, send, publish, launch, deployment, budget change, or task mutation must honour the owning skill's approval gate and the host policy. A child recommendation is not approval.

## Handback

For staged departmental work, use the canonical `state` vocabulary defined by the owning departmental-delivery contract. The shared canonical states are `planned`, `ready`, `worker_running`, `qa`, `correction_required`, `waiting_on_dependency`, `waiting_on_capacity`, `needs_context`, `needs_approval`, `waiting_on_capability`, `review_ready`, `completed`, `failed` and `stopped`.

Legacy callers may still require the older `status` field. Project canonical state into it without changing the durable state:

| Canonical `state` | Legacy `status` |
|---|---|
| `completed` | `completed` |
| `needs_context`, `needs_approval`, `correction_required`, `waiting_on_dependency`, `waiting_on_capacity`, `review_ready` | `needs_review` |
| `waiting_on_capability` | `route_unavailable` |
| `failed`, `stopped` | `failed` |
| `planned`, `ready`, `worker_running`, `qa` | `needs_review` |

Return canonical `state` whenever a departmental contract applies. Include legacy `status` only when the caller/schema needs backward compatibility. Never use legacy `needs_review` as the durable reason; retain the precise canonical state and resume point.

Return:
- `request_id`
- `parent_goal`, `department_goal`, and `action_id` when supplied
- `entry_agent`
- `delegations` in execution order
- `skills_used`
- `evidence_sources` with live/saved distinction
- `findings`
- `decisions_or_approvals_needed`
- `mutations` performed or `none`
- `validation_limits`
- canonical `state` for departmental work; compatibility `status`: `completed`, `needs_review`, `route_unavailable`, or `failed` when required

The parent must reconcile child results, identify contradictions, and present one combined handback.
