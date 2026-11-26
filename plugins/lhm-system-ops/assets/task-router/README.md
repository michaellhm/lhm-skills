# TED scoped approval repair

The central task router formerly rejected the entire authenticated request when
Michael wrote “all approved, except I don't approve the Melbourne bid strategy
changes. Send to Claude”. Its provider selection already understood the handoff;
the blanket negation check incorrectly rejected the action exclusion.

`scoped_approval.py` provides an admission-only projection for explicit provider
requests with a named `except/excluding … don't approve …` clause. The full original
instruction and its source hash still reach the worker. Global refusals, stops,
provider negations, author checks, later stops, duplicate checks and the existing
provider tool approval ceiling are retained. Ambiguous clauses remain fail-closed.

`scripts/patch_ted_scoped_approval.py` prepares the minimal router change, validates
the expected predecessor block and supports idempotent reapplication. Place the
helper beside the router. Deployment requires an exact predecessor hash check,
rollback backup, atomic replacement and an authenticated live route preview.

Run the regression suite with `TED_ROUTER_SOURCE` pointing to the deployed router
snapshot. The suite checks the actual Router contract as well as clause handling;
without that snapshot, contract tests explicitly skip. This repair does not grant
new Ads permissions or interpret approval choices for the worker.

Deployment on Michael's explicit request: original router SHA-256
`53c63aa40ff091ce48cf622db5bc4c9f0ce557d6e531f81f1beca9ac13ed83de`,
patched router `81c7b68f8e0f09d84020cc7c50bfe93a9a56657a789cf3797c4439ae44f3b998`,
helper `5081a4fe14ff9821e1755ca34fdde88b969bb7aa4e5dd1e69f5ca5b8ff322929`.
Ten regression tests, plugin versions, script parity and system ops validation
passed. Existing long-lived MCP processes require a controlled reconnect to import
the new module; fresh trusted invocations already use it.
