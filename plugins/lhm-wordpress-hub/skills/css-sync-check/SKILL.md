---
name: css-sync-check
description: "Validate that the WordPress theme CSS matches the approved HTML prototype CSS. Run this after theme installation and before page building. Use this when the user says 'check the CSS', 'CSS sync', 'does the theme match', 'validate theme CSS', 'CSS audit', 'compare CSS', or 'theme CSS check'. Catches styling divergence before pages are built."
---

# CSS Sync Check

Validate that the WordPress theme's CSS produces the same visual result as the approved HTML prototype. This skill catches CSS divergence BEFORE page building, saving hours of debugging.

## When to Run

- After theme-scaffold (Phase E1) and theme installation (Phase E2), before page building (Phase E3)
- After any manual edits to the theme's custom CSS
- When a page build doesn't match the prototype and you suspect CSS issues

## Before Starting

1. **Read the prototype CSS** - read `/design/prototype/{page}/assets/css/style.css` (or the prototype's stylesheet)
2. **Read the theme CSS** - read `/wp/theme/{theme-slug}/assets/css/custom.css` (or `custom-components.css`)
3. **Read the prototype HTML** - read the approved prototype HTML file
4. **Verify theme is installed and active** in WordPress

**Playwright MCP tools are available** for visual comparison: `mcp__playwright__browser_navigate`, `mcp__playwright__browser_resize`, `mcp__playwright__browser_take_screenshot`, `mcp__playwright__browser_wait_for`, `mcp__playwright__browser_evaluate`.

## Step 1: Class Inventory

Extract every CSS class selector from both files. Build a comparison table.

### 1a: Extract Prototype Classes

Scan the prototype CSS for all class selectors. Group them by type:
- **Layout classes** (`.container`, `.section`, `.grid`, `.columns`)
- **Component classes** (`.hero`, `.card`, `.btn`, `.faq`)
- **Utility classes** (`.text-center`, `.mb-6`, `.sr-only`)
- **State classes** (`.reveal`, `.is-visible`, `.active`, `.open`)
- **Responsive overrides** (classes inside `@media` queries)

### 1b: Extract Theme Classes

Do the same scan on the theme CSS.

### 1c: Identify Gaps

Compare the two lists. Report:
- **Missing from theme**: Classes in prototype CSS that don't exist in theme CSS. These WILL break visually.
- **Extra in theme**: Classes in theme CSS that don't exist in prototype CSS. Usually fine (WordPress-specific additions).
- **Present in both**: These need property-level comparison (Step 2).

**Critical missing classes to check first:**
- `.container` (max-width, margin auto, padding) — most common cause of full-width overflow
- `.section` (vertical padding) — causes cramped sections
- `.btn-group` (flex layout for button rows) — causes button stacking
- Any WordPress layout resets (`.wp-site-blocks`, `.is-layout-flow` margin resets)

## Step 2: Property-Level Diff

For classes that exist in both files, compare the CSS property values. Focus on properties that produce visible differences:

| Property Type | Impact if Different |
|---|---|
| `display`, `grid-template-columns`, `flex-direction` | Layout completely changes |
| `max-width`, `width`, `padding`, `margin` | Sizing and spacing off |
| `background`, `color` | Visual identity wrong |
| `font-size`, `font-weight`, `text-align` | Typography mismatch |
| `border`, `border-radius`, `box-shadow` | Component shape differs |
| `position`, `top`, `left`, `z-index` | Elements in wrong place |

For each difference found, categorise as:
- **Breaking** — will cause a visible layout or styling difference
- **Intentional** — CSS variable substitution (e.g. `#0D9488` replaced with `var(--wp--preset--color--primary)`)
- **Enhancement** — WordPress-specific addition that doesn't conflict

## Step 3: Visual Validation (Push Test Page)

This is the definitive check. Push the prototype's body content to WordPress and screenshot both.

### 3a: Prepare Test Content

Extract the `<body>` content from the prototype HTML (exclude `<header>` and `<footer>` since those are template parts). Wrap each major section in `<!-- wp:html -->` blocks:

```bash
# Save to a temp file
cat > /tmp/css-sync-test.html << 'CONTENT'
<!-- wp:html -->
[first section from prototype]
<!-- /wp:html -->

<!-- wp:html -->
[second section from prototype]
<!-- /wp:html -->
CONTENT
```

### 3b: Push to WordPress

```bash
# Create a test page
wp post create --post_type=page \
  --post_title="CSS Sync Test" \
  --post_name="css-sync-test" \
  --post_status=draft \
  --post_content="$(cat /tmp/css-sync-test.html)"
```

Use the page template that matches the prototype (e.g. `page-location-landing` for location pages).

### 3c: Serve Prototype via HTTP

file:// URLs are blocked in Playwright. Start a local server:

```bash
python3 -m http.server 8099 --directory /path/to/design/prototype/ &
```

### 3d: Screenshot Comparison

For Desktop Standard (1440x900) and Mobile Standard (390x844):

1. Resize viewport
2. Navigate to prototype via HTTP server, wait for network idle, screenshot
3. Navigate to WordPress test page, wait for network idle, remove admin bar, screenshot
4. Visually compare both screenshots

### 3e: Report Findings

For each visual difference found:
1. Identify which CSS class is responsible
2. Check whether it's a missing class (Step 1c) or a property difference (Step 2)
3. Write the fix

## Step 4: Apply Fixes

For each issue found, edit the theme CSS directly:

- **Missing classes**: Copy the class definition from the prototype CSS into the theme CSS
- **Property differences**: Update the theme CSS property to match the prototype value
- **WordPress layout resets needed**: Add these standard resets if missing:

```css
/* WordPress layout resets — prevent default block gaps */
.wp-site-blocks > * + *,
.is-layout-flow > * + *,
.is-layout-constrained > * + * {
  margin-block-start: 0;
}
```

After fixing, bump the theme version constant in `functions.php` for cache busting.

## Step 5: Re-verify

After applying fixes:
1. Bump theme version for cache busting
2. Re-screenshot the WordPress test page
3. Compare again
4. Repeat until the test page matches the prototype

## Step 6: Clean Up

```bash
# Delete the test page
wp post delete <test-page-id> --force

# Stop the HTTP server if you started one
kill %1
```

## Step 7: Report to User

Present a summary:

> "CSS sync check complete. Found X missing classes and Y property differences. All fixed. Theme CSS now matches prototype. Ready to proceed with page building."

If unfixable issues exist (e.g. WordPress block editor limitations), document them so wp-page-builder knows to work around them.

## Output

- Updated theme CSS file with all fixes applied
- Bumped theme version for cache busting
- Summary of what was found and fixed
- Any known limitations for wp-page-builder to handle
