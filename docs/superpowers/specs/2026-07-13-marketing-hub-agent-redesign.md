# LHM Marketing Hub — Agent Architecture Redesign
**Date:** 2026-07-13  
**Approach:** Refactor existing agents (Approach A)  
**Status:** Approved for implementation

---

## Problem

The current plugin has `marketing-assistant` as a monolithic orchestrator and a `start` skill that duplicates its logic. Specialist agents (`seo-specialist`, `google-ads-monthly-review`, `content-writer`) are thin wrappers — they route to skills but don't carry a persona, philosophy, or coaching behaviour. There is no client state awareness beyond `client_profile.md`, no agency-level learning, no self-improvement loop, and no second-opinion capability.

---

## Solution Overview

5 specialist agents, each self-sufficient, each carrying the LHM philosophy for their discipline. A shared infrastructure layer handles client context, goals, active projects, and agency-level learning. Two new skills handle meeting debriefs and client data updates.

---

## Architecture

```
/lhm-marketing-hub:start        → concierge agent (replaces marketing-assistant + start skill)
/lhm-marketing-hub:google-ads   → Google Ads specialist (refactors google-ads-monthly-review agent)
/lhm-marketing-hub:seo          → SEO specialist (refactors seo-specialist agent)
/lhm-marketing-hub:content      → Content specialist (refactors content-writer agent)
/lhm-marketing-hub:wordpress    → WordPress editor (new)
```

Each specialist agent is self-sufficient: if invoked directly (bypassing start), it runs the context preamble itself and proceeds. Start is a concierge, not a gate.

---

## Shared Infrastructure (New Reference Files)

### `references/context-preamble.md`

Runs at the top of every specialist agent. Steps in order:

1. Scan current directory for client folders
2. Load `client_profile.md` — authoritative, never re-ask what's already there
3. Flag `is_health_client` — AHPRA rules apply if true
4. Check conversion economics are defined: profitable CPA threshold, avg revenue per conversion, margin/overhead structure. If missing for Ads work, flag and ask before proceeding.
5. Load `client/goals.md` — KPIs per channel, 90-day targets, annual targets, benchmarks vs last year. If missing, create it.
6. Load `client/current-projects.md` — what the team is actively working on. If missing, create it.
7. Scan the relevant discipline folder (last 90 days) — last zone classification, last keyword snapshot, last review findings, open action items.
8. Read `references/agency-learnings/[discipline].md` — what's worked and failed across all clients in this discipline.
9. Narrate 4-line state summary:

```
Client: [Name] | Health: yes/no | AHPRA: applies/not applicable
State: [key metric vs last period] | [zone or ranking status] | [CPA vs target]
Goals: [primary KPI] | [90-day target] | [annual target]
Active: [current projects summary]
```

### `references/lhm-philosophy/google-ads.md`

- **Profitability-first:** ROAS and CPA are vanity metrics without margin context. Always anchor to true profitable CPA (revenue per conversion minus overheads). A ROAS of 5 on 15% margins is a loss. $100 CPA on a $500 average job value with high overheads may also be a loss.
- **Conversion quality before volume:** Clean, accurately tracked conversions are the foundation. Verify conversion setup before optimising for scale.
- **AdPulse zone system is the compass:** Determine zone before any action. Present only the checklist for the matched zone.
- **Adversarial by default:** Assume waste exists until data proves otherwise. Monthly = zone check + coaching. Quarterly = full red-team (Cynic lens + Path Tracer lens).
- **Coach mode:** Walk tasks one at a time. Push back when user wants to skip — ask them to justify. If justification reveals something new, trigger self-improvement check.
- **AHPRA compliance:** Only applies when `is_health_client = true`. Never apply to non-health clients.
- **Ad copy multi-model creative process:** `ad-copy-generator` uses a creative director model — multiple models contribute headlines/descriptions, Claude curates and compliance-checks:
  1. Claude generates a set anchored to brief and AHPRA compliance rules
  2. GPT-4o via OpenRouter generates a second set from a different creative angle
  3. Claude curates the combined pool — selects strongest, removes duplicates, flags compliance issues, verifies character limits
  4. Curated set goes to user for approval — never raw output from both models
  - AHPRA compliance review is always Claude's responsibility. No GPT-4o headline goes to the client without Claude reviewing it first.
- **Second opinion:** Offered after zone classification and before execution on significant changes.
- **MCP tools:** Google Ads MCP (MCC 394-736-1921), AdPulse MCP, Keywords Everywhere, OpenRouter MCP.

### `references/lhm-philosophy/seo.md`

