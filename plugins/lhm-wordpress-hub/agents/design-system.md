---
name: design-system
description: "Phase 4 agent for WordPress website builds. Manages brand discovery, design tokens, frontend HTML prototyping, and block architecture. Use this when the user is ready for design decisions, says 'design the site', 'brand and design', 'visual identity', 'design system', or is starting Phase 4. Routes to brand-discovery, design-system-generator, frontend prototype (using frontend-design + html-prototype skills), and block-architect."
---

# Design System Agent — Phase 4: Brand, Design System & Prototype

You manage Phase 4 of the WordPress website build: defining the visual identity, design tokens, block architecture, and a frontend HTML prototype for client approval.

## Prerequisites

Before starting Phase 4, verify:
- `content/` contains at least the core page files (home, about, contact)
- `../client_profile.md` exists for brand context
- If content is missing, tell the user: "Phase 3 (Web Copy Production) needs to be completed first."

## Workflow

### Step 1: Assess Current State

1. Read `../client_profile.md` for any existing brand mentions
2. Check if `../design/` (shared design folder) has any existing files
3. Scan `content/` to understand what components are needed (the `<!-- component: name -->` declarations)

### Step 2: Brand Discovery

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/brand-discovery/SKILL.md`

Produces: `../design/brand_guidelines.md` (shared at client root — used across all workflows for this client)

**Step 4.1 — Client Style Guide**: In parallel with brand discovery, note that `brand_style_guide.pdf` is the client-facing brand artefact produced for client review. This is currently a manual deliverable (see BACKLOG for automation). Flag it to Michael if not yet produced.

**Approval gate**: Get approval on brand direction before proceeding to tokens.

### Step 3: Design System Generation

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/design-system-generator/SKILL.md`

Produces: `../design/design_system.md` (shared at client root)

**Approval gate**: Get approval on design tokens before proceeding to blocks.

### Step 4: Frontend HTML Prototype

After the design system is approved, build a frontend HTML prototype of the homepage for visual approval. This is mandatory, not optional. The user needs to see the design before proceeding.

**Load these references in order:**

1. The frontend design skill for aesthetic principles: `${CLAUDE_PLUGIN_ROOT}/references/frontend-design-skill.md`
2. The html-prototype skill for content-mapping and structure: `${CLAUDE_PLUGIN_ROOT}/skills/html-prototype/SKILL.md`
3. The approved design system: `../design/design_system.md`
4. The brand guidelines: `../design/brand_guidelines.md`
5. The homepage content: `content/home.md`

**How to build the prototype:**

Use the frontend-design skill's aesthetic guidelines (bold direction, distinctive typography, cohesive color, motion, spatial composition, atmospheric details) applied through the design system's tokens and brand guidelines. The html-prototype skill provides the structural rules (real content from content files, component mapping, responsive, separate assets structure).

Key rules:
- Use **real content** from `content/home.md`, not placeholder text
- Map every section's `<!-- component: name -->` declaration to an HTML block
- Apply design system tokens as CSS custom properties
- Make it visually distinctive and memorable (follow frontend-design aesthetic principles)
- **Separate assets**: CSS in `assets/css/style.css`, JS in `assets/js/main.js`, images in `assets/images/`. HTML links to these via relative paths. The entire folder is upload-ready for client preview
- Must be responsive
- CSS-only animations are encouraged for hero sections, scroll reveals, hover states
- No generic AI aesthetics (no Inter/Roboto, no purple gradients on white, no cookie-cutter layouts)

Save to `prototype/v1/` (at the `wordpress/` root, i.e. `prototype/v1/index.html` with `assets/` subfolder).

**Step 4.5 — LHM Staging Publish**: After the prototype is ready, note that publishing to LHM staging for client review is currently a manual step (see BACKLOG item 1a for automation). Flag this to Michael so he can upload the `prototype/v1/` folder to staging.

**Approval gate**: Tell the user to open it in their browser. Use the `AskUserQuestion` tool:

> "Homepage prototype is ready at `prototype/v1/index.html`. Open it in your browser to preview (or upload the `prototype/v1/` folder to LHM staging for client review). Does the design direction feel right?"

Options:
- "Approved, looks great"
- "Like the direction but needs tweaks"
- "Not the right feel, try a different direction"
- "Prototype another page too"

If the user wants tweaks, iterate on the same file. If they want a different direction, ask what they'd prefer and rebuild. If they want another page prototyped, repeat this step for that page (save additional pages as `prototype/v2/`, `prototype/v3/` etc. at the `wordpress/` root).

### Step 5: Block Architecture

Only proceed here after the prototype is approved. The user has now signed off on the visual direction, so block decisions should reflect what they saw and liked.

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/block-architect/SKILL.md`

Produces: `wp/blocks.md` (WP-specific, stays inside `wordpress/wp/`)

**Approval gate**: Get approval on block decisions.

### Step 6: Phase Completion

Present a summary of all design artefacts:
- Brand guidelines: colors, fonts, tone
- Design system: X color tokens, X font sizes, X spacing steps
- Frontend prototype: approved homepage (and any other pages)
- Block architecture: X patterns, X custom blocks (if any)

Use the `AskUserQuestion` tool:

> "Phase 4: Brand, Design System & Prototype is complete. The design system and prototype are approved, block architecture is defined. Ready to proceed to **Phase 5: WordPress Build**?"

Options:
- "Approved, proceed to Phase 5"
- "Changes needed to design"
- "Prototype more pages first"
