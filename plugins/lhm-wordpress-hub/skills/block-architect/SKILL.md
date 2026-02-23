---
name: block-architect
description: "Evaluate Gutenberg native blocks vs custom blocks for the project. Output block specifications and pattern requirements. Use this when the user says 'block architecture', 'which blocks do I need', 'custom blocks', 'block specs', 'gutenberg blocks', 'block evaluation', or 'native vs custom'. Phase D of the website build. Requires content files and design system."
---

# Block Architect

Evaluate what the site needs and decide whether native Gutenberg blocks, block patterns, or custom blocks are required. Outputs a block specification document that accounts for both frontend rendering AND block editor compatibility.

## Before Starting

1. **Read content files** — scan `/content/` to understand what components are declared (the `<!-- component: name -->` comments)
2. **Read design system** — read `/design/design_system.md` for component specs
3. **Read block patterns reference** — read `${CLAUDE_PLUGIN_ROOT}/references/block-patterns-guide.md`
4. **Read the HTML prototype** — if `/design/homepage-prototype.html` exists, read it to understand exact HTML structure, CSS classes, and any JavaScript interactions
5. If content files don't exist yet, tell the user and offer to run the Page Copywriter first

## Step 1: Audit Component Declarations

Scan all content files in `/content/` for `<!-- component: name -->` declarations. Build a list of every unique component requested across all pages.

Example output:
```
Components found:
- hero-banner (used on: home, about, services)
- card-grid (used on: home, services)
- cta-section (used on: home, about, services, contact)
- image-text-split (used on: about, service-a)
- testimonials (used on: home, service-a)
- faq-accordion (used on: faq, service-a)
- contact-form (used on: contact)
- stats-counter (used on: home)
- team-grid (used on: about)
```

## Step 2: Evaluate Each Component

For each component, decide: **native blocks only**, **block pattern**, or **custom block**. You must evaluate both frontend rendering AND block editor experience.

### Decision Framework

**Use native blocks (no pattern needed)** when:
- A single core block handles it (e.g. a heading, paragraph, image)
- Minimal styling beyond theme.json defaults

**Use a block pattern** when:
- Multiple core blocks combined (e.g. group + columns + heading + paragraph + buttons)
- Consistent layout that repeats across pages
- Can be built entirely with core blocks + theme.json styles
- Most components fall here — **patterns are the default answer**

**Use a custom block** when:
- No combination of core blocks can achieve the layout
- Complex interactivity is required (e.g. filterable portfolio, interactive calculator)
- Dynamic data from custom post types or external APIs
- **This should be rare** — exhaust pattern options first

### Editor Compatibility: The `wp:html` Decision Tree

The WordPress block editor and the frontend are two different rendering environments. A `wp:html` block shows as raw code or empty white space in the editor. Before using `wp:html`, work through this decision tree:

1. Can this be done with a single native block? → **Use it**
2. Can this be done with nested native blocks (group, columns, heading, paragraph, buttons, list)? → **Use them**
3. Does it need a background image/video with content overlay? → **Use `wp:cover`**
4. Does it need multi-column layout? → **Use `wp:columns` + `wp:column`, or `wp:group` with `layout:{"type":"grid"}` or `layout:{"type":"flex"}`**
5. Does it need icons? → **Use `wp:image` with SVG files from `assets/icons/`**, or emoji in `wp:paragraph`
6. Does it need a list with custom icons? → **Use `wp:list` + `wp:list-item`** with CSS `::marker` or `list-style` styling
7. Is it purely decorative and non-editable (e.g. a background shape)? → **CSS pseudo-element** (acceptable, no block needed)
8. None of the above work? → **`wp:html` with explicit warning**

If you must use `wp:html`, document it with this warning: *"This section will appear as raw code in the block editor. The client cannot visually edit it."*

### Layout: Use WP Native Layout Attributes

The block editor has its own layout engine. Custom CSS grid/flex classes (e.g. `.card-grid { display: grid; grid-template-columns: repeat(3, 1fr) }`) only render on the frontend. The editor ignores them and stacks blocks vertically.

**The principle: WP layout attributes handle structure. CSS classes handle style. They complement each other.**

For every component that uses grid or flex layout in the prototype, specify the WP layout attribute:

| Prototype CSS | WP Layout Attribute | Block Type |
|---|---|---|
| `display: grid; grid-template-columns: repeat(2, 1fr)` | `"layout":{"type":"grid","columnCount":2}` | wp:group |
| `display: grid; grid-template-columns: repeat(3, 1fr)` | `"layout":{"type":"grid","columnCount":3}` | wp:group |
| `display: grid; grid-template-columns: repeat(4, 1fr)` | `"layout":{"type":"grid","columnCount":4}` | wp:group |
| `display: grid; grid-template-columns: repeat(auto-fit, minmax(Xpx, 1fr))` | `"layout":{"type":"grid","minimumColumnWidth":"Xpx"}` | wp:group |
| `display: flex; gap: ...` | `"layout":{"type":"flex","flexWrap":"wrap"}` | wp:group |
| `display: flex; flex-wrap: nowrap` | `"layout":{"type":"flex","flexWrap":"nowrap"}` | wp:group |
| `display: flex; justify-content: space-between` | `"layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}` | wp:group |
| Two-column split (e.g. text + image) | N/A | wp:columns + wp:column |

