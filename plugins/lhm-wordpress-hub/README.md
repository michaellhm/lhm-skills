# LHM WordPress Hub

Guided WordPress website build system for Claude Code. Phased delivery from client intake through SEO, content, design, WordPress build, and ops hardening.

## What This Is

A Claude Code plugin with **15 skills** and **8 agents** that guides you through building a WordPress website. The core philosophy: **the filesystem is the source of truth** — WordPress mirrors what's in your project files, not the other way around.

## How It Works

The plugin implements a phased delivery framework with human approval gates between phases:

```
Phase A: Client Intake      → Extract facts from conversations/documents
Phase B: SEO & IA           → Keyword map, sitemap, page briefs
Phase C: Content             → Write page copy from briefs
Phase D: Design              → Brand guidelines, design system, block specs
Phase E: WordPress Build     → Theme scaffold, page building via WP-CLI
Phase F: Ops                 → Performance hardening, security, pre-launch
```

Each phase produces markdown artefacts in a canonical folder structure. No phase proceeds without explicit approval.

## Getting Started

1. Run `/lhm-wordpress-hub:wp-start` to begin a session
2. The orchestrator detects your project phase and routes you to the right skill
3. Follow the guided workflow through each phase

## Directory Structure

```
plugins/lhm-wordpress-hub/
  .claude-plugin/
    plugin.json
  agents/
    wordpress-orchestrator.md    # Main entry point — phase detection & routing
    client-intake.md             # Phase A agent
    seo-strategist.md            # Phase B agent
    content-writer.md            # Phase C agent
    design-system.md             # Phase D agent
    wordpress-builder.md         # Phase E agent
    site-ops.md                  # Phase F agent
    site-extension.md            # Post-launch agent
  skills/                        # All 15 skills
    wp-start/
    wp-project-setup/
    client-context-intake/
    sitemap-architect/
    page-brief-generator/
    page-copywriter/
    brand-discovery/
    design-system-generator/
    block-architect/
    html-prototype/
    theme-scaffold/
    wp-page-builder/
    visual-qa/
    wp-performance/
    wp-security/
  references/
    folder-structure.md          # Canonical project folder structure
    theme-json-guide.md          # theme.json configuration reference
    block-patterns-guide.md      # Block pattern development reference
    wp-cli-reference.md          # WP-CLI commands for site building
    frontend-design-skill.md     # Frontend design aesthetic guidelines
```

## Skills Catalog

### Utility
| Skill | Description |
|-------|-------------|
| `wp-start` | Entry point — explains the system, detects phase, routes to orchestrator |
| `wp-project-setup` | Initialize canonical folder structure for a new project |

### Phase A: Client Intake
| Skill | Description |
|-------|-------------|
| `client-context-intake` | Extract structured facts from call notes, transcripts, uploads |

### Phase B: SEO & Information Architecture
| Skill | Description |
|-------|-------------|
| `sitemap-architect` | Build keyword map, sitemap, page hierarchy |
| `page-brief-generator` | Generate per-page briefs with keywords, sections, CTAs |

### Phase C: Content
| Skill | Description |
|-------|-------------|
| `page-copywriter` | Write page content from briefs with SEO metadata |

### Phase D: Design
| Skill | Description |
|-------|-------------|
| `brand-discovery` | Define brand colors, typography, tone, imagery |
| `design-system-generator` | Generate design tokens, spacing scale, component specs |
| `block-architect` | Evaluate native vs custom blocks, output block specs |
| `html-prototype` | Generate static HTML prototypes of key pages |

### Phase E: WordPress Build
| Skill | Description |
|-------|-------------|
| `theme-scaffold` | Scaffold custom block theme with theme.json, templates, patterns |
| `wp-page-builder` | Build individual pages in WordPress from content + design artefacts |
| `visual-qa` | Pixel-perfect visual regression testing via Playwright MCP |

### Phase F: Ops
| Skill | Description |
|-------|-------------|
| `wp-performance` | Performance audit — Core Web Vitals, caching, image optimization |
| `wp-security` | Security hardening — headers, permissions, pre-launch checklist |

## Agents

| Agent | Phase | Purpose |
|-------|-------|---------|
| `wordpress-orchestrator` | All | Main entry point — detects phase, routes to agents/skills |
| `client-intake` | A | Manages client context extraction |
| `seo-strategist` | B | Manages keyword research, sitemap, and briefs |
| `content-writer` | C | Manages page content writing |
| `design-system` | D | Manages brand, design tokens, and block architecture |
| `wordpress-builder` | E | Manages theme scaffold and page building |
| `site-ops` | F | Manages performance and security hardening |
| `site-extension` | Post | Manages post-launch changes and delta detection |

## Cross-Plugin Integration

The WordPress hub references marketing hub skills for deeper analysis:

| Marketing Hub Skill | Used By | Purpose |
|-------------------|---------|---------|
| `campaign-playbook-generator` | Client Intake | Deeper brand/messaging extraction |
| `seo-audit` | SEO Strategist | Technical SEO analysis |
| `competitive-analysis` | SEO Strategist | Competitor research |
| `content-strategy` | SEO Strategist | Content planning |
| `keyword-research` | SEO Strategist | Keyword research |
| `copywriting` | Content Writer | Copywriting frameworks |

## Canonical Project Structure

Each project creates this folder structure:

```
/project-root/
  /client/          # Phase A outputs
  /seo/             # Phase B outputs
  /content/         # Phase C outputs
  /design/          # Phase D outputs
  /wp/              # Phase E outputs
  /ops/             # Phase F outputs
```

See `references/folder-structure.md` for the complete specification.
