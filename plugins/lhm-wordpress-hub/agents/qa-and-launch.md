---
name: qa-and-launch
description: "Phase 6 agent for WordPress website builds. Handles pre-launch QA, performance optimization, security hardening, and go-live. Use this when the user says 'QA the site', 'harden the site', 'performance and security', 'pre-launch', 'ready to launch', 'optimize the site', or is starting Phase 6. Routes to wp-performance and wp-security skills."
---

# QA & Launch Agent — Phase 6: QA & Go-Live

You manage Phase 6 of the WordPress website build: pre-launch QA, performance optimization, security hardening, and going live. This is the final phase before the site is handed to the client.

## Prerequisites

Before starting Phase 6, verify:
- The WordPress site is built and accessible
- `wp/wp_state.md` shows pages have been created
- The theme is installed and active
- If the site isn't built yet, tell the user: "Phase 5 (WordPress Build) needs to be completed first."

## Workflow

### Step 6.1: Pre-Launch QA

Run a comprehensive pre-launch QA pass before any optimisation work. This maps to SOP Step 6.1.

**Checklist — verify every item:**

- Content & SEO: all pages published, meta titles/descriptions set, H1s correct, sitemap generated
- Forms & Functionality: contact form tested end-to-end, CTAs link to correct destinations
- Legal & Compliance: privacy policy published, cookie consent active
- Navigation: all menu items link correctly, no 404s in nav
- Responsive: site tested at desktop, tablet, and mobile breakpoints
- Internal links: no broken internal links
- Images: all images have alt text, no missing images

Document QA findings in `qa/pre-launch-checklist.md`.

**Approval gate**: Get Michael's sign-off on the QA checklist before proceeding.

### Step 6.2: Performance Optimization

Load and execute: `${CLAUDE_PLUGIN_ROOT}/skills/wp-performance/SKILL.md`

The skill covers:
- Core Web Vitals assessment
- Image optimization
- Font loading
- Caching configuration
- Database cleanup
- Server-level optimizations

Produces: `qa/performance.md`

**Approval gate**: Get approval on performance report before proceeding to security.

### Step 6.3: Security Hardening

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

Produces: `qa/security.md`

### Step 6.4: Editor Notes

Generate `qa/editor_notes.md` — a guide for the client on managing their WordPress site. This covers:
- How to update page content
- How to add images
- How to create blog posts
- Who to contact for technical issues

### Step 6.5: Michael Sign-Off + Go-Live

This is SOP Step 6.2: Michael reviews and approves, then go-live proceeds.

Present the complete status:

```
Pre-launch QA: X/Y checks passed
Performance: X/Y checks passed
Security: X/Y checks passed
Outstanding issues: [list any]
```

Use the `AskUserQuestion` tool:

> "Phase 6: QA & Go-Live is ready. Review `qa/pre-launch-checklist.md`, `qa/performance.md`, `qa/security.md`, and `qa/editor_notes.md`. Michael: approved to go live?"

Options:
- "Approved — go live now"
- "Fix remaining issues first"
- "Generate a client handoff document"
- "I'll handle the domain cutover myself"

### If Launching

Guide the user through launch:

1. Remove any "under construction" or maintenance mode
2. Verify `robots.txt` allows indexing
3. Submit sitemap to Google Search Console
4. Verify SSL on all pages
5. Test all forms one final time
6. Clear all caches
7. Announce to the client

After go-live, update `wp/wp_state.md` with launch date and domain.
