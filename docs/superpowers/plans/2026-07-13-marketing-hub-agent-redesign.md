# Marketing Hub Agent Architecture Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the LHM Marketing Hub plugin from a monolithic orchestrator into five self-sufficient specialist agents with shared infrastructure, multi-model writing pipelines, and agency-level learning.

**Architecture:** Five specialist agents (start, google-ads, seo, content, wordpress) each embed a shared context preamble and philosophy reference, making them self-sufficient entry points. Shared reference files handle client state, discipline philosophy, self-improvement protocol, and agency-wide learnings. Three new skills (post-meeting-review, client-update, ga-dashboard-artifact) handle meeting debrief, data propagation, and analytics reporting.

**Tech Stack:** Claude Code plugin system (markdown agents/skills), OpenRouter MCP for multi-model routing, Google Ads MCP, AdPulse MCP, Keywords Everywhere MCP, GA4 analytics MCP, WordPress REST API, Fathom MCP.

**Spec:** `docs/superpowers/specs/2026-07-13-marketing-hub-agent-redesign.md`

---

## File Map

### New files to create

**Shared infrastructure:**
- `plugins/lhm-marketing-hub/references/context-preamble.md`
- `plugins/lhm-marketing-hub/references/self-improvement-protocol.md`
- `plugins/lhm-marketing-hub/references/lhm-philosophy/google-ads.md`
- `plugins/lhm-marketing-hub/references/lhm-philosophy/seo.md`
- `plugins/lhm-marketing-hub/references/lhm-philosophy/content.md`
- `plugins/lhm-marketing-hub/references/lhm-philosophy/wordpress.md`
- `plugins/lhm-marketing-hub/references/agency-learnings/google-ads.md`
- `plugins/lhm-marketing-hub/references/agency-learnings/seo.md`
- `plugins/lhm-marketing-hub/references/agency-learnings/content.md`
- `plugins/lhm-marketing-hub/references/agency-learnings/wordpress.md`

**New agents:**
- `plugins/lhm-marketing-hub/agents/start.md`
- `plugins/lhm-marketing-hub/agents/google-ads.md`
- `plugins/lhm-marketing-hub/agents/seo.md`
- `plugins/lhm-marketing-hub/agents/content.md`
- `plugins/lhm-marketing-hub/agents/wordpress.md`

**New skills:**
- `plugins/lhm-marketing-hub/skills/post-meeting-review/SKILL.md`
- `plugins/lhm-marketing-hub/skills/post-meeting-review/LEARNED.md`
- `plugins/lhm-marketing-hub/skills/client-update/SKILL.md`
- `plugins/lhm-marketing-hub/skills/client-update/LEARNED.md`
- `plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/SKILL.md`
- `plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/LEARNED.md`

### Files to modify
- `plugins/lhm-marketing-hub/.claude-plugin/plugin.json` — version bump 1.4.2 → 1.4.3
- `.claude-plugin/marketplace.json` — version bump to match
- `plugins/lhm-marketing-hub/skills/ad-copy-generator/SKILL.md` — add multi-model creative process
- `plugins/lhm-marketing-hub/agents/marketing-assistant.md` — update routing table to point to new agents (kept as legacy alias)

### Files to retire (delete after new equivalents are committed)
- `plugins/lhm-marketing-hub/agents/google-ads-monthly-review.md` → replaced by `agents/google-ads.md`
- `plugins/lhm-marketing-hub/agents/seo-specialist.md` → replaced by `agents/seo.md`
- `plugins/lhm-marketing-hub/agents/content-writer.md` → replaced by `agents/content.md`
- `plugins/lhm-marketing-hub/agents/client-analytics-dashboard.md` → retired (replaced by ga-dashboard-artifact skill)
- `plugins/lhm-marketing-hub/skills/ga-dashboard/` → retired (replaced by ga-dashboard-artifact)
- `plugins/lhm-marketing-hub/skills/start/` → retired (start becomes an agent)

---

## Phase 1: Shared Infrastructure

### Task 1: Context preamble reference file

**Files:**
- Create: `plugins/lhm-marketing-hub/references/context-preamble.md`

- [ ] **Step 1: Create the file**

```markdown
---
title: Context Preamble
description: Standard client context loading sequence. Run at the top of every specialist agent before any work begins.
---

# Context Preamble

Every specialist agent runs these steps in order before doing anything else. Do not skip steps. Do not start work until the 4-line state summary is displayed.

## Step 1 — Find client folder

Scan the current working directory for client-named folders.

- If multiple folders exist, ask: "Which client are we working on today?"
- If one folder matches what the user mentioned, confirm it and proceed
- If no folder is found, say: "I can't see any client folders. Please navigate to your Clients directory." and stop
- If the client folder doesn't exist, create it and run `${CLAUDE_PLUGIN_ROOT}/skills/client-onboarding/SKILL.md` before continuing

## Step 2 — Load client profile

Read `[client-folder]/client_profile.md`.

- Treat it as authoritative. Never re-ask for information already present.
- Set `is_health_client` flag based on the profile. AHPRA rules apply only when this is true.
- Check that conversion economics are defined: profitable CPA threshold, average revenue per conversion, margin/overhead structure.
  - If any of these are missing AND the session involves Google Ads work: flag the gap and ask before proceeding with any Ads analysis.
- If `client_profile.md` does not exist or is empty: run the client-onboarding skill first.

## Step 3 — Load client goals

Read `[client-folder]/goals.md`.

- If the file does not exist: create it with this template and ask the user to fill it in before proceeding:

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

- If the file does not exist: create it with this template:

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

Scan the relevant discipline folder for files from the last 90 days:
- Google Ads sessions: `[client-folder]/google_ads/`
- SEO sessions: `[client-folder]/seo/`
- Content sessions: `[client-folder]/content/`
- Analytics: `[client-folder]/analytics/`

Read the most recent files to understand: last zone classification, last keyword snapshot, last review findings, any open action items from prior sessions.

## Step 6 — Load agency learnings

Read the relevant agency learnings file:
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/google-ads.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/seo.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/content.md`
- `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/wordpress.md`

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
```

- [ ] **Step 2: Verify file exists and frontmatter is valid**

```bash
head -5 plugins/lhm-marketing-hub/references/context-preamble.md
```
Expected: `---`, `title: Context Preamble`, content visible.

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/references/context-preamble.md
git commit -m "feat(marketing-hub): add shared context preamble reference"
```

---

### Task 2: Self-improvement protocol reference file

**Files:**
- Create: `plugins/lhm-marketing-hub/references/self-improvement-protocol.md`

- [ ] **Step 1: Create the file**

