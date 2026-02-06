# Budget Reallocation Example: Adelaide Naturopathy

> Complete interaction showing budget optimization with 80/20 analysis

---

## The Setup

**Date**: 18th June 2024 (Day 18 of month)

**Client**: Adelaide Naturopathy Clinic
- Monthly Budget: $2,000
- Target CPA: $55
- Current Zone: 🟠 Orange (on pace but poor performance)

**Problem**: Spending correctly but CPA is 40% over target. Need to reallocate budget from poor performers to good performers.

---

## The Conversation

### User Input

```
[Pastes SKILL.md content]

I need to optimise budgets for Adelaide Naturopathy. From our strategy
session, we're in Orange zone - on pace but CPA is too high.

Here's the campaign data:

Campaign,Current Daily Budget,Last 30 Days Spend,Conversions,CPA,Bid Strategy
Brand - Adelaide Naturopath,25,680,28,24.29,Target CPA
Generic - Naturopath Adelaide,45,1250,14,89.29,Max Conversions
Generic - Natural Health,30,820,10,82.00,Max Conversions
Generic - Holistic Medicine,25,650,6,108.33,Max Clicks
Competitor - Alt Practitioners,20,520,3,173.33,Manual CPC

Monthly budget: $2,000
Days remaining: 12
Focus: Reallocate budget to improve overall CPA

The Brand campaign is doing great but the others are struggling.
```

### Claude's Analysis

