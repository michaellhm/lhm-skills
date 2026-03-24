# Gutenberg Conversion Patterns (Proven Reference)

Battle-tested block markup patterns extracted from production WordPress sites. Use this as the single source of truth when converting HTML prototypes to native Gutenberg blocks.

## The Full-Width Section Pattern (Most Critical)

Every page section MUST use this nesting structure to achieve full-width backgrounds with centred content:

```html
<!-- wp:group {"className":"section-name","align":"full","layout":{"type":"default"}} -->
<div class="wp-block-group alignfull section-name">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">

  <!-- inner content blocks here -->

</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Why this is mandatory

- `"align":"full"` on the outer group makes the section span the full viewport width. Without it, WP constrains the section to `contentSize` from theme.json (often 800px), which is why pages appear ~600px wide in the editor.
- The `alignfull` class MUST appear on the rendered `<div>` alongside the JSON attribute.
- The inner `container` group provides max-width centering via your prototype CSS (`.container { max-width: 1200px; margin: 0 auto; }`).
- `"layout":{"type":"default"}` prevents WP from injecting its own layout classes that conflict with your CSS.

### Common mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Missing `"align":"full"` | Section constrained to contentSize (~800px) | Add `"align":"full"` to outer group JSON |
| Missing `alignfull` on div | Full-width doesn't render | Ensure `<div class="wp-block-group alignfull ...">` |
| Using `"layout":{"type":"constrained"}` | WP adds max-width that overrides your CSS | Use `"type":"default"` when prototype CSS handles layout |
| No container group | Content spans full viewport with no gutters | Always nest a container group inside full-width sections |

## Section-Level Patterns

### Hero with Video Background

```html
<!-- wp:cover {"url":"https://example.com/video.mp4","backgroundType":"video","dimRatio":70,"overlayColor":"foreground","align":"full","className":"hero"} -->
<div class="wp-block-cover alignfull hero"><span aria-hidden="true" class="wp-block-cover__background has-foreground-background-color has-background-dim-70 has-background-dim"></span><video class="wp-block-cover__video-background intrinsic-ignore" autoplay muted loop playsinline src="https://example.com/video.mp4" data-object-fit="cover"></video><div class="wp-block-cover__inner-container">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Overline Text</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 class="wp-block-heading">Main Headline</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Supporting paragraph text.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"className":"btn-group"} -->
<div class="wp-block-buttons btn-group">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">Primary CTA</a></div>
<!-- /wp:button -->

<!-- wp:button {"className":"is-style-outline"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="/contact">Secondary CTA</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div></div>
<!-- /wp:cover -->
```

### Hero with Background Colour (No Video/Image)

```html
<!-- wp:group {"className":"hero","align":"full","layout":{"type":"default"}} -->
<div class="wp-block-group alignfull hero">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Overline Text</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1} -->
<h1 class="wp-block-heading">Main Headline</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Supporting paragraph text.</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"className":"btn-group"} -->
<div class="wp-block-buttons btn-group">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">CTA Text</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Trust Bar (Stats Row)

