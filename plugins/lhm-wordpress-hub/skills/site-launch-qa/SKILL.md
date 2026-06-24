---
name: site-launch-qa
description: "Pre-launch QA checklist for WordPress and Astro websites. Runs automated checks (links, SSL, robots.txt, sitemap, console errors, PageSpeed, meta tags, favicon) then walks the user through manual checks that AI cannot verify. Updates the project management doc with QA results at the end. Use this when the user says 'run the QA checklist', 'pre-launch QA', 'site QA', 'launch checklist', 'quality assurance check', 'ready to go live checklist', or 'QA the site before launch'."
---

# Site Launch QA

Run the full pre-launch QA checklist for a WordPress or Astro site. Automate every check possible using Playwright, then walk the user through the manual items that require human eyes or external system access. Write a QA results summary and update the project management doc.

## Before Starting

1. Read `LEARNED.md` from this skill's directory
2. Read `[client_root]/client_profile.md` — extract `platform:` (`wordpress` or `astro`) and `site_url:`
3. If `site_url` is not in the profile, ask the user: "What is the live/staging URL to run the QA against?"
4. Confirm with the user: "Running QA for [platform] site at [url] — does that look right?"
5. Read `references/checklist-wp.md` or `references/checklist-astro.md` based on platform

---

## Phase 1: Automated Checks

Use the Playwright MCP (`mcp__plugin_playwright_playwright__*`) to run automated checks. Navigate to the site URL and work through each check below. Run all automated checks **before** presenting manual items to the user.

### 1.1 Setup

```
browser_navigate → site_url
browser_take_screenshot → confirm page loaded
```

If the page fails to load, stop and tell the user the site is not reachable at that URL.

### 1.2 SSL / HTTPS

- Confirm the URL is served over HTTPS (no mixed-content warnings)
- Use `browser_console_messages` to check for mixed-content errors
- **Pass**: URL is HTTPS, no mixed-content console errors
- **Fail**: HTTP only, or mixed-content warnings present

### 1.3 Navigation Links

- Use `browser_snapshot` to extract all `<a>` elements in the main nav
- For each nav link: `browser_navigate` → check HTTP status is not 404/500
- Check footer links the same way
- **Pass**: All links resolve to valid pages
- **Fail**: List any broken links found

### 1.4 404 Page

- Navigate to `[site_url]/this-page-does-not-exist-qa-check`
- Confirm a custom 404 page appears (not a blank page or hosting default)
- **Pass**: Custom 404 page with site branding
- **Fail**: Default hosting 404 or blank page

### 1.5 Favicon

- Use `browser_evaluate` to check `document.querySelector("link[rel*='icon']")` returns a result
- **Pass**: Favicon link tag present
- **Fail**: No favicon link tag

### 1.6 Console Errors

- Navigate to each main page (home, contact, a service page if applicable)
- Run `browser_console_messages` on each
- **Pass**: No errors or warnings (info/log messages OK)
- **Fail**: List any errors or warnings

### 1.7 Robots.txt

- Navigate to `[site_url]/robots.txt`
- Confirm it exists and does NOT contain `Disallow: /` (which would block all crawlers)
- **Pass**: robots.txt exists, no blanket disallow
- **Fail**: Missing, or blocks all crawlers

### 1.8 Sitemap

- Navigate to `[site_url]/sitemap.xml` (WordPress) or `[site_url]/sitemap-index.xml` / `[site_url]/sitemap.xml` (Astro)
- Confirm the sitemap is present and contains URLs
- **Pass**: Sitemap found with at least 1 URL
- **Fail**: 404 or empty sitemap

### 1.9 Meta Tags Spot-Check

- On the homepage, use `browser_evaluate` to extract:
  - `document.title`
  - `document.querySelector("meta[name='description']")?.content`
  - `document.querySelector("link[rel='canonical']")?.href`
- **Pass**: Title present (not "Just another WordPress site" or default), description present, canonical present
- **Fail**: Missing or default values

### 1.10 Mobile Viewport

