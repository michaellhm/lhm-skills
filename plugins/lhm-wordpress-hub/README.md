# LHM WordPress Hub

Two-workflow Claude Code plugin for delivering WordPress projects: a six-phase full website build governed by the LHM WordPress SOP, and an eight-phase landing page campaign workflow on WordPress multisite.

## Two Workflows

| | Full Website Build | Landing Page Campaign |
|---|---|---|
| **When to use** | New WordPress site from scratch | PPC ad campaign LP on multisite |
| **Orchestrator** | `website-build-orchestrator` | `landing-page-orchestrator` |
| **Project doc** | `wordpress/website-project-management.md` | `landing-pages/[campaign]/landing-page-project-management.md` |
| **Phases** | 1–6 (SOP-aligned) | 1–8 |
| **Project manager skill** | `wp-project-manager` | `lp-project-manager` |
| **Build owner** | Aiya | Aiya |

Run `/lhm-wordpress-hub:wp-start` to begin a session — the router detects which workflow applies and hands off to the right orchestrator.

## Full Website Build (SOP)

Six phases, end-to-end:

```
Phase 1: Client Onboarding & Strategy   → Krystalyn — playbook, brief, Superpowers spec/plan, PM doc
Phase 2: SEO Architecture & Content Planning → Jaimee — keyword map, sitemap, page briefs
Phase 3: Web Copy Production            → Jaimee — homepage (client-approved), then services, locations, supporting
Phase 4: Brand, Design System & Prototype → Aiya — brand guidelines, design system, block architecture, prototype variants
Phase 5: WordPress Build                → Aiya — local site, theme, pages, forms, tracking, deploy to staging
Phase 6: QA & Go-Live                   → Jaimee + Krystalyn + Michael — pre-launch checklist, sign-off, DNS cutover
```

Each phase ends with an explicit approval gate. The PM doc tracks every checkbox, who owns it, and when it was completed.

## Landing Page Campaigns

Eight phases for PPC campaign landing pages on multisite:

```
1. Copy & Content       → lp-copy
2. Theme & Infrastructure → manual
3. Prototype            → lp-prototype
4. Subsite Setup        → lp-subsite-setup
5. HTML Deploy          → lp-deploy-1
6. Gutenberg Conversion → lp-deploy-2
7. Remaining Pages      → lp-deploy-3
8. QA & Go-Live         → lp-subsite-deploy
```

## Canonical Project Structure

Shared client artefacts live at the client root for cross-project reuse (WordPress, LP, GMB, social). Workflow-specific artefacts live under workflow folders.

```
[client_root]/
  client_profile.md
  playbook.md
  website-brief.md
  clarifications.md
  design/
    brand_guidelines.md
    brand_style_guide.pdf
    design_system.md

  wordpress/                              # full WP build
    website-project-management.md
    seo/  content/  prototype/  wp/  qa/
    docs/superpowers/{specs,plans}/

  landing-pages/[campaign]/               # LP campaigns
    landing-page-project-management.md
    ...

  gmb/                                    # GMB optimisation
```

See `references/folder-structure.md` for the complete specification.

## Directory Structure

```
plugins/lhm-wordpress-hub/
  .claude-plugin/
    plugin.json
  agents/
    website-build-orchestrator.md   # full build entry — phase detection, routing, gates
    landing-page-orchestrator.md    # LP campaign entry
    client-intake.md                # Phase 1 agent
    seo-strategist.md               # Phase 2 agent
    web-copy-orchestrator.md        # Phase 3 orchestrator (homepage 3-version flow, sequential pages)
    content-writer.md               # 8-pass writing engine (called by web-copy-orchestrator and skills)
    design-system.md                # Phase 4 agent
    wordpress-builder.md            # Phase 5 agent
    qa-and-launch.md                # Phase 6 agent
    site-extension.md               # Post-launch agent
  skills/                            # 27 skills (16 full-build, 8 LP, 3 shared utility)
    [full build...]
    [LP...]
    [shared utility: wp-start, wp-project-setup, wp-ssh-deploy, css-sync-check, visual-qa, wp-blog-publisher]
  references/
    folder-structure.md
    content-guardrails/web-copy.md
    block-patterns-guide.md
    theme-json-guide.md
    wp-cli-reference.md
    frontend-design-skill.md
    gutenberg-conversion-patterns.md
    lp-reference.md
  BACKLOG.md
  CLAUDE.md
  README.md
```

