# Shared Claude gateway release boundary

The files named in `shared-claude-gateway-release.json` are the authoritative tracked source for the root-owned shared Claude dispatch path. Release 0.9.4 was reconciled on 2026-08-23 against exact production bytes after paths, owners, modes, sizes and SHA-256 hashes were independently recorded. The admitted predecessor hashes are the observed live dispatcher `e6c7c17a…`, worker `ee1dff61…`, and container client `cf9eff52…`; the governed 0.9.3 source remains recorded in Git history.

These assets are distinct from the additive `lhm-evidence-claude-*` gateways. No evidence-bridge installer may overwrite the shared dispatcher or worker.

Release 0.9.4 is the shared-Claude gateway subrelease packaged inside LHM System Ops 0.9.8.
It supervises each worker for its full lifecycle. The root dispatcher maintains
only execute access for `claudeworker` and `codexworker` on the two named profile ancestors; the
Claude process still runs as `claudeworker`, and its only write grant is the validated canonical
run directory. An ACL maintenance error terminates the worker and records an explicit durable
failed terminal artifact. `assets/install/install-shared-claude-gateway.py` verifies the exact
tracked source hashes and exact deployed predecessor hashes before mutation, saves binaries,
metadata, and `getfacl` output, and restores all of them on rollback.

Release 0.9.4 retains the host admission and registry-write protections and governs the authoritative bind-mounted
Hermes `claude-dispatch` client as a governed source asset. Relative to the exact observed live
predecessors pinned in the release manifest, the Google Ads and general marketing submitters use the shared collision-safe sequence
scanner across incoming, processed, running and failed buckets. The submitted Google Ads timeout
remains 600 seconds. The installer targets the approved host side of the read-write bind mount, preserves owner
10000, group 10000 and mode 0755, and includes the client in exact preflight, backup, atomic install
and byte-for-byte atomic rollback. Deployment acceptance must independently prove that the host and
container paths have the manifest post-change hash and are byte-identical.

Release 0.9.4 enters Google Ads through the installed `/lhm-marketing-hub:start-googleads` command,
captures Claude stream events, persists `skill-provenance.json`, and fails closed unless the monthly
review, bid/budget, conversion-audit and delivery-QA skills emitted real `Skill` tool calls. It uses
a bounded 24-turn and USD 4.00 provider ceiling, strict read-only MCP configuration, exact Google Ads tool
allowlist, single registered client/CID boundary, unprivileged worker identity, and run-directory-only
write grant. Rollback restores the exact observed live predecessor bytes pinned in the manifest; the Google Ads ceiling remains 600 seconds.

Release 0.9.4 grants the dispatcher write access to only the exact handback-registry file. Timestamped
safety copies remain inside the already-writable dispatch audit tree. Updates are flushed and synced;
an update error restores the captured backup and produces a durable refusal.

Release 0.9.4 also retains the Google Ads reconciliation evidence boundary and explicit Prototype,
Astro and WordPress department routes. The dispatcher reads only
the client-specific Markdown paths explicitly registered in `google-ads-clients.json`, enforces the
client folder, file-count and byte ceilings, rejects links and path traversal, and passes content
with SHA-256 receipts to the isolated worker. The worker may load packaged Google Ads skills and use
the allowlisted read-only Google Ads MCP; it still has no filesystem, Drive, BasicOps or mutation
tool. See `google-ads-evidence-pack.md`.

The handback-target registration surface additionally admits one internal destination only:
`local-health-marketing` at the exact canonical vault prefix `30 Projects/LHM Growth/`. Every other
internal slug or prefix fails closed. Existing client and opportunity registration behavior is
unchanged; the Drive folder ID and BasicOps task IDs remain exact bounded inputs.

Release 0.9.4 reconciles the workflow metadata already present on the live client without trusting
it as authority. A root-owned dispatcher table pins the exact workflow ID, ordered required skills,
and required capabilities for every admitted profile and specialist route; missing, reordered,
duplicated, additional, or substituted values fail closed. These values are propagated from the
pinned table into prompts and terminal receipts. Google Ads and specialist runs capture actual
`Skill` tool calls and fail when a required invocation is absent. Search Console, HTML production,
Drive, BasicOps, marketing orchestration, and registration receipts explicitly label skill metadata
as declared-only where that profile does not produce observable Skill-call evidence.

For Drive and BasicOps handback, an existing canonical Google Ads client may supply its bounded
client prefix, exact Drive folder URL, and at most 20 unique numeric task IDs. If an explicit
handback entry exists for the same slug, it must agree exactly with the canonical values or the
request fails closed. This does not broaden the exact artifact-path, folder, task, read-back, or
mutation boundaries.

## Change and release rules

1. Modify the tracked shared assets only in a reviewed `lhm-system-ops` feature branch.
2. Run the full system-ops validator and test suite. Tests must verify source hashes against the release manifest, least-privilege traversal, run-directory-only write authority, honest terminal states and non-duplicate recovery.
3. Build an immutable release from the reviewed commit and record its commit and archive SHA-256.
4. Deployment requires the applicable delegated CTO approval class or explicit Michael approval. The host installer must back up every listed destination, install only the manifest-listed files with their exact metadata, run `systemd-analyze verify`, reload units and execute the dispatcher regression probe.
5. Rollback restores every captured destination byte-for-byte and reloads systemd. Run artifacts and audit evidence are preserved.

Publication alone does not alter the live host. Credential access, new destinations, broader filesystem permission, destructive recovery or a change to the Google Ads mutation ceiling remains outside the bounded repair class.
