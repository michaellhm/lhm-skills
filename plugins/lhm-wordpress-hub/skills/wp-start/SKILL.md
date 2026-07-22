---
name: wp-start
description: "Start a session in the WordPress hub. Use this when the user wants to begin a website project, asks 'build a website', 'start a WordPress site', 'start an Astro site', mentions 'website build', 'new site', 'landing page', 'LP campaign', or invokes /lhm-wordpress-hub:wp-start. Also use when the user mentions 'contact form', 'form submissions', 'wire up forms', 'set up form handling', 'Cloudflare forms', 'D1 form submissions', or 'Turnstile'. Also use when the user mentions 'QA checklist', 'run the QA', 'pre-launch checklist', 'site QA', 'launch checklist', or 'ready to go live'. This skill is a router — it detects which workflow (full WP build, LP campaign, or standalone utility skill) and hands off to the right orchestrator or skill."
---

# WP Start — Router

The plugin handles two workflows. This skill detects which one and hands off.

## Step 0: Check for Standalone Utility Intent

If the user's request clearly targets a standalone skill rather than a full workflow, route directly without going through workflow detection:

| User says | Route to |
|---|---|
| "contact form", "form submissions", "wire up forms", "set up form handling", "Cloudflare forms", "D1 submissions", "Turnstile" | `contact-form-submissions` skill |
| "QA checklist", "run the QA", "pre-launch checklist", "site QA", "launch checklist", "quality assurance", "ready to go live checklist" | `site-launch-qa` skill |

For a standalone route: tell the user what you're loading, then load the relevant skill file and follow it:
- Contact forms → `${CLAUDE_PLUGIN_ROOT}/skills/contact-form-submissions/SKILL.md`
- QA checklist → `${CLAUDE_PLUGIN_ROOT}/skills/site-launch-qa/SKILL.md`

---

## Step 1: Detect Workflow

Use Glob to inspect the current working directory and any client folders detected:

| Signal | Workflow |
|---|---|
| `wordpress/website-project-management.md` or `astro/website-project-management.md` exists | Full Website Build |
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
- "Full website build" → ask platform question below, then run `wp-project-setup`, then `website-build-orchestrator`
- "Landing page campaign" → run `wp-project-setup` (creates client root if needed), then `landing-page-orchestrator` (which sets up the campaign folder via `lp-project-manager`)
- "Not sure yet — let's just create the client folder" → run `wp-project-setup` and stop

**If "Full website build" selected:** ask the platform question before handing off to `wp-project-setup`:

Use AskUserQuestion:
> "Which platform are we building on?"

Options:
- "WordPress (block theme — standard LHM build)"
- "Astro (static site framework — git-only workflow)"

Pass this choice to `wp-project-setup`. The skill records it in `client_profile.md` and the PM doc, so every downstream skill knows which path it's on.

> **Note for Astro builds:** use the Astro workflow and PM template in `wp-project-manager`. Do not route Astro builds through WordPress-only theme, Gutenberg, or SSH-deploy skills.

## Step 4: Confirm Handoff

Tell the user which orchestrator was loaded and let it take over from here. Do not proceed with phase work in this skill — that's the orchestrator's job.

## What This Skill Does NOT Do

- Phase detection (orchestrators handle this)
- Skill routing within a workflow (orchestrators handle this)
- Project management updates (`wp-project-manager` / `lp-project-manager` handle this)
- Folder creation (`wp-project-setup` handles this)

This skill is a router and, for a fresh full website project, the kickoff brief collector. Do not begin project setup until the kickoff brief below is complete.

## Fresh Full-Website Kickoff Brief

For a fresh full website build, ask these questions **one at a time** before running `wp-project-setup`. Do not show a long form. Briefly reflect each answer, then ask the next question.

1. **Client relationship:** "Is this a new client or an existing client?"
2. **Strategy call:**
   - New client: set `strategy_call_required: yes`; tell the user the call is mandatory. Do not ask whether to skip it.
   - Existing client: ask Michael, "Do we know this client well enough to proceed, or do we need a strategy call?"
3. **Design scope:** "Are we redesigning from scratch, improving the current design, or migrating it largely as-is?"
4. **Copy scope:** "Are we rewriting all copy, selectively rewriting it, or migrating it as-is?"
5. **Deadline:** "Is there a fixed deadline or launch constraint? If not, we'll use the standard seven-week active-delivery schedule."
6. **Client considerations:** "Are there any special requirements, known sensitivities, difficult stakeholders, compliance needs, or scope risks?"
7. **Michael attendance:** "Which client approval meetings, if any, does Michael want to attend? This can be decided case by case."

Summarise the completed brief and ask for confirmation before setup. Pass the answers to `wp-project-setup`, which records them in `client_profile.md` and creates the project-management doc immediately.

Do not ask which pages belong in the prototype at kickoff. Michael chooses the prototype page set when he signs off the SEO sitemap.

## Standalone Skills Routable from Here

| Skill | When to route |
|---|---|
| `contact-form-submissions` | User asks about contact forms, D1 form storage, Turnstile, or form email notifications |
| `site-launch-qa` | User asks about the QA checklist, pre-launch checks, running QA, or going live |
