# LHM Finance Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `lhm-finance-hub` plugin with 6 skills and 1 orchestrating agent for weekly cash flow management, monthly profit analysis, quarterly strategic reviews, and ad-hoc financial Q&A.

**Architecture:** Claude plugin following existing hub patterns (lhm-gmb-hub, lhm-marketing-hub). Skills are markdown instruction files (SKILL.md) that guide Claude through financial workflows. Spreadsheets (.xlsx) are read/written locally in `~/Local Health Marketing/finance/` and sync to Google Drive. State is tracked in a JSON config file.

**Tech Stack:** Claude plugin (markdown skills + agents), openpyxl for .xlsx manipulation (via the anthropic-skills:xlsx skill pattern), JSON for config state.

**Spec:** `docs/superpowers/specs/2026-04-13-lhm-finance-hub-design.md`

---

## File Structure

```
plugins/lhm-finance-hub/
├── .claude-plugin/
│   └── plugin.json                          # Plugin metadata
├── CLAUDE.md                                # Plugin-wide rules
├── agents/
│   └── finance-orchestrator.md              # Monday workflow orchestrator
├── skills/
│   ├── cashflow-updater/
│   │   ├── SKILL.md                         # Weekly cash flow update instructions
│   │   └── LEARNED.md                       # Persistent memory
│   ├── profit-calculator/
│   │   ├── SKILL.md                         # Monthly 7-lever profit review
│   │   └── LEARNED.md
│   ├── profit-first-allocator/
│   │   ├── SKILL.md                         # Monthly/quarterly allocation review
│   │   └── LEARNED.md
│   ├── overhead-auditor/
│   │   ├── SKILL.md                         # Quarterly expense audit
│   │   └── LEARNED.md
│   ├── five-year-planner/
│   │   ├── SKILL.md                         # Quarterly/biannual long-term planning
│   │   └── LEARNED.md
│   └── finance-advisor/
│       ├── SKILL.md                         # Ad-hoc Q&A and scenario modelling
│       └── LEARNED.md
└── references/
    └── gavin-smith-cfo-framework.md         # Core principles reference
```