```
📊 **Budget Optimization: Adelaide Naturopathy**
📅 Date: 18th June 2024 (Day 18 of 30)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Current State Analysis

### Budget Status
- Monthly Budget: $2,000
- Spend to Date: $3,920 ⚠️ (196% of budget!)
- Days Remaining: 12
- Remaining Budget: -$1,920 (already over!)

**Wait - there's a problem.** Your campaigns have already spent $3,920,
which is nearly double the $2,000 monthly budget. Let me recalculate
based on your daily budgets.

Current daily budget total: $145/day
If this continued for 30 days: $4,350/month

**This explains the overspend!** Daily budgets are set too high for the
monthly budget. Let's fix this.

### Ideal Daily Budget
```
$2,000 ÷ 30 days = $66.67/day
```
Currently set at: $145/day (2.2x too high!)

### Performance Analysis

| Campaign | CPA | vs Target | Efficiency |
|----------|-----|-----------|------------|
| Brand - Adelaide Naturopath | $24.29 | 44% ✅ | 226% |
| Generic - Naturopath Adelaide | $89.29 | 162% ❌ | 62% |
| Generic - Natural Health | $82.00 | 149% ❌ | 67% |
| Generic - Holistic Medicine | $108.33 | 197% ❌ | 51% |
| Competitor - Alt Practitioners | $173.33 | 315% ❌ | 32% |

**Blended CPA**: $64.26 (117% of target)
**Best Performer**: Brand at $24.29 (226% efficiency)
**Worst Performer**: Competitor at $173.33 (32% efficiency)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 80/20 Analysis

### Conversion Distribution

| Campaign | Conversions | % of Total | Category |
|----------|-------------|-----------|----------|
| Brand | 28 | 46% | **Top 20%** |
| Generic - Naturopath | 14 | 23% | Middle 60% |
| Generic - Natural Health | 10 | 16% | Middle 60% |
| Generic - Holistic | 6 | 10% | Bottom 20% |
| Competitor | 3 | 5% | **Bottom 20%** |

**Key Insight**: Brand campaign drives 46% of conversions at 44% of target CPA.
The two worst performers drive only 15% of conversions at 2-3x target CPA.

### Budget vs Performance Mismatch

| Campaign | % of Budget | % of Conversions | Verdict |
|----------|-------------|------------------|---------|
| Brand | 17% | 46% | Underfunded ⚠️ |
| Generic - Naturopath | 31% | 23% | Overfunded |
| Generic - Natural Health | 21% | 16% | Slightly overfunded |
| Generic - Holistic | 17% | 10% | Overfunded |
| Competitor | 14% | 5% | Significantly overfunded |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Budget Recommendations

### Target: $67/day (within $2,000/month budget)

| Campaign | Current | Recommended | Change | Reason |
|----------|---------|-------------|--------|--------|
| Brand - Adelaide Naturopath | $25 | $30 | +$5 (+20%) | Top performer, increase share |
| Generic - Naturopath Adelaide | $45 | $20 | -$25 (-56%) | High CPA, reduce significantly |
| Generic - Natural Health | $30 | $12 | -$18 (-60%) | High CPA, test viability |
| Generic - Holistic Medicine | $25 | $5 | -$20 (-80%) | Very high CPA, minimal budget |
| Competitor - Alt Practitioners | $20 | $0 | -$20 (Pause) | CPA 3x target, pause |
| **TOTAL** | **$145** | **$67** | **-$78 (-54%)** | |

### Safety Checks

✅ **Total Budget Check**
- New daily budget: $67
- Days remaining: 12
- Projected remaining spend: $804
- Already spent: $3,920
- Total projected: $4,724 (still over, but can't undo past)
- Going forward: On pace for future months

⚠️ **Gradual Change Required**
- Generic - Naturopath: -56% → Split over 3 days
- Generic - Natural Health: -60% → Split over 3 days
- Generic - Holistic: -80% → Split over 4 days

⚠️ **Bid Strategy Consideration**
- Generic - Naturopath uses Max Conversions
- Generic - Natural Health uses Max Conversions
- Large budget cuts may cause algorithm volatility
- Consider switching to Target CPA after stabilisation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Implementation Plan

### Day 1 (Today)
| Campaign | Action | New Budget |
|----------|--------|------------|
| Competitor | PAUSE | $0 |
| Brand | Increase | $30 |
| Generic - Holistic | Reduce | $15 |

### Day 2 (Tomorrow)
| Campaign | Action | New Budget |
|----------|--------|------------|
| Generic - Naturopath | Reduce | $32 |
| Generic - Natural Health | Reduce | $22 |
| Generic - Holistic | Reduce | $10 |

### Day 3
| Campaign | Action | New Budget |
|----------|--------|------------|
| Generic - Naturopath | Reduce | $25 |
| Generic - Natural Health | Reduce | $16 |
| Generic - Holistic | Reduce | $7 |

### Day 4 (Final)
| Campaign | Action | New Budget |
|----------|--------|------------|
| Generic - Naturopath | Final | $20 |
| Generic - Natural Health | Final | $12 |
| Generic - Holistic | Final | $5 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Expected Impact

### Projected Performance (Days 18-30)

| Metric | Current Pace | New Allocation | Change |
|--------|-------------|----------------|--------|
| Daily Spend | $145 | $67 | -54% |
| Daily Conversions | ~2 | ~1.5 | -25% |
| Blended CPA | $64 | ~$45 | -30% |
| Monthly Total Conv | ~61 | ~46 | -25% |

### Why Conversions Drop Less Than Spend

The Brand campaign, which is being protected and increased, converts at
$24 CPA - more than 2x better than the campaigns being cut. By shifting
budget to Brand, we maintain more conversions per dollar.

**Conversion Math:**
- $78/day freed from poor performers = ~0.6 conversions at avg $130 CPA
- $5/day added to Brand = ~0.2 conversions at $24 CPA
- Net: Fewer total conversions, but at sustainable CPA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚠️ APPROVAL REQUIRED

**Do you approve these changes?**

1. [ ] Pause Competitor campaign (saves $20/day)
2. [ ] Increase Brand to $30 (best performer)
3. [ ] Gradual reduction of Generic campaigns (4-day plan)
4. [ ] Accept ~25% conversion drop for ~30% CPA improvement

**Concerns to address:**
- The account has significantly overspent this month already
- Should we communicate budget situation to client?
- Any campaigns we absolutely can't reduce?
```

### User Approval

