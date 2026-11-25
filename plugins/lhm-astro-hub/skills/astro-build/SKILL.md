---
name: astro-build
description: "Build the Astro website in the client repo's site/ folder from the approved plain-HTML prototype. Use this when the user says 'build the Astro site', 'convert the prototype to Astro', 'astro build', 'scaffold the Astro project', 'convert to Astro', 'build out the Astro pages', or 'start the build stage'. Requires the approved prototype from astro-prototype at lhm-prototype/<client>/ and the client repo from client-repo-setup. Converts prototype sections to .astro components, extracts copy to content collections, wires up SEO, sitemap and robots.txt, asks the form question and hands off to astro-form, then configures Cloudflare Pages (root directory site) and deploys staging from main. Production deploy needs explicit approval."
---
## Client file routing

For client-specific work, first read [Client knowledge and working-file routing](../../references/obsidian-context-contract.md). Resolve knowledge records in the shared LHM Knowledge vault and deliverables under the verified Claude Workspace/Current Clients folder. These routing rules override legacy single-folder examples; preserve this skill's narrower approval and privacy rules. For non-client work, retain the appropriate private or internal destination.


# Astro Build

The build stage. Converts the approved plain-HTML prototype into a production Astro project in the `site/` folder of the client repo: structured components, typed content collections, SEO layer, sitemap, form wiring and deployment config.

**Where things live.** The client repo (made by `client-repo-setup`) holds `README.md`, `brain/`, `skills/` and `site/`. The Astro project lives in `site/`, never at the repo root. Every `npm`, `astro` and `wrangler` command below runs from `site/`. Cloudflare Pages builds with root directory `site`.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/astro-build/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/astro-build-standard.md`. It is the source of truth for all conventions. Where it shows `<client>-site/` as the project root, the project root is `site/` in the client repo.
3. Read `${CLAUDE_PLUGIN_ROOT}/references/website-departmental-delivery.md` and validate the dispatch envelope. Read `${CLAUDE_PLUGIN_ROOT}/references/delivery-artifact-contract.md` before producing the artefact.
4. Read the client's contact, location and booking details (business name, addresses, phone, email, booking URL, production domain) from the client overview in the internal LHM Knowledge vault or other verified client records, resolved per `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`. `brain/Profile.md` is not filled until `build-brain`, after this stage, so do not source these details from it. If a detail is not verified, ask; never invent it. Read `brain/Brand.md` (colour tokens, typography, spacing, style guide written by `astro-prototype`) in the client repo.
5. Confirm the prototype exists and is approved: `lhm-prototype/<client>/` (plain HTML with `assets/css`, `assets/js`, `assets/images`), from `astro-prototype`. Read its CSS for the real token values.
6. Confirm the client repo is cloned (default `~/Documents/Projects/<client>/<slug>/`) and has `site/`.
7. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`. Australian English, no em or en dashes in customer copy, no invented facts, prices, staff or results, AHPRA rules where they apply.

If the prototype is not approved or the repo is not cloned, stop and tell the user what is needed.

## Step 0: Ask the form question

Use the `AskUserQuestion` tool:

> "Does this site need a contact or enquiry form?"

Options: "Yes", "No form". Record the answer in the internal project file. If yes, `astro-form` runs after the pages exist (Step 8b below); it asks the GoHighLevel question itself.

## Step 1: Scaffold the Astro Project

Run from the `site/` folder of the client repo (create it if missing):

```bash
npm create astro@latest . -- --template minimal --typescript strict --no-install
npm install
npx astro add sitemap
```

The `.` installs into `site/` only. Confirm nothing outside `site/` changed (`README.md`, `brain/`, `skills/` must be untouched). If the scaffold overwrote anything, restore it from git. Never scaffold at the repo root.

Verify the project runs:

```bash
npm run dev
```

Open `http://localhost:4321` and confirm the dev server starts.

## Step 2: Configure `astro.config.mjs`

Replace the generated config with the LHM baseline:

```js
import { defineConfig } from 'astro/config'
import sitemap from '@astrojs/sitemap'

export default defineConfig({
  site: 'https://[clientdomain].com.au',  // update to actual production domain
  trailingSlash: 'never',
  output: 'static',
  integrations: [
    sitemap(),
  ],
  image: {
    domains: [],
  },
})
```

