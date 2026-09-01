# Hermes subscription Codex default — sealed change review

- Parent: `michael-codex-primary-routing-20260901`
- Incident: `hermes-openrouter-bypass-codex-subscription-20260901`
- Base: `f2d6e5584258fea75356b4726bb136ed395ffb89` (`origin/main`)
- Candidate branch: `cto/hermes-openrouter-bypass-codex-subscription-20260901`
- Return point: `desktop-control-review-sealed-codex-primary-routing-change-before-live-deployment`

## Recorded passes

1. **Capability Researcher — recommended.** Reused native LHM queue/watcher, structured-receipt, codexworker and Codex CLI patterns. No third-party dependency. The CTO lane and explicit Claude destination connectors remain separate.
2. **Platform Engineer — implemented.** Added an exact-schema container intake client, codexworker-only host worker, replacement path/service, validation, tests and release/rollback contract. Generic non-mutating, marketing and knowledge-work classes all select Codex. Only `default-review-only` is registered.
3. **QA Tester — pass with live limitations.** Targeted tests and repository validators pass. The full system-ops suite returned 188 passed and 34 subtests passed, plus three pre-existing CAP-015 assertions on unchanged files that expect release 0.9.6 while the canonical manifest is already 0.9.7.
4. **Security/Reliability Reviewer — approved for publication review.** The worker is the existing `codexworker` identity, receives only HOME/CODEX_HOME/PATH, checks ChatGPT login status, ignores user provider config, runs ephemeral/read-only, and cannot read the lhm_brain vault, root home or Docker sockets. API/OpenRouter/Anthropic variables are not inherited. Auth failure creates a durable incident and no alternate worker is called. Residual risk: prompt/tool-turn ceiling is reinforced by a 900-second hard process timeout and 16,000-character intake ceiling; live provider metering and subscription exhaustion cannot be proven in the source sandbox.
5. **Plugin Release Manager — sealed, not published or deployed.** Versions are Codex 0.9.51 and Claude/marketplace 0.9.72. The obsolete generic `lhm-codex-dispatch.path` is explicitly superseded by `lhm-codex-execution.path`; the CTO watcher is not replaced. Michael retains merge, release and deployment authority.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q plugins/lhm-system-ops/tests/test_codex_execution_bridge.py` — 8 passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 plugins/lhm-system-ops/scripts/validate_system_ops.py` — passed, 12 skills.
- `python3 scripts/validate-plugin-versions.py` — passed.
- `python3 scripts/validate-script-parity.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q plugins/lhm-system-ops/tests` — 188 passed, 34 subtests passed, 3 pre-existing unchanged CAP-015 failures.
- `git diff --check` — passed.
- Sensitive-material scan — no credential material found; prohibited provider names occur only in negative tests/validation and the live regression instructions.

## Smallest consequential approval and rollout

One approval from Michael should name the immutable reviewed commit and authorise only: merge/release of lhm-system-ops; root-owned installation of the two executables and two units using the ownership/ACL contract; disabling an obsolete `lhm-codex-dispatch.path` only if it exists; enabling `lhm-codex-execution.path`; and running the redacted live smoke/regression suite. It does not authorise credential changes, Telegram downtime, main bypass, broader filesystem access, Claude-route changes or OpenRouter use.

Before installation record prior file/unit hashes, owners, modes, enablement, and the OpenRouter generation counter. Verify subscription status as codexworker without retaining output. Then test protected generic intake, marketing/knowledge default selection, auth failure, duplicate, invalid profile, timeout, existing website/repository gates, explicit Claude destination connectors and rollback. Acceptance requires zero new OpenRouter generation records and no hermes-2 worker inference during the controlled fail-closed regression.

Rollback is the exact procedure in `references/codex-execution-release.md`: disable only the replacement watcher, wait for its oneshot, restore the recorded inventory, daemon-reload, restore prior healthy watchers, and retain receipts/incidents.
