# Work Resumer Hermes Invocation Review — 2026-08-20

Incident: `work-resumer-hermes-invocation-20260820`

## Capability Researcher pass

The repository's native deployment contract maps the host handoff root
`/run/lhm-work-resumer` to `/opt/run/lhm-work-resumer` in Hermes. The captured live CLI contract
supports the global `--in DIR` option and `-z/--oneshot`; the prior unsupported option is not part
of that contract. No third-party capability is required.

## Platform Engineer pass

The release asset now derives the container handoff from the configured host handoff root, rejects
paths outside that root, and invokes Hermes as `-p lhm_brain --in
/opt/run/lhm-work-resumer/<idempotency_key> -z <prompt>`. Docker continues to request uid/gid
`10000:10000`. No schema, state transition, store, reconciliation, permission, or systemd wiring was
changed.

## QA Tester pass

A subprocess fixture implements the captured live argparse surface, rejects unknown options,
checks the exact profile, container path and requested identity, changes into the mapped handoff,
reads `event.json` and `parent.json`, and writes the exact `response/agent-consumed.json` path.

- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests/test_work_resumer.py` — 21 passed, 10 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 pytest -q plugins/lhm-system-ops/tests` — 104 passed, 29 subtests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 11 skills.
- `git diff --check` — passed.
- Release-tree scan for the unsupported option — no matches.

## Security/Reliability Reviewer pass

The handoff remains mode 0700 with 0400 input files and a 0700 response directory, all assigned to
uid/gid 10000. The container path is derived rather than accepted from input and fails closed when
outside the configured root. Existing exact-schema validation, parent digest check, strict allowed
transitions, durable agent record, idempotent recovery, false-marker audit reconciliation and
single incoming-store wiring remain covered by the passing regression suite. Tests use temporary
state only; no live Hermes or work-control state was read or mutated.

## Plugin Release Manager pass

The bounded release consists of the host executable change, its integration tests, and this review
record. It is ready for the root-owned publisher's automatic merge/install/requeue flow under
Michael's standing authority. This review does not authorize this lane to commit, push, merge,
install, deploy, or claim capability restoration.
