---
name: bid-budget-optimizer
description: Adjust Google Ads campaign budgets and bid strategies to improve performance or control spending. Use this when users request budget optimization, bid strategy changes, budget pacing fixes, spend control, budget reallocation, or scaling campaigns.
license: MIT
---

# Bid & Budget Optimizer

## Purpose

Adjust campaign budgets and bid strategies to improve performance or control spending. Get specific recommendations for budget allocation, daily spend targets, and bid strategy changes with safety guardrails built in.

## When to Use

- **Red Zone accounts**: Reduce overspending and reallocate budget
- **Yellow Zone accounts**: Scale budgets on performing campaigns
- **Blue Zone accounts**: Pace budget or request increase from client
- **Budget pacing issues**: Campaigns exhausting budget too early or late
- **After strategy session**: When budget changes are recommended
- **Mid-month corrections**: Account trending over/under budget

## Prerequisites

- Client name and account context
- Campaign performance data (last 30 days)
- Current daily budgets per campaign
- Monthly budget target
- Target CPA or ROAS
- (Optional) Bid strategy per campaign

## How It Works

### Step 1: Data Access

**Option A: Google Ads MCP (Recommended)**
If you have Google Ads MCP installed:

> "Please fetch campaign budgets, spend, and performance data for [client name] for the last 30 days."

**Option B: Manual Data (Fallback)**
Please provide a table with:

| Campaign | Current Daily Budget | Last 30 Days Spend | Conversions | CPA/ROAS | Bid Strategy |
|----------|---------------------|-------------------|-------------|----------|--------------|
| | $ | $ | | $ | |

### Step 2: Gather Context

I'll ask you for:

1. **Monthly Budget**: What's the total monthly budget?
2. **Days Remaining**: How many days left in the month?
3. **Focus Area**: What's the main goal?
   - Reduce overspending
   - Scale performing campaigns
   - Fix pacing issues
   - Reallocate to best performers
4. **Constraints**: Any campaigns that can't be changed?

### Step 3: Calculate Ideal Daily Spend

For each campaign, I'll calculate:

```
Remaining Budget = Monthly Budget - Spend to Date
Ideal Daily Spend = Remaining Budget ÷ Days Remaining
Current Pacing = (Actual Spend ÷ Expected Spend) × 100
```

### Step 4: Apply 80/20 Analysis

Identify which campaigns deserve more/less budget:

- **Top 20% performers**: Candidates for budget increase
- **Middle 60%**: Maintain current allocation
- **Bottom 20%**: Candidates for budget reduction or pause

### Step 5: Generate Recommendations

For each campaign, provide:
- Current budget vs recommended budget
- Daily change amount
- Reason for change
- Priority level
- Expected impact

### Step 6: Apply Safety Rules

Before finalising recommendations:

✅ **Max 20% daily increase** for:
- Max Clicks
- Max Conversions
- Max Conversion Value

✅ **Total budget check**: Ensure changes don't overshoot monthly budget

✅ **Gradual changes**: Large adjustments split over multiple days

### Step 7: Generate Outputs

- CSV file ready for implementation
- Markdown summary with reasoning
- Net impact projection

## Expected Interaction Flow

```
You: [Paste this SKILL.md content]

I need to optimise budgets for Sydney Podiatry. We're in Red zone -
overspending with poor CPA.

Here's the campaign data:
[Provides campaign table]

Monthly budget: $2,500
Days remaining: 18
Focus: Reduce overspending and improve allocation

Claude: Got it! Let me analyse your campaigns...

[Analysis and recommendations]

## Budget Recommendations

| Campaign | Current | Recommended | Change | Reason |
|----------|---------|-------------|--------|--------|
| Brand | $30 | $35 | +$5 | Best performer, protect |
| Generic | $50 | $25 | -$25 | High CPA, reduce waste |
| ...

**Safety Check:**
✅ Total daily budget stays within target
✅ No bid strategy limits exceeded
⚠️ Generic reduction is 50% - recommend gradual over 3 days

Would you like me to generate the implementation CSV?

You: Yes, and explain the gradual approach for Generic.

Claude: [Provides CSV and detailed implementation steps]
```

