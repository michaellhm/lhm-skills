# VPS Codex integration upgrade

The registered RTB route supports `codex_task_submit(task_id, instruction_message_id)` when `direct_task_intake` is enabled. It binds the task description and the registered human's durable BasicOps instruction; TED need not invent a plan for ordinary draft preparation. Existing approved-plan admission remains compatible. The RTB pilot still limits automatic host delivery to new review files and a source review branch. Main pushes or staging deployment must use an explicitly authorized integration action; this change does not publish the existing RTB branch.

## Installed integration shape

- LHM plugin skill sources are installed read-only outside client workspaces and exposed through `~/.agents/skills`. Supporting references remain alongside the source skills. This makes skills available; it does not authenticate every service mentioned in them.
- GitHub official MCP server 2.0.3, verified against the vendor release checksum, runs as the Codex worker. A launcher obtains its runtime token from that worker's explicitly authorized normal `gh` login, never from another profile or source files. Repository access follows the signed-in account. Git and GitHub MCP are complementary.
- `workspace-mcp==2.1.2` runs from its own Python environment with only Drive and Docs services enabled. It has its own normal Google consent and dedicated credential store. Existing host rclone delivery remains separate. Never copy unrelated cached credentials or claim registration proves connectivity.
- The Google OAuth app is currently in Testing; renewal can be needed after seven days. Move to an appropriate production/internal OAuth setup before relying on long unattended schedules.
- The VPS requires its own account connections. Installing a skill is not equivalent to having its remote service, browser or platform-specific dependency.

## Regression repairs

The TED BasicOps webhook toolset must include `codex_sessions`, and the MCP include list must include `codex_task_submit`, `codex_session_submit` and `codex_session_status`. Protected workspace `.git`, `.codex` and `.agents` mount anchors prevent bwrap launch failures without broadening writable directories. A previous failed notification must not suppress a later successful handback. Assign the reviewer before the native review request, because changing the assignee afterwards resets BasicOps review state.

## Verification

The direct-intake tests reject AI relays and retain idempotent approval binding. Old bridge, worker and delivery tests remain required. Live checks must include MCP discovery, an authenticated repository read, Codex skills/list, authenticated Drive folder read and an explicitly scoped write/readback test before claiming editing is verified. A rendered prototype preview remains a separate check. Do not use a paid model turn merely as a health probe.
