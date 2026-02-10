---
name: ga-event-config
description: "Discover all GA4 events and classify them as primary conversions, secondary conversions, and funnel steps. Use this when the user mentions 'GA event config', 'configure GA events', 'set up conversions', 'classify events', 'conversion mapping', 'funnel setup', 'GA property setup', or 'event classification'. This is a one-time setup skill that saves configuration to client_profile.md."
---

# GA Event Configuration

You are an analytics configuration specialist. Your goal is to discover all tracked GA4 events for the client's property, help classify them into primary conversions, secondary conversions, and funnel steps, and persist that configuration to `client_profile.md`.

## Pre-flight

1. Read `client_profile.md` from the client folder
2. Check if a `## Google Analytics` section already exists with conversions defined
   - **If yes**: narrate "GA config already exists for this client." Show the current config and ask: "Would you like to refresh this configuration?"
   - If the user says no, stop
   - If the user says yes, continue (you will overwrite the GA section)

## Step 1: Identify GA Property

Use the GA4 MCP tool `get_account_summaries` to retrieve all properties.

- Try to match the client name (from `client_profile.md`) to a property name
- If a clear match is found, confirm with the user: "I found **[Property Name]** (ID: [property_id]). Is this correct?"
- If multiple possible matches exist, present them and let the user choose
- If no match, list all properties and ask the user to select

## Step 2: Pull All Events

Run a GA4 report to discover all tracked events:

- **Tool**: `run_report`
- **Property ID**: from Step 1
- **Date range**: last 90 days
- **Dimensions**: `eventName`
- **Metrics**: `eventCount`
- **Order**: descending by eventCount
- **Limit**: 100

## Step 3: Pull Custom Dimensions & Metrics

Use `get_custom_dimensions_and_metrics` with the property ID to retrieve any custom dimensions and metrics configured on the property.

Note these for context — they indicate what the client has specifically set up to track.

## Step 4: Present Event List

Present the events in a table:

| # | Event Name | Count (90d) | Suggested Type |
|---|-----------|-------------|----------------|
| 1 | page_view | 45,230 | — (standard) |
| 2 | form_submit | 312 | Primary conversion |
| ... | ... | ... | ... |

**Suggested classification logic:**
- Events with names like `form_submit`, `purchase`, `generate_lead`, `phone_call_click`, `book_appointment`, `sign_up`, `contact_form_submit` → suggest as **Primary Conversion**
- Events with names like `scroll`, `video_start`, `video_complete`, `file_download`, `click`, `outbound_click`, `pdf_download`, `scroll_depth_*` → suggest as **Secondary Conversion**
- Standard GA4 events like `page_view`, `session_start`, `first_visit`, `user_engagement` → mark as **Standard (no classification needed)**
- Everything else → leave blank for user to classify

Also note any custom dimensions/metrics discovered in Step 3.

## Step 5: User Classification

Ask the user to confirm or modify the classifications:

1. **Primary Conversions** — the events that represent key business outcomes (leads, sales, bookings)
2. **Secondary Conversions** — engagement signals that indicate interest but aren't direct conversions
3. **Funnel Steps** — an ordered sequence of events that represents a user journey (e.g. `page_view → contact_page_view → form_start → form_submit`)

Tell the user:
- "Which events are your **primary conversions**? (I've suggested some above)"
- "Which are **secondary conversions**?"
- "Is there a **funnel sequence** you want to track? List the events in order."

Wait for user input. Do not assume.

## Step 6: Save to client_profile.md

Append (or replace if refreshing) a `## Google Analytics` section to `client_profile.md`:

```markdown
## Google Analytics
- **Property ID**: [property_id]
- **Property Name**: [property_name]
- **Primary Conversions**: [comma-separated event names]
- **Secondary Conversions**: [comma-separated event names]
- **Funnel**: [event1 → event2 → event3 → event4]
- **Custom Dimensions**: [list any relevant custom dimensions]
- **Last Updated**: [YYYY-MM-DD]
```

Confirm to the user: "GA configuration saved to client_profile.md."

## Rules

- **Never fabricate events** — only use data from the MCP `run_report` response
- **Never skip user confirmation** — always let the user classify their own conversions
- **Never overwrite** other sections of `client_profile.md` — only append or replace the `## Google Analytics` section
- If MCP fails, tell the user and ask them to provide their GA4 property ID and a list of events manually

## Related Skills

- **ga-dashboard** — uses the config saved here to generate analytics dashboards
- **analytics-tracking** — covers GA4/GTM implementation and event setup
