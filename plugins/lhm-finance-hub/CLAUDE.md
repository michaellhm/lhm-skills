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
