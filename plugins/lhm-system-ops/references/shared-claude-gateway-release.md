# Shared Claude gateway release boundary

The files named in `shared-claude-gateway-release.json` are the authoritative tracked source for the root-owned shared Claude dispatch path. They were captured byte-for-byte from the verified deployed host on 2026-08-20 after their paths, owners, modes, sizes and SHA-256 hashes were independently recorded.

These assets are distinct from the additive `lhm-evidence-claude-*` gateways. No evidence-bridge installer may overwrite the shared dispatcher or worker.

Release 0.9.2 supervises each worker for its full lifecycle. The root dispatcher maintains
only execute access for `claudeworker` and `codexworker` on the two named profile ancestors; the
Claude process still runs as `claudeworker`, and its only write grant is the validated canonical
run directory. An ACL maintenance error terminates the worker and records an explicit durable
failed terminal artifact. `assets/install/install-shared-claude-gateway.py` verifies the exact
tracked source hashes and exact deployed predecessor hashes before mutation, saves binaries,
metadata, and `getfacl` output, and restores all of them on rollback.

Release 0.9.2 retains the 0.8.7 host admission change and governs the authoritative bind-mounted
Hermes `claude-dispatch` client as a governed source asset. Relative to its exact 0.8.7 deployed
line, the Google Ads and general marketing submitters now use the shared collision-safe sequence
scanner across incoming, processed, running and failed buckets. The submitted Google Ads timeout
remains 600 seconds. The installer targets the approved host side of the read-write bind mount, preserves owner
10000, group 10000 and mode 0755, and includes the client in exact preflight, backup, atomic install
and byte-for-byte atomic rollback. Deployment acceptance must independently prove that the host and
container paths have the manifest post-change hash and are byte-identical.

Release 0.9.2 enters Google Ads through the installed `/lhm-marketing-hub:start-googleads` command,
captures Claude stream events, persists `skill-provenance.json`, and fails closed unless the monthly
review, bid/budget, conversion-audit and delivery-QA skills emitted real `Skill` tool calls. It uses
a bounded 24-turn and USD 4.00 provider ceiling, strict read-only MCP configuration, exact Google Ads tool
allowlist, single registered client/CID boundary, unprivileged worker identity, and run-directory-only
write grant. Rollback restores the prior 300-second dispatcher byte-for-byte.

Release 0.9.2 grants the dispatcher write access to only the exact handback-registry file. Timestamped
safety copies remain inside the already-writable dispatch audit tree. Updates are flushed and synced;
an update error restores the captured backup and produces a durable refusal.

Release 0.9.2 also retains the Google Ads reconciliation evidence boundary and explicit Prototype,
Astro and WordPress department routes. The dispatcher reads only
the client-specific Markdown paths explicitly registered in `google-ads-clients.json`, enforces the
client folder, file-count and byte ceilings, rejects links and path traversal, and passes content
with SHA-256 receipts to the isolated worker. The worker may load packaged Google Ads skills and use
the allowlisted read-only Google Ads MCP; it still has no filesystem, Drive, BasicOps or mutation
tool. See `google-ads-evidence-pack.md`.

## Change and release rules

1. Modify the tracked shared assets only in a reviewed `lhm-system-ops` feature branch.
2. Run the full system-ops validator and test suite. Tests must verify source hashes against the release manifest, least-privilege traversal, run-directory-only write authority, honest terminal states and non-duplicate recovery.
3. Build an immutable release from the reviewed commit and record its commit and archive SHA-256.
4. Deployment requires the applicable delegated CTO approval class or explicit Michael approval. The host installer must back up every listed destination, install only the manifest-listed files with their exact metadata, run `systemd-analyze verify`, reload units and execute the dispatcher regression probe.
5. Rollback restores every captured destination byte-for-byte and reloads systemd. Run artifacts and audit evidence are preserved.

Publication alone does not alter the live host. Credential access, new destinations, broader filesystem permission, destructive recovery or a change to the Google Ads mutation ceiling remains outside the bounded repair class.
