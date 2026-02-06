# Budget Calculation Templates

Reference formulas and templates for budget optimisation calculations.

---

## Core Formulas

### Budget Pacing

```
Budget Pacing % = (Actual Spend to Date ÷ Expected Spend to Date) × 100

Where:
Expected Spend to Date = (Monthly Budget ÷ Days in Month) × Days Elapsed
```

**Example:**
- Monthly Budget: $3,000
- Days in Month: 30
- Days Elapsed: 15
- Actual Spend: $1,800

```
Expected Spend = ($3,000 ÷ 30) × 15 = $1,500
Budget Pacing = ($1,800 ÷ $1,500) × 100 = 120%
```
Result: 20% overspending

---

### Ideal Daily Spend (Remaining Budget)

```
Remaining Budget = Monthly Budget - Actual Spend to Date
Ideal Daily Spend = Remaining Budget ÷ Days Remaining

Days Remaining = Days in Month - Days Elapsed
```

**Example:**
- Monthly Budget: $3,000
- Actual Spend: $1,800
- Days Remaining: 15

```
Remaining Budget = $3,000 - $1,800 = $1,200
Ideal Daily Spend = $1,200 ÷ 15 = $80/day
```

---

### Performance Efficiency Score

```
Efficiency Score = (Target CPA ÷ Actual CPA) × 100

OR for ROAS:

Efficiency Score = (Actual ROAS ÷ Target ROAS) × 100
```

**Interpretation:**
- >100% = Performing better than target
- 90-100% = On target
- <90% = Underperforming

---

## 80/20 Budget Allocation

### Identifying Top Performers

**Step 1: Rank by Efficiency Score**

| Rank | Campaign | Conversions | CPA | Efficiency |
|------|----------|-------------|-----|------------|
| 1 | Brand | 20 | $25 | 200% |
| 2 | Generic A | 15 | $40 | 125% |
| 3 | Generic B | 10 | $48 | 104% |
| 4 | Generic C | 5 | $65 | 77% |
| 5 | Competitor | 2 | $90 | 56% |

**Step 2: Identify Top 20%**
- 5 campaigns × 20% = 1 campaign (Brand)
- This is your "protect at all costs" campaign

**Step 3: Identify Bottom 20%**
- 5 campaigns × 20% = 1 campaign (Competitor)
- This is your "reduce or pause" candidate

**Step 4: Reallocation Logic**

```
Budget freed from bottom 20%: $X
Allocate 70% to top 20%
Allocate 30% to middle 60% (best performers in middle)
```

---

### Reallocation Calculation

**Scenario: Reducing total spend while protecting performance**

Current State:
| Campaign | Budget | CPA | Conversions |
|----------|--------|-----|-------------|
| Brand | $30 | $25 | 10 |
| Generic | $50 | $65 | 6 |
| Competitor | $20 | $90 | 2 |
| **Total** | **$100** | **$56** | **18** |

Goal: Reduce to $75/day (-25%)

**Step 1: Calculate Conversion Value**
- Brand: $25 CPA = high efficiency, protect
- Generic: $65 CPA = medium efficiency, reduce somewhat
- Competitor: $90 CPA = low efficiency, cut significantly

**Step 2: Apply Cuts Weighted by Efficiency**

Worst performer absorbs largest cut:
- Competitor: -$10 (50% cut)
- Generic: -$15 (30% cut)
- Brand: +$0 (protect) or even +$5 if scaling

New Allocation:
| Campaign | Old Budget | New Budget | Change |
|----------|-----------|------------|--------|
| Brand | $30 | $35 | +17% |
| Generic | $50 | $35 | -30% |
| Competitor | $20 | $5 | -75% |
| **Total** | **$100** | **$75** | **-25%** |

**Expected Result:**
- Total spend: -25%
- Conversions: Brand maintains, others drop
- Blended CPA: Improves (less waste)

---

## Safety Rule Calculations

### Max 20% Increase Rule

For Max Clicks, Max Conversions, Max Conversion Value campaigns:

```
Maximum New Budget = Current Budget × 1.20
```

**Example:**
- Current budget: $50/day
- Requested increase: $75/day (+50%)
- Maximum allowed: $50 × 1.20 = $60/day

**Multi-day Scaling Plan:**
- Day 1: $50 → $60 (+20%)
- Day 2: $60 → $72 (+20%)
- Day 3: $72 → $75 (final target, +4%)

---

### Budget Overshoot Check

```
Projected Monthly Spend = Sum(Daily Budgets) × Days Remaining + Spend to Date

IF Projected Monthly Spend > Monthly Budget:
   Adjustment Needed = Projected Monthly Spend - Monthly Budget
   Reduce lowest-priority campaign budgets to fit
```

**Example:**
- Monthly Budget: $2,500
- Spend to Date: $1,000
- Days Remaining: 15
- Proposed Daily Budgets: $120

```
Projected = ($120 × 15) + $1,000 = $2,800
Overshoot = $2,800 - $2,500 = $300
Daily Reduction Needed = $300 ÷ 15 = $20/day
```

---

## Bid Strategy Decision Matrix

### When to Change Bid Strategy

| Current Strategy | Performance | Recommendation |
|-----------------|-------------|----------------|
| Max Clicks | CPA too high | Switch to Target CPA |
| Max Clicks | CPA good | Consider Max Conversions |
| Max Conversions | CPA volatile | Switch to Target CPA |
| Max Conversions | CPA stable & good | Maintain |
| Target CPA | Not spending | Increase target CPA |
| Target CPA | CPA higher than target | Lower target gradually |
| Manual CPC | Consistent results | Consider automation |
| Manual CPC | Need more control | Maintain |

### Target CPA Adjustment Formula

```
If actual CPA is 20% higher than target:
   Reduce target CPA by 10% (gradual adjustment)

If account isn't spending:
   Increase target CPA by 10-15%
```

---

## Quick Reference Tables

### Pacing Interpretation

| Pacing % | Status | Typical Action |
|----------|--------|----------------|
| <70% | Severely underspending | Increase budgets or bids |
| 70-90% | Underspending | Consider scaling |
| 90-110% | On pace | Maintain |
| 110-130% | Overspending | Monitor or reduce |
| >130% | Severely overspending | Immediate reduction |

### Efficiency Score Interpretation

| Efficiency % | Status | Budget Action |
|-------------|--------|---------------|
| >150% | Excellent | Increase budget |
| 100-150% | Good | Maintain or increase |
| 80-100% | Acceptable | Maintain |
| 60-80% | Below target | Reduce or optimise |
| <60% | Poor | Significant reduction |

---

## Template: Budget Recommendation Table

```csv
Campaign,Current Budget,Recommended Budget,Daily Change,Change %,Reason,Priority,Bid Strategy,Safety Check
[Campaign Name],$[X],$[Y],+/-$[Z],[%],[Reason],[Critical/High/Medium/Low],[Strategy],[Pass/Gradual/Limited]
```

**Example:**
```csv
Campaign,Current Budget,Recommended Budget,Daily Change,Change %,Reason,Priority,Bid Strategy,Safety Check
Brand - Sydney Podiatry,$30,$35,+$5,+17%,Best performer - protect,High,Target CPA,Pass
Generic - Podiatrist,$50,$25,-$25,-50%,CPA $95 vs $50 target,Critical,Max Conversions,Gradual
Generic - Foot Pain,$35,$20,-$15,-43%,CPA $72 - underperforming,High,Max Clicks,Gradual
Competitor,$25,$15,-$10,-40%,Low conversion volume,Medium,Manual CPC,Pass
```

---

*Reference: AdPulse Quadrant Budget Optimization*