- `browser_resize` → 390×844 (iPhone 14 viewport)
- `browser_take_screenshot` → check layout looks correct
- Check `browser_console_messages` for layout errors
- **Pass**: Page renders without obvious layout breaks
- **Fail**: Horizontal scroll, overlapping elements, or layout errors

### 1.11 PageSpeed Score

- Navigate to `https://pagespeed.web.dev/report?url=[encoded_site_url]`
- `browser_wait_for` → wait for scores to load
- `browser_take_screenshot` → capture the scores
- Record mobile and desktop scores
- **Pass**: Mobile ≥ 50, Desktop ≥ 70 (flag if lower, don't hard-fail)

### 1.12 Google Tag Manager

- Use `browser_evaluate` to check for the GTM script: `document.querySelector("script[src*='googletagmanager.com/gtm.js']") !== null`
- Also check for the `<noscript>` iframe fallback in the body: `document.querySelector("noscript iframe[src*='googletagmanager']") !== null`
- Extract the GTM container ID if present (look for `GTM-XXXXXXX` pattern in the script src or inline dataLayer push)
- **Pass**: GTM script found in `<head>` and noscript fallback in `<body>`, container ID recorded
- **Fail**: GTM snippet missing entirely
- **Warning**: Script present but noscript fallback missing (degraded tracking for users with JS disabled)

### 1.13 Copyright Footer

- On homepage, use `browser_evaluate` to check for copyright text in the footer
- Look for current year (2025 or 2026)
- **Pass**: Copyright text with correct year found
- **Fail**: Missing or stale year

### Platform-Specific Automated Checks

**WordPress only:**
- Check WP Admin is not publicly listing users at `[site_url]/?author=1` (should redirect or 404)
- Navigate to `[site_url]/wp-admin` → confirm it loads the login page (not bypassed)

**Astro only:**
- Check for `_astro/` asset paths in page source (confirms build output is serving correctly)
- Check `browser_console_messages` for hydration errors

---

## Phase 2: Automated Check Summary

After completing all automated checks, present a clean summary table:

```
## Automated QA Results — [site_url]

| Check | Result | Notes |
|-------|--------|-------|
| SSL / HTTPS | ✅ Pass | |
| Navigation Links | ✅ Pass | |
| 404 Page | ✅ Pass | |
| Favicon | ✅ Pass | |
| Console Errors | ⚠️ Warning | 1 error on /contact |
| robots.txt | ✅ Pass | |
| Sitemap | ✅ Pass | |
| Meta Tags | ✅ Pass | |
| Mobile Viewport | ✅ Pass | |
| PageSpeed (mobile/desktop) | ⚠️ 48 / 72 | Mobile below threshold |
| Google Tag Manager | ✅ Pass | GTM-XXXXXXX |
| Copyright Footer | ✅ Pass | |
```

Flag any failures clearly. Do not proceed to Phase 3 until the user has acknowledged the automated results.

---

## Phase 3: Manual Checklist

Work through manual items in grouped batches. Present each group as an `AskUserQuestion` with checkboxes. Wait for the user to respond before moving to the next group.

### Group A: Content & Communication

Present as a single AskUserQuestion (multiSelect: true):

"**Content & Communication** — please tick off what you've confirmed:
- Text is checked and free from spelling, grammatical, and formatting errors
- Page titles and meta descriptions are unique and descriptive across all pages
- All images have appropriate alt text
- Contact details are correct and easy to find
- Social media links are set up and pointing to the right profiles
- Comments and pings are turned off (WordPress: Settings > Discussion)"

### Group B: Forms & Thank You Pages

"**Forms & Thank You Pages** — please tick off:
- All web forms submit correctly (test each one with a real submission)
- Email notifications from forms arrive at the correct email addresses
- Thank you pages load correctly after each form submission
- Spam protection is active on all forms (honeypot or reCAPTCHA)"

### Group C: Infrastructure & Hosting

**WordPress:**
"**Infrastructure** — please tick off:
- Domain is pointing to the correct hosting
- SSL certificate is installed and active
- Automatic backups are configured and running (ManageWP or hosting panel)
- Admin email updated: WP Admin → Settings → General → Administration Email Address
- Client user account set up with correct role
- Client user signed up for Gravatar"

**Astro:**
"**Infrastructure** — please tick off:
- Domain is pointing to Vercel/Netlify with correct DNS
- SSL certificate is active (auto-provisioned by host)
- Deployment pipeline is working (push → auto-deploy confirmed)
- Environment variables are set in the hosting dashboard (not committed to repo)"

### Group D: Analytics & Tracking

"**Analytics & Tracking** — please tick off:
- GA4 tracking is installed and recording sessions (check Real-Time in GA4)
- Key event tracking is set up and firing (contact form submits, calls, bookings)
- Google Search Console is set up and site is verified
- Sitemap has been submitted to GSC
- GTM container is published and tags are firing correctly (if applicable)"

### Group E: Browser & Device Testing

"**Cross-browser & Device Testing** — please tick off:
- Tested and working in Chrome
- Tested and working in Firefox
- Tested and working in Safari
- Tested and working in Edge
- Tested on an iOS device (real device, not just resize)
- Tested on an Android device (real device, not just resize)"

### Group F: Accessibility

"**Accessibility** — please tick off:
- Links are recognisable and have a visible focus state
- All form fields have associated labels (not just placeholder text)
- Colour contrast passes WCAG AA (use a checker like WebAIM Contrast Checker)
- Site is usable with a screen reader (basic walkthrough with VoiceOver or NVDA)"

### Group G: Platform-Specific

**WordPress only:**
"**WordPress Configuration** — please tick off:
- WordPress is on the latest stable version
- All plugins are updated to current versions
- WP Mail SMTP is activated and sending mail correctly
- Search engine indexing is enabled: WP Admin → Settings → Reading → uncheck 'Discourage search engines'
- Unused pages, templates, and global styles have been removed
- All Elementor contact forms have been renamed from defaults"

**Astro only:**
"**Astro Configuration** — please tick off:
- Build is running without errors or warnings in the CI pipeline
- All environment variables are set correctly in production
- Redirects are configured in `vercel.json` or `netlify.toml` (not in `.htaccess`)
- sitemap plugin is generating correctly"

### Group H: Performance & Caching

**WordPress only:**
"**Performance & Caching** — please tick off:
- Caching plugin is active and configured (LiteSpeed Cache, WP Rocket, or W3 Total Cache)
- GZIP or Brotli compression is enabled (confirm via Cloudflare or hosting)
- Images are compressed and correctly sized
- CSS and JS files are minified where possible"

**Astro only:**
"**Performance** — please tick off:
- Images are using Astro's `<Image>` component with correct sizing
- Build output has been verified (no unintended large JS bundles)
- Caching headers are set correctly via Vercel/Netlify config"

---

## Phase 4: QA Results File

After collecting all manual responses, write a QA results file at:

`[client_root]/wordpress/qa-launch-results.md` (WordPress)
`[client_root]/astro/qa-launch-results.md` (Astro)

Structure:

```markdown
# Site Launch QA — [Client Name]

**Date:** [today's date]
**URL:** [site_url]
**Platform:** [WordPress / Astro]
**Run by:** [ask user for their name if not known]

## Automated Checks

| Check | Result | Notes |
|-------|--------|-------|
[populate from Phase 2 table]

## Manual Checks

### Content & Communication
[list each item with ✅ or ❌]

### Forms & Thank You Pages
[list each item with ✅ or ❌]

[... all groups ...]

## Outstanding Issues

[List any items that were not ticked or flagged as failing]

## Sign-off

- [ ] All automated checks passed (or issues noted and accepted)
- [ ] All manual checks completed
- [ ] Outstanding issues documented and assigned
```

---

## Phase 5: PM Doc Update

After writing the QA results file:

1. Ask the user: "Happy for me to mark the QA checklist as complete in the project management doc?"
2. If yes, invoke `wp-project-manager` skill in "mark complete" mode for the QA/launch task
3. Append a note to the PM doc's Notes & Decisions section: "QA completed [date]. Results at `[path]/qa-launch-results.md`. Outstanding items: [count]."

---

## Additional Resources

- `references/checklist-wp.md` — Full WordPress checklist item reference with instructions
- `references/checklist-astro.md` — Full Astro checklist item reference
