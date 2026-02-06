# Wasted Spend Audit Template

Reference template for identifying and categorising wasted keyword spend.

---

## Waste Categories

### Category 1: Zero Conversion - High Spend

**Criteria:**
- Spend > $100
- Conversions = 0
- Running for 14+ days

**Priority**: Critical - Pause Immediately

**Questions to Ask:**
- Is the keyword relevant to services offered?
- Is the landing page appropriate for this keyword?
- Is this a new keyword that needs more time?

**Action Options:**
1. Pause keyword
2. Add as negative (if search term is the issue)
3. Review landing page alignment
4. Change match type to more restrictive

---

### Category 2: Zero Conversion - Moderate Spend

**Criteria:**
- Spend $50-100
- Conversions = 0
- Running for 7+ days

**Priority**: High - Action This Week

**Questions to Ask:**
- Is this keyword targeting the right intent?
- What search terms are triggering this keyword?
- Is the ad copy aligned with keyword intent?

**Action Options:**
1. Reduce bid by 30-50%
2. Review search terms report for negatives
3. Test different ad copy
4. Consider pausing if trend continues

---

### Category 3: Zero Conversion - Low Spend

**Criteria:**
- Spend < $50
- Conversions = 0
- Running for 7+ days

**Priority**: Medium - Monitor

**Questions to Ask:**
- Is low spend due to low bids or low volume?
- Could this keyword convert with more clicks?
- Is it supporting branded queries?

**Action Options:**
1. Monitor for another week
2. Increase bid to get more data
3. Pause if consistent pattern
4. Add to watch list

---

### Category 4: High CPA - Significant Spend

**Criteria:**
- Spend > $50
- CPA > 2x target
- At least 1 conversion

**Priority**: High - Optimise or Reduce

**Questions to Ask:**
- Why is CPA so high?
- What search terms are driving this?
- Is conversion quality good? (Real bookings?)

**Action Options:**
1. Reduce bid by 30-50%
2. Add negative keywords for poor search terms
3. Review landing page for this keyword
4. Consider more restrictive match type

---

### Category 5: High CPA - Low Spend

**Criteria:**
- Spend < $50
- CPA > 2x target
- 1-2 conversions

**Priority**: Low - Insufficient Data

**Questions to Ask:**
- Is there enough data to judge?
- Could CPA improve with volume?
- Is this a valuable keyword despite CPA?

**Action Options:**
1. Continue monitoring
2. Collect more data before action
3. Review in next audit cycle

---

## Audit Process

### Step 1: Export Data

From Google Ads, export:
- Keywords report (30 days)
- Search terms report (30 days)
- Columns: Campaign, Ad Group, Keyword, Match Type, Impr, Clicks, Cost, Conv, CPA

### Step 2: Filter High Spend Keywords

Sort by Cost (descending) and review top 50 keywords.

### Step 3: Identify Zero Conversion Keywords

Filter: Conversions = 0, Cost > $50

### Step 4: Identify High CPA Keywords

Filter: CPA > 2x target, Cost > $50

### Step 5: Categorise Each Keyword

| Keyword | Spend | Conv | CPA | Category | Priority |
|---------|-------|------|-----|----------|----------|
| | $ | | $ | [1-5] | [Crit/High/Med/Low] |

### Step 6: Document Recommendations

For each flagged keyword, document:
- Current status
- Recommended action
- Expected impact

---

## Waste Audit Table Template

```csv
Keyword,Match Type,Campaign,Ad Group,Spend,Clicks,Conversions,CPA,Waste Category,Priority,Recommended Action,Expected Savings
[keyword],[broad/phrase/exact],[campaign],[ad group],$X,XX,X,$X,[Category 1-5],[Critical/High/Medium/Low],[Action],[Est. monthly savings]
```

**Example:**
```csv
Keyword,Match Type,Campaign,Ad Group,Spend,Clicks,Conversions,CPA,Waste Category,Priority,Recommended Action,Expected Savings
back pain exercises,phrase,Generic,Back Pain,$145,89,0,-,Cat 1: Zero Conv High Spend,Critical,Pause & Add Negative,$145/mo
chiropractor free,broad,Generic,Chiropractor,$78,52,0,-,Cat 2: Zero Conv Mod Spend,High,Add Negative for 'free',$78/mo
spine specialist,phrase,Generic,Back Pain,$95,28,1,$95,Cat 4: High CPA Sig Spend,High,Reduce bid 40%,$38/mo (est)
```

---

## Common Waste Patterns

### Intent Mismatches

| Search Intent | Problem | Example Keywords |
|--------------|---------|------------------|
| Job seekers | Looking for employment | [service] jobs, careers |
| DIY/Self-help | Want free/home solutions | exercises for, how to fix |
| Educational | Want to learn, not buy | course, degree, training |
| Research | Just gathering info | what is, meaning of |
| Price shoppers | Unlikely to book | free, cheap, cost of |

### Location Mismatches

| Pattern | Problem | Example |
|---------|---------|---------|
| Wrong city | Outside service area | "chiropractor sydney" (you're in perth) |
| National queries | Too broad | "best chiropractor australia" |
| Competitor areas | Not serviceable | Suburb names outside range |

### Negative Keyword Gaps

| Gap Type | Example Search Term | Negative to Add |
|----------|--------------------|-----------------|
| Informational | "what does a chiropractor do" | "what is", "what does" |
| DIY | "back exercises at home" | "at home", "exercises" |
| Jobs | "chiropractor salary perth" | "salary", "jobs" |
| Free | "free back pain assessment" | "free" |

---

## Waste Calculation Summary

After audit, summarise:

```
Total Spend Analysed: $X,XXX
Wasted Spend Identified: $XXX (X%)

Breakdown:
- Zero Conv High Spend: $XXX (X keywords)
- Zero Conv Moderate: $XXX (X keywords)
- High CPA Keywords: $XXX (X keywords)

Potential Monthly Savings: $XXX

Actions Required:
- Pause X keywords
- Add X negative keywords
- Reduce bids on X keywords
```

---

## Warning Signs

**Red Flags to Watch:**
- Single keyword spending >20% of campaign budget with no conversions
- Keyword CPA more than 3x target
- Keyword running 30+ days with zero conversions
- Search terms showing clear intent mismatch pattern
- Sudden CPA increase on previously good keyword

**When to Escalate:**
- More than 30% of spend is wasted
- Single campaign has 50%+ waste
- Waste pattern indicates landing page or tracking issue
- Client-approved keywords are underperforming

---

*Find the waste, fix the leaks, protect the performers*