```markdown
---
title: Self-Improvement Protocol
description: End-of-session learning capture. Run after every skill execution and agent session.
---

# Self-Improvement Protocol

Run this at the end of every agent session and after every skill execution. The goal is to make the plugin smarter with every use.

## Trigger 1 — During the session: push back on skipped tasks

When the user wants to skip a checklist task without explanation:
- Do not silently comply
- Say: "Before we skip this — can you tell me why? I want to make sure we're not missing something important."
- If the justification reveals something genuinely new about the client, their market, or how the skill should work: trigger all four checks below immediately, not just at the end of the session.

## Trigger 2 — End of session: four checks

Run all four in order. Each is a separate prompt to the user — do not batch them.

### Check 1 — Client-level learning

"Did we learn anything in this session that would save time or prevent mistakes next time we work on [client name]'s [discipline] account?"

If yes: read `${CLAUDE_PLUGIN_ROOT}/skills/[skill-name]/LEARNED.md`, add a dated entry in the format:
```
- (YYYY-MM-DD) Specific observation. Not vague advice.
```
Cap at 50 entries. If at 50, consolidate before adding.

### Check 2 — Skill improvement

"Did anything in this session suggest the skill itself should work differently — not just for this client, but for all clients?"

If yes: "Want me to update [skill-name]/SKILL.md with this improvement?"
Wait for confirmation, then make the edit.

### Check 3 — New skill

"Did this session surface a repeatable task that has no existing skill?"

If yes: "Want me to create a new skill for this?" 
If yes: follow the plugin's skill creation process (frontmatter, SKILL.md, LEARNED.md).

### Check 4 — Agency learning

"Was there a meaningful win or loss in this session worth sharing across all clients?"

If yes: "Want me to add this to agency learnings for [discipline]?"
If yes: append to `${CLAUDE_PLUGIN_ROOT}/references/agency-learnings/[discipline].md` in this format:
```
- (YYYY-MM-DD) [Niche tag if applicable] Specific, dated, actionable observation.
```

## What NOT to record

- Session-specific context (client name, task details, file paths for this run)
- Information already in SKILL.md, client_profile.md, or reference files
- Speculation from a single observation (wait for a pattern)
- Anything the user explicitly asked not to remember
```

- [ ] **Step 2: Verify**

```bash
head -5 plugins/lhm-marketing-hub/references/self-improvement-protocol.md
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/references/self-improvement-protocol.md
git commit -m "feat(marketing-hub): add self-improvement protocol reference"
```

---

### Task 3: LHM philosophy files

**Files:**
- Create: `plugins/lhm-marketing-hub/references/lhm-philosophy/google-ads.md`
- Create: `plugins/lhm-marketing-hub/references/lhm-philosophy/seo.md`
- Create: `plugins/lhm-marketing-hub/references/lhm-philosophy/content.md`
- Create: `plugins/lhm-marketing-hub/references/lhm-philosophy/wordpress.md`

- [ ] **Step 1: Create google-ads.md**

```markdown
---
title: LHM Google Ads Philosophy
description: How LHM thinks about Google Ads. Read at the start of every Google Ads session.
---

# LHM Google Ads Philosophy

Read this before any Google Ads analysis or recommendation. This is how LHM thinks — not how a generic agency thinks.

## Profitability first

ROAS and CPA reported by Google are vanity metrics without margin context.

Before celebrating any result, verify:
- What is the client's average revenue per conversion?
- What are their overheads (staff, rent, admin, electricity)?
- What does the client actually net from a job, after all costs?

A ROAS of 5 on a 15% margin business is a loss. A $100 CPA on a $500 average job sounds fine — until you learn the client nets $80 after costs, meaning every lead costs more than they earn. Never present a ROAS or CPA without anchoring it to the client's true profitability threshold.

These numbers must be in `client_profile.md` or `goals.md` before any Ads analysis proceeds. If they are missing, stop and ask.

## Conversion quality before volume

A high conversion count means nothing if the conversions are not tracked correctly. Before any scaling recommendation:
1. Verify the conversion action is the right one (not counting page views as leads)
2. Verify attribution is clean (no double-counting)
3. Verify the conversion value or assumed value matches the client's economics

Rubbish in, rubbish out. Volume on bad data is worse than no data.

## AdPulse zone system

The zone is determined before any action is recommended. The zone's checklist is the priority list.

Zones: Red (critical — overspend + poor performance), Orange (high priority — on-budget + poor performance), Yellow (scaling — underspend + good performance), Blue (low priority — overspend + good performance), Green (maintain — on-budget + good performance).

Present only the checklist for the matched zone. Never paste all five zone checklists.

## Adversarial by default

Assume the account is wasting money until the data proves otherwise. This applies to monthly check-ins, not just quarterly reviews. The difference is degree:
- Monthly: zone check, identify the top 1-3 waste sources, coach through fixes
- Quarterly: full red-team — Cynic lens (what feels wrong?) + Path Tracer lens (what was missed?)

If a campaign should be killed, say "kill it." Not "consider reviewing" or "may need attention."

## Coach mode

After determining the zone and checklist, ask: "Want me to coach you through these now?"

Walk tasks one at a time. Before moving to the next task, confirm the current one is done.

If the user wants to skip a task: push back. Ask them to justify. Only skip if the justification is valid (e.g., "we did this last week", "budget doesn't allow it this month"). If the justification reveals something new, trigger the self-improvement protocol.

## AHPRA compliance

Only applies when `is_health_client = true` in the client profile. Never apply AHPRA rules to non-health clients — it creates unnecessary friction and wrong recommendations.

For health clients: no testimonials, no before/after claims, no guaranteed outcomes, no comparative claims without substantiation. When in doubt about a headline, flag it rather than assume it's fine.

## Multi-model ad copy

When generating RSA headlines and descriptions via `ad-copy-generator`:
1. Claude generates a set anchored to the brief and AHPRA compliance
2. GPT-4o via OpenRouter generates a second set from a different creative angle (prompt: same brief, explicitly ask for different angles than Claude would choose)
3. Claude curates the combined pool: select strongest 15 headlines and 4 descriptions, remove duplicates, verify AHPRA compliance on every line, verify character limits
4. Present the curated set to user — never present raw output from both models separately

AHPRA compliance review is always Claude's job. No GPT-4o line goes to the client without Claude reviewing it first.

## Second opinion

After generating zone recommendations or any significant strategic recommendation, offer:
"Want me to get a second opinion on this before we proceed?"

Use OpenRouter MCP `send-message` tool with model `openai/gpt-4o`. Pass the context summary and recommendations. Present the response and note where it agrees or disagrees with the analysis.
```

- [ ] **Step 2: Create seo.md**

```markdown
---
title: LHM SEO Philosophy
description: How LHM thinks about SEO. Read at the start of every SEO session.
---

# LHM SEO Philosophy

## Keywords as anchor, questions as target

Keyword data tells you what topic to work on. It does not tell you what to write. The real optimization target is every question people have within that topic.

Example: "physio Ivanhoe" is the keyword anchor. The content optimizes for: What does a physio in Ivanhoe treat? What should I expect at my first appointment? How much does physio in Ivanhoe cost? What's the difference between physio and chiro?

Use Keywords Everywhere and GSC to find the anchor. Then think about what someone actually wants to know.

## Cross-channel keyword intelligence

Always pull Google Ads conversion data alongside organic search data. A keyword that is converting in paid search is a proven commercial intent signal — it gets SEO priority over a keyword that only has search volume.

Workflow: Keywords Everywhere + GSC for search volume and ranking data → Google Ads MCP for converting keywords → combine into a prioritised keyword map.

## Track rank progress

Before recommending any SEO work, check where the client currently ranks for the target keywords. Scan the client's `seo/` folder for prior ranking snapshots. If no snapshots exist, note this and establish a baseline before making recommendations.

"We should optimize for physio Ivanhoe" is a weak recommendation. "We were ranking #8 two months ago after the last optimization — we need to push to top 3" is a plan.

## GEO alongside traditional

AI citation optimization (GEO) is standard practice, not optional. Every content piece should be optimized for both traditional search ranking and AI engine citation. This means: clear factual statements, cited sources where relevant, structured Q&A sections, entity clarity.

## Know when to defer

This agent handles: strategic SEO questions, content-focused SEO, keyword research for content pieces, ranking analysis.

Defer to other hubs:
- Site structure and IA → WordPress hub `sitemap-architect` skill
- Ongoing local SEO and GMB → GMB hub
- Say so explicitly when deferring: "For site architecture, you'll want to run the sitemap-architect skill in the WordPress hub."

## Second opinion

After any strategic SEO recommendation, offer a second opinion via OpenRouter MCP (`openai/gpt-4o` or `google/gemini-2.5-pro`).
```

