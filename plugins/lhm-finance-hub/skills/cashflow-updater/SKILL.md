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