Ask the user for the production domain if it is not in the verified client records. If the domain is not confirmed yet, use a placeholder but flag it prominently in the internal project file's notes — sitemap and canonical URLs won't be correct until this is set.

## Step 3: Create Global Styles

Create `src/styles/global.css`. Extract design token CSS variables from the prototype's `assets/css` files and `brain/Brand.md`:

```css
/* ============================================
   Design Tokens — [Client Name]
   Source: brain/Brand.md and lhm-prototype/<client>/assets/css
   ============================================ */
:root {
  /* Colours */
  --color-primary: [HEX from brain/Brand.md];
  --color-primary-dark: [HEX];
  --color-secondary: [HEX];
  --color-background: #ffffff;
  --color-foreground: [HEX];
  --color-muted: [HEX];
  --color-surface: [HEX];

  /* Typography */
  --font-heading: '[Heading Font]', serif;
  --font-body: '[Body Font]', sans-serif;

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 1.5rem;
  --space-lg: 2rem;
  --space-xl: 3rem;
  --space-2xl: 5rem;
  --space-3xl: 8rem;

  /* Layout */
  --content-width: 800px;
  --wide-width: 1200px;
  --container-padding: 1.5rem;

  /* Radius / shadow */
  --radius-sm: 4px;
  --radius-md: 8px;
  --shadow-card: 0 4px 16px rgba(0,0,0,0.08);
}

/* ============================================
   Utility classes — shared across components
   ============================================ */
*, *::before, *::after { box-sizing: border-box; }

body {
  font-family: var(--font-body);
  color: var(--color-foreground);
  background: var(--color-background);
  line-height: 1.6;
  margin: 0;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  line-height: 1.2;
}

.container {
  max-width: var(--content-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
}

.wide {
  max-width: var(--wide-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
}

.section {
  padding: var(--space-2xl) var(--container-padding);
}

.section--alt { background: var(--color-surface); }
.section--dark { background: var(--color-primary); color: var(--color-background); }

/* Button base — extend in components */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-primary {
  background: var(--color-primary);
  color: #ffffff;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}
```

## Step 4: Build Layout Components

### `src/components/BaseHead.astro`

Create this component to own all `<head>` content. Populate from the verified client records (business name, site URL).

Before wiring the component:
- Replace Astro's default favicon with a favicon based on the approved client brand.
- Add `public/favicon.svg`, `public/favicon.ico` (fallback), and `public/apple-touch-icon.png`.
- Do not ship the Astro logo or another framework/template favicon.
- Use the shared head component so favicon markup appears on every page.

Then add the favicon links alongside the other site-wide metadata:

```astro
---
interface Props {
  title: string
  description: string
  image?: string
  canonicalURL: string
}

const { title, description, image, canonicalURL } = Astro.props
const siteTitle = '[Client Business Name]'  // from the verified client records
---

<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} | {siteTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalURL} />
<link rel="sitemap" href="/sitemap-index.xml" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />

<meta property="og:type" content="website" />
<meta property="og:url" content={canonicalURL} />
<meta property="og:title" content={`${title} | ${siteTitle}`} />
<meta property="og:description" content={description} />
{image && <meta property="og:image" content={new URL(image, canonicalURL).toString()} />}

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:url" content={canonicalURL} />
<meta name="twitter:title" content={`${title} | ${siteTitle}`} />
<meta name="twitter:description" content={description} />
{image && <meta name="twitter:image" content={new URL(image, canonicalURL).toString()} />}

<meta name="robots" content="max-image-preview:large" />

<!-- Fonts: self-hosted via @fontsource or Google Fonts link tag -->
<!-- Add font <link> or @import here -->
```

### `src/layouts/BaseLayout.astro`

```astro
---
import BaseHead from '../components/BaseHead.astro'
import Header from '../components/Header.astro'
import Footer from '../components/Footer.astro'
import '../styles/global.css'

interface Props {
  title: string
  description: string
  image?: string
}

const { title, description, image } = Astro.props
---

<!doctype html>
<html lang="en">
  <head>
    <BaseHead
      title={title}
      description={description}
      image={image}
      canonicalURL={Astro.url.href}
    />
  </head>
  <body>
    <Header />
    <main>
      <slot />
    </main>
    <Footer />
  </body>
</html>
```

