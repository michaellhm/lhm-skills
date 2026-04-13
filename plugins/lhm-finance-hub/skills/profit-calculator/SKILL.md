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
