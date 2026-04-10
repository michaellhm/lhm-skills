# lhm-gmb-hub Plugin Design Spec

**Date:** 2026-04-11
**Author:** Michael + Claude
**SOP Source:** GMB 3-Month Ranking Flow — Execution SOP v1.3 (April 2026)
**Framework Source:** Caleb's Core 30 Local SEO System + LHM Additions

---

## 1. Overview

A standalone Claude plugin (`plugins/lhm-gmb-hub/`) that executes a repeating 3-month Google Business Profile optimisation cycle for local SEO clients. The plugin manages the full workflow from GBP foundation through service page optimisation, content expansion, and strategic link building.

The plugin also acts as a project manager: it maintains a per-client `GMBProjectManagement.md` file that tracks all tasks, focus keywords with ranking history, and cycle progress. When resuming work, the orchestrator reads this file to understand where the client is and what needs doing next.

### What This Plugin Does

- Runs a repeating 3-month cycle: Month 0 (onboarding/GBP foundation), Month 1 (service pages), Month 2 (content expansion), Month 3 (link building)
- Maintains a project management doc per client with task tracking, ranking history, and diagnostic summaries
- Uses an 8-pass writing engine for all content production that mimics human writing patterns
- Integrates with Local Falcon, DataForSEO, Screaming Frog MCPs (with graceful fallbacks when not installed)
- Works alongside existing GSC, GA4, and Keywords Everywhere MCPs

### Key Principles (From SOP)

1. The GBP is the asset we're ranking. The website exists to support the GBP's authority.
2. Goal completion over aesthetics. Every page should help the user take action.
3. No traditional blogging. FAQ and supporting pages serve the same purpose but actually move rankings.
4. Every page needs a link. If Google can't find an external signal that a human valued the page, it may ignore it.
5. Diagnose before you build. The Local Falcon grid tells you whether to build topical content or geographical content.
6. AHPRA compliance is non-negotiable for healthcare clients.
7. Editorial links, not nav links. Google treats links within paragraph content as authority signals.

---

## 2. Plugin Structure

```
plugins/lhm-gmb-hub/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md
├── README.md
├── .mcp.json
├── agents/
│   ├── gmb-orchestrator.md
│   ├── onboarding-agent.md
│   ├── service-optimizer-agent.md
│   ├── content-expansion-agent.md
│   ├── link-building-agent.md
│   └── content-writer.md
├── skills/
│   ├── gmb-project-manager/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── run-local-diagnostic/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── gbp-optimiser/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── gbp-post-generator/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── citation-audit/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── entity-mapper/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── site-architecture-mapper/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── service-priority-selector/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── consistency-signal-audit/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── service-page-writer/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── technical-page-audit/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── faq-content-builder/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── neighbourhood-overlay-writer/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── link-gap-finder/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── local-authority-finder/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   ├── pr-brief-generator/
│   │   ├── SKILL.md
│   │   └── LEARNED.md
│   └── monthly-cycle-report/
│       ├── SKILL.md
│       └── LEARNED.md
└── references/
    ├── anti-ai-writing-guidelines.json
    ├── ahpra-compliance-framework.md
    ├── gmb-ranking-principles.md
    ├── mcp-setup-guide.md
    ├── 8-pass-writing-engine.md
    └── content-guardrails/
        ├── service-page.md
        ├── category-page.md
        ├── location-page.md
        └── supporting-content.md
```

**17 skills, 6 agents, 4 reference files + writing engine + 4 content guardrails.**

---

## 3. Client Folder Structure

```
client_folder/
├── client_profile.md                    # Shared with marketing-hub
├── gmb/
│   ├── GMBProjectManagement.md          # Project tracker (spans all cycles)
│   ├── onboarding/
│   │   ├── diagnostic_report.md
│   │   ├── gbp_optimisation_plan.md
│   │   ├── gbp_posts_52_weeks.csv
│   │   ├── citation_audit.md
│   │   ├── entity_map.md
│   │   └── site_architecture.md
│   └── monthly-optimization/
│       ├── YYYY-MM/                     # One folder per month of work
│       │   ├── service_priorities.md
│       │   ├── consistency_audit.md
│       │   ├── [service-slug].md        # Service page content
│       │   ├── [faq-slug].md            # FAQ pages (Month 2)
│       │   ├── [geo-slug].md            # Overlay pages (Month 2)
│       │   ├── link_gap_report.md       # Month 3
│       │   ├── link_tracking.csv        # Month 3
│       │   ├── local_authority_opportunities.md  # Month 3
│       │   ├── press_release.md         # Month 3 (optional)
│       │   ├── diagnostic_rerun.md      # Month 2 re-diagnostic
│       │   ├── technical_audit.md
│       │   └── month_N_report.md
│       └── YYYY-MM/                     # Next month...
```