```html
<!-- wp:group {"className":"trust-bar","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull trust-bar">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"trust-bar-grid","layout":{"type":"grid","columnCount":4}} -->
<div class="wp-block-group trust-bar-grid">
<!-- wp:group {"className":"trust-item"} -->
<div class="wp-block-group trust-item">
<!-- wp:paragraph {"className":"trust-number"} -->
<p class="trust-number">30+</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph {"className":"trust-label"} -->
<p class="trust-label">Years Experience</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"trust-item"} -->
<div class="wp-block-group trust-item">
<!-- wp:paragraph {"className":"trust-number"} -->
<p class="trust-number">2x</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph {"className":"trust-label"} -->
<p class="trust-label">Client Bookings Doubled</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- repeat for each stat -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Content Section (Narrow Text Block)

```html
<!-- wp:group {"className":"section problem-section","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section problem-section">
<!-- wp:group {"className":"container container--narrow","layout":{"type":"default"}} -->
<div class="wp-block-group container container--narrow">
<!-- wp:group {"className":"content-block","layout":{"type":"default"}} -->
<div class="wp-block-group content-block">
<!-- wp:paragraph {"className":"overline overline--primary"} -->
<p class="overline overline--primary">Section Label</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section Heading</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Body text paragraph one.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>Body text paragraph two. <strong>Bold emphasis text.</strong></p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">CTA Text</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Card Grid (2-4 columns)

```html
<!-- wp:group {"className":"section section--surface","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section section--surface">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Section Label</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section Heading</h2>
<!-- /wp:heading -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"card-grid","layout":{"type":"grid","columnCount":3}} -->
<div class="wp-block-group card-grid">
<!-- wp:group {"className":"card","layout":{"type":"default"}} -->
<div class="wp-block-group card">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Card Title</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Card description text.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"className":"card-link"} -->
<p class="card-link"><a href="/page">Learn more</a></p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- repeat for each card -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

**Grid column count**: Match the prototype. Use `columnCount` in the JSON. Common values: 2 for features, 3 for services, 4 for stats/industries.

### Features Grid (Icon + Title + Description, 2 columns)

```html
<!-- wp:group {"className":"section","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--primary"} -->
<p class="overline overline--primary">Section Label</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section Heading</h2>
<!-- /wp:heading -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"features-grid","layout":{"type":"grid","columnCount":2}} -->
<div class="wp-block-group features-grid">
<!-- wp:group {"className":"feature-item","layout":{"type":"default"}} -->
<div class="wp-block-group feature-item">
<!-- wp:group {"className":"feature-content","layout":{"type":"default"}} -->
<div class="wp-block-group feature-content">
<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading">Feature title.</h4>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Feature description text.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->

<!-- repeat for each feature -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Results/Case Study with Metrics

```html
<!-- wp:group {"className":"section results-section","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section results-section">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--primary"} -->
<p class="overline overline--primary">Results</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section Heading</h2>
<!-- /wp:heading -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"results-card","layout":{"type":"default"}} -->
<div class="wp-block-group results-card">
<!-- wp:paragraph -->
<p>Case study narrative text.</p>
<!-- /wp:paragraph -->

<!-- wp:group {"className":"results-metrics","layout":{"type":"grid","columnCount":3}} -->
<div class="wp-block-group results-metrics">
<!-- wp:group {"className":"metric","layout":{"type":"default"}} -->
<div class="wp-block-group metric">
<!-- wp:paragraph {"className":"metric-value"} -->
<p class="metric-value">30-40</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph {"className":"metric-label"} -->
<p class="metric-label">Bookings Before</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- repeat for each metric -->
</div>
<!-- /wp:group -->

<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button {"className":"is-style-outline"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="/case-studies">See Case Studies</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Industry/Category Grid (Linked Cards)

```html
<!-- wp:group {"className":"section section--surface","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section section--surface">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Industries</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Section Heading</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"className":"text-muted max-prose"} -->
<p class="text-muted max-prose">Supporting subtext.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"industry-grid","layout":{"type":"grid","columnCount":4}} -->
<div class="wp-block-group industry-grid">
<!-- wp:group {"className":"industry-card","layout":{"type":"default"}} -->
<div class="wp-block-group industry-card">
<!-- wp:paragraph {"className":"industry-icon"} -->
<p class="industry-icon">&#128295;</p>
<!-- /wp:paragraph -->
<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading"><a href="/industries/plumbers">Plumbers</a></h4>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Short description text.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- repeat for each industry -->
</div>
<!-- /wp:group -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} -->
<div class="wp-block-buttons">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">CTA Text</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Good Fit / Bad Fit (Two-Column Comparison)

