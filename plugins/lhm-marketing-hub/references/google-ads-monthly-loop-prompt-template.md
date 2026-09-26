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
Prepare the complete monthly Google Ads decision pack for {{CLIENT_NAME}} before Michael starts work: load canonical Obsidian context, run the required read-only/prepare-only specialists, save and verify one combined Drive review plus any implementation files, and only then create or update the BasicOps review record. Do not perform live Google Ads mutations in this scheduled run.

## Step 1 — Analyze the account
Invoke the `google-ads` agent for the client "{{CLIENT_NAME}}", session type "monthly check-in", and follow `references/google-ads-monthly-operating-model.md`. Hermes first resolves the canonical Obsidian service file and passes a context envelope with objectives, conversion definitions, locations, budget/targets, strategy, open issues, prior decisions and commitments, Drive destination and existing BasicOps task. Never create blank local context files.

Pull Google Ads data (customer id `{{GOOGLE_ADS_CUSTOMER_ID}}`, under MCC `{{MCC_ID}}`) for the current 30 days and immediately preceding 30 days using aligned definitions: spend, conversions, CPA, search terms, keyword performance, device split and conversion action configuration. Reconcile each prior commitment against live settings. Run `bid-budget-optimizer` read-only for every active campaign and return keep/change/insufficient-evidence. When PMax is active, run the read-only monthly tactical `pmax-optimizer` slice. When Search is active, run the read-only/prepare-only `keyword-optimizer` slice even if first-pass evidence does not yet show obvious waste; produce the Editor CSV and negative TXT when evidence supports changes. Run `google-ads-conversion-audit` for account and campaign goal settings; use GA4 over the same windows when Ads evidence is unclear.

Pull AdPulse zone inputs directly (budget id `{{ADPULSE_BUDGET_ID}}`) per `references/adpulse-integration.md`. If unavailable, calculate the mechanical result and label it `manual_fallback`. Report **performance zone** separately from **measurement confidence**. A tracking concern lowers confidence or makes the zone unclassified; it does not automatically create a Red performance zone.

Use the matched zone's Execution Checklist (from `skills/google-ads-monthly-review/SKILL.md`) to ground what this cycle's priorities actually are.

## Step 2 — Resolve the top five
After the mandatory and evidence-triggered specialists return, select no more than five resolved actions. State the exact change, retention decision or bounded investigation, why, expected outcome, producing/owning skill and whether a live mutation requires approval. Do not return “run a skill”, “confirm whether”, “review” or “clean up” when a specialist can resolve the recommendation now.

## Step 3 — Optional second opinion
Do not make an external panel a dependency of the scheduled review. Only obtain a second opinion when Michael has requested it or the evidence produces a genuinely borderline strategic call. Disclose the model and result; an unavailable connector must not block the handoff.

## Step 4 — Hermes decision brief
Preserve Hermes' concise presentation: four-line state summary, short campaign breakdown, headline findings, separate performance-zone and measurement-confidence lines, and the numbered top five. Include the structured YAML handback from the operating model so the flow can resume in a later conversation.

## Step 5 — Output
Never make changes in Google Ads directly. Finish with:

1. **Save and verify the complete manifest before any notification or decision handoff.** The Google Ads worker owns these artefacts. Read the exact Google Drive destination from the client's canonical service file and save `google-ads-monthly-review-YYYY-MM.md` in the governed `google_ads/YYYY-MM/` folder. This one document contains the executive review, conversion, bid/budget, keyword and PMax findings, other triggered evidence, the implementation checklist and a separate `Michael approval required` section. Save implementation files separately only where directly useful, normally `keyword-changes-<client-slug>-YYYY-MM.csv` and `negative-keywords-<client-slug>-YYYY-MM.txt` when Search evidence supports changes. Link every implementation file from the combined review and read each one back. Return every observed URL and byte count. Do not use an inferred local path or claim completion without readback.

   Before the BasicOps mutation, verify a manifest containing the combined review plus every file promised by a specialist result. Require terminal, QA-passed receipts for bid/budget, conversion, active-Search keyword and active-PMax diagnostics. If a required child, file, upload or readback is incomplete, return `analysis complete; delivery incomplete`, name the first incomplete stage, preserve its run ID and do not create the decision handoff yet.

2. **BasicOps review task** — route this mutation through the configured ChatGPT/Codex delivery worker and `lhm-project-hub:basicops-task-manager`; Hermes does not require a direct BasicOps connector:
   - Project id `{{BASICOPS_PROJECT_ID}}`, section id `{{BASICOPS_SECTION_ID}}`
   - Task title: "{{CLIENT_NAME}} - Month Flow"
   - Task **description**: use the exact semicolon-delimited `LHM metadata:` line required by `lhm-project-hub:basicops-task-manager`. For this handoff set `handoff_trigger=waiting; next_handoff=Michael via Hermes; handoff_channel=basicops; orchestration_owner=hermes; workflow_state=waiting-on-michael-via-hermes; approval_status=pending-michael`, then add only useful report/workflow URLs. Do not create a second metadata format.
   - Post key metrics, the campaign breakdown with bid-strategy verdicts, performance zone, measurement confidence, resolved top five, matched-zone optional checklist, the combined review URL, applicable implementation-file URLs and the exact approval question as a discussion message. State that Michael should respond through Hermes and that Hermes will resume from the structured state.
   - Do **not** create execution subtasks before approval. After approval, Hermes may create/link only the approved execution subtasks and must follow the BasicOps task-creation rules.

3. **Optional email** — only when this loop was explicitly configured to send one. Keep it to the performance zone, measurement confidence, key findings, and links. Say that proposals await Michael's direction through Hermes; do not claim a decision has been made.

4. **Hermes record and handoff** — after the delivery worker returns verified Drive and BasicOps URLs, Hermes records the structured handback in the canonical Obsidian service file. Use `dispatch_ready` when a dependency-ready Lead action exists, even if another action waits for Michael; otherwise use `waiting_michael_hermes` for an exact consequential decision. If any required URL is missing, say `analysis complete; delivery incomplete` and preserve the delivery run ID for resumption. Dispatch exactly one approved implementation action at a time. After each handback, update Obsidian and BasicOps before starting another.

## Constraints
- Data-driven, profitability-first — not activity for its own sake.
- Keep the email and BasicOps description short. The discussion message can be fuller but still tight.
- Always pull AdPulse's pacing/kpiPercentage directly — that's the point of the integration.
- If Google Ads, GA4, AdPulse or BasicOps access isn't available, say so clearly and lower confidence or set `needs_review` as appropriate. OpenRouter is optional.
