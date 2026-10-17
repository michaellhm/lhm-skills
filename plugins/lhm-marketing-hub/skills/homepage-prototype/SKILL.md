---
name: homepage-prototype
description: Design and build a client-ready homepage prototype (single self-contained HTML file) for an LHM client or prospect, starting from their proposed sitemap and live website. Researches the business, writes three target-market personas and a homepage brief, then builds a conservative, professional, non-AI-looking homepage in the client's own brand, verifies it at desktop and phone widths, and (only when explicitly approved) publishes it to lhmstaging. Use this whenever someone asks for a homepage mock-up, homepage prototype, homepage concept, homepage redesign, "make their homepage look like a $20m business", a pitch homepage to sit beside a proposed sitemap, or wants to rebuild a client's homepage design, even if they don't say "prototype". For the sitemap itself use prospect-sitemap-opportunity or client-sitemap-plan first; for building the real WordPress or Astro site use the website build skills.
---

# Homepage Prototype

This skill turns a client's proposed sitemap and current website into one polished homepage concept they can click through. The output is a single `index.html` (plus a short personas brief) that looks like it belongs to a well-run, established business: calm, credible, specific to that client, and free of the tells that make a page read as AI-generated.

Every client is different. The section library and rules here are a starting kit, not a template to fill in. Decide what this business's homepage needs from the research, then pick, reorder, drop or invent sections to suit.

## The process

Work through these stages in order. Show Michael (or whoever asked) the brief before building if anything about the audience or structure is uncertain; otherwise keep moving and let them react to a real page.

### 1. Gather the inputs

- **Proposed sitemap.** Look for the sitemap deliverable in the client's working folder (usually `prospect-sitemap-opportunity/YYYY-MM/sitemap.json` and its HTML). The homepage nav, service names, funding/getting-started labels and location structure must match it, because the homepage is the front door to that architecture. If there is no sitemap yet, say so and suggest running `prospect-sitemap-opportunity` (prospects) or `client-sitemap-plan` (clients) first.
- **Current website.** Fetch the homepage and two or three inner pages (a service page, a location or clinic page, the team page). Extract: their hero line and any messaging worth keeping, services, funding schemes, locations and addresses, phone number, reviews and testimonials (verbatim), partner and accreditation logos, awards, team members, and every reasonably sized photo and video. Photos on service and location pages are often far better than the homepage ones, so check them. Use the browser tools or `curl`; `scripts/scan_site_assets.py` lists images with their pixel sizes.
- **Brand.** Take colours from the live site itself, especially the footer, buttons and clinic or location pages, not just the logo. Note the site's current fonts. Run `scripts/contrast.py` on every text/background pair you plan to use.
- **Reference sites.** If the person names reference sites or earlier LHM prototypes (for example on lhmstaging.net/prototypes/), look at them for structure and tone, not for copy.

### 2. Write the personas and homepage brief

Identify the three main target markets who land on this homepage (plus referrers if referrals matter to the business, as they do for NDIS, aged care and most allied health). For each, write a short persona: who they are, what they search, what they need to see quickly, what worries them, and what wins them. Then build a table mapping each need to a homepage section.

Save it as `personas-and-homepage-brief.md` next to the prototype, using `assets/personas-brief-template.md`. `assets/healthstin-personas-example.md` shows a finished one. This brief is the spec for the page. If a section on the page doesn't serve a need in the brief, cut it.

### 3. Set the design system

- Use the client's own palette: a dark neutral for headings, dark bands and footer; their brand colour as the accent; a darker shade of the brand colour for buttons on white (at least 4.5:1); and a neutral light grey for alternate sections. Add a secondary brand colour (for example the referral purple at Healthstin) only for one specific job.
- Pick a readable, professional font pairing. Lexend for headings with Source Sans 3 for body works well for health and ageing audiences. Matching the client's current font is also fine; ask if unsure.
- **Using UI UX Pro Max (optional helper).** If the `ui-ux-pro-max` skill is installed, you can run its `--design-system` search for typography and palette ideas and its `--domain ux` checklist for accessibility. Treat its output as input, not direction: its style and pattern picks (for example "exaggerated minimalism" or "before and after") often produce exactly the AI look this skill exists to avoid. The client's brand and the rules in `references/anti-ai-design.md` win every conflict.

### 4. Build the page

Read `references/anti-ai-design.md` before writing any markup, then `references/section-library.md` for the proven sections and how each one should be built.

- One self-contained `index.html`: inline CSS and JS, Google Fonts link, inline SVG icons. Images may be hotlinked from the client's site for a prototype (check they load with a staging referrer) or saved into an `assets/` folder beside it.
- Container around 1400px wide. Mobile-first CSS with breakpoints at roughly 640, 960 and 1200px.
- Copy: plain, specific, Australian spelling, no em dashes. Keep the client's best existing lines (Healthstin kept "Movement is for everyone."). Quote reviews and testimonials word for word. Never invent statistics, response times, awards or claims; take figures only from the client's own site and say where they came from.
- Add `<meta name="robots" content="noindex, nofollow">` and a small fixed note at the bottom ("Homepage concept by Local Health Marketing, Month Year") so nobody mistakes it for a live site.
- Save to the client's working folder: `homepage-prototype/YYYY-MM/index.html` alongside the brief.

`assets/healthstin-homepage-example.html` is a complete worked example built with this process. Use it for patterns and code, not as a skin to recolour.

### 5. Verify before showing anyone

Follow `references/qa-and-verification.md`. In short: check the nav stays on one row at 1280 and 1440, nothing scrolls sideways at 375, all images and video load, interactive pieces (menus, tabs, carousels, toggles) work by mouse and keyboard, contrast passes, and the copy has no AI tells. Look at real screenshots, not just DOM numbers; `scripts/screenshot.sh` captures and crops full-page desktop shots.

### 6. Iterate with feedback

Expect several rounds. Typical feedback and the fixes that worked are in `references/feedback-patterns.md`; read it when feedback arrives, because the same comments come up client after client.

### 7. Publish (only when explicitly approved)

Publishing puts the page in front of the client. Only do it when the person asks in this conversation, and follow `references/publishing.md`: independent QA, the `michaellhm/lhm-prototype` repo conventions, hash readback of the live URL. Offer to publish the matching sitemap at the same time.

## What to hand back

- Links to the prototype file and the brief.
- What each section is for, in a sentence or two, tied back to the personas.
- What was checked and at what widths.
- Anything that needs the client: missing photos, claims to confirm, services that only some locations offer, and so on.
