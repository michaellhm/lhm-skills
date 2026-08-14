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

Treat missing capabilities as unavailable. Never claim an MCP read or mutation without a successful tool result.

## Delegation

Choose the smallest approved combination of specialist agents and skills that can satisfy the objective. A clear single-domain request may enter its specialist directly. General, ambiguous, or cross-domain work enters the hub orchestrator.

For every child call, pass:
- the parent `request_id`
- a bounded child objective
- relevant confirmed context
- permitted capabilities
- mutation and approval boundaries
- the required return fields

Use installed agent or skill identifiers, not filesystem paths into another plugin. Do not replace a child workflow with an improvised prompt. If an approved target is unavailable, return `ROUTE_UNAVAILABLE` with the missing target.

Run independent read-only children in parallel when supported. Run dependent or mutation-capable work sequentially. Never let a child expand its own permissions.

## Approval

Reads and analysis may proceed within the registered policy. Any external write, send, publish, launch, deployment, budget change, or task mutation must honour the owning skill's approval gate and the host policy. A child recommendation is not approval.

## Handback

Return:
- `request_id`
- `entry_agent`
- `delegations` in execution order
- `skills_used`
- `evidence_sources` with live/saved distinction
- `findings`
- `decisions_or_approvals_needed`
- `mutations` performed or `none`
- `validation_limits`
- `status`: `completed`, `needs_review`, `route_unavailable`, or `failed`

The parent must reconcile child results, identify contradictions, and present one combined handback.
