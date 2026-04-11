# LHM GMB Hub

A Claude Code plugin that executes a repeating 3-month Google Business Profile optimisation cycle for local SEO clients. Built by LHM Digital.

## What This Is

17 skills and 6 agents organised into a structured workflow: Month 0 (onboarding and GBP foundation), Month 1 (service page optimisation), Month 2 (content expansion), Month 3 (strategic link building). The cycle then repeats with new priority services.

The plugin maintains a per-client `GMBProjectManagement.md` file that tracks all tasks, focus keywords with ranking history, and cycle progress. When resuming work, the orchestrator reads this file to understand where the client is and what needs doing next.

All content production uses an 8-pass writing engine designed to produce human-like content that passes AI detection.

## How It Works

1. **Start** — Say "work on GMB for [Client]" or "continue GMB work"
2. **Detection** — The orchestrator reads the project doc and identifies the current phase
3. **Routing** — Routes to the appropriate phase agent (onboarding, service optimizer, content expansion, or link building)
4. **Execution** — Phase agent walks through skills in order, getting user confirmation before each
5. **Tracking** — Every completed task updates GMBProjectManagement.md

## Structure

```
plugins/lhm-gmb-hub/
├── .claude-plugin/plugin.json
├── CLAUDE.md                               # Plugin-wide rules
├── .mcp.json                               # MCP server configs
├── agents/
│   ├── gmb-orchestrator.md                 # Master agent
│   ├── onboarding-agent.md                 # Month 0
│   ├── service-optimizer-agent.md          # Month 1
│   ├── content-expansion-agent.md          # Month 2
│   ├── link-building-agent.md              # Month 3
│   └── content-writer.md                   # 8-pass writing utility
├── skills/                                 # All 17 skills
│   ├── gmb-project-manager/                # Project tracking
│   ├── run-local-diagnostic/               # Grid scans + competitor audit
│   ├── gbp-optimiser/                      # GBP profile optimisation
│   ├── gbp-post-generator/                 # 52 weekly posts
│   ├── citation-audit/                     # Directory NAP check
│   ├── entity-mapper/                      # Competitor entity extraction
│   ├── site-architecture-mapper/           # GBP-mirrored silo
│   ├── service-priority-selector/          # Pick 3 services
│   ├── consistency-signal-audit/           # 8 homepage signals
│   ├── service-page-writer/                # Goal-completion content
│   ├── technical-page-audit/               # Schema, speed, indexing
│   ├── faq-content-builder/                # PAA to supporting pages
│   ├── neighbourhood-overlay-writer/       # Geo pages
│   ├── link-gap-finder/                    # Pages missing links
│   ├── local-authority-finder/             # Chambers, sponsorships
│   ├── pr-brief-generator/                 # Press release drafts
│   └── monthly-cycle-report/               # Monthly/cycle reports
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

## Skills Catalog

### Month 0 — Onboarding & GBP Foundation

| Skill | Description |
|-------|-------------|
| `gmb-project-manager` | Read, create, or update the per-client project tracking document |
| `run-local-diagnostic` | 169-point grid scan, competitor audit, threshold calculation |
| `gbp-optimiser` | Categories, services, business description, profile completion |
| `gbp-post-generator` | 52 weekly GBP posts in CSV format |
| `citation-audit` | Directory listings check and NAP consistency audit |
| `entity-mapper` | Extract expert-level entities from competitor content |
| `site-architecture-mapper` | Generate GBP-mirrored site silo structure |

### Month 1 — Service Page Optimisation

| Skill | Description |
|-------|-------------|
| `service-priority-selector` | Cross-reference data to pick 3 priority services |
| `consistency-signal-audit` | Check 8 homepage consistency signals |
| `service-page-writer` | Research + 8-pass content for service pages |
| `technical-page-audit` | Schema, indexing, speed, mobile checks |

### Month 2 — Content Expansion

| Skill | Description |
|-------|-------------|
| `faq-content-builder` | PAA and Reddit question discovery, supporting pages |
| `neighbourhood-overlay-writer` | Hyper-local geo pages for yellow grid points |

### Month 3 — Link Building

| Skill | Description |
|-------|-------------|
| `link-gap-finder` | Identify pages with zero external links |
| `local-authority-finder` | Chambers of Commerce, sponsorships, .edu links |
| `pr-brief-generator` | Press release drafts (optional) |

### Cross-Phase

| Skill | Description |
|-------|-------------|
| `monthly-cycle-report` | Adapted monthly/cycle report with ranking trends |

## MCP Dependencies

| MCP | Status | Skills That Use It |
|-----|--------|-------------------|
| Google Search Console | Already installed | 6 skills |
| Google Analytics (GA4) | Already installed | 2 skills |
| Keywords Everywhere | Already installed | 8 skills |
| Local Falcon | Optional (new) | 4 skills |
| DataForSEO | Optional (new) | 3 skills |
| Screaming Frog | Optional (new) | 1 skill |

10 of 17 skills are fully functional with already-installed MCPs. See `references/mcp-setup-guide.md` for installation instructions.

## Key Principles

1. The GBP is the asset we're ranking. The website supports it.
2. Goal completion over aesthetics. Every page drives action.
3. No traditional blogging. FAQ pages serve the same purpose better.
4. Every page needs a link. No external signal = Google may ignore it.
5. Diagnose before you build. The grid scan tells you what to build.
6. AHPRA compliance is non-negotiable for healthcare clients.
7. Editorial links, not nav links. Paragraph links pass authority.