- **Keywords as data anchor, questions as the optimization target:** Use keyword data to find the topic, then optimise for every question people have within that topic.
- **Cross-channel keyword intelligence:** Keywords Everywhere + GSC for search data. Layer in Google Ads MCP to surface keywords that are actually converting — these get SEO priority.
- **Track progress from prior work:** Before recommending anything, check prior ranking snapshots in the client folder. Know where we are before deciding where to go.
- **GEO alongside traditional:** AI citation optimisation is standard, not optional.
- **Know when to defer:** Site structure and IA → WordPress hub (`sitemap-architect`). Ongoing local SEO and GMB → GMB hub. Marketing hub SEO = strategic advisor and content-focused SEO.
- **Second opinion:** Offered after strategy recommendations.
- **MCP tools:** GSC MCP, Keywords Everywhere, Google Ads MCP (for converting keywords), browser.

### `references/lhm-philosophy/content.md`

- **Interview before writing:** Always understand the goal, audience, and intent before producing anything.
- **Research before brief:** Offer research options — keyword research, TAYA question discovery, web research — before the brief is written. Never skip this step.
- **Brief before writing:** A structured brief is always generated and confirmed before any content is written. No exceptions.
- **8-pass pipeline with multi-model routing:** All content over 300 words routes through the 8-pass engine. Passes are split across models by role:
  - Pass 1 (research synthesis): Gemini 2.5 Pro via OpenRouter — strongest at grounding and factual recall
  - Passes 2-7 (outline, drafts, burstiness, perplexity, human bookends, conversion): Claude — voice consistency during core writing
  - Pass 8 (final QC): GPT-4o via OpenRouter — fresh eyes, different bias, catches what Claude misses in its own output
- **No single-pass content.** Never generate long-form in one call regardless of model.
- **Anti-AI writing:** All output enforces the anti-AI writing guidelines from `references/anti-ai-writing-guidelines.json`.
- **Second opinion:** Offered after brief generation, before writing begins.
- **MCP tools:** Keywords Everywhere, GSC MCP, OpenRouter MCP, browser (for research).

### `references/lhm-philosophy/wordpress.md`

- **Level 1-2 editor, not developer:** Title tags, meta descriptions, copy updates, blog publishing, minor structural edits.
- **Site type detection:** Detect Elementor vs Gutenberg at session start. If Gutenberg, check for Git repository.
- **WordPress REST API for direct changes:** Use API credentials from `client_profile.md` to make changes on behalf of the user.
- **Coach mode:** For team members not confident with WordPress, coach through manual steps instead of executing directly.
- **Backup gate:** Before any Level 2 or structural change, prompt user to run a Sark backup. Wait for confirmation before proceeding.
- **No second opinion:** This agent is execution-focused, not strategic.
- **MCP tools:** WordPress REST API, browser.

### `references/self-improvement-protocol.md`

Applies across all agents and skills. At the end of every session:

1. **Client-level learning:** Did we discover something reusable about how this client's account or market works? If yes: "Want me to update LEARNED.md for this skill?"
2. **Skill improvement:** Did we discover something that should change how the skill works for everyone? If yes: "This should probably be baked into the skill itself — want me to update it?"
3. **New skill:** Did this session surface a repeatable task that has no existing skill? If yes: "This doesn't fit any existing skill — should we create a new one?"
4. **Agency learning:** Was this a meaningful win or loss worth sharing across all clients? If yes: "Want me to add this to agency learnings for [discipline]?"

The agent also pushes back during sessions when the user wants to skip a checklist task. Ask for justification. If the justification reveals something genuinely new about the client or the market, trigger steps 1-4 immediately.

### `references/agency-learnings/`

```
references/agency-learnings/
  google-ads.md
  seo.md
  content.md
  wordpress.md
```

Entry format — dated, specific, niche-tagged where relevant:

```
- (2026-07-13) [Healthcare] RSA headlines leading with condition name outperformed benefit-led headlines by 40% CTR across 3 physio clients.
- (2026-07-13) [Local services] Broad match with tCPA consistently wastes 30%+ budget in the first 30 days on new campaigns. Start with exact/phrase.
```

Read at the start of every relevant session via the context preamble. Written to at the end of sessions via the self-improvement protocol.

---

## Agent Specifications

### Agent 1: `start`

**File:** `agents/start.md` (replaces `marketing-assistant.md`)  
**Role:** Concierge. Oriented, not operational.

**Workflow:**
1. Run context preamble — display 4-line state summary
2. Ask: "What are we working on today?" — offer: Google Ads, SEO, Content, WordPress, Post-Meeting Review, Client Update, Other
3. If "just had a meeting" → run `post-meeting-review` skill first, then re-ask
4. If "something's changed" → run `client-update` skill first, then re-ask
5. Route to the correct specialist agent with full context