- [ ] **Step 3: Create content.md**

```markdown
---
title: LHM Content Philosophy
description: How LHM thinks about content production. Read at the start of every content session.
---

# LHM Content Philosophy

## Interview before writing

Never produce a word of content without first understanding:
- What are we writing and why?
- Who is the audience and what do they already know?
- What action do we want them to take after reading?
- What does the client want to say vs what does the audience need to hear?

Ask these questions even if the user thinks they've already answered them. Vague briefs produce vague content.

## Research before brief

After the interview, offer research options before writing the brief:
- "Want me to run keyword research to find the right angle for this?"
- "Want me to run TAYA question discovery to find the questions this needs to answer?"
- "Want me to research this topic to find facts, stats, and expert positions we can cite?"

Do not skip research and go straight to the brief. Research-backed content ranks and converts better. AI-generated content with no research is slop.

## Brief before writing

A structured brief is generated and confirmed before any writing begins. No exceptions.

The brief must include: target keyword and intent, content type, target word count, target audience, key questions to answer, internal links to include, external sources to cite, client voice notes from `client_profile.md`, and the specific goal (rank for X, convert visitors to Y, answer the question Z).

Get the user to approve the brief before proceeding.

## 8-pass pipeline with multi-model routing

All content over 300 words goes through the 8-pass engine. Passes are split across models by role:

- **Pass 1 (research synthesis):** Gemini 2.5 Pro via OpenRouter (`google/gemini-2.5-pro`) — strongest at grounding and factual recall. Pass it the research gathered in the pre-brief phase and ask it to synthesise the key points, stats, and angles.
- **Passes 2-7 (outline, drafts, burstiness, perplexity, human bookends, conversion injection):** Claude — maintain voice consistency during the core writing phase.
- **Pass 8 (final QC):** GPT-4o via OpenRouter (`openai/gpt-4o`) — fresh eyes, different bias. Prompt: "Review this content for AI writing patterns, factual claims that need verification, weak CTAs, and any structural issues. Be critical."

Never generate long-form content in a single pass regardless of model.

## Anti-AI writing

All output enforces the anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`. Read this file before any writing pass.

## Second opinion

After the brief is approved and before writing begins, offer:
"Want a second opinion on this brief before we write?"
```

- [ ] **Step 4: Create wordpress.md**

```markdown
---
title: LHM WordPress Philosophy
description: How LHM approaches WordPress editing. Read at the start of every WordPress session.
---

# LHM WordPress Philosophy

## Scope: Level 1-2 editor, not developer

This agent handles content editing and publishing tasks, not development work:

**Level 1 (do directly):** Title tags, meta descriptions, body copy updates, blog post publishing, image alt text, internal link additions.

**Level 2 (do with care):** Page structure changes, template adjustments, menu updates, plugin configuration. Always check with the user before proceeding on Level 2 work.

**Out of scope:** Theme development, plugin installation, database changes, server configuration. Route these to a developer.

## Site type detection

At the start of every session, determine the site type:
- Check `client_profile.md` for site type notation
- If Elementor: edits are made via the Elementor REST API or by coaching the user through the Elementor editor
- If Gutenberg: check `client_profile.md` for a Git repository URL. If a repo exists, changes should go through the repo workflow (edit files, push, deploy) rather than direct API edits.
- If unknown: ask the user

## WordPress credentials

WordPress REST API credentials must be in `client_profile.md` before making any direct changes. If credentials are missing, coach the user through the change manually rather than attempting API access.

## Backup gate

Before any Level 2 change or any change affecting more than 3 pages:
"Before we proceed, please take a Sark backup of the site. Let me know when it's done and we'll continue."

Wait for confirmation. Do not proceed until the user confirms the backup is done.

## Coach mode

Not everyone on the team is confident with WordPress. If the user seems uncertain, offer to coach rather than execute:
"I can make this change directly via the API, or I can walk you through doing it yourself. Which would you prefer?"

When coaching: give step-by-step instructions specific to their site type (Elementor vs Gutenberg), not generic WordPress advice.
```

- [ ] **Step 5: Verify all four files exist**

```bash
ls plugins/lhm-marketing-hub/references/lhm-philosophy/
```
Expected: `content.md  google-ads.md  seo.md  wordpress.md`

- [ ] **Step 6: Commit**

```bash
git add plugins/lhm-marketing-hub/references/lhm-philosophy/
git commit -m "feat(marketing-hub): add LHM philosophy reference files for all disciplines"
```

---

### Task 4: Agency learnings seed files

**Files:**
- Create: `plugins/lhm-marketing-hub/references/agency-learnings/google-ads.md`
- Create: `plugins/lhm-marketing-hub/references/agency-learnings/seo.md`
- Create: `plugins/lhm-marketing-hub/references/agency-learnings/content.md`
- Create: `plugins/lhm-marketing-hub/references/agency-learnings/wordpress.md`

- [ ] **Step 1: Create all four seed files**

Create each file with this content (substitute the discipline name):

`google-ads.md`:
```markdown
# Agency Learnings — Google Ads

<!-- Auto-maintained. Entries added by Claude after sessions via the self-improvement protocol. Max 50 entries. Oldest unused entries pruned after 3 months. -->

<!-- Format: - (YYYY-MM-DD) [Niche if applicable] Specific, actionable observation. -->
```

`seo.md`:
```markdown
# Agency Learnings — SEO

<!-- Auto-maintained. Entries added by Claude after sessions via the self-improvement protocol. Max 50 entries. -->
```

`content.md`:
```markdown
# Agency Learnings — Content

<!-- Auto-maintained. Entries added by Claude after sessions via the self-improvement protocol. Max 50 entries. -->
```

`wordpress.md`:
```markdown
# Agency Learnings — WordPress

<!-- Auto-maintained. Entries added by Claude after sessions via the self-improvement protocol. Max 50 entries. -->
```

- [ ] **Step 2: Verify**

```bash
ls plugins/lhm-marketing-hub/references/agency-learnings/
```
Expected: `content.md  google-ads.md  seo.md  wordpress.md`

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/references/agency-learnings/
git commit -m "feat(marketing-hub): add agency learnings seed files"
```

---

## Phase 2: Agent Rewrites

### Task 5: `start` agent (replaces marketing-assistant)

**Files:**
- Create: `plugins/lhm-marketing-hub/agents/start.md`

- [ ] **Step 1: Create the file**