---

## 4. GMBProjectManagement.md Structure

This file is the single source of truth for where a client is in their GMB optimisation journey. It lives at `client_folder/gmb/GMBProjectManagement.md`.

### Template

```markdown
# GMB Project Management — [Client Name]

## Overview
- **Client:** [Name]
- **Primary Location:** [Address]
- **Primary Modality:** [e.g. Physiotherapy]
- **Current Cycle:** 1 (started YYYY-MM-DD)
- **Current Phase:** Month 0 — Onboarding & GBP Foundation
- **Last Updated:** YYYY-MM-DD

## Focus Keywords & Ranking History

| Keyword | Target | M0 (Baseline) | M1 | M2 | M3 | Trend |
|---------|--------|---------------|----|----|----|----|
| [Primary Modality] [City] | Top 3 | — | — | — | — | — |
| [Service 2] [City] | Top 3 | — | — | — | — | — |
| [Service 3] [City] | Top 5 | — | — | — | — | — |
| [Service 4] [City] | Top 5 | — | — | — | — | — |
| [Service 5] [City] | Top 5 | — | — | — | — | — |
| [Service 6] [City] | Top 10 | — | — | — | — | — |
| [Service 7] [City] | Top 10 | — | — | — | — | — |

## Diagnostic Summary
- **Threshold Decision:** [Topical relevance / Proximity / Mixed]
- **Top Competitor Top3%:** [X]%
- **Client Top3%:** [X]% ([X]% of competitor = [above/below] threshold)
- **Month 2 Direction:** [FAQ content / Neighbourhood overlays / Mixed]

## Priority Services (Current Cycle)
1. [Service 1]
2. [Service 2]
3. [Service 3]

---

## Month 0 — Onboarding & GBP Foundation

### Tasks
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

## Month 1 — Service Page Optimisation

### Tasks
- [ ] Priority services selected and approved
- [ ] Homepage consistency signal audit
- [ ] Service page: [Service 1]
- [ ] Service page: [Service 2]
- [ ] Service page: [Service 3]
- [ ] Technical audit: all service pages
- [ ] Pages submitted to GSC
- [ ] Month 1 report generated
- [ ] **Exit criteria met**

## Month 2 — Content Expansion

### Tasks
- [ ] Diagnostic re-run (compare to baseline)
- [ ] Content direction decided (FAQ vs overlay vs mixed)
- [ ] Supporting content for [Service 1] (X pages)
- [ ] Supporting content for [Service 2] (X pages)
- [ ] Supporting content for [Service 3] (X pages)
- [ ] Month 2 report generated
- [ ] **Exit criteria met**

## Month 3 — Link Building

### Tasks
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
- [Date]: [Decision or note]
```

### Update Rules

- Every skill updates this file when it completes
- Tasks are marked `[x]` with a completion date appended: `- [x] Run baseline diagnostic — completed 2026-04-01`
- Rankings are updated when new data is available (via MCP or manual input)
- Sub-tasks are expanded as needed (e.g. citation audit lists each directory)
- Notes section captures decisions that affect future work
- When a new cycle starts, new Month 0-3 sections are appended below the previous cycle

---

## 5. Agent Orchestration

### gmb-orchestrator (Master Agent)

**Trigger:** "work on GMB for [Client]", "continue GMB work", "GMB optimisation", "where are we at with GMB"

**Behaviour:**

1. Identifies the client (asks or detects from context)
2. Reads `gmb/GMBProjectManagement.md`
   - If it doesn't exist: routes to onboarding-agent to create it
3. Presents a status summary showing current phase, completed/outstanding tasks
4. Suggests the next action based on outstanding tasks
5. Asks the user: proceed with suggestion, pick a different task, or run a specific skill
6. Routes to the appropriate phase agent