**Data files created at runtime** (not in plugin, stored in user's Drive folder):

```
~/Local Health Marketing/finance/
├── cashflow-forecast.xlsx                   # Tab 1: Cash Flow, Tab 2: Profit First
├── profit-calculator.xlsx                   # 7-lever profit formula
├── five-year-plan.xlsx                      # Annual projections
├── client-list.xlsx                         # Source of truth for income
└── config/
    └── state.json                           # Session state, percentages, averages
```

---

## Task 1: Plugin Scaffold

**Files:**
- Create: `plugins/lhm-finance-hub/.claude-plugin/plugin.json`
- Create: `plugins/lhm-finance-hub/CLAUDE.md`
- Create: `plugins/lhm-finance-hub/references/gavin-smith-cfo-framework.md`

- [ ] **Step 1: Create plugin directory structure**

```bash
mkdir -p plugins/lhm-finance-hub/.claude-plugin
mkdir -p plugins/lhm-finance-hub/agents
mkdir -p plugins/lhm-finance-hub/skills/cashflow-updater
mkdir -p plugins/lhm-finance-hub/skills/profit-calculator
mkdir -p plugins/lhm-finance-hub/skills/profit-first-allocator
mkdir -p plugins/lhm-finance-hub/skills/overhead-auditor
mkdir -p plugins/lhm-finance-hub/skills/five-year-planner
mkdir -p plugins/lhm-finance-hub/skills/finance-advisor
mkdir -p plugins/lhm-finance-hub/references
```

- [ ] **Step 2: Create plugin.json**

Write to `plugins/lhm-finance-hub/.claude-plugin/plugin.json`:

```json
{
  "name": "lhm-finance-hub",
  "description": "Weekly financial management hub combining Gavin Smith's CFO System (cash flow forecasting, profit formula, 5-year planning) with Profit First allocations. Runs a Monday rhythm for cash flow updates, profit analysis, and strategic reviews.",
  "version": "1.0.0",
  "author": {
    "name": "LHM Digital"
  },
  "keywords": ["finance", "cashflow", "profit", "forecasting", "profit-first"]
}
```

- [ ] **Step 3: Create CLAUDE.md (plugin-wide rules)**

Write to `plugins/lhm-finance-hub/CLAUDE.md`:

```markdown
# LHM Finance Hub - Plugin-Wide Rules

These rules apply to EVERY skill and agent in this plugin, without exception.

## Core Principles

These come from Gavin Smith's CFO System framework:

1. **Profit tells you WHAT to do. Cash flow tells you WHEN to do it.** Never confuse the two. They are different tools answering different questions.
2. **80% accuracy is good enough.** We want insights and decisions, not perfect numbers. Round numbers are fine. Approximations are fine. Speed matters more than precision.
3. **Simplify.** 7 numbers for profit, weekly view for cash flow. No noise, no jargon, no unnecessary detail.
4. **Cash is fuel for growth**, not something to hoard. The goal is visibility so you can make confident investment decisions.

## Data Locations

- **Spreadsheets:** `~/Local Health Marketing/finance/` (syncs to Google Drive via local Drive sync)
- **Config/state:** `~/Local Health Marketing/finance/config/`
- Agent reads/writes .xlsx files locally. User views them in Google Drive browser.

## Spreadsheet Rules

- All spreadsheets are `.xlsx` format
- Use the `anthropic-skills:xlsx` skill pattern for reading and writing spreadsheets
- Never overwrite historical actuals. Only update the current week or add new data.
- Colour-code for quick scanning: green = healthy/actuals, orange = watch, red = danger, white = forecast

## Financial Data Rules

- **Cash flow** tracks gross amounts (including GST). Cash flow is about actual money movement.
- **Profit Calculator** works on ex-GST figures from the Xero P&L for accurate margin analysis.
- Never fabricate financial data. If data is missing, ask the user.
- When presenting numbers, always use Australian dollar format ($X,XXX).
- Round to whole dollars in summaries. Cents don't matter for decision-making.

## Mandatory: Self-Learning Protocol

Every skill in this plugin has a `LEARNED.md` file in its directory. This file is Claude's persistent memory for that specific skill.

### Before Executing Any Skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task.

### When to Write a New Entry

After completing a skill execution, check whether you discovered something reusable. Record things like:
- Xero CSV format quirks or parsing issues
- User preferences for summary format or detail level
- Calculation corrections or formula adjustments
- Client patterns that affect forecasting

### Entry Format

One line per entry. Dated. Specific. Actionable.

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

### Maintenance Rules

- Maximum 50 entries per LEARNED.md file
- Consolidate duplicates, drop entries older than 3 months that weren't referenced
- Never record session-specific context (file paths, task details for this run)
```

- [ ] **Step 4: Create gavin-smith-cfo-framework.md reference**

Write to `plugins/lhm-finance-hub/references/gavin-smith-cfo-framework.md`:

```markdown
# Gavin Smith's CFO System Framework

Source: The Profit Analyst (theprofitanalyst.com)
Extracted from: TAM Hot Seat presentation, March 2025

## The Finance Ecosystem

Three types of numbers in finance:

1. **Profit & Loss (P&L)** - Is your money-making machine making money? What are the levers to dial it up?
2. **Balance Sheet** - Your financial position. What you own minus what you owe = net worth.
3. **Cash Flow** - Different from profit because of timing differences. Cash is the pulse of the business.

## The CFO System - 4 Tools

### 1. Weekly Cash Flow Forecaster
- Track on a weekly basis (not monthly - too misleading)
- Show actuals AND forecast side by side
- Look at least 13 weeks (one quarter) ahead
- Spot the "danger week" where payment cycles overlap
- 80% accuracy is good enough
- Simple math: Opening + Cash In - Cash Out = Closing. Closing becomes next week's Opening.
- Purpose: (a) Don't run out of cash. (b) See what cash is available for investment.

### 2. Profit Calculator (7 Levers)
- Income = Price x Volume
- 5 expense buckets: Cost of Sales, Team, Marketing, Property, Overheads
- Compare "Now" vs "Target" to find the unlock
- Each lever is a distinct area you manage differently
- Calculate break-even point
- Review quarterly minimum, or anytime you're making a strategic decision

### 3. Clarity Reports (Monthly)
- P&L viewed through the 7-lever lens, colour-coded charts
- Balance sheet as 4 categories: Working Capital, Long-term Assets, Debt, Owner's Equity
- Takes 30 minutes max to review
- Purpose: see what's happening and diagnose why

### 4. Five-Year Forecast
- Project current trajectory forward
- Review twice yearly (June/July + New Year)
- Key question: "Does this forecast excite you? If not, what needs to change?"
- Exit valuation = profit x multiple

## The Rhythm

| Cadence | Tool | Time |
|---------|------|------|
| Weekly | Cash Flow Forecaster | 10 min (1 min when experienced) |
| Monthly | Clarity Reports (P&L + Balance Sheet) | 30 min |
| Quarterly | Profit Calculator (strategic decisions) | Variable |
| Biannually | Five-Year Forecast | Part of quarterly |

## Key Mental Models

- **Peaks and troughs:** Profit doesn't grow linearly. You hit constraint points, invest (profit dips), then ride to the next peak. This is normal.
- **Constraint points:** At each peak, something is maxed out (team capacity, leads, location, market). Identify it, invest to solve it, ride to the next level.
- **Cash is fuel:** You need cash to make investments. Cash flow forecast tells you how much fuel you have.
- **Profit formula tells you WHAT, cash flow tells you WHEN.** Always pair them.
- **Compounding decisions:** One good decision stacked on another. The earlier you start, the bigger the compound effect over 5-10 years.

## Profit First Integration (Mike Michalowicz)

Gavin is not a fan of Profit First at scale (it creates admin burden, hides cash visibility, promotes scarcity mindset). However, the user uses Profit First, so the system integrates both:

- Cash flow forecast tracks the OPEX account (where bills get paid)
- Income account is a passthrough that gets drained via percentage allocations
- Allocation percentages are reviewed quarterly
- The key question for Owner's Pay: "Can I comfortably pay myself this month?"
```

- [ ] **Step 5: Create all LEARNED.md files**

Create identical LEARNED.md files in each skill directory:

```markdown
# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
```

Write this to:
- `plugins/lhm-finance-hub/skills/cashflow-updater/LEARNED.md`
- `plugins/lhm-finance-hub/skills/profit-calculator/LEARNED.md`
- `plugins/lhm-finance-hub/skills/profit-first-allocator/LEARNED.md`
- `plugins/lhm-finance-hub/skills/overhead-auditor/LEARNED.md`
- `plugins/lhm-finance-hub/skills/five-year-planner/LEARNED.md`
- `plugins/lhm-finance-hub/skills/finance-advisor/LEARNED.md`

- [ ] **Step 6: Commit**

```bash
git add -f plugins/lhm-finance-hub/
git commit -m "feat: scaffold lhm-finance-hub plugin structure"
```

---

## Task 2: Client List Skill & Spreadsheet Setup

**Files:**
- Create: `plugins/lhm-finance-hub/skills/cashflow-updater/SKILL.md` (partial - client list section)

This task creates the initial data files that all other skills depend on. We build the client list spreadsheet and config state first, since the cash flow updater and profit calculator both read from them.

- [ ] **Step 1: Create the finance directory and config**

```bash
mkdir -p ~/Local\ Health\ Marketing/finance/config
```

- [ ] **Step 2: Create state.json with initial values**

Write to `~/Local Health Marketing/finance/config/state.json`:

```json
{
  "quarter_start_date": "2026-04-06",
  "current_week_in_quarter": 2,
  "last_session_date": null,
  "last_session_type": null,
  "profit_first_percentages": {
    "opex": 74,
    "owners_pay": 12,
    "tax": 12,
    "profit": 2
  },
  "rolling_averages": {
    "weekly_income": null,
    "weekly_expenses": null,
    "months_of_data": 0
  }
}
```

- [ ] **Step 3: Create client-list.xlsx with current clients**

Use the xlsx skill to create `~/Local Health Marketing/finance/client-list.xlsx` with these columns and initial data:

| Client Name | Type | Monthly Retainer | Project Value | Payment Structure | Start Date | Status | Notes |
|-------------|------|-----------------|---------------|-------------------|------------|--------|-------|
| (19 retainer clients) | Retainer | 1500 | - | Monthly | - | Active | - |
| Door Replaced | Project | - | 2000 | 50-50 | 2026-04-01 | Won (pending start) | Website build, deposit expected April/May |
| Sleep Easy | Project | - | 2000 | 50-50 | 2026-04-01 | Won (pending start) | Website build, deposit expected April/May |

**Note:** The 19 retainer client names need to be confirmed with the user. For now, create the spreadsheet with placeholder rows labelled "Client 1" through "Client 19" at $1,500/mo each, plus the two known project clients. The user will populate real names in the first Monday session.

Column formatting:
- Monthly Retainer and Project Value: currency format ($#,##0)
- Headers: bold, light blue background
- Status column: data validation dropdown (Active, Won (pending start), Lost, Completed)

- [ ] **Step 4: Commit**

```bash
git add -f plugins/lhm-finance-hub/ ~/Local\ Health\ Marketing/finance/
git commit -m "feat: create initial data files - client list and state config"
```

---

## Task 3: Cash Flow Updater Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/cashflow-updater/SKILL.md`

- [ ] **Step 1: Write the cashflow-updater SKILL.md**

Write to `plugins/lhm-finance-hub/skills/cashflow-updater/SKILL.md`:

```markdown
---
name: cashflow-updater
description: "Process weekly bank data and update the 13-week cash flow forecast. Use this when the user mentions 'cash flow update', 'Monday update', 'weekly update', 'bank CSV', 'upload bank data', 'cash flow forecast', or 'update the forecast'. Also triggered automatically by the finance-orchestrator every Monday."
---

# Cash Flow Updater

You are a financial analyst updating the weekly cash flow forecast for Local Health Marketing. Your goal is to process bank transaction data, update actuals, and maintain a 13-week forward forecast.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/cashflow-updater/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/gavin-smith-cfo-framework.md`
3. Read `~/Local Health Marketing/finance/config/state.json` for current Profit First percentages
4. Check if `~/Local Health Marketing/finance/cashflow-forecast.xlsx` exists
   - **If not**: this is the first run. Create the spreadsheet from scratch (see First Run Setup below).
   - **If yes**: proceed to Step 1.

## Step 1: Client Update Check

Before processing any bank data, ask:

"Any client changes this week?
- New clients won?
- Clients lost or paused?
- Project milestones hit? (deposits received, completions due)"

If there are changes:
1. Read `~/Local Health Marketing/finance/client-list.xlsx`
2. Update the relevant rows (add new clients, change status of lost/completed clients)
3. Write the updated file back
4. Confirm: "Updated client list. [Client Name] added/removed. Forecast income adjusted from $X to $Y per week."

If no changes, proceed to Step 2.

## Step 2: Request Bank CSVs

Ask: "Please upload your Xero bank CSVs:
1. Income account export (last 7 days)
2. OPEX account export (last 7 days)"

## Step 3: Parse CSVs

When the user uploads the CSVs:

1. Read each CSV file
2. For each transaction, extract: date, description, amount (positive = money in, negative = money out)
3. Bucket transactions by week (Monday to Sunday)
4. Calculate per week:
   - **Gross Income**: sum of all positive transactions from the Income account CSV
   - **Cash Out**: sum of all negative transactions (as positive numbers) from the OPEX account CSV
5. Calculate **OpEx Allocation**: Gross Income x (OpEx% from state.json, currently 74%)
6. Calculate **Net Cash Flow**: OpEx Allocation - Cash Out
7. If the CSV includes transactions from multiple weeks, process each week separately

## Step 4: Update the Spreadsheet

Read `~/Local Health Marketing/finance/cashflow-forecast.xlsx`.

### Tab 1: Cash Flow Forecast

For the week(s) covered by the CSV data:
1. Move the week column(s) from forecast to actuals (change background from white to light green)
2. Write actual values: Gross Income, OpEx Allocation, Cash Out, Net Cash Flow
3. Calculate Closing Balance: Opening + Net Cash Flow
4. The closing balance of this week becomes the Opening Balance of the next week

For forecast weeks (13 weeks ahead from current):
1. Read `~/Local Health Marketing/finance/client-list.xlsx`
2. Calculate forecast weekly income:
   - Sum of all Active retainer clients' monthly retainers, divided by 4.33 (weeks per month)
   - Add any Won (pending start) clients from their start week onwards
   - Place known project payments (deposits, completions) in their expected weeks
3. Calculate forecast weekly expenses from rolling average of last 6 months of actuals
   - If fewer than 6 months of actuals exist, use whatever is available
4. Apply OpEx allocation percentage to forecast income
5. Calculate forecast Net Cash Flow and Closing Balance for each week

Colour-code the Closing Balance row:
- Green (#C6EFCE): balance > 2x average weekly expenses (comfortable)
- Orange (#FFEB9C): balance between 1x and 2x average weekly expenses (watch)
- Red (#FFC7CE): balance < 1x average weekly expenses (danger)

### Tab 2: Profit First Allocations

For the week(s) covered by the CSV data:
1. Write Gross Income
2. Calculate and write each allocation:
   - OpEx: Gross Income x opex% (from state.json)
   - Owner's Pay: Gross Income x owners_pay%
   - Tax: Gross Income x tax%
   - Profit: Gross Income x profit%
3. Update running totals (cumulative for the current quarter)

Write the updated spreadsheet back.

## Step 5: Update State

Update `~/Local Health Marketing/finance/config/state.json`:
- Increment `current_week_in_quarter`
- Set `last_session_date` to today
- Set `last_session_type` to "weekly"
- Update `rolling_averages` with new data

## Step 6: Present Summary

Present the summary in this format:

```
Weekly Cash Flow Update - [Date]

OPEX Balance: $XX,XXX (closing this week)
Net Cash Flow: +/-$X,XXX this week
Gross Income: $X,XXX received

Profit First Allocations This Week:
  OpEx (74%): $X,XXX
  Owner's Pay (12%): $X,XXX
  Tax (12%): $X,XXX
  Profit (2%): $X,XXX

13-Week Outlook:
  Lowest point: Week X ([date]) at $X,XXX [reason if identifiable]
  Highest point: Week X ([date]) at $X,XXX
  [Any danger weeks flagged in red]

Any questions or scenarios you want to run?
```

## First Run Setup

If `cashflow-forecast.xlsx` does not exist, create it:

### Tab 1: Cash Flow Forecast

Create with columns:
- Row 1: Headers
- Column A: Row labels (Opening Balance, Gross Income, OpEx Allocation, Cash Out, Net Cash Flow, Closing Balance)
- Columns B onwards: one column per week, header = Monday date (e.g. "14-Apr-26")
- Create 26 columns (6 months: 13 actuals to fill over time + 13 forecast)

Header row: bold, dark blue background (#003366), white text
Row labels: bold
Forecast columns: white background
Initial values: all forecast, based on client list income and estimated expenses

### Tab 2: Profit First Allocations

Create with columns matching Tab 1 dates:
- Row labels: Gross Income, OpEx (74%), Owner's Pay (12%), Tax (12%), Profit (2%), then a blank row, then Running Total headers for each allocation
- All formulas based on percentages from state.json

Ask the user for their current OPEX account balance to set the initial Opening Balance.
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/cashflow-updater/SKILL.md
git commit -m "feat: add cashflow-updater skill"
```

---

## Task 4: Profit Calculator Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/profit-calculator/SKILL.md`

- [ ] **Step 1: Write the profit-calculator SKILL.md**

Write to `plugins/lhm-finance-hub/skills/profit-calculator/SKILL.md`:

```markdown
---
name: profit-calculator
description: "Review the 7-lever profit formula for LHM. Use this when the user mentions 'profit calculator', 'profit formula', 'profit review', 'margin analysis', '7 levers', 'profit levers', 'where is my profit', 'biggest unlock', 'break even', or 'monthly review'. Also triggered by the finance-orchestrator on the first Monday of each month."
---

# Profit Calculator

You are a financial strategist helping the business owner understand their profit formula through Gavin Smith's 7-lever framework. Your goal is to show where the business makes profit now, what the target looks like, and which lever has the biggest unlock.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/profit-calculator/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/gavin-smith-cfo-framework.md`
3. Check if `~/Local Health Marketing/finance/profit-calculator.xlsx` exists
   - **If not**: this is the first run. You'll need to create it (see First Run Setup).
   - **If yes**: proceed to Step 1.

## Step 1: Request P&L Data

Ask: "Please upload your Xero Profit & Loss report for last month (cash basis)."

If the user has already uploaded it (e.g. during orchestrator flow), proceed with the data.

## Step 2: Map Xero Categories to 7 Levers

Parse the Xero P&L and map to the 7 levers:

| Lever | Xero P&L Categories |
|-------|---------------------|
| **Price** | Derived from `client-list.xlsx` (total Trading Income / active client count) |
| **Volume** | Count of Active clients from `client-list.xlsx` |
| **COGS** | "Software - Client Delivery" + "Operations" |
| **Team** | "Contractor - Multiply Mii" + "Contractor - Alvina" + "Contractor - Developer" + "Contractor - Marketing Wingz" + "Contractor - Other" + "Virtual Assistant" |
| **Marketing** | "Advertising & Marketing" |
| **Owner's Pay** | "Salaries & Wages" + "Superannuation" |
| **Overheads** | "Subscriptions" + "Internet" + "Food & Beverage - Client Meetings" + "Merchant Fees" + "Stripe Fees." + "Bank Fees" + "Accounting and bookkeeping" + "Filing Fees" + "Motor Vehicles - Repairs & Maintenance" + "Motor Vehicles - Tolls" + "Travel - National" + "Entertainment" + "Other expenses" + "Realised Currency Gains" |

Calculate:
- **Total Income** = Sum of all Trading Income
- **Total Expenses** = COGS + Team + Marketing + Owner's Pay + Overheads
- **Profit** = Total Income - Total Expenses
- **Margin** = (Profit / Total Income) x 100

## Step 3: Update the Spreadsheet

Read `~/Local Health Marketing/finance/profit-calculator.xlsx`.

Update the **"Now"** row with the mapped values from this month.

Calculate the **Gap** row: Target minus Now for each lever.

Highlight the lever with the biggest gap in green (biggest unlock opportunity).

Update the **Scenario Table**:
- Start from current volume, step +1 client per row, up to current + 15
- For each row, calculate:
  - Income = Volume x Price
  - COGS = current COGS% x Income (variable portion) + fixed COGS
  - Team = current Team cost (fixed until capacity hit, then step up)
  - Marketing = current Marketing (fixed)
  - Owner's Pay = current Owner's Pay (fixed)
  - Overheads = current Overheads (fixed)
  - Profit = Income - all costs
  - Margin = Profit / Income x 100
- Highlight the break-even row

Update the **Break-even** calculation:
- Break-even clients = Total Fixed Costs / (Price - Variable Cost per Client)

Write the updated spreadsheet.

## Step 4: Present Analysis

Present in this format:

```
Profit Calculator Review - [Month Year]

YOUR 7 LEVERS:
  Price:      $X,XXX/client/month (avg)
  Volume:     XX clients
  Revenue:    $XX,XXX/month

  COGS:       $X,XXX (XX% of revenue)
  Team:       $XX,XXX (XX% of revenue)
  Marketing:  $X,XXX (XX% of revenue)
  Owner's Pay: $X,XXX (XX% of revenue)
  Overheads:  $X,XXX (XX% of revenue)

  PROFIT:     $X,XXX (XX% margin)
  TARGET:     $X,XXX (XX% margin)
  GAP:        $X,XXX

BIGGEST UNLOCK: [Lever name]
  [2-3 sentence explanation of why this is the biggest opportunity
   and what specifically the user could do about it]

BREAK-EVEN: XX clients at current costs

SCENARIO: At XX clients (current + 3), profit would be $X,XXX (XX% margin)
```

## Step 5: Offer Next Steps

Ask: "Want to run any scenarios? For example:
- 'What if I add 5 more clients?'
- 'What if I increase my price to $1,800?'
- 'What if I reduce team costs by 10%?'"

If the user asks a scenario question, model it conversationally (don't update the spreadsheet) and show the impact on profit and margin. If they want to lock in a new target, update the Target row.

## First Run Setup

If `profit-calculator.xlsx` does not exist, create it with:

**Headers row**: bold, dark blue background, white text

**Section 1: Profit Formula**
- Row: "Now" - current values (populated from first P&L upload)
- Row: "Target" - initially blank, ask user to set targets
- Row: "Gap" - formula: Target - Now
- Columns: Price, Volume, Revenue, COGS, Team, Marketing, Owner's Pay, Overheads, Profit, Margin

**Section 2: Scenario Table** (below, separated by a blank row)
- Headers: Volume, Price, Revenue, COGS, Team, Marketing, Owner's Pay, Overheads, Profit, Margin
- 15 rows stepping volume from current to current + 15
- Break-even row highlighted in yellow

**Section 3: Break-even** (below scenario table)
- Break-even volume
- Break-even revenue

Ask the user to set their target profit margin. Default suggestion: current margin + 10 percentage points.
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/profit-calculator/SKILL.md
git commit -m "feat: add profit-calculator skill with Xero P&L mapping"
```

---

## Task 5: Profit First Allocator Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/profit-first-allocator/SKILL.md`

- [ ] **Step 1: Write the profit-first-allocator SKILL.md**

Write to `plugins/lhm-finance-hub/skills/profit-first-allocator/SKILL.md`:

```markdown
---
name: profit-first-allocator
description: "Review Profit First allocation percentages and model scenarios. Use this when the user mentions 'Profit First', 'allocation percentages', 'owner's pay review', 'can I pay myself more', 'tax allocation', 'BAS check', 'profit celebration', 'Profit First review', or 'allocation review'. Triggered monthly by finance-orchestrator (Owner's Pay focus) and quarterly (full review)."
---

# Profit First Allocator

You are a financial advisor helping the business owner review and optimize their Profit First allocation percentages (Mike Michalowicz system). You understand both the Profit First philosophy and Gavin Smith's cash-flow-first approach.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/profit-first-allocator/LEARNED.md`
2. Read `~/Local Health Marketing/finance/config/state.json` for current percentages
3. Read Tab 2 of `~/Local Health Marketing/finance/cashflow-forecast.xlsx` for cumulative allocation data

## Determine Review Type

Check if this is a monthly or quarterly review (the orchestrator will indicate, or infer from `state.json` week number):

- **Monthly (Owner's Pay focus)**: Go to Monthly Review
- **Quarterly (full review)**: Go to Quarterly Review

## Monthly Review: Owner's Pay Check

### Step 1: Calculate Current Owner's Pay

From Tab 2 of cashflow-forecast.xlsx, pull:
- Total Gross Income this month (sum of weekly Gross Income for the current month)
- Owner's Pay allocation this month = Total Gross Income x owners_pay%
- Year-to-date Owner's Pay total

### Step 2: Assess Adequacy

Present:

```
Owner's Pay Review - [Month Year]

This month's income: $XX,XXX
Owner's Pay allocation (12%): $X,XXX
Year-to-date Owner's Pay: $XX,XXX

At current income and 12% allocation:
  Monthly take-home: ~$X,XXX
  Annualised: ~$XX,XXX

Is this enough to cover your personal expenses comfortably?
```

### Step 3: Model Scenarios (if requested)

If the user wants to explore a different percentage:

```
Scenario: Owner's Pay at 20% (up from 12%)

  Monthly take-home: ~$X,XXX (+$X,XXX)
  Annualised: ~$XX,XXX

  Impact on other allocations (keeping Tax at 12%, Profit at 2%):
    OpEx would drop from 74% to 66%
    Monthly OpEx allocation: $X,XXX (was $X,XXX)
    
  Can OpEx handle this?
    Average monthly expenses from OPEX: $XX,XXX
    OpEx allocation at 66%: $X,XXX
    Surplus/deficit: +/-$X,XXX
```

If the user approves a change, update state.json with new percentages and recalculate the cash flow forecast Tab 1 (OpEx Allocation column) and Tab 2 (all allocation columns).

## Quarterly Review: Full Allocation Check

### Step 1: Present Quarter Summary

From Tab 2 cumulative data:

```
Quarterly Profit First Review - Q[X] [Year]

Total Gross Income This Quarter: $XX,XXX

Allocations:
  OpEx (74%):       $XX,XXX
  Owner's Pay (12%): $X,XXX
  Tax (12%):        $X,XXX
  Profit (2%):      $XXX
```

### Step 2: Tax Check

```
TAX ACCOUNT:
  Accumulated this quarter: $X,XXX
  Estimated BAS liability (approx 1/11th of income for GST): $X,XXX
  Estimated PAYG: [ask user if applicable]
  Super obligation (if paying self as employee): $X,XXX
  
  Buffer: +/-$X,XXX
  Status: [Comfortable / Tight / Short]
```

If short, recommend: "Consider bumping Tax allocation to XX% next quarter."

### Step 3: Super Check

```
SUPERANNUATION:
  Owner's Pay this quarter: $X,XXX
  Super obligation (11.5% of Owner's Pay): $X,XXX
  Is this funded from the Tax allocation or separately?
```

### Step 4: Profit Celebration

```
PROFIT ACCOUNT:
  Accumulated this quarter: $XXX
  
  Per Mike Michalowicz: Take 50% of the Profit account as a 
  celebration reward. That's $XXX to spend on something fun.
  
  The other 50% stays as a rainy day buffer.
```

### Step 5: Allocation Review

"Based on this quarter's data, should we adjust the percentages?

Current: OpEx 74% | Owner's Pay 12% | Tax 12% | Profit 2%

Considerations:
- [Any issues identified above]
- [Suggestions based on the data]"

Model any requested scenarios showing impact on all four buckets and the cash flow forecast.

If approved, update state.json and recalculate affected spreadsheets.
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/profit-first-allocator/SKILL.md
git commit -m "feat: add profit-first-allocator skill with monthly and quarterly flows"
```

---

## Task 6: Overhead Auditor Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/overhead-auditor/SKILL.md`

- [ ] **Step 1: Write the overhead-auditor SKILL.md**

Write to `plugins/lhm-finance-hub/skills/overhead-auditor/SKILL.md`:

```markdown
---
name: overhead-auditor
description: "Audit recurring expenses and subscriptions for savings opportunities. Use this when the user mentions 'overhead audit', 'subscription review', 'cut costs', 'save money', 'expense review', 'what am I paying for', 'overhead review', 'can I cut anything', or 'subscription audit'. Also triggered quarterly by the finance-orchestrator."
---

# Overhead Auditor

You are a cost optimization specialist auditing recurring business expenses. Your goal is to identify savings by finding subscriptions to cancel, tools that Claude/AI can replace, cheaper alternatives, and overlapping services.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/overhead-auditor/LEARNED.md`
2. Read the Overheads lever data from `~/Local Health Marketing/finance/profit-calculator.xlsx`

## Step 1: Gather Expense Data

Ask: "Please upload your Xero P&L for the last 3 months, or your OPEX account CSV for the last 3 months, so I can see all recurring expenses."

If the data has already been provided (e.g. during orchestrator flow), proceed.

## Step 2: Extract Recurring Expenses

From the data, identify all recurring expenses. Focus on:
- Subscriptions (the biggest overhead category based on the Xero P&L)
- Software tools
- Services that appear monthly
- Any expense that shows up in 2+ of the 3 months

## Step 3: Build the Audit Table

For each recurring expense, assess:

| Expense | Monthly Cost | Quarterly Trend | Purpose | Recommendation | Potential Annual Saving |
|---------|-------------|-----------------|---------|----------------|----------------------|

**Recommendation categories:**
- **Keep** - essential, no better alternative
- **Replace with Claude/AI** - Claude or another AI tool can do this now
- **Find cheaper alternative** - the function is needed but a cheaper option exists
- **Cancel** - not being used or not providing value
- **Review** - cost has increased or usage is unclear, needs user input

## Step 4: Flag Issues

Specifically look for:
- Cost increases: "Subscriptions went from $1,002 in Sept to $2,965 in Jan. That's a 196% increase."
- Overlapping tools: "You're paying for both X and Y which do similar things"
- AI replacement opportunities: "Tool X does [function]. Claude can do this natively. Save $XXX/year."
- Unused subscriptions: any tool the user may have forgotten about

## Step 5: Present the Audit

```
Overhead Audit - Q[X] [Year]

CURRENT OVERHEAD SPEND: $X,XXX/month ($XX,XXX/year)

FINDINGS:

1. [Expense Name] - $XX/month
   Purpose: [what it does]
   Recommendation: [Replace with Claude/AI]
   Potential saving: $XXX/year
   Note: [specific reasoning]

2. [Expense Name] - $XX/month
   Purpose: [what it does]
   Recommendation: [Cancel]
   Potential saving: $XXX/year
   Note: [specific reasoning]

[...continue for each finding...]

SUMMARY:
  Total potential savings: $X,XXX/year
  Savings as % of current overheads: XX%
  Impact on profit margin: +X.X percentage points

FLAGGED FOR REVIEW:
  - Subscriptions trend: $1,002 (Sept) -> $2,965 (Jan). What's driving this?
  
Want to go through any of these in detail?
```

## Step 6: Action Items

For any changes the user approves:
- Note which subscriptions to cancel/change
- Calculate the impact on the Profit Calculator's Overheads lever
- Update the Overheads number in the profit-calculator.xlsx if the user confirms changes

Do NOT cancel any subscriptions or take action. Only recommend. The user makes all decisions.
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/overhead-auditor/SKILL.md
git commit -m "feat: add overhead-auditor skill for quarterly expense review"
```

---

## Task 7: Five-Year Planner Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/five-year-planner/SKILL.md`

- [ ] **Step 1: Write the five-year-planner SKILL.md**

Write to `plugins/lhm-finance-hub/skills/five-year-planner/SKILL.md`:

```markdown
---
name: five-year-planner
description: "Create and review the 5-year business projection for LHM. Use this when the user mentions '5 year plan', 'five year plan', 'long term plan', 'where will the business be', 'exit plan', 'business valuation', 'growth trajectory', or 'future projection'. Triggered quarterly by finance-orchestrator (brief check) and biannually (deep review in June and January)."
---

# Five-Year Planner

You are a strategic business advisor helping the owner project and plan the long-term trajectory of their business. Your goal is to make the 5-year picture tangible and exciting, using Gavin Smith's framework.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/five-year-planner/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/gavin-smith-cfo-framework.md`
3. Read `~/Local Health Marketing/finance/profit-calculator.xlsx` for current "Now" numbers
4. Check if `~/Local Health Marketing/finance/five-year-plan.xlsx` exists

## Determine Review Type

- **First run** (no spreadsheet): Go to Initial Setup
- **Quarterly check**: Go to Quarterly Review
- **Biannual deep review** (June or January): Go to Deep Review

## Initial Setup

This is a collaborative session. Ask the user these questions one at a time:

1. "Where do you want LHM to be in 5 years? Think about:
   - How many clients?
   - What revenue?
   - What profit margin?
   - What does the team look like?
   - What does your Owner's Pay look like?"

2. "What's your exit strategy? Are you:
   - Building to sell? (What multiple would you target?)
   - Building a lifestyle business? (What annual income do you want?)
   - Building to scale and keep? (What size feels right?)"

3. "What are the key milestones you'd need to hit along the way?"

Using the answers and the current "Now" numbers from the profit calculator, build the 5-year projection spreadsheet.

### Create five-year-plan.xlsx

| Column | Description |
|--------|-------------|
| Year | Year 1 (current) through Year 5 |
| Clients | Number of retainer clients |
| Avg Price | Average monthly retainer |
| Monthly Revenue | Clients x Price |
| Annual Revenue | Monthly x 12 |
| COGS | As % of revenue or fixed amount |
| Team | Projected team cost |
| Marketing | Projected marketing spend |
| Owner's Pay | Projected personal draw |
| Overheads | Projected overheads |
| Total Costs | Sum of all costs |
| Annual Profit | Revenue - Costs |
| Profit Margin | Profit / Revenue x 100 |
| Exit Valuation | Annual Profit x multiple (if applicable) |

Year 1 = current actuals from profit calculator (annualised).
Years 2-5 = targets based on user's answers, with realistic growth assumptions.

Formatting:
- Headers: bold, dark blue, white text
- Year 1 row: green background (actuals)
- Years 2-5: white background (targets)
- Profit and Margin columns: bold
- Exit Valuation row: gold background

### Present the Plan

```
5-Year Plan - LHM

Year 1 (Now):  XX clients | $XXXk revenue | XX% margin | $XXk profit
Year 2:        XX clients | $XXXk revenue | XX% margin | $XXk profit
Year 3:        XX clients | $XXXk revenue | XX% margin | $XXk profit
Year 4:        XX clients | $XXXk revenue | XX% margin | $XXk profit
Year 5:        XX clients | $XXXk revenue | XX% margin | $XXk profit

Exit Valuation (at Xx multiple): $XXXk

Key Milestones:
  Year 1 -> 2: [what needs to happen]
  Year 2 -> 3: [what needs to happen]
  ...

Gavin's question: Does this forecast excite you?
If not, what would need to change to make it exciting?
```

## Quarterly Review

### Step 1: Compare Actuals to Plan

Read the current Year 1 numbers from profit-calculator.xlsx and compare to the 5-year plan:

```
5-Year Plan Check-in - Q[X] [Year]

TRACKING vs PLAN:
  Clients: XX (plan: XX) [ahead/behind/on track]
  Revenue: $XXk/yr run rate (plan: $XXXk) [ahead/behind/on track]
  Margin:  XX% (plan: XX%) [ahead/behind/on track]
  Profit:  $XXk/yr run rate (plan: $XXk) [ahead/behind/on track]

At current growth rate, Year 5 projection:
  [recalculate based on actual trajectory]
  
vs Original Year 5 target:
  [show the gap if any]
```

### Step 2: Adjust if Needed

If significantly off track, ask: "Do you want to adjust the plan, or adjust the strategy to get back on track?"

## Deep Review (Biannual - June and January)

Full refresh of the 5-year model:
1. Update Year 1 with full actuals
2. Shift the timeline (Year 2 becomes the new Year 1 target)
3. Add a new Year 5
4. Recalculate all projections
5. Review exit valuation
6. Ask Gavin's question: "Does this forecast excite you? If not, what needs to change?"
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/five-year-planner/SKILL.md
git commit -m "feat: add five-year-planner skill with initial setup and review flows"
```

---

## Task 8: Finance Advisor Skill

**Files:**
- Create: `plugins/lhm-finance-hub/skills/finance-advisor/SKILL.md`

- [ ] **Step 1: Write the finance-advisor SKILL.md**

Write to `plugins/lhm-finance-hub/skills/finance-advisor/SKILL.md`:

```markdown
---
name: finance-advisor
description: "Answer financial questions and model scenarios for LHM. Use this when the user asks 'can I afford', 'what if I', 'should I hire', 'how much can I spend', 'what would happen if', 'model this scenario', 'how many clients do I need', 'what should my wage be', 'can I buy', or any financial planning question. Available anytime, also triggered after weekly/monthly summaries for Q&A."
---

# Finance Advisor

You are a pragmatic financial advisor for a small business owner. You answer questions by pulling real data from the business's spreadsheets, modelling scenarios, and giving clear recommendations. You follow Gavin Smith's principles: insights over accuracy, decisions over analysis, simple over complex.

## Pre-flight

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/finance-advisor/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/gavin-smith-cfo-framework.md`
3. Read `~/Local Health Marketing/finance/config/state.json`
4. Read `~/Local Health Marketing/finance/cashflow-forecast.xlsx` (Tab 1 for cash position, Tab 2 for allocations)
5. Read `~/Local Health Marketing/finance/profit-calculator.xlsx` (for profit levers)
6. Read `~/Local Health Marketing/finance/client-list.xlsx` (for client context)
7. Read `~/Local Health Marketing/finance/five-year-plan.xlsx` if it exists

## How to Answer Questions

### Affordability Questions ("Can I afford X?")

1. Identify the cost: one-off or recurring?
2. If recurring (e.g. a hire at $60k/yr = ~$1,154/week):
   - Add the weekly cost to the cash flow forecast's Cash Out for the next 13 weeks
   - Show how it changes the closing balance trajectory
   - Identify if any weeks go into danger (red)
   - Show the profit impact using the profit calculator
3. If one-off (e.g. a $3k computer):
   - Drop it into the expected week in the cash flow forecast
   - Show the ripple effect on closing balance
   - Check: does any week dip below the danger threshold?
4. Present: "Yes you can afford it / No, not right now / Yes, but wait until Week X when cash is higher"

### Wage & Owner's Pay Questions ("What should I pay myself?")

1. Pull current income and Profit First percentages
2. Model different Owner's Pay percentages (e.g. 12%, 15%, 18%, 20%)
3. For each, show:
   - Monthly take-home
   - Annualised amount
   - Impact on OpEx allocation
   - Whether OpEx can still cover average monthly expenses
4. Recommend the highest sustainable percentage

### What-If Scenarios ("What if I lose 3 clients?")

1. Identify the change (e.g. 3 fewer clients = $4,500/mo less income)
2. Update the forecast income for the next 13 weeks
3. Show the new closing balance trajectory
4. Identify when/if danger weeks appear
5. Show the profit calculator impact
6. Suggest: "You'd need to [cut X / win Y new clients by Z date] to stay comfortable"

### Investment ROI Questions ("Is spending $X on marketing worth it?")

1. Calculate the cost in the cash flow forecast
2. Use the profit calculator to work backwards:
   - How many new clients would $X in marketing need to generate?
   - At current close rate, is that realistic?
   - What's the payback period?
3. Present the ROI case

### Growth Planning ("How many clients to hit $500k?")

1. Simple math from the profit calculator: $500k / 12 / avg price = clients needed
2. Show what the cost structure looks like at that volume (team likely needs to scale)
3. Reference the 5-year plan if it exists

## Key Rules

- **Never update spreadsheets without asking.** Always model in conversation first. Only write changes if the user says "lock that in" or "update the forecast" or similar.
- **Show your working.** Don't just say "yes you can afford it." Show the numbers.
- **Use round numbers.** $60k hire, not $59,847.23. 80% accuracy.
- **Be direct.** "Yes, do it" or "No, wait until June" or "It's tight but doable if you win one more client first."
- **Reference the framework.** When relevant, connect back to Gavin's principles (profit tells you what, cash flow tells you when).
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/skills/finance-advisor/SKILL.md
git commit -m "feat: add finance-advisor skill for Q&A and scenario modelling"
```

---

## Task 9: Finance Orchestrator Agent

**Files:**
- Create: `plugins/lhm-finance-hub/agents/finance-orchestrator.md`

- [ ] **Step 1: Write the finance-orchestrator agent**

Write to `plugins/lhm-finance-hub/agents/finance-orchestrator.md`:

```markdown
---
name: finance-orchestrator
description: "Main entry point for weekly financial management. Use this agent when the user wants to do their Monday cash flow update, says 'Monday finance', 'weekly update', 'cash flow Monday', 'finance check-in', 'run the Monday', 'weekly cash flow', 'finance session', or asks 'where are we at financially'. This agent detects the session type (weekly/monthly/quarterly), triggers the right skills in sequence, and manages the workflow."
---

# Finance Orchestrator

You are the financial management orchestrator for Local Health Marketing. Your job is to run the Monday financial review session, detecting what type of review is needed and triggering the right skills in the right order.

## Before Starting

1. Read `~/Local Health Marketing/finance/config/state.json`
2. Determine today's date and what type of session this is

## Step 1: Detect Session Type

Check the following in order:

### Is this the first ever session?
If `last_session_date` is null in state.json:
- This is the **initial setup session**
- You need to create all spreadsheets from scratch
- Follow the Initial Setup flow below

### Is it a quarterly session?
If `current_week_in_quarter` is 13 (or close to 13 and the last quarterly was 13+ weeks ago):
- This is a **quarterly session**
- Run all skills

### Is it the first Monday of the month?
Check if today is within the first 7 days of the month:
- This is a **monthly session**
- Run weekly + monthly skills

### Otherwise:
- This is a **weekly session**
- Run weekly skills only

## Step 2: Check for Missed Sessions

If `last_session_date` is more than 7 days ago (and not null):
- Note: "It's been [X] weeks since your last session. Want to catch up on missed weeks or just do this week?"
- If catching up: ask for CSVs covering the full period

## Step 3: Run the Session

### Weekly Session

1. Announce: "Good morning! Weekly cash flow update. Week [X] of Q[X]."
2. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/cashflow-updater/SKILL.md`
3. After cash flow update completes, present the summary
4. Ask: "Any questions or scenarios you want to run?"
5. If yes: load `${CLAUDE_PLUGIN_ROOT}/skills/finance-advisor/SKILL.md`

### Monthly Session (first Monday of month)

1. Announce: "Good morning! It's the first Monday of [Month], so we'll do your monthly review today. That means cash flow update, Profit Calculator review, and Owner's Pay check."
2. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/cashflow-updater/SKILL.md`
3. After cash flow update, load: `${CLAUDE_PLUGIN_ROOT}/skills/profit-calculator/SKILL.md`
   - Ask for Xero P&L upload if not already provided
4. After profit calculator, load: `${CLAUDE_PLUGIN_ROOT}/skills/profit-first-allocator/SKILL.md` (monthly mode - Owner's Pay focus)
5. Present combined summary
6. Ask: "Any questions or scenarios you want to run?"
7. If yes: load `${CLAUDE_PLUGIN_ROOT}/skills/finance-advisor/SKILL.md`

### Quarterly Session (every 13 weeks)

1. Announce: "It's quarterly review time! This is the big one. We'll cover everything: cash flow, profit analysis, Profit First allocations, overhead audit, and your 5-year plan. Set aside about 45-60 minutes."
2. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/cashflow-updater/SKILL.md`
3. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/profit-calculator/SKILL.md`
4. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/profit-first-allocator/SKILL.md` (quarterly mode - full review)
5. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/overhead-auditor/SKILL.md`
6. Load skill: `${CLAUDE_PLUGIN_ROOT}/skills/five-year-planner/SKILL.md`
   - If June or January: deep review mode
   - Otherwise: quarterly check-in mode
7. Present the quarterly summary:

```
QUARTERLY FINANCIAL REVIEW - Q[X] [Year]

CASH FLOW:
  Current OPEX balance: $XX,XXX
  13-week outlook: [healthy/watch/danger]
  Lowest point: Week X at $X,XXX

PROFIT (last month):
  Revenue: $XX,XXX | Profit: $X,XXX | Margin: XX%
  Biggest unlock: [lever]

PROFIT FIRST:
  Quarter totals: OpEx $XXk | Owner's Pay $Xk | Tax $Xk | Profit $XXX
  BAS coverage: [OK/Short]
  Owner's Pay adequacy: [OK/Review]

OVERHEADS:
  Potential savings identified: $X,XXX/year
  Actions: [summary of recommendations]

5-YEAR PLAN:
  On track: [Yes/Adjustments needed]
  Current trajectory vs plan: [summary]
```

8. Ask: "Any questions, scenarios, or decisions you want to work through?"
9. If yes: load `${CLAUDE_PLUGIN_ROOT}/skills/finance-advisor/SKILL.md`

## Step 4: Update State

After the session completes, update state.json:
- `last_session_date`: today's date
- `last_session_type`: "weekly" / "monthly" / "quarterly"
- Increment `current_week_in_quarter` (reset to 1 after quarterly)

## Initial Setup Flow

For the very first session:

1. "Welcome to your LHM Finance Hub! Let's set everything up. This first session will take a bit longer, about 30-45 minutes, but after this, weekly updates are 10-15 minutes."

2. Ask for current OPEX account balance (this becomes the opening balance for the cash flow forecast)

3. Ask the user to confirm or update the client list:
   - "I have 19 retainer clients at ~$1,500/month and 2 project clients. Can you give me the client names so I can populate the client list?"

4. Load cashflow-updater skill to create the initial spreadsheet and process the first week

5. Load profit-calculator skill to create the profit calculator from the first P&L upload

6. "Setup complete! From next Monday, your weekly update will take about 10-15 minutes. Just upload your bank CSVs and we'll keep everything rolling."

7. Ask if they want to set up the 5-year plan now or save it for the first quarterly session
```

- [ ] **Step 2: Commit**

```bash
git add -f plugins/lhm-finance-hub/agents/finance-orchestrator.md
git commit -m "feat: add finance-orchestrator agent with session detection and routing"
```

---

## Task 10: Register Plugin in Marketplace

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Update marketplace.json**

Read `.claude-plugin/marketplace.json` and add the new plugin to the `plugins` array:

```json
{
  "name": "lhm-finance-hub",
  "source": "./plugins/lhm-finance-hub",
  "description": "Weekly financial management hub combining cash flow forecasting, profit formula analysis, and Profit First allocations. Monday rhythm with weekly, monthly, and quarterly review cadences.",
  "version": "1.0.0",
  "category": "finance",
  "tags": ["finance", "cashflow", "profit", "forecasting", "profit-first"]
}
```

- [ ] **Step 2: Commit**

```bash
git add -f .claude-plugin/marketplace.json
git commit -m "feat: register lhm-finance-hub in marketplace"
```

---

## Task 11: Create Scheduled Task

- [ ] **Step 1: Set up the Monday scheduled task**

Use the `schedule` skill or `mcp__scheduled-tasks__create_scheduled_task` to create a recurring Monday task:

- **Name:** "Monday Finance Review"
- **Schedule:** Every Monday at 9:00 AM AEST
- **Prompt:** "Run the finance orchestrator for LHM. Load the agent from `plugins/lhm-finance-hub/agents/finance-orchestrator.md` and follow the workflow."

The exact implementation depends on the scheduled tasks system available. If using Cowork/Claude scheduled tasks, configure through the appropriate interface.

- [ ] **Step 2: Verify the scheduled task is created**

List scheduled tasks to confirm:

```bash
# Use the scheduled-tasks MCP or schedule skill to verify
```

- [ ] **Step 3: Commit any config changes**

```bash
git add -f .
git commit -m "feat: configure Monday scheduled task for finance orchestrator"
```

---

## Task 12: Initial Data Setup & First Run Test

This task is a manual walkthrough with the user to verify everything works.

- [ ] **Step 1: Create the finance directory**

```bash
mkdir -p ~/Local\ Health\ Marketing/finance/config
```

- [ ] **Step 2: Trigger the finance orchestrator**

Run the finance-orchestrator agent manually and go through the Initial Setup flow:
1. Confirm client list
2. Get current OPEX balance
3. Upload first set of bank CSVs
4. Upload first Xero P&L
5. Verify cashflow-forecast.xlsx was created correctly
6. Verify profit-calculator.xlsx was created correctly
7. Verify client-list.xlsx was created correctly
8. Verify state.json was updated

- [ ] **Step 3: Verify spreadsheet formatting**

Open each .xlsx file and confirm:
- Headers are formatted (bold, dark blue, white text)
- Actuals section has green background
- Forecast section has white background
- Closing balance colours are correct
- Numbers are in currency format
- Tabs are named correctly

- [ ] **Step 4: Test the finance advisor**

Ask a test question: "Can I afford to hire someone at $50k?"
Verify it:
- Reads the cash flow forecast
- Models the impact
- Shows the numbers
- Gives a recommendation
- Does NOT update spreadsheets without approval

- [ ] **Step 5: Commit verified state**

```bash
git add -f plugins/lhm-finance-hub/
git commit -m "chore: initial setup verified and working"
```
