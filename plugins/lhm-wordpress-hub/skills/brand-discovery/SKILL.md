---
name: brand-discovery
description: "Extract or define brand guidelines — colors, typography, tone of voice, imagery direction. Use this when the user says 'brand guidelines', 'define the brand', 'brand discovery', 'color palette', 'brand identity', 'typography choices', 'visual identity', or 'brand direction'. Phase D of the website build. Can also be run standalone."
---

# Brand Discovery

Define the visual and verbal brand identity for the website. Outputs a brand guidelines document that feeds into the design system and theme scaffold.

## Before Starting

1. **Read client context** — read `/client/client_profile.md` for existing brand mentions, tone preferences, values
2. **Check for existing brand work** — if `/design/brand_guidelines.md` exists, read it and build on it
3. **Check for existing assets** — ask if the client has a logo, existing brand guide, or style preferences

## Step 1: Brand Audit

Use the `AskUserQuestion` tool to understand the starting point:

> "What brand assets exist?"

Options:
- "Existing brand guide / style guide"
- "Logo and colors only"
- "Nothing — starting from scratch"
- "Website exists — extract from that"

### If Existing Brand Guide
- Ask user to share the file or describe the key elements
- Extract and formalize into the standard format below

### If Logo and Colors Only
- Work with what exists, define everything else

### If Starting from Scratch
- Run the full discovery process below

### If Extracting from Existing Site
- Ask for the URL
- Note the colors, fonts, and overall feel
- Use as a starting point for refinement

## Step 2: Brand Discovery Questions

For each category, gather information from the client (skip what's already known from client files):

### Personality & Tone
- If the brand were a person, how would you describe their personality?
- Three adjectives that describe the brand
- What should the website *feel* like? (e.g. professional, friendly, bold, minimal)
- Any brands you admire (not necessarily competitors)?

### Color Direction
- Any existing brand colors? (hex codes if available)
- Color associations: warm/cool, bright/muted, bold/subtle
- Any colors to avoid?

### Typography Direction
- Modern or traditional?
- Clean/minimal or decorative?
- Any font preferences or existing brand fonts?

### Imagery Direction
- Photography style: real people, abstract, product shots, lifestyle?
- Illustration: yes/no, style?
- Overall visual approach: minimal, rich, editorial, corporate?

## Step 3: Generate Brand Guidelines

Write `/design/brand_guidelines.md`:

```markdown
---
client: "[Business Name]"
version: 1
status: draft
---

# Brand Guidelines

## Brand Personality

**Tone of voice**: [e.g. Professional yet approachable, warm, authoritative]

**Brand adjectives**: [e.g. Trusted, Modern, Compassionate]

**Communication style**:
- We say: [examples]
- We don't say: [examples]

## Color Palette

### Primary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary | #XXXXXX | R, G, B | Headings, CTAs, key accents |
| Secondary | #XXXXXX | R, G, B | Supporting elements, hover states |

### Neutral Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Background | #XXXXXX | R, G, B | Page backgrounds |
| Foreground | #XXXXXX | R, G, B | Body text |
| Muted | #XXXXXX | R, G, B | Secondary text, borders |

### Accent Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Accent | #XXXXXX | R, G, B | Highlights, badges, alerts |
| Success | #XXXXXX | R, G, B | Positive indicators |
| Error | #XXXXXX | R, G, B | Error states |

## Typography

### Heading Font
- **Family**: [Font name]
- **Weights**: [e.g. 600, 700]
- **Source**: [Google Fonts / self-hosted / system]
- **Usage**: All headings (H1-H6)

### Body Font
- **Family**: [Font name]
- **Weights**: [e.g. 400, 500, 600]
- **Source**: [Google Fonts / self-hosted / system]
- **Usage**: Body text, navigation, UI elements

### Hierarchy
| Element | Font | Size | Weight | Line Height |
|---------|------|------|--------|-------------|
| H1 | Heading | 2.5-3rem | 700 | 1.1 |
| H2 | Heading | 2-2.25rem | 700 | 1.2 |
| H3 | Heading | 1.5-1.75rem | 600 | 1.3 |
| Body | Body | 1-1.125rem | 400 | 1.6 |
| Small | Body | 0.875rem | 400 | 1.5 |

## Imagery

### Photography Style
[Description of photography direction — people, settings, lighting, mood]

### Illustration
[If applicable — style, usage]

### Iconography
[Style: outlined/filled, weight, source library]

## Logo Usage
[Minimum size, clear space, color variations, placement rules]
```

## Step 4: Approval Gate

Present the brand guidelines summary. Use the `AskUserQuestion` tool:

> "Brand guidelines drafted. Review `/design/brand_guidelines.md`. Approved — proceed to **Design System Generator**?"

Options:
- "Approved — generate design system"
- "Changes needed"
- "I want to see color/font options before deciding"
