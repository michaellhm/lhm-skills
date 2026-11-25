---
name: astro-prototype
description: "Build the static HTML prototype for an Astro website project, driven by UI UX Pro Max's design-system step, then write the brand style guide into the client repo and publish the prototype for client approval. Use this when the user says 'prototype', 'HTML prototype', 'static prototype', 'mockup', 'homepage prototype', 'preview the design', 'design the site', 'style guide', 'brand guide', or 'prototype the homepage' for an Astro build. Runs after the sitemap is approved. Requires the ui-ux-pro-max design-system run, plain HTML with no inline CSS or JS, a passing check_no_inline.py, a brain/Brand.md style guide, and explicit approval before anything is published to lhm-prototype."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill's narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.

# Astro Prototype

This skill turns the approved sitemap into a clickable, plain-HTML prototype of the homepage (and any other pages the brief names), and records the design as the client's style guide in `brain/Brand.md`. The prototype is what the client approves before the Astro build starts, so the design decisions made here are the ones the build inherits.

A local prototype that has not been pushed and has no observed commit is not published.

---

## Before Starting

1. **Delivery contract** — read `${CLAUDE_PLUGIN_ROOT}/references/website-departmental-delivery.md` and validate the envelope. Read `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before producing the artefact.
2. **Client context** — read and follow `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. Inspect the canonical client folder and any existing prototype or brand material. Preserve history and any established design. Never overwrite an existing prototype; add a new version.
3. **Approved sitemap** — read the approved `sitemap.json` from `astro-sitemap`. If the sitemap is not approved, stop and say so. Page names, slugs, keywords, audience and intent all come from it.
4. **Client repo** — the client repo made by `client-repo-setup` must exist, with `brain/Brand.md` present. If it does not, stop and run that skill first.
5. **Writing rules** — read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`. Australian English, no em or en dashes in customer copy, no invented facts, prices, staff or results, and AHPRA rules wherever they apply.
6. **Own learnings** — read `LEARNED.md` in this skill folder and apply any entries.

## Step 1: Scope

Use the `AskUserQuestion` tool:

> "Which pages should I prototype?"

Options: "Homepage only" (most common), "Homepage plus one service page", "All core pages", "Specific page".

Also ask whether the client already has an established brand (logo, colours, fonts). That decides how Step 2 treats the design-system output.

## Step 2: Run UI UX Pro Max (required)

This step is not optional. Do not pick colours, fonts or a style from memory.

1. Invoke the `ui-ux-pro-max` skill and use its design-system step: `search.py --design-system "<product type> <industry> <keywords>" -p "<Client Name>"`, run from that skill's own folder, using the exact command form the skill documents. Use the business type, services and audience from the approved sitemap as the query. Add `--persist` only if the skill's `design-system/` output folder is wanted in the working directory.
2. If the run returns something that does not fit (wrong industry, wrong tone), re-run with different keywords rather than forcing it. Use its `--domain` searches (style, typography, colour, ux) to settle any single dimension you are unsure about.
3. **Record an adopt, override or reject table** covering every recommendation: pattern, style, colours, typography, effects, and the anti-patterns it lists. For each, write `adopt`, `override` or `reject`, and one line of reasoning. This table is kept and goes into `brain/Brand.md` in Step 6.

Rules for the table:

- **Existing clients keep their established brand tokens.** Where the client already has colours, fonts or a logo, those win. Mark the matching recommendation `override` and use UI UX Pro Max for the parts the brand does not cover (layout pattern, spacing, component style, interaction).
- **AHPRA-regulated clients: reject testimonial and social-proof patterns.** If the recommended page pattern includes testimonials, star ratings, patient reviews, before-and-after, or "trusted by" counters, mark each `reject` with the reason "AHPRA advertising rules". Use credentials, process and plain service information instead.
- **Reject anything that needs inline CSS or JS to work**, and any pattern that implies a claim the client cannot back up.
- **Check contrast and tap targets** against the skill's own UX guidance before adopting a palette. Reject a combination that fails.
- **Never ship placeholder claims.** The prototype uses real copy from the sitemap and client records, not lorem ipsum, and not invented numbers.

## Step 3: Build the plain HTML prototype

Create the prototype in the client working folder (or the client repo's working area), one folder per page:

**Single version**

```
<slug>/
  index.html
  assets/
    css/style.css
    js/main.js
    images/
```

**Multiple versions** (when comparing directions)

```
<slug>/
  v1.html
  v2.html
  assets/            shared across all versions
    css/style.css
    js/main.js
    images/
```

Every page is `<slug>/index.html` (or `v1.html`, `v2.html` and so on). The folder must work when dropped on any static server.

### HTML skeleton

```html
<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Title] - Prototype</title>
  <link rel="stylesheet" href="./assets/css/style.css">
  <!-- web font <link> tags here if not self-hosted -->
</head>
<body>
  <header>...</header>
  <main>...</main>
  <footer>...</footer>
  <script src="./assets/js/main.js"></script>
