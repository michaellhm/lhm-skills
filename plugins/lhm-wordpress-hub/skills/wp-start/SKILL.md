---
name: wp-start
description: "Start a WordPress website build session. Use this when the user wants to begin a website project, asks 'build a website', 'start a WordPress site', mentions 'website build', 'new site', or invokes /lhm-wordpress-hub:wp-start. This skill explains the phased delivery system, detects where the project is at, and routes to the right phase."
---

# Start a WordPress Build Session

Follow these steps in order. Do not skip steps.

## 1. Pre-flight — Verify Project Location

Check whether the current working directory is a client project folder or contains client folders.

- Use Glob or ls to inspect the current directory
- The location is **dynamic** — do not assume a fixed path
- If you can see a project structure (e.g. `/client/`, `/seo/`, `/content/` folders), you're inside a project
- If you can see client-named folders, ask which client to work on
- If neither: say "I can't find a project folder. Would you like me to create a new project?" and offer to run the `wp-project-setup` skill

## 2. Explain the System

Briefly tell the user:

> This is a phased WordPress build system. Each phase produces markdown files that become the source of truth. WordPress mirrors the filesystem — not the other way around.
>
> **Phases:**
> - **A. Client Intake** — Extract facts from conversations and documents
> - **B. SEO & Information Architecture** — Keywords, sitemap, page briefs
> - **C. Content** — Write page copy from briefs
> - **D. Design** — Brand guidelines, design tokens, block specs
> - **E. WordPress Build** — Theme scaffold, block registration, page building
> - **F. Ops** — Performance hardening, security, pre-launch checklist
>
> Each phase needs approval before moving to the next.

## 3. Detect Current Phase

Inspect the project folder to determine which phase to work on next. Read `${CLAUDE_PLUGIN_ROOT}/references/folder-structure.md` for the phase detection rules.

Check which folders exist:

| Folders Present | Current State | Next Action |
|----------------|---------------|-------------|
| None or empty | Fresh project | Run Phase A — Client Intake |
| `/client/` only | Intake done | Run Phase B — SEO & IA |
| `/client/` + `/seo/` | SEO done | Run Phase C — Content |
| `/client/` + `/seo/` + `/content/` | Content done | Run Phase D — Design |
| All above + `/design/` | Design done | Run Phase E — WP Build |
| All above + `/wp/` | Build done | Run Phase F — Ops |
| All folders populated | Site launched | Offer Site Extension |

Tell the user: "Your project is at **Phase X**. The next step is **[description]**. Ready to proceed?"

## 4. Route to Phase

Use the `AskUserQuestion` tool to confirm the next phase or let the user pick a different one:

- **Phase A**: Read `${CLAUDE_PLUGIN_ROOT}/skills/client-context-intake/SKILL.md`
- **Phase B**: Read `${CLAUDE_PLUGIN_ROOT}/skills/sitemap-architect/SKILL.md` (then `page-brief-generator`)
- **Phase C**: Read `${CLAUDE_PLUGIN_ROOT}/skills/page-copywriter/SKILL.md`
- **Phase D**: Read `${CLAUDE_PLUGIN_ROOT}/skills/brand-discovery/SKILL.md` (then `design-system-generator`, `block-architect`)
- **Phase E**: Read `${CLAUDE_PLUGIN_ROOT}/skills/theme-scaffold/SKILL.md` (then `wp-page-builder`)
- **Phase F**: Read `${CLAUDE_PLUGIN_ROOT}/skills/wp-performance/SKILL.md` (then `wp-security`)

Or the user can run any individual skill directly.

## 5. Available Skills

### Phase A: Client Intake
| Skill | Use When |
|-------|----------|
| **Client Context Intake** | Extracting facts from call notes, transcripts, or uploads |

### Phase B: SEO & Information Architecture
| Skill | Use When |
|-------|----------|
| **Sitemap Architect** | Building site structure, keyword map, page hierarchy |
| **Page Brief Generator** | Creating per-page briefs with keywords and sections |

### Phase C: Content
| Skill | Use When |
|-------|----------|
| **Page Copywriter** | Writing page content from a brief |

### Phase D: Design
| Skill | Use When |
|-------|----------|
| **Brand Discovery** | Defining brand colors, typography, tone, imagery |
| **Design System Generator** | Creating design tokens and component specs |
| **Block Architect** | Evaluating native vs custom blocks |
| **HTML Prototype** | Building static HTML prototypes |

### Phase E: WordPress Build
| Skill | Use When |
|-------|----------|
| **Theme Scaffold** | Scaffolding the block theme files |
| **WP Page Builder** | Building individual pages in WordPress |

### Phase F: Ops
| Skill | Use When |
|-------|----------|
| **WP Performance** | Performance audit and optimization |
| **WP Security** | Security hardening and pre-launch checklist |

### Utility
| Skill | Use When |
|-------|----------|
| **Project Setup** | Creating the canonical folder structure for a new project |
