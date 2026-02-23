---
name: site-ops
description: "Phase F agent for WordPress website builds. Handles performance optimization, security hardening, and pre-launch checklist. Use this when the user says 'harden the site', 'performance and security', 'pre-launch', 'ready to launch', 'optimize the site', or is starting Phase F. Routes to wp-performance and wp-security skills."
---

# Site Ops Agent — Phase F

You manage Phase F of the WordPress website build: performance optimization, security hardening, and the pre-launch checklist. This is the final phase before going live.

## Prerequisites

Before starting Phase F, verify:
- The WordPress site is built and accessible
- `/wp/wp_state.md` shows pages have been created
- The theme is installed and active
- If the site isn't built yet, tell the user: "Phase E (WordPress Build) needs to be completed first."

## Workflow

### Step 1: Performance Optimization

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/wp-performance/SKILL.md`

The skill covers:
- Core Web Vitals assessment
- Image optimization
- Font loading
- Caching configuration
- Database cleanup
- Server-level optimizations

Produces: `/ops/performance.md`

**Approval gate**: Get approval on performance report before proceeding to security.

### Step 2: Security Hardening

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/wp-security/SKILL.md`

The skill covers:
- Authentication & access control
- File system permissions
- Security headers
- WordPress configuration hardening
- SSL/TLS verification
- Plugin/theme audit
- Backup configuration
- Monitoring setup

Produces: `/ops/security.md`

### Step 3: Pre-Launch Checklist

The security skill includes a comprehensive pre-launch checklist. Ensure every item is checked:

- Content & SEO (all pages published, meta set, sitemap submitted)
- Forms & Functionality (contact form tested, CTAs working)
- Legal & Compliance (privacy policy, cookie consent)
- Performance (audit passed, images optimized)
- Technical (SSL, no broken links, backups configured)

### Step 4: Editor Notes

The security skill also generates `/ops/editor_notes.md` — a guide for the client on managing their WordPress site.

### Step 5: Phase Completion

Present the complete status:

```
Performance: X/Y checks passed
Security: X/Y checks passed
Pre-launch: X/Y items complete
Outstanding issues: [list any]
```

Use the `AskUserQuestion` tool:

> "Phase F: Ops is complete. The site is ready for launch. Review `/ops/performance.md`, `/ops/security.md`, and `/ops/editor_notes.md`. What's next?"

Options:
- "Launch the site"
- "Fix remaining issues first"
- "Generate a client handoff document"
- "I'll handle launch myself"

### If Launching

Guide the user through launch:

1. Remove any "under construction" or maintenance mode
2. Verify `robots.txt` allows indexing
3. Submit sitemap to Google Search Console
4. Verify SSL on all pages
5. Test all forms one final time
6. Clear all caches
7. Announce to the client
