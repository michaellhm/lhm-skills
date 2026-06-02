---
name: quarterly-adversarial-review
description: "Adversarial 90-day Google Ads review that red-teams the account against the prior 90 days and assigns an AdPulse zone. Use this when the user mentions 'quarterly review', '90 day review', 'quarter review', 'adversarial review', 'red team the account', 'stress test the account', or 'Q review'. Runs every 90 days as a critical challenge to the account, not a friendly status update."
license: MIT
---

# Quarterly Adversarial Review

## Purpose

Every 90 days, stop trusting the account and attack it. This is a red-team review: assume the account is wasting money and that last quarter's wins were luck until the data proves otherwise. Compare the last 90 days against the prior 90 days, assign the AdPulse zone, and produce a single-page verdict with the matched zone's execution checklist.

The monthly review asks "what zone are we in?" This review asks "what would a sceptical auditor tear apart if they were paid to find the waste?"

## When to Use

- **Quarterly cadence** — every 90 days, on schedule
- **Before a client renewal or budget conversation** — pressure-test the story before the client does
- **After a strong quarter** — challenge whether the gains are real or seasonal
- **When something feels off but the monthly reviews keep coming back green**

## The Adversarial Stance

Run the whole review as a critic, not a cheerleader. Concretely:

- **Assume waste exists.** Your job is to find it, not to confirm the account is fine.
- **Distrust the headline numbers.** A falling CPA can hide a collapsing conversion volume. A rising ROAS can be one fluke order. Always check the counter-metric.
- **Attribute wins to luck first.** Did conversions rise because the work was good, or because it was Q4, a competitor dropped out, or tracking double-counted? Make the account disprove the boring explanation.
- **Hunt the quiet failures.** Zero-conversion spend, impression share lost to budget on winners, ad groups coasting on one keyword, creative that has not changed in 90 days.
- **No hedging in the writeup.** If a campaign should die, say "kill it" — not "consider reviewing".

If you cannot find anything wrong, say so plainly and show the three checks that would have caught a problem. A clean bill of health is a valid verdict — but only after a genuine hunt.

## Data Required

Two 90-day periods to compare. Default: **last 90 days vs the 90 days before that.**

### Option A: Google Ads MCP (Preferred)

Fetch from MCC **394-736-1921**. Pull both periods at campaign level:
- Impressions, Clicks, Cost
- Conversions, CPA, Conversion Value, ROAS
- Impression share, lost IS (budget), lost IS (rank)
- Current bid strategy and daily budget

Also pull the **90-day search terms report** and **90-day keyword report** for the waste hunt.

### Option B: CSV Fallback

Ask the user for two campaign exports (current 90 days + prior 90 days), plus a 90-day search terms export if they want the waste hunt to have teeth. Place files in `google_ads/YYYY-Qn/`.

## Context to Gather

Read `client_profile.md` first. Then confirm only what is missing:
1. Client name
2. Monthly budget target (to derive the 90-day expected spend)
3. Target CPA or ROAS
4. Any changes made last quarter (bid strategy switches, new campaigns, budget moves) — so you can judge whether they actually worked

## How It Works

### Step 1: Build the period comparison

For each campaign and for the account total, compute current 90 days vs prior 90 days:
- Cost, Conversions, CPA/ROAS, Conversion Value — each with direction and both values
- Always show the counter-metric alongside the headline (e.g. CPA improved but conversions down)

### Step 2: Determine the AdPulse zone

Use the same framework as the monthly review. Read the full decision tree and per-zone checklists from:

`${CLAUDE_PLUGIN_ROOT}/skills/google-ads-monthly-review/templates/zone-analysis.md`

| Budget Pacing (90-day) | Performance | Zone |
|--------------|-------------|------|
| >110% | Poor (CPA >110% of target or ROAS <90% of target) | 🔴 Red — CRITICAL |
| 90-110% | Poor | 🟠 Orange — High |
| <90% | Good (CPA ≤110% of target or ROAS ≥90% of target) | 🟡 Yellow — Scaling |
| >110% | Good | 🔵 Blue — Low |
| 90-110% | Good | 🟢 Green — Maintain |

Pacing is measured against the 90-day expected spend (monthly target × 3).

### Step 3: Run the waste hunt (adversarial core)

This is what separates this review from the monthly one. Actively attack:
- **Zero-conversion spend** over the quarter — name the keywords/campaigns and the dollar figure
- **CPA drift** — keywords/campaigns now >2x target that were fine last quarter
- **Hidden volume loss** — conversions down even where CPA looks good
- **Lost impression share to budget** on profitable campaigns — money left on the table
- **Stale creative** — RSAs unchanged for 90 days with declining CTR
- **Lucky-quarter check** — is the improvement explained by seasonality or a one-off, rather than the work?

Quantify everything. "Roughly $X of the quarter's spend produced zero conversions" beats "some waste exists".

### Step 4: Write the verdict

One blunt paragraph: is the account healthier or worse than last quarter, and is the trajectory real or fragile? Name the single biggest threat for next quarter.

### Step 5: Emit the matched zone checklist

Pull the **matched zone's Execution Checklist only** from `zone-analysis.md` (never all five). This is the prescribed action set for the quarter ahead.

### Step 6: Approval gate

Present the verdict, zone, and the top findings. Ask which findings to action this quarter before chaining into `keyword-optimizer`, `bid-budget-optimizer`, or `ad-copy-generator`.

## Output

**Filename:** `google_ads/YYYY-Qn/quarterly-review-YYYY-Qn.md` (e.g. `2026-Q2/quarterly-review-2026-Q2.md`)

**This report is a one-pager. One page maximum.** Lead with the verdict and the numbers. No preamble, no recap of methodology, no inspirational close. If it does not fit on one printed page, cut findings to the top 3.

```
# Quarterly Adversarial Review: [Client Name]
Period: [last 90 days] vs [prior 90 days] | Date: [Today]

## Verdict: [Emoji] [Zone] — [Healthier / Worse / Fragile]
[2-3 blunt sentences: real trajectory or luck, and the single biggest threat next quarter.]

## 90-Day vs Prior 90-Day
| Metric | Prior 90 | Last 90 | Δ |
|--------|----------|---------|---|
| Cost | $X | $X | ±X% |
| Conversions | X | X | ±X% |
| CPA / ROAS | $X | $X | ±X% |
| Conv. Value | $X | $X | ±X% |

## What I'd Tear Apart (waste hunt)
1. [Finding] — [$ quantified] — [kill / fix / investigate]
2. ...
3. ...

## Lucky-Quarter Check
[1-2 lines: is the result explained by seasonality / one-off / tracking, or by the work?]

## [Zone] Execution Checklist
[Paste the matched zone's checklist from zone-analysis.md — only that one zone]
```

## Tips

- Run on a fixed 90-day cadence so the comparison windows never overlap
- Always pull the counter-metric — a single improving number is never the whole story
- Quantify waste in dollars; vague findings get ignored
- A clean verdict is fine, but only after a real hunt — show the checks that would have caught a problem
- For a lighter monthly cadence, use `google-ads-monthly-review` instead

## Related Skills

- **Google Ads Monthly Review**: The lighter monthly cadence using the same AdPulse zones
- **Keyword Optimizer**: Execute the waste-hunt findings (pause keywords, add negatives)
- **Bid & Budget Optimizer**: Act on pacing and impression-share findings
- **Ad Copy Generator**: Refresh creative flagged as stale

---

*Every 90 days, attack the account before the client does*
