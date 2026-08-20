# Work Resumer Mount Path Review — 2026-08-20

Incident: `work-resumer-mount-path-20260820`

## Capability Researcher pass

The supplied live Docker evidence establishes one authoritative bind: host
`/home/hermes/.hermes` maps to container `/opt/data`. The existing LHM work-resumer, strict event
schema, durable work-control store, supported Hermes `--in` CLI, and reconciliation machinery are
the native capability. The defect was an unsupported second-mount assumption, not a missing
capability; no third-party or custom subsystem is required.

## Platform Engineer pass

The per-event handoff root is now the `handoffs` child of the authoritative host work-control
store. Its container root is the identical relative path beneath `/opt/data`. The systemd service
needs only the existing work-control `ReadWritePaths` boundary because the ephemeral subtree is
inside it. Handoff construction still creates mode-0700 handoff and response directories and
mode-0400 inputs, assigns all four paths to uid/gid 10000, and now also removes a partial handoff if
construction fails. The existing `finally` cleanup removes completed or failed invocation
handoffs. Event validation, parent validation, transition allowlisting, parent digests, durable
agent consumption, idempotency, false-marker preservation, and reconciliation are unchanged.

## QA Tester pass

The deployment test derives the exact host and container handoff paths from the proven bind. The
captured CLI fixture requires Docker identity `10000:10000`, accepts the supported `--in` syntax,
reads only `event.json` and `parent.json`, denies readable canonical sibling state, and writes the
exact `response/agent-consumed.json`. Regression tests verify 0700/0400 modes, uid/gid assignment
requests, success cleanup, invocation-failure cleanup, partial-construction cleanup, and durable
canonical state on failure.

- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests/test_work_resumer.py` — 23 passed, 10 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests` — 106 passed, 29 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 11 skills.
- `git diff --check` — passed.

All fixtures use the feature workspace and temporary files. No live Hermes, Docker, work-control,
GitHub, deployment, credential, or canonical operational state was read or mutated.

## Security/Reliability Reviewer pass

Only the idempotency-key-specific handoff receives uid/gid 10000 ownership. Canonical `incoming`,
`parents`, `consumed`, and `reconciliations` siblings remain outside the payload and root-controlled.
The container path is derived from the configured root and rejects out-of-root input. Cleanup is
covered for success, Hermes failure, and partial setup failure; canonical audit and parent state
remain durable. Validator checks fail if the host handoff leaves the authoritative store, the
container handoff leaves the `/opt/data` store, or the service loses its bounded write path.

## Plugin Release Manager pass

The reviewed release contains the native host executable, systemd boundary, deployment contract,
validator, regression tests, corrected prior operational notes, and this five-pass review. It is
ready for the root-owned publisher's automatic merge/install/requeue flow under Michael's standing
approval. This lane did not commit, push, branch, merge, install, deploy, requeue, or claim live
capability restoration.
