---
name: lp-deploy-2
description: "Convert a landing page from raw Gutenberg HTML blocks to native WordPress blocks for full editor editability. Use this when the user says 'convert to blocks', 'convert to Gutenberg', 'lp-deploy-2', 'make the landing page editable', 'convert the HTML blocks', or 'Gutenberg conversion'. Requires lp-deploy-1 to have run successfully. Produces a native block version of the page that works in the Gutenberg editor."
---

# LP Deploy 2 — Convert HTML to Native Gutenberg Blocks

Take the raw HTML prototype (currently sitting in `wp:html` blocks) and convert it section by section to native WordPress blocks. The visual frontend should not change — only the editor experience improves.

The golden rule: **the frontend proven in deploy-1 is the reference. Every converted section must match it.**

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-deploy-2/LEARNED.md`
2. Read `lp/lp_state.md` — confirm the target page has status "HTML Live" and has a Post ID
3. Read `${CLAUDE_PLUGIN_ROOT}/skills/wp-page-builder/SKILL.md` — specifically the section "Step 3: Convert to Native Blocks". The conversion patterns in that skill (wp:cover, wp:columns, wp:group with layout attributes, wp:list, wp:image for icons) apply here exactly.
4. **Prefer the client's `wp/wp-cli.sh` helper** over raw `docker exec` commands. It auto-installs WP-CLI and passes the correct `--url` flag. The theme CSS file is `assets/css/custom-components.css` (not `custom.css`) for the healthcare-theme. Theme files can be edited directly via the client's `wp/healthcare-theme` symlink.
5. Get the current page content:

```bash
docker exec $CONTAINER wp --allow-root post get [POST_ID] \
  --field=post_content \
  --url=[SUBSITE_URL]
```

Save the current content as `/lp/deploy/[SLUG]-content.html` (this is your fallback if something goes wrong).

## Section-to-Block Mapping

Use this table to decide how to convert each landing page section. The class names match what lp-prototype produces.

| Section class | Native block approach |
|--------------|----------------------|
| `.site-header` | Template part (skip — already in theme header template) |
| `.hero-section` | `wp:cover` with background colour and inner text/button blocks |
| `.trust-bar` | `wp:group` with `layout: {type:"flex"}` containing `wp:paragraph` items |
| `.pain-points-section` | `wp:group` containing `wp:heading` + `wp:group` grid with `wp:paragraph` items |
| `.solution-section` | `wp:group` with `wp:heading` + `wp:paragraph` |
| `.features-section` | `wp:group` containing heading + `wp:group` with `layout: {type:"grid"}` for feature cards |
| `.testimonials-section` | `wp:group` containing heading + quote blocks (`wp:quote`) |
| `.process-section` | `wp:group` with heading + ordered `wp:list` |
| `.faq-section` | `wp:group` with heading + `wp:details` blocks (FAQ accordion) |
| `.locations-section` | `wp:group` containing heading, paragraph, and location `wp:html` (dynamic content — keep as `wp:html` since it uses CPT data) |
| `.site-footer` | Template part (skip — already in theme footer template) |

**Keep as `wp:html` only if:**
- The section uses JavaScript that can't be replicated natively (complex animations)
- It relies on dynamic CPT data (locations grid)
- Converting it would change the visual output and you can't resolve the discrepancy
- Custom button classes (`.btn .btn--primary`) on bare `<a>` tags are used, since `wp:button` wraps `<a>` inside `<div class="wp-block-button">`, breaking CSS targeting
- JS-driven FAQ accordion using `<button>` pattern with `.is-open` class toggling (converting to `wp:details` would lose single-open-at-a-time behaviour from frontend.js)
- Hero sections with CSS grid (`hero__grid`), trust strip `<span>` elements, and custom button classes have too many inline elements with no native block equivalent
- Announcement bar with inline `<span>` elements and pipe dividers (no native block equivalent)

**Nesting `wp:html` inside `wp:group` is fine.** The HTML block renders correctly and the parent group remains editable in Gutenberg. Use this pattern for button groups or complex elements inside an otherwise native section.

If keeping a section as `wp:html`, document why in `lp_state.md`.

## Conversion Rules

### Do NOT use WP layout attributes when prototype CSS handles responsive grid/flex

If the prototype CSS already defines `display: grid` or `display: flex` with `@media` queries for responsive breakpoints, do NOT add WP layout attributes (`layout: {type: "grid"}`). WP grid layout ignores `@media` queries and breaks responsive breakpoints. Use `wp:group` with `className` only and let the prototype CSS handle the layout.

### CSS specificity: prototype CSS always wins over WP defaults

WP `is-layout-flow` margin rules use `:where()` selectors (0 specificity). Any prototype CSS with class or element selectors wins automatically without `!important`.

### `wp:group` with `className` preserves custom classes

WP adds `wp-block-group` and `is-layout-flow` alongside your custom classes. Custom CSS `display: grid`/`display: flex` overrides WP's `is-layout-flow` block display via specificity.

### Reveal animation limitations on native blocks

`data-delay` attributes for staggered IntersectionObserver reveal animations can't be added to native blocks. Accept simultaneous fade-in as a trade-off for editor editability. `.reveal { opacity: 0 }` works on real page scroll but causes elements to appear invisible in Playwright `fullPage` screenshots. Verify by programmatically scrolling or evaluating `document.querySelectorAll('.reveal.is-visible').length`.

## Conversion Process

Convert one section at a time. After each section, re-push and visually compare.

### Hero Section
```html
<!-- wp:cover {"backgroundColor":"primary","align":"full","className":"hero-section","minHeight":600} -->
<div class="wp-block-cover alignfull hero-section has-primary-background-color has-background" style="min-height:600px">
  <div class="wp-block-cover__inner-container">
    <!-- wp:heading {"level":1,"className":"hero-headline"} -->
    <h1 class="wp-block-heading hero-headline">[HEADLINE]</h1>
    <!-- /wp:heading -->
    <!-- wp:paragraph {"className":"hero-subheadline"} -->
    <p class="hero-subheadline">[SUBHEADLINE]</p>
    <!-- /wp:paragraph -->
    <!-- wp:buttons {"className":"hero-cta-group"} -->
    <div class="wp-block-buttons hero-cta-group">
      <!-- wp:button {"className":"hero-cta btn-primary"} -->
      <div class="wp-block-button hero-cta btn-primary">
        <a class="wp-block-button__link wp-element-button" href="#book">[CTA TEXT]</a>
      </div>
      <!-- /wp:button -->
    </div>
    <!-- /wp:buttons -->
    <!-- wp:paragraph {"className":"hero-cta-subtext"} -->
    <p class="hero-cta-subtext">[CTA SUBTEXT]</p>
    <!-- /wp:paragraph -->
  </div>