```html
<!-- wp:group {"className":"section section--surface","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section section--surface">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Is This For You?</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">Who this is for (and who it isn't)</h2>
<!-- /wp:heading -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"fit-grid","layout":{"type":"grid","columnCount":2}} -->
<div class="wp-block-group fit-grid">
<!-- wp:group {"className":"fit-card fit-card--good","layout":{"type":"default"}} -->
<div class="wp-block-group fit-card fit-card--good">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Good fit</h3>
<!-- /wp:heading -->

<!-- wp:list {"className":"fit-list"} -->
<ul class="fit-list">
<!-- wp:list-item -->
<li>First criteria item</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Second criteria item</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"fit-card fit-card--bad","layout":{"type":"default"}} -->
<div class="wp-block-group fit-card fit-card--bad">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Not a good fit</h3>
<!-- /wp:heading -->

<!-- wp:list {"className":"fit-list"} -->
<ul class="fit-list">
<!-- wp:list-item -->
<li>First exclusion item</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Second exclusion item</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Process/Steps Section

```html
<!-- wp:group {"className":"section","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull section">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:group {"className":"text-center","layout":{"type":"default"}} -->
<div class="wp-block-group text-center">
<!-- wp:paragraph {"className":"overline overline--primary"} -->
<p class="overline overline--primary">Process</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">How it works</h2>
<!-- /wp:heading -->
</div>
<!-- /wp:group -->

<!-- wp:group {"className":"steps","layout":{"type":"grid","columnCount":4}} -->
<div class="wp-block-group steps">
<!-- wp:group {"className":"step","layout":{"type":"default"}} -->
<div class="wp-block-group step">
<!-- wp:heading {"level":4} -->
<h4 class="wp-block-heading">Step Title</h4>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>Step description text.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->

<!-- repeat for each step -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### CTA Section (Final Call to Action)

```html
<!-- wp:group {"className":"cta-section","layout":{"type":"default"},"align":"full"} -->
<div class="wp-block-group alignfull cta-section">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
<!-- wp:paragraph {"className":"overline overline--white"} -->
<p class="overline overline--white">Get Started</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2 class="wp-block-heading">CTA headline text.</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Supporting CTA paragraph.</p>
<!-- /wp:paragraph -->

<!-- wp:list {"className":"cta-checklist"} -->
<ul class="cta-checklist">
<!-- wp:list-item -->
<li>Benefit one</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Benefit two</li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li>Benefit three</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"},"className":"btn-group"} -->
<div class="wp-block-buttons btn-group">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">Primary CTA</a></div>
<!-- /wp:button -->

<!-- wp:button {"className":"is-style-outline"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="/contact">Secondary CTA</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Styled Paragraph (Custom Class)

```html
<!-- wp:paragraph {"className":"overline overline--accent"} -->
<p class="overline overline--accent">Overline Text</p>
<!-- /wp:paragraph -->
```

```html
<!-- wp:paragraph {"className":"text-muted max-prose"} -->
<p class="text-muted max-prose">Muted supporting text.</p>
<!-- /wp:paragraph -->
```

```html
<!-- wp:paragraph {"className":"text-center text-muted","style":{"typography":{"fontSize":"1.125rem"}}} -->
<p class="text-center text-muted" style="font-size:1.125rem">Inline styled text.</p>
<!-- /wp:paragraph -->
```

## Critical Conversion Rules

### 1. Every section gets `align: full`

Without exception. If a section spans the full viewport width in the prototype, it needs `"align":"full"` in the block JSON AND `alignfull` on the rendered div.

### 2. Preserve exact prototype class names

The CSS was extracted from the prototype. If the prototype has `.hero`, the block needs `className: "hero"`. If it has `.section--surface`, the block needs `className: "section section--surface"`. WordPress adds its own classes (`wp-block-group`, `is-layout-flow`) alongside yours. They stack, they don't conflict.

### 3. JSON attributes must match rendered HTML

The Gutenberg block validator compares JSON attributes against rendered HTML. If they don't match, you get "This block contains unexpected content" errors.

Common mismatches:
- JSON says `"align":"full"` but div doesn't have `alignfull` class
- JSON says `"backgroundColor":"primary"` but div doesn't have `has-primary-background-color`
- JSON says `"className":"hero"` but div has a different class

### 4. Layout type: `default` vs `grid` vs `flex` vs `constrained`

- `"type":"default"` = no WP layout interference. Your CSS handles everything. Use this for most outer sections.
- `"type":"grid"` = WP injects CSS Grid. Use for card grids, stats rows, steps. Set `"columnCount"` to match prototype columns.
- `"type":"flex"` = WP injects Flexbox. Use for inline elements (button groups, trust bars).
- `"type":"constrained"` = WP adds max-width. Avoid when prototype CSS has its own max-width via `.container`.

### 5. Do NOT use WP grid when prototype CSS has responsive breakpoints

If your prototype CSS defines `display: grid` with `@media` queries for mobile/tablet, do NOT add `layout: {type: "grid"}` to the block. WP grid ignores media queries and breaks responsive behaviour. Use `wp:group` with `className` only and let prototype CSS handle it.

### 6. Buttons: use wp:buttons, not raw anchors

```html
<!-- WRONG: raw anchor tags -->
<a href="/contact" class="btn btn--primary">CTA</a>

<!-- RIGHT: wp:buttons wrapper -->
<!-- wp:buttons {"className":"btn-group"} -->
<div class="wp-block-buttons btn-group">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact">CTA</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
```

Exception: If prototype CSS targets bare `.btn` on `<a>` tags and `wp:button` wrapper breaks the styling, keep as `wp:html`.

### 7. Lists: use wp:list + wp:list-item

```html
<!-- WRONG: raw HTML list -->
<ul><li>Item</li></ul>

<!-- RIGHT: native blocks -->
<!-- wp:list {"className":"checklist"} -->
<ul class="checklist">
<!-- wp:list-item -->
<li>Item</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
```

### 8. Inline SVG icons: use emoji or wp:image

Inline SVG in `wp:html` blocks is invisible in the editor. Use emoji in a paragraph or `wp:image` pointing to an SVG file.

```html
<!-- Emoji approach (simpler) -->
<!-- wp:paragraph {"className":"industry-icon"} -->
<p class="industry-icon">&#128295;</p>
<!-- /wp:paragraph -->

<!-- SVG file approach (cleaner) -->
<!-- wp:image {"className":"card-icon","sizeSlug":"full"} -->
<figure class="wp-block-image size-full card-icon">
  <img src="/wp-content/themes/theme-slug/assets/icons/icon.svg" alt="Icon" />
</figure>
<!-- /wp:image -->
```

## Editor Width Troubleshooting

If the page appears narrow in the Gutenberg editor (~600px instead of full-width):

1. **Check `align: full`** on every outer section group. This is the #1 cause.
2. **Check theme.json `contentSize`**. This sets the default editor width. A value of 800px is normal for content, but full-width sections override it with `alignfull`.
3. **Check `useRootPaddingAwareAlignments`** in theme.json settings. When `true`, WP adds root-level padding that constrains aligned blocks differently.
4. **Check editor.css** overrides. The editor stylesheet might need `.editor-styles-wrapper .alignfull { max-width: none; margin-left: auto; margin-right: auto; }` to allow full-width rendering in the editor.

## theme.json Settings That Affect Block Layout

```json
{
  "settings": {
    "layout": {
      "contentSize": "800px",   // Default block width
      "wideSize": "1200px"      // Wide alignment width
    },
    "useRootPaddingAwareAlignments": true  // Enables proper full-width in editor
  },
  "styles": {
    "spacing": {
      "blockGap": "0"  // CRITICAL: prevents WP from adding gaps between sections
    }
  }
}
```

`blockGap: "0"` is essential. Without it, WordPress inserts default vertical margins between every block, creating white strips between full-width sections.
