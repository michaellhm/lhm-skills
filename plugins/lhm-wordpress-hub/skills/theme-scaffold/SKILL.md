---
name: theme-scaffold
description: "Scaffold a custom WordPress block theme with theme.json, templates, template parts, patterns, and styles. Use this when the user says 'scaffold theme', 'create theme', 'build theme', 'theme.json', 'block theme', 'custom theme', or 'WordPress theme'. Phase E of the website build. Requires design system and block specs."
---

# Theme Scaffold

Scaffold a complete custom block theme from the design system and block specifications. Outputs a ready-to-install WordPress theme.

## Before Starting

1. **Read design system** - read `/design/design_system.md`
2. **Read brand guidelines** - read `/design/brand_guidelines.md`
3. **Read block specs** - read `/design/blocks.md`
4. **Read the approved homepage prototype** - read from `/design/prototype/homepage/` (the approved version: `index.html`, or the specific approved version file like `v2.html`). Also read `assets/css/style.css`, `assets/js/main.js`, and check `assets/images/` for any images
5. **Read theme.json guide** - read `${CLAUDE_PLUGIN_ROOT}/references/theme-json-guide.md`
6. **Read block patterns guide** - read `${CLAUDE_PLUGIN_ROOT}/references/block-patterns-guide.md`
7. If design system doesn't exist, tell the user and offer to run Design System Generator first

## Step 1: Theme Identity

Use the `AskUserQuestion` tool:

> "What should the theme be called?"

Also ask:
- Theme slug (kebab-case, e.g. `client-name-theme`)
- Text domain (same as slug)
- Does the client need a child theme or is this the only theme?

## Step 2: Rip the HTML Prototype Apart

**This is the most critical step.** The approved HTML prototype lives at `/design/prototype/homepage/` with CSS, JS, and images already in separate files under `assets/`. Your job is to copy each asset into the right place in the theme and convert the HTML into WordPress block markup. The goal is pixel-perfect parity between the prototype and the WordPress build.

### 2a: Copy CSS → `assets/css/custom.css`

Read `/design/prototype/homepage/assets/css/style.css` and copy it into the theme at `assets/css/custom.css`.

**Rules:**
- Copy the CSS verbatim first. Do NOT rename classes, do NOT refactor, do NOT "improve" the CSS. This must be taken literally. In past builds, the CSS was rewritten with different design decisions (e.g. 3-column steps vs vertical, banner trust strip vs inline dots) which caused hours of debugging. Copy first, replace CSS variables second, change nothing else
- After copying verbatim, make ONLY these targeted replacements:
  - Replace hardcoded color hex values with `var(--wp--preset--color--{slug})` where a matching theme.json palette entry exists
  - Replace hardcoded font-family values with `var(--wp--preset--font-family--{slug})` where a matching theme.json font family exists
  - Replace hardcoded spacing values with `var(--wp--preset--spacing--{slug})` ONLY where an exact match exists in the spacing scale
  - Replace hardcoded font-size values with `var(--wp--preset--font-size--{slug})` ONLY where an exact match exists
- **Include ALL utility/layout classes** (`.container`, `.section`, `.text-center`, `.btn-group`, `.mb-6`, etc.), not just component classes. Missing `.container` causes every section to render full-width in WordPress. Scan the prototype CSS for every class definition and verify each is present in the theme CSS
- Keep ALL class names exactly as they appear in the prototype. Do NOT rename `.hero-section` to `.{theme-slug}-hero` or add prefixes
- Keep ALL media queries, animations, transitions, keyframes, hover states, and pseudo-elements exactly as they are
- Keep `@import` statements (Google Fonts, etc.) at the top
- Preserve self-hosted font `@font-face` declarations exactly from the prototype CSS. If the prototype uses Google Fonts `@import`, keep that too. Do not silently switch font loading strategies
- If in doubt, keep the original value. A working hardcoded value is better than a broken CSS variable reference

**Important: CSS should handle style, NOT structure.** The `custom.css` file will contain grid/flex declarations from the prototype (e.g. `.card-grid { display: grid; grid-template-columns: repeat(3, 1fr) }`). Keep these in the CSS for frontend rendering, but understand that the block editor will ignore them. The wp-page-builder skill uses WP layout attributes (`type:"grid"`, `type:"flex"`) for structure, which work in both editor and frontend. The CSS grid/flex rules act as a frontend enhancement on top of WP's layout system.

