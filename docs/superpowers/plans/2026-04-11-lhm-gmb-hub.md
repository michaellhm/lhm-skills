# lhm-gmb-hub Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Claude plugin that executes a repeating 3-month Google Business Profile optimisation cycle for local SEO clients, with project management tracking and an 8-pass writing engine.

**Architecture:** 17 individual skills organised by phase (Month 0-3), 6 agents (1 master orchestrator, 4 phase agents, 1 content-writing utility agent), per-client GMBProjectManagement.md for state tracking, and shared reference files for the 8-pass writing engine, content guardrails, and MCP setup guides. All content-producing skills hand off to a content-writer agent for the 8-pass pipeline.

**Tech Stack:** Claude Code plugin system (markdown skills, agents, plugin.json), MCP integrations (Local Falcon, DataForSEO, Screaming Frog + existing GSC/GA4/Keywords Everywhere)

**Spec:** `docs/superpowers/specs/2026-04-11-lhm-gmb-hub-design.md`

---

## File Structure

```
plugins/lhm-gmb-hub/
├── .claude-plugin/plugin.json                          # Plugin manifest
├── CLAUDE.md                                           # Plugin-wide rules
├── README.md                                           # Plugin documentation
├── .mcp.json                                           # MCP server configs
├── agents/
│   ├── gmb-orchestrator.md                             # Master agent
│   ├── onboarding-agent.md                             # Month 0
│   ├── service-optimizer-agent.md                      # Month 1
│   ├── content-expansion-agent.md                      # Month 2
│   ├── link-building-agent.md                          # Month 3
│   └── content-writer.md                               # 8-pass writing utility
├── skills/
│   ├── gmb-project-manager/SKILL.md + LEARNED.md       # Project tracking
│   ├── run-local-diagnostic/SKILL.md + LEARNED.md      # Grid scans + competitor audit
│   ├── gbp-optimiser/SKILL.md + LEARNED.md             # GBP profile optimisation
│   ├── gbp-post-generator/SKILL.md + LEARNED.md        # 52 weekly posts
│   ├── citation-audit/SKILL.md + LEARNED.md            # Directory NAP check
│   ├── entity-mapper/SKILL.md + LEARNED.md             # Competitor entity extraction
│   ├── site-architecture-mapper/SKILL.md + LEARNED.md  # GBP-mirrored silo
│   ├── service-priority-selector/SKILL.md + LEARNED.md # Pick 3 services
│   ├── consistency-signal-audit/SKILL.md + LEARNED.md  # 8 homepage signals
│   ├── service-page-writer/SKILL.md + LEARNED.md       # Goal-completion content
│   ├── technical-page-audit/SKILL.md + LEARNED.md      # Schema, speed, indexing
│   ├── faq-content-builder/SKILL.md + LEARNED.md       # PAA → supporting pages
│   ├── neighbourhood-overlay-writer/SKILL.md + LEARNED.md # Geo pages
│   ├── link-gap-finder/SKILL.md + LEARNED.md           # Pages missing links
│   ├── local-authority-finder/SKILL.md + LEARNED.md    # Chambers, sponsorships
│   ├── pr-brief-generator/SKILL.md + LEARNED.md        # Press release drafts
│   └── monthly-cycle-report/SKILL.md + LEARNED.md      # Monthly/cycle reports
└── references/
    ├── anti-ai-writing-guidelines.json                 # Copy from marketing-hub
    ├── ahpra-compliance-framework.md                   # Healthcare compliance
    ├── gmb-ranking-principles.md                       # 7 key principles
    ├── mcp-setup-guide.md                              # Install guide for 3 MCPs
    ├── 8-pass-writing-engine.md                        # Writing pipeline spec
    └── content-guardrails/
        ├── service-page.md                             # Service page guardrails
        ├── category-page.md                            # Category page guardrails
        ├── location-page.md                            # Location/geo page guardrails
        └── supporting-content.md                       # FAQ/supporting guardrails
```

## Task Dependencies

```
Task 1 (scaffold) ──┬── Task 2 (CLAUDE.md)
                     ├── Task 3 (.mcp.json)
                     ├── Task 4-9 (references) ──┬── Task 10-26 (skills) ── Task 27-32 (agents)
                     └────────────────────────────┘
Task 27-32 (agents) ── Task 33 (README) ── Task 34 (marketplace + version bump)
```

**Parallelisable groups:**
- Tasks 2, 3, 4-9 (all depend only on Task 1)
- Tasks 10-26 (all skills, depend on references being done)
- Tasks 27-32 (all agents, depend on skills being done so we can reference them)

---

## Task 1: Plugin Scaffold

**Files:**
- Create: `plugins/lhm-gmb-hub/.claude-plugin/plugin.json`
- Create: All skill directories with empty LEARNED.md files

- [ ] **Step 1: Create the plugin directory structure**

```bash
# Plugin root
mkdir -p plugins/lhm-gmb-hub/.claude-plugin
mkdir -p plugins/lhm-gmb-hub/agents
mkdir -p plugins/lhm-gmb-hub/references/content-guardrails

# All 17 skill directories
for skill in gmb-project-manager run-local-diagnostic gbp-optimiser gbp-post-generator citation-audit entity-mapper site-architecture-mapper service-priority-selector consistency-signal-audit service-page-writer technical-page-audit faq-content-builder neighbourhood-overlay-writer link-gap-finder local-authority-finder pr-brief-generator monthly-cycle-report; do
  mkdir -p "plugins/lhm-gmb-hub/skills/$skill"
done
```

- [ ] **Step 2: Create plugin.json**

Write to `plugins/lhm-gmb-hub/.claude-plugin/plugin.json`:

```json
{
  "name": "lhm-gmb-hub",
  "description": "Google Business Profile optimisation system — repeating 3-month cycle of GBP foundation, service page optimisation, content expansion, and strategic link building with per-client project management tracking.",
  "version": "1.2.8",
  "author": {
    "name": "LHM Digital"
  },
  "keywords": ["gmb", "gbp", "local-seo", "google-business-profile", "agency"]
}
```

- [ ] **Step 3: Create all LEARNED.md files**

Write this content to every `plugins/lhm-gmb-hub/skills/*/LEARNED.md`:

```markdown
# Learned

<!-- Auto-maintained by Claude. Max 50 entries. Oldest/unused entries pruned after 3 months. -->
```

- [ ] **Step 4: Commit scaffold**

```bash
git add plugins/lhm-gmb-hub/
git commit -m "scaffold: create lhm-gmb-hub plugin directory structure"
```

---

## Task 2: CLAUDE.md (Plugin-Wide Rules)

**Files:**
- Create: `plugins/lhm-gmb-hub/CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

Write to `plugins/lhm-gmb-hub/CLAUDE.md`:

```markdown
# LHM GMB Hub - Plugin-Wide Rules

These rules apply to EVERY skill and agent in this plugin, without exception.

## Mandatory: Anti-AI Writing Guidelines

Before writing ANY content (copy, suggestions, reports, emails, audits, strategies, recommendations, file outputs, or conversational responses that include written content), you MUST follow the anti-AI writing guidelines stored at:

`${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`

Read this file at the start of every skill execution. These rules apply to ALL written output.

### Quick Reference (always enforce these):

1. **Break the Rule of 3** - Don't organize ideas in triplets. Vary structural patterns.
2. **Avoid contrast framing** - Reduce "while X, Y" and "although X, Y" constructions.
3. **Eliminate poetic shift phrases** - No "in a world where," "in an era of," "in a landscape defined by."
4. **Use varied paragraph structures** - Don't default to odd-numbered structures (5, 7, 9 paragraphs).
5. **Limit hypophora** - Don't pose questions and immediately answer them.
6. **Moderate adverb usage** - Avoid "-ly" adverbs (significantly, dramatically, effectively). Use stronger verbs.
7. **Avoid marketing cliche pairings** - No "seamless integration," "robust solution," "game-changing innovation."
8. **Use natural transitions** - No "Let's explore," "Let's dive into," "Now, let's turn to."
9. **End paragraphs naturally** - No vague emotional insights or forced inspirational statements.
10. **No em dashes** - Never use em dashes. Use commas, periods, or parentheses instead.

### Overall principle

Write with an authentic voice. Use specific examples, concrete details, and natural phrasing. Occasional imperfection is better than polished-but-robotic output.

## Mandatory: AHPRA Compliance (Healthcare Clients)

All content for healthcare clients MUST comply with AHPRA advertising guidelines. Before publishing any content, check against:

`${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`

Key rules (always enforce):
- No testimonials that could be interpreted as clinical outcomes
- No before/after claims
- No "best" or superlative claims about treatment
- No guarantees of results
- No misleading or deceptive claims about services

## Mandatory: 8-Pass Writing Engine

All content-producing skills MUST route content generation through the content-writer agent which implements the 8-pass writing pipeline. Skills handle research and context gathering; the content-writer agent handles the actual writing.

Reference: `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md`

Never generate long-form content in a single pass. The 8-pass system exists to produce content that passes AI detection, reads naturally, and converts.

## Mandatory: Project Doc Updates

Every skill that completes a task MUST update `GMBProjectManagement.md` in the client's gmb/ folder:
- Mark the relevant task as `[x]` with a completion date
- Record any key outputs or metrics
- Add notes for any decisions made

## Mandatory: Self-Learning Protocol

Every skill in this plugin has a `LEARNED.md` file in its directory. This file is Claude's persistent memory for that specific skill, written by Claude through use.

### Before Executing Any Skill

Read `LEARNED.md` from the current skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/LEARNED.md`). Apply any relevant entries to the current task. If the file is empty or only contains the header, proceed normally.

### When to Write a New Entry

After completing a skill execution, check whether you discovered something that would save time or prevent mistakes in future runs. Only record entries that are **reusable across sessions**, not one-off context.

Record things like:
- **Tool/API failures** - specific services that block access, rate limits, broken endpoints
- **Data quirks** - unexpected formats, missing fields, inconsistent naming conventions
- **Workflow blockers** - steps that consistently fail or need workarounds
- **Format corrections** - output formats the user corrected or preferred over the default
- **Skill interaction issues** - when skills need to be run in a specific order

### Entry Format

One line per entry. Dated. Specific. Actionable.

```
- (YYYY-MM-DD) Specific observation or rule. Not vague advice.
```

### Maintenance Rules

- **Cap**: Maximum 50 entries per LEARNED.md file
- **Before adding**: Count existing entries. If at or over 50, consolidate first
- **Consolidation**: Merge duplicate/similar entries, drop entries older than 3 months that were never referenced again
- **Never delete**: Entries that document persistent limitations or that you've referenced in recent sessions

### Do NOT Record

- Session-specific context (current client name, task details, file paths for this run)
- Information already documented in SKILL.md, client_profile.md, or reference files
- Speculative conclusions from a single observation (wait until a pattern recurs)
- Anything the user explicitly told you not to remember

## Mandatory: MCP Graceful Fallbacks

This plugin uses several MCP servers that may not be installed. When a skill requires an MCP that is not available:

1. Do NOT fail silently or skip the step
2. Display the setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`
3. Offer a manual alternative (e.g. "paste your Local Falcon results and I'll record them")
4. Continue with the skill using whatever data is available