</div>
<!-- /wp:cover -->
```

### Trust Bar
```html
<!-- wp:group {"className":"trust-bar","layout":{"type":"flex","flexWrap":"wrap","justifyContent":"center"}} -->
<div class="wp-block-group trust-bar">
  <!-- wp:paragraph {"className":"trust-item"} -->
  <p class="trust-item"><strong class="trust-rating">[RATING]★</strong> [REVIEW COUNT] Google Reviews</p>
  <!-- /wp:paragraph -->
  <!-- wp:separator {"className":"trust-divider"} -->
  <hr class="wp-block-separator trust-divider" />
  <!-- /wp:separator -->
  <!-- wp:paragraph {"className":"trust-item"} -->
  <p class="trust-item">[STAT 1]</p>
  <!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
```

### Feature Grid (4-6 items)
```html
<!-- wp:group {"className":"features-section"} -->
<div class="wp-block-group features-section">
  <!-- wp:heading {"level":2,"className":"section-heading"} -->
  <h2 class="wp-block-heading section-heading">[HEADING]</h2>
  <!-- /wp:heading -->
  <!-- wp:group {"className":"features-grid","layout":{"type":"grid","columnCount":3,"minimumColumnWidth":"280px"}} -->
  <div class="wp-block-group features-grid">
    <!-- wp:group {"className":"feature-card"} -->
    <div class="wp-block-group feature-card">
      <!-- wp:heading {"level":3,"className":"feature-title"} -->
      <h3 class="wp-block-heading feature-title">[FEATURE]</h3>
      <!-- /wp:heading -->
      <!-- wp:paragraph {"className":"feature-body"} -->
      <p class="feature-body">[DESCRIPTION]</p>
      <!-- /wp:paragraph -->
    </div>
    <!-- /wp:group -->
    <!-- repeat for each feature -->
  </div>
  <!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### Testimonials
