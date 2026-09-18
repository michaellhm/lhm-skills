# Weekly web brief Codex worker routing

- Incident: `weekly-web-brief-worker-routing`
- Parent: `weekly-web-brief-20260921`
- Return point: `lhm_brain / weekly-web-project-brief / activate-codex-worker-route`
- Base: `99ca198d069985e8e92de8ce64a586e02df68312` (PR 134)
- Branch: `cto/weekly-web-brief-worker-routing`

## Recorded passes

1. **Capability Researcher — recommended.** Native LHM already has the subscription-authenticated `codexworker`, queue watcher, closed intake, read-only Codex sandbox, redacted incidents and no-provider-fallback behavior. The existing generic contract could return only a summary, so it could not carry scoped research evidence or a renderable weekly brief. No third-party dependency is needed.
2. **Platform Engineer — implemented.** Added the single bound request variant `weekly_web_project_brief` / `weekly-web-brief-json-v1`. It accepts only a capped object containing a research receipt and BasicOps boards 68635/68921, Obsidian, Gmail and optional Fathom evidence, then returns a closed brief object in the durable Codex receipt. Generic task profiles are unchanged. The scheduled contract requires Hermes to acquire evidence, Codex to draft JSON, and Hermes to render/check/send.
3. **QA Tester — pass.** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q plugins/lhm-system-ops/tests plugins/lhm-project-hub/skills/weekly-web-project-brief/tests/test_brief.py` returned 221 passed and 34 subtests passed. The fixture proves intake, subscription-Codex selection, brief receipt and deterministic render without Mailgun. Negative tests reject wrong profiles, workflows and evidence. Existing tests cover Melbourne/DST, fixed recipients, weekly dedup and uncertain-send suppression. `validate_system_ops.py`, plugin version validation and `git diff --check` pass.
4. **Security/Reliability Reviewer — approved for publication review.** No service, unit, ACL, group, shell, credential, connector, Mailgun, recipient, default-model or other-job change exists. The existing allowlisted environment, ephemeral writable runtime home with read-only auth link, read-only Codex sandbox, hard timeout and redacted incidents remain. Evidence is capped at 240 KB, source-key/board bound and labelled untrusted. A missing, failed or mismatched receipt blocks send.
5. **Plugin Release Manager — sealed for bounded publisher, not published or deployed.** Project Hub is 0.1.91; System Ops is Claude 0.9.101 and Codex 0.9.55. The root-owned publisher must create and push only this generated `cto/*` branch and write Michael's review note. Michael retains merge, release and deployment authority. No live acceptance or email send is part of this repair workspace.

## Activation and rollback

After approved merge, build/install the exact immutable Project Hub weekly skill release to `lhm_brain` and `lhm_project_manager`, and the exact System Ops Codex client/worker release through the root-owned installer. Preserve job `a295f78522d7`'s hourly gate, Monday-noon Australia/Melbourne behavior, fixed sender/recipients and weekly receipts. Update only that job's wake-agent body to the persisted scheduled prompt. Before any normal send, run a controlled live fixture through `lhm-codex-dispatch`, require a subscription-backed Codex receipt with the exact workflow/week and render its brief without invoking `send`. Do not run a real email test from this repair.

If the live fixture fails, pause only `a295f78522d7`, restore the prior System Ops client/worker bytes and both prior standalone skill links, and retain all queue incidents and weekly delivery receipts. Do not fall back to Hermes/default DeepSeek or another provider. Other jobs and global model configuration remain untouched.
