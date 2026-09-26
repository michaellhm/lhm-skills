# Hermes Codex primary runtime exit — source evidence

- Parent: `michael-codex-primary-routing-20260901`
- Incident: `hermes-codex-primary-runtime-exit-20260902`
- Base: merged commit `91072b43d1609dde85542a2efd65792ee52b5ab9` (approved source commit `07fc5ebf63f9b88f27c1f2cca3287191d295a4f9`)
- Return point: `desktop-control-review-sealed-runtime-exit-repair-before-live-deployment`

## Redacted reproduction

The installed source-test runtime reports `codex-cli 0.147.0`. Running the same `codex exec --ephemeral --ignore-user-config --sandbox read-only ...` shape with an empty, deliberately non-writable synthetic `CODEX_HOME` exits `1` before a structured result and reports:

`failed to initialize in-process app-server client: Permission denied (os error 13)`

No credential or network-backed inference was used. The options are accepted by 0.147.0; initialization fails because the CLI still needs writable app-server state under `CODEX_HOME` during an ephemeral exec. This matches the production unit's `ProtectHome=read-only` confinement and its intentional exclusion of the real credential home from `ReadWritePaths`.

## Repair boundary

The worker now creates a mode `0700` runtime home inside the request's existing mode `0700` `worker-runs` directory. It links only the existing regular, non-symlink subscription `auth.json`; the real Codex home remains read-only under systemd. Missing or unexpected auth storage fails closed. The execution environment remains limited to `HOME`, the request-local `CODEX_HOME`, and `PATH`; no metered provider keys or fallback route are added.

On subprocess failure the incident JSON retains only the exit status and the final 4000 characters of each captured stream after token-pattern redaction. It does not retain the command or objective, avoiding the prior `CalledProcessError` command-string exposure.

## Deployment gate

This source repair is not a deployment approval. The controlled post-install suite must cover positive generic, marketing and knowledge receipts plus auth failure, invalid profile, duplicate, timeout and existing Claude/repository routes. Snapshot OpenRouter metering before and after the whole suite and require byte-identical evidence. Any failed, missing or malformed positive receipt requires immediate candidate watcher disablement and rollback using the release contract; do not fall back to OpenRouter, Hermes inference or Claude.

## Recorded role passes

1. **Capability Researcher — passed.** Reconciled the canonical `lhm-system-ops` source at base `91072b43d1609dde85542a2efd65792ee52b5ab9`; the native worker, systemd unit, handoff and release contract cover the capability, so no third-party dependency is required.
2. **Platform Engineer — passed.** Reproduced the pre-result exit against `codex-cli 0.147.0` and implemented the request-local writable state home, read-only subscription-auth link, safe subprocess error, and bounded redacted incident evidence.
3. **QA Tester — passed for affected scope.** The 13-test bridge suite covers generic/marketing/knowledge Codex routing, subscription authentication, review-only authority, no fallback, exact 0.147.0 failure reproduction, runtime-home repair, diagnostics redaction, systemd boundaries and direct-json/no-follow/non-recursive ACL handoff. Repository system-ops, version and parity validators pass.
4. **Security/Reliability Reviewer — passed.** No credential bytes, metered key, provider fallback, Telegram change, Claude-route change, group change, ACL expansion, broader writable path or live edit is present. The real Codex home remains excluded from systemd `ReadWritePaths`; failures remain closed and rollout requires immediate rollback on any failed positive receipt.
5. **Plugin Release Manager — sealed for bounded publication only.** Candidate versions are Codex `0.9.54` and Claude/marketplace `0.9.75`. No commit, push, merge, installation or deployment was performed. The root-owned publisher must reconcile these exact persisted files; Michael retains merge, release and live deployment authority at `desktop-control-review-sealed-runtime-exit-repair-before-live-deployment`.

The broader workflow-controller suite is not an acceptance dependency for this isolated bridge change. Its environment-bound cases require an installed v5 CLI, staged `/tmp` live candidates and matching trusted marketing package fixtures; without those fixtures it reports expected setup/candidate/version failures. The directly affected bridge suite and repository validators are fully green.
