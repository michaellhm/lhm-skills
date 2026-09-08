# Google Ads portfolio continuation checkpoint — recorded role passes

Incident: `cap-gads-continuation-checkpoint-20260908`  
Parent: `ads-cycle-2026-09-07-week-2`  
Return point: `head_of_production`  
Base: `8f16d06`

## Capability Researcher

Passed. The canonical `lhm-system-ops` work-resumer, authoritative work-control store, Hermes
handoff, path unit and existing Head of Production checkpoint contract are the native capability.
No provider, third-party plugin or permission expansion is required. The defect was that one
Hermes subprocess received the entire 1800-second service budget and a nonterminal response could
not record a continuation ID, child receipts, active child, remaining clients or next wake.

The isolated process namespace showed no active Hermes, Claude, Google Ads or work-resumer child;
therefore this change issued no retry. Live reconciliation remains an activation-time readback.

## Platform Engineer

Passed. Agent receipts are now closed schema version 2. Each invocation must reconcile an active
child before dispatch, must not repeat completed child receipts, and may process at most the first
remaining portfolio child. Every nonterminal receipt requires a unique continuation ID, UTC next
wake, cumulative child receipts, active-child state and remaining clients. The resumer persists the
checkpoint and atomically queues a typed `work_continuation` event. `main()` snapshots the incoming
queue so the next event receives a fresh service invocation and fresh 1800-second budget.

The continuation event is SHA-256 bound to parent, original resume token and continuation ID. Its
parent must already be `continued` and carry the same continuation ID. Completed results cannot
retain an active child, continuation ID, next wake or remaining work.

## QA Tester

Passed in repository fixtures. Regression coverage proves the Alpha receipt set survives, the
known EHP run `claude-gads-20260908-03` is carried as `reconcile`, a next wake is durable, restart
consumes only that wake, cumulative receipts remain intact, and completion leaves no queued wake.
The existing duplicate, refusal, invalid digest, traversal, symlink, interrupted apply, false-marker
and success-marker recovery tests remain passing. No fixture invokes live Hermes, Drive, BasicOps
or Ads.

## Security and Reliability Reviewer

Passed for publication. The worker remains uid/gid 10000, sees only the per-event handoff, and
receives no credentials or canonical-store access. The service retains its existing single
authoritative `ReadWritePaths` boundary and lock. Closed schemas reject unsafe identifiers, stale
parent/continuation bindings, duplicate completed clients, overlap between completed and remaining
clients, invalid active runs and naive timestamps. No Ads mutation, DM, client contact, billing,
provider or permission change is introduced.

Rollback is the prior immutable `lhm-system-ops` release plus restoration of the previous resumer
asset; retain the pre-install executable hash and ownership. A live smoke test must inspect exact
processes and persisted parent/checkpoint state before enabling the queued recovery.

## Plugin Release Manager

Prepared as a separate pass. Candidate versions are Claude/marketplace `0.9.77` and Codex
`0.9.55`. This lane did not commit, push, merge, install, deploy, invoke Hermes or resume the live
portfolio. The root-owned publisher may reconcile only the listed persisted files and publish only
the generated `cto/*` branch. Michael retains merge, release and deployment authority.

Post-deployment acceptance must first reconcile the actual EHP run, preserve Alpha BasicOps task
`2198570` and Drive receipts `claude-gdrive-20260908-01/02/03`, then resume EHP,
`raise-the-bar`, and `the-heel-centre` one client per wake. It must read back verified Drive and
BasicOps handoffs in Michael Inbox with AI authorship and prove no Ads mutation.
