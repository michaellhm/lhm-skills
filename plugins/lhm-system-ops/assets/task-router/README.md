# TED central provider routing

Michael can ask `@Ted can we work on this?` on an identified client task. The installed webhook skill acknowledges, previews the central decision, claims the task, and submits the exact personal instruction. No provider wording or TED plan is required for ordinary draft execution. Assignment alone is not a work request.

Policy v1 selects Claude for research, writing, analysis and planning; Codex for website/code or connected Workspace work, including mixed document/website tasks. Only the verified personal instruction may override the provider. There is no silent fallback. The client comes from existing task bindings or one exact registered name in the task; unknown/ambiguous identities use the governed handback registration rather than guessed paths. Existing pilot sessions are preserved.

The MCP surface is `task_route_preview`, `task_route_submit`, `task_route_status`. `server.py` reuses TED's authenticated connector. `router.py` verifies author, exact message, owner, live task, instruction digest and client. The host re-verifies the whole contract immediately before execution. The admission receipt is durable before process launch; restart never resubmits an admitted run. New personal feedback after a terminal result resumes the same provider/session. A later stop blocks admission; already-running work requires explicit worker/chat interruption and verification.

`dispatch.py` runs from a systemd timer, snapshots at most 32 registered client markdown files/160KB and starts non-root systemd workers. Private homes, strict filesystem protection and task-specific write directories isolate the runtime from Hermes/root. Protected Codex workspace anchors remain root-owned. Queue result directories are root-owned and not group-writable. Untrusted queue/output reads reject symlinks and oversized files; request IDs never become shell code.

Codex uses the maintained native app-server conversation function and saves the chat on paired `hermes-vps`. Its central route allows read tools only on Workspace/GitHub MCP; the worker prepares files locally. Claude uses the existing authenticated account, installed skills and Read/Write/Edit/Skill tools, with no MCP or shell and session persistence enabled. Its transcript is resumable on the VPS; it does not automatically appear in the Claude app. An unavailable live tool is an evidence gap, not a fabricated completed action.

The supervisor copies the actual result and returns it once to the source BasicOps Discussion, with the selected provider/session. It leaves the task open. A draft is not verified Drive delivery or business completion; TED must use the existing governed delivery route for already-authorised file delivery. Publishing, main pushes and client sends remain separately scoped actions. Full arbitrary-task live write integration is not claimed by this initial central route.

## Install / rollback

Stage `router.py`, `server.py`, `worker.py`, `dispatch.py`, `install.py`, the host `lhm-codex-session-worker` and the BasicOps webhook `SKILL.md` together. Run `install.py` as root. It backs up the previous files/config, adds the MCP server to both server configuration and webhook toolsets, and installs `lhm-task-router.timer`. Reload only TED's gateway when idle. Verify MCP discovery through the webhook runtime, both providers, source/live hashes and timer health.

Rollback: stop/disable the new timer, stop only the `lhm-task-ted-route-*` units admitted by this route, restore the backed-up TED config/skill/pilot worker, then reload only TED. Keep saved sessions/results and existing pilot services. Do not erase credentials or revert unrelated configuration.

## Recorded role passes (same runtime)

- Research: existing role policies were workflow-specific, pilot admission was task-specific, and the old Claude worker disabled session persistence. Reused native Codex app-server and normal Claude CLI authentication rather than introducing a new credential service.
- Engineering / skill maintenance: central deterministic policy, shared MCP, live-contract re-verification, isolated provider workers, persistent feedback and additive installer. Canonical branch only; no unrelated source edits.
- QA: routing/identity/duplicates/client ambiguity/stops/restarts/feedback unit tests, existing pilot regressions, and isolated fictional live-provider smoke checks. Both providers created `drafts/smoke.md` containing the required `ROUTER_OK` text and returned `needs_review`; Codex retained a native app-server thread and Claude retained a resumable session. Feedback on both providers retained the original session ID and produced `ROUTER_RESUME_OK`. The three MCP tools were discovered through the live container SDK; TED’s profile gateway was refreshed through its normal supervisor command. A fabricated human BasicOps comment is never used as approval evidence.
- Security: credential contents are never copied; existing authenticated homes remain provider-specific. Preparation has a fixed review ceiling. Central tools do not authorise publication or client sends. No shell interpolation of task data; root consumer reads bounded regular files only.
- Release: source patch/version/catalogue validation and exact installed-asset/remote-commit checks; scoped live router installation only. No merge to main or blanket plugin rollout.