```html
<!-- wp:group {"className":"testimonials-section"} -->
<div class="wp-block-group testimonials-section">
  <!-- wp:heading {"level":2,"className":"section-heading"} -->
  <h2 class="wp-block-heading section-heading">[HEADING]</h2>
  <!-- /wp:heading -->
  <!-- wp:group {"className":"testimonials-grid","layout":{"type":"grid","columnCount":2}} -->
  <div class="wp-block-group testimonials-grid">
    <!-- wp:quote {"className":"testimonial-card"} -->
    <blockquote class="wp-block-quote testimonial-card">
      <!-- wp:paragraph -->
      <p>[QUOTE]</p>
      <!-- /wp:paragraph -->
      <cite>[NAME], [SUBURB]</cite>
    </blockquote>
    <!-- /wp:quote -->
    <!-- repeat -->
  </div>
  <!-- /wp:group -->
</div>
<!-- /wp:group -->
```

### FAQ Section (using wp:details)
```html
<!-- wp:group {"className":"faq-section"} -->
<div class="wp-block-group faq-section">
  <!-- wp:heading {"level":2,"className":"section-heading"} -->
  <h2 class="wp-block-heading section-heading">[FAQ HEADING]</h2>
  <!-- /wp:heading -->
  <!-- wp:details {"className":"faq-item"} -->
  <details class="wp-block-details faq-item">
    <summary>[QUESTION]</summary>
    <!-- wp:paragraph -->
    <p>[ANSWER]</p>
    <!-- /wp:paragraph -->
  </details>
  <!-- /wp:details -->
  <!-- repeat for each FAQ -->
</div>
<!-- /wp:group -->
```

Note: `wp:details` requires WordPress 6.4+. If the site runs an earlier version, keep FAQ as `wp:html`.

## kses and Content Placement Warnings

### kses Strips Iframes
`wp_update_post()` runs content through kses sanitisation which strips `<iframe>` tags (Google Maps embeds, videos). Use `$wpdb->update()` on the posts table directly + `clean_post_cache($pid)` to bypass. See `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for the full pattern.

### Content Placement in Gutenberg Blocks
When inserting content into `wp:group` blocks via regex or string replacement, the new content must go BEFORE the closing `</div>`, not between `</div>` and `<!-- /wp:group -->`. The `</div>` closes the rendered DOM element. Anything placed after it but before the block comment renders outside the component in the DOM.

### Link Colour in Dark Sections
"Learn more" links and other `::after` arrow pseudo-elements need explicit `color: var(--healthcare-primary)` (or the appropriate brand colour). Colour inheritance can fail when the parent `<p>` gets overridden by block editor paragraph styles.

## Push and Verify After Each Section

After converting a section, save the block markup to `/lp/deploy/[SLUG]-content-blocks.html` and push:

```bash
docker cp lp/deploy/[SLUG]-content-blocks.html $CONTAINER:/tmp/[SLUG]-content-blocks.html

docker exec $CONTAINER wp --allow-root post update [POST_ID] \
  --post_content="$(docker exec $CONTAINER cat /tmp/[SLUG]-content-blocks.html)" \
  --url=[SUBSITE_URL]
```

Check the frontend after each section push. If a section looks wrong after conversion, the issue is in the block structure (not the CSS — deploy-1 proved the CSS works). Fix block structure and re-push before moving on.

## Editor QA

After all sections are converted, open the block editor and verify:

1. Every section has visible, editable content (no blank white space)
2. Multi-column layouts show columns, not stacked rows
3. All text (headings, paragraphs, CTAs) is editable inline
4. No unexplained `wp:html` blocks except documented exceptions
5. The locations section (if it uses CPT data) is clearly labelled as an intentional `wp:html` block

Tell the user the results:
> "Editor QA: [N] sections converted to native blocks. [SECTION] kept as HTML because [REASON]. Full editor editability confirmed."

## Update State File

Update `/lp/lp_state.md`:
- Change page status to "Blocks Live"
- Note any sections kept as `wp:html` with reasons

```markdown
| [Ad Group] | ... | /lp/deploy/[slug]-content-blocks.html | [POST_ID] | Blocks Live |
```

## Handoff

Tell the user:

> "Page is now fully editable in Gutenberg at [SUBSITE_URL]wp-admin/post.php?post=[POST_ID]&action=edit
>
> Run **lp-deploy-3** to build the remaining landing pages."