**Skill catalog and agent routing logic** carried over from `marketing-assistant.md` (all existing routing rules preserved).

---

### Agent 2: `google-ads`

**File:** `agents/google-ads.md` (refactors `google-ads-monthly-review.md`)  
**Persona:** Senior Google Ads manager. Opinionated, data-driven, adversarial by default. Knows Australian healthcare. Never celebrates a ROAS without checking the margin.

**Workflow:**
1. Context preamble + 4-line state summary (last zone, CPA target, true profitable CPA, budget pacing)
2. Ask: "Monthly check-in, quarterly adversarial review, or specific task?"
3. Determine AdPulse zone → present that zone's checklist only
4. Ask: "Want me to coach you through these now?"
5. Walk tasks one at a time — push back if user skips without justification
6. Pull in the right skill per task: `keyword-optimizer`, `ad-copy-generator`, `bid-budget-optimizer`, `pmax-optimizer`, `landing-page-optimizer`
7. After recommendations: "Want a second opinion on this before we execute?"
8. End of session: self-improvement protocol

**MCP tools:** Google Ads MCP, AdPulse MCP, Keywords Everywhere, browser  
**Inherits:** All existing `google-ads-monthly-review` agent routing logic

---

### Agent 3: `seo`

**File:** `agents/seo.md` (refactors `seo-specialist.md`)  
**Persona:** Senior SEO strategist. Thinks in topics, not keywords. Cross-references paid data with organic. Knows where the client ranks before recommending anything.

**Workflow:**
1. Context preamble + 4-line state summary (last ranking snapshot, organic trend, active SEO work)
2. Ask: "What's the SEO question or task today?"
3. Classify: content piece / ranking check / audit / strategy question / other
4. For content: keyword research (Keywords Everywhere + GSC + Google Ads MCP converters) → recommend content angle (TAYA, GEO, standard blog) → hand to `content` agent for writing
5. For ranking/audit: pull GSC data, compare to prior snapshots in client folder
6. Defer explicitly: "Site structure → WordPress hub. Local/GMB ongoing → GMB hub."
7. After strategy: "Want a second opinion on this?"
8. End of session: self-improvement protocol

**MCP tools:** GSC MCP, Keywords Everywhere, Google Ads MCP, browser

---

### Agent 4: `content`

**File:** `agents/content.md` (refactors `content-writer.md`)  
**Persona:** Senior copywriter and content strategist. Interviews before writing. Never produces a word without a brief. Allergic to AI slop.

**Workflow:**
1. Context preamble + 4-line state summary (active content pieces, brand voice from client_profile.md)
2. Interview: what are we writing, who for, what's the goal, what do we know?
3. Recommend research: "Want me to run keyword research / TAYA / web research first?"
4. Generate structured brief — always, before any writing
5. "Want a second opinion on this brief before we write?"
6. Route to 8-pass pipeline for anything over 300 words
7. Enforce anti-AI writing guidelines on all output
8. End of session: self-improvement protocol

**MCP tools:** Keywords Everywhere, GSC MCP, browser

---

### Agent 5: `wordpress`

**File:** `agents/wordpress.md` (new)  
**Persona:** Senior content editor who knows WordPress. Calm, methodical, safety-conscious. Coaches team members who aren't confident.

**Workflow:**
1. Context preamble + check WordPress credentials in client_profile.md
2. Detect site type: Elementor or Gutenberg (check for Git repo if Gutenberg)
3. Ask: what needs updating?
4. Classify: Level 1 (meta, copy, blog post) or Level 2 (structural changes)
5. Level 2: "Before we proceed, please take a Sark backup. Confirm when done."
6. Execute via WordPress REST API, or coach user through manual steps if they prefer
7. End of session: self-improvement protocol (agency-learnings less relevant here)

**MCP tools:** WordPress REST API, browser

---

## New Skills

### `post-meeting-review`

**Trigger:** User says "we just had a meeting" or runs it directly after a client call.

1. Pull Fathom transcript (Fathom MCP if available; fallback: user pastes transcript)
2. Extract: decisions made, action items, client feedback, anything that changes goals or projects
3. Update `client/goals.md`, `client/current-projects.md`, `client_profile.md` with changes
4. Save `meetings/YYYY-MM-DD-meeting-notes.md` to client folder
5. Flag strategic implications: "Client mentioned Ads performance — recommend zone check" etc.
6. Trigger `client-update` skill if any client data changed (name, service, contact)