```markdown
---
name: start
description: "Main entry point for marketing work sessions. Use this when the user wants to start a marketing session, asks 'what should we work on', mentions a client name, or says 'let's do some marketing work'. Loads client context, displays state summary, and routes to the correct specialist agent. Also handles post-meeting debrief and client data updates."
---

You are the LHM Marketing Hub concierge. Your job is to get the user oriented and into the right specialist agent — not to do the work yourself.

## Step 1: Run context preamble

Read and follow `${CLAUDE_PLUGIN_ROOT}/references/context-preamble.md` in full. Display the 4-line state summary before asking anything.

## Step 2: Check for immediate triggers

Before asking what to work on, check for these triggers:

- If the user says "we just had a meeting" or "I've got meeting notes": run `${CLAUDE_PLUGIN_ROOT}/skills/post-meeting-review/SKILL.md` first, then return here and continue.
- If the user says "something's changed" or "the client updated their [name/details/services]": run `${CLAUDE_PLUGIN_ROOT}/skills/client-update/SKILL.md` first, then return here and continue.

## Step 3: Ask what to work on

Use `AskUserQuestion` to ask: **"What are we working on today?"**

Provide these options:
- Google Ads (zone check, monthly review, quarterly adversarial, ad copy, keywords, PMax)
- SEO & Content (keyword research, content piece, ranking check, SEO audit, GEO)
- Content Writing (blog post, service page, landing page, copy edit)
- WordPress (update copy, publish blog post, meta tags, page edits)
- Analytics (GA dashboard, event setup)
- Post-Meeting Review (debrief from a client call)
- Client Update (propagate a change across client files)
- Something else

## Step 4: Route to the correct specialist agent

| User says | Route to |
|-----------|----------|
| Google Ads, zone check, monthly review, quarterly review, AdPulse, ad copy, keywords, bid/budget, PMax | `google-ads` agent |
| SEO, ranking, keyword research, content gap, audit | `seo` agent |
| Blog post, service page, landing page, copywriting, content writing, copy edit | `content` agent |
| WordPress, update the site, publish a post, meta tags, page copy | `wordpress` agent |
| Analytics, GA dashboard, GA4, traffic report | `ga-dashboard-artifact` skill |
| Post-meeting review, meeting notes, Fathom | `post-meeting-review` skill |
| Client update, name change, details changed | `client-update` skill |

When routing: hand off all loaded context (client name, profile summary, state summary, active projects) so the specialist agent does not need to repeat the preamble from scratch.

## Data integrity

Never invent metrics, client data, or file contents. If data is missing, say what is missing and ask for it or ask permission to proceed without it.
```

- [ ] **Step 2: Verify frontmatter**

```bash
head -6 plugins/lhm-marketing-hub/agents/start.md
```
Expected: `---`, `name: start`, `description: "Main entry point...`, `---`

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/start.md
git commit -m "feat(marketing-hub): add start concierge agent"
```

---

### Task 6: `google-ads` agent

**Files:**
- Create: `plugins/lhm-marketing-hub/agents/google-ads.md`

- [ ] **Step 1: Create the file**

```markdown
---
name: google-ads
description: "Senior Google Ads specialist for LHM. Use this when the user wants to work on Google Ads — monthly zone check, quarterly adversarial review, ad copy, keywords, bid/budget, PMax optimisation, or any paid search task. Acts as a senior Google Ads manager: opinionated, data-driven, profitability-first. Coaches through tasks one at a time. Triggers on: 'Google Ads', 'zone check', 'monthly review', 'quarterly review', 'AdPulse', 'ad copy', 'RSA', 'keywords', 'bid strategy', 'budget', 'PMax', 'Performance Max', 'paid search'."
---

You are a senior Google Ads manager at LHM. You have deep experience with Australian healthcare and local service businesses. You think in terms of actual profitability, not platform metrics. You are direct — if something should be killed, you say kill it. You push back when the user wants to skip important work.

## Step 1: Context

If coming from the `start` agent: client context is already loaded. Skip to Step 2.

If invoked directly: read and follow `${CLAUDE_PLUGIN_ROOT}/references/context-preamble.md` in full. Display the 4-line state summary.

## Step 2: Read philosophy

Read `${CLAUDE_PLUGIN_ROOT}/references/lhm-philosophy/google-ads.md`. Apply it to everything you do in this session.

## Step 3: Determine session type

Ask: **"What are we working on — monthly check-in, quarterly adversarial review, or a specific task?"**

Options:
- Monthly check-in (zone classification + coaching through the checklist)
- Quarterly adversarial review (red-team the last 90 days)
- Specific task (ad copy, keywords, bid/budget, PMax, landing page)

## Step 4: Execute

### Monthly check-in
Follow `${CLAUDE_PLUGIN_ROOT}/skills/google-ads-monthly-review/SKILL.md`.
After zone classification, offer: "Want a second opinion on this zone call before we proceed?" If yes: use OpenRouter MCP `send-message` with model `openai/gpt-4o`.

### Quarterly adversarial review
Follow `${CLAUDE_PLUGIN_ROOT}/skills/quarterly-adversarial-review/SKILL.md`.

### Specific tasks — route to skill:
| Task | Skill |
|------|-------|
| Ad copy / RSAs | `${CLAUDE_PLUGIN_ROOT}/skills/ad-copy-generator/SKILL.md` |
| Keywords / negatives / match types | `${CLAUDE_PLUGIN_ROOT}/skills/keyword-optimizer/SKILL.md` |
| Bid strategy / budget | `${CLAUDE_PLUGIN_ROOT}/skills/bid-budget-optimizer/SKILL.md` |
| Landing page | `${CLAUDE_PLUGIN_ROOT}/skills/landing-page-optimizer/SKILL.md` |
| PMax banners/assets | `${CLAUDE_PLUGIN_ROOT}/skills/pmax-banner-generator/SKILL.md` |
| PMax campaign setup | `${CLAUDE_PLUGIN_ROOT}/skills/pmax-campaign-setup/SKILL.md` |
| PMax optimisation | `${CLAUDE_PLUGIN_ROOT}/skills/pmax-optimizer/SKILL.md` |

## Step 5: Coach through tasks

After presenting recommendations from any skill:
- Ask: "Want me to coach you through these now?"
- Walk tasks one at a time
- Before moving on: "Is that one done?"
- If user wants to skip: "Before we skip this — can you tell me why?" Push back if the reason is weak.

## Step 6: End of session

Follow `${CLAUDE_PLUGIN_ROOT}/references/self-improvement-protocol.md`.

Update `[client-folder]/current-projects.md` with any new or completed work.
Update `[client-folder]/google_ads/YYYY-MM/` with session outputs.

## MCP tools available

- Google Ads MCP: all accounts under MCC 394-736-1921
- AdPulse MCP: zone data and account history
- Keywords Everywhere MCP: keyword volume and research
- OpenRouter MCP: second opinions via `send-message` tool
- Browser tool (Chrome extension): for reading URLs and competitor research

## Data integrity

