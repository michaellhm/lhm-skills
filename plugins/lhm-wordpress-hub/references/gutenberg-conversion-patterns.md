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

### FAQ Accordion (core/details — NEVER wp:html)

An expand/collapse FAQ is a native block. `core/details` renders a real `<details>/<summary>` with no JavaScript, and it is fully editable in the canvas. Do not reach for `wp:html` here. The markup below is extracted verbatim from a shipped page (zero validation warnings):

```html
<!-- wp:group {"className":"faq-list","layout":{"type":"default"}} -->
<div class="wp-block-group faq-list">
<!-- wp:details {"className":"faq-item"} -->
<details class="wp-block-details faq-item"><summary>How often should a women's cut be booked?</summary>
<!-- wp:paragraph -->
<p>Most of Tumi's clients return on a six to eight week rhythm for a cut.</p>
<!-- /wp:paragraph -->
</details>
<!-- /wp:details -->
<!-- ...one wp:details per question... -->
</div>
<!-- /wp:group -->
```

CSS bridge: the open/close marker is styled on the summary, not the markup. Hide the native triangle and add your own:

```css
.faq-item > summary { list-style: none; cursor: pointer; }
.faq-item > summary::-webkit-details-marker { display: none; }
.faq-item > summary::after { content: "+"; /* position right */ }
.faq-item[open] > summary::after { content: "\00d7"; } /* × */
```

The answer body is real block content (paragraphs, lists, buttons) nested inside `<details>`, so the client edits it inline like any other block.

### Data / Hours Table (core/table — NEVER wp:html)

Any tabular data — opening hours, price lists, comparison rows — is `core/table`. It must be wrapped in `<figure class="wp-block-table">`. Extracted verbatim from a shipped page:

```html
<!-- wp:table {"className":"hours-table"} -->
<figure class="wp-block-table hours-table"><table><tbody>
<tr><td>Monday</td><td>10:00 – 18:00</td></tr>
<tr><td>Tuesday</td><td>10:00 – 20:00</td></tr>
<tr><td>Sunday</td><td><em>Closed</em></td></tr>
</tbody></table></figure>
<!-- /wp:table -->
```

Use `<thead>` for a header row when the prototype has one. Inline emphasis (`<em>`, `<strong>`, `<a>`) inside cells is valid and stays editable.

### Section Separator (core/separator)

A horizontal rule / hairline divider is `core/separator`, not a styled `<div>` in `wp:html`:

```html
<!-- wp:separator {"className":"hairline"} -->
<hr class="wp-block-separator has-alpha-channel-opacity hairline"/>
<!-- /wp:separator -->
```

Keep `has-alpha-channel-opacity` — Gutenberg adds it by default and the validator expects it. Your `.hairline` class controls colour/width/margin.

### Editorial 2-Column Split (image + text, className-only)

A text-beside-image band where the prototype CSS already defines the two-column grid with `@media` collapse. Do NOT use `wp:columns` or WP grid layout here — a plain `className` group lets the prototype CSS drive structure AND responsiveness. Each side is its own `wp:group`; the image is a real `wp:image` (swappable in the editor), not a CSS background. Extracted verbatim:

```html
<!-- wp:group {"className":"editorial-2col","layout":{"type":"default"}} -->
<div class="wp-block-group editorial-2col">
<!-- wp:group {"className":"editorial-2col__image","layout":{"type":"default"}} -->
<div class="wp-block-group editorial-2col__image">
<!-- wp:image {"sizeSlug":"full","className":"size-full"} -->
<figure class="wp-block-image size-full"><img src="/wp-content/themes/theme-slug/assets/images/intro-image.webp" alt="Descriptive alt."/></figure>
<!-- /wp:image -->
</div>
<!-- /wp:group -->
<!-- wp:group {"layout":{"type":"default"}} -->
<div class="wp-block-group">
<!-- wp:paragraph {"className":"eyebrow"} --><p class="eyebrow"><span class="eyebrow__rule"></span>The Story</p><!-- /wp:paragraph -->
<!-- wp:heading --><h2 class="wp-block-heading">Heading</h2><!-- /wp:heading -->
<!-- wp:paragraph --><p>Body copy.</p><!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

To alternate image/text sides per row, add a modifier class (e.g. `editorial-2col--reverse` or `subservice-row--reverse`) and let CSS flip `flex-direction`/`order`. This is the pattern behind alternating "Approach / Work / Hair Spa"-style stacks — each row is a `subservice-row` group, the stack is a `subservice-stack` group, all className-only.

### Whole-Card Link (drop the outer anchor)

In a prototype, an entire card is often wrapped in `<a class="card">…</a>`. Gutenberg has no "group that is a link" block, so do NOT keep the card as `wp:html` to preserve the wrapper. Instead, drop the outer `<a>` and link the heading and/or an explicit CTA inside the card. The card stays a normal editable `wp:group`:

```html
<!-- wp:group {"className":"subservice-row__link-card","layout":{"type":"default"}} -->
<div class="wp-block-group subservice-row__link-card">
<!-- wp:heading {"level":3} --><h3 class="wp-block-heading"><a href="/womens-cuts">Women's Cuts</a></h3><!-- /wp:heading -->
<!-- wp:paragraph --><p>Short description.</p><!-- /wp:paragraph -->
<!-- wp:paragraph --><p><a class="subservice-row__link" href="/womens-cuts">Explore women's cuts →</a></p><!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
```

If the prototype relied on the whole card being clickable, restore that with a tiny progressive-enhancement script that makes `.subservice-row__link-card` clickable via its inner link — but the editable structure stays native.

### The Only Legitimate wp:html: Plugins & iframes

`wp:html` survives in exactly two cases. Document each with the editor warning. Examples:

```html
<!-- Plugin-rendered form (Gravity Forms / CF7 shortcode placeholder) -->
<!-- wp:html -->
<form class="enquiry-form" aria-label="Enquiry form">…fields…</form>
<!-- /wp:html -->

<!-- iframe embed (Google Map / video) -->
<!-- wp:html -->
<iframe src="https://www.google.com/maps/embed?…" loading="lazy" title="Salon location"></iframe>
<!-- /wp:html -->
```

In production the form `wp:html` is replaced by the actual plugin shortcode (`[gravityform id="1"]`), which is itself editable as a shortcode block. Nothing else qualifies — "bespoke", "complex", or "custom grid" all have native paths above.

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

If your prototype CSS defines `display: grid`/`flex` with `@media` queries for mobile/tablet, do NOT add `layout: {type: "grid"}` to the block. WP grid ignores media queries and breaks responsive behaviour. Use `wp:group` with `className` only and let prototype CSS handle structure AND breakpoints.

**This is the default for prototype-driven builds** — the prototype CSS was extracted into the theme, so it already owns the grid. Reserve `layout: {type:"grid"|"flex"}` for *new* sections you author without responsive CSS (see the Card Grid / Features Grid examples above, which assume no prototype `@media`). When in doubt, className-only is the safe choice: it never fights the prototype. See "Editorial 2-Column Split" and "Alternating Subservice Rows" above for className-only multi-column markup.

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

**No exception — custom-styled buttons still convert.** If prototype CSS targets bare `.btn` on `<a>` tags, do NOT keep the button as `wp:html`. Move the `className` onto `wp:button` and retarget the prototype CSS at the WP anchor. The block renders `<div class="wp-block-button btn-group__item"><a class="wp-block-button__link wp-element-button btn btn--primary">`. Either keep your `.btn`/`.btn--primary` classes on the inner `<a>` (they ride alongside `wp-block-button__link`), or rewrite the selector to `.wp-block-button__link`. Both keep the button fully editable. `wp:html` is reserved for plugins and iframes only — a styled anchor is neither.

```html
<!-- wp:buttons {"className":"btn-group"} -->
<div class="wp-block-buttons btn-group">
<!-- wp:button {"className":"btn btn--primary"} -->
<div class="wp-block-button btn btn--primary"><a class="wp-block-button__link wp-element-button" href="/contact">Book a consultation</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
```

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
