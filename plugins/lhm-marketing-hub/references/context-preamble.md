---
title: Context Preamble
description: Standard client context loading sequence. Run at the top of every specialist agent before any work begins.
---

# Context Preamble

Every specialist agent runs these steps in order before doing anything else. Do not skip steps. Do not start work until the 4-line state summary is displayed.

## Step 1 — Resolve canonical Obsidian client

Read `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`, then resolve the named client in the configured Local Health Marketing Obsidian vault. Do not scan the current working directory and infer a client from repository or temporary folder names.

- If multiple folders exist, ask: "Which client are we working on today?"
- If one folder matches what the user mentioned, confirm it and proceed
- If no canonical client is found, name that exact gap and route to the owning Project Hub onboarding workflow. Do not create a folder here.

## Step 2 — Load client profile

Read `[client-folder]/client_profile.md`.

- Treat it as authoritative. Never re-ask for information already present.
- Set `is_health_client = true` if the profile's industry, business type, or notes field indicates health, medical, allied health, psychology, physiotherapy, chiropractic, dental, or any other regulated health profession. Set `false` for all other businesses. AHPRA rules apply only when `is_health_client = true`.
- Check that conversion economics are defined: profitable CPA threshold, average revenue per conversion, margin/overhead structure.
  - If any of these are missing AND the session involves Google Ads work: flag the gap and ask before proceeding with any Ads analysis.
- If `client_profile.md` does not exist or is empty: report the missing canonical profile and route to the owning Project Hub onboarding/client-update workflow. Do not create a local substitute.

## Step 3 — Load client goals

Read `[client-folder]/goals.md`.

- If the canonical record does not exist, or required economics fields are blank, report the exact missing record or fields and route the update through the owning Project Hub workflow. Do not create a template in this preamble and do not silently proceed with empty economics data.

## Step 4 — Load active projects

Read `[client-folder]/current-projects.md`.

- If the canonical active-project record does not exist, report that exact gap and route its creation through the owning Project Hub kickoff or project-manager workflow. Do not create a template in this preamble.

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
Goals: canonical goals record not found — routed to Project Hub; not created here
Active: No active projects on file
```
