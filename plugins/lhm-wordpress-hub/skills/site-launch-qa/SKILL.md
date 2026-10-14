---
name: site-launch-qa
description: "Combined website completion and pre-launch QA for WordPress and Astro, with adaptive coaching for Jaimee, full-site SEO, sitemap generation/repair and GSC verification, real-phone review and tests derived from approved client requests. Runs automated checks (links, SSL, robots.txt, sitemap, console errors, PageSpeed, meta tags, favicon) then walks the user through manual checks that AI cannot verify. Updates the project management doc with QA results at the end. Use this when the user says 'run the QA checklist', 'pre-launch QA', 'site QA', 'launch checklist', 'quality assurance check', 'ready to go live checklist', or 'QA the site before launch'."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill’s narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Site Launch QA

Run the full pre-launch QA checklist for a WordPress or Astro site. Offer self-led checks, step-by-step coaching or delegated accessible checks. Use browser automation according to that choice, then guide the reviewer through remaining human/device or account steps. Write a QA results summary and update the project management doc.

## Combined completion workflow

Read and follow [Website completion QA](../../references/website-completion-qa.md) before the phases below. It governs source-based requirements, Jaimee’s real-device checks, tracking evidence, staging/live distinctions and completion status where older checklist wording differs.

Use this as the single completion-QA entry point: gather project requirements, run the automated checks below and `visual-qa` for browser/design evidence, guide Jaimee through the phone and client-request tests, then use `website-delivery-qa` to verify the combined handback. Keep a single report with linked specialist evidence. Do not automatically message Jaimee or assign a task merely because a report was prepared.

## Before Starting

1. Read `LEARNED.md` from this skill's directory
2. Read `[client_root]/client_profile.md` — extract `platform:` (`wordpress` or `astro`) and `site_url:`
3. If `site_url` is not in the profile, ask the user: "What is the live/staging URL to run the QA against?"
4. Confirm with the user: "Running QA for [platform] site at [url] — does that look right?"
5. Read `references/checklist-wp.md` or `references/checklist-astro.md` based on platform

---

## Phase 1: Automated Checks

Use the Playwright MCP (`mcp__plugin_playwright_playwright__*`) to run automated checks. Navigate to the site URL and work through each check below. Offer the coaching mode first. Run authorised automated checks before requesting their related manual confirmations; in self-led or coaching mode, let Jaimee perform checks with guidance and review her evidence rather than silently taking over.

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

- Use `browser_evaluate` to extract every `link[rel~='icon']` and `link[rel='apple-touch-icon']`, including resolved `href`, `type`, and `sizes`
- Confirm at least one standard favicon is linked from the document head
- Request every linked icon URL and confirm it returns a successful response with an image content type
- For Astro sites, confirm the icon is client-branded and is not Astro's default starter favicon (inspect the asset name/content or compare it with the scaffolded default)
- Record Apple touch icon absence as a warning; fail it when the build standard or approved design explicitly requires one
- **Pass**: Branded favicon link present and its asset loads successfully
- **Fail**: Link missing, asset broken/non-image, or framework/template default still in use
- **Warning**: Branded favicon works but Apple touch icon is absent

### 1.6 Console Errors

- Navigate to each main page (home, contact, a service page if applicable)
- Run `browser_console_messages` on each
- **Pass**: No errors or warnings (info/log messages OK)
- **Fail**: List any errors or warnings

### 1.7 Robots.txt

Follow [Website SEO QA](../../references/website-seo-qa.md): check the root file, effective rules for intended pages and resources, staging/live restrictions and the production Sitemap directive. Prepare precise corrections for missing or unsuitable rules, then apply only within the established authority and verify live readback. Do not reduce this check to searching for `Disallow: /`.

### 1.8 Sitemap, repair and GSC

Discover the actual sitemap/index and child sitemaps, validate XML and compare all entries against the intended canonical page inventory. If missing or invalid, prepare a platform-appropriate generator/configuration repair and validate it. Follow the bounded repair workflow for application/deployment and verify the resulting live sitemap before authorised GSC submission. Record site-side, deployment and GSC processing results separately. A missing default path, prepared XML or submission acknowledgement alone cannot pass this check.

### 1.9 Full-site SEO audit

