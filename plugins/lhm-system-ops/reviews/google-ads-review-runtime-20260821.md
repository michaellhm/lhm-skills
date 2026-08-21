# CAP-GADS-2.2-RUNTIME-001 — governed source repair

Parent: `claude-gads-20260821-03`  
Return role: `head_of_production`  
Return point: `mhealth review-only regression after capability_restored`

## 1. Capability Researcher — recommended

Native CAP-015 already admits and supervises 600-second bounded workers. The incident is caused by
the `google_ads_readonly` profile alone being pinned to 300 seconds. Extending that exact profile to
600 seconds is smaller and safer than adding partial-result storage, phase schemas, and resume
coordination. No third-party or custom runtime is warranted.

## 2. Platform Engineer — implemented

Release 0.8.7 changes only the admitted elapsed-time value for `google_ads_readonly`, from 300 to
600 seconds. The tracked dispatcher, release manifest, root-only installer version, tests, and
release boundary documentation are updated. The release manifest pins the current 0.8.6 dispatcher
as the exact required predecessor.

Rollback is the existing CAP-015 byte-for-byte path: the installer records all destination bytes,
metadata, and ancestor ACLs before installation; `--rollback-state` restores those exact assets and
reloads systemd. The prior dispatcher hash is
`65257d7a6e9b28362eddd108afe207b32dbe27944bc6deb14b7d8b5a3443e7cc`.

## 3. QA Tester — source regression passed

- Focused gateway and installer tests: 13 passed.
- Full system-ops suite: 124 passed, 32 subtests passed.
- System-ops validator: passed, 11 skills.
- Positive boundary: `google_ads_readonly` resolves to exactly 600 seconds.
- Compatibility boundaries: registration remains 30 seconds and HTML production remains 1200
  seconds; supervisor allowlist already admits 600 seconds.
- Negative/security assertions confirm the Google Ads worker has no mutation, shell, browser, or web
  tools.

The original live four-file mhealth run is intentionally not claimed here: this isolated source
workspace cannot deploy to live Hermes or access the governed operational run store.

## 4. Security/Reliability Reviewer — passed for publication

The worker source is byte-identical to 0.8.6. Therefore the strict read-only MCP configuration,
Google Ads query/documentation tool allowlist, packaged-skill-only local tool surface, single
registered client/CID injection, unprivileged worker identity, run-directory-only write authority,
12-turn ceiling, and USD 2.00 provider ceiling remain unchanged. The dispatcher continues to reject
unregistered clients, malformed ten-digit account IDs, cross-client evidence paths, unexpected
fields, duplicate run IDs, and every timeout other than the profile's one admitted value.

Longer elapsed time increases only bounded resource occupancy. Existing turn and spend limits cap
provider consumption, and the supervisor continues fail-closed ACL maintenance and durable terminal
artifacts.

## 5. Plugin Release Manager — source handoff ready; restoration pending

Branch: `cto/cap-gads-2-2-runtime-001`. No commit, push, merge, deployment, live Hermes mutation, or
restoration event was performed by the CTO worker. The bounded publisher may publish only the exact
persisted paths reported in the CTO result. Publication is not capability restoration.

After separately authorised deployment, Production must run a fresh `claude-gads-YYYYMMDD-NN`
mhealth four-file review and retain authoritative evidence showing: terminal completion without
timeout; mandatory skills; QA verdict; all four file bodies; structured handback; and `mutations:
none`. Only then may the exact `capability_restored` event for parent `claude-gads-20260821-03` be
emitted and consumed, proving automatic resume at the saved mhealth return point.