### Routing Logic

```
IF GMBProjectManagement.md doesn't exist:
  → onboarding-agent (creates file, starts Month 0)

IF Month 0 incomplete:
  → onboarding-agent (picks up where it left off)

IF Month 0 complete, Month 1 incomplete:
  → service-optimizer-agent

IF Month 1 complete, Month 2 incomplete:
  → content-expansion-agent
  → Agent reads diagnostic to decide: FAQ path or overlay path

IF Month 2 complete, Month 3 incomplete:
  → link-building-agent

IF Month 3 complete:
  → Prompt: "Cycle complete. Start new cycle?"
  → If yes: append new cycle sections, re-run Month 0 diagnostic
```

### Phase Agent Behaviour (Shared Pattern)

Each phase agent follows the same pattern:

1. **Load context** — reads `GMBProjectManagement.md` + `client_profile.md`
2. **Check exit criteria for previous phase** — if incomplete, block and explain what's missing
3. **Walk through skills in order** — suggest each, let user skip or reorder
4. **After each skill completes** — update `GMBProjectManagement.md` (mark task done, add date, record outputs)
5. **Check phase exit criteria** — when all tasks done, prompt to advance to next month

### Key Constraint: Agents Suggest and Confirm

Phase agents do NOT auto-execute through all skills silently. Each skill requires user go-ahead before executing. Reasons:

- Michael needs to approve priority services before Month 1 proceeds
- User might want to skip a skill or run it later
- Content needs human review before publishing
- Some tasks require manual action (applying GBP changes, submitting citations)

### Agent Inventory

| Agent | Role | Skills It Chains |
|-------|------|-----------------|
| `gmb-orchestrator` | Master — detects phase, routes to phase agent | All (via phase agents) |
| `onboarding-agent` | Month 0 — GBP foundation | run-local-diagnostic, gbp-optimiser, gbp-post-generator, citation-audit, entity-mapper, site-architecture-mapper |
| `service-optimizer-agent` | Month 1 — service pages | service-priority-selector, consistency-signal-audit, service-page-writer, technical-page-audit, monthly-cycle-report |
| `content-expansion-agent` | Month 2 — FAQ or overlays | run-local-diagnostic (re-run), faq-content-builder, neighbourhood-overlay-writer, monthly-cycle-report |
| `link-building-agent` | Month 3 — link acquisition | link-gap-finder, local-authority-finder, pr-brief-generator, monthly-cycle-report |
| `content-writer` | Utility — 8-pass writing engine | Called by any content-producing skill |

---

## 6. 8-Pass Writing Engine

### Overview

All content-producing skills route to the `content-writer` agent for actual content generation. The skill handles research and context gathering; the writing agent handles the 8-pass pipeline.

### Handoff Pattern

```
Content skill (e.g. service-page-writer):
  → Gathers research: entities, competitor analysis, local context, PAA
  → Builds structured brief
  → Hands off to content-writer agent with:
     - content_type: "service-page" | "category-page" | "location-page" | "supporting-content"
     - structured_brief: the research synthesis
     - client_context: client_profile.md data
     - target_keyword: primary keyword for the page
     - location: city/suburb

Content-writer agent:
  → Loads 8-pass-writing-engine.md
  → Loads content-guardrails/[content_type].md
  → Executes all 8 passes
  → Runs parallel steps
  → Returns finished content to the calling skill

Calling skill:
  → Saves content to client folder
  → Updates GMBProjectManagement.md
```

### The 8 Passes

**Pass 1 — Research Synthesis**
Takes raw research (PAA questions, Reddit threads, competitor angles, local landmarks, entity map) and compresses it into a structured content brief. Defines: what questions to answer, what local details to weave in, what competitor angles to cover but better, what entities must appear.

**Pass 2 — Strategic Outline**
Builds the full page architecture from the brief. Every H2 heading, the angle for each section, how sections connect, what each section needs to accomplish. This is not just a list of headings; it maps the logical flow from top to bottom.

**Pass 3 — Section Draft (Independent Calls)**
Each H2 section is written with a separate, independent API call. Each section gets its own prompt containing only:
- The overall content brief and guardrails
- This section's specific context (what it needs to accomplish)
- The preceding section's final paragraph (for transition continuity)