### `src/components/Header.astro`

Lift the `<header>` HTML from the prototype's `index.html`. Replace hardcoded nav links with a nav array (or content collection if nav is dynamic):

```astro
---
const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/services', label: 'Services' },
  { href: '/contact', label: 'Contact' },
]
---

<header class="site-header">
  <div class="wide header-inner">
    <a href="/" class="site-logo">
      <img src="/logo.svg" alt="[Client Name]" width="160" height="48" />
    </a>
    <nav class="site-nav" aria-label="Primary navigation">
      {navLinks.map(({ href, label }) => (
        <a href={href} class={Astro.url.pathname === href ? 'active' : ''}>{label}</a>
      ))}
    </nav>
    <a href="#book" class="btn btn-primary header-cta">Book Online</a>
    <button class="mobile-menu-toggle" aria-expanded="false" aria-label="Toggle menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>

<style>
  /* Lifted from prototype header CSS */
</style>

<script>
  /* Converted from prototype JS — with TypeScript types */
  const toggle = document.querySelector<HTMLButtonElement>('.mobile-menu-toggle')
  const nav = document.querySelector<HTMLElement>('.site-nav')
  toggle?.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true'
    toggle.setAttribute('aria-expanded', String(!expanded))
    nav?.classList.toggle('is-open')
  })
</script>
```

### `src/components/Footer.astro`

Lift the `<footer>` HTML from the prototype. Pull business details from the verified client records:

```astro
---
const currentYear = new Date().getFullYear()
---

<footer class="site-footer">
  <div class="wide footer-inner">
    <div class="footer-brand">
      <img src="/logo.svg" alt="[Client Name]" width="120" height="36" />
    </div>
    <nav class="footer-nav" aria-label="Footer navigation">
      <!-- footer nav links -->
    </nav>
    <div class="footer-contact">
      <!-- phone, email from the verified client records -->
    </div>
    <p class="footer-legal">© {currentYear} [Client Name]. All rights reserved.</p>
  </div>
</footer>

<style>
  /* Lifted from prototype footer CSS */
</style>
```

## Step 5: Set Up Content Collections

Create `src/content/config.ts` with Zod schemas. Define schemas based on the content the prototype contains:

```ts
import { defineCollection, z } from 'astro:content'

const pages = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().max(160),
    draft: z.boolean().optional().default(false),
  }),
})

const services = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().max(160),
    shortDescription: z.string(),
    order: z.number().default(99),
    draft: z.boolean().optional().default(false),
  }),
})

const locations = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    suburb: z.string(),
    address: z.string(),
    phone: z.string(),
    bookingUrl: z.string().url(),
    mapEmbed: z.string().optional(),
    draft: z.boolean().optional().default(false),
  }),
})

export const collections = { pages, services, locations }
```

Add collections as needed for this project (blog, team, FAQs, etc.).

## Step 6: Extract Copy from Prototype into Content Files

Go through the approved prototype section by section. For each section with text content:

1. Identify all strings a client might want to update (headlines, body text, CTA labels, testimonial quotes, service descriptions, stats)
2. Extract them into frontmatter of the relevant content `.md` file
3. Longer copy (service descriptions, FAQ answers) can go in the `.md` body

**Create these files from the prototype content:**

- `src/content/pages/homepage.md` — hero headline, subheadline, CTA, trust bar stats, section headings, testimonials
- `src/content/services/<slug>.md` — one per service (from the services section or sitemap)
- `src/content/locations/<suburb-slug>.md` — one per location (from the locations section)

Pull address, phone and booking data from the client overview in the internal vault or other verified client records. If a detail is missing or unverified, ask the user; never invent it.

**Rule:** if a string appears once and is unlikely to change, it's fine in the component. If it appears in a prominent position or a client will want to update it, it goes in a `.md` file.

## Step 7: Convert Prototype Sections to Components

For each prototype section, create `src/components/sections/<SectionName>.astro`.

Work through them in order:
- `Hero.astro`
- `TrustBar.astro`
- `PainPoints.astro` (or similar)
- `Solution.astro`
- `Features.astro`
- `Testimonials.astro`
- `Process.astro`
- `FAQ.astro`
- `Locations.astro`
- `CTABanner.astro`

