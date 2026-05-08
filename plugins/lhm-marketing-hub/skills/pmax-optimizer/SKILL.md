---
name: pmax-optimizer
description: Optimise an existing Performance Max campaign for an Australian local-service business. Runs either a monthly tactical optimisation pass or a 90-day strategic review. Use this when the user mentions "optimise PMax", "PMax optimisation", "Performance Max review", "PMax monthly", "PMax 90-day", "PMax quarterly", "fix Performance Max", "improve PMax performance", "PMax not converting", "PMax CPL too high", or routes from the google-ads-monthly-review agent for a PMax-heavy account. Outputs a prioritised action list with AdPulse zone mapping and routes to bid-budget-optimizer, pmax-banner-generator, or landing-page-optimizer where appropriate.
---

# PMax Optimizer (Local Business)

## Purpose

Run a structured optimisation pass on an existing Performance Max campaign for an **Australian local-service business**. Two modes:

- **Monthly tactical pass** - every month, walks the 15-item monthly checklist.
- **90-day strategic review** - quarterly, walks the 30-item 90-day checklist (15 monthly + 15 strategic) (includes everything monthly, plus structural decisions).

Pulls live data via the Google Ads MCP, walks the checklist, scores the campaign against the AdPulse zone framework, and produces a prioritised action list with skill-routing instructions.

## CRITICAL - Local Business Only

This skill is for lead-gen / call-gen / visit-gen PMax. If the campaign is eCommerce / Shopping (has a Merchant Center feed, product groups, or Sales as the objective), refuse and tell the user to use a Shopping-focused workflow.

Detect by asking the user OR by GAQL:
```sql
SELECT campaign.id, campaign.name, campaign.advertising_channel_type, campaign.advertising_channel_sub_type
FROM campaign
WHERE campaign.id = [campaign_id]
```
If `advertising_channel_sub_type` includes `SHOPPING_*`, stop.

## When to Use

- Monthly client review where the dominant channel is PMax
- Routed from `google-ads-monthly-review` when PMax is > 50% of account spend
- After a PMax campaign has been live for ≥ 14 days and the user wants the first sense-check
- Quarterly strategic review for a mature PMax campaign
- "PMax CPL is rising / volume is dropping" troubleshooting

## Mode Selection

At the start of the run, ask:

> "Monthly tactical pass, or 90-day strategic review?"

