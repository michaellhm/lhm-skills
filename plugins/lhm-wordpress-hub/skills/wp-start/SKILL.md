---
name: wp-start
description: "Start a session in the WordPress hub. Use this when the user wants to begin a website project, asks 'build a website', 'start a WordPress site', mentions 'website build', 'new site', 'landing page', 'LP campaign', or invokes /lhm-wordpress-hub:wp-start. This skill is a router — it detects which workflow (full WP build or LP campaign) and hands off to the right orchestrator."
---

# WP Start — Router

The plugin handles two workflows. This skill detects which one and hands off.

## Step 1: Detect Workflow

Use Glob to inspect the current working directory and any client folders detected:

| Signal | Workflow |
|---|---|
| `wordpress/website-project-management.md` exists | Full Website Build |
| `landing-pages/[campaign]/landing-page-project-management.md` exists | Landing Page Campaign |
| Both exist | Ask user which to work on |
| Neither exists, but a `client_profile.md` exists | Ask user — both workflows are possible |
| Nothing exists | Ask user — fresh start, both workflows are possible |

## Step 2: Confirm with User

Use AskUserQuestion:

> "Which workflow are we running today?"

Options (presented based on what was detected):
- "Full WordPress website build"
- "Landing page campaign"
- "Set up a new project / something else"

## Step 3: Route

### Full Website Build
Hand off to `website-build-orchestrator`:
- Tell the user: "Starting a full website build session. Loading the website-build-orchestrator."
- Load `${CLAUDE_PLUGIN_ROOT}/agents/website-build-orchestrator.md`

### Landing Page Campaign
Hand off to `landing-page-orchestrator`:
- Tell the user: "Starting a landing page campaign session. Loading the landing-page-orchestrator."
- Load `${CLAUDE_PLUGIN_ROOT}/agents/landing-page-orchestrator.md`

### Fresh / New Project
Use AskUserQuestion:
> "What kind of project are we setting up?"

Options:
- "Full WordPress website build" → run `wp-project-setup`, then `website-build-orchestrator`
- "Landing page campaign" → run `wp-project-setup` (creates client root if needed), then `landing-page-orchestrator` (which sets up the campaign folder via `lp-project-manager`)
- "Not sure yet — let's just create the client folder" → run `wp-project-setup` and stop

## Step 4: Confirm Handoff

Tell the user which orchestrator was loaded and let it take over from here. Do not proceed with phase work in this skill — that's the orchestrator's job.

## What This Skill Does NOT Do

- Phase detection (orchestrators handle this)
- Skill routing within a workflow (orchestrators handle this)
- Project management updates (`wp-project-manager` / `lp-project-manager` handle this)
- Folder creation (`wp-project-setup` handles this)

This skill is a thin router. Keep it that way.
