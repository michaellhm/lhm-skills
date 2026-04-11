---
name: monthly-cycle-report
description: "Generate a monthly or end-of-cycle report showing ranking progress, work completed, and next steps. Use this when the user mentions 'generate month 1 report', 'generate month 2 report', 'generate month 3 report', 'monthly report', 'cycle report', 'end of month report', 'end of cycle report', 'progress report', or wants a formatted summary of what was accomplished and how rankings have moved. Adapts format based on which month of the cycle (1, 2, or 3). Month 3 produces a full cycle summary with next-cycle recommendations."
---

# Monthly Cycle Report

Pulls performance data from GSC, GA4, and Local Falcon, compares against the baseline diagnostic, and generates a formatted report adapted to the current month of the cycle. Month 1 focuses on service page results. Month 2 focuses on content expansion. Month 3 produces a full cycle summary with recommendations for the next 3 priority services.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/monthly-cycle-report/LEARNED.md`
2. Identify the client and locate their `client_profile.md`
3. Read `[client_folder]/gmb/GMBProjectManagement.md` — determine which month of the cycle this is
4. Read `[client_folder]/gmb/onboarding/diagnostic_report.md` — baseline data for comparison
5. Read `[client_folder]/gmb/monthly-optimization/YYYY-MM/service_priorities.md` — current cycle's priority services

## Workflow

### 1. Determine Report Type

Read `GMBProjectManagement.md` to identify:
- Current cycle number
- Current month within the cycle (1, 2, or 3)
- Which tasks have been completed this month

If unclear, ask the user: "Which month report should I generate? Month 1 (service pages), Month 2 (content expansion), or Month 3 (end of cycle)?"

### 2. Gather Ranking Data

Ask the user via `AskUserQuestion`:

"Would you like to supply the latest rankings manually, or should I pull them from GSC and Local Falcon?"

**If auto-pull:**
- Use GSC MCP `get_advanced_search_analytics` for the priority keywords: pull impressions, clicks, CTR, and average position for the past 28 days
- Use GSC MCP `compare_search_periods` to compare this month vs. the previous month
- Attempt Local Falcon MCP for Top 3% grid metric (if available)
- Use GA4 MCP `run_report` for page-level sessions and conversions on optimised pages

**If manual:**
- Ask the user for each focus keyword's current position and Top 3% metric
- Ask for GSC impressions and clicks if available
- Ask for GA4 page traffic if available

### 3. Compare Against Baseline

Pull baseline data from the diagnostic report:
- Original Top 3% metric per keyword
- Original average positions
- Original impressions/clicks (if baseline included GSC data)

Calculate changes:
- Position movement per keyword (positive or negative)
- Top 3% trend across months (M0, M1, M2, M3)
- Impressions and clicks trend
- New pages indexed since baseline

### 4. Compile Work Summary

From `GMBProjectManagement.md`, list all completed tasks for the current month with their completion dates and output file paths.

### 5. Generate Report — Adapt by Month

#### Month 1 Report: Service Page Optimisation

```markdown
# Month 1 Report — [Client Name]
## [Month Year]

### Summary
[2-3 sentence overview of what was accomplished and the headline metric movement]

### Ranking Progress

| Keyword | Baseline (M0) | Current (M1) | Change |
|---------|--------------|--------------|--------|
| [kw1] | Pos X / Top3% Y% | Pos X / Top3% Y% | +/- Z |

### GSC Performance (28-day comparison)
| Metric | Previous Period | Current Period | Change |
|--------|----------------|----------------|--------|
| Impressions | X | Y | +/- Z% |
| Clicks | X | Y | +/- Z% |
| Avg Position | X | Y | +/- Z |

### Work Completed
- [Service page 1]: [URL] — published [date]
- [Service page 2]: [URL] — published [date]
- [Service page 3]: [URL] — published [date]
- Technical audit: X/Y checks passing
- Consistency signal audit: X/8 signals passing

### What Changed
[Brief explanation of the optimisations made and why]