</body>
</html>
```

### CSS file

`assets/css/style.css` starts with the design tokens taken from the adopted/overridden rows of the table:

```css
:root {
  --color-primary: #XXXXXX;
  --color-secondary: #XXXXXX;
  --color-accent: #XXXXXX;
  --color-background: #XXXXXX;
  --color-foreground: #XXXXXX;
  --color-muted: #XXXXXX;
  --color-surface: #XXXXXX;
  --font-heading: '[Heading Font]', serif;
  --font-body: '[Body Font]', sans-serif;
  --space-xs: 0.5rem; --space-sm: 1rem; --space-md: 1.5rem;
  --space-lg: 2rem; --space-xl: 3rem; --space-2xl: 5rem;
  --content-width: 800px;
  --wide-width: 1200px;
  --radius-sm: 4px; --radius-md: 8px;
}
```

Then base styles, layout helpers (`.container`, `.wide`, `.section`, `.section--alt`, `.text-center`, `.btn-group`) and component styles.

### Rules

- **No inline CSS and no inline JS.** No `style="..."` attributes, no `<style>` blocks, no `<script>` blocks without `src`. Styles go in `assets/css/style.css`, scripts in `assets/js/main.js`. Only `<script type="application/ld+json">` may stay inline. This is checked in Step 4, and the check must pass.
- **Real content** from the sitemap and client records. Cross-check addresses, phone numbers and locations against the client records before building.
- **Every colour, font and spacing value comes from the tokens.** No one-off hex values in components.
- **Responsive.** Use flexbox and grid. It must read well at phone width.
- **Accessible.** Visible focus states, sufficient contrast, labelled controls, `alt` text, `prefers-reduced-motion` respected, semantic headings.
- **JavaScript is allowed** in `assets/js/main.js` for menus, scroll effects and similar interactions.
- **FAQ sections use `<details>` and `<summary>`**, not JS-driven accordions.
- **Prefer CSS pseudo-elements for decorative icons** (for example an arrow via `::after`) over inline SVG markup.
- **Class names are descriptive and stable.** The Astro build reuses the prototype's CSS and class names, so choose clear names (`.hero-section`, `.card-grid`) and do not rename them after approval.
- **Multi-version navigator.** When there are several versions, add a floating `<nav class="version-nav">` before `</body>`, with its styling in `style.css` and an `aria-current="page"` on the current pill. Never style it with a `style` attribute.

## Step 4: Run the inline check

Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/astro-prototype/scripts/check_no_inline.py" <prototype folder>
```

It prints `<file>:<line>: <reason>` for each inline style attribute, inline style block or inline script, and exits 1 if there are any. Fix every finding and re-run until it exits 0. Do not continue while it fails, and do not argue the check down.

## Step 5: Preview and self-check

Open `index.html` in a browser and check the page at phone, tablet and desktop widths. Check the page against the sitemap: every section the page brief calls for is there, and nothing in the copy is invented.

## Step 6: Write the style guide to `brain/Brand.md`

Write the style guide into the client repo's `brain/Brand.md`, keeping its frontmatter (`type: brand`, `client`, `updated`, `sources`). Replace each `> gap:` line with real content, so that no `> gap:` line remains:

- **Colours** — each token with its hex, role and contrast note.
- **Typography** — heading and body fonts, scale, weights, line height.
- **Spacing and layout** — spacing scale, content widths, breakpoints.
- **Components** — buttons, cards, forms, navigation, FAQ, with the class names used in the prototype.
- **Do and don't** — including the AHPRA rejections and the anti-patterns UI UX Pro Max listed.
- **Design-system decisions** — the adopt, override and reject table from Step 2.

Set `updated` to today's date and fill `sources` with where this came from: the UI UX Pro Max run (with the query used), the prototype path, and any client brand material. A `Brand.md` with no `> gap:` lines is treated as "brand written" by the stage detector, so do not leave a placeholder behind, and do not remove a gap that you have not filled.

**Write it locally only. Do not commit or push `brain/Brand.md` yet.** A pushed `Brand.md` moves the stage detector on to `astro-build`, so it is committed in Step 9, only after the client approves the prototype. If the design changes during review, update the local `Brand.md` to match the version being reviewed.

## Step 7: Publish the prototype (after explicit approval)

Ask first, and wait for a clear yes:

> "Publish the prototype to `github.com/michaellhm/lhm-prototype` under `<client>/`?"

Publishing needs explicit approval every time. On a yes:

1. Check whether `lhm-prototype` is cloned locally. If not, clone `github.com/michaellhm/lhm-prototype`. Never create a separate per-client prototype repo.
2. Copy each page folder into `<lhm-prototype clone>/<client>/<slug>/`. One folder per client. Do not touch other clients' folders.
3. Commit and push:

   ```bash
   cd <lhm-prototype clone>
   git add <client>/<slug>/
   git commit -m "feat(<client>): add <slug> prototype"
   git push
   ```

4. Confirm with the observed commit and the URL it is served from. A prototype without an observed commit and URL is not live.

## Step 8: Approval stop

Stop here for client approval of the prototype and its copy. Use the `AskUserQuestion` tool:

> "Review the prototype. Does the design direction and the copy look right?"

Options: "Approved", "Changes needed", "Create another page prototype", "Create an alternate version to compare".

If several versions exist, record which one was approved (for example "v2 approved"). The Astro build starts only from an approved prototype. Changes go in as a new version or a revised page, never by overwriting history.

## Step 9: Record the approval, then push `Brand.md`

Only after the client's explicit approval:

1. Record the prototype approval in the internal project file (LHM Knowledge vault, per the routing contract): the approved version and its `lhm-prototype/<client>/` path, who approved it, when, and the evidence (for example the email or call). Read it back. `astro-lead`, `build-brain` and `astro-build` read the approved version from there.
2. Make sure the local `brain/Brand.md` matches the approved version, then commit and push the client repo to `main`:

   ```bash
   git add brain/Brand.md
   git commit -m "docs(brain): write brand style guide from approved prototype"
   git push
   ```

3. Read the push result back and report the actual commit. If the push failed, say so.

If the client has not approved, leave `Brand.md` uncommitted and report the prototype as awaiting approval.

## Handback

Return the departmental handback per the delivery contract: prototype path, adopt/override/reject table location (`brain/Brand.md`), the `check_no_inline.py` result, the publish commit and URL (or "not published"), the approval status and where it is recorded, and the `Brand.md` commit (or "not pushed: awaiting approval").