The separate calls produce slightly different tone, energy, and word choice per section. This mimics how a human writes section by section over the course of a day, coming back with fresh energy each time.

**Pass 4 — Burstiness**
Breaks the robotic rhythm that AI naturally produces. AI writes sentences of consistent length with predictable paragraph cadence. This pass varies sentence length: long, then short, then two medium, then a fragment. Mixes paragraph lengths. Adds the irregular pacing that makes content feel alive.

**Pass 5 — Perplexity Injection**
Finds predictable AI word patterns and replaces them. "Significant improvements" becomes something a human would actually say. Targets AI-favourite words: robust, leverage, streamline, comprehensive, utilize, facilitate. Removes em dashes. Checks against the anti-ai-writing-guidelines.json for additional patterns.

**Pass 6 — Human Bookends**
Rewrites the first 2 and last 2 sentences of the article with extremely conversational, opinionated language. These sentences are weighted heaviest by search algorithms and AI systems. They're what searchers read first (opening) and last (conclusion). Getting these right matters more than the rest of the article combined.

**Pass 7 — Conversion Injection**
Naturally injects calls to action, phone numbers, and conversational urgency throughout the content. Not spammy banners dropped in paragraphs. The kind of lines that make someone stop reading and pick up the phone. This pass is different for each content type:
- Service pages: click to call, get directions, book online CTAs
- Location pages: local-specific CTAs with driving directions
- FAQ pages: soft CTAs linking back to the parent service page
- Category pages: editorial links to child service pages with action language

**Pass 8 — Final QC**
Evaluates the entire article as a whole for:
- Cohesion: do sections flow together despite being written independently?
- Brief adherence: did it cover everything from the original content brief?
- Outline adherence: does the structure match the strategic outline?
- Word count: is it within the target range for this content type?
- AI pattern check: any leftover AI patterns that slipped through passes 4-5?
- AHPRA compliance: for healthcare clients, final compliance sweep
- Anti-AI guidelines: final check against all 10 rules
Anything that doesn't meet standard gets flagged and rewritten in this pass.

### Parallel Steps (Run During/After Pass 8)

These are generated alongside the main content:
- **FAQ section:** 3-5 questions with answers (for FAQ schema)
- **Meta title, description, H1 tag:** optimised for CTR and keyword targeting
- **Schema markup:** Service schema for service pages, FAQ schema for FAQ pages, LocalBusiness for location pages
- **External authority links:** 2-3 relevant outbound links to authoritative sources
- **Image prompts:** Descriptions of what images should show for each section (for manual sourcing or AI generation)

### Content-Type Guardrails

Each content type has its own guardrail prompt loaded on top of every pass:

**Service page guardrails** (`content-guardrails/service-page.md`):
- Goal-completion focused. Target the "who can do this for me?" searcher, not the "how do I do this?" searcher
- Action-first opening addressing the user's immediate problem
- What the service includes (specific steps), how long it takes, what to expect
- CTAs: click to call, get directions, book online
- Entities from entity map woven naturally
- AHPRA compliance enforced
- No informational content (save that for FAQ pages)

**Category page guardrails** (`content-guardrails/category-page.md`):
- Hub page overview of a broader modality
- Editorial links within paragraphs to all child service pages
- Establishes topical authority for the category
- Internal linking is the primary purpose

**Location page guardrails** (`content-guardrails/location-page.md`):
- Hyper-local content. NOT just a service page with a swapped suburb name
- Neighbourhood-specific demographics, landmarks, driving routes, local conditions
- Target keyword: [Service] near [Landmark] in [City]
- Must sound like it was written by someone who operates in that market
- Links back to parent service page

**Supporting content guardrails** (`content-guardrails/supporting-content.md`):
- Answers a specific question comprehensively (300-500+ words)
- Brief answer + editorial link added to parent service page
- Links back to parent service page
- Informational but still local
- Uses entities from entity map

---

## 7. Skill Inventory

### Month 0 Skills