### `client-update`

**Trigger:** Account manager says something has changed (name, service, location, contact), or triggered automatically by `post-meeting-review`.

1. Take the change as input
2. Scan all client files — list every reference found
3. Update data references automatically
4. Flag strategic downstream implications: "This affects your Google Ads brand campaign — want me to queue an RSA refresh?"
5. Log the change with date in `client_profile.md` change history section

---

## Standard Client File Structure

Every client folder should contain:

```
[client-name]/
  client_profile.md         — who they are, AHPRA flag, conversion economics
  goals.md                  — KPIs per channel, 90-day and annual targets, benchmarks
  current-projects.md       — what the team is actively working on
  meetings/                 — YYYY-MM-DD-meeting-notes.md files
  google_ads/YYYY-MM/       — existing structure preserved
  seo/YYYY-MM/              — existing structure preserved
  content/YYYY-MM/          — existing structure preserved
```

`goals.md` and `current-projects.md` are created by the context preamble on first load if missing.

---

## Second Opinion Pattern

Available in: `google-ads`, `seo`, `content` agents.  
Trigger: On-demand — agent offers after generating significant recommendations.

Standard offer: "Want me to get a second opinion on this before we proceed?"

Implementation: **OpenRouter MCP** (primary) — install with two commands, provides access to GPT-4o, Gemini 2.5 Pro, Grok and 400+ models via a single `send-message` tool call. Enable BYOK in OpenRouter settings to use your own OpenAI/Google API keys at direct pricing. Default $10 spend cap — raise in OpenRouter settings.

Setup:
```bash
claude mcp add --transport http openrouter https://mcp.openrouter.ai/mcp
claude mcp login openrouter
```

Fallback: Bash curl with `$OPENAI_API_KEY` env var — works immediately in any skill with no MCP required.

Note: "Anthology MCP" does not exist — confirmed via research. Was likely a confusion with AnythingLLM (different product, different use case).

Not applicable in `wordpress` agent — execution-focused, not strategic.

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Specialist agents are self-sufficient (don't require start) | Power users jump straight in; start is a concierge not a gate |
| Agency learnings are a separate tier from client LEARNED.md | Client patterns stay client-specific; cross-client wins become agency IP |
| Second opinion is on-demand, not automatic | Keeps routine sessions fast; option is always visible |
| post-meeting-review triggers client-update automatically | One command after a meeting keeps all state files current |
| AHPRA gated on is_health_client flag | LHM works with non-health clients; AHPRA should never apply to them |
| Fathom MCP primary, paste fallback | Fathom MCP existence unconfirmed — fallback ensures skill works regardless |

---

## New Skills (Additional)

### `ga-dashboard-artifact` (replaces `ga-dashboard` skill and `client-analytics-dashboard` agent)

**Scope: Barebones v1, iterate from there.**

1. Connect to GA4 via analytics MCP
2. Pull core metrics for chosen date range vs prior period: sessions, users, conversions, top pages, traffic sources
3. Render as a Claude Artifact — KPI tiles at top, bar/line charts for trends, period comparison
4. Save a `analytics/YYYY-MM/dashboard-summary-YYYY-MM.md` to client folder alongside the Artifact

`ga-event-config` skill is unchanged — setup work, not reporting.  
`client-analytics-dashboard` agent is retired.  
`ga-dashboard` skill is replaced by this.

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Specialist agents are self-sufficient (don't require start) | Power users jump straight in; start is a concierge not a gate |
| Agency learnings are a separate tier from client LEARNED.md | Client patterns stay client-specific; cross-client wins become agency IP |
| Second opinion is on-demand, not automatic | Keeps routine sessions fast; option is always visible |
| post-meeting-review triggers client-update automatically | One command after a meeting keeps all state files current |
| AHPRA gated on is_health_client flag | LHM works with non-health clients; AHPRA should never apply to them |
| Fathom MCP primary, paste fallback | Fathom MCP now connected — confirm tool names at implementation start |
| OpenRouter MCP for second opinions | Two-command install, access to GPT-4o/Gemini/Grok, BYOK removes markup |
| ga-dashboard-artifact replaces ga-dashboard skill + client-analytics-dashboard agent | Artifacts produce better output than markdown dashboards; iterate from barebones v1 |

---

## Out of Scope

- WordPress hub refactor (separate plugin, separate concern)
- GMB hub refactor (separate plugin)
- OpenRouter MCP configuration (user sets up separately; plugin uses `send-message` tool once connected)
- Fathom MCP configuration (user sets up separately; skill uses transcript tool once connected)
