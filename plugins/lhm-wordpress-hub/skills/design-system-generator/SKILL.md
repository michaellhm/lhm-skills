---
name: design-system-generator
description: "Generate design tokens, spacing scale, and component specs for theme.json. Use this when the user says 'design system', 'design tokens', 'spacing scale', 'generate theme.json settings', 'component specs', or 'design variables'. Phase D of the website build. Requires brand guidelines from Brand Discovery."
---

# Design System Generator

Translate brand guidelines into concrete design tokens, spacing scales, and component specifications that directly map to `theme.json` settings. This is the bridge between design decisions and WordPress implementation.

## Before Starting

1. **Read brand guidelines** — read `/design/brand_guidelines.md`
2. **Read theme.json reference** — read `${CLAUDE_PLUGIN_ROOT}/references/theme-json-guide.md`
3. If brand guidelines don't exist, tell the user and offer to run Brand Discovery first

## Step 1: Generate Design Tokens

Create `/design/design_system.md`:

```markdown
---
client: "[Business Name]"
version: 1
status: draft
---

# Design System

## Color Tokens

Maps directly to theme.json `settings.color.palette`.

| Token | Slug | Hex | CSS Variable |
|-------|------|-----|-------------|
| Primary | primary | #XXXXXX | var(--wp--preset--color--primary) |
| Secondary | secondary | #XXXXXX | var(--wp--preset--color--secondary) |
| Accent | accent | #XXXXXX | var(--wp--preset--color--accent) |
| Background | background | #XXXXXX | var(--wp--preset--color--background) |
| Foreground | foreground | #XXXXXX | var(--wp--preset--color--foreground) |
| Muted | muted | #XXXXXX | var(--wp--preset--color--muted) |
| Surface | surface | #XXXXXX | var(--wp--preset--color--surface) |

## Typography Tokens

Maps to theme.json `settings.typography`.

### Font Families
| Token | Slug | Stack | CSS Variable |
|-------|------|-------|-------------|
| Heading | heading | '[Font]', serif | var(--wp--preset--font-family--heading) |
| Body | body | '[Font]', sans-serif | var(--wp--preset--font-family--body) |

### Font Sizes (Fluid)
| Token | Slug | Min | Max | CSS Variable |
|-------|------|-----|-----|-------------|
| Small | small | 0.875rem | 1rem | var(--wp--preset--font-size--small) |
| Medium | medium | 1rem | 1.125rem | var(--wp--preset--font-size--medium) |
| Large | large | 1.25rem | 1.5rem | var(--wp--preset--font-size--large) |
| X-Large | x-large | 1.75rem | 2.25rem | var(--wp--preset--font-size--x-large) |
| XX-Large | xx-large | 2.25rem | 3rem | var(--wp--preset--font-size--xx-large) |

## Spacing Scale

Maps to theme.json `settings.spacing.spacingSizes`.

| Token | Slug | Size | CSS Variable | Usage |
|-------|------|------|-------------|-------|
| 2XS | 10 | 0.25rem | var(--wp--preset--spacing--10) | Inline gaps |
| XS | 20 | 0.5rem | var(--wp--preset--spacing--20) | Tight gaps |
| S | 30 | 1rem | var(--wp--preset--spacing--30) | Default gap |
| M | 40 | 1.5rem | var(--wp--preset--spacing--40) | Section padding |
| L | 50 | 2rem | var(--wp--preset--spacing--50) | Component spacing |
| XL | 60 | 3rem | var(--wp--preset--spacing--60) | Section spacing |
| 2XL | 70 | 5rem | var(--wp--preset--spacing--70) | Large sections |
| 3XL | 80 | 8rem | var(--wp--preset--spacing--80) | Hero padding |

## Layout

| Property | Value |
|----------|-------|
| Content width | 800px |
| Wide width | 1200px |
| Full width | 100% |

## Border & Radius

| Token | Value | Usage |
|-------|-------|-------|
| Radius small | 4px | Buttons, inputs |
| Radius medium | 8px | Cards |
| Radius large | 16px | Feature sections |
| Radius full | 9999px | Pills, avatars |

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| Shadow small | 0 1px 3px rgba(0,0,0,0.1) | Cards, dropdowns |
| Shadow medium | 0 4px 12px rgba(0,0,0,0.1) | Modals, popovers |
| Shadow large | 0 8px 24px rgba(0,0,0,0.12) | Featured elements |

## Component Specifications

### Buttons
| Variant | Background | Text | Border | Radius | Padding |
|---------|-----------|------|--------|--------|---------|
| Primary | primary | background | none | small | spacing-20 spacing-40 |
| Secondary | transparent | primary | 1px primary | small | spacing-20 spacing-40 |
| Accent | accent | background | none | small | spacing-20 spacing-40 |

### Cards
- Background: surface
- Border: 1px muted (or shadow-small)
- Radius: radius-medium
- Padding: spacing-40
- Gap between cards: spacing-40

### Section Defaults
- Vertical padding: spacing-70
- Horizontal padding: spacing-40
- Background alternation: background ↔ surface
- Max width: constrained to content-width
```

## Step 2: Validate Against Brand

Cross-check every token against the brand guidelines:
- Colors match the palette
- Font families match the typography choices
- Scale feels proportional and intentional

## Step 3: Approval Gate

Present a summary of the design system. Use the `AskUserQuestion` tool:

> "Design system generated with X color tokens, X font sizes, X spacing steps, and component specs. Review `/design/design_system.md`. Approved — proceed to **Block Architect**?"

Options:
- "Approved — evaluate block needs"
- "Changes needed"
- "Skip to theme scaffold"