**gmb-project-manager**
- Trigger: "update GMB project", "where are we at", "GMB status", "update rankings"
- Reads/writes: `GMBProjectManagement.md`
- Used by: all agents call this after completing tasks; can also be invoked standalone by the user
- Behaviour: Reads the project doc, presents status, updates tasks/rankings. When updating rankings, asks user via AskUserQuestion: supply manually or pull from MCPs? When invoked standalone (not via an agent), acts as a status dashboard showing current phase, outstanding tasks, and ranking trends. The gmb-orchestrator reads the project doc directly for routing decisions; this skill is for presenting status to the user and recording updates.

**run-local-diagnostic**
- Trigger: "run a local diagnostic for [Client]"
- MCPs: Local Falcon (primary), GSC, Keywords Everywhere. Fallback: manual scan + paste results
- Reads: `client_profile.md`
- Writes: `onboarding/diagnostic_report.md` (Month 0) or `monthly-optimization/YYYY-MM/diagnostic_rerun.md` (Month 2)
- Behaviour: Runs 169-point grid scan for primary keyword, records Top 3% metric, runs competitor audit (site: searches for indexed page counts), calculates threshold (25-50% of top competitor), determines topical vs proximity problem

**gbp-optimiser**
- Trigger: "optimise GBP for [Client]"
- MCPs: DataForSEO, Keywords Everywhere. Fallback: web search for competitor categories
- Reads: `client_profile.md`
- Writes: `onboarding/gbp_optimisation_plan.md`
- Behaviour: Researches competitor GBP categories, generates up to 10 recommended categories, produces 30+ service listings with descriptions, writes 750-char business description, outputs checklist with all recommended changes, flags NAP inconsistencies

**gbp-post-generator**
- Trigger: "generate 52 GBP posts for [Client]"
- MCPs: None required
- Reads: `client_profile.md`
- Writes: `onboarding/gbp_posts_52_weeks.csv`
- Behaviour: Generates 52 weekly posts rotating between service highlights, tips, seasonal content, team spotlights. AHPRA-compliant. CSV format for bulk upload.

**citation-audit**
- Trigger: "run a citation audit for [Client]"
- MCPs: None required (web search)
- Reads: `client_profile.md`
- Writes: `onboarding/citation_audit.md`
- Behaviour: Searches major Australian directories for existing listings, flags NAP inconsistencies, generates action plan (new submissions vs corrections). Directories: Apple Maps, Bing Places, Yelp, True Local, Hotfrog, Yellow Pages Australia, industry-specific.

**entity-mapper**
- Trigger: "run entity mapping for [Client]"
- MCPs: DataForSEO, GSC, Keywords Everywhere. Fallback: web search for competitor content
- Reads: `client_profile.md`, `onboarding/diagnostic_report.md`
- Writes: `onboarding/entity_map.md`
- Behaviour: Identifies top 3 competitors, fetches their top-ranking page content, extracts expert-level entities and concepts (not just keywords) that Google associates with authority in that modality. Entity map is referenced by all content-producing skills.

**site-architecture-mapper**
- Trigger: "map the site architecture for [Client]"
- MCPs: None required
- Reads: `client_profile.md`, `onboarding/gbp_optimisation_plan.md`
- Writes: `onboarding/site_architecture.md`
- Behaviour: Generates siloed site hierarchy mirroring GBP structure. Homepage links to category pages, category pages link to child service pages. Maps internal linking structure with editorial link instructions.

### Month 1 Skills

**service-priority-selector**
- Trigger: "select priority services for [Client] this cycle"
- MCPs: Local Falcon, GSC, GA4, Keywords Everywhere. Fallback: manual ranking input
- Reads: `client_profile.md`, `onboarding/diagnostic_report.md`
- Writes: `monthly-optimization/YYYY-MM/service_priorities.md`
- Behaviour: Cross-references ranking data, search volume, and conversion data. Recommends top 3 services with reasoning. Uses decision framework: primary modality ranking, sub-service gaps, surrounding suburbs, multi-modality prioritisation.

**consistency-signal-audit**
- Trigger: "audit consistency signals for [Client]"
- MCPs: GSC
- Reads: `client_profile.md`
- Writes: `monthly-optimization/YYYY-MM/consistency_audit.md`
- Behaviour: Fetches homepage (or location pages for multi-location), checks all 8 consistency signals: title tag, H1, Google Maps embed, secondary categories, review widget, address, phone number, Local Business Schema. Pass/fail per signal. Handles multi-location clinics per SOP section 1.2.1.