## Output Structure

All skill outputs go to the client folder under `gmb/`:

```
client_folder/gmb/
├── GMBProjectManagement.md
├── onboarding/           # Month 0 outputs
└── monthly-optimization/
    └── YYYY-MM/          # Per-month outputs
```

Skills must create these directories if they don't exist before writing output files.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/CLAUDE.md
git commit -m "feat(gmb-hub): add plugin-wide rules (CLAUDE.md)"
```

---

## Task 3: MCP Configuration

**Files:**
- Create: `plugins/lhm-gmb-hub/.mcp.json`

- [ ] **Step 1: Write .mcp.json**

Write to `plugins/lhm-gmb-hub/.mcp.json`:

```json
{
  "local-falcon": {
    "command": "npx",
    "args": ["@local-falcon/mcp"],
    "env": {
      "LOCAL_FALCON_API_KEY": ""
    }
  },
  "dataforseo": {
    "command": "npx",
    "args": ["dataforseo-mcp"],
    "env": {
      "DATAFORSEO_LOGIN": "",
      "DATAFORSEO_PASSWORD": ""
    }
  },
  "screaming-frog": {
    "command": "uvx",
    "args": ["screaming-frog-mcp"],
    "env": {}
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/.mcp.json
git commit -m "feat(gmb-hub): add MCP server configuration"
```

---

## Task 4: Reference — Anti-AI Writing Guidelines

**Files:**
- Create: `plugins/lhm-gmb-hub/references/anti-ai-writing-guidelines.json`

- [ ] **Step 1: Copy from marketing-hub**

```bash
cp plugins/lhm-marketing-hub/references/anti-ai-writing-guidelines.json plugins/lhm-gmb-hub/references/anti-ai-writing-guidelines.json
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/references/anti-ai-writing-guidelines.json
git commit -m "feat(gmb-hub): add anti-AI writing guidelines reference"
```

---

## Task 5: Reference — AHPRA Compliance Framework

**Files:**
- Create: `plugins/lhm-gmb-hub/references/ahpra-compliance-framework.md`

- [ ] **Step 1: Write the AHPRA framework**

Write to `plugins/lhm-gmb-hub/references/ahpra-compliance-framework.md`:

```markdown
# AHPRA Compliance Framework for Content

This framework applies to ALL content produced for healthcare clients regulated by AHPRA (Australian Health Practitioner Regulation Agency).

## Mandatory Pre-Publish Checks

Every piece of content must pass ALL of the following checks before it can be published or delivered to a client.

### 1. No Testimonials as Clinical Evidence

- [ ] No patient quotes implying treatment outcomes ("After my treatment, I could walk again")
- [ ] No case studies presented as typical results
- [ ] Reviews displayed on the website must not be curated to show only positive clinical outcomes
- [ ] Google review widgets are permitted (unfiltered display of actual reviews)

### 2. No Before/After Claims

- [ ] No before/after photos showing treatment results
- [ ] No comparative language suggesting transformation ("from pain to pain-free")
- [ ] No "success rate" statistics unless from peer-reviewed published research
- [ ] No implied outcomes through narrative ("patients typically experience...")

### 3. No Superlative Claims

- [ ] No "best physiotherapist in [city]"
- [ ] No "leading provider of [service]"
- [ ] No "#1 rated" or "top-rated" claims
- [ ] No "most experienced" or "most qualified"
- [ ] Acceptable: factual statements like "established in 2005" or "team of 12 practitioners"

### 4. No Guarantees of Results

- [ ] No "guaranteed results" or "guaranteed improvement"
- [ ] No "we will fix your [condition]"
- [ ] No timeframe promises ("you'll feel better in 3 sessions")
- [ ] Acceptable: "treatment aims to..." or "may help with..."

### 5. No Misleading Claims

- [ ] No implying services are unique when they are standard practice
- [ ] No creating unreasonable expectations about treatment
- [ ] No omitting material information that would affect a patient's decision
- [ ] No using scientific terminology to make claims sound more credible than they are

### 6. Acceptable Language Patterns

Use these patterns instead of prohibited claims:

| Instead of | Write |
|-----------|-------|
| "Best physio in Melbourne" | "Physiotherapy clinic in Melbourne's inner north" |
| "We guarantee results" | "Our treatment approach focuses on..." |
| "Patients experience dramatic improvement" | "Treatment aims to support recovery and manage symptoms" |
| "Our proven method" | "Evidence-based treatment approaches" |
| "Leading experts" | "Experienced practitioners" |
| "You'll feel better fast" | "Many conditions respond well to early intervention" |

### 7. Required Disclaimers

For any content that discusses treatment outcomes or effectiveness:
- Include: "Individual results may vary"
- Include: "Consult with a qualified practitioner for advice specific to your situation"
- These can be in a footer or at the end of the relevant section

## Quick Decision Tree

1. Does the content make a claim about treatment outcomes? → Check sections 2, 4, 5
2. Does the content include patient stories or reviews? → Check section 1
3. Does the content compare the practice to others? → Check section 3
4. Does the content promise specific timeframes or results? → Check section 4
5. When in doubt → use softer language and flag for human review
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/references/ahpra-compliance-framework.md
git commit -m "feat(gmb-hub): add AHPRA compliance framework reference"
```

---

## Task 6: Reference — GMB Ranking Principles

**Files:**
- Create: `plugins/lhm-gmb-hub/references/gmb-ranking-principles.md`

- [ ] **Step 1: Write the principles**

Write to `plugins/lhm-gmb-hub/references/gmb-ranking-principles.md`:

```markdown
# GMB Ranking Principles

These 7 principles underpin every skill in this plugin. Reference them when making content or strategy decisions.

## 1. The GBP is the Asset We're Ranking

The Google Business Profile is what appears in the map pack. The website exists to support the GBP's authority, not the other way around. Every page we create, every link we build, every piece of content we write serves the goal of making the GBP rank higher.

## 2. Goal Completion Over Aesthetics

Google measures "goal completion" for local businesses. This means: did the user solve their problem and stop searching? For local services, this is measured by ACTION (clicking to call, getting directions, booking), not by how long someone reads.

Every service page must target the "Who can do this for me?" searcher, not the "How do I do this?" searcher. Content must drive action: click to call, get directions, book online.

## 3. No Traditional Blogging

FAQ and supporting content pages serve the same purpose as blog posts but actually move rankings. They live within the site structure (linked from service pages), not in a blog feed. They strengthen the parent service page's topical authority.

Traditional blog posts ("5 tips for back pain") target people who will never be customers and rarely trigger a map pack result.

## 4. Every Page Needs a Link

If Google can't find an external signal that a human valued the page, it may ignore it. Every page on the client's website needs at least one external link pointing to it. This signals that the content was worth mentioning by someone outside the business.

Acceptable: directory submissions, blog comments, guest posts, forum contributions, chamber of commerce listings, sponsorship links.
Not acceptable: PBN links.

## 5. Diagnose Before You Build

The Local Falcon grid scan tells you whether to build topical content or geographical content. Never guess.

- **Below threshold (topical relevance problem):** Build FAQ and supporting content pages
- **At or above threshold (proximity problem):** Build neighbourhood overlay pages
- **Mixed:** Split effort accordingly

The threshold is 25-50% of the top competitor's Top 3% score.

## 6. AHPRA Compliance is Non-Negotiable

Every piece of content for healthcare clients gets checked against the AHPRA compliance framework before publishing. No exceptions. No "we'll fix it later." Check it before it goes out.

## 7. Editorial Links, Not Nav Links

Google treats links within paragraph content as authority signals. Navigation and footer links are treated as site structure only. They do NOT pass authority the same way contextual paragraph links do.

Every internal link that matters should be an editorial link: placed within body content, using natural anchor text that includes the target keyword. Not just a link in the nav bar or footer.

## Diagnostic Decision Framework

| Metric | Meaning |
|--------|---------|
| Top 3% | Percentage of 169 grid points where the business appears in positions 1-3 |
| Green pins | Positions 1-3 (strong) |
| Yellow pins | Positions 4-10 (opportunity zone, especially 4-6) |
| Red pins | Position 11+ or invisible |
| Threshold | 25-50% of top competitor's Top 3% score |

## Service Priority Decision Framework

| Scenario | What to Prioritise |
|----------|-------------------|
| Client doesn't rank #1 for primary modality + location | Pick the primary modality page + 2 highest-value sub-services |
| Client ranks #1 for primary modality in their suburb | Pick 2-3 sub-services they don't rank for yet |
| Client ranks well locally but wants surrounding suburbs | Pick primary modality + location combinations for 2-3 adjacent suburbs |
| Multi-modality client (e.g. physio + pilates + massage) | Pick the strongest revenue modality first, then the next 2 most important |

## GBP-Website Silo Rule

If a service exists on the GBP, it needs a dedicated page on the website. If a category exists on the GBP, it needs a category page. The website silo and the GBP structure should be identical. Google uses this structure to understand the relationship between the website and the GBP.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/references/gmb-ranking-principles.md
git commit -m "feat(gmb-hub): add GMB ranking principles reference"
```

---

## Task 7: Reference — MCP Setup Guide

**Files:**
- Create: `plugins/lhm-gmb-hub/references/mcp-setup-guide.md`

- [ ] **Step 1: Write the setup guide**

Write to `plugins/lhm-gmb-hub/references/mcp-setup-guide.md`:

```markdown
# MCP Setup Guide

This plugin uses three optional MCP servers in addition to the already-installed GSC, GA4, and Keywords Everywhere MCPs. Skills will work without them (using manual fallbacks), but they are significantly more powerful with MCPs configured.

## Local Falcon MCP

**What it does:** Runs 169-point geo-grid scans for local keywords, returns Top 3% metrics, trend reports, and competitor data. Used by: run-local-diagnostic, service-priority-selector, neighbourhood-overlay-writer, monthly-cycle-report.

**Auth:** API key (get from your Local Falcon account at localfalcon.com)
**Cost:** Credit-based (each scan costs credits based on grid size)

### Claude Code

```bash
claude mcp add local-falcon -- npx @local-falcon/mcp
```

Then set your API key:
```bash
export LOCAL_FALCON_API_KEY="your-api-key-here"
```

### Claude Desktop / CoWork

Add to your MCP configuration (usually `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "local-falcon": {
      "command": "npx",
      "args": ["@local-falcon/mcp"],
      "env": {
        "LOCAL_FALCON_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Alternative: Remote MCP

Local Falcon also offers a hosted MCP endpoint:
```
https://mcp.localfalcon.com/mcp?local_falcon_api_key=YOUR_KEY
```

---

## DataForSEO MCP

**What it does:** SERP data, keyword research, backlink analysis, domain analytics, business listing data from Google Maps. Used by: gbp-optimiser, entity-mapper, link-gap-finder.

**Auth:** Username + password (get from dataforseo.com)
**Cost:** Pay-per-API-call (e.g. $0.01 per keyword task). Very affordable for typical usage.

### Claude Code

```bash
claude mcp add dataforseo -- npx dataforseo-mcp
```

Then set your credentials:
```bash
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"
```

### Claude Desktop / CoWork

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "npx",
      "args": ["dataforseo-mcp"],
      "env": {
        "DATAFORSEO_LOGIN": "your-login",
        "DATAFORSEO_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## Screaming Frog MCP

**What it does:** Full site crawl, exports all indexed pages with on-page data. Used by: link-gap-finder.

**Auth:** None (wraps local Screaming Frog CLI)
**Cost:** Screaming Frog licence is 199 GBP/year. Free version crawls up to 500 URLs.
**Requirement:** Screaming Frog must be installed locally on your machine.

### Claude Code

```bash
claude mcp add screaming-frog -- uvx screaming-frog-mcp
```

### Claude Desktop / CoWork

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "screaming-frog": {
      "command": "uvx",
      "args": ["screaming-frog-mcp"]
    }
  }
}
```

---

## Already Installed MCPs

These MCPs should already be configured in your environment:

| MCP | Used By |
|-----|---------|
| Google Search Console (GSC) | run-local-diagnostic, consistency-signal-audit, technical-page-audit, link-gap-finder, monthly-cycle-report |
| Google Analytics (GA4) | service-priority-selector, monthly-cycle-report |
| Keywords Everywhere | run-local-diagnostic, gbp-optimiser, entity-mapper, service-priority-selector, service-page-writer, faq-content-builder, neighbourhood-overlay-writer, monthly-cycle-report |

If any of these are missing, check your Claude Code or Claude Desktop MCP configuration.

## Checking MCP Availability

When a skill needs an MCP, it should attempt to use the tool first. If the tool is not available, display this message template:

```
[MCP Name] is not configured yet. To set it up, see:
${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md

In the meantime, you can provide the data manually:
[Specific manual alternative for this skill]
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/references/mcp-setup-guide.md
git commit -m "feat(gmb-hub): add MCP setup guide reference"
```

---

## Task 8: Reference — 8-Pass Writing Engine

**Files:**
- Create: `plugins/lhm-gmb-hub/references/8-pass-writing-engine.md`

- [ ] **Step 1: Write the 8-pass engine spec**

Write to `plugins/lhm-gmb-hub/references/8-pass-writing-engine.md`:

```markdown
# 8-Pass Human-Like Writing Engine

This document defines the writing pipeline used by the content-writer agent for ALL long-form content produced by this plugin. No content-producing skill should generate content in a single pass. Every piece of content goes through all 8 passes.

## Why 8 Passes?

One prompt, one model, one pass produces content that reads like AI wrote it, because it did. One consistent tone, predictable sentence lengths, robotic rhythm. That is not how humans write.

Humans write section by section. They take breaks. They come back. The tone shifts slightly between sections. Sentence lengths vary. The 8-pass pipeline mimics this natural variation.

## Content Guardrails

Before every pass, load the content-type-specific guardrail file:

- Service pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/service-page.md`
- Category pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/category-page.md`
- Location/geo pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/location-page.md`
- Supporting/FAQ content: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/supporting-content.md`

Also load: `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`

The guardrail prompt sits on top of every pass to prevent the writing from drifting off-brief.

---

## Pass 1: Research Synthesis

**Input:** Raw research from the calling skill (PAA questions, Reddit threads, competitor page content, local landmarks, entity map entries, search volume data)

**Output:** A structured content brief

**What this pass does:**

Takes all of the raw research and compresses it into a focused writing plan:
- What specific questions does this page need to answer?
- What local details should be woven into the content?
- What angles are competitors covering that we need to cover better?
- What entities from the entity map must appear naturally?
- What is the primary search intent we're targeting?
- What makes this page distinct from every other page on the internet about this topic?

The brief should be 200-400 words. It is the foundation for every subsequent pass.

---

## Pass 2: Strategic Outline

**Input:** The content brief from Pass 1

**Output:** Full page architecture

**What this pass does:**

Builds the page structure from the brief:
- Every H2 heading with its specific angle
- What each section needs to accomplish (not just a topic, but the goal)
- How sections connect to each other (the logical flow from top to bottom)
- Where CTAs should appear naturally
- Where local details should be concentrated
- Approximate word count per section

This is NOT just a list of headings. It maps the logical progression of the entire page. Most AI tools skip this step and just start writing, which is why their content wanders.

---

## Pass 3: Section Draft (Independent Calls)

**Input:** The outline from Pass 2 + content brief from Pass 1 + guardrails

**Output:** First draft of each section

**What this pass does:**

Each H2 section is written with a SEPARATE, INDEPENDENT call. For each section:

1. Load the content brief and guardrails
2. Load ONLY this section's context from the outline (what it needs to accomplish, its angle)
3. Load the preceding section's final paragraph (for transition continuity only)
4. Write JUST this section (target word count from outline)
5. Do NOT reference other sections' exact wording

The separate calls produce slightly different tone, energy, and word choice per section. This mimics how a real writer drafts an article over the course of a day, coming back to each section with fresh energy.

**Implementation note:** Use separate tool calls or separate prompt constructions for each section. The point is that each section gets its own generation context.

---

## Pass 4: Burstiness

**Input:** The assembled first draft (all sections combined)

**Output:** Draft with varied rhythm

**What this pass does:**

AI typically writes in a consistent rhythm. Sentences tend to be about the same length. Paragraphs follow the same cadence. Humans don't write this way.

This pass goes through the entire draft and:
- Varies sentence length: long sentence, then short. Then two medium. Then a fragment.
- Mixes paragraph lengths: a 4-sentence paragraph, then a 1-sentence paragraph, then 3 sentences
- Breaks up any sequences of similarly-structured sentences
- Adds the kind of irregular pacing that makes content feel alive

**Do NOT change the meaning or content.** Only adjust rhythm and structure.

---

## Pass 5: Perplexity Injection

**Input:** The burstiness-adjusted draft

**Output:** Draft with AI patterns removed

**What this pass does:**

Finds predictable AI word patterns and replaces them with words a human would actually use. AI has favourite words and constructions that immediately flag content as machine-generated.

**Kill these words/patterns:**
- "robust" → specific alternative (e.g. "solid", "reliable", or just remove)
- "leverage" → "use", "apply", or rephrase
- "streamline" → "simplify", "speed up", or specific description
- "comprehensive" → "full", "complete", or just remove
- "utilize" → "use"
- "facilitate" → "help", "support", or rephrase
- "significant improvements" → specific description of what improved
- "ensure" → "make sure", "check", or rephrase
- "delve into" → remove or rephrase
- "it's important to note" → remove (just state the thing)
- "in today's [noun]" → remove or be specific
- "whether you're [X] or [Y]" → remove or rephrase
- Em dashes (—) → replace with commas, periods, or parentheses

**Also check against:** `anti-ai-writing-guidelines.json` for the full pattern list.

**Do NOT change the meaning.** Same information, different word choice.

---

## Pass 6: Human Bookends

**Input:** The perplexity-adjusted draft

**Output:** Draft with rewritten opening and closing

**What this pass does:**

Rewrites the FIRST 2 sentences and LAST 2 sentences of the article with extremely conversational, opinionated language. These sentences matter more than the rest of the article combined because:

1. Google's algorithm weighs the opening and closing most heavily
2. AI systems (ChatGPT, Perplexity, etc.) weight the opening when deciding to cite content
3. Searchers read the first couple of sentences, then scroll to the bottom and read the last couple

**Opening sentences must:**
- Address the reader's immediate problem directly
- Sound like a real person talking, not a textbook
- Contain an opinion or perspective (not just facts)
- Be specific to the local area where possible

**Closing sentences must:**
- Circle back to the reader's problem
- Include a natural call to action
- Sound conversational, not like a corporate sign-off
- NOT be a generic "Contact us today!" type ending

---

## Pass 7: Conversion Injection

**Input:** The bookends-adjusted draft

**Output:** Draft with natural CTAs and conversion elements

**What this pass does:**

Goes through the content and naturally injects calls to action, phone numbers, and conversational urgency. Not spammy. Not banner ads dropped in the middle of paragraphs. The kind of lines that make someone stop reading and pick up the phone.

**This pass is DIFFERENT for each content type:**

**Service pages:** Direct CTAs, click to call, get directions, book online. Multiple touchpoints throughout. Phone number in at least 2 places. "If you're dealing with [problem], give us a call on [number]" type language woven into the content.

**Location/geo pages:** Local-specific CTAs with driving directions or proximity references. "We're a [X] minute drive from [landmark]" type language. Local phone number prominent.

**FAQ/supporting pages:** Soft CTAs linking back to the parent service page. "If you'd like to discuss your specific situation, see our [service] page or call us on [number]." Less aggressive, more helpful.

**Category pages:** Editorial links to child service pages with action-oriented language. "Ready to explore [sub-service]? Here's what to expect" type transitions.

**Do NOT:**
- Drop a CTA box in the middle of a paragraph
- Use "Contact us today!" or "Don't wait!" type language
- Add more than 3-4 conversion touchpoints per page
- Make every paragraph end with a CTA

---

## Pass 8: Final QC

**Input:** The conversion-adjusted draft

**Output:** Final content ready for delivery

**What this pass does:**

Evaluates the ENTIRE article as a whole:

1. **Cohesion check:** Do sections flow together despite being written independently? Fix any jarring transitions.
2. **Brief adherence:** Does the content cover everything from the original content brief (Pass 1)? Flag and fill any gaps.
3. **Outline adherence:** Does the structure match the strategic outline (Pass 2)? Fix any drift.
4. **Word count check:** Is the total within the target range for this content type?
   - Service pages: 1,500-2,500 words
   - Location/geo pages: 800-1,500 words
   - FAQ/supporting pages: 400-800 words
   - Category pages: 1,000-1,800 words
5. **AI pattern scan:** Any leftover AI patterns that slipped through Passes 4-5? Fix them.
6. **AHPRA compliance:** For healthcare clients, run final compliance sweep against the AHPRA framework.
7. **Anti-AI guidelines:** Final check against all 10 rules from anti-ai-writing-guidelines.json.
8. **Entity check:** Did the required entities from the entity map appear naturally? Add any missing ones.
9. **Local check:** Does the content sound genuinely local? Or could this page be about any city?

Anything that doesn't meet standard gets rewritten in this pass. This is the quality control layer that catches what the other seven passes may have missed.

---

## Parallel Steps (Generated Alongside Pass 8)

These are produced at the same time as the final QC:

### Meta Tags
- **Title tag:** [Service/Topic] [City] | [Brand Name] (max 60 chars)
- **Meta description:** Action-oriented, includes keyword, max 155 chars
- **H1:** Natural variation of the title tag

### FAQ Section
- 3-5 questions with concise answers
- Based on PAA research from the content brief
- Formatted for FAQ schema markup

### Schema Markup
- **Service pages:** Service schema (serviceType, provider, areaServed)
- **Location pages:** LocalBusiness schema (address, geo, openingHours)
- **FAQ pages:** FAQPage schema (mainEntity array)
- Output as JSON-LD ready for insertion

### External Authority Links
- 2-3 outbound links to authoritative sources
- Government health sites, peak body websites, published research
- Natural anchor text, placed where they add genuine value
- Do NOT link to competitors

### Image Prompts
- 1-2 image descriptions per major section
- Describe what the image should show (for manual sourcing or AI generation)
- Prefer: clinic/practice photos, equipment, team at work, local area shots
- Avoid: generic stock photo descriptions

---

## Content-Writer Agent Handoff Protocol

When a skill calls the content-writer agent, it provides:

```
content_type: "service-page" | "category-page" | "location-page" | "supporting-content"
structured_brief: {
  target_keyword: "[primary keyword]",
  location: "[city/suburb]",
  client_name: "[business name]",
  client_phone: "[phone number]",
  client_address: "[address]",
  entity_map: [list of entities to include],
  research: {
    paa_questions: [...],
    competitor_angles: [...],
    local_context: [...],
    reddit_questions: [...]
  },
  parent_service_page: "[URL, if applicable]",
  word_count_target: [number],
  ahpra_required: true/false
}
```

The content-writer agent returns:

```
content_markdown: "[full page content in markdown]",
meta_title: "[title tag]",
meta_description: "[meta description]",
h1: "[H1 heading]",
faq_section: "[FAQ markdown]",
schema_json_ld: "[JSON-LD schema markup]",
external_links: [{url, anchor_text, placement}],
image_prompts: [{section, description}],
word_count: [actual count],
passes_completed: 8
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/references/8-pass-writing-engine.md
git commit -m "feat(gmb-hub): add 8-pass human-like writing engine reference"
```

---

## Task 9: Reference — Content Guardrails (4 files)

**Files:**
- Create: `plugins/lhm-gmb-hub/references/content-guardrails/service-page.md`
- Create: `plugins/lhm-gmb-hub/references/content-guardrails/category-page.md`
- Create: `plugins/lhm-gmb-hub/references/content-guardrails/location-page.md`
- Create: `plugins/lhm-gmb-hub/references/content-guardrails/supporting-content.md`

- [ ] **Step 1: Write service-page guardrails**

Write to `plugins/lhm-gmb-hub/references/content-guardrails/service-page.md`:

```markdown
# Content Guardrails: Service Pages

Load these guardrails before EVERY pass of the 8-pass writing engine when producing service page content.

## Purpose

Service pages target the "Who can do this for me?" searcher. These people have a problem and want to find someone to solve it. They are NOT looking for information about how to solve it themselves.

## Mandatory Elements

1. **Action-first opening** — The first paragraph addresses the user's immediate problem. NOT how long the practice has been running, NOT their credentials. The problem.

2. **Why the customer needs this service** — Address the specific situation that brings someone to search for this. Be concrete, not generic.

3. **What exactly the service includes** — Specific steps of the treatment/service process. Not vague descriptions. Walk the reader through what happens when they come in.

4. **How long the process takes** — Session duration, number of typical sessions, what to expect on the first visit.

5. **What to expect during and after** — Remove uncertainty. The reader should feel like they know exactly what will happen.

6. **Clear CTAs** — Click to Call, Get Directions, Book Online. Google tracks these actions via Chrome and Android as goal completion signals. Include the phone number in the content at least twice.

7. **Entities from the entity map** — Woven in naturally, not forced. These are the expert-level terms that signal genuine authority to Google.

8. **Service Schema markup** — Generated as part of the parallel steps.

## Do NOT Include

- Informational "how to" content (save for FAQ pages)
- Long histories of the practice or modality
- Generic advice the reader could find anywhere
- Walls of text without images, callouts, or formatting breaks

## Voice and Tone

- Confident but not arrogant
- Specific and practical
- Written for someone in mild distress or urgency (they have a problem)
- Local: mention the suburb, nearby landmarks, driving routes where natural
- Use "you" and "your" throughout

## Formatting

- Short paragraphs (2-4 sentences max)
- Images or image placeholders between sections
- Callout boxes for key information (hours, phone, address)
- Tables where comparison or process information helps
- Bullet points for lists of services or steps
- No walls of text

## SEO Requirements

- Title tag: [Service] [City] | [Brand Name]
- H1: [Service] [City] or natural variation
- URL: /[service]-[city]/
- Target word count: 1,500-2,500 words
```

- [ ] **Step 2: Write category-page guardrails**

Write to `plugins/lhm-gmb-hub/references/content-guardrails/category-page.md`:

```markdown
# Content Guardrails: Category Pages

Load these guardrails before EVERY pass of the 8-pass writing engine when producing category page content.

## Purpose

Category pages are hub pages that link to child service pages. They establish topical authority for a broader modality (e.g. "Physiotherapy" as a category linking to specific service pages like "Sports Physiotherapy", "Dry Needling", "Post-Surgery Rehab").

## Mandatory Elements

1. **Overview of the modality/category** — What this area of practice covers, who it helps, what conditions it addresses
2. **Editorial links to ALL child service pages** — Within paragraph text, not just a list. Each link uses natural anchor text including the service keyword.
3. **Brief descriptions of each child service** — 2-3 sentences per child service explaining what it is and who it's for, with the editorial link embedded
4. **Local context** — Mention the location, the community served
5. **CTA** — General booking/contact CTA appropriate for someone still exploring options

## Do NOT Include

- Detailed treatment information (that belongs on the child service pages)
- Duplicate content from child service pages
- Navigation-style link lists without editorial context

## Internal Linking Rule

Links to child service pages MUST be editorial links within paragraph body content. NOT lists. NOT navigation. Google treats links within paragraphs as authority signals; navigation and lists are treated as site structure only.

## SEO Requirements

- Title tag: [Category] [City] | [Brand Name]
- H1: [Category] [City] or natural variation
- Target word count: 1,000-1,800 words
```

- [ ] **Step 3: Write location-page guardrails**

Write to `plugins/lhm-gmb-hub/references/content-guardrails/location-page.md`:

```markdown
# Content Guardrails: Location / Neighbourhood Overlay Pages

Load these guardrails before EVERY pass of the 8-pass writing engine when producing location or neighbourhood overlay page content.

## Purpose

Location pages target proximity-based searches like "[Service] near [Landmark]" or "[Service] [Suburb]". They exist to capture rankings in areas where the business is visible but not yet in the top 3 (yellow pins on the Local Falcon grid).

## Critical Rule

This is NOT a service page with a swapped suburb name. Google penalises thin location pages that are just templates with find-and-replace city names. The content must be genuinely local.

## Mandatory Elements

1. **Hyper-local opening** — Reference the specific neighbourhood, suburb, or landmark. What is it like? What kind of people live/work there?
2. **Neighbourhood-specific demographics** — Population, typical residents, relevant community characteristics
3. **Localised service issues** — Problems specific to this area (e.g. old housing stock causing plumbing issues, coastal weather affecting joints, high-density living causing noise-related stress)
4. **Driving routes and proximity** — How to get from this neighbourhood to the practice. Specific roads, travel time, parking information
5. **Nearby landmarks** — Reference Google Maps-recognised landmarks near the business location
6. **Service connection** — How the service specifically helps people in this neighbourhood
7. **Link back to parent service page** — Editorial link within the content

## Do NOT Include

- Generic service descriptions that could apply to any location
- Copy-paste content with only the suburb name changed
- Fake local details that could be easily debunked

## Voice and Tone

- Written as if the author lives and works in this area
- Conversational references to local features ("just past the [landmark]", "if you're coming from [road]")
- Specific and verifiable local details

## SEO Requirements

- Title tag: [Service] near [Landmark/Suburb] in [City] | [Brand Name]
- H1: Natural variation of the title tag
- Target word count: 800-1,500 words
- Target keyword: [Service] near [Landmark] in [City]
```

- [ ] **Step 4: Write supporting-content guardrails**

Write to `plugins/lhm-gmb-hub/references/content-guardrails/supporting-content.md`:

```markdown
# Content Guardrails: Supporting Content (FAQ Pages)

Load these guardrails before EVERY pass of the 8-pass writing engine when producing FAQ or supporting content.

## Purpose

Supporting content pages answer specific questions that real people ask about a service. They strengthen the parent service page's topical authority by covering related questions in depth. They live within the site structure (linked from the parent service page), NOT in a blog feed.

## Critical Rule

These are NOT traditional blog posts. They don't go in a /blog/ directory. They are transactional/informational support pages that directly serve the parent service page. They should be linked from the parent service page (brief answer + "read more" editorial link) and they should link back to the parent service page.

## Mandatory Elements

1. **Clear, specific question as the topic** — Reworded from PAA or Reddit (not copied verbatim from People Also Ask to avoid duplication flags)
2. **Comprehensive answer** — 400-800 words. Address the actual question directly in the first paragraph, then go deeper.
3. **Local context where relevant** — Mention the city, local conditions, local pricing norms, anything that makes the answer specific to this market
4. **Entities from the entity map** — Expert-level terminology woven naturally
5. **Link back to parent service page** — Editorial link with service-keyword anchor text
6. **Brief answer text for the parent page** — 2-3 sentences that summarise the answer, to be added to the parent service page with an editorial link to this page

## Do NOT Include

- Generic advice available on WebMD or the first Google result
- Overly technical content that only practitioners would read
- Self-promotional content disguised as an FAQ answer

## Voice and Tone

- Helpful and authoritative
- Written for someone with the problem, not a fellow practitioner
- Conversational but informative
- Local where possible

## SEO Requirements

- Title tag: [Question rephrased as statement] | [Brand Name]
- H1: The question itself (or natural variation)
- Target word count: 400-800 words
- FAQ schema markup for the main question + answer
```

- [ ] **Step 5: Commit all guardrails**

```bash
git add plugins/lhm-gmb-hub/references/content-guardrails/
git commit -m "feat(gmb-hub): add content guardrails for 4 content types"
```

---

## Task 10: Skill — gmb-project-manager

**Files:**
- Create: `plugins/lhm-gmb-hub/skills/gmb-project-manager/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Write to `plugins/lhm-gmb-hub/skills/gmb-project-manager/SKILL.md`:

```markdown
---
name: gmb-project-manager
description: "Read, create, or update the GMBProjectManagement.md file for a client. Use this when the user mentions 'GMB status', 'where are we at with GMB', 'update GMB project', 'update rankings', 'GMB progress', 'what's left to do', 'mark as done', or wants to check or modify the project tracking document. Also used internally by all agents after completing tasks."
---

# GMB Project Manager

Manages the per-client `GMBProjectManagement.md` file which tracks the full state of a client's GMB optimisation: current cycle, phase, task completion, focus keywords, and ranking history.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gmb-project-manager/LEARNED.md`
2. Identify the client (ask if not clear from context)
3. Locate the client folder

## Workflow

### 1. Check If Project Doc Exists

Look for `[client_folder]/gmb/GMBProjectManagement.md`.

**If it does NOT exist:** Create the `gmb/` directory and a new `GMBProjectManagement.md` using the template below. Populate the Overview section from `client_profile.md`. Set Current Phase to "Month 0 — Onboarding". Ask the user for the 7 focus keywords (or suggest them based on the client profile).

**If it DOES exist:** Read it and proceed to step 2.

### 2. Present Status Summary

Display a concise summary:

```
Client: [Name]
Current Phase: [Phase]
Cycle: [N] ([date range])

Completed: X/Y tasks in current phase
[List completed tasks with ✅]
[List outstanding tasks with ⬜]

Suggested next: [Next incomplete task]
```

### 3. Handle User Request

The user may want to:

**View status** — Display the summary above. No changes needed.

**Update rankings** — Use `AskUserQuestion` to ask:
- "Would you like to supply the latest rankings manually, or should I pull them from GSC/Local Falcon?"
- If manual: ask for each keyword's current position and Top3% metric
- If auto-pull: attempt to use GSC MCP and Local Falcon MCP. Fall back to manual if unavailable.
- Update the ranking history table in the project doc

**Mark tasks complete** — Mark specific tasks as `[x]` with today's date. Expand sub-tasks if needed (e.g. list each service page individually).

**Add notes** — Append to the Notes & Decisions section with today's date.

**Start new cycle** — Append a new `## 3-Month Cycle N` section with fresh Month 0-3 tasks. The re-cycle Month 0 is lighter (only diagnostic + service selection, not full GBP optimisation).

**Check exit criteria** — Review all tasks in the current phase. Report which are complete and which are outstanding. Only mark exit criteria as met if ALL tasks are done.

### 4. Save Changes

Write the updated `GMBProjectManagement.md` back to the client folder. Confirm to the user what was changed.

## GMBProjectManagement.md Template

When creating a new project doc, use this structure:

```markdown
# GMB Project Management — [Client Name]

## Overview
- **Client:** [Name]
- **Primary Location:** [Address]
- **Primary Modality:** [e.g. Physiotherapy]
- **Last Updated:** [Today's date]

## Focus Keywords & Ranking History

| Keyword | Cycle 1 M0 | Cycle 1 M1 | Cycle 1 M2 | Cycle 1 M3 |
|---------|-----------|-----------|-----------|-----------|
| [Keyword 1] | — | — | — | — |
| [Keyword 2] | — | — | — | — |
| [Keyword 3] | — | — | — | — |
| [Keyword 4] | — | — | — | — |
| [Keyword 5] | — | — | — | — |
| [Keyword 6] | — | — | — | — |
| [Keyword 7] | — | — | — | — |

---

## 3-Month Cycle 1 — [Start Month Year] to [End Month Year]

### Cycle Focus
- **Priority Services:** (to be determined during Month 0)
- **Selection Reasoning:** —
- **Approved by:** —
- **Diagnostic Direction:** —
- **Threshold:** —

### Month 0 — Onboarding ([Month Year])

#### Tasks
- [ ] Run baseline diagnostic
- [ ] Competitor audit (3 competitors)
- [ ] GBP categories optimised (up to 10)
- [ ] GBP services listed (30+)
- [ ] 750-char business description written
- [ ] All GBP profile fields completed
- [ ] 52 weekly GBP posts generated
- [ ] Citation audit completed
- [ ] Entity mapping completed
- [ ] Site architecture mapped
- [ ] **Exit criteria met**

### Month 1 — Service Pages ([Month Year])

#### Tasks
- [ ] Homepage consistency signal audit
- [ ] Service page: [Service 1]
- [ ] Service page: [Service 2]
- [ ] Service page: [Service 3]
- [ ] Technical audit: all service pages
- [ ] Pages submitted to GSC
- [ ] Month 1 report generated
- [ ] **Exit criteria met**

### Month 2 — Content Expansion ([Month Year])

#### Tasks
- [ ] Diagnostic re-run (compare to baseline)
- [ ] Content direction decided (FAQ vs overlay vs mixed)
- [ ] Supporting content for [Service 1] (X pages)
- [ ] Supporting content for [Service 2] (X pages)
- [ ] Supporting content for [Service 3] (X pages)
- [ ] Month 2 report generated
- [ ] **Exit criteria met**

### Month 3 — Link Building ([Month Year])

#### Tasks
- [ ] Link gap audit completed
- [ ] "Not AI slop" links: [Service 1] page
- [ ] "Not AI slop" links: [Service 2] page
- [ ] "Not AI slop" links: [Service 3] page
- [ ] Local authority opportunities identified
- [ ] Chamber of Commerce outreach (target: 2-5)
- [ ] Sponsorship outreach (target: 2-4)
- [ ] PR brief generated (if applicable)
- [ ] Month 3 / full cycle report generated
- [ ] **Exit criteria met**

---

## Notes & Decisions
```

## Output

- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Creates the file and `gmb/` directory if they don't exist
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/skills/gmb-project-manager/
git commit -m "feat(gmb-hub): add gmb-project-manager skill"
```

---

## Tasks 11-26: All Remaining Skills

Due to the size of this plan, the remaining 16 skills follow the same pattern as Task 10. Each task creates a SKILL.md for one skill. The skills are grouped below by phase with their key characteristics. Each SKILL.md must follow the exact same structure: YAML frontmatter (name + description with trigger phrases), sections for Before Starting, Workflow (numbered steps), MCP dependencies with fallbacks, and Output.

### Task 11: Skill — run-local-diagnostic

**File:** `plugins/lhm-gmb-hub/skills/run-local-diagnostic/SKILL.md`

**Key characteristics:**
- Trigger: "run a local diagnostic for [Client]", "local diagnostic", "grid scan", "baseline diagnostic", "re-run diagnostic"
- MCPs: Local Falcon (primary), GSC, Keywords Everywhere. Fallback: manual scan results
- Before Starting: Read LEARNED.md, read client_profile.md, check if this is Month 0 (baseline) or Month 2 (re-run)
- Workflow:
  1. Determine if baseline or re-run (check GMBProjectManagement.md)
  2. Run 169-point grid scan for primary keyword via Local Falcon MCP (or ask user to paste results)
  3. Record Top 3% metric, colour breakdown (green/yellow/red)
  4. Identify where authority "falls off the cliff" on the map
  5. Run competitor audit: Google primary keyword, identify top 3 competitors, run site:domain for each to count indexed pages
  6. Calculate threshold: 25-50% of top competitor's Top 3% score
  7. Determine direction: below threshold = topical relevance problem, at/above = proximity problem
  8. If re-run: compare against previous diagnostic, show trend
  9. Save diagnostic report
  10. Update GMBProjectManagement.md (rankings, threshold decision, diagnostic direction)
- Output: `onboarding/diagnostic_report.md` (Month 0) or `monthly-optimization/YYYY-MM/diagnostic_rerun.md` (Month 2)

### Task 12: Skill — gbp-optimiser

**File:** `plugins/lhm-gmb-hub/skills/gbp-optimiser/SKILL.md`

**Key characteristics:**
- Trigger: "optimise GBP for [Client]", "GBP optimisation", "Google Business Profile", "optimise the profile", "GBP categories", "GBP services"
- MCPs: DataForSEO, Keywords Everywhere. Fallback: web search for competitor categories
- Workflow:
  1. Read client_profile.md for current business details
  2. Research competitor GBP categories (top 3 competitors, what categories they use)
  3. Recommend up to 10 categories
  4. Generate 30+ specific service listings with descriptions (not broad categories)
  5. Write 750-character business description (use FULL 750 characters)
  6. Generate profile completion checklist (business name, categories, services, description, attributes, address, phone, hours, photos, logo)
  7. Flag any NAP inconsistencies between website and GBP
  8. Present plan to user for review
  9. Update GMBProjectManagement.md
- Output: `onboarding/gbp_optimisation_plan.md`
- Note: Changes must be manually applied in GBP dashboard. Skill generates the plan only.

### Task 13: Skill — gbp-post-generator

**File:** `plugins/lhm-gmb-hub/skills/gbp-post-generator/SKILL.md`

**Key characteristics:**
- Trigger: "generate 52 GBP posts for [Client]", "GBP posts", "weekly posts", "Google Business posts"
- MCPs: None required
- Workflow:
  1. Read client_profile.md for services, modality, brand voice
  2. Generate 52 weekly posts rotating between: service highlights, tips, seasonal content, team spotlights
  3. Each post: 150-300 words, AHPRA compliant, follows anti-AI writing guidelines
  4. Output as CSV with columns: Week Number, Post Date, Post Type, Post Content, CTA Link
  5. Present first 4 posts for user review before generating all 52
  6. Update GMBProjectManagement.md
- Output: `onboarding/gbp_posts_52_weeks.csv`
- Note: Posts need human review for brand voice before scheduling

### Task 14: Skill — citation-audit

**File:** `plugins/lhm-gmb-hub/skills/citation-audit/SKILL.md`

**Key characteristics:**
- Trigger: "run a citation audit for [Client]", "citation audit", "directory check", "NAP check", "citations"
- MCPs: None required (web search)
- Workflow:
  1. Read client_profile.md for NAP details (name, address, phone)
  2. Search each major directory for existing listings: Apple Maps, Bing Places, Yelp, True Local, Hotfrog, Yellow Pages Australia
  3. Also search industry-specific directories for the client's modality
  4. For each directory: check if listing exists, check NAP matches exactly, flag inconsistencies
  5. Generate action plan: which directories need new submissions, which need corrections
  6. Update GMBProjectManagement.md (list each directory with status)
- Output: `onboarding/citation_audit.md`
- Note: Manual submission/correction still required. Skill identifies what needs doing.

### Task 15: Skill — entity-mapper

**File:** `plugins/lhm-gmb-hub/skills/entity-mapper/SKILL.md`

**Key characteristics:**
- Trigger: "run entity mapping for [Client]", "entity mapping", "entity map", "extract entities"
- MCPs: DataForSEO, GSC, Keywords Everywhere. Fallback: web search for competitor content
- Workflow:
  1. Read client_profile.md and diagnostic_report.md (for competitors)
  2. Identify top 3 ranking competitors for primary keyword
  3. Fetch content from their top-ranking service pages
  4. Extract entities, concepts, and technical terms that prove expertise (not keywords, but the concepts Google associates with a genuine expert in this modality)
  5. Organise into categories: medical/technical terms, equipment/tools, conditions treated, treatment approaches, anatomy references
  6. Cross-reference with client's existing content to identify entity gaps
  7. Save structured entity map
  8. Update GMBProjectManagement.md
- Output: `onboarding/entity_map.md`
- Note: Entity map is referenced automatically by all content-producing skills

### Task 16: Skill — site-architecture-mapper

**File:** `plugins/lhm-gmb-hub/skills/site-architecture-mapper/SKILL.md`

**Key characteristics:**
- Trigger: "map the site architecture for [Client]", "site architecture", "silo structure", "site map", "page hierarchy"
- MCPs: None required
- Workflow:
  1. Read client_profile.md and gbp_optimisation_plan.md (for GBP categories and services)
  2. Generate siloed hierarchy mirroring GBP structure:
     - Homepage (GBP landing page) links to category pages
     - Category pages (one per GBP category) link to child service pages
     - Service pages (one per specific service) linked from parent category
  3. Map internal linking structure (editorial links within paragraph text, not just nav)
  4. Identify which pages already exist vs need to be created
  5. Handle multi-location: if client has 2+ locations, each gets its own location page as GBP landing page
  6. Present architecture for user review
  7. Update GMBProjectManagement.md
- Output: `onboarding/site_architecture.md`

### Task 17: Skill — service-priority-selector

**File:** `plugins/lhm-gmb-hub/skills/service-priority-selector/SKILL.md`

**Key characteristics:**
- Trigger: "select priority services for [Client] this cycle", "pick services", "which services should we focus on", "service priorities", "priority selection"
- MCPs: Local Falcon, GSC, GA4, Keywords Everywhere. Fallback: manual ranking input
- Workflow:
  1. Read client_profile.md and most recent diagnostic report
  2. Ask user via AskUserQuestion: "Would you like to supply current rankings, or should I pull from GSC/Local Falcon?"
  3. Get current rankings for all client's service keywords
  4. Cross-reference with search volume and competition data
  5. Apply the decision framework from gmb-ranking-principles.md:
     - Not ranking #1 for primary modality? → primary modality + 2 sub-services
     - Ranking #1 locally? → 2-3 sub-services not ranking for yet
     - Ranking well locally, wants surrounding suburbs? → primary modality + location combos
     - Multi-modality? → strongest revenue modality first, then next 2
  6. Present top 3 recommendation with reasoning
  7. Remind user: "Confirm with Michael before proceeding"
  8. Once approved, update GMBProjectManagement.md (Cycle Focus section + priority services)
- Output: `monthly-optimization/YYYY-MM/service_priorities.md`

### Task 18: Skill — consistency-signal-audit

**File:** `plugins/lhm-gmb-hub/skills/consistency-signal-audit/SKILL.md`

**Key characteristics:**
- Trigger: "audit consistency signals for [Client]", "homepage audit", "consistency signals", "8 signals check", "NAP consistency"
- MCPs: GSC, web fetch
- Workflow:
  1. Read client_profile.md for GBP data (business name, address, phone, categories)
  2. Check if single or multi-location (from client profile)
  3. For single location: audit the homepage. For multi-location: audit each location page individually
  4. Check all 8 consistency signals:
     - Title tag: Primary category + city name
     - H1: Primary category + city name (matches title intent)
     - Google Maps embed: functional embed of specific GBP location
     - Secondary categories: mentioned as H2s or in body content
     - Review widget: displaying actual Google reviews
     - Address: matches GBP character-for-character
     - Phone number: matches GBP character-for-character
     - Local Business Schema: implemented and validated
  5. Generate pass/fail report for each signal
  6. For multi-location: check that each GBP's website URL points to its specific location page (not homepage)
  7. Update GMBProjectManagement.md (expand sub-tasks for each signal)
- Output: `monthly-optimization/YYYY-MM/consistency_audit.md`

### Task 19: Skill — service-page-writer

**File:** `plugins/lhm-gmb-hub/skills/service-page-writer/SKILL.md`

**Key characteristics:**
- Trigger: "write service page content for [Service] for [Client]", "write service page", "create service page", "service page for [topic]"
- MCPs: Keywords Everywhere, web search
- Workflow:
  1. Read client_profile.md, entity_map.md, service_priorities.md
  2. Research phase: analyse top competitor service pages for this keyword, collect PAA questions, gather local context
  3. Build structured brief for the content-writer agent
  4. Hand off to content-writer agent with content_type "service-page"
  5. Content-writer runs 8-pass pipeline and returns finished content
  6. Run AHPRA compliance check (if healthcare client)
  7. Generate internal linking instructions (what to add to homepage and category page)
  8. Present content to user for review
  9. Update GMBProjectManagement.md (mark service page task complete)
- Output: `monthly-optimization/YYYY-MM/[service-slug].md`
- Note: Hands off actual writing to content-writer agent. This skill handles research and context.

### Task 20: Skill — technical-page-audit

**File:** `plugins/lhm-gmb-hub/skills/technical-page-audit/SKILL.md`

**Key characteristics:**
- Trigger: "run a technical audit on [URL]", "technical audit", "check page technical", "schema check", "indexing check"
- MCPs: GSC, web fetch
- Workflow:
  1. Fetch the live page URL
  2. Check each technical requirement:
     - Service Schema present on service pages (or LocalBusiness on location pages)
     - Schema validates without errors
     - No broken internal links on the page
     - Page indexed in GSC (check indexing status)
     - Page loads in under 3 seconds
     - Mobile responsive
     - Sitemap is up to date and includes this page
  3. Generate pass/fail checklist
  4. If page not indexed: submit for indexing via GSC MCP
  5. Update GMBProjectManagement.md
- Output: `monthly-optimization/YYYY-MM/technical_audit.md`

### Task 21: Skill — faq-content-builder

**File:** `plugins/lhm-gmb-hub/skills/faq-content-builder/SKILL.md`

**Key characteristics:**
- Trigger: "build FAQ content for [Service] for [Client]", "FAQ pages", "supporting content", "PAA content", "build FAQs"
- MCPs: Keywords Everywhere, web search
- Workflow:
  1. Read client_profile.md, entity_map.md
  2. Question discovery: Google the service keyword (without location), expand People Also Ask, collect 20-30 questions
  3. Search local Reddit threads for real questions people ask about this service in the client's area
  4. Reword all questions (change phrasing/word order to avoid PAA duplication flags)
  5. Prioritise questions by search volume and relevance
  6. Present top 6-10 questions to user, ask which 2-4 to build pages for
  7. For each selected question: build structured brief, hand off to content-writer agent with content_type "supporting-content"
  8. For each page: also generate the brief answer + editorial link text to add to parent service page
  9. Update GMBProjectManagement.md (list each FAQ page as a sub-task)
- Output: `monthly-optimization/YYYY-MM/faq-[question-slug].md` (one per page)

### Task 22: Skill — neighbourhood-overlay-writer

**File:** `plugins/lhm-gmb-hub/skills/neighbourhood-overlay-writer/SKILL.md`

**Key characteristics:**
- Trigger: "write neighbourhood overlay pages for [Service] for [Client]", "overlay pages", "geo pages", "location pages", "neighbourhood pages"
- MCPs: Local Falcon, Keywords Everywhere. Fallback: manual grid point identification
- Workflow:
  1. Read client_profile.md, entity_map.md
  2. Get Local Falcon scan report for the service keyword (or ask user to identify yellow grid points)
  3. Focus on the "4-5-6 rule": positions 4-6 are easiest to push into top 3
  4. Identify Google Maps landmarks near yellow dots: suburbs, parks, shopping centres, schools, major intersections
  5. Suggest 10-20 potential overlay targets
  6. Present to user, ask which 3-5 to build pages for
  7. For each selected target: research local area (demographics, local conditions, driving routes), build brief, hand off to content-writer with content_type "location-page"
  8. Generate internal linking instructions: add each page to "Areas We Serve" page, link back to parent service page
  9. Update GMBProjectManagement.md
- Output: `monthly-optimization/YYYY-MM/[service]-near-[landmark].md` (one per page)

### Task 23: Skill — link-gap-finder

**File:** `plugins/lhm-gmb-hub/skills/link-gap-finder/SKILL.md`

**Key characteristics:**
- Trigger: "find pages missing external links for [Client]", "link gap", "pages without links", "link audit", "backlink gap"
- MCPs: DataForSEO (backlinks), Screaming Frog, GSC. Fallback: GSC external links report + site: search
- Workflow:
  1. Read client_profile.md
  2. Get full page list: crawl sitemap via Screaming Frog MCP, or run site:domain search, or use GSC indexed pages
  3. Pull backlink data per page from DataForSEO (or GSC external links report)
  4. Identify pages with zero or insufficient external links
  5. Prioritise: service pages first, then FAQ/supporting pages, then geo pages
  6. Generate tracking spreadsheet template: Page URL, Link Source, Link Type, Date Acquired, Status
  7. Update GMBProjectManagement.md
- Output: `monthly-optimization/YYYY-MM/link_gap_report.md` + `monthly-optimization/YYYY-MM/link_tracking.csv`

### Task 24: Skill — local-authority-finder

**File:** `plugins/lhm-gmb-hub/skills/local-authority-finder/SKILL.md`

**Key characteristics:**
- Trigger: "find local authority link opportunities for [Client]", "chamber of commerce", "sponsorship links", "local links", "authority links"
- MCPs: None required (web search)
- Workflow:
  1. Read client_profile.md for business address and modality
  2. Search for Chambers of Commerce within 70-80km radius (include small suburban chambers)
  3. Search for local sponsorship opportunities: youth sports leagues, local charities, community events, schools/colleges (potential .edu links), TEDx
  4. For each opportunity: estimate cost, identify contact method, assess link value
  5. Prioritise by link value (.edu and chambers at top) and cost efficiency
  6. Generate outreach plan with contact details where available
  7. Budget guidance: chambers ~$200-300 each (aim 2-5), sponsorships ~$100-500 each (aim 2-4)
  8. Update GMBProjectManagement.md
- Output: `monthly-optimization/YYYY-MM/local_authority_opportunities.md`
- Note: Outreach and sign-ups are manual. Skill finds opportunities and builds the plan.

### Task 25: Skill — pr-brief-generator

**File:** `plugins/lhm-gmb-hub/skills/pr-brief-generator/SKILL.md`

**Key characteristics:**
- Trigger: "generate a PR brief for [Client] targeting [Keyword]", "PR brief", "press release", "Signal Genesis"
- MCPs: None required (web search)
- Workflow:
  1. Read client_profile.md and service_priorities.md
  2. Identify potential newsworthy angles: new service launch, expansion, community involvement, milestone, award
  3. If no clear angle exists, tell the user: "No strong newsworthy angle found. PR is optional this cycle. Skip, or would you like to brainstorm an angle?"
  4. Write press release draft following Signal Genesis formatting
  5. Specify target link URLs: primary service page URL + GBP listing URL
  6. AHPRA compliance check for healthcare clients
  7. Present draft to user for review
  8. Update GMBProjectManagement.md
- Output: `monthly-optimization/YYYY-MM/press_release.md`
- Note: Optional. Only for clients on plans that include PR distribution.

### Task 26: Skill — monthly-cycle-report

**File:** `plugins/lhm-gmb-hub/skills/monthly-cycle-report/SKILL.md`

**Key characteristics:**
- Trigger: "generate month [1/2/3] report for [Client]", "monthly report", "cycle report", "end of month report"
- MCPs: Local Falcon, GSC, GA4, Keywords Everywhere. Fallback: manual Local Falcon data
- Workflow:
  1. Read GMBProjectManagement.md to determine which month of the cycle this is
  2. Ask user via AskUserQuestion: "Supply rankings manually or pull from GSC/Local Falcon?"
  3. Pull GSC data: impressions, clicks, average position for priority service keywords
  4. Pull GA4 data: page-level traffic and conversions for optimised pages
  5. Compare against baseline (from diagnostic report)
  6. Adapt report format based on month:
     - **Month 1:** Focus on service page optimisation results. Top 3% trend (M0 vs M1). Pages optimised with URLs. What was changed. Next month preview.
     - **Month 2:** Focus on content expansion results. Top 3% trend (M0→M1→M2). New pages created and purpose. Link building queue for Month 3. Diagnostic direction update.
     - **Month 3 / End of Cycle:** Full cycle summary. Top 3% trend across all 4 months. All pages created/optimised. All links acquired. Recommendations for next cycle's 3 priority services.
  7. Update GMBProjectManagement.md (rankings + Cycle Summary section for Month 3)
- Output: `monthly-optimization/YYYY-MM/month_N_report.md`

**For each of Tasks 11-26:**

- [ ] **Step 1: Write the SKILL.md** following the structure described above
- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/skills/[skill-name]/
git commit -m "feat(gmb-hub): add [skill-name] skill"
```

---

## Task 27: Agent — gmb-orchestrator

**Files:**
- Create: `plugins/lhm-gmb-hub/agents/gmb-orchestrator.md`

- [ ] **Step 1: Write gmb-orchestrator.md**

Write to `plugins/lhm-gmb-hub/agents/gmb-orchestrator.md`:

```markdown
---
name: gmb-orchestrator
description: "Main entry point for GMB optimisation work. Use this agent when the user wants to work on GMB for a client, continue GMB work, check GMB status, asks 'where are we at with GMB', mentions 'GMB optimisation', 'Google Business Profile', 'local SEO cycle', or 'GMB project'. This agent detects the current phase, routes to the correct phase agent, and manages approval gates between phases."
---

# GMB Orchestrator

You are the master orchestrator for the GMB 3-Month Ranking Flow. Your job is to detect where a client is in their optimisation cycle and route to the right phase agent.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gmb-project-manager/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/gmb-ranking-principles.md`

## Step 1: Identify the Client

Ask the user which client they want to work on if not clear from context. Locate the client folder.

## Step 2: Load Project State

Read `[client_folder]/gmb/GMBProjectManagement.md`.

**If the file does NOT exist:**
- Tell the user: "This client hasn't been onboarded for GMB yet. I'll set up the project and start Month 0."
- Load the gmb-project-manager skill to create the project doc: `${CLAUDE_PLUGIN_ROOT}/skills/gmb-project-manager/SKILL.md`
- Then route to the onboarding-agent

**If the file DOES exist:**
- Parse the current cycle, current phase, and task completion status
- Continue to Step 3

## Step 3: Present Status Summary

Display:

```
Client: [Name]
Current Phase: [Phase name and month]
Cycle: [N] ([date range])

Progress: X/Y tasks complete
✅ [Completed tasks]
⬜ [Outstanding tasks]

Suggested next: [First outstanding task]
```

## Step 4: Route to Phase Agent

Based on the project state:

| Condition | Route To |
|-----------|----------|
| Month 0 incomplete | Load `${CLAUDE_PLUGIN_ROOT}/agents/onboarding-agent.md` |
| Month 0 complete, Month 1 incomplete | Load `${CLAUDE_PLUGIN_ROOT}/agents/service-optimizer-agent.md` |
| Month 1 complete, Month 2 incomplete | Load `${CLAUDE_PLUGIN_ROOT}/agents/content-expansion-agent.md` |
| Month 2 complete, Month 3 incomplete | Load `${CLAUDE_PLUGIN_ROOT}/agents/link-building-agent.md` |
| Month 3 complete (cycle done) | Ask: "Cycle complete. Start a new 3-month cycle?" If yes, use gmb-project-manager to create new cycle, then route to onboarding-agent |

**Before routing:** Ask the user if they want to proceed with the suggested task, or if they want to work on something specific. Respect user choice.

## Step 5: Phase Transition Gates

When a phase agent reports all tasks complete:
1. Run exit criteria check (verify all tasks in the phase are marked done)
2. If exit criteria met: prompt "Month [N] is complete. Ready to move to Month [N+1]?"
3. Only advance to next phase after user confirmation
4. Update GMBProjectManagement.md with phase completion

## Skill Catalog

All available skills in this plugin:

| Skill | Trigger | Phase |
|-------|---------|-------|
| `gmb-project-manager` | "GMB status", "update rankings" | Any |
| `run-local-diagnostic` | "Run diagnostic for [Client]" | 0, 2 |
| `gbp-optimiser` | "Optimise GBP for [Client]" | 0 |
| `gbp-post-generator` | "Generate 52 GBP posts" | 0 |
| `citation-audit` | "Citation audit for [Client]" | 0 |
| `entity-mapper` | "Entity mapping for [Client]" | 0 |
| `site-architecture-mapper` | "Map site architecture" | 0 |
| `service-priority-selector` | "Select priority services" | 1 (start) |
| `consistency-signal-audit` | "Audit consistency signals" | 1 |
| `service-page-writer` | "Write service page for [Service]" | 1 |
| `technical-page-audit` | "Technical audit on [URL]" | 1 |
| `faq-content-builder` | "Build FAQ content for [Service]" | 2 |
| `neighbourhood-overlay-writer` | "Write overlay pages for [Service]" | 2 |
| `link-gap-finder` | "Find pages missing links" | 3 |
| `local-authority-finder` | "Find local authority links" | 3 |
| `pr-brief-generator` | "Generate PR brief" | 3 |
| `monthly-cycle-report` | "Generate month [N] report" | 1, 2, 3 |

## Important Rules

1. **Never auto-execute skills silently.** Always present the next task and get user confirmation before running a skill.
2. **Respect user choices.** If the user wants to skip a task or work on something out of order, allow it.
3. **Always update the project doc.** After any skill completes, ensure GMBProjectManagement.md is updated.
4. **Check exit criteria before advancing phases.** Don't move to Month 1 if Month 0 tasks are incomplete.
5. **For re-cycles (Cycle 2+):** Month 0 is lighter. Only diagnostic + service selection. Don't re-run GBP optimisation, citations, entity mapping, site architecture, or post generation unless specifically requested.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/gmb-orchestrator.md
git commit -m "feat(gmb-hub): add gmb-orchestrator master agent"
```

---

## Task 28: Agent — onboarding-agent

**File:** `plugins/lhm-gmb-hub/agents/onboarding-agent.md`

- [ ] **Step 1: Write the agent**

Write to `plugins/lhm-gmb-hub/agents/onboarding-agent.md`:

```markdown
---
name: onboarding-agent
description: "Month 0 phase agent for GMB optimisation. Handles GBP foundation work: baseline diagnostic, GBP profile optimisation, post generation, citation sync, entity mapping, and site architecture. Use this when the gmb-orchestrator routes here because Month 0 is incomplete, or when a new client needs GMB onboarding."
---

# Onboarding Agent — Month 0

You manage the Month 0 (Onboarding & GBP Foundation) phase of the GMB 3-Month Ranking Flow.

## Before Starting

1. Read `[client_folder]/gmb/GMBProjectManagement.md` — check which Month 0 tasks are already complete
2. Read `[client_folder]/client_profile.md`
3. Determine if this is Cycle 1 (full onboarding) or a re-cycle (lighter Month 0)

## Re-Cycle Detection

If the project doc shows a previous completed cycle (e.g. "3-Month Cycle 1" with exit criteria met):
- This is a re-cycle. Month 0 only requires:
  1. Re-run diagnostic (run-local-diagnostic)
  2. Select new priority services (service-priority-selector)
- Skip: GBP optimisation, post generation, citation audit, entity mapping, site architecture
- Unless the user specifically requests re-running any of these

## Skill Execution Order (Cycle 1)

Present each skill to the user and get confirmation before running. Do not auto-execute.

1. **Baseline Diagnostic** — Load `${CLAUDE_PLUGIN_ROOT}/skills/run-local-diagnostic/SKILL.md`
   - Must be done first (provides baseline metrics for everything else)

2. **GBP Optimisation** — Load `${CLAUDE_PLUGIN_ROOT}/skills/gbp-optimiser/SKILL.md`
   - Depends on: client_profile.md
   - Outputs: gbp_optimisation_plan.md (needed by site-architecture-mapper)

3. **GBP Post Generation** — Load `${CLAUDE_PLUGIN_ROOT}/skills/gbp-post-generator/SKILL.md`
   - Can run in parallel with steps 4-6

4. **Citation Audit** — Load `${CLAUDE_PLUGIN_ROOT}/skills/citation-audit/SKILL.md`
   - Can run in parallel with steps 3, 5, 6

5. **Entity Mapping** — Load `${CLAUDE_PLUGIN_ROOT}/skills/entity-mapper/SKILL.md`
   - Depends on: diagnostic_report.md (for competitor identification)

6. **Site Architecture Mapping** — Load `${CLAUDE_PLUGIN_ROOT}/skills/site-architecture-mapper/SKILL.md`
   - Depends on: gbp_optimisation_plan.md (for GBP categories and services)

## After Each Skill

1. Confirm the skill completed successfully
2. Update GMBProjectManagement.md via gmb-project-manager skill
3. Present the next task and ask user to proceed

## Exit Criteria

Do NOT advance to Month 1 until ALL of these are complete:
- [ ] Baseline diagnostic saved with Top 3% metric
- [ ] Competitor audit complete (3 competitors)
- [ ] GBP fully optimised (all checklist items)
- [ ] 52 weekly posts generated
- [ ] Citation audit complete
- [ ] Entity map saved
- [ ] Site architecture mapped

When all tasks are done, mark "Exit criteria met" in the project doc and report back to the gmb-orchestrator.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/onboarding-agent.md
git commit -m "feat(gmb-hub): add onboarding-agent (Month 0)"
```

---

## Task 29: Agent — service-optimizer-agent

**File:** `plugins/lhm-gmb-hub/agents/service-optimizer-agent.md`

- [ ] **Step 1: Write the agent** following the same pattern as onboarding-agent but for Month 1. Skills in order: service-priority-selector, consistency-signal-audit, service-page-writer (x3, one per priority service), technical-page-audit, submit pages to GSC, monthly-cycle-report. Exit criteria: 3 services selected + approved, consistency signals passing, 3 service pages written, technical audit passing, pages submitted, report generated.

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/service-optimizer-agent.md
git commit -m "feat(gmb-hub): add service-optimizer-agent (Month 1)"
```

---

## Task 30: Agent — content-expansion-agent

**File:** `plugins/lhm-gmb-hub/agents/content-expansion-agent.md`

- [ ] **Step 1: Write the agent** for Month 2. Key behaviour: starts with run-local-diagnostic (re-run), then reads the threshold decision to determine path. Below threshold = faq-content-builder for each of 3 services. At/above threshold = neighbourhood-overlay-writer for each of 3 services. Mixed = split accordingly. Ends with monthly-cycle-report. Exit criteria: diagnostic re-run complete, direction decided, 6-12 supporting pages created, report generated.

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/content-expansion-agent.md
git commit -m "feat(gmb-hub): add content-expansion-agent (Month 2)"
```

---

## Task 31: Agent — link-building-agent

**File:** `plugins/lhm-gmb-hub/agents/link-building-agent.md`

- [ ] **Step 1: Write the agent** for Month 3. Skills in order: link-gap-finder, local-authority-finder, pr-brief-generator (optional), monthly-cycle-report (end-of-cycle version). Exit criteria: link gap audit complete, at least 1 link per service page, local authority opportunities identified + outreach started, cycle report generated with next-cycle recommendations.

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/link-building-agent.md
git commit -m "feat(gmb-hub): add link-building-agent (Month 3)"
```

---

## Task 32: Agent — content-writer

**File:** `plugins/lhm-gmb-hub/agents/content-writer.md`

- [ ] **Step 1: Write the content-writer agent**

Write to `plugins/lhm-gmb-hub/agents/content-writer.md`:

```markdown
---
name: content-writer
description: "8-pass human-like writing agent for all content production. Use this agent when any content-producing skill needs to generate long-form content. This agent implements the 8-pass writing pipeline: research synthesis, strategic outline, section drafts (independent calls), burstiness, perplexity injection, human bookends, conversion injection, and final QC. Called by service-page-writer, faq-content-builder, neighbourhood-overlay-writer, and any skill that produces page content."
---

# Content Writer Agent — 8-Pass Pipeline

You are the writing engine for the GMB Hub plugin. Content-producing skills gather research and build briefs; you turn those briefs into human-like content that passes AI detection, reads naturally, and converts.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md` — the full pipeline specification
2. Load the appropriate content guardrails based on content_type:
   - "service-page" → `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/service-page.md`
   - "category-page" → `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/category-page.md`
   - "location-page" → `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/location-page.md`
   - "supporting-content" → `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/supporting-content.md`
3. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
4. If the client is a healthcare provider, also read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`

## Input

The calling skill provides:
- `content_type`: which type of content to produce
- `structured_brief`: research data including target keyword, location, entities, PAA questions, competitor angles, local context
- `client_context`: business name, phone, address, brand voice notes
- `word_count_target`: target word count for this content type
- `ahpra_required`: whether AHPRA compliance is needed

## Execution

Follow the 8-pass-writing-engine.md specification exactly. Execute each pass in order:

1. **Pass 1: Research Synthesis** — Compress the raw research into a structured content brief (200-400 words)
2. **Pass 2: Strategic Outline** — Build the full page architecture with H2s, angles, and section goals
3. **Pass 3: Section Draft** — Write each H2 section with a SEPARATE, INDEPENDENT generation. Different prompt per section. This is the most important pass for creating natural tonal variation.
4. **Pass 4: Burstiness** — Vary sentence length and paragraph cadence throughout
5. **Pass 5: Perplexity Injection** — Replace AI-favourite words and patterns
6. **Pass 6: Human Bookends** — Rewrite first 2 and last 2 sentences with conversational, opinionated language
7. **Pass 7: Conversion Injection** — Add natural CTAs appropriate to the content type
8. **Pass 8: Final QC** — Check cohesion, brief adherence, word count, AI patterns, AHPRA compliance

## Parallel Steps

Generate alongside Pass 8:
- Meta title, description, H1 tag
- FAQ section (3-5 questions)
- Schema markup (JSON-LD)
- External authority links (2-3)
- Image prompts (1-2 per major section)

## Output

Return to the calling skill:
- `content_markdown`: full page content in markdown
- `meta_title`: title tag (max 60 chars)
- `meta_description`: meta description (max 155 chars)
- `h1`: H1 heading
- `faq_section`: FAQ markdown
- `schema_json_ld`: JSON-LD schema markup
- `external_links`: list of outbound links with anchor text and placement
- `image_prompts`: list of image descriptions per section
- `word_count`: actual word count
- `passes_completed`: 8

## Critical Rules

1. **Never skip passes.** All 8 passes must run for every piece of content.
2. **Pass 3 MUST use separate generations per section.** This is what creates natural variation.
3. **The anti-AI writing guidelines apply to every pass.** Load them at the start and check against them in Pass 8.
4. **AHPRA compliance is checked in Pass 8** for healthcare clients. Do not skip this.
5. **Do not over-optimise.** Content should read naturally. Keyword stuffing is worse than under-optimisation.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/agents/content-writer.md
git commit -m "feat(gmb-hub): add content-writer agent (8-pass pipeline)"
```

---

## Task 33: README.md

**Files:**
- Create: `plugins/lhm-gmb-hub/README.md`

- [ ] **Step 1: Write README**

Write a README following the pattern of other plugins. Include: plugin description, skill count (17), agent count (6), skills catalog table, MCP dependencies, client folder structure, and the 3-month cycle overview.

- [ ] **Step 2: Commit**

```bash
git add plugins/lhm-gmb-hub/README.md
git commit -m "feat(gmb-hub): add README"
```

---

## Task 34: Marketplace + Version Bump + Pre-Push Checklist

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `plugins/lhm-marketing-hub/.claude-plugin/plugin.json` (version bump)
- Modify: `README.md` (root)

- [ ] **Step 1: Add lhm-gmb-hub to marketplace.json**

Add a new entry to the `plugins` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "lhm-gmb-hub",
  "source": "./plugins/lhm-gmb-hub",
  "description": "Google Business Profile optimisation system — repeating 3-month cycle of GBP foundation, service page optimisation, content expansion, and strategic link building with per-client project management tracking.",
  "version": "1.2.8",
  "category": "local-seo",
  "tags": ["gmb", "gbp", "local-seo", "google-business-profile", "agency"]
}
```

- [ ] **Step 2: Bump version in all 3 locations**

Update version to `1.2.8` in:
1. `plugins/lhm-gmb-hub/.claude-plugin/plugin.json` → `version` (already set)
2. `.claude-plugin/marketplace.json` → `metadata.version`
3. `.claude-plugin/marketplace.json` → new plugin entry `version`

All three must match.

- [ ] **Step 3: Update root README.md**

Add the GMB Hub to the plugin listing and skill counts.

- [ ] **Step 4: Verify all LEARNED.md files are clean**

Check every `plugins/lhm-gmb-hub/skills/*/LEARNED.md` contains only the clean header.

- [ ] **Step 5: Remove any scaffold placeholder files**

Check for and remove: `scripts/example.py`, `assets/example_asset.txt`, any placeholder content in references.

- [ ] **Step 6: Final commit**

```bash
git add .claude-plugin/marketplace.json README.md
git commit -m "feat(gmb-hub): add to marketplace, bump version to 1.2.8, update README"
```

---

## Summary

| Task | Description | Dependencies | Files |
|------|------------|-------------|-------|
| 1 | Plugin scaffold | None | Directories + plugin.json + LEARNED.md files |
| 2 | CLAUDE.md | Task 1 | Plugin-wide rules |
| 3 | .mcp.json | Task 1 | MCP configuration |
| 4 | Anti-AI guidelines | Task 1 | Copy from marketing-hub |
| 5 | AHPRA framework | Task 1 | Healthcare compliance reference |
| 6 | Ranking principles | Task 1 | 7 key principles reference |
| 7 | MCP setup guide | Task 1 | Install instructions for 3 MCPs |
| 8 | 8-pass engine | Task 1 | Writing pipeline specification |
| 9 | Content guardrails (x4) | Task 1 | 4 content type guardrails |
| 10 | gmb-project-manager | Tasks 1-9 | Project tracking skill |
| 11-26 | 16 remaining skills | Tasks 1-9 | One skill per task |
| 27 | gmb-orchestrator | Tasks 10-26 | Master agent |
| 28 | onboarding-agent | Tasks 10-26 | Month 0 agent |
| 29 | service-optimizer-agent | Tasks 10-26 | Month 1 agent |
| 30 | content-expansion-agent | Tasks 10-26 | Month 2 agent |
| 31 | link-building-agent | Tasks 10-26 | Month 3 agent |
| 32 | content-writer | Tasks 10-26 | 8-pass writing agent |
| 33 | README | Tasks 27-32 | Plugin documentation |
| 34 | Marketplace + version | Task 33 | Pre-push checklist |

**Total: 34 tasks, 17 skills, 6 agents, 10 reference files, 1 plugin config, 1 MCP config, 1 README**
