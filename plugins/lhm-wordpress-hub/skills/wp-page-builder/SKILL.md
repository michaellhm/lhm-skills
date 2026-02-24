---
name: wp-page-builder
description: "Build individual pages in WordPress from content and design artefacts. Use this when the user says 'build pages', 'create pages in WordPress', 'page builder', 'add pages to WordPress', 'build the homepage', or 'WP build'. Phase E of the website build. Requires content files, design system, and theme installed."
---

# WP Page Builder

Build individual pages in WordPress using a two-step process: first push the raw HTML prototype to prove the design works, then convert to native WordPress blocks for editor editability.

## Before Starting

1. **Read content files** - scan `/content/` for all page files
2. **Read block specs** - read `/design/blocks.md` for component-to-pattern mapping. Pay attention to **WP layout**, **Prototype classes**, **Icon strategy**, and **Editor compatible** fields
3. **Read custom CSS** - read `/wp/theme/{theme-slug}/assets/css/custom.css` for all available CSS classes
4. **Read editor CSS** - read `/wp/theme/{theme-slug}/assets/css/editor.css` to understand editor overrides
5. **Read the homepage prototype** - read the approved version from `/design/prototype/homepage/` (e.g. `index.html` or the specific approved version like `v2.html`) as the pixel-perfect visual reference
6. **Read WP state** - read `/wp/wp_state.md` to see what's already built
7. **Read WP-CLI reference** - read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md`
8. **Read viewport reference** - read `${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/references/viewports.md` for standard breakpoint sizes
9. **Diff prototype CSS against theme CSS** - compare the prototype's CSS (`design/prototype/*/assets/css/style.css`) against the theme CSS (`assets/css/custom-components.css` or `custom.css`). Class names will match but styling rules often diverge during theme scaffold. Fix CSS discrepancies BEFORE pushing page content, not after.
10. **Verify `.container` class exists** in the theme CSS with `max-width`, `margin: 0 auto`, and gutter padding. Without it, every section using `<div class="container">` renders full-width and content overflows. This is the single highest-impact missing class.
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
6. **Complex interactive elements** — keep as `wp:html` ONLY if no native alternative exists (refer to the `wp:html` decision tree in block-architect)

### Using WP Layout Attributes for Multi-Column Sections

Do NOT rely on custom CSS classes for grid/flex layout structure. The editor ignores them. Use WP's native layout attributes instead:

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

### Critical Rule: Use Exact Prototype Classes

The CSS in `custom.css` was extracted directly from the HTML prototype. The JS in `custom.js` (if present) targets elements by the same class names. For styles and interactions to work, the WordPress block markup MUST use the exact same classes.

**Rules:**
- Do NOT invent new class names. Only use classes that exist in `custom.css`
- Do NOT rename prototype classes (e.g. don't change `.hero-section` to `.theme-slug-hero`)
- If the prototype has a wrapper `<div class="card-grid">`, the WordPress block must also have `className: "card-grid"`
- WordPress will add its own classes (like `wp-block-group`, `is-layout-grid`) alongside yours. That's fine, they stack
- The custom CSS handles visual styling (colors, borders, spacing, typography). WP layout attributes handle structure (grid columns, flex direction). They work together

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
6. **No `wp:html` blocks are present** except documented exceptions from the block spec

If any section fails these checks, identify the issue:
- **Layout stacked vertically** → Switch to WP native layout attributes (`type:"grid"` or `type:"flex"`)
- **Content invisible/raw code** → Switch from `wp:html` to native blocks
- **Animated elements hidden** → Check `editor.css` has overrides for `.reveal`, `.fade-in`, etc.
- **Icons invisible** → Switch from inline SVG to `wp:image` with SVG file

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

> "All pages built and navigation configured. Ready to proceed to **Phase F: Ops (Performance & Security)**?"

Options:
- "Approved — proceed to ops"
- "Changes needed on [page]"
- "Build more pages"