### Next Month Preview
Month 2 will focus on content expansion:
- Diagnostic re-run to measure service page impact
- Direction decision: FAQ content, neighbourhood overlays, or both
- Target: 6-12 supporting content pages
```

#### Month 2 Report: Content Expansion

```markdown
# Month 2 Report — [Client Name]
## [Month Year]

### Summary
[2-3 sentence overview]

### Ranking Progress (3-month trend)

| Keyword | M0 | M1 | M2 | Trend |
|---------|----|----|----|----|
| [kw1] | X | Y | Z | [arrow] |

### Diagnostic Comparison
| Metric | Baseline (M0) | Re-run (M2) | Change |
|--------|--------------|-------------|--------|
| Top 3% (primary) | X% | Y% | +/- Z% |
| Direction | — | [Topical/Proximity/Mixed] | — |

### Content Created
- [List each page with title, URL, and target keyword]

### Content Direction
[Explain the diagnostic-driven decision: why FAQ, why overlays, or why mixed]

### Link Building Queue for Month 3
[List pages that need external links, prioritised]

### Next Month Preview
Month 3 will focus on link building:
- Link gap audit to prioritise pages
- Chamber of Commerce outreach
- Local sponsorship opportunities
- PR brief (if applicable)
```

#### Month 3 Report: Full Cycle Summary

```markdown
# Cycle [N] Report — [Client Name]
## [Start Month] to [End Month Year]

### Cycle Summary
[3-4 sentence overview of the entire cycle: what was accomplished, headline results]

### Ranking Progress (Full Cycle)

| Keyword | M0 | M1 | M2 | M3 | Total Change |
|---------|----|----|----|----|-------------|
| [kw1] | X | Y | Z | W | +/- N positions |

### Key Metrics
| Metric | Start of Cycle | End of Cycle | Change |
|--------|---------------|-------------|--------|
| Top 3% (primary) | X% | Y% | +/- Z% |
| GSC Impressions (28d) | X | Y | +/- Z% |
| GSC Clicks (28d) | X | Y | +/- Z% |
| Pages Created | 0 | [count] | — |
| External Links Acquired | [count] | — | — |

### Pages Created This Cycle
**Service Pages:**
- [List each with URL]

**Supporting Content:**
- [List each with URL]

**Location Pages:**
- [List each with URL, if any]

### Links Acquired
| Page | Link Source | Link Type | Date |
|------|-----------|-----------|------|
| [data from link_tracking.csv] |

### Recommendations for Next Cycle
Based on this cycle's results, the recommended next 3 priority services are:

1. **[Service A]** — [reasoning based on data]
2. **[Service B]** — [reasoning based on data]
3. **[Service C]** — [reasoning based on data]

**Carry-over items:**
- [Any incomplete tasks from this cycle]

**Direction for next cycle:**
- [Topical authority vs proximity vs mixed, based on current diagnostic]
```

### 6. Present to User

Present the formatted report for review. Ask if any sections need adjustment or additional data before finalising.

### 7. Save and Update Project Doc

Save the report to `[client_folder]/gmb/monthly-optimization/YYYY-MM/month_N_report.md`.

Update `GMBProjectManagement.md`:
- Mark the month report task as complete with today's date
- Update the ranking history table with current month's data
- For Month 3: complete the Cycle Summary section and add next-cycle recommendations

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Local Falcon | Top 3% grid metric | Ask user to supply manually |
| GSC | Impressions, clicks, average position, period comparison | Ask user to supply GSC data manually |
| GA4 | Page-level traffic and conversions | Ask user to supply GA4 data manually |
| Keywords Everywhere | Keyword volume context for recommendations | Proceed without; use existing data from service_priorities.md |

If any MCP is unavailable, display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md` and ask the user to provide the data manually. The report can be generated with any combination of auto-pulled and manual data.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/month_N_report.md` — Formatted monthly or cycle report
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Rankings updated, report task marked complete, Cycle Summary populated (Month 3 only)
