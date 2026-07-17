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

**Zone data specifically: use AdPulse MCP directly, don't hand-calculate it.** Read `${CLAUDE_PLUGIN_ROOT}/references/adpulse-integration.md` and pull `pacing`/`kpiPercentage` straight from AdPulse for Step 3-4 below instead of computing budget pacing % / performance variance % from raw Google Ads numbers. That reference also covers a known gap in the zone matrix (Under-pacing + Poor performance) and how to handle it.

### Step 2: Gather Context

Ask for:
1. **Client Name**: Which client/account?
2. **Monthly Budget**: Target monthly spend
3. **Performance Target**: Target CPA or ROAS
4. **Observations**: What have you noticed recently?

### Step 3: Calculate Metrics

If AdPulse MCP is connected, pull `pacing` and `kpiPercentage` directly (see `references/adpulse-integration.md`) and skip the manual math below. Only calculate by hand if AdPulse isn't available for this account:

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

**Gap: Under-pacing (<90%) + Poor performance has no defined cell.** Do not default this to Yellow — see `references/adpulse-integration.md` for why, and treat it as Red-severity (performance overrides pacing when they disagree).

See the **Zone Reference** section below for full zone decision trees and execution checklists.

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

### Step 8: Guided Task Execution

Once the report is saved and the user has approved which actions matter, hand off to the shared guided task execution protocol:

`${CLAUDE_PLUGIN_ROOT}/references/guided-task-execution.md`

Read it and follow it. It writes the approved actions to the chat as a numbered task list ("Here are the N tasks"), asks if the user wants to work through them one at a time, walks them one task at a time asking "Is that one done?" before moving on, then closes the session by writing learnings and always asking whether to schedule a follow-up.

## Output

Save the zone assessment to the client folder:

**File**: `google_ads/YYYY-MM/monthly-review-YYYY-MM.md`

**This report is a one-pager. One page maximum.** Keep prose to a minimum, lead with the data, no preamble or wrap-up. The whole thing should fit on a single printed page.

Include the **Execution Checklist for the matched zone only** (see Zone Reference section below). Do not paste all five zone checklists — only the one that applies.

```
# Google Ads Monthly Review: [Client Name]
Date: [Today's Date]

## Zone: [Emoji] [Zone] — [Priority]

### Key Metrics
- Monthly Budget: $X,XXX | Actual Spend: $X,XXX (XX% of month elapsed)
- Budget Pacing: XXX% | Target CPA: $XX | Actual CPA: $XX | Performance vs Target: XX%

### Campaign Breakdown
| Campaign | Spend | Conv | CPA | vs Target | Status |
|----------|-------|------|-----|-----------|--------|
| ... | ... | ... | ... | ... | ... |

### Priority Actions
1. [Action] — [Impact] — [Reasoning]
2. ...

### [Zone] Execution Checklist
[Paste the matched zone's checklist from zone-analysis.md]

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

---

## Zone Reference

### Zone Determination Matrix

| Budget Pacing | Performance | Zone | Priority |
|--------------|-------------|------|----------|
| >110% (Over) | >110% CPA or <90% ROAS (Poor) | Red | CRITICAL |
| 90-110% (On Pace) | >110% CPA or <90% ROAS (Poor) | Orange | High |
| <90% (Under) | ≤110% CPA or ≥90% ROAS (Good) | Yellow | Medium |
| >110% (Over) | ≤110% CPA or ≥90% ROAS (Good) | Blue | Low |
| 90-110% (On Pace) | ≤110% CPA or ≥90% ROAS (Good) | Green | Maintain |

### Red Zone Execution Checklist

Stabilise the patient: check vitals, treat life-threatening issues first, then stabilise.

**One-off**
- [ ] Budget reduced to 80-90% of ideal daily calculation
- [ ] Budget allocation tweaked to favour best performers
- [ ] Conversion actions are firing
- [ ] Geo-targeting tight enough
- [ ] Search partners performance checked
- [ ] Ad extensions - all relevant types exist
- [ ] Search term audit - wasted spend focus
- [ ] Blocked search terms checked
- [ ] Competitor analysis - check ads and special deals
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / demographics / audiences / geo)

**Daily**
- [ ] Budget reduced to 80-90% of ideal daily calculation
- [ ] Budget allocation tweaked to favour best performers
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day - adjust bids down if not
- [ ] Search terms - wasted spend focus
- [ ] Check troubleshooter to find weak metrics

**Monthly**
- [ ] Check performance & add bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Pause/exclude poor performers (landing pages / ad groups / ads / keywords / search terms)
- [ ] Bid strategy - change/experiment?
- [ ] Landing page speed
- [ ] Bounce rate or time-on-page metrics

### Orange Zone Execution Checklist

Flip the Red Zone priorities: performance fixes on top, budget increases only once performance is back on track.

**One-off**
- [ ] Budget allocation tweaked to favour best performers
- [ ] Conversion actions are firing
- [ ] Feed issues checked
- [ ] Geo-targeting tight enough
- [ ] Search partners performance checked
- [ ] Ad extensions - all relevant types exist
- [ ] Search term audit - wasted spend focus
- [ ] Blocked search terms checked
- [ ] Competitor analysis - check ads and special deals
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / demographics / audiences / geo)

**Daily**
- [ ] Budget allocation tweaked to favour best performers
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day - adjust bids down if not
- [ ] Search terms - wasted spend focus
- [ ] Check troubleshooter to find weak metrics

**Monthly**
- [ ] Check performance & add bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Pause/exclude poor performers (landing pages / ad groups / ads / keywords / search terms)
- [ ] Bid strategy - change/experiment?
- [ ] Landing page speed
- [ ] Bounce rate or time-on-page metrics

### Yellow Zone Execution Checklist

Easy zone: increase budgets where impactful, expand existing campaigns, then add new campaign types/networks.

**One-off**
- [ ] Budget allocation - increase where impactful
- [ ] Raise bids in best campaigns
- [ ] Blocked search terms checked
- [ ] Turn on search partners?
- [ ] Ad extensions - all relevant types exist
- [ ] Best campaigns - can they be expanded? (duplicate with different bid strategy / match type upgrade / keyword expansion / new ad formats / demographics / audiences / geo)
- [ ] Remarketing campaigns?
- [ ] Pay-for-conversions (display)?
- [ ] Add new campaign types?
- [ ] New networks (Bing)?

**Daily**
- [ ] Budget allocation - ensure top performers are not limited
- [ ] All ads approved
- [ ] No 404 errors on landing pages

**Weekly**
- [ ] Budgets lasting all day? Increase budgets if not

**Monthly**
- [ ] Check performance & add positive bid modifiers on anomalies (devices / locations / audiences / demographics)
- [ ] Bid strategy - change/experiment?

### Blue Zone Actions (ordered steps)

The whitepaper gives Blue no checklist. Run these in order until spend is back in line:

1. [ ] Ask the client for more budget (performance is good - more leads/sales is an easy conversation)
2. [ ] Decrease bids, starting with poorer performers (10%/day until spend drops)
3. [ ] Decrease budget on poorer performers if bids alone do not pull spend back
4. [ ] Turn off worst-performing keywords / ad groups / campaigns as a last resort

### Green Zone Maintenance

- [ ] Test a new strategy or experiment (use the stability to learn)
- [ ] Incremental optimisation - small, low-risk improvements
- [ ] Monitor competitor impression share and offers
- [ ] Plan for next month / anticipate seasonal shifts
- [ ] Document what is working as a template for other accounts
