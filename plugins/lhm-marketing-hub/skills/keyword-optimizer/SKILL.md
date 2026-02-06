---
name: keyword-optimizer
description: Identify wasted spend on poor-performing keywords, find top performers with 80/20 analysis, generate negative keyword lists, and recommend match type changes. Use this when users request keyword optimization, wasted spend audit, negative keywords, search terms analysis, or keyword performance review.
license: MIT
---

# Keyword Optimizer

## Purpose

Identify wasted spend on poor-performing keywords, find your top 20% performers, generate negative keyword lists from bad search terms, and recommend match type optimisations. Get actionable outputs ready to implement in Google Ads.

## When to Use

- **After strategy session** identifies keyword waste as a priority
- **High CPA campaigns** where you suspect keyword targeting issues
- **Monthly maintenance** to clean up search term waste
- **New campaigns** to quickly build negative keyword lists
- **Performance drops** to diagnose if keyword quality has declined

## Prerequisites

- Client name and campaign/ad group focus
- Keyword performance report (last 30 days minimum)
- Search terms report (last 30 days minimum)
- Target CPA or ROAS for benchmarking
- (Optional) Current negative keyword lists

## How It Works

### Step 1: Data Access

**Option A: Google Ads MCP (Recommended)**
If you have Google Ads MCP installed:

> "Please fetch keyword performance and search terms data for [campaign] for the last 30 days."

**Option B: CSV Export (Fallback)**
Please export two reports from Google Ads:

**1. Keywords Report:**
- Columns: Campaign, Ad Group, Keyword, Match Type, Impressions, Clicks, Cost, Conversions, CPA
- Date range: Last 30 days

**2. Search Terms Report:**
- Columns: Campaign, Ad Group, Search Term, Match Type, Impressions, Clicks, Cost, Conversions
- Date range: Last 30 days

### Step 2: Gather Context

I'll ask you for:

1. **Focus Area**: Which campaigns/ad groups to analyse?
2. **Target CPA/ROAS**: What's the performance benchmark?
3. **Specific Concerns**: Any known problem areas?
4. **Current Negatives**: Do you have existing negative lists?

### Step 3: Wasted Spend Audit

Identify keywords and search terms that:
- High spend (>$50) with zero conversions
- CPA more than 2x target
- High clicks with very low conversion rate
- Irrelevant search term patterns

### Step 4: 80/20 Keyword Analysis

Rank keywords by efficiency to find:
- **Top 20%**: Your best performers - protect and scale
- **Middle 60%**: Acceptable performers - maintain
- **Bottom 20%**: Underperformers - reduce or pause

### Step 5: Negative Keyword Generation

Analyse search terms to identify:
- Irrelevant n-gram patterns (common word combinations)
- Location mismatches (outside service area)
- Intent mismatches (jobs, DIY, free, etc.)
- Competitor terms performing poorly
- Question/research queries with no conversions

### Step 6: Blocked Terms Audit

Check if any negatives are blocking valuable queries:
- Search terms that previously converted
- Branded terms accidentally blocked
- Service terms with overly broad negatives

### Step 7: Match Type Recommendations

For top performers, suggest:
- Phrase match additions for exact match winners
- Exact match upgrades for consistent converters
- Broad match consideration for very high performers

### Step 8: Generate Outputs

- CSV with keyword recommendations
- TXT file with negative keywords (import-ready)
- Markdown summary report

## Expected Interaction Flow

```
You: [Paste this SKILL.md content]

I need to optimise keywords for Perth Chiropractic - Generic campaigns.
They're in Red zone and I suspect keyword waste.

Here's the keyword data:
[Pastes keyword report CSV]

Here's the search terms data:
[Pastes search terms report CSV]

Target CPA is $45. Main concern is the "back pain" ad group seems to
be attracting a lot of DIY searches.

Claude: Analysing your keyword data...

## Wasted Spend Audit

I found $650 in wasted spend across these categories:
[Analysis with specific keywords]

## 80/20 Analysis

Your top 5 keywords drive 68% of conversions:
[List with performance metrics]

## Negative Keyword Recommendations

Based on search terms analysis, here are negatives to add:
[Categorised list]

Ready to generate the output files?

You: Yes, generate the files.

Claude: [Provides CSV, TXT, and summary files]
```

## Analysis Types

### Wasted Spend Audit

**Thresholds:**
| Category | Criteria | Action |
|----------|----------|--------|
| High waste | >$100 spend, 0 conversions | Pause immediately |
| Moderate waste | >$50 spend, 0 conversions | Pause or reduce bid |
| Low efficiency | >$50 spend, CPA >2x target | Reduce bid |
| Low volume waste | <$50 spend, 0 conversions | Monitor or pause |

**Output:**
```csv
Keyword,Campaign,Ad Group,Spend,Conversions,CPA,Category,Recommendation
back pain exercises,Generic,Back Pain,$145,0,-,High Waste,Pause & Add Negative
chiropractor careers,Generic,Chiropractor,$78,0,-,High Waste,Add Negative
```

### 80/20 Keyword Analysis