Follow the complete inventory and per-page checks in `../../references/website-seo-qa.md`, covering titles, descriptions, canonicals, LHM’s one-H1 convention, heading structure, indexing and image loading/appropriate alt text. Include every agreed public HTML page and cross-page duplicates. Record coverage gaps; the homepage is only the first page, never a substitute for the full inventory.

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

The GTM presence result above is only the installation check. Complete the account-ID, published-container, duplicate and firing checks in the combined protocol before marking tracking passed.

### 1.13 Copyright Footer

- On homepage, use `browser_evaluate` to check for copyright text in the footer
- Look for the current year at execution time
- **Pass**: Copyright text with correct year found
- **Fail**: Missing or stale year

### Platform-Specific Automated Checks

**WordPress only:**
- Check WP Admin is not publicly listing users at `[site_url]/?author=1` (should redirect or 404)
- Navigate to `[site_url]/wp-admin` → confirm it loads the login page (not bypassed)

**Astro only:**
- Check for `_astro/` asset paths in page source (confirms build output is serving correctly)
- Check `browser_console_messages` for hydration errors
- Test production redirect URLs directly. On Cloudflare Pages, verify a Pages Function is not intercepting a path that should be handled by `public/_redirects`.

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
| Full-site SEO | Pass / Fail / Pending / Blocked | Checked / expected pages; inventory link |
| Mobile Viewport | ✅ Pass | |
| PageSpeed (mobile/desktop) | ⚠️ 48 / 72 | Mobile below threshold |
| Google Tag Manager | ✅ Pass | GTM-XXXXXXX |
| Copyright Footer | ✅ Pass | |
```

Flag any failures clearly. Do not proceed to Phase 3 until the user has acknowledged the automated results.

---

## Phase 3: Manual Checklist

Follow the coaching mode chosen in the combined protocol. In self-led mode give a short section checklist; in coaching mode give one practical step and wait for the result; in delegated mode run available authorised checks and ask only for human/access-dependent observations. Use the available question/chat interface; the example checklists below are prompts, not mandatory checkbox-tool calls. Never demand blanket confirmation for checks already evidenced.

### Group 0: Jaimee’s phone and client requirements

Run the guided real-device review and the source-linked client requirements matrix in `../../references/website-completion-qa.md`. Ask for exact observations: menu behaviour, dialler number, booking destination and new-tab behaviour where required. Record pending, failed and blocked items; unanswered items are not passes. Browser screenshots do not replace this group.

### Group A: Content & Communication

In self-led mode, offer this compact checklist; in coaching mode, work through its items one at a time:

"**Content & Communication** — please tick off what you've confirmed:
- Text is checked and free from spelling, grammatical, and formatting errors
- Page titles and meta descriptions are unique and descriptive across all pages
- Meaningful images have appropriate alt text; decorative images use empty alt
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

Apply the tracking/search verification protocol before accepting these confirmations. Record IDs, tested actions and received-event evidence; snippet presence and broad tick boxes alone cannot pass this group.

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

Save and incrementally update the combined report under the verified `work_root/site-launch-qa/YYYY-MM/qa-launch-results.md`, including pending checks even if the session ends early. Include the source-linked requirements matrix, tester/device details, automated and real-device evidence, tracking/search results, full-site SEO inventory and coverage, sitemap/robots repairs and GSC state, coaching mode/resume step, fix owners, accepted exceptions and retest history from the combined protocol. Do not save a full deliverable in the knowledge root.

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
[list each item with pass, fail, pending, blocked or not_applicable and evidence]

### Forms & Thank You Pages
[list each item with pass, fail, pending, blocked or not_applicable and evidence]

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

After writing and reading back the QA results file, run `website-delivery-qa` on the combined handback. Pending mandatory checks, unresolved failures or missing required evidence prevent a completion claim; update progress truthfully instead. Only when eligible for sign-off:

1. Ask the user: "Happy for me to mark the QA checklist as complete in the project management doc?"
2. If yes, invoke `lhm-project-hub:wp-project-manager` skill in "mark complete" mode for the QA/launch task
3. Append a note to the PM doc's Notes & Decisions section: "QA completed [date]. Results at `[path]/qa-launch-results.md`. Outstanding items: [count]."

---

## Additional Resources

- `../../references/website-seo-qa.md` — Full-site SEO, sitemap repair, robots.txt and GSC evidence
- `references/checklist-wp.md` — Full WordPress checklist item reference with instructions
- `references/checklist-astro.md` — Full Astro checklist item reference