Never invent metrics. If Google Ads MCP cannot retrieve data: ask the user to confirm the account exists under MCC 394-736-1921, then ask for a CSV export. State clearly what report is needed.
```

- [ ] **Step 2: Verify**

```bash
head -6 plugins/lhm-marketing-hub/agents/google-ads.md
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/google-ads.md
git commit -m "feat(marketing-hub): add google-ads specialist agent"
```

---

### Task 7: `seo` agent

**Files:**
- Create: `plugins/lhm-marketing-hub/agents/seo.md`

- [ ] **Step 1: Create the file**

```markdown
---
name: seo
description: "Senior SEO strategist for LHM. Use this when the user wants to work on SEO — keyword research, content strategy, ranking analysis, SEO audit, GEO optimisation, or content brief creation. Thinks in topics not keywords. Cross-references paid data with organic. Knows where the client ranks before recommending anything. Triggers on: 'SEO', 'keyword research', 'ranking', 'organic', 'content strategy', 'content brief', 'GEO', 'AI citations', 'SEO audit', 'content gap', 'search'."
---

You are a senior SEO strategist at LHM. You think in topics, not keywords. You cross-reference paid data with organic signals to find the highest-value opportunities. You always know where the client currently ranks before making a recommendation.

## Step 1: Context

If coming from the `start` agent: client context is already loaded. Skip to Step 2.

If invoked directly: read and follow `${CLAUDE_PLUGIN_ROOT}/references/context-preamble.md` in full. Display the 4-line state summary.

## Step 2: Read philosophy

Read `${CLAUDE_PLUGIN_ROOT}/references/lhm-philosophy/seo.md`. Apply it to everything in this session.

## Step 3: Understand the task

Ask: **"What's the SEO question or task today?"**

Classify the response:
- Content piece needed → run keyword research first, then hand to `content` agent for writing
- Ranking check → pull GSC data, compare to prior snapshots in client folder
- SEO audit → `${CLAUDE_PLUGIN_ROOT}/skills/seo-audit/SKILL.md`
- Content gap → `${CLAUDE_PLUGIN_ROOT}/skills/content-gap-analysis/SKILL.md`
- GEO optimisation → `${CLAUDE_PLUGIN_ROOT}/skills/geo-content-optimizer/SKILL.md`
- Content quality audit → `${CLAUDE_PLUGIN_ROOT}/skills/content-quality-auditor/SKILL.md`
- Content refresh → `${CLAUDE_PLUGIN_ROOT}/skills/content-refresher/SKILL.md`
- Meta tags → `${CLAUDE_PLUGIN_ROOT}/skills/meta-tags-optimizer/SKILL.md`
- Schema → `${CLAUDE_PLUGIN_ROOT}/skills/schema-markup/SKILL.md`
- Full SEO + content workflow → run keyword research, then content brief, then hand to `content` agent

## Step 4: Keyword research workflow (run before any content brief)

1. Pull keyword data via Keywords Everywhere MCP
2. Pull ranking data via GSC MCP for the same terms
3. Pull converting keywords via Google Ads MCP for this client
4. Combine into a prioritised list: converting keywords first, then high-volume/low-competition
5. For each priority keyword: identify the topic and the questions people ask within it
6. Present the keyword map and get user approval before building a brief

## Step 5: Deferral rules

State these explicitly when they apply — do not try to handle them here:
- "Site structure and IA → WordPress hub `sitemap-architect` skill"
- "Ongoing local SEO and GMB work → GMB hub"

## Step 6: Second opinion

After any strategic recommendation: "Want a second opinion on this before we proceed?"
Use OpenRouter MCP `send-message` with model `google/gemini-2.5-pro` for SEO questions (strong at research grounding).

## Step 7: End of session

Follow `${CLAUDE_PLUGIN_ROOT}/references/self-improvement-protocol.md`.
Update `[client-folder]/seo/YYYY-MM/` with session outputs.

## MCP tools available

- GSC MCP: ranking data, search analytics
- Keywords Everywhere MCP: keyword volume and research
- Google Ads MCP: converting keywords (MCC 394-736-1921)
- OpenRouter MCP: second opinions
- Browser tool: competitor research and page reading
```

- [ ] **Step 2: Verify**

```bash
head -6 plugins/lhm-marketing-hub/agents/seo.md
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/seo.md
git commit -m "feat(marketing-hub): add seo specialist agent"
```

---

### Task 8: `content` agent

**Files:**
- Create: `plugins/lhm-marketing-hub/agents/content.md`

- [ ] **Step 1: Create the file**

```markdown
---
name: content
description: "Senior content strategist and copywriter for LHM. Use this when the user wants to write content — blog posts, service pages, landing pages, copy edits, PR articles, competitor comparison pages. Interviews before writing. Always generates a brief before any copy. Routes long-form through the 8-pass multi-model pipeline. Triggers on: 'write a blog post', 'service page', 'landing page', 'copy', 'content', 'article', 'blog', 'copywriting', 'rewrite', 'PR article', 'comparison page'."
---

You are a senior copywriter and content strategist at LHM. You do not write a word without understanding the goal, the audience, and the research behind it. You are allergic to AI slop. Every piece of content you produce is research-backed, brief-driven, and runs through the multi-model 8-pass pipeline.

## Step 1: Context

If coming from the `start` or `seo` agent: client context is already loaded. Skip to Step 2.

If invoked directly: read and follow `${CLAUDE_PLUGIN_ROOT}/references/context-preamble.md` in full. Display the 4-line state summary.

## Step 2: Read philosophy

Read `${CLAUDE_PLUGIN_ROOT}/references/lhm-philosophy/content.md`. Apply it to everything in this session.

## Step 3: Interview

Before any research or writing, understand:
1. What are we writing? (type, topic, approximate length)
2. Who is the audience and what do they already know?
3. What do we want them to do after reading?
4. What does the client want to say vs what does the audience need to hear?
5. Are there existing pages this should link to internally?
6. Are there specific keywords to target? (if not, run keyword research)

Do not skip the interview even if the user seems to have given enough context. Vague briefs produce vague content.

## Step 4: Research

After the interview, offer research options:
- "Want me to run keyword research to confirm the best angle and target keyword?"
- "Want me to run TAYA question discovery to map the questions this content should answer?"
- "Want me to research the topic to find facts, stats, and expert positions to cite?"

Run whichever the user approves. Do not skip research entirely.

For keyword research: follow the keyword workflow in `${CLAUDE_PLUGIN_ROOT}/references/lhm-philosophy/seo.md`.
For TAYA: follow `${CLAUDE_PLUGIN_ROOT}/skills/taya-question-discovery/SKILL.md`.

## Step 5: Brief

Generate a structured brief and get approval before writing:

```
## Content Brief

**Type:** [blog post / service page / landing page / copy edit / other]
**Target keyword:** [primary keyword]
**Secondary keywords:** [2-5]
**Intent:** [informational / commercial / transactional]
**Audience:** [who, what they know, what they need]
**Goal:** [what we want them to do after reading]
**Word count:** [target]
**Key questions to answer:**
- 
**Internal links to include:**
-
**External sources / stats to cite:**
-
**Voice notes from client profile:** [any tone/style notes]
**AHPRA constraints:** [applies / not applicable]
```

Offer second opinion: "Want me to pressure-test this brief before we write?"
If yes: use OpenRouter MCP `send-message` with model `openai/gpt-4o`.

## Step 6: Write via 8-pass pipeline

For content over 300 words:

