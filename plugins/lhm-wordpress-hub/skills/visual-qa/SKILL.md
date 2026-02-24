---
name: visual-qa
description: "Pixel-perfect visual regression testing using Playwright MCP. Compares the approved HTML prototype against the live WordPress build at multiple viewport sizes. Use this when the user says 'visual QA', 'check the build', 'compare to prototype', 'pixel perfect check', 'screenshot comparison', 'does it match', 'visual regression', 'test the pages', 'QA the site', or 'check responsive'. Also triggered automatically after every page build, blog post, or site extension."
---

# Visual QA - Pixel-Perfect Design Verification

You are a visual QA specialist. Your job is to verify that the WordPress build is a pixel-perfect match to the approved HTML prototype. You use Playwright MCP to take full-page screenshots at multiple breakpoints, check for console errors and broken resources, then visually analyse every difference using your multimodal vision capabilities.

This skill is not optional. It runs after every page build and every site extension.

## Playwright MCP Tool Reference

You have access to these Playwright MCP tools. Use the exact tool names shown here:

### Navigation & Screenshots
- `mcp__playwright__browser_navigate` - Navigate to a URL (prototype file or live WordPress page)
- `mcp__playwright__browser_navigate_back` - Go back to previous page
- `mcp__playwright__browser_take_screenshot` - Capture a screenshot of the current page
- `mcp__playwright__browser_snapshot` - Get the page's accessibility tree (for structural verification)

### Element Interaction
- `mcp__playwright__browser_click` - Click elements (dismiss cookie banners, interact with menus)
- `mcp__playwright__browser_hover` - Hover over elements (test hover states, dropdowns)
- `mcp__playwright__browser_type` - Type text into fields
- `mcp__playwright__browser_press_key` - Press keyboard keys (Escape to close modals, Tab for focus testing)

### Browser Management
- `mcp__playwright__browser_resize` - Resize viewport to specific dimensions (critical for responsive testing)
- `mcp__playwright__browser_wait_for` - Wait for elements, network idle, or specific conditions
- `mcp__playwright__browser_close` - Close the browser when done

### Debugging & Diagnostics
- `mcp__playwright__browser_console_messages` - Get browser console output (check for JS errors, failed resource loads)
- `mcp__playwright__browser_network_requests` - Monitor network requests (check for 404s, failed font loads, broken images)
- `mcp__playwright__browser_evaluate` - Run JavaScript in the page (compute element dimensions, check computed styles)

### Important Notes
- All Playwright MCP tools have **auto-wait** built in. You do not need manual sleep/delay calls.
- **Never use `browser_run_code`** if it appears available. It causes the Playwright MCP server to crash.
- If the browser is not yet installed, use `mcp__playwright__browser_install` first.

## Before Starting

1. **Read the viewport reference** - read `${CLAUDE_PLUGIN_ROOT}/skills/visual-qa/references/viewports.md` for exact breakpoint sizes
2. **Read the design system** - read `/design/design_system.md` for the expected tokens
3. **Read the custom CSS** - read `/wp/theme/{theme-slug}/assets/css/custom-styles.css` for expected styles
4. **Read WP state** - read `/wp/wp_state.md` to know which pages are built and their URLs
5. **Identify the prototype files** - scan `/design/prototype/` for page folders (each contains an `index.html` or versioned `.html` file)

## Step 1: Determine QA Scope

Use the `AskUserQuestion` tool:

> "Which pages should I run visual QA on?"

Options:
- "Homepage only" (fastest, use after homepage build)
- "All pages with prototypes" (compare every page that has an HTML prototype)
- "Full site at all breakpoints" (comprehensive, use before launch)
- "Specific page" (let them choose)

Also confirm:
- The WordPress site URL (e.g. `https://staging.example.com` or `http://localhost:8080`)
- Whether to run full breakpoints (8 viewports) or minimum pass (4 viewports)

## Step 2: Screenshot the Prototype

For each page being tested, screenshot the HTML prototype file at every breakpoint.

**For each viewport breakpoint, execute this exact sequence:**

1. **Resize the viewport:**
   ```
   mcp__playwright__browser_resize → width: [breakpoint width], height: [breakpoint height]
   ```

