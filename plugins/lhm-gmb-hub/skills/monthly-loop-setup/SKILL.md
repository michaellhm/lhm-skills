---
name: monthly-loop-setup
description: "Set up (or update) a recurring automated monthly GMB optimisation run for a client — a scheduled task that works the client's GMBProjectManagement.md checklist, stages any site changes on a branch, creates a BasicOps follow-up task, and notifies the team via Telegram and email. Use this when the user says 'set up the monthly GMB loop for [Client]', 'automate the GMB cycle for [Client]', 'turn on the monthly loop', 'create a scheduled GMB run', or wants to repurpose an existing client's loop for a new client."
---

# Monthly Loop Setup

Creates a `create_scheduled_task` cron job that runs the GMB monthly cycle end-to-end for one client: works the outstanding checklist items in `GMBProjectManagement.md`, stages any site edits on a branch (never merges), updates the PM doc, creates a BasicOps task with per-action sub-tasks, and sends a Telegram + email summary. This skill only sets up the automation — it does not itself run the monthly work.

This was first built and proven out manually for Align Health Co (see `${CLAUDE_PLUGIN_ROOT}/skills/monthly-loop-setup/references/loop-prompt-template.md` — that template is the distilled, working version). Use this skill to repeat the setup for any other client without re-deriving it from scratch.

## Before Starting

Read `${CLAUDE_PLUGIN_ROOT}/skills/monthly-loop-setup/LEARNED.md` if it exists — it captures gotchas discovered on prior setups (e.g. Telegram/Mailgun auth quirks below).

## Step 1: Identify the client and confirm prerequisites

1. Confirm which client. Locate `[client_folder]/gmb/GMBProjectManagement.md`.
2. **If it doesn't exist:** this client hasn't been onboarded for GMB yet. Route to the `gmb-project-manager` skill / `gmb-orchestrator` agent first — the loop needs a PM doc to work from. Don't proceed with loop setup until it exists.
3. Check for a website repo (Astro, WordPress, or otherwise) under the client folder — look for a `website/` or similar directory with a `.git` repo. Note whether it exists, its path, its default branch, and whether `git status` on the default branch is currently clean or has pending uncommitted work. If there's no site repo yet, the loop simply skips the site-staging section entirely.

## Step 2: Collect the config

Ask the user (batch these into one AskUserQuestion round where possible — most have sensible LHM-wide defaults):

1. **Telegram destination** — which group/chat should get monthly updates? Reuse the existing LHM Zapier Telegram bot (check `list_enabled_zapier_actions` for `TelegramCLIAPI` — it's already connected agency-wide, no new integration needed per client). The bot must be a member of the target chat AND that chat must have at least one message sent in it, or Zapier's dynamic chat_id lookup returns nothing — call this out explicitly, it bit us on the first setup. Confirm chat_id resolves via `list_enabled_zapier_actions` with `tool_name: "telegram_send_message"`, `enum_property: "chat_id"`, `enum_search: "<chat name>"` before finishing setup.
2. **Email recipients** — who gets the monthly report email? Default to the standing LHM team distribution (confirm current addresses with the user rather than assuming) unless they want different/additional recipients (e.g. add the client's own contact). Mailgun is already connected agency-wide (`MailgunCLIAPI`, domain `mail.patienthub.app`, action `mailgun_send_email` / key `createEmail`) — no new integration needed.
3. **BasicOps target** — default to the shared `*Client Flow` project, `Delivery` section (same board every client's monthly task lands in, distinguished by title `[Client Name] - [Month] GMB`). Call `list_projects` / `list_sections_in_project` to get current IDs rather than hardcoding — IDs can differ per workspace. Ask who the default assignee should be for the main task (a specific team member, or leave unassigned).
4. **NotebookLM fallback** (optional) — does this client have a dedicated infrastructure/process notebook to fall back to when the loop gets stuck? If not, skip this section of the prompt.
5. **Astro/site staging behaviour** (only if a site repo exists) — confirm: create/push a `gmb-cycle-YYYY-MM` branch off the default branch for any site edits, never merge or push to the default branch directly. If the default branch currently has pending uncommitted work unrelated to GMB, the loop should skip all site-editing checklist items that run and flag it instead — confirm this is still what the user wants.
6. **Schedule** — default 1st of the month, 8am local time (`0 8 1 * *`). Confirm or adjust.

## Step 3: Generate the task prompt

Read `${CLAUDE_PLUGIN_ROOT}/skills/monthly-loop-setup/references/loop-prompt-template.md` and fill in every `{{PLACEHOLDER}}` with the values collected above. If there's no site repo, delete the "Astro/site staging workflow" section and its references entirely rather than leaving it in with empty values. If there's no NotebookLM notebook, delete that fallback line.

## Step 4: Create the scheduled task

Call `create_scheduled_task` with:
- `taskId`: `<client-slug>-gmb-monthly-loop`
- `description`: one line, e.g. "Monthly GMB optimisation cycle for [Client] — works the PM checklist, stages site changes, creates a BasicOps task, and reports via Telegram + email"
- `cronExpression`: from Step 2.6
- `prompt`: the filled-in template from Step 3
- `notifyOnCompletion`: true

## Step 5: Report back and recommend a live test

Tell the user:
- The task ID, schedule, and next run time
- That scheduled tasks only run while the app is open — if closed on run day, it fires on next launch
- Recommend running a live test now (dispatch the same prompt via the Agent tool in the current session) rather than waiting for the real scheduled run, so any auth/config issues (Telegram chat not yet active, Mailgun needing re-auth, wrong BasicOps IDs) surface immediately instead of on the 1st.
- If a live test is run and finds broken config, fix it and update the scheduled task with `update_scheduled_task` rather than leaving the cron prompt untested.

## Known gotchas (learned from the Align Health Co build)

- **Telegram dynamic chat_id lookup returns empty** if the bot hasn't received any message in the target chat yet — this is a Telegram API limitation (bots can't see a chat until they've gotten a message in it), not a Zapier bug. Always have the user send one test message in the target chat before finishing setup.
- **Mailgun connector can silently need re-auth** even after being "enabled" — the Zapier action set differs depending on auth state (bare-enabled gives only validation/mailing-list actions; authenticated gives the real `createEmail` "Send Email" action). Confirm `mailgun_send_email` (key `createEmail`) is actually present in `list_enabled_zapier_actions` before relying on it.
- **BasicOps `@mentions` in messages**: the `create_message_in_task` tool only accepts raw HTML with no documented mention microformat. Plain `@Name` text is stored as literal text, not confirmed to trigger a real mention/notification. If real notifications matter, prefer setting the **assignee** field (confirmed to work) over relying on `@mention` text in a discussion message until the correct mention syntax is confirmed.
- **A freshly-launched background orchestrator agent can stall** after fanning out parallel sub-agents without returning to do its own follow-up steps (PM doc update, notifications). If a background agent goes quiet, use `SendMessage` to resume it explicitly with the remaining steps, or just do the remaining steps directly rather than waiting indefinitely.