**service-page-writer**
- Trigger: "write service page content for [Service] for [Client]"
- MCPs: Keywords Everywhere
- Reads: `client_profile.md`, `onboarding/entity_map.md`, `monthly-optimization/YYYY-MM/service_priorities.md`
- Writes: `monthly-optimization/YYYY-MM/[service-slug].md`
- Behaviour: Gathers research (competitor service pages, PAA, local context), builds structured brief, hands off to content-writer agent with content_type "service-page". Also generates title tag, H1, meta description, Service schema markup, and internal linking instructions.

**technical-page-audit**
- Trigger: "run a technical audit on [URL]"
- MCPs: GSC
- Reads: None (works from URL)
- Writes: `monthly-optimization/YYYY-MM/technical_audit.md`
- Behaviour: Validates schema markup (Service + LocalBusiness in correct places), checks broken internal links, verifies GSC indexing status, submits for indexing if needed, checks page speed indicators, confirms mobile responsiveness. Pass/fail checklist.

### Month 2 Skills

**faq-content-builder**
- Trigger: "build FAQ content for [Service] for [Client]"
- MCPs: Keywords Everywhere
- Reads: `client_profile.md`, `onboarding/entity_map.md`
- Writes: `monthly-optimization/YYYY-MM/faq-[question-slug].md` (one per FAQ page)
- Behaviour: Searches Google for PAA questions (20-30), searches local Reddit threads for real questions, rewords to avoid PAA duplication flags, prioritises by search volume. Generates full content via content-writer agent with content_type "supporting-content". Also generates brief answer + editorial link text for parent service page.

**neighbourhood-overlay-writer**
- Trigger: "write neighbourhood overlay pages for [Service] for [Client]"
- MCPs: Local Falcon, Keywords Everywhere. Fallback: manual grid point identification
- Reads: `client_profile.md`, `onboarding/entity_map.md`
- Writes: `monthly-optimization/YYYY-MM/[service]-near-[landmark].md` (one per overlay)
- Behaviour: Uses Local Falcon scan to identify yellow grid points (positions 4-6), identifies Google Maps landmarks near those points, suggests 10-20 targets (user picks 3-5). Generates hyper-local content via content-writer agent with content_type "location-page". Includes neighbourhood demographics, local conditions, driving routes. Also generates internal linking instructions for "Areas We Serve" page.

### Month 3 Skills

**link-gap-finder**
- Trigger: "find pages missing external links for [Client]"
- MCPs: DataForSEO, Screaming Frog, GSC. Fallback: GSC external links report + site: search
- Reads: `client_profile.md`
- Writes: `monthly-optimization/YYYY-MM/link_gap_report.md` + `monthly-optimization/YYYY-MM/link_tracking.csv`
- Behaviour: Crawls sitemap, pulls backlink data per page, identifies pages with zero external links. Prioritises: service pages first, then FAQ, then geo pages. Outputs tracking spreadsheet template.

**local-authority-finder**
- Trigger: "find local authority link opportunities for [Client]"
- MCPs: None required (web search)
- Reads: `client_profile.md`
- Writes: `monthly-optimization/YYYY-MM/local_authority_opportunities.md`
- Behaviour: Searches for Chambers of Commerce within 70-80km radius, identifies local sponsorship opportunities (youth sports, charities, community events, schools, TEDx). Estimates costs, prioritises by link value and cost efficiency. Generates outreach plan with contact details.

**pr-brief-generator**
- Trigger: "generate a PR brief for [Client] targeting [Keyword]"
- MCPs: None required (web search)
- Reads: `client_profile.md`, `monthly-optimization/YYYY-MM/service_priorities.md`
- Writes: `monthly-optimization/YYYY-MM/press_release.md`
- Behaviour: Identifies newsworthy angles, writes press release draft following Signal Genesis format, specifies target link URLs (service page + GBP). AHPRA compliant. Optional — only when budget/plan includes PR distribution.

### Cross-Phase Skills

