# Integration verification — 22 October 2026

Engineering, security and QA checks were performed sequentially in the same Codex session; no independent reviewer is claimed.

- Bridge tests: 10 passed. Worker contract tests: 3 passed.
- Plugin versions, duplicate-script parity, edited skill frontmatter and system-ops release validation passed; no new top-level skill was added.
- The live MCP stdio handshake listed exactly `codex_session_submit` and `codex_session_status`; registered task status returned `not_submitted` and the existing connector identity verified as TED 82491.
- Only the TED gateway was reloaded. It discovered the new MCP process; other Hermes gateways were preserved.
- Live BasicOps assignment and discussion events reached TED. TED posted a versioned saved-context, review-only plan and refused an explicitly AI-authored relay of earlier permission. No task was dispatched on that relay. This approval refusal is expected behaviour, not evidence of a completed Codex run.
- The handback timer runs successfully without a model. End-to-end session creation and native review handback still require Michael's personal approval of the canonical plan on the registered integration-test task.

Test record: https://app.basicops.com/481630853364967730?l=_805_31C_1BHYZD839B2

The existing paired Wellness chat was previously verified by Michael. That confirms the underlying persistent VPS chat transport; it does not substitute for this TED route's pending end-to-end trial.

All skill LEARNED files were scanned. Existing prospect-sitemap learnings concern unrelated marketing work and were preserved without changes in this scoped infrastructure update. An exploratory broad unittest pattern encountered an existing pytest-dependent test in a Python environment without pytest; the two new test suites were then selected explicitly and passed.

Deployment is a scoped runtime pilot, not a main-branch merge or full marketplace plugin installation. Rollback copies are under `/var/lib/lhm-codex-pilot-build/ted-*`; the first installation attempt's backup precedes any worker/skill changes, while subsequent backups include prior pilot revisions. Keep both when rolling back.

## Integration and direct-intake upgrade

- Direct-intake human task and AI-relay rejection: bridge suite 12/12.
- Existing worker suite 4/4 and delivery suite 4/4.
- Version, duplicate-script parity and system-ops validation pass.
- Canonical LEARNED scan reviewed the existing prospect sitemap entries; they are unrelated to this integration change and preserved rather than reset or absorbed into unrelated skills.
- Live GitHub MCP 2.0.3: 35 tools discovered; authenticated RTB homepage source read passed. GitHub account repository push permission verified without publishing.
- Live Codex skills/list: 371 total available skills across roots, zero loader errors; this deployment adds the 200 top-level LHM skills. Dependencies and authentication remain per-service.
- Workspace MCP package installed at 2.1.2; Google Docs consent and live editing checks remain pending until Michael completes consent. Do not describe installed as authenticated.
- This is a same-runtime QA/security pass, not independent review.