| CSS Property Type | Keep in custom.css? | Works in Editor? |
|---|---|---|
| Colors, backgrounds, gradients | Yes | Yes |
| Typography (font-size, weight, letter-spacing) | Yes | Yes |
| Borders, border-radius, box-shadow | Yes | Yes |
| Padding, margins | Yes | Yes |
| Grid/flex layout (display, grid-template-columns) | Yes (frontend enhancement) | No (WP layout handles this in editor) |
| Animations, transitions, keyframes | Yes | No (overridden by editor.css) |
| Pseudo-elements (::before, ::after) | Yes | No (not rendered in editor) |

**After copying, add WordPress layout resets** to the end of `custom.css`:

```css
/* WordPress layout resets — prevent default block gaps */
.wp-site-blocks > * + *,
.is-layout-flow > * + *,
.is-layout-constrained > * + * {
  margin-block-start: 0;
}
```

WordPress injects default block spacing that creates white gaps between full-bleed sections. These resets are mandatory.

**Specificity warning:** WordPress block group `display` styles can override component CSS. If a component uses `display: none` (e.g. a sticky mobile CTA hidden on desktop), the WP `.wp-block-group` display will override it. Fix with double specificity: `.wp-block-group.sticky-cta { display: none !important }` inside a media query.

### 2b: Copy JS → `assets/js/custom.js`

Read `/design/prototype/homepage/assets/js/main.js` and copy it into the theme at `assets/js/custom.js`.