**monthly-cycle-report**
- Trigger: "generate month [1/2/3] report for [Client]"
- MCPs: Local Falcon, GSC, GA4, Keywords Everywhere. Fallback: manual Local Falcon data input
- Reads: `client_profile.md`, `GMBProjectManagement.md`, `onboarding/diagnostic_report.md`, `monthly-optimization/YYYY-MM/service_priorities.md`
- Writes: `monthly-optimization/YYYY-MM/month_N_report.md`
- Behaviour: Adapts to which month of the cycle. Pulls GSC performance data, compares against baseline, generates formatted report. Month 3 version includes full cycle summary with next-cycle recommendations. When rankings are available, asks user: supply manually or auto-pull?

---

## 8. MCP Configuration

### .mcp.json

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

### Graceful Fallback Pattern

Every skill that depends on an MCP follows this pattern:

1. Attempt to use the MCP tool
2. If MCP not available, display setup guide + manual alternative:

```
[MCP Name] is not configured. To set it up:

Claude Code:   claude mcp add [name] -- [install command]
Claude Desktop: Add to claude_desktop_config.json (see mcp-setup-guide.md)
CoWork:         Add to MCP settings (see mcp-setup-guide.md)

In the meantime, you can:
[Manual alternative steps]
```

### MCP Dependency Map

| Skill | Required MCPs | Already Installed | Fallback Strategy |
|-------|--------------|-------------------|-------------------|
| run-local-diagnostic | Local Falcon, GSC, KE | GSC, KE | Manual scan + paste results |
| gbp-optimiser | DataForSEO, KE | KE | Web search for competitor categories |
| gbp-post-generator | None | — | Fully functional |
| citation-audit | None (web search) | — | Fully functional |
| entity-mapper | DataForSEO, GSC, KE | GSC, KE | Web search for competitor content |
| site-architecture-mapper | None | — | Fully functional |
| service-priority-selector | Local Falcon, GSC, GA4, KE | GSC, GA4, KE | Manual ranking input |
| consistency-signal-audit | GSC | GSC | Fully functional |
| service-page-writer | KE | KE | Fully functional |
| technical-page-audit | GSC | GSC | Fully functional |
| faq-content-builder | KE | KE | Fully functional |
| neighbourhood-overlay-writer | Local Falcon, KE | KE | Manual grid point identification |
| link-gap-finder | DataForSEO, Screaming Frog, GSC | GSC | GSC external links + site: search |
| local-authority-finder | None (web search) | — | Fully functional |
| pr-brief-generator | None (web search) | — | Fully functional |
| monthly-cycle-report | Local Falcon, GSC, GA4, KE | GSC, GA4, KE | Manual Local Falcon data |

10 of 16 skills are fully or nearly fully functional with already-installed MCPs.

---

## 9. Data Flow

### How Data Moves Between Skills

```
Month 0:
  run-local-diagnostic
    → WRITES: onboarding/diagnostic_report.md
    → UPDATES: GMBProjectManagement.md (baseline rankings, threshold decision)

  gbp-optimiser
    → READS: client_profile.md
    → WRITES: onboarding/gbp_optimisation_plan.md
    → UPDATES: GMBProjectManagement.md (tasks checked off)

  entity-mapper
    → READS: client_profile.md, onboarding/diagnostic_report.md
    → WRITES: onboarding/entity_map.md
    → UPDATES: GMBProjectManagement.md

  site-architecture-mapper
    → READS: client_profile.md, onboarding/gbp_optimisation_plan.md
    → WRITES: onboarding/site_architecture.md
    → UPDATES: GMBProjectManagement.md

Month 1:
  service-priority-selector
    → READS: client_profile.md, onboarding/diagnostic_report.md
    → WRITES: monthly-optimization/YYYY-MM/service_priorities.md
    → UPDATES: GMBProjectManagement.md (priority services recorded)

  service-page-writer
    → READS: client_profile.md, onboarding/entity_map.md, service_priorities.md
    → CALLS: content-writer agent (8-pass engine, service-page guardrails)
    → WRITES: monthly-optimization/YYYY-MM/[service-slug].md
    → UPDATES: GMBProjectManagement.md (task checked off per page)

Month 2:
  run-local-diagnostic (re-run)
    → READS: onboarding/diagnostic_report.md (for comparison)
    → WRITES: monthly-optimization/YYYY-MM/diagnostic_rerun.md
    → UPDATES: GMBProjectManagement.md (new rankings, direction decision)

  faq-content-builder OR neighbourhood-overlay-writer
    → READS: diagnostic (threshold determines path)
    → CALLS: content-writer agent (supporting-content OR location-page guardrails)
    → WRITES: monthly-optimization/YYYY-MM/[content-slug].md
    → UPDATES: GMBProjectManagement.md

Month 3:
  link-gap-finder
    → WRITES: monthly-optimization/YYYY-MM/link_gap_report.md + link_tracking.csv
    → UPDATES: GMBProjectManagement.md

  monthly-cycle-report (end of cycle)
    → READS: GMBProjectManagement.md (full history)
    → WRITES: monthly-optimization/YYYY-MM/cycle_report.md
    → UPDATES: GMBProjectManagement.md (cycle complete, next cycle recs)
```

