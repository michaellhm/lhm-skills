---
name: google-ads-monthly-loop
description: "Register a recurring, unattended monthly Google Ads review for a client — analysis, AdPulse zone check, 4-avatar second opinion panel, final decision, client-owner email, and a BasicOps task with subtasks. Use this when the user wants to 'set up the monthly loop', 'automate the Google Ads review', 'schedule the monthly review', or run the google-ads-monthly-review flow on a recurring cadence instead of manually each month."
license: MIT
---

# Google Ads Monthly Loop

## Purpose

Turn the monthly Google Ads review (zone check → suggestions → second opinion → decision → client-owner handoff) into a recurring, unattended scheduled task for a given client, so it runs every month without a human kicking it off.

This skill does not do the review itself — it sets up the loop that will. The review logic lives in `${CLAUDE_PLUGIN_ROOT}/skills/google-ads-monthly-review/SKILL.md` and the `google-ads` agent; this skill's job is to correctly parameterize and register the recurring task, once, per client.

## When to Use

- "Set up the monthly loop for [client]"
- "Automate [client]'s Google Ads review"
- First time a client's monthly review process has proven out manually and should now run on its own
- Not for a one-off review — use the `google-ads-monthly-review` skill (or the `google-ads` agent, monthly check-in) directly for that

## Prerequisites

Check these before registering anything — don't silently proceed if one is missing:

- Client folder exists with `client_profile.md` populated (industry, Google Ads ID, budget)
- `goals.md` exists with conversion economics filled in (revenue per conversion, margin, CPA/ROAS threshold) — the review can't be profitability-first without this. If missing or placeholder-only, ask the user for these numbers now (see the questions asked for Your Story Physio: average revenue per conversion, CPA ceiling, margin after overheads) and write them into `goals.md` before continuing.
- The Google Ads account is reachable via Google Ads MCP under MCC 394-736-1921
- BasicOps MCP is authorized (task/subtask creation, discussion messages)
- A Gmail-send-capable Zapier action is enabled (`list_enabled_zapier_actions`)
- Scheduled-tasks capability is available in this environment

If BasicOps or Zapier aren't authorized yet, still register the loop but say clearly in your confirmation to the user that those steps will fail on the account's first live run until connected.

## How It Works

### Step 1: Resolve the Google Ads customer ID

Read `client_profile.md`. If "Google Ads ID" is filled in, use it. If it's missing or says "(to confirm)": query Google Ads MCP (`list_accessible_accounts`, then GAQL against likely accounts, or ask the user directly) to find the right customer ID, then write it back into `client_profile.md` so future sessions don't have to re-resolve it.

### Step 2: Resolve the AdPulse budget ID

Follow `${CLAUDE_PLUGIN_ROOT}/references/adpulse-integration.md` to find the client's AdPulse budget (`bdg_...`) from the Google Ads customer ID. Write it into `client_profile.md` under an "AdPulse Budget ID" field.

If the account isn't onboarded in AdPulse at all, tell the user — the loop can still run (it'll fall back to the manual pacing calculation in `google-ads-monthly-review/SKILL.md` Step 3) but flag that AdPulse coverage is missing for this client.

### Step 3: Confirm conversion economics

Read `goals.md`. If the Conversion Economics section is missing or only has `$` placeholders, ask the user now:
- Average revenue per completed conversion (may differ by conversion type, e.g. private vs insurance/claim-based patients)
- Target CPA ceiling or ROAS threshold
- Margin after overheads (%)

Write the answers into `goals.md` before proceeding — the panel and priority calls depend on this.

### Step 4: Determine cadence

Ask the user what cadence they want. Offer a default and let them override:

**Default: 3rd Tuesday of the month, 8am.** Cron can't express "nth weekday of month" directly, so this uses a two-part pattern: schedule every Tuesday (`0 8 * * 2`), and have the prompt itself check whether today's day-of-month falls in the 3rd-occurrence range (15–21 inclusive) — if not, it exits immediately without doing anything. This is the `{{DATE_GUARD}}` in the prompt template.

Other common cadences and how to express them:
- **A fixed day of month** (e.g. "the 1st", "the 28th"): no guard needed, cron alone does it (`0 8 1 * *`). Set `{{DATE_GUARD}}` to "N/A — cron alone handles this."
- **Nth weekday of another month** (e.g. "2nd Monday"): same two-part pattern, adjust the weekday field and the day-of-month range (2nd occurrence ≈ days 8–14, 1st ≈ days 1–7, 4th ≈ days 22–28).

Confirm the resulting cron expression and guard condition back to the user before registering.

### Step 5: Determine output destinations

Ask (don't assume):
- **Email recipient** — who should get the monthly summary for this client? (Could be the client owner, an account manager, or both.)
- **BasicOps board/section** — default to "Michael Tasks" (project id `49020`) / "Google Ads Flow" (section id `106309`), but confirm — a different team member may own this client and want it on their own board instead. Use `list_projects` / `list_sections_in_project` to resolve a different board if named.

### Step 6: Generate and register the prompt

Fill in `${CLAUDE_PLUGIN_ROOT}/references/google-ads-monthly-loop-prompt-template.md` with everything resolved above. Call `create_scheduled_task` with:
- `taskId`: `google-ads-monthly-review-<client-slug>` (kebab-case client name)
- `cronExpression`: from Step 4
- `prompt`: the filled-in template
- `description`: one line, e.g. "Monthly Google Ads review + BasicOps handoff for [Client Name]"

### Step 7: Confirm and flag pre-approval

Tell the user: task ID, cadence in plain English, next run time, and that recurring scheduled tasks auto-expire after 7 days of the harness being closed (per the underlying scheduling tool's own behavior — mention if relevant to their setup). Recommend clicking "Run now" once on the new task to pre-approve the tools it'll need (Google Ads MCP, AdPulse MCP, OpenRouter, BasicOps, Zapier) so later unattended runs don't stall on a permission prompt.

### Step 8: Record it

Add a line to `[client-folder]/current-projects.md` under Active: "Google Ads monthly review loop — automated, runs [cadence]".

## Output

Nothing is saved by this skill itself beyond the `client_profile.md` / `goals.md` updates (Steps 1-3) and the `current-projects.md` note (Step 8). The scheduled task's own runs produce the monthly report, email, and BasicOps task per `google-ads-monthly-loop-prompt-template.md`.

## Related Skills

- **google-ads-monthly-review**: the actual review logic this loop calls every cycle
- **quarterly-adversarial-review**: not part of this loop — set up separately if wanted on its own cadence