## Outputs

### 1. Budget Recommendations CSV

```csv
Campaign,Current Budget,Recommended Budget,Daily Change,Reason,Priority,Expected Impact
Brand - Sydney Podiatry,30,35,+5,Best performer CPA $28,High,Protect conversions
Generic - Podiatrist,50,25,-25,CPA $95 vs $50 target,Critical,Reduce waste
Generic - Foot Pain,35,20,-15,CPA $72 - underperforming,High,Reduce waste
Competitor,25,15,-10,Low conversion volume,Medium,Test viability
```

### 2. Implementation Summary (Markdown)

```markdown
## Budget Changes - Sydney Podiatry
Date: [Today]

### Summary
- Total Daily Budget: $140 → $95 (-32%)
- Projected Monthly Impact: -$810 spend, maintain core conversions
- Focus: Reduce waste on underperforming campaigns

### Critical Changes (Implement Today)
1. Generic - Podiatrist: $50 → $25 (CPA too high)

### High Priority (Implement This Week)
2. Generic - Foot Pain: $35 → $20
3. Brand - Sydney Podiatry: $30 → $35 (protect)

### Gradual Implementation Required
- Generic - Podiatrist: Large reduction
  - Day 1: $50 → $40
  - Day 2: $40 → $32
  - Day 3: $32 → $25

### Net Impact
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Daily Spend | $140 | $95 | -32% |
| Monthly Projection | $4,200 | $2,850 | -32% |
| Est. Conversions | ~42 | ~35 | -17% |
| Est. CPA | $100 | $81 | -19% |
```

### 3. Safety Warnings

Any safety concerns will be clearly flagged:

```
⚠️ SAFETY WARNINGS

1. BID STRATEGY LIMIT
   Campaign: Generic - Podiatrist
   Current: Max Conversions
   Requested increase: 30%
   Limit: 20% max daily increase
   Adjusted to: 20% increase

2. BUDGET OVERSHOOT
   If all changes applied: $3,100/month
   Monthly budget: $2,500
   Action: Reduced allocations to fit budget

3. GRADUAL CHANGE REQUIRED
   Campaign: Generic - Foot Pain
   Change: -43%
   Recommendation: Split over 2-3 days
```

## Safety Rules Detail

### Bid Strategy Limits

For campaigns using these bid strategies, **never increase budget by more than 20% per day**:

| Bid Strategy | Max Daily Increase | Reason |
|--------------|-------------------|--------|
| Max Clicks | 20% | Algorithm needs time to adjust |
| Max Conversions | 20% | Sudden increases can spike CPAs |
| Max Conversion Value | 20% | Can cause overspending |
| Target CPA | No limit | Self-regulating |
| Target ROAS | No limit | Self-regulating |
| Manual CPC | No limit | You control bids directly |

### Total Budget Check

Before finalising:

```
Sum of all recommended daily budgets × Days remaining ≤ Monthly budget remaining
```

If exceeded, I'll automatically adjust the lowest-priority increases.

### Gradual Changes

For any single campaign change greater than 25%:

- **25-40% change**: Split over 2 days
- **40-60% change**: Split over 3 days
- **>60% change**: Split over 4+ days or consider pausing

## Tips

- **Protect best performers**: Don't cut budgets on campaigns hitting targets
- **Cut waste first**: Reduce budget on high-CPA campaigns before increasing anywhere
- **Gradual scaling**: Increase budgets 10-20% at a time
- **Monitor after changes**: Check performance 2-3 days after major changes
- **Document reasoning**: The markdown summary helps explain changes to clients

## Related Skills

- **Google Ads Monthly Review**: Run first to identify zone and budget issues
- **Keyword Optimizer**: If budget issues stem from keyword waste
- **Ad Copy Generator**: If performance issues need creative refresh

---

*Control your spend, maximise your impact*
