# 80/20 Keyword Analysis Template

Reference template for identifying top performers and optimising keyword portfolio.

---

## The 80/20 Principle for Keywords

**Core Concept:** Approximately 20% of your keywords drive approximately 80% of your conversions.

**Goal:** Identify your winners, protect them, and reallocate resources from losers to winners.

---

## Analysis Method

### Step 1: Gather Data

Export keyword report with:
- Keyword
- Campaign / Ad Group
- Match Type
- Impressions
- Clicks
- Cost
- Conversions
- Conversion Value (if ROAS-based)
- CPA or ROAS

**Time Period:** Minimum 30 days, ideally 60-90 days for seasonal stability.

### Step 2: Calculate Efficiency Score

**For CPA-based accounts:**
```
Efficiency Score = (Target CPA ÷ Actual CPA) × 100
```

**For ROAS-based accounts:**
```
Efficiency Score = (Actual ROAS ÷ Target ROAS) × 100
```

**Interpretation:**
- >150% = Excellent performer
- 100-150% = Good performer
- 80-100% = Acceptable
- 50-80% = Below target
- <50% = Poor performer

### Step 3: Rank Keywords

Sort by two metrics:
1. **Primary:** Total Conversions (descending)
2. **Secondary:** Efficiency Score (descending)

### Step 4: Calculate Cumulative Contribution

For each keyword, calculate:
```
Cumulative Conversions % = Sum of conversions to this row ÷ Total conversions × 100
```

### Step 5: Assign Tiers

| Cumulative % | Tier | Typical Action |
|--------------|------|----------------|
| 0-80% | Top Performers | Protect, scale, phrase match |
| 80-95% | Middle Performers | Maintain, monitor |
| 95-100% | Tail Performers | Evaluate, reduce, pause |

**Note:** The top ~20% of keywords should drive ~80% of the first tier.

---

## Tier Definitions

### Top 20% - Protect and Scale

**Characteristics:**
- High conversion volume
- Efficiency score >100%
- Consistent performance over time
- Clear intent alignment

**Actions:**
| Action | When | How |
|--------|------|-----|
| Protect | Always | Ensure adequate budget, don't reduce bids |
| Scale bids | If impression share <80% | Increase bid 10-15% |
| Add phrase match | If only exact match | Create phrase match version |
| Test broad match | If very high performer | With close negative monitoring |
| Dedicated ad | If generic ad | Create keyword-specific ad copy |

### Middle 60% - Maintain and Monitor

**Characteristics:**
- Moderate conversion volume
- Efficiency score 80-120%
- Stable but not exceptional

**Actions:**
| Action | When | How |
|--------|------|-----|
| Maintain | Default | Keep current settings |
| Monitor | Weekly | Watch for changes |
| Optimise ad | If CTR <2% | Test new ad variations |
| Review search terms | Monthly | Add negatives for waste |

### Bottom 20% - Evaluate and Reduce

**Characteristics:**
- Low or zero conversions
- Efficiency score <80%
- High cost relative to value

**Actions:**
| Action | When | How |
|--------|------|-----|
| Reduce bid | CPA 50-100% over target | Reduce by 30-50% |
| Pause | CPA >2x target, no trend improvement | Pause keyword |
| More restrictive match | Broad showing waste | Change to phrase or exact |
| Review necessity | Consider if keyword is needed | Remove if redundant |

---

## Analysis Table Template

```csv
Rank,Keyword,Match Type,Campaign,Conversions,Cost,CPA,Efficiency,Cum Conv %,Tier,Recommendation
1,[keyword],[type],[campaign],XX,$XXX,$XX,XXX%,XX%,Top 20%,[action]
2,[keyword],[type],[campaign],XX,$XXX,$XX,XXX%,XX%,Top 20%,[action]
...
```

