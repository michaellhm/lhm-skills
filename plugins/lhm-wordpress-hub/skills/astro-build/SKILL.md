---
name: astro-build
description: "Build an Astro website from the approved HTML prototype. Use this when the user says 'build the Astro site', 'convert the prototype to Astro', 'astro build', 'scaffold the Astro project', 'convert to Astro', 'build out the Astro pages', or 'start Phase 5 for an Astro build'. This is the Phase 5 equivalent for projects where platform is Astro. Requires an approved HTML prototype (html-prototype skill) and a design system. Converts prototype sections to .astro components, extracts copy to content collections, wires up SEO, sitemap, and robots.txt, and configures for deployment."
---

# Astro Build

Phase 5 for Astro platform builds. Converts the approved HTML prototype into a production Astro project — structured components, typed content collections, SEO layer, sitemap, and deployment config.

**Platform check:** only run this skill when `platform: astro` is recorded in `client_profile.md`. For WordPress builds, use `theme-scaffold` + `wp-page-builder` instead.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/astro-build/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/astro-build-standard.md` — this is the source of truth for all conventions
3. Read `client_profile.md` — for business name, locations, contacts, brand colours
4. Read `design/design_system.md` — for colour tokens, typography, spacing, breakpoints
5. Confirm the HTML prototype exists and is approved:
   - Full website prototype: `design/prototype/<slug>/` (from `html-prototype` skill)
   - LP prototype: `lp/prototype/<slug>/` (from `lp-prototype` skill)
6. Confirm the client's `<client>-site` repo is cloned at `~/Documents/Projects/<client>/<client>-site/`

If the prototype is not approved or the repo isn't cloned, stop and tell the user what's needed.

## Step 1: Scaffold the Astro Project

Run from inside the `<client>-site` repo directory:

```bash
npm create astro@latest . -- --template minimal --typescript strict --no-install
npm install
npx astro add sitemap
```

The `.` installs into the existing repo (which already has `docs/`, `skills/`, `README.md`). Confirm the scaffold didn't overwrite any of those files — if it did, restore from git.

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

Ask the user for the production domain if it's not in `client_profile.md`. Note: if the domain isn't confirmed yet, use a placeholder but flag it prominently in the Notes & Decisions section of the PM doc — sitemap and canonical URLs won't be correct until this is set.

## Step 3: Create Global Styles

Create `src/styles/global.css`. Extract design token CSS variables from the prototype `<style>` block and from `design/design_system.md`:

```css
/* ============================================
   Design Tokens — [Client Name]
   Source: design/design_system.md
   ============================================ */
:root {
  /* Colours */
  --color-primary: [HEX from design system];
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

Create this component to own all `<head>` content. Populate from `client_profile.md` (business name, site URL):

```astro
---
interface Props {
  title: string
  description: string
  image?: string
  canonicalURL: string
}

const { title, description, image, canonicalURL } = Astro.props
const siteTitle = '[Client Business Name]'  // from client_profile.md
---

<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} | {siteTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalURL} />
<link rel="sitemap" href="/sitemap-index.xml" />

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

Lift the `<header>` HTML from the prototype. Replace hardcoded nav links with a nav array (or content collection if nav is dynamic):

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

Lift the `<footer>` HTML from the prototype. Pull business details from `client_profile.md`:

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
      <!-- phone, email from client_profile.md -->
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

Pull address/phone/booking data from `client_profile.md`, not the prototype (the prototype may have placeholder data).

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

## Step 9: JSON-LD for Local Business

Add a `LocalBusiness` JSON-LD block to `BaseLayout.astro`. Pull data from `client_profile.md`:

```astro
---
const schema = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Client Name]",
  "description": "[From client_profile.md]",
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

1. Push the repo to GitHub (`git push`)
2. In Cloudflare Pages dashboard: Connect to Git → select the `<client>-site` repo
3. Build settings:
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Node version: match local (set via environment variable `NODE_VERSION`)
4. Deploy and verify the preview URL loads correctly

> **Deployment warnings:**
> - Do NOT add `npx wrangler pages deploy` as a deploy command in Cloudflare for Git-connected projects. Use the framework build command + output directory only. Mixing both deploy paths causes conflicts.
> - `Authentication error [code: 10000]` from Wrangler is not always a credentials problem. It can also mean wrong project type (Worker vs Pages), wrong project name, or wrong deployment model. Check project type before regenerating tokens.

**Vercel (if applicable):**

No adapter needed for static output. Connect repo in Vercel dashboard, set build command `npm run build`, output `dist`. Framework preset: "Astro".

## Step 13: Visual QA

Compare the Astro build against the approved HTML prototype.

Run the `visual-qa` skill if Playwright is available, or check manually at:
- Desktop (1440px)
- Tablet (768px)
- Mobile (390px)

For each page and breakpoint, verify:
- Typography, colours, and spacing match the prototype
- All sections present and in the correct order
- Interactive elements work (FAQ accordion, mobile menu, any sliders)
- Images load and aren't shifted (no CLS)
- No console errors

## Step 14: Commit and Push

```bash
git add .
git commit -m "feat: Astro project scaffold and prototype conversion"
git push
```

Tell the user:

> "Astro build complete. The project is live on Cloudflare Pages (or Vercel). Sitemap at `/sitemap-index.xml`, robots.txt is in staging mode — flip it to production before DNS cutover.
>
> Next steps:
> 1. Submit sitemap in Google Search Console after go-live
> 2. Flip `robots.txt` before DNS cutover
> 3. Run the `visual-qa` skill for a full pixel comparison

## Astro-Specific PM Notes

When running this skill for a full website build, mark Phase 5 tasks in the PM doc. The equivalent steps are:

| WordPress step | Astro equivalent |
|---|---|
| Local WP instance | Astro dev server — `npm run dev` |
| Theme scaffold | Steps 1–4 (scaffold, global styles, layout) |
| Raw HTML push | Step 6–7 (content extraction, components) |
| Gutenberg conversion | Not applicable — Astro is the source |
| Visual QA | Step 13 |
| Deploy to staging | Step 12 |

> **Note:** WordPress-specific Phase 5 tasks (theme-scaffold, wp-page-builder, CSS sync check, wp-ssh-deploy) do not apply to Astro builds. Skip them in the PM doc.