### Icon Strategy

Icons need to be visible and editable in the block editor. These are the approaches ranked by preference:

| Approach | Editor Visible | Editable | Best For |
|---|---|---|---|
| `wp:image` with SVG file in `assets/icons/` | Yes | Yes (can swap image) | Service icons, feature icons |
| Emoji in `wp:paragraph` | Yes | Yes | Simple decorative icons |
| Custom block with `render.php` | Yes (if preview implemented) | Partially | Complex interactive elements |
| CSS `::before` pseudo-element | No | No | Purely decorative, non-essential only |
| Inline SVG in `wp:html` | No | Code only | **Avoid** |

For every component that uses icons, the block spec must specify which icon approach to use. The theme-scaffold skill will create the `assets/icons/` directory with SVG files for all icons used in the design.

## Step 3: Generate Block Specifications

**Critical rule: If an HTML prototype exists (`/design/homepage-prototype.html`), you MUST reference it when defining block specs. Each pattern must document the exact CSS classes, the WP layout type, the icon strategy, and any editor warnings.**

Write `/design/blocks.md`:

```markdown
---
client: "[Business Name]"
version: 1
status: draft
---

# Block Architecture

## Summary

| Type | Count |
|------|-------|
| Native blocks only | X |
| Block patterns | X |
| Custom blocks | X |
| wp:html blocks (last resort) | X |
| **Total components** | **X** |

## Block Patterns Needed

### hero-banner
- **Used on**: Home, About, Services
- **Core blocks**: Cover (full-width, video/image bg) > Group > Heading + Paragraph + Buttons
- **WP layout**: `wp:cover` with `"align":"full"` for background, constrained inner container
- **Prototype classes**: `.hero-section`, `.hero-content`, `.hero-title`, `.hero-subtitle`, `.hero-cta` (exact classes from prototype)
- **Icon strategy**: N/A
- **Editor compatible**: Yes (wp:cover renders background in editor)
- **Pattern file**: `patterns/hero-banner.php`

### card-grid
- **Used on**: Home, Services
- **Core blocks**: Group > [Group > Image + Heading + Paragraph + Button] per card
- **WP layout**: `"layout":{"type":"grid","columnCount":3}` on outer group
- **Prototype classes**: `.card-grid`, `.card`, `.card-title`, `.card-text` (exact classes from prototype)
- **Icon strategy**: `wp:image` with SVG files for card icons
- **Editor compatible**: Yes (WP grid layout renders columns in editor)
- **Pattern file**: `patterns/card-grid.php`

### cta-section
- **Used on**: Home, About, Services, Contact
- **Core blocks**: Group (full-width, primary bg) > Heading + Paragraph + Buttons
- **WP layout**: Constrained inner container
- **Prototype classes**: `.cta-section`, `.cta-content`, `.cta-heading` (exact classes from prototype)
- **Icon strategy**: N/A
- **Editor compatible**: Yes
- **Pattern file**: `patterns/cta-section.php`

### checklist-section
- **Used on**: Home, About
- **Core blocks**: Group > List + List Items
- **WP layout**: Default flow
- **Prototype classes**: `.checklist`, `.checklist-item` (exact classes from prototype)
- **Icon strategy**: CSS `::marker` or `list-style-image` for checkmark icons (acceptable — decorative)
- **Editor compatible**: Yes (wp:list renders in editor)
- **Pattern file**: `patterns/checklist-section.php`

[... one entry per component ...]

## Custom Blocks Needed

### [block-name] (if any)
- **Justification**: [Why native blocks can't handle this]
- **Functionality**: [What it does]
- **Data source**: [Static / CPT / API]
- **Complexity**: Low / Medium / High
- **Build approach**: [ACF blocks / create-block / manual]

## wp:html Blocks (Last Resort)

### [element-name] (if any)
- **Justification**: [Why no native block alternative exists]
- **Editor warning**: This section will appear as raw code in the block editor. The client cannot visually edit it.
- **Affected pages**: [list]

## Icons Required

SVG files to be created in `assets/icons/`:
- `icon-name.svg` — used in [component] on [pages]
- [... one per icon ...]

## Blocks NOT Needed

Components that can use existing core blocks without patterns:
- Single images → core/image
- Text sections → core/paragraph + core/heading
- Spacers → core/spacer

## Pattern Registration

These pattern categories should be registered in `functions.php`:
- hero — Hero sections
- cta — Call to action sections
- content — Content sections (cards, splits, features)
- testimonials — Social proof sections
- faq — FAQ sections
```

## Step 4: Approval Gate

Present the block architecture summary. Use the `AskUserQuestion` tool:

> "Block architecture defined: X patterns, X custom blocks, X wp:html blocks (with warnings). Review `/design/blocks.md`. Approved — proceed to **HTML Prototype** or skip to **Theme Scaffold**?"

Options:
- "Approved — create HTML prototypes first"
- "Approved — skip prototypes, go to theme scaffold"
- "Changes needed"
