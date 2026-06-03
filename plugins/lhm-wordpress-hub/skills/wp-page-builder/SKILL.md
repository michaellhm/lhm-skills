---
name: wp-page-builder
description: "Build individual pages in WordPress from content and design artefacts. Use this when the user says 'build pages', 'create pages in WordPress', 'page builder', 'add pages to WordPress', 'build the homepage', or 'WP build'. Phase 5 of the website build. Requires content files, design system, and theme installed."
---

# WP Page Builder

Build individual pages in WordPress using a two-step process: first push the raw HTML prototype to prove the design works, then convert to native WordPress blocks for editor editability.

## Before Starting

1. **Read content files** - scan `/content/` for all page files
2. **Read block specs** - read `/design/blocks.md` for component-to-pattern mapping. Pay attention to **WP layout**, **Prototype classes**, **Icon strategy**, and **Editor compatible** fields
3. **Read conversion patterns** - read `${CLAUDE_PLUGIN_ROOT}/references/gutenberg-conversion-patterns.md`. This is the single source of truth for block markup. Every section you convert in Step 3 MUST follow these patterns exactly. The patterns are extracted from production sites and are proven to work.
4. **Read custom CSS** - read `/wp/theme/{theme-slug}/assets/css/custom.css` for all available CSS classes
5. **Read editor CSS** - read `/wp/theme/{theme-slug}/assets/css/editor.css` to understand editor overrides
6. **Read the homepage prototype** - read the approved version from `/design/prototype/homepage/` (e.g. `index.html` or the specific approved version like `v2.html`) as the pixel-perfect visual reference
7. **Read WP state** - read `/wp/wp_state.md` to see what's already built
8. **Read WP-CLI reference** - read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md`
9. **Read viewport reference** - read `${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/references/viewports.md` for standard breakpoint sizes
10. **Run CSS sync check** - run the `css-sync-check` skill to diff the prototype CSS against the theme CSS. Class names will match but styling rules often diverge during theme scaffold. Fix CSS discrepancies BEFORE pushing page content, not after. This check also verifies the `.container` class exists with `max-width`, `margin: 0 auto`, and gutter padding (the single highest-impact missing class).
11. **Verify logo is set** - the `wp:site-logo` block in the header requires a logo attachment via Customizer theme_mods (`custom_logo` key). Upload via `wp media import [url]` then set via `wp option update theme_mods_[theme-slug]`. Without this, the header logo area is blank.
12. Verify the theme is installed and activated

**Playwright MCP tools are available** for screenshotting and visual comparison. Key tools used in this skill: `mcp__playwright__browser_navigate`, `mcp__playwright__browser_resize`, `mcp__playwright__browser_take_screenshot`, `mcp__playwright__browser_wait_for`, `mcp__playwright__browser_evaluate`. If the browser is not installed, run `mcp__playwright__browser_install` first. Note: `file://` URLs are blocked in Playwright MCP. To screenshot local prototypes, run `python3 -m http.server [port] --directory [path]` and navigate to `http://localhost:[port]/filename.html`.

## Step 1: Build Order

Use the `AskUserQuestion` tool:

> "Which pages should I build?"

Options:
- "Homepage first" (recommended)
- "All pages in order"
- "Specific page" (let them choose)

### Recommended Build Order
1. Homepage — sets the visual direction
2. Contact page — simple, gets a CTA destination live
3. About page — establishes brand story
4. Service pages — core content
5. Location pages — if applicable
6. FAQ — supporting content
7. Utility pages — privacy, terms

### Parallel Agent Strategy for Multi-Page Builds

When converting multiple pages simultaneously (not sequentially), spin out one parallel agent per page rather than running them in series. Each agent needs a detailed shared prompt containing the complete block pattern library extracted from the homepage reference — section wrappers, feature blocks, pricing cards, FAQ items, CTA, review cards, and any site-specific patterns. This produces consistent block markup across all pages at once rather than introducing drift when patterns are re-derived page by page.

The shared prompt must include:
- The full pattern reference (copy directly from the homepage-content-blocks.html or gutenberg-conversion-patterns.md)
- The exact prototype CSS class names to preserve
- The WP-CLI command pattern with the correct `--url` flag if on multisite
- Which sections are candidates for Synced Patterns (see below)

## Step 2: Push Raw HTML Prototype (Prove the Design)

**This step establishes a proven visual baseline in WordPress.** Take the HTML prototype body content and push it directly into WordPress. The prototype HTML goes in as-is.

### Why this step matters

The theme's `custom.css` was extracted from the same prototype. The CSS classes match exactly. The frontend renders pixel-perfect immediately. This gives you:
- Proof that the theme CSS works correctly in WordPress
- A working visual baseline to compare against during native block conversion
- Immediate client review of the design in a real WordPress environment

### WordPress CSS Resets Required

WordPress adds default block gap margins that create visible white strips between full-width sections. Add these resets to `custom.css` if not already present:

```css
/* Reset WP default block gaps */
.wp-site-blocks > * + *,
.is-layout-flow > * + * {
  margin-block-start: 0;
}
```

Also watch for WordPress block group `display` styles overriding component CSS. For example, a `.sticky-cta { display: none }` rule gets overridden by WP's `.wp-block-group` display. Fix with specificity: `.wp-block-group.sticky-cta { display: none !important }` inside a media query.

### How to do it

1. Extract the `<body>` content from the prototype HTML (everything between `<body>` and `</body>`, excluding header and footer which are already in template parts)
2. **Wrap each section in a separate `<!-- wp:html -->` block** (hero, services, FAQ, CTA, etc.). One monolithic HTML block is impossible to debug and edit.
3. Save it to `/wp/homepage-content.html`
4. Push to WordPress:

```bash
# Create or update the page with raw HTML
wp post create --post_type=page \
  --post_title="Home" \
  --post_name="home" \
  --post_status=publish \
  --post_content="$(cat wp/homepage-content.html)"

# Set as homepage
wp option update show_on_front page
wp option update page_on_front <page_id>
```

**Don't trust the stdout of a `post update --post_content="$(cat ...)"`.** When the HTML content is large, WP-CLI often echoes output that LOOKS like an argument-parse error (the tail of the file content followed by something like `in 'cli'`) even though the update succeeded. Never conclude the push failed from that message alone. Verify by comparing byte counts and block markers: `wp post get <id> --field=content | wc -c` against the source file, and grep the stored content for expected block comments (`<!-- wp:`). Trust the DB, not the echo.

### Multisite Considerations

On WordPress multisite installations, **every WP-CLI command** needs the `--url` flag pointing to the correct subsite:

```bash
# All commands must include --url for the target subsite
wp post create --post_type=page \
  --post_title="Page Title" \
  --post_status=publish \
  --url=http://localhost:8083/ehp/ \
  --post_content="$(cat wp/page-content.html)"
```

**Prefer the client's `wp/wp-cli.sh` helper** over raw `docker exec` commands where available. It auto-installs WP-CLI (which is ephemeral in `wordpress:6.7-php8.2-apache`) and passes the correct `--url` flag. The healthcare-theme CSS file is `assets/css/custom-components.css` (not `custom.css`). Theme files can be edited directly via the client's `wp/healthcare-theme` symlink to the central canonical copy.

When running inside Docker without the helper, use `docker cp` to get content files into the container, then `cat` from inside:

```bash
docker cp wp/page-content.html wp-wordpress-1:/tmp/page-content.html
docker exec wp-wordpress-1 wp --allow-root post create \
  --post_type=page \
  --post_title="Page Title" \
  --post_status=publish \
  --url=http://localhost:8083/ehp/ \
  --post_content="$(docker exec wp-wordpress-1 cat /tmp/page-content.html)"
```

If the theme uses Location CPTs (or similar) for dynamic data (phone numbers, addresses), link the location to the page after creation:

```bash
wp post meta update <page_id> _healthcare_location_id <location_id> --url=http://localhost:8083/ehp/
```

4. Verify the frontend renders pixel-perfect. If it doesn't, the issue is in the CSS extraction (theme-scaffold step), not in the block conversion

### Template hierarchy warning

If the site will have a blog, use `front-page.html` (not `home.html`) for the homepage template. WordPress reserves `home.html` for the blog posts index when `show_on_front = page`. If you build the homepage using `home.html` and later add a blog, you'll need to rename the homepage template to `front-page.html` and create a new `home.html` for the blog listing. Plan this from the start.

### What you get
- Pixel-perfect frontend rendering
- A working reference page

### What you don't get
- Editor editability (the entire page is raw HTML in the editor)

**This is intentional.** Step 2 solves the visual problem. Step 3 solves the editor problem.

### Screenshot Comparison: HTML Push vs Prototype

Before asking for approval, run an automated visual check at two viewports (Desktop Standard and Mobile Standard). This catches CSS issues before the user has to eyeball anything.

**For each viewport (Desktop Standard 1440x900, Mobile Standard 390x844):**

1. **Resize the viewport:**
   ```
   mcp__playwright__browser_resize → width: [width], height: [height]
   ```

2. **Screenshot the prototype** (skip if already captured for this page):
   ```
   mcp__playwright__browser_navigate → url: "file:///[absolute-path]/design/prototype/{slug}/index.html"
   mcp__playwright__browser_wait_for → wait for network idle
   mcp__playwright__browser_take_screenshot
   ```
   Save to `/qa/{page-slug}/prototype-desktop-standard.png` and `prototype-mobile-standard.png`

3. **Screenshot the live WordPress page:**
   ```
   mcp__playwright__browser_navigate → url: "[wordpress-url]/{page-slug}"
   mcp__playwright__browser_wait_for → wait for network idle
   mcp__playwright__browser_evaluate → document.getElementById('wpadminbar')?.remove()
   mcp__playwright__browser_take_screenshot
   ```
   Save to `/qa/{page-slug}/html-push-desktop-standard.png` and `html-push-mobile-standard.png`

4. **Visually compare** each pair using your multimodal vision. Check:
   - Layout structure matches
   - Colors and backgrounds render correctly
   - Typography loads and displays correctly
   - Spacing and alignment are consistent
   - No broken images or missing elements

5. **If issues found:** fix the CSS/markup, re-push, re-screenshot, and verify the fix before proceeding

This is a lightweight 2-viewport check. The full 8-viewport visual-qa pass with accessibility, hover states, and computed styles runs before launch.

### Approval Gate: Confirm Before Block Conversion

Use the `AskUserQuestion` tool:

> "Raw HTML page is live in WordPress. Check the frontend — does it match the prototype? Approved to convert to Gutenberg blocks?"

Options:
- "Looks good — convert to blocks"
- "CSS issues — needs fixes first"
- "Move to next page (stay as HTML for now)"

**Do not proceed to Step 3 without approval.** If the user reports CSS issues, debug the theme CSS extraction (Step 2 of theme-scaffold) before converting to blocks. If the user skips to the next page, note that this page is still raw HTML in `wp_state.md` and return to block conversion later.

## Step 3: Convert to Native Blocks (Editor Experience)

With the proven frontend as your reference, systematically convert each section from raw HTML to native WordPress blocks. After each section is converted, compare the frontend against the Step 2 baseline to catch any visual regressions.

### The `wp:html` Policy (Strict)

Once the HTML baseline is approved, the page converts to **100% native Gutenberg blocks**. `wp:html` is permitted in exactly **two** cases:

1. **A plugin renders the section** — its shortcode / widget / block (e.g. an Elfsight reviews widget, a Gravity Forms / Contact Form 7 form, a booking widget).
2. **The section is an `<iframe>` embed** — Google Maps, a YouTube video, or a similar third-party embed.

**Nothing else qualifies.** "Bespoke", "complex", or "has a custom CSS grid" is NEVER a reason to keep `wp:html` — every one of those has a native equivalent and MUST be converted:

| Section type | Native block (NOT `wp:html`) |
|---|---|
| Bespoke CSS grid / card grid | `wp:group` with `className` only — the prototype CSS drives the grid |
| FAQ accordion | `wp:details` (one per question) |
| Data / pricing / hours table | `wp:table` |
| Hero / any section with a background image or video | `wp:cover` |
| Buttons with custom classes (`.btn`, `.btn--primary`) | `wp:buttons` + `wp:button` with `className`; style `.wp-block-button__link` in CSS |
| "Whole-card" link wrapping multiple blocks | Drop the outer `<a>`; make the card heading (or its CTA button) the link |
| Icons | `wp:image` with an SVG file, or emoji in `wp:paragraph` |

If you reach for `wp:html` for anything other than the two allowed cases, stop and convert it instead. This is the single most common cause of a build that looks finished on the frontend but is uneditable in the editor.

### Section Inventory (Mandatory First Step)

Before converting anything, create a complete inventory of every section on the page. This prevents the "half converted" problem where some sections get done and others are missed.

1. List every section by its class name, in order from top to bottom
2. For each section the default is **convert to native blocks**. Mark a section `wp:html` ONLY if it meets one of the two exceptions in the wp:html Policy above (plugin-rendered or iframe embed) — and note which one. If you can't name the plugin or the iframe, it converts.
3. Present the inventory to the user for approval before starting conversion

Do not start converting until the user approves the inventory.

### Synced Patterns for Identical Sections

Use WordPress Synced Patterns (`wp_block` post type) for sections that are character-identical across multiple pages — for example, a reviews/testimonials block that appears unchanged on every service page. A Synced Pattern means a single edit updates all pages simultaneously.

**Create a Synced Pattern via WP-CLI:**

```bash
# Create the synced pattern
wp post create \
  --post_type=wp_block \
  --post_title="Reviews Section" \
  --post_status=publish \
  --post_content="$(cat wp/reviews-section.html)"
# Note the returned post ID (e.g. 88)
```

**Reference it in any page:**

```html
<!-- wp:block {"ref":88} /-->
```

**When NOT to use a Synced Pattern:** sections that vary per page — even slightly — should remain independent blocks. For example, a "Final CTA" section where the heading and button text differ per service page has SEO and contextual value in being unique. Syncing it would force the same copy everywhere. Keep those as standalone `wp:group` blocks on each page.

### The Mandatory Full-Width Pattern

Every section that spans the full viewport width in the prototype MUST use this nesting:

```html
<!-- wp:group {"className":"section-name","align":"full","layout":{"type":"default"}} -->
<div class="wp-block-group alignfull section-name">
<!-- wp:group {"className":"container","layout":{"type":"default"}} -->
<div class="wp-block-group container">
  <!-- inner content blocks -->
</div>
<!-- /wp:group -->
</div>
<!-- /wp:group -->
```

This is the #1 reason conversions fail. Without `"align":"full"` AND `alignfull` on the div, sections are constrained to `contentSize` from theme.json (~800px), causing the page to appear ~600px wide in the editor. See `${CLAUDE_PLUGIN_ROOT}/references/gutenberg-conversion-patterns.md` for the full set of proven patterns for every section type.

### The Dual-Rendering Principle

The WordPress block editor and the frontend are two different rendering environments. Every block must work in both:

| Concern | Handled By | Works in Editor? |
|---|---|---|
| Grid/column structure | WP layout attributes (`type:"grid"`, `type:"flex"`) or `wp:columns` | Yes |
| Flex layout | WP flex layout or `wp:buttons` | Yes |
| Colors, backgrounds | Custom CSS classes | Yes (loaded via editor stylesheet) |
| Typography | Custom CSS classes + theme.json | Yes |
| Borders, radius, shadows | Custom CSS classes | Yes |
| Padding, margins | WP spacing attributes OR CSS classes | Yes |
| Animations (scroll reveal, etc.) | Custom CSS (overridden by editor.css) | Needs override |
| Icons | `wp:image` with SVG files, or emoji | Yes |
| Video backgrounds | `wp:cover` with `backgroundType:"video"` | Yes |
| Lists with custom markers | `wp:list` + `wp:list-item` | Yes |

**The rule: WP layout attributes for structure. CSS classes for style.**

### Conversion Order (recommended)

1. **Simple text sections first** (headings, paragraphs, buttons) — convert 1:1 to native blocks
2. **List sections** (checklists, feature lists, fit/not-fit) — use `wp:list` + `wp:list-item`
3. **Multi-column layouts** (card grids, feature grids, steps) — use WP layout attributes (`type:"grid"` or `type:"flex"`)
4. **Background sections** (hero, CTA with background image/video) — use `wp:cover`
5. **Icon elements** — use `wp:image` with SVG files from `assets/icons/`, or emoji in `wp:paragraph`
6. **Plugin-rendered or iframe sections** — these are the ONLY sections that stay `wp:html` (see the wp:html Policy above). Everything else, however "complex" or "bespoke", converts to native blocks. FAQ accordions → `wp:details`; data/hours tables → `wp:table`.

### Using WP Layout Attributes for Multi-Column Sections

**Warning: Do NOT use WP layout attributes when prototype CSS already handles responsive grid/flex.** WP grid layout (`layout: {type: "grid", columnCount: 3}`) ignores `@media` queries and breaks responsive breakpoints. If the prototype CSS defines `display: grid` with media queries, use `wp:group` with `className` only and let the prototype CSS handle layout. WP `is-layout-flow` margin rules use `:where()` selectors (0 specificity), so prototype CSS with class or element selectors wins automatically without `!important`.

**`wp:button` with custom classes — convert, don't fall back:** The prototype's `.btn .btn--primary` sits on a bare `<a>`, whereas `wp:button` wraps it as `<div class="wp-block-button {className}"><a class="wp-block-button__link wp-element-button">`. Convert anyway — do NOT use `wp:html` for buttons. Put the modifier class on the button via `className` (e.g. `<!-- wp:button {"className":"btn btn--primary"} -->`) and point the prototype's button CSS at `.wp-block-button__link` (or `.btn .wp-block-button__link`). A button is never a reason to keep a section as raw HTML.

When prototype CSS does NOT handle layout (e.g. new sections without responsive CSS), use WP's native layout attributes:

**Grid layout (equal columns):**
```html
<!-- wp:group {"className":"card-grid","layout":{"type":"grid","columnCount":3}} -->
<div class="wp-block-group card-grid">
  <!-- child blocks here, one per grid cell -->
</div>
<!-- /wp:group -->
```

**Flex layout (horizontal row):**
```html
<!-- wp:group {"className":"trust-bar","layout":{"type":"flex","flexWrap":"nowrap","justifyContent":"space-between"}} -->
<div class="wp-block-group trust-bar">
  <!-- child blocks here -->
</div>
<!-- /wp:group -->
```

**Two-column split (text + image):**
```html
<!-- wp:columns {"className":"image-text-split"} -->
<div class="wp-block-columns image-text-split">
  <!-- wp:column -->
  <div class="wp-block-column"><!-- text content --></div>
  <!-- /wp:column -->
  <!-- wp:column -->
  <div class="wp-block-column"><!-- image --></div>
  <!-- /wp:column -->
</div>
<!-- /wp:columns -->
```

### Using `wp:cover` for Hero/Background Sections

Any section with a background image, video, or color overlay MUST use `wp:cover`, not `wp:html`:

```html
<!-- wp:cover {"url":"video.mp4","backgroundType":"video","dimRatio":70,"overlayColor":"primary-dark","align":"full","className":"hero-section"} -->
<div class="wp-block-cover alignfull hero-section">
  <span class="wp-block-cover__background has-primary-dark-background-color has-background-dim-70 has-background-dim"></span>
  <video class="wp-block-cover__video-background" autoplay muted loop playsinline src="video.mp4"></video>
  <div class="wp-block-cover__inner-container">
    <!-- wp:heading {"level":1,"className":"hero-title"} -->
    <h1 class="wp-block-heading hero-title">Your Headline</h1>
    <!-- /wp:heading -->
    <!-- wp:paragraph {"className":"hero-subtitle"} -->
    <p class="hero-subtitle">Your subtitle text.</p>
    <!-- /wp:paragraph -->
    <!-- wp:buttons -->
    <div class="wp-block-buttons">
      <!-- wp:button {"className":"hero-cta"} -->
      <div class="wp-block-button hero-cta"><a class="wp-block-button__link wp-element-button" href="/contact">Book Now</a></div>
      <!-- /wp:button -->
    </div>
    <!-- /wp:buttons -->
  </div>
</div>
<!-- /wp:cover -->
```

The editor will show the video background with overlay and all content is editable in-place.

**Video background + custom gradient overlay is serialization-sensitive — recover it, don't hand-author it.** A `wp:cover` with a video background AND a gradient overlay (rather than the solid `overlayColor` shown above) frequently fails block validation when typed by hand. Canonical serialization for that variant puts the `<video class="wp-block-cover__video-background intrinsic-ignore" autoplay muted loop playsinline ...>` element BEFORE the overlay `<span>`, and the gradient span carries the exact class string `has-background-dim-100 has-background-dim wp-block-cover__gradient-background has-background-gradient`. Get one token wrong and the editor flags "unexpected or invalid content".

Rather than guess this markup, **recover the canonical form from the editor**: insert the block, open the page in the editor, then for any block flagged invalid run —
```js
// In the editor console (or via Playwright browser_evaluate)
const { getBlocks } = wp.data.select('core/block-editor');
const target = /* the invalid block's clientId */;
const b = getBlocks().find(x => x.clientId === target);
const fresh = wp.blocks.createBlock(b.name, b.attributes, b.innerBlocks);
wp.data.dispatch('core/block-editor').replaceBlock(target, fresh);
await wp.data.dispatch('core/editor').savePost();
```
Then pull the now-canonical content back into your source `.html` file: `wp post get <id> --field=content`. This recovers valid markup straight from Gutenberg's own serializer instead of trial-and-error.

### Using `wp:image` for Icons

Do NOT use inline SVG in `wp:html` blocks for icons. They're invisible in the editor.

```html
<!-- wp:image {"className":"card-icon","sizeSlug":"full"} -->
<figure class="wp-block-image size-full card-icon">
  <img src="/wp-content/themes/{theme-slug}/assets/icons/plumbing.svg" alt="Plumbing" />
</figure>
<!-- /wp:image -->
```

For simple decorative icons, emoji in a paragraph works well:
```html
<!-- wp:paragraph {"className":"industry-icon"} -->
<p class="industry-icon">🔧</p>
<!-- /wp:paragraph -->
```

### Using `wp:list` for List Content

All list content (checklists, feature lists, fit/not-fit sections) should use `wp:list` + `wp:list-item`:

```html
<!-- wp:list {"className":"checklist"} -->
<ul class="checklist">
  <!-- wp:list-item -->
  <li>Licensed and insured professionals</li>
  <!-- /wp:list-item -->
  <!-- wp:list-item -->
  <li>Same-day emergency service</li>
  <!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
```

Style checkmark icons via CSS `list-style-image` or `::marker` in `custom.css`.

### Scroll Animations

`.reveal` classes for IntersectionObserver scroll animations must be explicitly added to the page content HTML. They don't come from WordPress blocks or templates. Add `class="... reveal"` to each animatable element and `data-delay="N"` for stagger timing. Make sure `custom.js` with the IntersectionObserver code is enqueued by the theme.

#### Editor CSS Overrides Required for Animated Elements

Scroll-reveal CSS animations (e.g. `opacity:0; transform:translateY(30px)`) make elements invisible in the Gutenberg editor because the frontend IntersectionObserver JS never runs there. Any element that starts hidden via animation CSS will appear as blank white space in the editor. Fix this by adding overrides to `editor.css`:

```css
/* Reveal animation overrides — editor only */
.editor-styles-wrapper .reveal,
.editor-styles-wrapper [class*="fade"],
.editor-styles-wrapper [class*="slide"] {
  opacity: 1 !important;
  transform: none !important;
  transition: none !important;
}
```

Adjust selectors to match whatever animation classes the prototype uses. Load this via `enqueue_block_editor_assets` (same hook used for all other `editor.css` rules). The `!important` is required to override the inline-style-like specificity of animation CSS.

#### Body-Scoped Variant Styles Don't Reach the Editor Canvas

If the theme applies a per-page "variant" scope class via the PHP `body_class` filter (e.g. `.variant-warm` on `<body>` swapping fonts or section backgrounds), that class never reaches the **iframed** Gutenberg editor canvas — and `admin_body_class` only sets the OUTER admin body, not the canvas. The result: every `.variant-scope` rule (fonts, section backgrounds) is missing while editing, so the editing surface diverges from the frontend even though the frontend is correct. Fix by enqueuing a small script via `enqueue_block_editor_assets` that adds the scope class to the canvas body, re-applying on remount:

```js
// editor-canvas-scope.js — enqueued via enqueue_block_editor_assets
( function () {
  const apply = () => {
    const iframe = document.querySelector('iframe[name="editor-canvas"]');
    iframe?.contentDocument?.body.classList.add('variant-warm'); // the active scope class
  };
  apply();
  new MutationObserver(apply).observe(document.body, { childList: true, subtree: true });
} )();
```

### kses Sanitisation Warning

`wp_update_post()` strips `<iframe>` tags via kses sanitisation. When pages contain Google Maps embeds or video iframes in `<!-- wp:html -->` blocks, use `$wpdb->update()` + `clean_post_cache()` instead. See `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md` for the full pattern.

### Content Placement in Gutenberg Blocks

When inserting content into `wp:group` blocks via string replacement, place new blocks BEFORE the closing `</div>`, not between `</div>` and `<!-- /wp:group -->`. The `</div>` closes the rendered DOM element. Anything after it renders outside the component.

### Inline Style Override Warning

Block editor inline padding (e.g. `style="padding:24px"`) overrides CSS class padding. Use `!important` on component CSS when the design requires larger/different padding than what the editor sets.

### Critical Rule: Use Exact Prototype Classes

The CSS in `custom.css` was extracted directly from the HTML prototype. The JS in `custom.js` (if present) targets elements by the same class names. For styles and interactions to work, the WordPress block markup MUST use the exact same classes.

**Rules:**
- Do NOT invent new class names. Only use classes that exist in `custom.css`
- Do NOT rename prototype classes (e.g. don't change `.hero-section` to `.theme-slug-hero`)
- If the prototype has a wrapper `<div class="card-grid">`, the WordPress block must also have `className: "card-grid"`
- WordPress will add its own classes (like `wp-block-group`, `is-layout-grid`) alongside yours. That's fine, they stack
- The custom CSS handles visual styling (colors, borders, spacing, typography). WP layout attributes handle structure (grid columns, flex direction). They work together

**Copy page-specific inline `<style>` blocks into the theme CSS — don't assume the shared stylesheet covers it.** A prototype page often carries its own inline `<style>` block (bespoke section classes: grids, cards, FAQ accordions, 2-col editorial) IN ADDITION to the shared `style.css`. When porting that page, those inline rules must be copied into the theme's `custom.css`. If skipped, the WP markup uses the correct class names but they're unstyled, so grids and 2-col layouts silently fall back to stacked block flow and the page "doesn't match the prototype". Before QA, diff every `.selector` in each prototype page's inline `<style>` against the theme CSS and confirm each definition is present (the inline blocks are often identical copies across pages, but verify per page — a class can be defined inline on one page and nowhere else).

### After Each Section Conversion

Compare the frontend against the Step 2 HTML baseline. If the converted version looks different, the issue is in the block structure, not the CSS (because Step 2 already proved the CSS works). Fix the block structure before moving to the next section.

### Screenshot Comparison: Block Conversion vs Prototype

After all sections are converted, run the same 2-viewport screenshot check to catch regressions introduced during block conversion. The prototype screenshots were already captured in Step 2.

**For each viewport (Desktop Standard 1440x900, Mobile Standard 390x844):**

1. **Resize, navigate to the WordPress page, remove admin bar, and screenshot** (same sequence as Step 2)
2. Save to `/qa/{page-slug}/blocks-desktop-standard.png` and `blocks-mobile-standard.png`
3. **Compare against the prototype screenshots** (`prototype-desktop-standard.png` and `prototype-mobile-standard.png`)
4. If regressions found: fix block structure, re-push, re-screenshot, and verify before proceeding

After this check passes, proceed to Editor QA (Step 5).

## Step 4: Save Both Content Files

Maintain two content files per page so you always have the proven HTML baseline to fall back to:

```
wp/
  homepage-content.html          # Raw HTML (Step 2 baseline)
  homepage-content-blocks.html   # Native block markup (Step 3 conversion)
```

Push the native block version to WordPress:

```bash
# Push converted native block content
wp post update <page_id> \
  --post_content="$(cat wp/homepage-content-blocks.html)"
```

## Step 5: Editor QA

**This step is mandatory.** After pushing the native block content, verify the block editor experience.

Open the block editor at `/wp-admin/post.php?post=<page_id>&action=edit` and check:

1. **Every section has visible, editable content** — no empty white space, no raw code
2. **Multi-column layouts show columns** — not stacked single-column blocks
3. **All text (headings, paragraphs, buttons, lists) is editable inline**
4. **Icons are visible** (even if not perfectly styled)
5. **Background images/videos are visible** (via wp:cover)
6. **No `wp:html` blocks are present** except the two allowed exceptions (plugin-rendered or iframe embed). Verify the count programmatically — see below.

### Verify Conversion Completeness (Programmatic — Mandatory)

Eyeballing the canvas misses blocks below the fold, so confirm the counts directly. Log into the editor, then via Playwright `browser_evaluate` (or the browser console) read the editor canvas iframe:

```js
const doc = document.querySelector('iframe[name="editor-canvas"]').contentDocument;
({
  htmlBlocks: doc.querySelectorAll('[data-type="core/html"]').length,
  warnings:   doc.querySelectorAll('.block-editor-warning').length,
});
```

- `warnings` MUST be `0` (no "this block contains unexpected or invalid content" blocks).
- `htmlBlocks` MUST equal the number of **documented plugin/iframe exceptions** for that page — and no more. If it's higher, a bespoke section was wrongly left as `wp:html`; go convert it.

The DOM `.block-editor-warning` count catches *rendered* warnings, but the most reliable validity check reads Gutenberg's own parse state — recurse `getBlocks()` and flag any block whose `isValid === false` (these don't always surface a visible warning node):

```js
const { getBlocks } = wp.data.select('core/block-editor');
const invalid = [];
(function walk(blocks){ blocks.forEach(b => { if (b.isValid === false) invalid.push(b.name); walk(b.innerBlocks || []); }); })(getBlocks());
invalid; // MUST be []
```

A frontend HTTP 200 and a matching screenshot prove the design *renders*. They do NOT prove *editability*. This count is the editability gate — do not declare a page done until it passes.

> **Screenshot gotcha:** sections carrying a `.reveal` scroll-animation class are `opacity:0` until the IntersectionObserver adds `.is-visible` on scroll. A Playwright `fullPage` screenshot does not trigger the observer, so converted content can look blank. Before screenshotting the frontend, force them visible: `browser_evaluate` → `document.querySelectorAll('.reveal').forEach(el=>el.classList.add('is-visible'))`. Blank ≠ broken.

If any section fails these checks, identify the issue:
- **Layout stacked vertically** → Switch to WP native layout attributes (`type:"grid"` or `type:"flex"`)
- **Content invisible/raw code** → Switch from `wp:html` to native blocks
- **Animated elements hidden** → Check `editor.css` has overrides for `.reveal`, `.fade-in`, etc.
- **Icons invisible** → Switch from inline SVG to `wp:image` with SVG file
- **Sections appear narrow (~600px)** → Missing `"align":"full"` on outer section groups. See Editor Width Fix below.

### Editor Width Fix

If sections appear narrow in the editor instead of full-width:

1. Check every outer section group has `"align":"full"` in JSON AND `alignfull` on the div
2. Check theme.json has `useRootPaddingAwareAlignments: true`
3. Check editor.css has: `.editor-styles-wrapper .alignfull { max-width: none; }`
4. Check theme.json `styles.spacing.blockGap` is `"0"` (prevents white strips between sections)

### Hiding the Post Title in the Editor

The `.editor-post-title` element sits **outside** `.editor-styles-wrapper` in the Gutenberg editor. Scoped rules like `.editor-styles-wrapper .editor-post-title` will not reach it. To hide the post title area (common on full-page designs where the H1 lives inside the hero block), target these three selectors directly in `editor.css`:

```css
/* Post title is outside .editor-styles-wrapper — must be targeted globally */
.editor-post-title,
.editor-post-title__input,
.edit-post-visual-editor__post-title-wrapper {
  display: none !important;
}
```

CSS loaded via `enqueue_block_editor_assets` is global in the editor scope, so it can reach these selectors even though they sit outside `.editor-styles-wrapper`.

### Completion Checklist

Before declaring a page done, verify against the section inventory:

```
[ ] All sections from inventory are accounted for
[ ] Converted sections match frontend baseline at desktop and mobile
[ ] core/html count == documented plugin/iframe exceptions only (verified programmatically)
[ ] Editor shows full-width sections (not constrained to contentSize)
[ ] All text is editable in block editor
[ ] block-editor-warning count == 0 (no "unexpected/invalid content" blocks)
```

Tell the user the results:

> "Editor QA complete. X sections pass, X need fixes. [details]"

## Step 6: Build Navigation

After core pages are created:

```bash
# Create primary navigation menu
wp menu create "Primary Navigation"

# Add pages to menu (in order)
wp menu item add-post primary-navigation <home_id> --position=1
wp menu item add-post primary-navigation <about_id> --position=2
wp menu item add-post primary-navigation <services_id> --position=3
wp menu item add-post primary-navigation <contact_id> --position=4

# Assign to theme location
wp menu location assign primary-navigation primary
```

## Step 7: Update Build State

After each page is built, update `/wp/wp_state.md`:

```markdown
| Page | Content File | HTML Baseline | Block Version | Status | Post ID |
|------|-------------|---------------|---------------|--------|---------|
| Home | /content/home.md | /wp/homepage-content.html | /wp/homepage-content-blocks.html | Published | 42 |
| About | /content/about.md | /wp/about-content.html | /wp/about-content-blocks.html | Published | 43 |
```

## Cache Busting After CSS Changes

After adding or modifying CSS, bump the theme version constant in `functions.php` (e.g. `THEME_VERSION`). This constant is used as the version parameter for enqueued stylesheets, so incrementing it busts browser caches. Use a named constant rather than `wp_get_theme()->get('Version')` for easier programmatic bumping.

## Step 8: Approval Gate

After building each page (or batch), use the `AskUserQuestion` tool:

> "Built X pages in WordPress. Both frontend and editor have been verified. Continue with remaining pages?"

After all pages are built:

> "All pages built and navigation configured. Ready to proceed to **Phase 6: QA & Go-Live**?"

Options:
- "Approved — proceed to ops"
- "Changes needed on [page]"
- "Build more pages"
