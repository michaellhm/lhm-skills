# LHM Finance Hub — Design Spec

**Date:** 2026-04-13
**Status:** Approved
**Plugin:** `lhm-finance-hub`

---

## Overview

A weekly financial management plugin for Local Health Marketing (LHM) that combines Gavin Smith's CFO System (cash flow forecasting, profit formula, 5-year planning) with Mike Michalowicz's Profit First allocation system. The plugin runs on a Monday rhythm — processing bank data, updating forecasts, reviewing profitability, and answering financial questions conversationally.

### Core Principles (from Gavin Smith's framework)

- **Profit tells you WHAT to do. Cash flow tells you WHEN to do it.**
- **80% accuracy is good enough** — we want insights and decisions, not perfect numbers.
- **Simplify** — 7 numbers for profit, weekly view for cash flow. No noise.
- **Cash is fuel for growth**, not something to hoard.

### Business Context

- **Business:** Local Health Marketing (digital marketing agency)
- **Revenue model:** Monthly retainers (~$1,500/client) + project-based lump sums
- **Current clients:** ~19 retainer clients
- **Accounting software:** Xero
- **Profit First accounts:** Income, OpEx (74%), Owner's Pay (12%), Tax (12%), Profit (2%)

---

## Plugin Architecture

### Skills

| Skill | Purpose | Frequency |
|-------|---------|-----------|
| `cashflow-updater` | Process bank CSVs, update 13-week cash flow forecast | Weekly (Monday) |
| `profit-calculator` | 7-lever profit formula review — current vs. target | Monthly (1st Monday) |
| `profit-first-allocator` | Owner's Pay check (monthly), full allocation review (quarterly) | Monthly / Quarterly |
| `overhead-auditor` | Audit recurring expenses — keep, replace with AI, find cheaper, cancel | Quarterly |
| `five-year-planner` | Long-term projection, milestone tracking, exit valuation | Quarterly / Biannual |
| `finance-advisor` | Conversational Q&A and scenario modelling | Anytime (ad hoc) |

### Agent

| Agent | Role |
|-------|------|
| `finance-orchestrator` | Detects session type (weekly/monthly/quarterly), triggers the right skills in sequence, manages the Monday workflow |

### Data Locations

- **Spreadsheets:** `~/Local Health Marketing/finance/` (syncs to Google Drive)
- **Config/state:** `~/Local Health Marketing/finance/config/`

### Spreadsheet Files

| File | Contents |
|------|----------|
| `cashflow-forecast.xlsx` | Tab 1: Cash Flow Forecast, Tab 2: Profit First Allocations |
| `profit-calculator.xlsx` | 7-lever profit formula with current, target, gap analysis, scenario table |
| `five-year-plan.xlsx` | Annual projections for 5 years with milestones |

### Config Files

| File | Contents |
|------|----------|
| `config/state.json` | Current week in quarter, last session date/type, client list, retainer rate, Profit First percentages, known upcoming lump sums, rolling averages |

---

## Skill Designs

### 1. Cash Flow Updater (`cashflow-updater`)

**Trigger:** Monday scheduled task or manual invocation.

**Input:** Two Xero bank CSV exports:
1. Income account (last 7 days)
2. OPEX account (last 7 days)

**Processing steps:**
1. Parse CSVs — extract transactions, dates, amounts
2. Bucket transactions into the week they fall in (Mon-Sun)
3. Calculate weekly totals: Total Cash In, Total Cash Out, Net Cash Flow
4. Write actuals into `cashflow-forecast.xlsx` for the completed week
5. Recalculate rolling average from last 6 months of actuals
6. Update 13-week forecast columns using new rolling average
7. If new retainer clients added (user informs agent), bump forecast income
8. Colour-code closing balance: green (healthy), orange (tight), red (danger)

**Tab 1: Cash Flow Forecast — Columns per week:**