**Rules:**
- Copy the JavaScript verbatim. Do NOT refactor or "improve" it
- Keep all event listeners, scroll handlers, intersection observers, animations, and DOM manipulation exactly as written
- The JS references CSS classes and HTML structure from the prototype. Since we're preserving those exact classes, the JS will continue to work
- If the prototype has no JS file (or it's empty), skip this file

### 2c: Generate `assets/css/editor.css` (Editor Overrides)

The block editor loads `custom.css` via `add_editor_style()`. This means animation/transition classes (like `.reveal { opacity: 0; transform: translateY(24px); }`) will make content invisible in the editor. You MUST create an editor-only stylesheet that overrides these.

Scan `custom.css` for any rules that hide or transform elements (scroll animations, fade-ins, slide-ups, etc.) and write overrides:

```css
/* Editor overrides — make all animated elements visible while editing */
.reveal,
.fade-in,
.slide-up,
.animate-on-scroll,
[class*="reveal"],
[class*="fade-in"] {
  opacity: 1 !important;
  transform: none !important;
  transition: none !important;
  animation: none !important;
}
```

Add any other editor-specific fixes discovered during the build. This file will grow as edge cases are found.

### 2d: Create `assets/icons/` Directory

If the HTML prototype uses icons (SVG icons, icon fonts, or decorative elements), create SVG files for each icon in `assets/icons/`.

1. Scan the prototype for all icon usage (inline SVG, CSS background SVGs, icon font references)
2. For each unique icon, create a standalone `.svg` file (e.g. `plumbing.svg`, `electrical.svg`, `checkmark.svg`)
3. The wp-page-builder skill will reference these via `wp:image` blocks so they're visible in the block editor

If the prototype uses no icons, skip this directory.

### 2d-ii: Copy Images → `assets/images/`

If `/design/prototype/homepage/assets/images/` contains any files, copy them into the theme at `assets/images/`. These are images referenced by the prototype (hero backgrounds, section images, etc.) that need to ship with the theme.

If the prototype uses no local images (only external URLs), skip this directory.

### 2e: Extract Header → `parts/header.html`

Read the `<header>` element from the prototype (including its full inner HTML) and convert it to WordPress block markup.

**Rules:**
- Preserve the exact HTML structure and class names from the prototype header
- Wrap the header content in a `<!-- wp:group -->` block with the same classes the prototype header uses
- Replace the static navigation `<nav>` / `<ul>` / `<li>` links with a WordPress `<!-- wp:navigation -->` block so the menu is dynamic
- Keep all other header elements (logo, phone number, CTA button, etc.) as close to the prototype HTML as possible using `<!-- wp:html -->` blocks if needed to preserve exact markup
- The header CSS classes must match what's in `custom.css` so styles apply

### 2f: Extract Footer → `parts/footer.html`

Read the `<footer>` element from the prototype and convert it to WordPress block markup.

**Rules:**
- Same approach as header: preserve exact HTML structure and class names
- Use `<!-- wp:html -->` blocks where needed to keep the markup identical to the prototype
- Footer navigation can use `<!-- wp:navigation -->` for dynamic links, but preserve the wrapper classes

### 2g: Scaffold the Theme Directory

Create the theme at `/wp/theme/{theme-slug}/`:

```
{theme-slug}/
  style.css
  theme.json
  functions.php
  /templates/
    index.html
    home.html
    page.html
    single.html
    archive.html
    404.html
    search.html
  /parts/
    header.html
    footer.html
  /patterns/
    [... from blocks.md ...]
  /assets/
    /css/
      custom.css       (extracted from prototype — visual styles)
      editor.css       (editor overrides — animation/visibility fixes)
    /js/
      custom.js        (only if prototype had JS)
    /icons/
      [name].svg       (only if prototype uses icons)
    /fonts/
    /images/
```

### `style.css` — Theme Header

```css
/*
Theme Name: [Theme Name]
Theme URI:
Author: LHM Digital
Author URI:
Description: Custom block theme for [Client Name]
Version: 1.0.0
Requires at least: 6.4
Tested up to: 6.9
Requires PHP: 8.0
License: GNU General Public License v2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html
Text Domain: [theme-slug]
*/
```

### `theme.json` - Design System as Configuration

Build this from `/design/design_system.md`. Map every token to the theme.json structure:

- Color palette → `settings.color.palette`
- Font families → `settings.typography.fontFamilies`
- Font sizes → `settings.typography.fontSizes` (with fluid values)
- Spacing scale → `settings.spacing.spacingSizes`
- Layout widths → `settings.layout`
- Global styles → `styles`
- Element styles → `styles.elements`
- Block overrides → `styles.blocks`

Refer to `${CLAUDE_PLUGIN_ROOT}/references/theme-json-guide.md` for the exact format.

### `functions.php`

```php
<?php
/**
 * [Theme Name] functions and definitions
 */

define('THEME_VERSION', '1.0.0');

// Register navigation menus
function theme_slug_register_menus() {
    register_nav_menus([
        'primary'  => 'Primary Navigation',
        'footer'   => 'Footer Navigation',
    ]);
}
add_action('init', 'theme_slug_register_menus');

// Register block pattern categories
function theme_slug_register_pattern_categories() {
    $categories = [
        'hero' => 'Hero Sections',
        'cta' => 'Call to Action',
        'content' => 'Content Sections',
        'testimonials' => 'Testimonials',
        'faq' => 'FAQ',
    ];
    foreach ($categories as $slug => $label) {
        register_block_pattern_category($slug, ['label' => $label]);
    }
}
add_action('init', 'theme_slug_register_pattern_categories');

// Enqueue custom CSS and JS on the frontend
function theme_slug_enqueue_assets() {
    wp_enqueue_style(
        'theme-slug-custom',
        get_template_directory_uri() . '/assets/css/custom.css',
        [],
        THEME_VERSION
    );

    // Only enqueue JS if the file exists (prototype may not have had JS)
    $js_path = get_template_directory() . '/assets/js/custom.js';
    if (file_exists($js_path)) {
        wp_enqueue_script(
            'theme-slug-custom',
            get_template_directory_uri() . '/assets/js/custom.js',
            [],
            THEME_VERSION,
            true // Load in footer
        );
    }
}
add_action('wp_enqueue_scripts', 'theme_slug_enqueue_assets');

// Enqueue editor styles so the block editor matches the frontend
// Order matters: custom.css loads first, then editor.css overrides animations/visibility
function theme_slug_editor_styles() {
    add_editor_style('style.css');
    add_editor_style('assets/css/custom.css');
    add_editor_style('assets/css/editor.css');
}
add_action('after_setup_theme', 'theme_slug_editor_styles');
```

Replace `theme_slug` and `theme-slug` with the actual theme slug in kebab and snake case.

### Templates

Build each template using block markup. Every template follows this structure:

```html
<!-- wp:template-part {"slug":"header","area":"header"} /-->

<!-- page content blocks here -->

<!-- wp:template-part {"slug":"footer","area":"footer"} /-->
```

#### `templates/index.html` (Fallback)
```html
<!-- wp:template-part {"slug":"header","area":"header"} /-->
<!-- wp:group {"layout":{"type":"constrained"}} -->
<div class="wp-block-group">
  <!-- wp:post-title {"level":1} /-->
  <!-- wp:post-content /-->
</div>
<!-- /wp:group -->
<!-- wp:template-part {"slug":"footer","area":"footer"} /-->
```

#### `templates/page.html` (Default Page)
```html
<!-- wp:template-part {"slug":"header","area":"header"} /-->
<!-- wp:post-content /-->
<!-- wp:template-part {"slug":"footer","area":"footer"} /-->
```

Build all templates listed in the scaffold structure.

### Template Parts

#### `parts/header.html`
Build a header with: site logo, site title, navigation menu. Use core blocks: `core/site-logo`, `core/site-title`, `core/navigation`.

#### `parts/footer.html`
Build a footer with: footer navigation, copyright notice, contact info. Use core blocks: `core/group`, `core/columns`, `core/paragraph`, `core/navigation`.

### Block Patterns

For each pattern listed in `/design/blocks.md`, create a PHP pattern file in `/patterns/`. Use the component specs from the block specs document and design tokens from the design system.

Refer to `${CLAUDE_PLUGIN_ROOT}/references/block-patterns-guide.md` for the pattern file format.

## Step 3: Validate

Check the scaffolded theme:

1. `style.css` has valid theme header
2. `theme.json` has valid JSON with correct schema reference
3. Every color, font, and spacing token from the design system is in `theme.json`
4. `assets/css/custom.css` exists and contains the CSS copied from the prototype's `assets/css/style.css` (with targeted WP variable replacements only)
5. `assets/css/editor.css` exists and overrides all animation/transition classes (`.reveal`, `.fade-in`, etc.) with `opacity: 1 !important; transform: none !important`
6. `assets/js/custom.js` exists if the prototype had a JS file (`assets/js/main.js`)
7. `assets/icons/` directory exists with SVG files if the prototype used icons
8. `functions.php` enqueues `custom.css` on both frontend and editor
9. `functions.php` enqueues `editor.css` via `add_editor_style()` AFTER `custom.css`
10. `functions.php` enqueues `custom.js` in the footer (if it exists)
11. `functions.php` registers navigation menus (`primary` and `footer`)
12. `parts/header.html` preserves the prototype's header structure and CSS classes
13. `parts/footer.html` preserves the prototype's footer structure and CSS classes
14. Header uses `<!-- wp:navigation -->` for dynamic menu (not static `<a>` links)
15. Every pattern from `/design/blocks.md` has a corresponding PHP file
16. All templates reference header and footer parts
17. `functions.php` registers all needed pattern categories
18. **Class name check**: compare CSS classes used in `parts/header.html`, `parts/footer.html`, and patterns against `custom.css` to confirm they match

## Step 4: Visual Diff After Installation

After the theme is installed and activated, run a visual diff immediately. Push a minimal test page with representative sections from the prototype and screenshot both the prototype (served via local HTTP server) and the WordPress page at Desktop Standard (1440x900) and Mobile Standard (390x844). Catching CSS divergence at theme scaffold time saves rebuilding pages later. Use the `css-sync-check` skill for this.

## Step 5: Installation Instructions

Tell the user how to install the theme:

> **To install the theme:**
>
> **Option A: WP-CLI**
> ```bash
> # Copy theme to WordPress
> cp -r /wp/theme/{theme-slug} /path/to/wordpress/wp-content/themes/
> wp theme activate {theme-slug}
> ```
>
> **Option B: Manual**
> 1. Zip the theme folder
> 2. Upload via Appearance → Themes → Add New → Upload Theme
> 3. Activate
>
> **Option C: WordPress MCP**
> If using a WordPress MCP, use the theme installation tool.

## Step 6: Approval Gate

Use the `AskUserQuestion` tool:

> "Theme scaffolded at `/wp/theme/{theme-slug}/`. Ready to proceed to **WP Page Builder** to start building pages?"

Options:
- "Approved — start building pages"
- "I need to install the theme first"
- "Changes needed to the theme"
