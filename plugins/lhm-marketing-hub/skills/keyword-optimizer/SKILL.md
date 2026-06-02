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

**Always decompose to n-grams, never block the whole phrase.** When a wasteful search term is a multi-word phrase, do not add the full phrase as a negative. Identify the individual word(s) that signal the bad intent and add each as its own single-word (unigram) negative. Example: the search term `how much does physio cost` should not become a negative as-is — add `"how"` and `"cost"` as two separate n-gram negatives instead. This catches every future variant that contains those words, not just the one phrase.

**Every negative is phrase match, wrapped in quotes.** Output each negative as `"keyword"` (with the double quotes) so it pastes straight into a Google Ads phrase-match negative list. One keyword per line.

**Group into named categories.** Each category becomes a separately identifiable negative keyword list the user can name and reuse. See the TXT output format below.

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

Three deliverables:
1. **Short 1-pager** (Markdown) — summary only, one page maximum
2. **Google Ads Editor CSV** — keyword status (pause/enable) and match-type changes, ready to import into Google Ads Editor
3. **Negative keywords TXT** — categorised, phrase-match, quoted, n-gram decomposed

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
- chiropractor jobs perth
- chiropractic jobs near me
- chiropractor career salary
- how much does a chiropractor cost

N-Gram tokens signalling bad intent: jobs, career, salary, how, cost

Negative Keywords to Add (phrase match, quoted, one n-gram per line):
"jobs"
"career"
"salary"
"how"
"cost"
```

Note how the multi-word phrases are never added whole — only the offending single-word n-grams are, so every future variant is caught.

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

### 1. Google Ads Editor CSV

**Filename:** `keyword-changes-[client]-[date].csv`

Built for direct import into **Google Ads Editor**. Exactly these columns, in this order:

```csv
Campaign,Ad Group,Keyword,Status,Match Type
Generic,Back Pain,back pain exercises,Paused,Phrase
Generic,Back Pain,back specialist,Paused,Phrase
Generic,Chiropractor,perth chiro,Enabled,Phrase
Generic,Chiropractor,chiropractor perth,Enabled,Exact
```

Rules:
- **Status** is only ever `Paused` or `Enabled`.
- **Match Type** is `Broad`, `Phrase`, or `Exact` (capitalised — Editor is case-sensitive on import).
- **To pause a wasteful keyword:** add a row with the keyword at its *current* match type and `Status = Paused`.
- **To re-enable a paused winner:** same keyword, current match type, `Status = Enabled`.
- **For a match-type upgrade:** add a row with the keyword at the *new* match type and `Status = Enabled` (Editor adds it as a new keyword; pause the old match type in a separate row if you want it removed).
- Do **not** put negative keywords in this file — they go in the TXT.

### 2. Negative Keywords TXT

**Filename:** `negative-keywords-[client]-[date].txt`

Categorised so each block can be pasted into its own named negative keyword list. Every keyword is phrase match, wrapped in double quotes, one per line. Multi-word wasteful phrases are decomposed into single-word n-gram negatives (see Step 5).

```
=== Information / research intent ===
"how"
"cost"
"price"
"vs"

=== Job seekers ===
"jobs"
"careers"
"salary"
"hiring"

=== DIY / free ===
"exercises"
"free"
"diy"

=== Education ===
"course"
"degree"
"training"

=== Wrong location ===
"sydney"
"melbourne"
```

Category headers are `=== Label ===` lines so they are obvious to skip when copying — copy only the quoted keyword lines into each Google Ads list.

### 3. Short 1-Pager (Markdown)

**Filename:** `keyword-optimization-[client]-[date].md`

**One page maximum.** Summary only — the detail lives in the CSV and TXT.

```markdown
## Keyword Optimization: Perth Chiropractic — Generic
**Date:** 15th July 2024

- Keywords analysed: 85 | Wasted spend: $650 (18%) | Negatives generated: 42 | Match-type changes: 8
- Top performers protected: chiropractor perth ($32 CPA), back pain treatment ($41), perth chiro ($48)

### Actions (in the CSV / TXT)
1. Pause 12 high-waste keywords — see CSV (Status = Paused)
2. Add 42 phrase-match negatives across 5 lists — see TXT
3. Reduce/upgrade 8 keywords by match type — see CSV
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

- **Google Ads Monthly Review**: Run first to identify keyword issues
- **Bid & Budget Optimizer**: After fixing keywords, optimise budgets
- **Ad Copy Generator**: If keywords are fine but ads underperform

---

*Stop the waste, scale the winners*
