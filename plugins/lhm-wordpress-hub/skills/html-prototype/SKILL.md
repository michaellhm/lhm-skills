---
name: html-prototype
description: "Generate static HTML prototypes of key pages using the design system. Use this when the user says 'HTML prototype', 'static prototype', 'mockup', 'preview the design', 'HTML preview', or 'prototype the homepage'. Phase 4 of the website build. Optional step — requires brand guidelines and design system."
---

# HTML Prototype

Generate static HTML/CSS prototypes of key pages to preview the design before building in WordPress. This is an optional step — useful for client approval or design validation.

## Before Starting

1. **Read brand guidelines** — read `/design/brand_guidelines.md`
2. **Read design system** — read `/design/design_system.md`
3. **Read content files** — read the relevant page from `/content/`
4. **Read block specs** — read `/design/blocks.md` for component patterns

## Step 1: Scope

Use the `AskUserQuestion` tool:

> "Which pages should I prototype?"

Options:
- "Homepage only" (most common)
- "Homepage + one service page"
- "All core pages"
- "Specific page" (let them choose)

## Step 2: Generate HTML Prototype

For each page, create a folder at `/design/prototype/{slug}/` with separated assets:

### Output Structure

**Single version:**
```
design/prototype/{slug}/
  index.html
  assets/
    css/style.css
    js/main.js
    images/
```

**Multiple versions** (when the user wants to compare directions):
```
design/prototype/{slug}/
  v1.html
  v2.html
  v3.html
  assets/
    css/style.css       ← shared across all versions
    js/main.js          ← shared across all versions
    images/             ← shared across all versions
```

### HTML File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Title] — Prototype</title>
  <link rel="stylesheet" href="./assets/css/style.css">
  <!-- Google Fonts links here if needed -->
</head>
<body>

  <!-- Header -->
  <header>...</header>

  <!-- Page sections from content file -->
  <!-- Each section maps to a component declaration -->

  <!-- Footer -->
  <footer>...</footer>

  <script src="./assets/js/main.js"></script>
</body>
</html>
```

### CSS File (`assets/css/style.css`)

```css
/* Design System Tokens */
:root {
  /* Colors */
  --color-primary: #XXXXXX;
  --color-secondary: #XXXXXX;
  --color-accent: #XXXXXX;
  --color-background: #XXXXXX;
  --color-foreground: #XXXXXX;
  --color-muted: #XXXXXX;
  --color-surface: #XXXXXX;

  /* Typography */
  --font-heading: '[Heading Font]', serif;
  --font-body: '[Body Font]', sans-serif;

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2rem;
  --space-xl: 3rem;
  --space-2xl: 5rem;
  --space-3xl: 8rem;

  /* Layout */
  --content-width: 800px;
  --wide-width: 1200px;

  /* Border */
  --radius-sm: 4px;
  --radius-md: 8px;
}

/* Base styles */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font-body);
  color: var(--color-foreground);
  background: var(--color-background);
  line-height: 1.6;
}
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  line-height: 1.2;
}

/* Layout helpers */
.container { max-width: var(--content-width); margin: 0 auto; padding: 0 var(--space-md); }
.wide { max-width: var(--wide-width); margin: 0 auto; padding: 0 var(--space-md); }
.full-width { width: 100%; }

/* Section styles */
.section { padding: var(--space-2xl) var(--space-md); }
.section--alt { background: var(--color-surface); }
.section--dark { background: var(--color-primary); color: var(--color-background); }

