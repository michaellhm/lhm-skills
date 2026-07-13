---
title: Context Preamble
description: Standard client context loading sequence. Run at the top of every specialist agent before any work begins.
---

# Context Preamble

Every specialist agent runs these steps in order before doing anything else. Do not skip steps. Do not start work until the 4-line state summary is displayed.

## Step 1 — Find client folder

Scan the current working directory for client-named folders. A folder is a client folder if it contains a `client_profile.md` file, or if it was explicitly named by the user. Ignore folders like `assets/`, `scripts/`, `references/`, `node_modules/`, or any folder starting with `.`

- If multiple folders exist, ask: "Which client are we working on today?"
- If one folder matches what the user mentioned, confirm it and proceed
- If no folder is found, say: "I can't see any client folders. Please navigate to your Clients directory." and stop
- If the client folder doesn't exist, create it and run `${CLAUDE_PLUGIN_ROOT}/skills/client-onboarding/SKILL.md` before continuing

## Step 2 — Load client profile

Read `[client-folder]/client_profile.md`.

- Treat it as authoritative. Never re-ask for information already present.
- Set `is_health_client = true` if the profile's industry, business type, or notes field indicates health, medical, allied health, psychology, physiotherapy, chiropractic, dental, or any other regulated health profession. Set `false` for all other businesses. AHPRA rules apply only when `is_health_client = true`.
- Check that conversion economics are defined: profitable CPA threshold, average revenue per conversion, margin/overhead structure.
  - If any of these are missing AND the session involves Google Ads work: flag the gap and ask before proceeding with any Ads analysis.
- If `client_profile.md` does not exist or is empty: run the client-onboarding skill first.

## Step 3 — Load client goals

Read `[client-folder]/goals.md`.

- If the file does not exist: create it with this template and ask the user to fill it in before proceeding. If the file exists but conversion economics fields are blank or show only `$` placeholders, treat it the same as a missing file for the purpose of flagging gaps to the user — do not silently proceed with empty economics data.

```
# Goals — [Client Name]

## Conversion Economics
- Average revenue per conversion/booking: $
- Estimated margin after overheads (%):
- Profitable CPA threshold: $
- Profitable ROAS threshold:

## Channel KPIs
### Google Ads
- Monthly lead target:
- CPA target: $
- Monthly budget: $

### SEO
- Primary keyword targets:
- Organic traffic target (monthly sessions):
- Ranking targets (keyword → position by date):

### Content
- Monthly content output target:

## Benchmarks
- Last 90 days vs prior 90 days summary:
- Last year vs this year:

## Annual targets:
-
```

## Step 4 — Load active projects

Read `[client-folder]/current-projects.md`.

- If the file does not exist: create it with this template. After creating the file, note to the user: "current-projects.md not found — created a template. Please populate it with active work when you get a chance."

```
# Current Projects — [Client Name]
Last updated: YYYY-MM-DD

## Active
- [Project name] — [Brief description] — Started: YYYY-MM-DD

## Completed this quarter
-

## Backlog
-
```

## Step 5 — Scan discipline folder

Scan the channel folder that matches the calling agent or skill. If the session involves multiple channels, scan all relevant folders. Channel folders:
- Google Ads sessions: `[client-folder]/google_ads/`
- SEO sessions: `[client-folder]/seo/`
- Content sessions: `[client-folder]/content/`
- Analytics: `[client-folder]/analytics/`

Read the most recent files to understand: last zone classification, last keyword snapshot, last review findings, any open action items from prior sessions. If no files exist within the last 90 days, read the most recent file regardless of date. If the folder does not exist, note this in the state summary.

## Step 6 — Load agency learnings

Read the relevant agency learnings file:
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/google-ads.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/seo.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/content.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/wordpress.md`

If a file does not exist, skip it and continue. Load all files relevant to the disciplines involved in this session (not just one).

Apply any relevant entries to this session.

## Step 7 — Display state summary

Narrate a 4-line state summary before doing anything else:

```
Client: [Name] | Health: yes/no | AHPRA: applies/not applicable
State: [key metric vs last period] | [zone or ranking status] | [CPA vs target]
Goals: [primary KPI] | [90-day target] | [annual target]
Active: [current projects — one line summary]
```

If any data is missing (no goals.md, no prior discipline folder work), say what's missing in the summary line rather than leaving it blank:

```
Client: Bayside Physio | Health: yes | AHPRA: applies
State: No prior Google Ads data on file | CPA target: not set
Goals: goals.md not found — created template, please fill in
Active: No active projects on file
```
