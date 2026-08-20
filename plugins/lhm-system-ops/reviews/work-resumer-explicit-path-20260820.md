# Work Resumer Explicit Path Review — 2026-08-20

Incident: `work-resumer-explicit-path-20260820`

## Capability Researcher pass

The supplied uid/gid 10000 verification and existing LHM contracts establish the native solution:
Hermes supports `--in <container_handoff>`, the authoritative host `/home/hermes/.hermes` tree maps
to container `/opt/data`, and the bounded handoff already contains the exact event, parent, and
response locations. The remaining defect was prompt discovery, not missing capability. No
third-party plugin or new state store is required.

## Platform Engineer pass

`invoke` now derives one canonical direct-child handoff from the configured host root, maps that
same child beneath the configured container root, and interpolates its absolute `event.json`,
`parent.json`, and `response/agent-consumed.json` paths into the one-shot prompt. The identical
container directory remains the value of supported Hermes `--in`. The vague “supplied handoff”
dependency is removed. Event schema, parent transition, durable records, idempotency, reconciliation,
and cleanup logic are unchanged.

## QA Tester pass

The captured Docker/Hermes fixture verifies uid/gid `10000:10000`, the exact `--in` value, each of
the three absolute prompt paths exactly once, and reads/writes mapped fixture files from those exact
container paths. Regression coverage rejects relative, traversal-bearing, nested, host-out-of-root,
and container-out-of-`/opt/data` inputs. It also retains permission, isolation, failure cleanup,
strict schema, transition, idempotency, recovery, and audit reconciliation coverage.

- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests/test_work_resumer.py` — 25 passed, 13 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests` — 108 passed, 32 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 11 skills.
- `git diff --check` — passed.

All execution used the feature workspace and temporary fixtures. No live Hermes, Docker,
work-control, parent, deployment, credential, GitHub, or publication state was mutated.

## Security/Reliability Reviewer pass

Invocation fails before subprocess execution unless the host handoff is absolute, canonical, a
single safe-named child of the configured handoff root, and the canonical container root remains
beneath `/opt/data`. This closes lexical traversal and path-injection cases while preserving the
0700/0400 handoff permissions, uid/gid ownership, response validation, canonical-state race check,
durable audit evidence, and unconditional ephemeral cleanup.

## Plugin Release Manager pass

The bounded release changes only the work-resumer executable, its regression test, and this review
record. It is ready for the root-owned publisher to reconcile, commit, push the generated `cto/*`
branch, and perform Michael's standing-approved merge/install/requeue workflow. This lane did not
commit, push, merge, install, deploy, requeue, or claim live capability restoration.