Default to **Monthly** unless ≥ 85 days have passed since the last 90-day review (check the client's `google_ads/` folder for prior `pmax-optimisation-90day-*.md` files).

Refuse if:
- Monthly pass with < 14 days of campaign data - too early to read.
- 90-day review with < 60 days of campaign data - not enough history.

## Pre-flight

1. Read these three files first, in order:
   - `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` - applies to every recommendation, action, and report line.
   - `${CLAUDE_PLUGIN_ROOT}/skills/pmax-optimizer/LEARNED.md` - apply prior-session learnings to this run.
   - `client_profile.md` for the active client.
2. Confirm CID under MCC `394-736-1921` via `mcp__GoogleAds__list_accessible_accounts`.
3. Confirm campaign is local lead-gen, not Shopping (GAQL above).
4. Confirm reporting window:
   - Monthly: last 30 days vs prior 30 days.
   - 90-day: last 90 days vs prior 90 days.
5. Read prior optimisation reports in `clients/<slug>/google_ads/` for context (last month's actions, unresolved items).
6. Read `pmax-banner-generator/references/ahpra-pmax.md` for the banned-language list.

## Data Pull via Google Ads MCP

Run the queries in `references/gaql-queries.md` against the campaign. Pull all of:

- Campaign-level performance (cost, conversions, CPA, conversion rate, impressions, search impression share lost-to-budget, lost-to-rank).
- Asset-group-level performance (same metrics, per group).
- Asset performance ratings (BEST / GOOD / LOW per asset type per group).
- Audience-signal performance (where the API exposes it).
- Conversion-action breakdown (form vs call vs location vs lead form).
- Geo-performance breakdown (sub-locations within the targeted area).
- Final URL expansion landing-page report (only relevant if expansion is ON).
- Brand vs non-brand spend split (use a brand-term filter on the search-terms / Insights export).

If the MCP cannot return the search-terms / Insights data (some MCC permissions block it), instruct the user to export the **Insights** report from the Google Ads UI and place it in `clients/<slug>/google_ads/YYYY-MM/insights-export-YYYY-MM.csv`. Do not fabricate the data.

## Run the Checklist

Load the right checklist:

- Monthly tactical → `references/monthly-checklist.md`
- 90-day strategic → `references/90-day-checklist.md`

Walk every item. For each item, produce a row:

| Item | Status | Evidence | Recommended Action | Owner | Routing |
|------|--------|----------|--------------------|-------|---------|
| [Checklist line] | ✅ / ⚠️ / 🔴 | Specific number from GAQL | One sentence, specific | LHM / Client | Skill name + parameters |

Do not guess. Every status must be backed by a number from the data pull.

## AdPulse Zone Mapping

Map the campaign's findings to an AdPulse zone using the same framework as `google-ads-monthly-review`. PMax-specific thresholds live in `references/adpulse-pmax-mapping.md`.

The zone is for **this campaign**, not the whole account. Note this clearly in the output so it doesn't confuse a reader who's also seen the account-level zone.

## AHPRA Compliance Gate

Before any new copy / creative / landing-page suggestion is written into the action list, run it through the AHPRA banned-language check (see `references/ahpra-pmax-quick-ref.md`). Healthcare clients only. Non-healthcare local services (legal, accounting, trades) get the equivalent industry compliance pass instead.

## Action List & Routing

Produce a prioritised action list at the top of the report. Each action specifies which skill to run next:

| Trigger | Route to |
|---------|----------|
| ≥ 3 LOW assets in any group | `pmax-banner-generator` (list specific asset IDs to refresh) |
| Budget pacing < 90% AND zone Yellow | `bid-budget-optimizer` (recommend scale-up) |
| Budget pacing > 110% AND zone Red/Orange | `bid-budget-optimizer` (recommend pull-back) |
| LP score < 6/10 OR LP-experience flag in data | `landing-page-optimizer` |
| Conversion action firing inconsistently | `analytics-tracking` or `ga-event-config` |
| Search-terms list reveals new negatives | Inline (add directly to the negative keyword list) - flag in the action list |
| Audience signal under-performing | Inline (refresh signal in the asset group) - flag in the action list |
| 90-day: account-level structural change | Document the recommendation; route to `bid-budget-optimizer` if budget-impacting |

## Output

Save to:

```
clients/<slug>/google_ads/YYYY-MM/pmax-optimisation-<monthly|90day>-YYYY-MM.md
```

Structure:

```markdown
# PMax Optimisation - [Client] - [Monthly | 90-Day] - YYYY-MM
Date: [YYYY-MM-DD]
Reporting window: [from] to [to]

## Action List (Top of Report)
1. [Action] - [Owner] - [Skill to run next] - [Due]
2. ...

## Zone (PMax Campaign): [Emoji] [Zone] - [Priority]

### Headline Numbers
- Spend: $X (vs $Y prior period - [Up/Down] X%)
- Conversions: X (vs Y - [Up/Down] X%)
- CPL: $X (vs $Y - [Improved/Worsened])
- Conv mix: form X% / call X% / location X% / lead form X%
- Search IS lost (budget): X%
- Search IS lost (rank): X%

### Checklist Walkthrough
[Table - every checklist item with status, evidence, action, owner, routing]

### Routing Summary
- pmax-banner-generator: [yes/no - specifics]
- bid-budget-optimizer: [yes/no - specifics]
- landing-page-optimizer: [yes/no - specifics]
- analytics-tracking / ga-event-config: [yes/no - specifics]

### Notes / Open Questions
[Anything that needs the operator's judgment]
```

The action list goes at the **top** so the operator can act inside 5 minutes.

## Related Skills

- **pmax-campaign-setup** - for building the campaign in the first place.
- **pmax-banner-generator** - for creative refresh on LOW assets.
- **bid-budget-optimizer** - for budget / bid-strategy changes.
- **landing-page-optimizer** - for LP issues.
- **google-ads-monthly-review** (skill / agent) - for account-level zone check that may have routed here.

## Reference Files

- `references/monthly-checklist.md` - 15 tactical items, every month.
- `references/90-day-checklist.md` - 25 strategic items, every quarter (includes monthly).
- `references/gaql-queries.md` - every GAQL query the skill runs.
- `references/adpulse-pmax-mapping.md` - PMax-specific zone thresholds.
- `references/ahpra-pmax-quick-ref.md` - banned-language list for the compliance gate.

---

*PMax rewards cadence. Run the monthly. Don't skip the 90-day.*
