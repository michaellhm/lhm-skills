---
name: ga-dashboard
description: "Generate a GA4 analytics dashboard with period-over-period comparison. Use this when the user mentions 'analytics dashboard', 'GA dashboard', 'traffic report', 'site performance', 'how is the site performing', 'analytics report', 'show me the numbers', 'traffic overview', 'conversion report', or 'quick dashboard'. Pulls data from GA4 via MCP and generates a standardised markdown dashboard."
---

# GA Dashboard

You are an analytics reporting specialist. Your goal is to pull GA4 data via MCP and generate a standardised dashboard with period-over-period comparison, conversion analysis, and actionable recommendations.

## Pre-flight

1. Read `client_profile.md` from the client folder
2. Look for the `## Google Analytics` section
   - **If missing**: tell the user "No GA configuration found. Run the `ga-event-config` skill first to set up your property and classify conversions." Then **stop**.
   - **If found**: extract property ID, primary conversions, secondary conversions, and funnel steps

## Step 1: Get Context

Ask the user:

1. **Comparison period** (default: last 30 days vs previous 30 days):
   - "Last 30 days vs previous 30 days" (default)
   - "Last 90 days vs previous 90 days"
   - Custom dates
2. **Focus area** (optional): "Is there anything specific you want me to investigate? (e.g. 'why did traffic drop', 'check conversion rate', 'organic performance')"

If the user says "just run it" or similar, use the defaults and proceed.

## Step 2: Pull GA Reports

Use `run_report` for all reports. Always include **two date ranges** for comparison.

For a 30-day comparison, use:
- Period 1: `30daysAgo` to `yesterday`
- Period 2: `60daysAgo` to `31daysAgo`

### Report 1: Traffic Overview (by date)
- **Dimensions**: `date`
- **Metrics**: `sessions`, `totalUsers`, `newUsers`, `screenPageViews`, `engagementRate`, `averageSessionDuration`, `bounceRate`
- **Date ranges**: both periods

### Report 2: Channel Breakdown
- **Dimensions**: `sessionDefaultChannelGroup`
- **Metrics**: `sessions`, `totalUsers`, `conversions`, `engagementRate`
- **Order**: descending by sessions
- **Date ranges**: both periods

### Report 3: Source / Medium
- **Dimensions**: `sessionSource`, `sessionMedium`
- **Metrics**: `sessions`, `totalUsers`, `conversions`, `bounceRate`
- **Order**: descending by sessions
- **Limit**: 20
- **Date ranges**: both periods

### Report 4: Landing Pages
- **Dimensions**: `landingPage`
- **Metrics**: `sessions`, `bounceRate`, `averageSessionDuration`, `conversions`
- **Order**: descending by sessions
- **Limit**: 20
- **Date ranges**: both periods

### Report 5: Conversion Events
- **Dimensions**: `eventName`
- **Metrics**: `eventCount`
- **Dimension filter**: filter to only the primary and secondary conversion event names from client_profile.md
- **Date ranges**: both periods

### Report 6: Funnel Events (if funnel defined)
- **Dimensions**: `eventName`
- **Metrics**: `eventCount`
- **Dimension filter**: filter to only the funnel step event names
- **Date ranges**: both periods

### Report 7: Device Breakdown
- **Dimensions**: `deviceCategory`
- **Metrics**: `sessions`, `totalUsers`, `conversions`, `bounceRate`
- **Date ranges**: both periods

### Report 8: Country Breakdown
- **Dimensions**: `country`
- **Metrics**: `sessions`, `totalUsers`, `conversions`
- **Order**: descending by sessions
- **Limit**: 10
- **Date ranges**: both periods

**Run as many reports in parallel as possible** to minimise wait time.

If any report fails, note it and continue with the data you have. Do not fabricate data.

## Step 3: Generate Dashboard

Read the template from `${CLAUDE_PLUGIN_ROOT}/skills/ga-dashboard/templates/dashboard-template.md` and populate it with the data from Step 2.

### Calculation Notes

For period-over-period comparison, calculate:
- **Change %** = ((Current - Previous) / Previous) x 100
- Use directional indicators: positive change on good metrics (sessions, conversions) = good, positive change on bad metrics (bounce rate) = bad
- Format large numbers with commas
- Round percentages to 1 decimal place

### Funnel Analysis (if funnel defined)

Calculate drop-off between each step:
- Step 1 count → Step 2 count → Step 3 count → Step 4 count
- Drop-off % between each step
- Overall funnel conversion rate (last step / first step)

### Recommendations

Generate 3-5 actionable recommendations based on the data. Each recommendation should:
- Reference specific data points
- Suggest a concrete action
- Mention which skill could help execute it (if applicable)

Examples:
- "Organic traffic dropped 15% — run `seo-audit` to diagnose"
- "Mobile bounce rate is 12% higher than desktop — run `page-cro` on top mobile landing pages"
- "Form submissions dropped 20% despite stable traffic — run `form-cro` to investigate"

## Step 4: Save Dashboard

Save to: `analytics/YYYY-MM/ga-dashboard-YYYY-MM-DD.md` inside the client folder.

Present the dashboard to the user and narrate the key findings.

## Rules

- **Never fabricate metrics** — only use data returned by MCP
- **Never skip the GA config check** — if no config exists, stop and direct to `ga-event-config`
- **Always use two date ranges** — comparison is the core value of this dashboard
- **If MCP fails**: tell the user which reports failed and offer to retry or accept partial data
- **Format for readability** — use tables, directional indicators, and concise commentary

## Related Skills

- **ga-event-config** — sets up the GA config this skill depends on
- **analytics-tracking** — covers GA4/GTM implementation
- **seo-audit** — for organic traffic deep dives
- **page-cro** — for conversion optimisation on underperforming pages