## Skills Catalog — Full Website Build

### Utility (shared)
| Skill | Description |
|-------|-------------|
| `wp-start` | Workflow router — detects full-build vs LP, hands off to the right orchestrator |
| `wp-project-setup` | Initialize client-root scaffolding and `wordpress/` subtree |
| `wp-project-manager` | Read, create, or update `website-project-management.md` |

### Phase 1: Client Onboarding & Strategy
| Skill | Description |
|-------|-------------|
| `client-context-intake` | Extract structured facts from call notes, transcripts, uploads |

### Phase 2: SEO Architecture & Content Planning
| Skill | Description |
|-------|-------------|
| `sitemap-architect` | Build keyword map, sitemap, page hierarchy |
| `page-brief-generator` | Per-page briefs with keywords, sections, CTAs |

### Phase 3: Web Copy Production
| Skill | Description |
|-------|-------------|
| `page-copywriter` | Write page copy from briefs (routes through `content-writer` 8-pass agent) |

### Phase 4: Brand, Design System & Prototype
| Skill | Description |
|-------|-------------|
| `brand-discovery` | Define brand colours, typography, tone, imagery |
| `design-system-generator` | Generate design tokens, spacing scale, component specs |
| `block-architect` | Evaluate native vs custom blocks, output specs |
| `html-prototype` | Generate static HTML prototypes |

### Phase 5: WordPress Build
| Skill | Description |
|-------|-------------|
| `theme-scaffold` | Scaffold custom block theme with theme.json, templates, patterns |
| `css-sync-check` | Verify theme CSS matches prototype CSS |
| `wp-page-builder` | Build pages in WordPress from content + design artefacts |
| `visual-qa` | Pixel-perfect visual regression via Playwright MCP |
| `wp-ssh-deploy` | Push local WP site to remote server via SSH + WP-CLI |
| `wp-blog-publisher` | Publish blog posts via WP-CLI over SSH |

### Phase 6: QA & Go-Live
| Skill | Description |
|-------|-------------|
| `wp-performance` | Performance audit — Core Web Vitals, caching, images |
| `wp-security` | Security hardening — headers, permissions, pre-launch checklist |

## Skills Catalog — Landing Page Campaigns

| Skill | Description |
|-------|-------------|
| `lp-project-manager` | Read, create, or update `landing-page-project-management.md` |
| `lp-copy` | Write landing page copy for each ad group |
| `lp-prototype` | Build HTML/CSS landing page prototypes |
| `lp-subsite-setup` | Configure WordPress multisite subsite for the campaign |
| `lp-deploy-1` | Push prototype HTML into WordPress as Gutenberg HTML blocks |
| `lp-deploy-2` | Convert HTML blocks to native Gutenberg blocks |
| `lp-deploy-3` | Deploy remaining ad group pages |
| `lp-subsite-deploy` | Deploy LeadScalePro subsite from local Docker to live server |

## Agents

| Agent | Used When |
|-------|-----------|
| `website-build-orchestrator` | User starts or continues a full WP build |
| `landing-page-orchestrator` | User starts or continues an LP campaign |
| `client-intake` | Phase 1 work for full builds |
| `seo-strategist` | Phase 2 work for full builds |
| `web-copy-orchestrator` | Phase 3 — orchestrates homepage 3-version flow and sequential pages |
| `content-writer` | 8-pass writing engine — called by skills, not invoked directly |
| `design-system` | Phase 4 work for full builds |
| `wordpress-builder` | Phase 5 work for full builds |
| `qa-and-launch` | Phase 6 work for full builds |
| `site-extension` | Post-launch changes (add, modify, retire pages) |

## Cross-Plugin Integration

The WordPress hub references the marketing hub for shared writing rules and deeper analysis:

| Marketing Hub | Used By | Purpose |
|---|---|---|
| `references/8-pass-writing-engine.md` | content-writer agent | Long-form writing pipeline |
| `references/anti-ai-writing-guidelines.json` | All content skills | Anti-AI writing rules |
| `campaign-playbook-generator` | client-intake | Phase 1 Step 1.3 deeper brand extraction |
| `seo-audit` | seo-strategist | Technical SEO analysis |
| `competitive-analysis` | seo-strategist | Competitor research |
| `keyword-research` | seo-strategist | Keyword research |
| `taya-question-discovery` | seo-strategist | Phase 2 Step 2.1 question discovery |
| `copywriting` | web-copy-orchestrator | Copywriting frameworks |
