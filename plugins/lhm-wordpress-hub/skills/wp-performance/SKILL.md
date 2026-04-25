---
name: wp-performance
description: "Performance audit and optimization for WordPress sites. Core Web Vitals, caching, image optimization, and speed improvements. Use this when the user says 'performance audit', 'speed optimization', 'Core Web Vitals', 'page speed', 'site speed', 'LCP', 'CLS', 'FID', 'caching', or 'optimize WordPress'. Phase 6 of the website build. Can also be run standalone on any WordPress site."
---

# WP Performance

Audit and optimize WordPress site performance. Covers Core Web Vitals, caching, image optimization, font loading, database optimization, and hosting configuration.

## Before Starting

1. **Read WP state** — read `/wp/wp_state.md` for current site configuration
2. **Read WP-CLI reference** — read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md`
3. Ask for the site URL if not already known

## Step 1: Performance Audit

### Core Web Vitals Assessment

Check each metric against Google's thresholds:

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP (Largest Contentful Paint) | ≤2.5s | 2.5–4s | >4s |
| FID (First Input Delay) | ≤100ms | 100–300ms | >300ms |
| INP (Interaction to Next Paint) | ≤200ms | 200–500ms | >500ms |
| CLS (Cumulative Layout Shift) | ≤0.1 | 0.1–0.25 | >0.25 |
| TTFB (Time to First Byte) | ≤800ms | 800ms–1.8s | >1.8s |

Use the `AskUserQuestion` tool to ask:

> "Do you have PageSpeed Insights or Search Console Core Web Vitals data? Or should I provide a checklist-based audit?"

### Checklist-Based Audit

Evaluate each category:

#### Images
- [ ] All images served in next-gen format (WebP/AVIF)
- [ ] Images properly sized (not larger than display size)
- [ ] Lazy loading enabled for below-fold images
- [ ] Hero/LCP image preloaded
- [ ] No missing alt text
- [ ] SVG used for icons and logos

#### Fonts
- [ ] Fonts self-hosted (not Google Fonts CDN) for privacy and speed
- [ ] `font-display: swap` set
- [ ] Font files preloaded
- [ ] Only required weights/styles loaded
- [ ] Variable fonts used where possible

#### Caching
- [ ] Browser caching headers set (Cache-Control, Expires)
- [ ] Page caching enabled (plugin or server-level)
- [ ] Object caching (Redis/Memcached) if available
- [ ] CDN configured

#### CSS & JavaScript
- [ ] Unused CSS removed or deferred
- [ ] Critical CSS inlined
- [ ] JavaScript deferred or async where possible
- [ ] No render-blocking resources
- [ ] Minification enabled

#### Database
- [ ] Post revisions limited
- [ ] Transients cleaned
- [ ] Spam comments deleted
- [ ] Database tables optimized

#### Server
- [ ] PHP 8.0+ running
- [ ] GZIP/Brotli compression enabled
- [ ] HTTP/2 or HTTP/3 enabled
- [ ] SSL/TLS configured
- [ ] Keep-alive enabled

#### WordPress
- [ ] Unused plugins deactivated and deleted
- [ ] Unused themes deleted
- [ ] WordPress auto-updates enabled
- [ ] Heartbeat API limited
- [ ] XML-RPC disabled (if not needed)
- [ ] oEmbed limited

## Step 2: Optimization Actions

### Image Optimization

```bash
# Install image optimization plugin
wp plugin install imagify --activate
# OR
wp plugin install shortpixel-image-optimiser --activate

# Convert existing images to WebP (if plugin supports CLI)
wp media regenerate --yes
```

### Caching Setup

```bash
# Install caching plugin
wp plugin install wp-super-cache --activate
# OR
wp plugin install w3-total-cache --activate
# OR (for managed hosting)
# Server-level caching is preferred — check hosting panel

# Flush cache after setup
wp cache flush
```

### Database Cleanup

```bash
# Limit post revisions (add to wp-config.php)
# define('WP_POST_REVISIONS', 5);

# Delete old revisions
wp post delete $(wp post list --post_type=revision --format=ids) --force

# Clean transients
wp transient delete --expired

# Optimize database tables
wp db optimize
```

### Font Loading

If using the block theme:
- Ensure fonts are in `/wp/theme/{theme-slug}/assets/fonts/`
- Verify `fontFace` entries in `theme.json` use `"fontDisplay": "swap"`
- Preload the primary font file in the header template part or `functions.php`

## Step 3: Generate Performance Report

Write `qa/performance.md`:

```markdown
---
site_url: "[URL]"
audit_date: "[Date]"
status: draft
---

# Performance Audit

## Core Web Vitals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| LCP | [value] | ≤2.5s | [Pass/Fail] |
| FID/INP | [value] | ≤200ms | [Pass/Fail] |
| CLS | [value] | ≤0.1 | [Pass/Fail] |
| TTFB | [value] | ≤800ms | [Pass/Fail] |

## Audit Results

### Images
[Findings and actions taken]

### Fonts
[Findings and actions taken]

### Caching
[Findings and actions taken]

### CSS & JavaScript
[Findings and actions taken]

### Database
[Findings and actions taken]

### Server
[Findings and actions taken]

## Actions Taken

| Action | Impact | Status |
|--------|--------|--------|
| [Action description] | [Expected impact] | Done / Pending |

## Recommendations

[Prioritized list of remaining optimizations]
```

## Step 4: Approval Gate

Use the `AskUserQuestion` tool:

> "Performance audit complete. Review `qa/performance.md`. Proceed to **WP Security** hardening?"

Options:
- "Approved — proceed to security"
- "Run more optimizations first"
- "Skip security for now"
