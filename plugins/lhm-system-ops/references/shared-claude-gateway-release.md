# Shared Claude gateway release boundary

The files named in `shared-claude-gateway-release.json` are the authoritative tracked source for the root-owned shared Claude dispatch path. They were captured byte-for-byte from the verified deployed host on 2026-08-20 after their paths, owners, modes, sizes and SHA-256 hashes were independently recorded.

These assets are distinct from the additive `lhm-evidence-claude-*` gateways. No evidence-bridge installer may overwrite the shared dispatcher or worker.

CAP-015 release 0.8.1 supervises each worker for its full lifecycle. The root dispatcher maintains
only execute access for `claudeworker` and `codexworker` on the two named profile ancestors; the
Claude process still runs as `claudeworker`, and its only write grant is the validated canonical
run directory. An ACL maintenance error terminates the worker and records an explicit durable
failed terminal artifact. `assets/install/install-shared-claude-gateway.py` verifies the exact
tracked source hashes and exact deployed predecessor hashes before mutation, saves binaries,
metadata, and `getfacl` output, and restores all of them on rollback.

## Change and release rules

1. Modify the tracked shared assets only in a reviewed `lhm-system-ops` feature branch.
2. Run the full system-ops validator and test suite. Tests must verify source hashes against the release manifest, least-privilege traversal, run-directory-only write authority, honest terminal states and non-duplicate recovery.
3. Build an immutable release from the reviewed commit and record its commit and archive SHA-256.
4. Deployment requires the applicable delegated CTO approval class or explicit Michael approval. The host installer must back up every listed destination, install only the manifest-listed files with their exact metadata, run `systemd-analyze verify`, reload units and execute the dispatcher regression probe.
5. Rollback restores every captured destination byte-for-byte and reloads systemd. Run artifacts and audit evidence are preserved.

Publication alone does not alter the live host. Credential access, new destinations, broader filesystem permission, destructive recovery or a change to the Google Ads mutation ceiling remains outside the bounded repair class.