**Example:**
```csv
Rank,Keyword,Match Type,Campaign,Conversions,Cost,CPA,Efficiency,Cum Conv %,Tier,Recommendation
1,chiropractor perth,exact,Generic,45,$1440,$32,141%,37%,Top 20%,Protect - add phrase match
2,back pain treatment perth,phrase,Generic,28,$1148,$41,110%,60%,Top 20%,Maintain - good performer
3,perth chiro,exact,Generic,12,$576,$48,94%,70%,Top 20%,Add phrase match
4,chiropractic clinic,phrase,Generic,10,$550,$55,82%,78%,Top 20%,Maintain
5,back specialist perth,phrase,Generic,8,$456,$57,79%,85%,Middle 60%,Monitor
6,spine doctor perth,phrase,Generic,5,$375,$75,60%,89%,Middle 60%,Reduce bid 20%
7,neck pain chiropractor,exact,Generic,4,$340,$85,53%,92%,Middle 60%,Review search terms
8,chiropractor appointment,broad,Generic,3,$285,$95,47%,95%,Bottom 20%,Add more negatives
9,back cracking,broad,Generic,2,$190,$95,47%,96%,Bottom 20%,Consider pause
10,spine alignment,phrase,Generic,1,$120,$120,38%,97%,Bottom 20%,Pause
```

---

## Conversion Concentration Analysis

### Check Your 80/20 Ratio

| Metric | Ideal | Warning | Critical |
|--------|-------|---------|----------|
| Top 20% keywords' conv share | 75-85% | 60-75% | <60% |
| Top keyword's conv share | <30% | 30-50% | >50% |
| Zero-conv keyword % | <20% | 20-35% | >35% |

**Interpretation:**
- **Ideal:** Healthy distribution, top performers clear
- **Warning:** May need more keyword diversity or optimisation
- **Critical:** Over-reliance on few keywords or too much waste

### Concentration Risk Assessment

If your top keyword drives >30% of conversions:
- ⚠️ High concentration risk
- Recommendation: Diversify by:
  - Adding related keywords
  - Testing new ad groups
  - Expanding match types on secondary performers

---

## Match Type Recommendations

### When to Upgrade Match Type

| Current | Convert to | Criteria |
|---------|-----------|----------|
| Broad | Phrase | CTR >2%, CPA on target |
| Phrase | Exact | Specific term drives most conversions |
| Exact | Phrase | Need more volume, strong negatives in place |

### Match Type Ladder

For top performers, consider this progression:

```
[+exact match winner] → Add [phrase match version] → Monitor

If phrase match performs well:
[phrase match] → Add [broad match modifier/broad] → Heavy negative monitoring
```

### Match Type Mix Recommendation

| Match Type | Ideal % of Spend | Purpose |
|------------|-----------------|---------|
| Exact | 40-60% | Core converters, control |
| Phrase | 30-40% | Variation capture |
| Broad | 10-20% | Discovery (with negatives) |

---

## Action Summary Template

After analysis, create action summary:

```markdown
## 80/20 Analysis Summary
**Client**: [Name]
**Campaign**: [Name]
**Date**: [Date]

### Portfolio Health
- Total keywords: XX
- Top 20% keywords: XX (driving XX% of conversions)
- Bottom 20% keywords: XX (driving XX% of conversions)
- Zero-conversion keywords: XX (XX% of total)

### Concentration
- Top keyword drives: XX% of conversions
- Top 3 keywords drive: XX% of conversions
- Risk level: [Low/Medium/High]

### Actions by Tier

**Top 20% - Protect (X keywords)**
1. [Keyword] - [Action]
2. [Keyword] - [Action]

**Middle 60% - Maintain (X keywords)**
- Continue monitoring
- Review search terms monthly

**Bottom 20% - Reduce (X keywords)**
1. [Keyword] - [Action]
2. [Keyword] - [Action]

### Expected Impact
- Projected waste reduction: $XXX/month
- Projected efficiency improvement: XX%
- Risk: [Low/Medium] - protecting top performers
```

---

## Common Mistakes to Avoid

1. **Cutting top performer bids** - Don't reduce bids on your winners
2. **Ignoring middle tier** - These can become winners with optimisation
3. **Keeping zombie keywords** - Zero conversions for 30+ days = pause
4. **Over-relying on efficiency score** - Volume matters too
5. **Ignoring match types** - Exact and phrase have different dynamics

---

*Know your winners, protect them fiercely, trim the losers*
