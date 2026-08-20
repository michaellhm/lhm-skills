# Claude Result Write Permission Review — 2026-08-20

Parent: `ads-delivery-2026-08-any-stage-pilot`  
Incident: `claude-result-write-permission-20260820`  
Return point: `claude-gads-20260820-01`

## Capability Researcher pass

The tracked shared Claude dispatcher and worker, effective-user access checks, POSIX ACL tooling,
and transient systemd units are the native capability. The observed failure was a concurrent ACL
mask reset, not a missing integration. No third-party plugin, new credential, new network path, or
broader Hermes permission is required. The bounded repair is to verify traversal as
`claudeworker`, restore execute-only ACL state on the two exact ancestors when ineffective, and
keep checking until terminal persistence completes.

## Platform Engineer pass

The dispatcher now tests effective traversal with `runuser --user claudeworker -- test -x`
immediately before worker dispatch. A root-owned per-run guard repeats that check while the worker
is active and once more at the terminal boundary. Repair is limited to `mask::x` and
`user:claudeworker:--x` on `/home/hermes/.hermes` and
`/home/hermes/.hermes/profiles/lhm_brain`. The worker retries terminal writes briefly while the
guard repairs a reset. Worker ownership and ACL write authority remain confined to the validated
`runs/<run_id>` directory.

The dispatcher also provides digest-bound, idempotent `--recover-lost` handling. It refuses a
mismatched request or an existing `result.md`, writes `error.txt` plus `final.json` with status
`failed` and reason `lost_before_persistence`, and records the stable run-ID/request-digest dedupe
key. It does not recreate or claim analysis.

## QA Tester pass

The regression resets effective traversal after dispatch and proves the guard checks before,
during, and at terminal persistence. Negative tests constrain repairs to the two ancestors, reject
digest mismatch, preserve an existing result, and prove recovery idempotency. Inventory tests
bind sources to the release manifest and verify exact destinations and modes.

- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 11 skills.
- `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider plugins/lhm-system-ops/tests` — 117 passed, 32 subtests passed.
- Focused shared-gateway regression — 9 passed.

Tests used only repository fixtures and temporary paths. Protected `main`, live Hermes, systemd,
credentials, GitHub, and production run state were not modified.

## Security/Reliability Reviewer pass

Disposition: approved for review. The change grants execute but no read access on two fixed
ancestors. Guard input must match the validated run-unit grammar and resolve directly beneath the
fixed runs directory. Terminal output remains mode `0640`; no secrets or dependencies were added.
Recovery fails closed on path, digest, and existing-analysis checks. Residual risk is bounded to a
reset occurring after the guard's final check; by then `final.json` is already durable or the
worker unit has stopped, and the final effective check restores traversal for readers.

Rollback is byte-for-byte restoration of dispatcher SHA-256
`fc633fa3afa017a230b48ed1a62b67aa50b9e87db252b500f4c6fe88f06de531` and worker SHA-256
`afe2d7655ec2b3699958bb82c23a59cf97c0ab850878ee3351dab9e9a75e9590`, followed by systemd reload
and the inventory/dispatcher probes. Run artifacts are preserved.

## Plugin Release Manager pass

The release manifest maps the two executables and two current unit files to exact root-owned
destinations. Current candidate hashes are dispatcher
`99724b00107e79c5ecd1ef40beec769cb2c66b585c56c6007191c73a8d6fd75b` and worker
`f60287bb638e7146f97ebfaa90c4827f9fd4a9d9246f0af93b60d183d4a7ee3b`. Plugin manifests and
marketplace are in parity at version `0.8.1`.

After separately approved deployment of the reviewed immutable commit, the original run must be
finalized once with:

```text
/usr/local/libexec/lhm-claude-dispatcher --recover-lost claude-gads-20260820-01 d4c516d96ff4a89456b54120cec26cbf78a20b09ce2b1e5c8a2119696d4a91e7
```

That action produces a failed/lost terminal state and the dedupe key
`claude-gads-20260820-01:d4c516d96ff4a89456b54120cec26cbf78a20b09ce2b1e5c8a2119696d4a91e7`.
It is not recovered analysis and must not redispatch the old request. A fresh analysis, if still
needed, requires a separately governed new run. This lane did not commit, push, branch, merge,
deploy, execute recovery, or claim live capability restoration; Michael retains those authorities.