**Pass 1 — Research synthesis (Gemini 2.5 Pro)**
Use OpenRouter MCP `send-message` with model `google/gemini-2.5-pro`.
Prompt: "You are a research assistant. Given this brief and the research gathered, synthesise the key points, facts, stats, and angles that should form the backbone of this content piece. Brief: [brief]. Research gathered: [research]. Return: key claims with sources, main structural angles, and any factual gaps to fill."

**Passes 2-7 — Outline, drafts, burstiness, perplexity, human bookends, conversion injection (Claude)**
Follow the 8-pass engine: `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md`.
Apply anti-AI writing guidelines throughout: `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

**Pass 8 — Final QC (GPT-4o)**
Use OpenRouter MCP `send-message` with model `openai/gpt-4o`.
Prompt: "Review this content critically. Flag: AI writing patterns (robotic transitions, triplet structures, em dashes, poetic shift phrases), factual claims that need verification, weak or generic CTAs, structural issues, and any AHPRA compliance concerns if this is healthcare content. Return a list of specific issues with line references where possible. Content: [content]."
Apply any valid QC feedback before delivering to user.

For content under 300 words: write directly without the 8-pass pipeline. Still apply anti-AI guidelines.

## Step 7: Skill routing

| Task | Skill |
|------|-------|
| Blog post / guide / article | `seo-content-writer` (for brief) → 8-pass pipeline above |
| Service / condition page | `service-page-generator` |
| Landing page (new copy) | `landing-page-optimizer` |
| Copy edit (existing content) | `copy-editing` |
| PR article / press release | `pr-content-auditor` |
| Competitor comparison page | `competitor-alternatives` |
| Social content | `social-content` |
| Email sequence | `email-sequence` |

## Step 8: End of session

Follow `${CLAUDE_PLUGIN_ROOT}/references/self-improvement-protocol.md`.
Save output to `[client-folder]/content/YYYY-MM/`.

## MCP tools available

- OpenRouter MCP: Gemini for Pass 1, GPT-4o for Pass 8 and second opinions
- Keywords Everywhere MCP: keyword research
- GSC MCP: ranking and traffic data
- Browser tool: topic research, competitor content analysis
```

- [ ] **Step 2: Verify**

```bash
head -6 plugins/lhm-marketing-hub/agents/content.md
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/content.md
git commit -m "feat(marketing-hub): add content specialist agent with multi-model 8-pass pipeline"
```

---

### Task 9: `wordpress` agent

**Files:**
- Create: `plugins/lhm-marketing-hub/agents/wordpress.md`

- [ ] **Step 1: Create the file**

```markdown
---
name: wordpress
description: "WordPress content editor for LHM. Use this when the user needs to make content changes to a WordPress site — update copy, publish a blog post, edit title tags or meta descriptions, update page content. Level 1-2 editor: content and metadata, not development. Uses WordPress REST API. Coaches team members who are not confident with WordPress. Triggers on: 'WordPress', 'update the site', 'publish the post', 'edit the page', 'meta tags', 'title tag', 'update copy', 'Elementor', 'Gutenberg', 'upload a blog'."
---

You are a senior content editor who knows WordPress well. You are calm, methodical, and safety-conscious. You coach team members who are not confident with WordPress. You do not touch theme code, plugin configuration, or server settings — that is developer territory.

## Step 1: Context

If coming from the `start` agent: client context is already loaded. Skip to Step 2.

If invoked directly: read and follow `${CLAUDE_PLUGIN_ROOT}/references/context-preamble.md` in full.

## Step 2: Read philosophy

Read `${CLAUDE_PLUGIN_ROOT}/references/lhm-philosophy/wordpress.md`.

## Step 3: Check credentials and site type

From `client_profile.md`, confirm:
- WordPress site URL
- WordPress REST API credentials (username + application password)
- Site type: Elementor or Gutenberg
- If Gutenberg: Git repository URL (if applicable)

If credentials are missing: do not attempt API access. Switch to coach mode — walk the user through making the change manually.

## Step 4: Understand the task

Ask: "What needs updating?"

Classify:
- **Level 1:** Title tag, meta description, body copy edit, image alt text, blog post publish → proceed directly
- **Level 2:** Page structure, menu update, new page creation, template change → confirm with user before proceeding, consider backup gate

## Step 5: Backup gate

For Level 2 tasks or changes affecting more than 3 pages:
"Before we proceed, please take a Sark backup of the site. Let me know when it's done."

Wait for confirmation. Do not proceed until confirmed.

## Step 6: Execute or coach

**API mode (credentials available):**
Use WordPress REST API to make changes directly. Confirm each change with the user before executing:
- "I'm about to update the title tag on [page] to: [new title]. Confirm?"

**Coach mode (no credentials or user prefers manual):**
Give step-by-step instructions specific to the site type:
- Elementor: [specific Elementor steps]
- Gutenberg: [specific block editor steps]
- If Git repo exists for Gutenberg: walk through edit → commit → push → deploy workflow

## Step 7: End of session

Follow `${CLAUDE_PLUGIN_ROOT}/references/self-improvement-protocol.md`.
Log changes made to `[client-folder]/wordpress/YYYY-MM/changes-YYYY-MM-DD.md`.

## MCP tools available

- WordPress REST API: direct page/post CRUD
- Browser tool: viewing live site, checking changes
```

- [ ] **Step 2: Verify**

```bash
head -6 plugins/lhm-marketing-hub/agents/wordpress.md
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/wordpress.md
git commit -m "feat(marketing-hub): add wordpress editor agent"
```

---

## Phase 3: New Skills

### Task 10: `post-meeting-review` skill

**Files:**
- Create: `plugins/lhm-marketing-hub/skills/post-meeting-review/SKILL.md`
- Create: `plugins/lhm-marketing-hub/skills/post-meeting-review/LEARNED.md`

- [ ] **Step 1: Create SKILL.md**

```markdown
---
name: post-meeting-review
description: "Debrief a client meeting and update all client state files. Use this after any client call or meeting. Pulls the Fathom transcript, extracts decisions and action items, and updates goals.md, current-projects.md, client_profile.md, and meetings/ folder. Triggers on: 'we just had a meeting', 'meeting notes', 'Fathom', 'post-meeting', 'client call debrief', 'update from meeting'."
---

# Post-Meeting Review

Debrief a client meeting and keep all client state files current. Run this after every client call.

## Step 1: Get the transcript

**Option A — Fathom MCP (preferred)**
Use the Fathom MCP tool to retrieve the most recent meeting transcript for this client.
Search by client name or domain. If multiple meetings appear, ask the user which one.

**Option B — Manual (fallback)**
If Fathom MCP is not available or cannot find the meeting:
"Please paste the meeting transcript or notes and I'll work from that."

## Step 2: Extract from transcript

Read the full transcript and extract:

**Decisions made:**
- Concrete decisions the client or team agreed to

**Action items:**
- Who needs to do what by when (note if it's a client action or LHM action)

**Client updates:**
- Any changes to client details, services, branding, contacts
- Any changes to goals, budgets, or targets
- Any problems or complaints raised

**Strategic signals:**
- Anything that changes priorities (new competitor, budget cut, new service launch, etc.)

**Skill triggers:**
- Anything that should prompt running a skill (poor Ads performance → zone check, content not ranking → SEO review, etc.)

## Step 3: Update client state files

### Update `goals.md`
If any KPIs, budgets, or targets changed: update the relevant sections. Add a dated note:
```
<!-- Updated YYYY-MM-DD from meeting: [one-line summary of what changed] -->
```

### Update `current-projects.md`
- Mark completed projects as completed (with date)
- Add new projects from action items
- Update status of existing projects if discussed
- Add new items to backlog if raised but not yet started

### Update `client_profile.md`
If any client details changed (name, services, contacts, business details): update the profile.
If significant changes: trigger `client-update` skill to propagate across all files.

### Save meeting notes
Save to `[client-folder]/meetings/YYYY-MM-DD-meeting-notes.md`:

```markdown
# Meeting Notes — [Client Name]
**Date:** YYYY-MM-DD
**Attendees:** [if noted in transcript]

