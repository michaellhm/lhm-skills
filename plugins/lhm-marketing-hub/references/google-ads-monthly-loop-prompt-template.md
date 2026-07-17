---
title: Google Ads Monthly Loop — Scheduled Task Prompt Template
description: Parameterized prompt registered via the scheduled-tasks MCP by skills/google-ads-monthly-loop/SKILL.md. Fill in every {{PLACEHOLDER}} before creating the task.
---

# Template

Copy the block below, substitute every `{{PLACEHOLDER}}`, and pass the result as the `prompt` argument to `create_scheduled_task`.

Placeholders:
- `{{CLIENT_NAME}}` — e.g. "Your Story Physiotherapy"
- `{{GOOGLE_ADS_CUSTOMER_ID}}` — digits only
- `{{MCC_ID}}` — usually `3947361921`
- `{{ADPULSE_BUDGET_ID}}` — `bdg_...`, from `references/adpulse-integration.md` lookup
- `{{EMAIL_TO}}` — who receives the monthly summary
- `{{BASICOPS_PROJECT_ID}}` / `{{BASICOPS_SECTION_ID}}` — default `49020` / `106309` (Michael Tasks / Google Ads Flow) unless told otherwise
- `{{CRON_EXPRESSION}}` and `{{DATE_GUARD}}` — see the cadence note in `skills/google-ads-monthly-loop/SKILL.md` Step 4 (cron can't express "nth weekday of month" directly — most cadences need a date-guard check at the top of the prompt)

---

This task runs on the schedule `{{CRON_EXPRESSION}}`, but should only actually execute when: {{DATE_GUARD}}. First check today's date against that condition. If it does not match, stop immediately and do nothing else. If it matches, proceed with the full monthly Google Ads review below for the client "{{CLIENT_NAME}}".

## Objective
Run a monthly Google Ads performance review for {{CLIENT_NAME}}, get an independent second opinion from a 4-avatar panel, decide what to prioritize, and hand off actionable instructions to the account owner — you never have direct write access to Google Ads.

## Step 1 — Analyze the account
Invoke the `google-ads` agent (or `/lhm-marketing-hub:start-googleads`) for the client "{{CLIENT_NAME}}", session type "monthly check-in". This reads the agent's context preamble, philosophy, and agency learnings automatically — trust that pipeline rather than re-deriving it here. It will pull Google Ads data (customer id `{{GOOGLE_ADS_CUSTOMER_ID}}`, under MCC `{{MCC_ID}}`) for the last 30 days vs prior 30 days: spend, conversions, CPA, search terms, keyword performance, device split, conversion action configuration (don't assume last cycle's tracking fixes stuck — re-check).

The agent will pull AdPulse zone data directly (budget id `{{ADPULSE_BUDGET_ID}}`) per `references/adpulse-integration.md` — don't hand-calculate pacing/performance. If the zone lands on the Under-pacing + Poor performance gap described in that reference, treat it as Red-severity and say so explicitly.

Use the matched zone's Execution Checklist (from `skills/google-ads-monthly-review/SKILL.md`) to ground what this cycle's priorities actually are.

## Step 2 — Draft suggestions
From the analysis and the matched zone's checklist, draft up to 5 concrete, prioritized suggestions. Each states: what to change, why (the data), expected impact.

## Step 3 — Second opinion via 4-avatar panel
Create 4 distinct avatars and have each critique/rank the draft suggestions:
1. **Digital marketing expert** — broad paid-media best-practice lens
2. **Experienced clinic owner** (or equivalent business-owner lens for this client's industry) — practical, revenue lens, skeptical of anything that doesn't clearly drive the core conversion
3. **Media buyer expert** — tactical PPC lens (bid strategy, budget allocation, auction dynamics)
4. **Perry Marshall** — direct-response/80-20 lens (concentration on what works, ruthless cutting of waste)

Route each avatar through a genuinely different model via the OpenRouter MCP (`send-message`/`list-models`). Pick current, comparable-tier models across providers (one GPT, one Gemini, one Grok) rather than defaulting to the same slugs every time — check `list-models` for what's current. "Manus" has no callable API — substitute a distinct-lineage model (e.g. DeepSeek) for that persona and disclose the substitution. If OpenRouter is unavailable, fall back to distinct in-model personas and flag that it was single-model simulated.

## Step 4 — Final decision
Synthesize analysis + zone/checklist + suggestions + panel feedback into a final prioritized list. Note where the panel agreed unanimously vs diverged, and why anything was deprioritized.

## Step 5 — Output
Never make changes in Google Ads directly. Finish with:

1. **Email** — via Gmail (Zapier MCP: check `list_enabled_zapier_actions` first). To: `{{EMAIL_TO}}`. Subject: "{{CLIENT_NAME}} — Google Ads Monthly Review [Month Year]". Body: concise — zone/checklist headline, key findings, what you decided and why, pointer to BasicOps for the rest.

2. **BasicOps task** (BasicOps MCP — if not authorized, say so in the completion summary):
   - Project id `{{BASICOPS_PROJECT_ID}}`, section id `{{BASICOPS_SECTION_ID}}`
   - Task title: "{{CLIENT_NAME}} - Month Flow"
   - Task **description**: one line pointing to the discussion + the saved report file. Do NOT put the full report in the description field.
   - Post the full report (zone, findings, panel synthesis, decision) as a **discussion message** via `create_message_in_task` — that's where the report content belongs.
   - One **subtask per action item**, each with a direct, actionable instruction assuming the account owner already knows how to execute it in the Google Ads UI (e.g. "Upload these negative keywords: [list]"). Include exact specifics (keywords, bid/budget numbers, ad copy lines).

3. **Save the report** to `google_ads/YYYY-MM/monthly-review-YYYY-MM.md` in the client folder (one-pager per the skill's format), including the matched zone's checklist with items marked off based on what this cycle covered.

## Constraints
- Data-driven, profitability-first — not activity for its own sake.
- Keep the email and BasicOps description short. The discussion message can be fuller but still tight.
- Always pull AdPulse's pacing/kpiPercentage directly — that's the point of the integration.
- If Google Ads MCP, AdPulse MCP, or OpenRouter access isn't available when this runs, say so clearly in the completion summary rather than fabricating numbers or skipping silently.
