---
name: wp-security
description: "Security hardening checklist for WordPress sites. Headers, permissions, plugin audit, backups, and pre-launch checks. Use this when the user says 'security hardening', 'secure WordPress', 'security audit', 'pre-launch checklist', 'security headers', 'harden WordPress', or 'launch checklist'. Phase 6 of the website build. Can also be run standalone."
---

# WP Security

Security hardening and pre-launch checklist for WordPress sites. Covers security headers, file permissions, authentication, plugin audit, backups, and monitoring.

## Before Starting

1. **Read WP state** — read `/wp/wp_state.md` for current configuration
2. **Read WP-CLI reference** — read `${CLAUDE_PLUGIN_ROOT}/references/wp-cli-reference.md`
3. Ask for the site URL and hosting environment if not already known

## Step 1: Security Audit

### Authentication & Access

- [ ] Admin username is NOT "admin"
- [ ] Strong passwords enforced
- [ ] Two-factor authentication enabled for admin accounts
- [ ] Login attempt limiting enabled
- [ ] wp-admin accessible only to authorized users
- [ ] User roles follow least-privilege principle
- [ ] Default "subscriber" role set for new registrations (or registration disabled)

### File System

- [ ] File permissions: directories 755, files 644
- [ ] `wp-config.php` is 640 or 600
- [ ] `.htaccess` protected
- [ ] Directory browsing disabled
- [ ] `wp-content/uploads` doesn't execute PHP
- [ ] File editing disabled in admin (`DISALLOW_FILE_EDIT`)

### Security Headers

Recommended headers (configure via plugin, `.htaccess`, or server config):

```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: [site-specific policy]
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### WordPress Configuration

- [ ] `WP_DEBUG` is `false` in production
- [ ] `DISALLOW_FILE_EDIT` is `true`
- [ ] Database table prefix is NOT `wp_`
- [ ] Security keys and salts are set and unique
- [ ] XML-RPC disabled (if not needed)
- [ ] REST API restricted (if not needed publicly)
- [ ] WordPress version hidden from source

### SSL/TLS

- [ ] SSL certificate installed and valid
- [ ] HTTP → HTTPS redirect in place
- [ ] Mixed content resolved
- [ ] HSTS header configured

### Plugins & Themes

- [ ] All plugins updated to latest versions
- [ ] Unused plugins deactivated AND deleted
- [ ] Unused themes deleted (keep one default as fallback)
- [ ] Plugins from reputable sources only
- [ ] No nulled/pirated plugins or themes

### Backups

- [ ] Automated backup schedule configured
- [ ] Backups stored off-site (not just on the server)
- [ ] Backup restoration tested
- [ ] Database and files both included

### Monitoring

- [ ] Uptime monitoring configured
- [ ] File integrity monitoring enabled
- [ ] Security plugin installed and configured
- [ ] Email alerts for admin login, plugin changes, core updates

## Step 2: Hardening Actions

### Install Security Plugin

```bash
# Wordfence
wp plugin install wordfence --activate

# OR Sucuri
wp plugin install sucuri-scanner --activate

# OR iThemes Security
wp plugin install better-wp-security --activate
```

### wp-config.php Hardening

Add to `wp-config.php`:

```php
// Disable file editing
define('DISALLOW_FILE_EDIT', true);

// Limit post revisions
define('WP_POST_REVISIONS', 5);

// Force SSL for admin
define('FORCE_SSL_ADMIN', true);

// Disable debug in production
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);
```

### Regenerate Security Keys

```bash
wp config shuffle-salts
```

### Disable XML-RPC

```bash
# Via plugin or .htaccess
# .htaccess method:
# <Files xmlrpc.php>
#   Require all denied
# </Files>
```

### Backup Setup

```bash
# Install backup plugin
wp plugin install updraftplus --activate
# Configure via admin panel — automated daily backups to cloud storage
```

## Step 3: Pre-Launch Checklist

Before going live, verify:

### Content & SEO
- [ ] All pages published and reviewed
- [ ] SEO titles and meta descriptions set for all pages
- [ ] XML sitemap generated and accessible
- [ ] robots.txt configured correctly
- [ ] Google Search Console verified
- [ ] Google Analytics / tracking configured
- [ ] Favicon and site icon set
- [ ] 404 page configured
- [ ] Redirects set up (if migrating from old site)

### Forms & Functionality
- [ ] Contact form tested (sends to correct email)
- [ ] All CTAs link to correct destinations
- [ ] Phone numbers clickable on mobile
- [ ] Email addresses linked correctly
- [ ] Maps/embeds loading correctly

### Legal & Compliance
- [ ] Privacy policy page published
- [ ] Cookie consent configured (if required)
- [ ] Terms of service (if applicable)
- [ ] Accessibility basics: alt text, contrast, keyboard navigation
- [ ] Industry compliance (AHPRA, NDIS, etc. from constraints.md)

### Performance
- [ ] Performance audit passed (see `qa/performance.md`)
- [ ] Mobile-friendly test passed
- [ ] All images optimized

### Technical
- [ ] SSL working on all pages
- [ ] No broken links
- [ ] WordPress and all plugins updated
- [ ] Caching enabled
- [ ] Backups configured and tested
- [ ] Search engines allowed to index (remove noindex if present)

## Step 4: Generate Security Report

Write `qa/security.md`:

```markdown
---
site_url: "[URL]"
audit_date: "[Date]"
status: draft
---

# Security Audit

## Summary

| Category | Items Checked | Passed | Issues |
|----------|--------------|--------|--------|
| Authentication | X | X | X |
| File System | X | X | X |
| Headers | X | X | X |
| Configuration | X | X | X |
| SSL/TLS | X | X | X |
| Plugins/Themes | X | X | X |
| Backups | X | X | X |
| Monitoring | X | X | X |

## Issues Found

| Issue | Severity | Status | Action |
|-------|----------|--------|--------|
| [Description] | High/Medium/Low | Fixed/Pending | [What was done] |

## Pre-Launch Checklist

[Completed checklist from above]

## Recommendations

[Prioritized list of remaining actions]
```

## Step 5: Create Editor Notes

Write `qa/editor_notes.md`:

```markdown
# Editor Notes

Guide for the client or content editors on managing the WordPress site.

## Logging In

- URL: [site]/wp-admin
- Use your assigned credentials
- Enable two-factor authentication on first login

## Adding/Editing Pages

1. Go to Pages → select the page
2. Click Edit
3. Modify content using the block editor
4. Click Update to save

## Using Block Patterns

When adding new sections to pages:
1. Click the + button
2. Go to Patterns tab
3. Select from the custom patterns (Hero, CTA, Cards, etc.)
4. Replace placeholder content

## Important Notes

- **Do not deactivate** the security or caching plugins
- **Do not update** plugins without checking with your developer first
- Content changes are safe to make anytime
- For structural changes (new pages, menu updates), contact your developer
```

## Step 6: Completion

Use the `AskUserQuestion` tool:

> "Security hardening and pre-launch checklist complete. The site is ready for launch. Review `qa/security.md` and `qa/editor_notes.md`. What's next?"

Options:
- "Launch the site"
- "More changes needed"
- "Generate a handoff document for the client"