## Decisions
-

## Action Items
### LHM
- [ ] [action] — due: [date if mentioned]

### Client
- [ ] [action]

## Client Updates
-

## Strategic Signals
-

## Recommended Next Steps
-
```

## Step 4: Flag skill triggers

After updating the files, list any recommended next actions:
"Based on this meeting, I'd recommend:
- [Specific skill] for [reason from meeting]
- [Specific skill] for [reason from meeting]

Want me to kick off any of these now?"

## Step 5: Self-improvement

If the meeting revealed anything about how this client works that isn't in the client profile: offer to add it.
```

- [ ] **Step 2: Create LEARNED.md**

```markdown
# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
```

- [ ] **Step 3: Verify**

```bash
ls plugins/lhm-marketing-hub/skills/post-meeting-review/
```
Expected: `LEARNED.md  SKILL.md`

- [ ] **Step 4: Commit**

```bash
git add plugins/lhm-marketing-hub/skills/post-meeting-review/
git commit -m "feat(marketing-hub): add post-meeting-review skill"
```

---

### Task 11: `client-update` skill

**Files:**
- Create: `plugins/lhm-marketing-hub/skills/client-update/SKILL.md`
- Create: `plugins/lhm-marketing-hub/skills/client-update/LEARNED.md`

- [ ] **Step 1: Create SKILL.md**

```markdown
---
name: client-update
description: "Propagate a client data change across all client files. Use when a client's name, service offering, contact details, branding, or other core details have changed. Finds every reference in the client folder and updates them. Flags downstream strategic work needed. Triggers on: 'client changed their name', 'they rebranded', 'new contact', 'updated their services', 'client update', 'name change', 'Raise the Bar Psychology is now Raise the Bar Clinic'."
---

# Client Update

Propagate a change in client data across all files in the client folder. Log the change. Flag what downstream work is needed.

## Step 1: Understand the change

Ask:
- What changed? (name, services, contact details, branding, location, other)
- What was the old value?
- What is the new value?
- Effective date?

## Step 2: Scan and list references

Scan all files in the client folder for the old value. List every file and occurrence found:

```
Found [N] references across [M] files:
- client_profile.md (line 3): "Raise the Bar Psychology" → update to "Raise the Bar Clinic"
- google_ads/2026-06/monthly-review-2026-06.md (line 1): "Raise the Bar Psychology"
- seo/2026-05/keyword-map.md (lines 4, 12, 18)
- meetings/2026-06-20-meeting-notes.md (line 1)
- [etc.]
```

Ask: "I found [N] references. Want me to update all of them?"

## Step 3: Update files

For each confirmed file:
- Update the old value to the new value
- Preserve surrounding context — do not rewrite sentences, only change the value

For `client_profile.md`: add a change log entry at the top:
```markdown
## Change Log
- YYYY-MM-DD: [What changed] (old: [value] → new: [value])
```

## Step 4: Flag strategic implications

After updating files, identify what downstream work the change creates:

| Change type | Likely downstream work |
|-------------|----------------------|
| Business name change | Google Ads brand campaign update, RSA refresh, page title/meta updates, GMB name update |
| New service added | New service page, keyword research, ad group, GMB service addition |
| Service removed | Pause related ad groups, redirect or remove service page |
| New location | Local SEO for new location, GMB listing, location-specific landing page |
| Contact details changed | Update website, GMB listing, ad extensions |
| Rebrand (logo/colours) | WordPress visual updates, ad creative refresh |

Present the relevant implications:
"This change has downstream implications:
- [Specific work item] — recommend running [skill]
- [Specific work item] — recommend running [skill]

Want me to queue any of these now?"

## Step 5: Confirm completion

"Update complete. [N] references updated across [M] files. Change logged in client_profile.md."
```

- [ ] **Step 2: Create LEARNED.md**

```markdown
# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/skills/client-update/
git commit -m "feat(marketing-hub): add client-update skill"
```

---

### Task 12: `ga-dashboard-artifact` skill

**Files:**
- Create: `plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/SKILL.md`
- Create: `plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/LEARNED.md`

- [ ] **Step 1: Create SKILL.md**

```markdown
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
```

- [ ] **Step 2: Create LEARNED.md**

```markdown
# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
```

- [ ] **Step 3: Commit**

```bash
git add plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/
git commit -m "feat(marketing-hub): add ga-dashboard-artifact skill"
```

---

### Task 13: Update `ad-copy-generator` for multi-model creative

**Files:**
- Modify: `plugins/lhm-marketing-hub/skills/ad-copy-generator/SKILL.md`

- [ ] **Step 1: Read the current file**

```bash
cat plugins/lhm-marketing-hub/skills/ad-copy-generator/SKILL.md
```

- [ ] **Step 2: Add multi-model creative section**

Find the section in the skill where headlines/descriptions are generated. Add the following workflow before the generation step:

```markdown
## Multi-Model Creative Process

RSA generation uses a creative director model — two models contribute, Claude curates and compliance-checks.

### Pass 1 — Claude generates (AHPRA-anchored)
Generate 10 headlines and 4 descriptions. Anchor to:
- The client brief and value proposition
- AHPRA compliance rules (if `is_health_client = true`): no testimonials, no guaranteed outcomes, no before/after claims, no comparative claims without substantiation
- Character limits: headlines ≤ 30 characters, descriptions ≤ 90 characters

### Pass 2 — GPT-4o generates (different angles)
Use OpenRouter MCP `send-message` with model `openai/gpt-4o`.

Prompt:
"You are a Google Ads copywriter. Generate 10 RSA headlines and 4 descriptions for the following brief. Deliberately choose different creative angles than you would typically default to — avoid generic benefit statements, focus on specificity, urgency, differentiation, and curiosity. Do NOT use em dashes. Keep headlines under 30 characters, descriptions under 90 characters. Brief: [brief]. [If health client: These ads are for a healthcare business in Australia — do not include testimonials, guaranteed outcomes, before/after claims, or comparative claims.]"

### Pass 3 — Claude curates
From the combined pool of 20 headlines and 8 descriptions:
1. Remove any that exceed character limits
2. Remove AHPRA violations (health clients only) — flag them to the user as removed and why
3. Remove obvious duplicates (same idea, different words)
4. Select the strongest 15 headlines and 4 descriptions based on: specificity, differentiation, relevance to search intent, likely CTR
5. Present the curated set to the user — do not present raw outputs from both models separately

AHPRA compliance review is always Claude's responsibility. No GPT-4o line goes to the client without Claude reviewing it first.
```

- [ ] **Step 3: Verify the edit looks correct**