For each component:

1. **Template:** paste the section HTML from the prototype, replace hardcoded strings with props
2. **Props interface:** define TypeScript props for every value that comes from content
3. **CSS:** move the section's CSS block into a `<style>` block (Astro scopes it automatically)
4. **Interactive JS:** if the section has a `<script>` block, move it into a typed `<script>` block (see astro-build-standard.md Section 3.2 for TypeScript conversion pattern)

Example — FAQ component:

```astro
---
interface Props {
  heading: string
  items: Array<{ question: string; answer: string }>
}
const { heading, items } = Astro.props
---

<section class="faq-section">
  <div class="container">
    <h2 class="section-heading">{heading}</h2>
    <div class="faq-list">
      {items.map(({ question, answer }) => (
        <div class="faq-item">
          <button class="faq-question" aria-expanded="false">{question}</button>
          <div class="faq-answer"><p>{answer}</p></div>
        </div>
      ))}
    </div>
  </div>
</section>

<style>
  /* Lifted from prototype — scoped automatically */
  .faq-section { ... }
  .faq-question { ... }
  .faq-answer { display: none; }
</style>

<script>
  const buttons = document.querySelectorAll<HTMLButtonElement>('.faq-question')
  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true'
      btn.setAttribute('aria-expanded', String(!expanded))
      const answer = btn.nextElementSibling as HTMLElement | null
      if (answer) answer.style.display = expanded ? 'none' : 'block'
    })
  })
</script>
```

## Step 8: Build Pages

Create `src/pages/index.astro` (and one file per page in the sitemap):

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro'
import Hero from '../components/sections/Hero.astro'
import TrustBar from '../components/sections/TrustBar.astro'
import Features from '../components/sections/Features.astro'
import Testimonials from '../components/sections/Testimonials.astro'
import FAQ from '../components/sections/FAQ.astro'
import Locations from '../components/sections/Locations.astro'

import { getEntry } from 'astro:content'
const homepage = await getEntry('pages', 'homepage')
---

<BaseLayout
  title={homepage.data.title}
  description={homepage.data.description}
>
  <Hero
    title={homepage.data.heroTitle}
    subheadline={homepage.data.heroSubheadline}
    ctaText={homepage.data.ctaText}
    ctaHref={homepage.data.ctaHref}
  />
  <TrustBar ... />
  <Features ... />
  <Testimonials ... />
  <FAQ heading={homepage.data.faqHeading} items={homepage.data.faqItems} />
  <Locations ... />
</BaseLayout>
```

For service and location pages, use dynamic routes:

- `src/pages/services/[slug].astro` — `getStaticPaths()` from the services collection
- `src/pages/locations/[slug].astro` — `getStaticPaths()` from the locations collection

## Step 8b: Forms

If the answer to the form question in Step 0 was yes, stop here and run `astro-form` for this client. It asks whether the client has a GoHighLevel account, builds the Turnstile-protected Pages Function (GoHighLevel inbound webhook, or Cloudflare D1 if there is no GoHighLevel account), the thank-you pages and GA tracking. Return to Step 9 when it is done. If there is no form, skip this step.

## Step 9: JSON-LD for Local Business

Add a `LocalBusiness` JSON-LD block to `BaseLayout.astro`. Pull data from the verified client records:

```astro
---
const schema = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Client Name]",
  "description": "[From the verified client records]",
  "url": "[site URL]",
  "telephone": "[Phone]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street]",
    "addressLocality": "[Suburb]",
    "addressRegion": "[State]",
    "postalCode": "[Postcode]",
    "addressCountry": "AU"
  }
}
---

<script type="application/ld+json" set:html={JSON.stringify(schema)} />
```

For multi-location businesses: inject a per-location `LocalBusiness` block on each `locations/[slug].astro` page instead of site-wide.

## Step 10: Sitemap and robots.txt

**Sitemap:** `@astrojs/sitemap` was installed in Step 1. Verify it generates on build:

```bash
npm run build
ls dist/sitemap*.xml
```

If `sitemap-index.xml` is missing: check that `site:` is set in `astro.config.mjs` and the integration is listed in `integrations`.

**`public/robots.txt` — create now as staging version:**

```
User-agent: *
Disallow: /