```
Yes, approve all changes. The client already knows about the overspend -
they've approved cutting back. Let's do the gradual plan as you suggested.

One question: should we consider changing the bid strategies on the
Generic campaigns once budgets stabilise?
```

### Claude's Output

```
Great question about bid strategies! Here's my recommendation:

## Bid Strategy Recommendation

### After Budget Stabilisation (Day 4+)

| Campaign | Current | Recommended | Reason |
|----------|---------|-------------|--------|
| Generic - Naturopath | Max Conversions | Target CPA ($60) | Control CPA |
| Generic - Natural Health | Max Conversions | Target CPA ($60) | Control CPA |
| Generic - Holistic | Max Clicks | Target CPA ($60) | Better conversion focus |
| Brand | Target CPA | Keep current | Already working |

**Why Target CPA?**

1. **CPA Control**: Target CPA gives more predictable CPAs than Max Conversions
2. **Budget Constraints**: Works better with reduced budgets
3. **Stability**: Less volatile after budget changes

**When to Switch**: Wait 5-7 days after budget changes stabilise, then switch
one campaign at a time.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Implementation CSV

Here's your CSV for reference:

```csv
Campaign,Current Budget,Day 1 Budget,Day 2 Budget,Day 3 Budget,Day 4 Budget,Reason,Priority,Bid Strategy Change
Brand - Adelaide Naturopath,$25,$30,$30,$30,$30,Top performer - increase,High,None
Generic - Naturopath Adelaide,$45,$45,$32,$25,$20,High CPA - gradual reduction,Critical,To Target CPA (Day 7+)
Generic - Natural Health,$30,$30,$22,$16,$12,High CPA - gradual reduction,High,To Target CPA (Day 7+)
Generic - Holistic Medicine,$25,$15,$10,$7,$5,Very high CPA - significant cut,High,To Target CPA (Day 7+)
Competitor - Alt Practitioners,$20,$0,$0,$0,$0,CPA 3x target - pause,Critical,N/A
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Summary Report

---

**Adelaide Naturopathy - Budget Reallocation**
**Date**: 18th June 2024

**Problem**: Spending 2x monthly budget with CPA 40% over target

**Solution**: 80/20 reallocation
- Pause worst performer (Competitor)
- Increase best performer (Brand)
- Gradual reduction of middle performers
- Switch to Target CPA bid strategy after stabilisation

**Implementation Timeline**: 4 days

**Expected Outcome**:
- Daily spend: $145 → $67 (-54%)
- Blended CPA: $64 → ~$45 (-30%)
- Conversions: -25% (acceptable trade-off)

**Follow-up Actions**:
- Day 4: Verify all budgets at final levels
- Day 7: Consider bid strategy switch
- Day 12: Review month-end performance

---

Start with Day 1 changes now:
1. Pause Competitor campaign
2. Increase Brand to $30
3. Reduce Generic - Holistic to $15

Good luck!
```

---

## Key Takeaways from This Example

### What Triggered Budget Optimization

1. **Orange Zone** - On pace for month but CPA too high
2. **Budget mismatch** - Daily budgets too high for monthly limit
3. **80/20 imbalance** - Best performer underfunded, worst overfunded

### Why These Changes Were Recommended

1. **Pause Competitor** - CPA 3x target with minimal conversions
2. **Increase Brand** - Best performer deserves more budget share
3. **Gradual reductions** - Protects algorithm stability
4. **Bid strategy change** - Target CPA provides better control

### Budget Optimization Best Practices

- Always check if daily budgets match monthly limits
- Use 80/20 analysis to identify misallocation
- Protect top performers even when cutting overall
- Make large changes gradually (3-4 days)
- Consider bid strategy changes after budget stabilises
- Accept some conversion loss for CPA improvement
- Communicate budget overruns to clients early

### Safety Rules Applied

- ✅ Gradual change plan for large reductions
- ✅ Bid strategy volatility warning
- ✅ Client communication recommended
- ✅ Multi-day implementation timeline

---

*Example from AdPulse Quadrant Budget Optimization*