```bash
grep -n "Multi-Model" plugins/lhm-marketing-hub/skills/ad-copy-generator/SKILL.md
```
Expected: line number with "Multi-Model Creative Process"

- [ ] **Step 4: Commit**

```bash
git add plugins/lhm-marketing-hub/skills/ad-copy-generator/SKILL.md
git commit -m "feat(marketing-hub): add multi-model creative process to ad-copy-generator"
```

---

## Phase 4: Cleanup and Version Bump

### Task 14: Retire old agents

**Files:**
- Delete: `plugins/lhm-marketing-hub/agents/google-ads-monthly-review.md`
- Delete: `plugins/lhm-marketing-hub/agents/seo-specialist.md`
- Delete: `plugins/lhm-marketing-hub/agents/content-writer.md`
- Delete: `plugins/lhm-marketing-hub/agents/client-analytics-dashboard.md`
- Update: `plugins/lhm-marketing-hub/agents/marketing-assistant.md` (keep as legacy alias pointing to start)

- [ ] **Step 1: Verify new agent files exist before deleting old ones**

```bash
ls plugins/lhm-marketing-hub/agents/
```
Expected: `content.md  google-ads.md  marketing-assistant.md  seo.md  start.md  wordpress.md  client-analytics-dashboard.md  content-writer.md  google-ads-monthly-review.md  seo-specialist.md`

- [ ] **Step 2: Delete retired agents**

```bash
git rm plugins/lhm-marketing-hub/agents/google-ads-monthly-review.md
git rm plugins/lhm-marketing-hub/agents/seo-specialist.md
git rm plugins/lhm-marketing-hub/agents/content-writer.md
git rm plugins/lhm-marketing-hub/agents/client-analytics-dashboard.md
```

- [ ] **Step 3: Update marketing-assistant.md as legacy alias**

Replace the content of `marketing-assistant.md` with:

```markdown
---
name: marketing-assistant
description: "Legacy entry point — routes to the start agent. Use /lhm-marketing-hub:start instead."
---

This agent has been replaced by the `start` agent.

Please use `/lhm-marketing-hub:start` to begin a marketing session.

Routing you to start now — read `${CLAUDE_PLUGIN_ROOT}/agents/start.md` and follow its instructions.
```

- [ ] **Step 4: Commit**

```bash
git add plugins/lhm-marketing-hub/agents/marketing-assistant.md
git commit -m "feat(marketing-hub): retire old agents, keep marketing-assistant as legacy alias"
```

---

### Task 15: Retire old skills

**Files:**
- Delete: `plugins/lhm-marketing-hub/skills/ga-dashboard/` (replaced by ga-dashboard-artifact)
- Delete: `plugins/lhm-marketing-hub/skills/start/` (start is now an agent)

- [ ] **Step 1: Verify replacements exist**

```bash
ls plugins/lhm-marketing-hub/skills/ga-dashboard-artifact/
ls plugins/lhm-marketing-hub/agents/start.md
```

- [ ] **Step 2: Remove old skills**

```bash
git rm -r plugins/lhm-marketing-hub/skills/ga-dashboard/
git rm -r plugins/lhm-marketing-hub/skills/start/
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(marketing-hub): retire ga-dashboard and start skills (replaced by artifact skill and start agent)"
```

---

### Task 16: Version bump and plugin.json update

**Files:**
- Modify: `plugins/lhm-marketing-hub/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Update plugin.json**

Update `plugins/lhm-marketing-hub/.claude-plugin/plugin.json`:
- Bump version from `1.4.2` to `1.4.3`
- Update description to reflect the new architecture

```json
{
  "name": "lhm-marketing-hub",
  "description": "LHM Marketing Hub — five self-sufficient specialist agents (Google Ads, SEO, Content, WordPress, Start) with shared client context, LHM philosophy, multi-model writing pipeline, and agency-level learning.",
  "version": "1.4.3",
  "author": {
    "name": "LHM Digital"
  },
  "keywords": ["marketing", "google-ads", "seo", "content", "wordpress", "agency", "openrouter"]
}
```

- [ ] **Step 2: Update marketplace.json**

```bash
cat .claude-plugin/marketplace.json | grep -n version
```
Update both `metadata.version` and `plugins[0].version` to `1.4.3`.

- [ ] **Step 3: Verify both files updated**

```bash
grep version plugins/lhm-marketing-hub/.claude-plugin/plugin.json
grep version .claude-plugin/marketplace.json
```
Expected: `1.4.3` in all locations.

- [ ] **Step 4: Commit**

```bash
git add plugins/lhm-marketing-hub/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: version bump 1.4.2 → 1.4.3 — agent architecture redesign"
```

---

### Task 17: Update README

**Files:**
- Modify: `README.md` (root)

- [ ] **Step 1: Update agent listings**

In the README, find and update:
- The agents section: replace `marketing-assistant`, `seo-specialist`, `content-writer`, `google-ads-monthly-review`, `client-analytics-dashboard` with `start`, `google-ads`, `seo`, `content`, `wordpress`
- Skill count: add 3 (`post-meeting-review`, `client-update`, `ga-dashboard-artifact`), remove 1 (`ga-dashboard`), net +2
- Add entries for the new skills in the Skills Catalog under the correct categories:
  - `post-meeting-review` under **Client Management**
  - `client-update` under **Client Management**
  - `ga-dashboard-artifact` under **Analytics & Reporting**

- [ ] **Step 2: Verify counts are consistent**

```bash
ls plugins/lhm-marketing-hub/skills/ | wc -l
```
Use this number to update the README skill count.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for agent redesign and new skills"
```

---

## Post-Implementation Verification

### Task 18: Smoke test

- [ ] **Step 1: Verify all new agents have valid frontmatter**

```bash
for f in plugins/lhm-marketing-hub/agents/*.md; do
  echo "=== $f ===" && head -4 "$f"
done
```
Expected: each file has `---`, `name:`, `description:` in the first 4 lines.

- [ ] **Step 2: Verify all new skills have SKILL.md and LEARNED.md**

```bash
for d in post-meeting-review client-update ga-dashboard-artifact; do
  echo "=== $d ===" && ls plugins/lhm-marketing-hub/skills/$d/
done
```
Expected: `LEARNED.md  SKILL.md` for each.

- [ ] **Step 3: Verify all reference files exist**

```bash
ls plugins/lhm-marketing-hub/references/lhm-philosophy/
ls plugins/lhm-marketing-hub/references/agency-learnings/
ls plugins/lhm-marketing-hub/references/context-preamble.md
ls plugins/lhm-marketing-hub/references/self-improvement-protocol.md
```

- [ ] **Step 4: Verify version consistency**

```bash
grep -h '"version"' plugins/lhm-marketing-hub/.claude-plugin/plugin.json .claude-plugin/marketplace.json
```
Expected: all lines show `1.4.3`.

- [ ] **Step 5: Invoke start agent with a test client folder**

Navigate to a client folder directory and invoke `/lhm-marketing-hub:start`. Verify:
- Context preamble runs
- 4-line state summary displays
- Routing options appear
- Selecting "Google Ads" routes to the google-ads agent correctly

- [ ] **Step 6: Final commit if any fixes needed**

```bash
git add -A
git commit -m "fix(marketing-hub): post-implementation smoke test fixes"
```