/* Component styles mapped to block patterns */
/* ... component CSS here ... */
```

### Mapping Content to HTML

For each section in the content file:
1. Read the `<!-- component: name -->` declaration
2. Look up the component in `/design/blocks.md` for structure
3. Build the HTML using real content from the content file
4. Style using design tokens from the design system

### Rules

- **Use real content** — pull actual copy from the content files, not Lorem ipsum
- **Map design tokens** — every color, font, and spacing value must come from the design system
- **Responsive** — the prototype should look reasonable on mobile (use flexbox/grid)
- **Separate assets** — CSS goes in `assets/css/style.css`, JS goes in `assets/js/main.js`, images go in `assets/images/`. HTML files link to these via relative paths (`./assets/css/style.css`, `./assets/js/main.js`, `./assets/images/hero.jpg`). The entire folder is upload-ready: drop it on any static server and it works
- Use Google Fonts `<link>` tags in the HTML `<head>` for web fonts if not self-hosted
- **JavaScript is allowed** — if the design calls for scroll animations, mobile menu toggles, intersection observers, or other interactions, put them in `assets/js/main.js`. The JS will be copied to `custom.js` during theme scaffold
- **Use `<details>/<summary>` for FAQ sections** — WordPress block themes style these natively, the theme's `frontend.js` handles single-open behaviour, and the CSS targets `.faq__list details` / `.faq__list summary`. This means zero conversion work when moving from prototype to WordPress. Do not use custom `<button class="faq__question">` with JS-driven accordions
- **Prefer CSS pseudo-elements over inline SVGs for decorative icons** — e.g. use `.service-card__link::after { content: '\2192'; }` for arrow icons rather than inline SVG markup. CSS pseudo-elements survive WordPress block conversion cleanly; inline SVGs often don't
- **Cross-reference campaign/location data from briefs** — always verify addresses, phone numbers, and location assignments from the content brief before building. Early prototypes have used incorrect location data when not double-checked
- **Class names are final** — the CSS classes you use here will be carried through verbatim to the WordPress theme. The theme scaffold skill copies your CSS into `custom.css` and the page builder uses your exact class names on WordPress blocks. So use clear, descriptive class names (e.g. `.hero-section`, `.card-grid`, `.testimonial-slider`) and be consistent. Do NOT rename classes after prototype approval, as the theme CSS and page content HTML will go out of sync
- **Include utility/layout classes** — the prototype CSS must include utility classes (`.container`, `.section`, `.text-center`, `.btn-group`) alongside component classes. These get copied verbatim to the WordPress theme. If they're missing from the prototype, they'll be missing from the theme and all sections will lack width constraints and spacing
- **Single version** — output as `index.html`
- **Multiple versions** — output as `v1.html`, `v2.html`, `v3.html` with a shared `assets/` folder. All versions use the same CSS and JS; only the HTML differs

### Version Navigator (multi-version only)

When creating multiple versions, add a floating version navigator to each HTML file. Place it just before the closing `</body>` tag:

```html
<!-- Version Navigator -->
<nav style="position:fixed;bottom:20px;right:20px;display:flex;gap:6px;z-index:9999;">
  <a href="./v1.html" style="padding:6px 14px;border-radius:999px;background:#333;color:#fff;text-decoration:none;font:600 13px/1 system-ui;">V1</a>
  <a href="./v2.html" style="padding:6px 14px;border-radius:999px;background:#333;color:#fff;text-decoration:none;font:600 13px/1 system-ui;">V2</a>
  <a href="./v3.html" style="padding:6px 14px;border-radius:999px;background:#333;color:#fff;text-decoration:none;font:600 13px/1 system-ui;">V3</a>
</nav>
```

Style the current version's pill differently (e.g. `background:#0066ff`) so the user knows which version they're viewing. Adjust the number of pills to match the number of versions.

### WordPress Editor Compatibility Notes

The prototype is a frontend-only artefact. The WordPress block editor renders differently. When building the prototype, keep these translation requirements in mind:

**Grid/flex layouts need WP layout attributes.** If you use `display: grid` or `display: flex` for multi-column layouts, the block editor will ignore those CSS rules and stack blocks vertically. Add an HTML comment annotation above each grid/flex section noting the WP translation:

```html
<!-- WP-LAYOUT: grid, columnCount: 3 -->
<div class="card-grid">
  ...
</div>
```

```html
<!-- WP-LAYOUT: flex, justifyContent: space-between -->
<div class="trust-bar">
  ...
</div>
```

```html
<!-- WP-LAYOUT: columns (2-col split) -->
<div class="image-text-split">
  ...
</div>
```

**Background image/video sections → `wp:cover`.** If you create a section with a background image/video and content overlay, annotate it:

```html
<!-- WP-BLOCK: wp:cover with video background -->
<section class="hero-section">
  <video ...></video>
  <div class="hero-overlay">...</div>
</section>
```

**Icons need SVG files.** If you use inline SVG icons, they will be invisible in the block editor. Annotate each icon element so the theme-scaffold skill knows to create standalone SVG files:

```html
<!-- WP-ICON: plumbing.svg -->
<svg class="card-icon">...</svg>
```

**Scroll animations need editor overrides.** If you use classes like `.reveal` with `opacity: 0` for scroll-triggered animations, the editor.css file will override these to keep content visible while editing. This is handled automatically by theme-scaffold, but be aware that any class that hides content on page load will need an editor override.

These annotations don't affect the prototype's appearance — they're instructions for the downstream skills (theme-scaffold and wp-page-builder) to handle the WordPress conversion correctly.

## Step 3: Presentation

Tell the user:

> "HTML prototype created at `/design/prototype/{slug}/`. Open `index.html` in a browser to preview (or upload the whole folder to a static server for client review). This is a static representation — the WordPress build will use block patterns for the actual implementation."

If multiple versions were created:

> "Created [N] versions at `/design/prototype/{slug}/`. Open any version in your browser — use the pill buttons in the bottom-right corner to switch between them."

## Step 4: Approval Gate

Use the `AskUserQuestion` tool:

> "Review the prototype in your browser. Does the design direction look right? Approved — proceed to **Phase 5: WordPress Build**?"

Options:
- "Approved — start theme scaffold"
- "Changes needed"
- "Create another page prototype"
- "Create an alternate version to compare"

After approval, if multiple versions exist, note which was approved (e.g. "v2 approved"). Downstream skills reference the approved version file specifically.
