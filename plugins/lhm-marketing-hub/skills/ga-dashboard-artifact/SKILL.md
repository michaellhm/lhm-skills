---
name: ga-dashboard-artifact
description: "Generate an interactive analytics dashboard as a Claude Artifact. Use when the user wants to see how the site is performing, wants a traffic report, analytics dashboard, or monthly analytics review. Pulls GA4 data via the analytics MCP and renders KPI tiles, trend charts, and period comparison as an interactive Artifact. Triggers on: 'analytics dashboard', 'GA dashboard', 'traffic report', 'how is the site performing', 'monthly analytics', 'analytics review', 'site performance'."
---

# GA Dashboard Artifact

Pull GA4 data and render an interactive analytics dashboard as a Claude Artifact.

## Prerequisites

- GA4 property ID for this client (check `client_profile.md`)
- Analytics MCP connected
- Date range to report on (default: last 30 days vs prior 30 days)

If GA4 property ID is missing from the client profile: ask the user for it, then run `${CLAUDE_PLUGIN_ROOT}/skills/ga-event-config/SKILL.md` to set up the property properly before continuing.

## Step 1: Confirm parameters

Ask:
- Date range (default: last 30 days — confirm or change)
- Comparison period (default: prior 30 days — confirm or change)
- Any specific metrics or pages to highlight?

## Step 2: Pull GA4 data via analytics MCP

Pull the following for both the reporting period and comparison period:

**Core metrics:**
- Sessions
- Users (total and new)
- Conversions (by conversion event)
- Bounce rate / engagement rate
- Average session duration

**Traffic sources:**
- Sessions by channel (Organic, Paid, Direct, Referral, Social, Email)

**Top pages:**
- Top 10 pages by sessions
- Top 5 pages by conversions

**Geographic:**
- Top 5 cities/regions (if relevant to local business)

## Step 3: Calculate period-over-period changes

For each metric: calculate the absolute change and percentage change vs the comparison period.
Flag significant movements (>20% change) for callout in the dashboard.

## Step 4: Build the Artifact

Generate a Claude Artifact with:

**KPI tiles row (top):**
- Sessions | Users | Conversions | Top channel
- Each tile: current value, change vs prior period (↑ green / ↓ red), percentage change

**Trend chart:**
- Line chart: sessions and conversions over the reporting period (daily)

**Channel breakdown:**
- Bar chart: sessions by channel, current vs prior period

**Top pages table:**
- Page | Sessions | Conversions | Change vs prior

**Callouts section:**
- Highlight 2-3 significant movements with a plain-English explanation

Use the dataviz skill design system for chart styling.

## Step 5: Save summary

Save a text summary to `[client-folder]/analytics/YYYY-MM/dashboard-summary-YYYY-MM.md`:

```markdown
# Analytics Summary — [Client Name]
**Period:** YYYY-MM-DD to YYYY-MM-DD vs YYYY-MM-DD to YYYY-MM-DD
**Generated:** YYYY-MM-DD

## Key Metrics
| Metric | Current | Prior | Change |
|--------|---------|-------|--------|
| Sessions | | | |
| Users | | | |
| Conversions | | | |

## Notable Movements
-

## Top Pages
-

## Recommended Actions
-
```

## Step 6: Offer next steps

"Dashboard generated. Based on what I can see:
- [Observation → skill recommendation]
- [Observation → skill recommendation]

Want me to dig into any of these?"