| Column | Description |
|--------|-------------|
| Week (date) | Monday of that week |
| Opening Balance | OPEX account opening (= last week's closing) |
| Gross Income | Total income received that week (Income account) |
| OpEx Allocation | Gross Income x OpEx% (what flows into OPEX) |
| Cash Out | Total expenses paid from OPEX that week |
| Net Cash Flow | OpEx Allocation minus Cash Out |
| Closing Balance | Opening + Net = OPEX account position |

- Left side = actuals (green background)
- Right side = forecast (white background)
- Closing balance colour-coded: green > comfortable, orange = watch, red = danger
- Rolling 13-week view minimum, extending to 52 weeks where possible

**Tab 2: Profit First Allocations — Columns per week:**

| Column | Description |
|--------|-------------|
| Week (date) | Monday of that week |
| Gross Income | Total income that week |
| OpEx (74%) | Allocation amount |
| Owner's Pay (12%) | Allocation amount |
| Tax (12%) | Allocation amount |
| Profit (2%) | Allocation amount |
| Running totals | Cumulative per account for the quarter |

**Forecast logic:**
- Base forecast = rolling 6-month average of weekly income/expenses
- When new clients are added, future forecast income adjusts upward automatically
- Known lump sums (e.g. project payments) are placed in their expected week
- Expenses forecast from historical patterns: weekly, fortnightly, monthly, quarterly cycles

**Conversational output after update:**
- Current OPEX balance (closing this week)
- Net cash flow this week (+/-)
- Lowest point in next 13 weeks — which week and how low
- Any danger weeks flagged
- Profit First allocation for this week's income

---

### 2. Profit Calculator (`profit-calculator`)

**Trigger:** First Monday of each month, or manual.

**The 7 levers for LHM:**

| Lever | What it means for LHM |
|-------|----------------------|
| Price | Average monthly retainer (~$1,500) |
| Volume | Number of retainer clients + project clients |
| COGS | Direct costs to deliver (subcontractors, tools per client) |
| Team | Staff/contractor costs |
| Marketing | Own lead gen spend |
| Overheads | Software, subscriptions, general admin |
| Property | Office/rent if applicable |

**Spreadsheet structure (`profit-calculator.xlsx`):**

- **Row: "Now"** — current 7 numbers based on actuals
- **Row: "Target"** — where you want to be
- **Gap analysis** — dollar difference per lever, highlights biggest unlock
- **Scenario table** — steps through volume (e.g. 19, 20, 21... 30 clients) showing Income, each cost bucket, Profit, Margin at each step
- **Break-even calculation** — minimum clients at current costs

**Monthly review flow:**
1. Agent pulls last month's actuals from cash flow data
2. Updates the "Now" row in the spreadsheet
3. Compares to target
4. Tells user: "Your biggest unlock right now is X. Here's why."
5. Updates scenario table

---

### 3. Profit First Allocator (`profit-first-allocator`)

**Monthly focus: Owner's Pay**
- "Based on current income and allocations, can I comfortably pay myself this month?"
- "Should Owner's Pay % adjust?"
- Model scenarios: "What does 20% Owner's Pay look like vs. 12%?"

**Quarterly focus: Full review**
- Tax: "Do I have enough in Tax to cover BAS?"
- Super: "Is superannuation funded for my Owner's Pay level?"
- Profit: "What's in the Profit account? Time to celebrate?" (per Michalowicz)
- Allocation percentages: "Should the split change?" with scenario modelling
- Uses Tab 2 of `cashflow-forecast.xlsx` for cumulative data

**Output:** Updated allocation percentages in `config/state.json`, modelled impact on cash flow forecast.

---

### 4. Overhead Auditor (`overhead-auditor`)

**Trigger:** Quarterly, or on demand.

**Input:** OPEX transaction data from last 3 months (from cash flow actuals or Xero CSV).

**For each recurring expense, assesses:**

| Column | What it answers |
|--------|----------------|
| Expense | What is it? (e.g. Canva, Slack, hosting) |
| Monthly cost | What are we paying? |
| Purpose | What does it do for the business? |
| Usage | Are we actually using this? |
| Recommendation | Keep / Replace with Claude or AI / Find cheaper alternative / Cancel |
| Potential saving | If replaced or cancelled, annual saving |

**Flags:**
- "You're paying for Tool X at $50/mo — Claude can do this now. Save $600/yr"
- "Two overlapping subscriptions for Y"
- "This cost increased 30% since last quarter — worth reviewing"

**Output:** Summary table in conversation + recommendations. No spreadsheet for this — it's a conversational review that feeds insights back into the Profit Calculator's Overheads lever.

---

### 5. Five-Year Planner (`five-year-planner`)

**Trigger:** Quarterly review (brief), biannual deep review (June + January).

**Spreadsheet structure (`five-year-plan.xlsx`):**

| Year | Clients | Avg Price | Revenue | COGS | Team | Marketing | Overheads | Property | Total Costs | Profit | Margin |
|------|---------|-----------|---------|------|------|-----------|-----------|----------|-------------|--------|--------|
| Year 1 (current) | Actuals | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...% |
| Year 2 | Target | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...% |
| Year 3 | Target | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...% |
| Year 4 | Target | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...% |
| Year 5 | Target | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...% |

**Quarterly review asks:**
- Where are we tracking vs. the plan?
- At current growth rate, where do we land in 5 years?
- What needs to change to hit the target?
- Key milestones: when to hire, when margin hits next level

**Biannual deep review (June + January):**
- Full refresh of the 5-year model
- Gavin's question: "Does this forecast excite you? If not, what needs to change?"
- Exit valuation estimate (profit x multiple)

**First session:** The initial quarterly session sets the 5-year targets collaboratively — "Where do you want LHM to be in 5 years?"

---

### 6. Finance Advisor (`finance-advisor`)

**Trigger:** Anytime — during Monday sessions or ad hoc.

**Capabilities:**

| Question Type | Example | Method |
|---------------|---------|--------|
| Affordability | "Can I afford to hire someone at $60k?" | Models new weekly expense in cash flow forecast, shows impact on closing balance and danger weeks |
| Wage modelling | "What should my Owner's Pay be?" | Models different Profit First % scenarios against current income |
| Purchase decisions | "I want to buy a $3k computer" | Drops expense into forecast at the right week, shows ripple effect |
| What-if scenarios | "What if I lose 3 clients?" | Adjusts income forecast, shows cash impact over 13 weeks |
| Investment ROI | "If I spend $2k/mo on marketing, how many clients to break even?" | Uses profit calculator to work backwards from spend |
| Growth planning | "How many clients to hit $500k revenue?" | Math from profit calculator |

**How it works:**
- Reads current spreadsheets (cash flow, profit calculator, Profit First allocations)
- Has context from `config/state.json` (client count, retainer rate, cost structure)
- Models scenarios in conversation — shows impact, does NOT update spreadsheets unless user approves
- If user approves a change (e.g. "yes, add that hire"), updates the forecast

**Key principle:** Never makes changes to spreadsheets without explicit approval.

---

## Finance Orchestrator (`finance-orchestrator`)

**Role:** Runs the Monday session and determines which skills to trigger based on timing.

**Detection logic:**
1. What week of the quarter are we in? (tracks in `state.json`)
2. Is it the first Monday of the month? → trigger monthly skills
3. Is it week 13 of the quarter? → trigger quarterly skills

**Session types:**

| Session | When | Skills in sequence |
|---------|------|-------------------|
| Weekly | Every Monday | `cashflow-updater` → summary → "Any questions?" → `finance-advisor` |
| Monthly | 1st Monday of month | `cashflow-updater` → `profit-calculator` → `profit-first-allocator` (Owner's Pay) → summary → Q&A |
| Quarterly | Every 13 weeks | `cashflow-updater` → `profit-calculator` → `profit-first-allocator` (full review) → `overhead-auditor` → `five-year-planner` → summary → Q&A |

**Example Monday flow:**

```
Agent: "Good morning! It's Monday — time for your weekly cash flow update.
       This is Week 8 of Q3, and it's the first Monday of the month,
       so we'll also review your Profit Calculator and Owner's Pay.

       Please upload your Xero CSVs:
       1. Income account export (last 7 days)
       2. OPEX account export (last 7 days)"

User: [uploads CSVs]

Agent: "Updated. Here's your summary:

       OPEX Balance: $18,400 (closing this week)
       Net Cash Flow: +$2,100 this week
       Lowest point: Week 11 — $6,200 (BAS + Super overlap)
       Profit Calculator: 19 clients, 8% margin — target is 15%
       Owner's Pay: $3,120 allocated this month — on track

       Your biggest unlock right now is volume — at 22 clients
       with current costs, you'd hit 15% margin.

       Any questions or scenarios you want to run?"

User: "What if I increase my wage to 20%?"

Agent: [triggers finance-advisor, models it, shows impact]
```

**State tracking (`config/state.json`):**
- Current week number in the quarter (1-13)
- Last session date and type
- Current Profit First percentages
- Active client count and average retainer rate
- Known upcoming lump sums with expected dates
- Rolling averages for income and expenses

**Missed session handling:** If a Monday is skipped, the orchestrator notes it — "You missed last week. Want to upload two weeks of CSVs or just this week?"

---

## Rhythm Summary

| Cadence | What happens | Time investment |
|---------|-------------|-----------------|
| **Weekly** (Monday) | Cash flow update, summary, Q&A | ~10-15 min |
| **Monthly** (1st Monday) | + Profit Calculator review, Owner's Pay check | ~20-30 min |
| **Quarterly** (every 13 weeks) | + Full Profit First review, overhead audit, 5-year check-in, forecast accuracy review | ~45-60 min |
| **Biannual** (June + January) | Deep 5-year plan refresh | Part of quarterly |
| **Ad hoc** | Finance Advisor Q&A | As needed |

---

## Technical Notes

- All spreadsheets are `.xlsx` format, stored in `~/Local Health Marketing/finance/`, synced to Google Drive via local Drive sync
- Agent reads/writes locally; user views in Google Drive browser
- No MCP dependency for spreadsheet access — direct local file operations
- Cash flow forecast uses rolling 6-month average for projections, auto-adjusting as new actuals come in
- GST handling: income figures may include GST — track gross amounts for cash flow purposes (cash flow is about actual money movement, not accounting treatment)
- Profit Calculator works on ex-GST figures for accurate margin analysis

---

## References

- **Gavin Smith / The Profit Analyst** — CFO System framework, Profit Calculator, Cash Flow Forecaster (source: TAM Hot Seat presentation, March 2025)
- **Mike Michalowicz / Profit First** — allocation system (Income → OpEx, Owner's Pay, Tax, Profit)
- Template screenshots from Gavin's presentation used as structural reference for spreadsheet design
