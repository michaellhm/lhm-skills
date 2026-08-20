# Shared Claude gateway release boundary

The files named in `shared-claude-gateway-release.json` are the authoritative tracked source for the root-owned shared Claude dispatch path. They were captured byte-for-byte from the verified deployed host on 2026-08-20 after their paths, owners, modes, sizes and SHA-256 hashes were independently recorded.

These assets are distinct from the additive `lhm-evidence-claude-*` gateways. No evidence-bridge installer may overwrite the shared dispatcher or worker.

## Change and release rules

1. Modify the tracked shared assets only in a reviewed `lhm-system-ops` feature branch.
2. Run the full system-ops validator and test suite. Tests must verify source hashes against the release manifest, least-privilege traversal, run-directory-only write authority, honest terminal states and non-duplicate recovery.
3. Build an immutable release from the reviewed commit and record its commit and archive SHA-256.
4. Deployment requires the applicable delegated CTO approval class or explicit Michael approval. The host installer must back up every listed destination, install only the manifest-listed files with their exact metadata, run `systemd-analyze verify`, reload units and execute the dispatcher regression probe.
5. Rollback restores every captured destination byte-for-byte and reloads systemd. Run artifacts and audit evidence are preserved.

Publication alone does not alter the live host. Credential access, new destinations, broader filesystem permission, destructive recovery or a change to the Google Ads mutation ceiling remains outside the bounded repair class.

## ACL-mask race repair

The dispatcher verifies effective `claudeworker` traversal immediately before dispatch and runs a root-owned, per-run guard until `final.json` exists or the worker unit stops. The guard may restore only `mask::x` and `user:claudeworker:--x` on `/home/hermes/.hermes` and `/home/hermes/.hermes/profiles/lhm_brain`; it grants no read access and never changes another path. Worker-owned write authority remains confined to the validated run directory. Terminal writes retry briefly while the guard repairs a concurrent mask reset.

Lost runs may be finalized only with `--recover-lost RUN_ID REQUEST_SHA256`. Recovery verifies the original request bytes, refuses an existing result, writes `failed/lost_before_persistence`, and records a stable dedupe key. It never claims or reconstructs analysis.

Rollback restores dispatcher SHA-256 `fc633fa3afa017a230b48ed1a62b67aa50b9e87db252b500f4c6fe88f06de531` and worker SHA-256 `afe2d7655ec2b3699958bb82c23a59cf97c0ab850878ee3351dab9e9a75e9590` from the pre-deployment backup, then reloads systemd and runs the source-inventory and dispatcher probes. Run artifacts remain untouched.