2. **Serve the prototype via local HTTP server** (file:// URLs are blocked by Playwright MCP):
   ```bash
   python3 -m http.server 8899 --directory /[absolute-path]/design/prototype/homepage/
   ```
   Then navigate:
   ```
   mcp__playwright__browser_navigate → url: "http://localhost:8899/index.html"
   ```

3. **Wait for full render:**
   ```
   mcp__playwright__browser_wait_for → wait for network idle (fonts, images loaded)
   ```

4. **Take a full-page screenshot:**
   ```
   mcp__playwright__browser_take_screenshot
   ```
   Visually inspect the screenshot. Confirm the page rendered correctly before saving.

5. **Save the screenshot** to `/qa/{page-slug}/prototype-{breakpoint-name}.png`

6. **Check console for errors:**
   ```
   mcp__playwright__browser_console_messages
   ```
   Note any errors (failed font loads, missing resources). These won't block QA but should be reported.

Example file naming:
```
/qa/home/prototype-desktop-standard.png
/qa/home/prototype-tablet-portrait.png
/qa/home/prototype-mobile-standard.png
```

## Step 3: Screenshot the WordPress Build

For the same page, screenshot the live WordPress build at each breakpoint using the same sequence.

**For each viewport breakpoint:**

1. **Resize:**
   ```
   mcp__playwright__browser_resize → width: [breakpoint width], height: [breakpoint height]
   ```

2. **Navigate:**
   ```
   mcp__playwright__browser_navigate → url: "[wordpress-site-url]/[page-slug]"
   ```

3. **Wait for full render:**
   ```
   mcp__playwright__browser_wait_for → wait for network idle
   ```

4. **Remove obstructions** (always do this before screenshotting):
   - WordPress admin bar (**mandatory** — shifts page down 32px and distorts comparisons): use `mcp__playwright__browser_evaluate` to run `document.getElementById('wpadminbar')?.remove(); document.documentElement.style.marginTop='0'`
   - Cookie consent banner: use `mcp__playwright__browser_click` to dismiss it, or use `browser_evaluate` to remove it from the DOM
   - Any popups or overlays: dismiss or remove them

5. **Take a full-page screenshot:**
   ```
   mcp__playwright__browser_take_screenshot
   ```

6. **Save** to `/qa/{page-slug}/wordpress-{breakpoint-name}.png`

7. **Check console for errors:**
   ```
   mcp__playwright__browser_console_messages
   ```
   Flag any JavaScript errors, failed resource loads, or 404s. These are bugs.

8. **Check network requests for failures:**
   ```
   mcp__playwright__browser_network_requests
   ```
   Look for:
   - Failed font file requests (fonts not loading = wrong typography)
   - 404 image requests (missing images)
   - Failed CSS file loads (broken styles)
   - Mixed content warnings (HTTP resources on HTTPS page)

## Step 4: Accessibility Snapshot

For each page at the desktop standard breakpoint, also capture an accessibility tree:

```
mcp__playwright__browser_snapshot
```

Check:
- All headings follow a logical hierarchy (h1 → h2 → h3, no skipping)
- All images have alt text
- All links have descriptive text (not "click here")
- All form inputs have labels
- ARIA landmarks are present (navigation, main, footer)

Include accessibility findings in the QA report.

## Step 5: Interactive Verification

Beyond static screenshots, verify interactive elements using Playwright:

### Navigation
- `mcp__playwright__browser_click` on each navigation menu item and verify it navigates to the correct page
- On mobile breakpoints: click the hamburger menu, verify the mobile menu opens, click a link

### Hover States
- `mcp__playwright__browser_hover` over buttons, cards, and links
- `mcp__playwright__browser_take_screenshot` to capture the hover state
- Compare button hover colors, card lift effects, and link underlines against the prototype

### CTA Buttons
- `mcp__playwright__browser_click` each CTA button
- Verify it navigates to the correct destination (contact page, form, etc.)
- Use `mcp__playwright__browser_navigate_back` to return

### Scroll Behaviour
- Use `mcp__playwright__browser_evaluate` to scroll the page in increments
- Take screenshots at different scroll positions to verify:
  - Sticky header behaviour (if applicable)
  - Scroll-triggered animations fire
  - Lazy-loaded images appear
  - Section backgrounds render correctly during scroll

## Step 6: Visual Comparison

Now compare each screenshot pair. You are a multimodal AI with vision capabilities. Read both the prototype and WordPress screenshots and perform a detailed comparison.

**CRITICAL: Only mark a page as passing after verifying with screenshots. Never skip visual verification.**

### Comparison Checklist

For **each breakpoint pair** (prototype vs WordPress), check:

#### Layout & Structure
- [ ] Overall page structure matches (same sections in same order)
- [ ] Section heights and proportions are consistent
- [ ] Content width and alignment match
- [ ] Grid/column layouts render identically
- [ ] Spacing between sections matches
- [ ] Header and footer layout match

#### Typography
- [ ] Font families render correctly (heading font, body font)
- [ ] Font sizes match at each heading level and body text
- [ ] Line heights are consistent
- [ ] Letter spacing matches
- [ ] Font weights are correct (bold, semibold, regular)
- [ ] Text alignment matches (left, center, right)
- [ ] Text wrapping and line breaks are similar (minor rendering differences acceptable)

#### Colors & Backgrounds
- [ ] Background colors match the design system tokens
- [ ] Text colors are correct
- [ ] Gradient directions and stops match
- [ ] Background patterns, textures, or overlays render
- [ ] Hover states use correct colors (verified via hover screenshots)

#### Components
- [ ] Buttons match (size, color, radius, padding, text)
- [ ] Cards render correctly (border, shadow, radius, padding)
- [ ] Hero section matches (layout, image placement, overlay)
- [ ] CTA sections match (background, text, button placement)
- [ ] Navigation renders correctly (logo, menu items, mobile menu)
- [ ] Footer matches (columns, links, spacing)
- [ ] Images are positioned and sized correctly
- [ ] Icons render (if using icon fonts or SVGs)

#### Animations & Effects
- [ ] CSS animations are present (entrance animations, hover effects)
- [ ] Box shadows match
- [ ] Border radius values are correct
- [ ] Opacity and transparency effects render

#### Responsive Behaviour
- [ ] Elements stack correctly on mobile
- [ ] Font sizes scale down appropriately
- [ ] Images resize and don't overflow
- [ ] Navigation collapses to mobile menu
- [ ] Horizontal scrolling does NOT appear (critical bug if it does)
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Content is readable without zooming on mobile
- [ ] No text truncation or overflow on small screens

#### Console & Network Health
- [ ] No JavaScript errors in console
- [ ] No failed network requests (404s, broken resources)
- [ ] All fonts load successfully
- [ ] All images load successfully
- [ ] No mixed content warnings

### Severity Levels

Rate each discrepancy:

| Severity | Definition | Example |
|----------|-----------|---------|
| **Critical** | Visually broken, unusable, or blocks conversion | CTA button missing, text overlapping, horizontal scroll on mobile, layout collapsed, JS errors breaking functionality |
| **Major** | Noticeable difference that changes the feel | Wrong font loading, colors off by more than a shade, significant spacing mismatch, missing animation, failed image load |
| **Minor** | Small difference most users won't notice | 1-2px spacing variance, slight font rendering difference, minor border-radius mismatch |
| **Acceptable** | Expected rendering differences between HTML and WordPress | Sub-pixel rounding, browser-specific font smoothing, minor text reflow |

## Step 7: QA Report

Create `/qa/{page-slug}/qa-report.md`:

```markdown
---
page: [Page Name]
slug: /[slug]
date: YYYY-MM-DD
prototype: /design/prototype/{slug}/index.html
wordpress_url: [full URL]
status: pass | fail | pass-with-notes
breakpoints_tested: [full | minimum]
---

# Visual QA Report: [Page Name]

## Summary

| Breakpoint | Status | Critical | Major | Minor |
|-----------|--------|----------|-------|-------|
| Desktop Large (1920) | Pass/Fail | 0 | 0 | 0 |
| Desktop Standard (1440) | Pass/Fail | 0 | 0 | 0 |
| Desktop Small (1280) | Pass/Fail | 0 | 0 | 0 |
| Tablet Landscape (1024) | Pass/Fail | 0 | 0 | 0 |
| Tablet Portrait (768) | Pass/Fail | 0 | 0 | 0 |
| Mobile Large (430) | Pass/Fail | 0 | 0 | 0 |
| Mobile Standard (390) | Pass/Fail | 0 | 0 | 0 |
| Mobile Small (360) | Pass/Fail | 0 | 0 | 0 |

**Overall: [PASS / FAIL / PASS WITH NOTES]**

## Console & Network Health

- JavaScript errors: [count] ([list if any])
- Failed network requests: [count] ([list if any])
- Font load failures: [count]
- Mixed content warnings: [count]

## Accessibility

- Heading hierarchy: [valid / issues found]
- Image alt text: [all present / X missing]
- Link text quality: [all descriptive / X generic]
- ARIA landmarks: [present / missing]

## Interactive Verification

- Navigation links: [all working / X broken]
- CTA destinations: [all correct / X incorrect]
- Hover states: [match prototype / X discrepancies]
- Mobile menu: [working / issues]

## Issues Found

### Critical Issues
[List each with breakpoint, description, screenshot reference, and suggested fix]

### Major Issues
[List each with breakpoint, description, screenshot reference, and suggested fix]

### Minor Issues
[List each with breakpoint, description, screenshot reference, and suggested fix]

## Screenshots

All screenshots saved to `/qa/[slug]/`:
- `prototype-{breakpoint}.png` - approved prototype
- `wordpress-{breakpoint}.png` - live WordPress build
- `hover-{element}.png` - hover state captures
```

## Step 8: Fix Loop

If **any Critical or Major issues** are found:

1. Present the issues to the user with specific descriptions and screenshot references
2. Propose fixes (CSS adjustments to `custom-styles.css`, block markup changes, or theme.json tweaks)
3. Use the `AskUserQuestion` tool:

> "Visual QA found [X] critical and [Y] major issues. Should I fix them now?"

Options:
- "Yes, fix all issues"
- "Fix critical only"
- "Show me the screenshots first"
- "Skip fixes, I'll handle it manually"

4. If fixing:
   a. Make the CSS, markup, or theme.json changes
   b. If the WordPress site needs updating, push changes via WP-CLI or MCP
   c. **Re-run the full screenshot sequence** for affected breakpoints:
      - `mcp__playwright__browser_resize` to the breakpoint
      - `mcp__playwright__browser_navigate` to the page (force reload)
      - `mcp__playwright__browser_wait_for` network idle
      - `mcp__playwright__browser_take_screenshot` to verify the fix
   d. Visually inspect the new screenshot to confirm the fix resolved the issue
5. Repeat until all Critical issues are resolved and Major issues are accepted or fixed
6. Update the QA report with the resolution status and new screenshots

**Only mark a page as passing after verification with screenshots. Never mark passing without re-screenshotting after fixes.**

## Step 9: Sign-Off

Once the page passes QA (no Critical issues, Major issues resolved or accepted):

Use the `AskUserQuestion` tool:

> "Visual QA complete for **[Page Name]**. [X] breakpoints tested, [status]. Console clean, network healthy, accessibility checked. Approved?"

Options:
- "Approved"
- "Re-run QA at all breakpoints"
- "Needs more fixes"

Update `/qa/{page-slug}/qa-report.md` with the final status.

## When This Skill is Triggered

This skill must run in these situations:

1. **After theme scaffold** (Sub-Phase E1) - the `theme-scaffold` skill runs a lightweight visual diff (2 viewports) immediately after installation. This catches CSS divergence before any pages are built
2. **After homepage build** (Sub-Phase E3) - compare `/design/prototype/homepage/` vs live homepage
2. **After each page build** (Sub-Phase E4) - if a prototype exists for that page, compare. If no prototype exists, still screenshot the WordPress build at all breakpoints for a standalone responsive check
3. **After any CSS or theme changes** - re-run QA on affected pages
4. **After site extension** (new pages, modified pages) - run QA on the changed pages
5. **Before launch** (Phase F) - full-site QA pass at all breakpoints
6. **After blog posts or new content** - run responsive check (no prototype comparison needed, just check for layout breaks)

## Pages Without Prototypes

For pages that don't have an HTML prototype (most pages beyond the homepage), run a **responsive-only check**:

1. Screenshot the WordPress page at all breakpoints using the Playwright MCP sequence above
2. Check `mcp__playwright__browser_console_messages` for errors
3. Check `mcp__playwright__browser_network_requests` for failures
4. Run `mcp__playwright__browser_snapshot` for accessibility
5. Check for layout breaks, overflow issues, readability problems
6. Verify the page uses the same design system tokens and CSS classes as the homepage
7. Check that the page's visual style is consistent with the approved prototype pages
8. Test navigation links and CTAs with `mcp__playwright__browser_click`
9. Save screenshots and report to `/qa/{page-slug}/`

The report format is the same, but the "prototype" column shows "N/A - responsive check only".

## Computed Style Verification

For precision checking, use `mcp__playwright__browser_evaluate` to extract computed CSS values from specific elements and compare them against the design system:

```javascript
// Example: verify a heading's computed styles match the design system
const el = document.querySelector('.wp-block-heading');
const styles = window.getComputedStyle(el);
JSON.stringify({
  fontFamily: styles.fontFamily,
  fontSize: styles.fontSize,
  fontWeight: styles.fontWeight,
  lineHeight: styles.lineHeight,
  color: styles.color,
  marginTop: styles.marginTop,
  marginBottom: styles.marginBottom
});
```

Use this when:
- A visual difference is subtle and hard to judge from screenshots alone
- You need to confirm exact pixel values for spacing, sizing, or positioning
- Font loading is ambiguous in the screenshot (verify the actual font-family resolved)
- Colors look close but might be slightly off (compare exact RGB values)

This gives you precise numerical data to include in the QA report alongside the visual comparison.