### The Golden Rule

Every skill updates GMBProjectManagement.md when it completes:
1. Marks its task(s) as done with a date
2. Records any outputs (file paths, key metrics)
3. Updates rankings if new data was pulled
4. Adds notes if decisions were made

### Cross-Plugin References

| Resource | Location | Relationship |
|----------|----------|-------------|
| `client_profile.md` | Client folder (shared) | Marketing-hub creates, GMB hub reads |
| `anti-ai-writing-guidelines.json` | Copied into GMB hub `references/` | Self-contained |
| AHPRA compliance framework | Copied into GMB hub `references/` | Self-contained |

The GMB hub is fully self-contained. It reads `client_profile.md` from the shared client folder but does not depend on marketing-hub being installed.

---

## 10. Exit Criteria Per Phase

Pulled directly from the SOP. The orchestrator checks these before allowing phase advancement.

**Month 0 exit — all must be true:**
- [ ] Baseline diagnostic saved with Top 3% metric
- [ ] Competitor audit complete (3 competitors)
- [ ] GBP fully optimised (all checklist items)
- [ ] 52 weekly posts generated
- [ ] Citations synced (audit complete, action plan created)
- [ ] Entity map saved
- [ ] Site architecture mapped

**Month 1 exit — all must be true:**
- [ ] 3 priority services selected and approved by Michael
- [ ] Homepage consistency signals passing (or flagged for fix)
- [ ] 3 service pages written and ready for publishing
- [ ] Technical audit passing for all service pages
- [ ] Pages submitted to GSC for indexing
- [ ] Month 1 report generated

**Month 2 exit — all must be true:**
- [ ] Diagnostic re-run completed with comparison to baseline
- [ ] Content direction decided (FAQ vs overlay vs mixed)
- [ ] 6-12 supporting content pages created
- [ ] Month 2 report generated

**Month 3 exit — all must be true:**
- [ ] Link gap audit complete
- [ ] At least 1 external link per service page acquired (or outreach in progress)
- [ ] Local authority opportunities identified and outreach started
- [ ] Month 3 / full cycle report generated with next-cycle recommendations

---

## 11. Multi-Location Handling

Per SOP section 1.2.1, multi-location clinics work differently:

- Each location gets its own GBP pointing to its own dedicated location page (not homepage)
- The 8 consistency signals apply to each location page individually
- The homepage becomes a brand/hub page linking to all locations
- Service pages can be shared across locations or duplicated if services differ

The orchestrator detects multi-location status from `client_profile.md` and adjusts:
- `consistency-signal-audit` runs per location page
- `run-local-diagnostic` can run per location
- GMBProjectManagement.md sections are expanded to cover each location

---

## 12. New Cycle Behaviour

When Month 3 is complete and the user confirms starting a new cycle:

1. The `monthly-cycle-report` skill generates end-of-cycle recommendations (next 3 priority services)
2. GMBProjectManagement.md gets new sections appended:
   - `## Cycle 2` header
   - New Month 0-3 task sections
   - Previous cycle's data remains as history
   - **Re-cycle Month 0 is lighter:** Only re-run diagnostic and select new priority services. GBP optimisation, citation audit, entity mapping, site architecture, and post generation are NOT repeated unless the user specifically requests them (e.g. GBP categories need updating). The onboarding-agent detects this is a re-cycle and skips completed foundation tasks.
3. The ranking history table adds new columns for the new cycle's months
4. Unfinished items from the previous cycle carry over (pages still missing links, etc.)