**Ranking Method:**
1. Calculate efficiency score: (Target CPA ÷ Actual CPA) × 100
2. Rank keywords by efficiency
3. Identify cumulative conversion contribution
4. Label: Top 20%, Middle 60%, Bottom 20%

**Output:**
```csv
Keyword,Conversions,CPA,Efficiency,Tier,Recommendation
chiropractor perth,45,$32,141%,Top 20%,Protect - consider phrase match
back pain treatment,28,$41,110%,Top 20%,Maintain - good performer
perth chiro,12,$48,94%,Middle 60%,Maintain
chiropractor near me,8,$62,73%,Middle 60%,Monitor - borderline
back specialist,3,$95,47%,Bottom 20%,Reduce bid or pause
```

### Negative Keyword Generation

**N-Gram Pattern Analysis:**

Look for common word combinations in non-converting search terms:

```
Example Search Terms (0 conversions):
- "chiropractor jobs perth"
- "chiropractic jobs near me"
- "chiropractor career salary"

N-Gram Pattern Identified: "jobs", "career", "salary"

Negative Keywords to Add:
- jobs
- careers
- career
- salary
- employment
```

**Categories of Negatives:**

| Category | Examples | Match Type |
|----------|----------|------------|
| Job seekers | jobs, careers, salary, hiring | Phrase |
| DIY/Free | exercises, free, at home, self | Phrase |
| Education | course, degree, how to become | Phrase |
| Location | [cities outside service area] | Phrase |
| Irrelevant conditions | [conditions not treated] | Phrase |

### Blocked Terms Audit

**Check for:**
- Exact match negatives blocking phrase/broad queries that converted
- Negatives accidentally matching branded terms
- Overly broad negatives (e.g., "pain" blocking "back pain")

**Output:**
```csv
Blocked Term,Previous Conversions,Previous CPA,Blocking Negative,Recommendation
back pain chiro,5,$38,-pain,Remove negative or make exact match
perth chiro clinic,3,$42,-perth,Check if intentional
```

## Outputs

### 1. Keyword Recommendations CSV

**Filename:** `keyword-recommendations-[client]-[date].csv`

```csv
Type,Keyword,Campaign,Ad Group,Spend,Conversions,CPA,Tier,Action,Reason,Priority
Pause,back pain exercises,Generic,Back Pain,$145,0,-,Waste,Pause,High spend no conversions,Critical
Reduce,back specialist,Generic,Back Pain,$285,3,$95,Bottom 20%,Reduce Bid 30%,CPA 2x target,High
Protect,chiropractor perth,Generic,Chiropractor,$1420,45,$32,Top 20%,Maintain,Best performer,High
Upgrade,perth chiro,Generic,Chiropractor,$576,12,$48,Top 20%,Add Phrase Match,Consistent converter,Medium
```

### 2. Negative Keywords TXT

**Filename:** `negative-keywords-[campaign]-[date].txt`

Ready for direct import into Google Ads:

```
jobs
careers
career
salary
employment
hiring
exercises
free
at home
diy
self treatment
course
degree
how to become
training
```

### 3. Summary Report (Markdown)

```markdown
## Keyword Optimization Report
**Client**: Perth Chiropractic
**Campaign**: Generic - Back Pain
**Date**: 15th July 2024

### Summary
- Total Keywords Analysed: 85
- Wasted Spend Identified: $650 (18% of total spend)
- Negative Keywords Generated: 42
- Match Type Changes Recommended: 8

### Wasted Spend Breakdown
| Category | Amount | Keywords |
|----------|--------|----------|
| Zero conversions, high spend | $450 | 12 |
| CPA >2x target | $200 | 6 |
| **Total** | **$650** | **18** |

### Top Performers (Protect)
1. chiropractor perth - $32 CPA, 45 conversions
2. back pain treatment - $41 CPA, 28 conversions
3. perth chiro - $48 CPA, 12 conversions

### Negative Keywords by Category
- Job seekers: 8 keywords
- DIY/Free: 12 keywords
- Education: 6 keywords
- Wrong location: 10 keywords
- Irrelevant: 6 keywords

### Recommended Actions
1. [Priority] Pause 12 high-waste keywords
2. [Priority] Add 42 negative keywords
3. [Medium] Reduce bids on 6 low-efficiency keywords
4. [Medium] Add phrase match versions of top 3 exact match keywords
```

## Tips

- **Focus on high-spend waste first** - $100+ zero conversion keywords are urgent
- **Don't over-negative** - Too many negatives can limit reach
- **Review before adding** - Always sanity-check negative suggestions
- **Keep existing negatives** - Don't remove negatives without checking history
- **Add at campaign level** - Unless ad group specific
- **Use phrase match for negatives** - Broad match negatives can be too restrictive
- **Check mobile vs desktop** - Some keywords perform differently by device

## Related Skills

- **Monthly Strategy Session**: Run first to identify keyword issues
- **Bid & Budget Optimizer**: After fixing keywords, optimise budgets
- **Ad Copy Generator**: If keywords are fine but ads underperform

---

*Stop the waste, scale the winners*
