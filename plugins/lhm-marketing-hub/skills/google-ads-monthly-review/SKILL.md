---
name: google-ads-monthly-review
description: "Quick Google Ads health check that analyses account performance and determines AdPulse zone (Red/Orange/Yellow/Blue/Green). Use this when the user mentions 'zone check', 'health check', 'what zone are we in', 'quick review', 'account health', or 'AdPulse zone'. For a full monthly review with automatic skill chaining, route to the google-ads-monthly-review agent instead."
license: MIT
---

# Google Ads Monthly Review

## Purpose

Analyse Google Ads account performance, determine the AdPulse zone, and recommend 3-5 prioritised actions. This is the lightweight skill version — it analyses and recommends but does not chain into other skills automatically.

For a full review that executes recommended actions across skills, use the **google-ads-monthly-review agent** instead.

## When to Use

- **Quick zone check** — "What zone are we in?"
- **Health check** — Quick account status before a meeting
- **Start of month** — Lightweight analysis without full execution
- **After major changes** — Reassess zone after budget or performance shifts

## Prerequisites

- Client name and account details
- Campaign performance data for the last 30 days
- Target CPA or ROAS goal
- Monthly budget target

## How It Works

### Step 1: Data Access

**Option A: Google Ads MCP (Preferred)**
If Google Ads MCP is available, fetch campaign performance data automatically. All accounts live under **MCC 394-736-1921**.

**Option B: CSV Export (Fallback)**
If MCP isn't available, ask the user to provide a campaign performance CSV with columns: Campaign, Cost, Conversions, Conv. Value, CPA, ROAS, Budget. Date range: last 30 days.

### Step 2: Gather Context

Ask for:
1. **Client Name**: Which client/account?
2. **Monthly Budget**: Target monthly spend
3. **Performance Target**: Target CPA or ROAS
4. **Observations**: What have you noticed recently?

### Step 3: Calculate Metrics

- **Budget Pacing %**: (Actual Spend / Expected Spend) x 100
- **Performance Variance %**: (Actual CPA / Target CPA) x 100 — or ROAS equivalent
- **Remaining Budget**: Monthly Budget - Actual Spend
- **Required Daily Spend**: Remaining Budget / Days Remaining

### Step 4: Determine Zone

| Budget Pacing | Performance | Zone |
|--------------|-------------|------|
| >110% | Poor (CPA >110% of target or ROAS <90% of target) | Red — CRITICAL |
| 90-110% | Poor | Orange — High |
| <90% | Good (CPA ≤110% of target or ROAS ≥90% of target) | Yellow — Scaling |
| >110% | Good | Blue — Low |
| 90-110% | Good | Green — Maintain |

See `templates/zone-analysis.md` for full zone decision tree and action frameworks.

### Step 5: Generate Recommendations

Based on the zone, provide 3-5 prioritised action items. Each recommendation must include:
- Action title and urgency
- Estimated impact
- Specific metrics to target
- Reasoning

### Step 6: Approval Gate

**APPROVAL REQUIRED** — Present recommendations and wait for user confirmation before proceeding. Ask:
- Which actions would you like to tackle?
- Any actions to skip or modify?
- Questions about any recommendations?

### Step 7: Recommend Next Skills

Based on approved actions, suggest which skills to run next:

| Issue Identified | Recommended Skill |
|-----------------|-------------------|
| Budget cuts/increases | `bid-budget-optimizer` |
| Keyword waste/negatives | `keyword-optimizer` |
| Ad performance/refresh | `ad-copy-generator` |
| Landing page issues | `landing-page-optimizer` |

Include specific parameters to pass to the next skill.

## Output

Save the zone assessment to the client folder:

**File**: `google_ads/YYYY-MM/monthly-review-YYYY-MM.md`

```
# Google Ads Monthly Review: [Client Name]
Date: [Today's Date]

## Zone Assessment: [Emoji] [Zone] — [Priority]

### Key Metrics
- Monthly Budget: $X,XXX
- Actual Spend: $X,XXX (XX% of month elapsed)
- Budget Pacing: XXX%
- Target CPA: $XX | Actual CPA: $XX
- Performance vs Target: XX%

### Campaign Breakdown
| Campaign | Spend | Conv | CPA | vs Target | Status |
|----------|-------|------|-----|-----------|--------|
| ... | ... | ... | ... | ... | ... |

### Priority Actions
1. [Action] — [Impact] — [Reasoning]
2. ...

### Recommended Next Skills
- [Skill name] for [specific focus]
```

## Tips

- Run at month start (days 1-5 is ideal)
- Don't skip the approval gate
- Follow zone priorities: Red/Orange before Yellow/Green
- For full execution across skills, use the agent version instead

## Related Skills

- **Bid & Budget Optimizer**: Run when budget issues are identified
- **Keyword Optimizer**: Run when wasted spend is flagged
- **Ad Copy Generator**: Run when ad performance is poor
- **Landing Page Optimizer**: Run when conversion rate needs improvement

---

*Quick zone check — let AdPulse guide your priorities*
