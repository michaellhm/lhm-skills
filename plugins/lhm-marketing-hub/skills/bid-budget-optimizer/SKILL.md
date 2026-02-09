---
name: bid-budget-optimizer
description: "Campaign-by-campaign Google Ads performance review with bid strategy and budget recommendations. Use this when users request budget optimization, bid strategy changes, budget pacing fixes, spend control, budget reallocation, scaling campaigns, or period-over-period performance comparison."
license: MIT
---

# Bid & Budget Optimizer

## Purpose

Review each campaign's performance vs the previous period, make a short call on what's happening, and recommend bid strategy and budget changes. No waffle — one block per campaign, done.

## When to Use

- After a monthly review identifies budget or bid issues
- Mid-month corrections when pacing is off
- Reviewing what changed after bid strategy adjustments
- Scaling or cutting campaigns based on performance

## Data Required

You need **two periods** of campaign data to compare. Default: last 30 days vs the 30 days before that.

### Option A: Google Ads MCP (Preferred)

Fetch from MCC **394-736-1921**. Pull two periods of campaign-level data:

**Metrics needed per campaign:**
- Impressions, Clicks, Cost
- Conversions, CPA, Conversion Value
- Current bid strategy
- Current daily budget

### Option B: CSV Fallback

Ask the user for campaign data covering both periods, or two separate exports (current period + previous period).

## Context to Gather

Before running the review, confirm:
1. **Client name**
2. **Monthly budget target**
3. **Target CPA or ROAS**
4. **Any recent changes** (bid strategy switches, budget adjustments, paused campaigns)

Skip anything already known from `client_profile.md`.

## Output Format

Produce **one block per campaign**. Each block follows this exact structure:

```
## [Campaign Name]

Impressions: [Up/Down] X% (current vs previous)
Clicks: [Up/Down] X% (current vs previous)
Cost: [Up/Down] X% ($current vs $previous)
Conversions: [Up/Down] X% (current vs previous)
CPA: [Improved/Worsened] from $X to $X
Conversion Value (Est.): $current vs $previous

➡️ Comment: [1-2 sentences on what's happening — what improved, what's concerning, or what needs attention.]

### Bid Strategy

[Current strategy and any recent changes]
[1-2 line recommendation with specific numbers — what to switch to, what target to set, or why to keep it]

### Budget

[1 line recommendation — specific daily budget number with brief reasoning]
```

### Rules for the output

- **Always show the direction** — "Up 25%", "Down 18%", "Flat" — never just raw numbers
- **Always show both values** — "(139 vs 86)", "($189.73 vs $72.14)"
- **Comments are 1-2 sentences max** — no hedging, no filler
- **Bid strategy recommendations are specific** — "Switch to Max Conversions with $25 target CPA", not "consider changing strategy"
- **Budget recommendations are one line** — "$15/day (up from $10)" or "Pause — CPA 3x target with zero trend improvement"
- **If a campaign should be paused, say so directly**
- **If a campaign is performing well, say so and move on** — don't invent problems

### Handling edge cases

- **New campaign (no previous period)**: Note "New campaign — no comparison period" and comment on early signals only
- **Paused campaign**: Note it's paused, state why if known, recommend whether to keep paused or reactivate
- **Zero conversions**: Flag clearly, recommend action based on spend level and click volume

## After All Campaigns

End with a short summary block:

```
## Summary

Total Cost: $X → $X ([Up/Down] X%)
Total Conversions: X → X ([Up/Down] X%)
Blended CPA: $X → $X
Monthly Budget Target: $X | Current Daily Total: $X/day | Projected: $X/month

[1-2 sentences: overall direction and the single most important thing to do next]
```

## Output File

Save to: `google_ads/YYYY-MM/bid-budget-review-YYYY-MM.md`

## Safety Guardrails

Apply these silently — don't explain them in the output unless a recommendation hits one:

- **Max 20% daily budget increase** for Max Clicks, Max Conversions, or Max Conversion Value campaigns
- **Gradual large changes**: If recommending >30% budget cut, note "gradual reduction over 2-3 days" in the budget line
- **Total budget check**: Ensure recommended daily budgets don't exceed monthly target

## Related Skills

- **Google Ads Monthly Review**: Run first to identify zone and budget issues
- **Keyword Optimizer**: If budget issues stem from keyword waste
- **Ad Copy Generator**: If performance issues need creative refresh

---

*Short, sharp, campaign by campaign*