Sitemap: https://[clientdomain].com.au/sitemap-index.xml
```

This blocks all crawlers during build and staging. The production version (replacing `Disallow: /` with `Disallow:`) is committed as part of the go-live checklist. Add a prominent comment in the file:

```
# STAGING — blocks all crawlers
# Switch to production robots before DNS cutover (remove Disallow line)
```

## Step 11: Run Build and TypeScript Check

```bash
npx astro check    # TypeScript and template errors
npm run build      # full static build
```

Fix any errors before proceeding. Common ones:
- Missing required props in components — add them or make them optional in the interface
- Type errors in `<script>` blocks — add missing DOM types
- Content schema validation failures — fix the frontmatter in the relevant `.md` file
- Missing `site:` in config — sitemap integration will warn

## Step 12: Deployment Config

**Cloudflare Pages (default — static output, no adapter):**

Create `public/_headers` to set security headers:

```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Create `public/_redirects` for any URL redirects (old site URLs → new slugs):

```
# /old-path  /new-path  301
```

**Deploying to Cloudflare Pages:**

1. Make sure the work is committed and pushed to `main` of the client repo (`git push origin main`). During staging, all deploys come from pushing `main`. There are no review branches.
2. In the Cloudflare Pages dashboard: Connect to Git, then select the client repo.
3. Build settings:
   - Root directory: `site`
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Deploy command: empty / not used
   - Node version: match local (set via environment variable `NODE_VERSION`)
4. Deploy and verify the `*.pages.dev` staging URL loads correctly. The `functions/` folder for `astro-form` lives in `site/functions/` so Pages picks it up with the same root directory.

> **Deployment warnings:**
> - Do NOT add `npx wrangler deploy`, `npx wrangler pages deploy`, `true`, or `echo ok` as a deploy command in Cloudflare for Git-connected projects. Use the Pages Git integration build command + output directory only. Mixing both deploy paths causes conflicts.
> - If Cloudflare requires a deploy command, you are probably in the wrong product/project flow (Worker/direct upload or a similarly named app), not the normal Git-connected Pages build settings.
> - `Authentication error [code: 10000]` from Wrangler is not always a credentials problem. It can also mean wrong project type (Worker vs Pages), wrong project name, or wrong deployment model. Check project type before regenerating tokens.
> - A Pages Function that matches a path can override `public/_redirects` for that path. Test redirects on the deployed URL.

**Production deploy needs explicit approval.** Attaching the real domain, flipping `robots.txt` to the production version, and any push that makes the real domain serve the new site are production deploys. Stop and ask the user for explicit approval first. Staging pushes to `main` that only update the `*.pages.dev` URL do not need it. After an approved production deploy, verify the pushed commit SHA on the remote and the Cloudflare deployment URL before reporting it live.

## Step 13: Visual QA

Compare the Astro build against the approved prototype at `lhm-prototype/<client>/`.

Use browser automation (Playwright MCP) if it is available, or check manually at:
- Desktop (1440px)
- Tablet (768px)
- Mobile (390px)

For each page and breakpoint, verify:
- Typography, colours, and spacing match the prototype
- All sections present and in the correct order
- Interactive elements work (FAQ accordion, mobile menu, any sliders)
- Images load and aren't shifted (no CLS)
- No console errors

Record screenshots and any differences. Do not mark the build ready until differences are fixed or accepted by the user.

## Step 14: Commit and Push

```bash
git add site
git commit -m "feat(site): Astro project scaffold and prototype conversion"
git push origin main
```

Tell the user:

> "Astro build is on the staging URL (`*.pages.dev`). Sitemap at `/sitemap-index.xml`; robots.txt is in staging mode and blocks all crawlers.
>
> Next steps:
> 1. Run `site-launch-qa` for the full pre-launch QA
> 2. Flip `robots.txt` to the production version only as part of the approved production deploy
> 3. Submit the sitemap in Google Search Console after go-live"

## Project state

Update the client's internal project file (`20 Clients/<client>/project-management/` in the LHM Knowledge vault, per `${CLAUDE_PLUGIN_ROOT}/references/obsidian-context-contract.md`) at these points: build started, form decision recorded, staging URL and commit SHA, QA results link, and production approval when given. Do not store secrets or form credentials there.
