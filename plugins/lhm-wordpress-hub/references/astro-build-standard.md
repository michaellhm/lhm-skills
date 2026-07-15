# Astro Build Standard — LHM

**Version:** 1.0 · **Last updated:** June 2026  
**Applies to:** all Astro website builds in the LHM WordPress/Astro Hub

This is the working reference for how LHM Astro projects are structured, how prototypes get converted to production components, and what SEO and build hygiene look like on Astro. The `astro-build` skill follows this document. If the skill and this doc ever disagree, the doc wins.

---

## 1. Project conventions

### 1.1 Folder structure

```
<client>-site/
  public/
    robots.txt                  ← static file, ships as-is
    favicon.svg
  src/
    assets/                     ← hero images, post images — go through image pipeline
    components/
      ui/                       ← Button.astro, Card.astro, Badge.astro
      sections/                 ← Hero.astro, TrustBar.astro, Testimonials.astro, FAQ.astro
    content/
      pages/                    ← homepage.md, about.md, service-physio.md ...
      services/                 ← one .md per service
      locations/                ← one .md per location
      blog/                     ← one .md per post (if applicable)
    layouts/
      BaseLayout.astro           ← wraps every page, imports Header + Footer
      PageLayout.astro           ← extends BaseLayout with common page sections
    pages/
      index.astro
      about.astro
      services/
        [slug].astro             ← dynamic route from services collection
      locations/
        [slug].astro
      blog/
        index.astro
        [slug].astro
    styles/
      global.css                 ← design token CSS variables only
  astro.config.mjs
  tsconfig.json
  wrangler.toml                  ← Cloudflare Pages config (if applicable)
  .gitignore
  README.md
```

### 1.2 TypeScript

TypeScript is enabled by default on all LHM Astro builds. When creating a new project use the "strict" TypeScript template. When converting prototype JS (accordion, menu, animations) to Astro component `<script>` blocks, add types in the same pass — don't leave it for later.

Minimal types needed in most interactive prototype components:
- Event handler params: `(e: MouseEvent)`, `(e: Event)`
- DOM queries: `document.querySelector<HTMLElement>('...')`
- Button/element references: `const btn = document.querySelector<HTMLButtonElement>('.faq-question')`

Frontmatter and content collection schemas use Zod (built into Astro) — no separate TypeScript types needed for content.

### 1.3 CSS approach

**Scoped component `<style>` blocks + a single `src/styles/global.css` for design tokens.**

Because LHM builds prototype-first, the CSS already exists with well-named class names (`.hero-section`, `.card-grid`, etc.) and CSS custom properties from the design system. The conversion approach is:

1. Copy the design token variables (`--color-primary`, `--font-heading`, etc.) from the prototype `<style>` block into `src/styles/global.css`. Import this in `BaseLayout.astro`.
2. For each prototype section converted to an `.astro` component, move its CSS into a scoped `<style>` block inside that component.
3. Utility classes (`.container`, `.section`, `.btn`) go in `global.css` since they're shared across components.

Do not use Tailwind on prototype-conversion projects — it would require rewriting all existing CSS as utility classes with no benefit. Tailwind is valid for greenfield Astro projects where no prototype exists.

### 1.4 Layout components — BaseLayout, Header, Footer

Every page renders through `BaseLayout.astro`. This is the single source of truth for the HTML shell, meta tags, and shared UI.

**`src/layouts/BaseLayout.astro`**

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
  canonicalURL?: string
}

const { title, description, image, canonicalURL } = Astro.props
---

<!doctype html>
<html lang="en">
  <head>
    <BaseHead
      title={title}
      description={description}
      image={image}
      canonicalURL={canonicalURL ?? Astro.url.href}
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

**`src/components/Header.astro`** — a single file. Every page gets the same header. Update once, updates everywhere. Pull nav links from a static array or a content collection; do not hard-code them across multiple pages.

**`src/components/Footer.astro`** — same principle. Clinic details, social links, legal copy live here. One change propagates everywhere.

**`src/components/BaseHead.astro`** — owns all `<head>` content: title, description, Open Graph tags, Twitter Card, canonical URL, font preloads, sitemap link. Receives props from BaseLayout. Never scatter `<head>` tags across individual pages.

### 1.5 Content in Markdown files

When converting from the HTML prototype to Astro, extract all copy into content collection `.md` files. Components receive content as typed props.

**Why:** Content editors (including clients) can update copy without touching Astro components. Frontmatter schemas catch missing or malformed fields at build time, not in production.

**Extraction rule:** if it's a string a client might want to change — headline, subheadline, CTA text, service description, testimonial quote, team bio — it goes in a `.md` file, not hardcoded in a component.

**Conversion pattern:**

Prototype HTML:
```html
<section class="hero-section">
  <h1>Physio That Gets You Back to Life</h1>
  <p>Evidence-based care in the Inner West. Same-week appointments available.</p>
  <a href="#book" class="btn btn-primary">Book Online</a>
</section>
```

Becomes `src/content/pages/homepage.md`:
```markdown
---
title: "Physio That Gets You Back to Life"
description: "Evidence-based care in the Inner West. Same-week appointments available."
ctaText: "Book Online"
ctaHref: "#book"
---
```

And `src/components/sections/Hero.astro`:
```astro
---
interface Props {
  title: string
  description: string
  ctaText: string
  ctaHref: string
}
const { title, description, ctaText, ctaHref } = Astro.props
---

<section class="hero-section">
  <h1>{title}</h1>
  <p>{description}</p>
  <a href={ctaHref} class="btn btn-primary">{ctaText}</a>
</section>

<style>
  /* lifted from prototype */
  .hero-section { ... }
</style>
```

---

## 2. Project setup

### 2.1 Scaffold

```bash
cd ~/Documents/Projects/<client>/<client>-site
npm create astro@latest . -- --template minimal --typescript strict --no-install
npm install
```

The `.` installs into the current directory (the existing repo, which already has `docs/` and `skills/`). This is intentional — the Astro project lives inside the `<client>-site` repo.

### 2.2 Core integrations — install on every build

```bash
npx astro add sitemap
```

Image optimization is built into Astro v3+ — no separate integration needed. Use the `<Image>` component from `astro:assets`.

### 2.3 Deployment adapters

| Target | When | Command |
|--------|------|---------|
| Cloudflare Pages (static) | Default — no SSR needed | No adapter. Deploy `dist/` directly. |
| Cloudflare Pages (SSR) | Server-side features needed | `npx astro add cloudflare` |
| Vercel (static) | Client uses Vercel | No adapter. Deploy `dist/` directly. |
| Vercel (SSR) | Server-side features needed | `npx astro add vercel` |

For local health business sites (no logged-in users, no dynamic data), **static output with no adapter is the default**. Only add an adapter if you have a confirmed SSR requirement.

**Cloudflare Pages Git-connected settings:** use the Pages product with the GitHub repo connected directly, production branch `main`, build command `npm run build`, output directory `dist`, root directory empty unless the Astro app is in a subfolder, and no deploy command. Do not use `npx wrangler deploy` or `npx wrangler pages deploy` inside Cloudflare for Git-connected Pages. If the UI requires a deploy command, verify you are not in a Worker/direct-upload style project or similarly named app.

### 2.4 `astro.config.mjs` baseline

```js
import { defineConfig } from 'astro/config'
import sitemap from '@astrojs/sitemap'

export default defineConfig({
  site: 'https://clientdomain.com.au',   // replace per client — required for sitemap
  trailingSlash: 'never',                // consistent URL form
  output: 'static',                      // default; change to 'server' if SSR needed
  integrations: [
    sitemap(),
  ],
  image: {
    domains: [],                         // add remote image domains if needed
  },
})
```

Update `site:` before first deploy. Sitemap generation and canonical URLs both depend on it.

### 2.5 `tsconfig.json`

Use Astro's recommended strict config:

```json
{
  "extends": "astro/tsconfigs/strict"
}
```

---

## 3. Converting from HTML prototype

This is the Phase 5 workflow for Astro builds. The HTML prototype (from `html-prototype` or `lp-prototype` skill) is the approved design source of truth.

### 3.1 Conversion order

1. **Set up the global styles** — extract design token variables from the prototype `<style>` block into `src/styles/global.css`. Extract utility classes (`.container`, `.section`, `.btn`, `.btn-primary`).
2. **Build BaseLayout, Header, Footer** — lift the `<header>` and `<footer>` HTML from the prototype into component files. Move their CSS into scoped `<style>` blocks.
3. **Convert sections one at a time** — for each prototype section (Hero, TrustBar, Features, Testimonials, FAQ, etc.):
   a. Extract copy to a content collection `.md` file
   b. Create a `src/components/sections/<SectionName>.astro` file
   c. Paste the section HTML as the template, replacing hardcoded strings with props
   d. Move section CSS into a `<style>` block
   e. Convert any `<script>` JS to TypeScript (see 3.2)
4. **Build pages** — create `src/pages/index.astro` (and other pages), import section components, pass content from collections as props.
5. **Wire up SEO** — BaseHead props, JSON-LD, canonical URLs.
6. **Generate sitemap and robots** — verified on `astro build`.

### 3.2 Converting prototype JS to TypeScript

Prototype interactive JS (FAQ accordion, mobile menu, scroll animations) lives in a `<script>` block at the bottom of the HTML file. In Astro, move it into a `<script>` tag inside the relevant `.astro` component (not a global script). Astro bundles, hashes, and deduplicates these automatically.

Conversion pattern (FAQ accordion example):

**Prototype JS:**
```js
document.querySelectorAll('.faq-question').forEach(btn => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true'
    btn.setAttribute('aria-expanded', !expanded)
    btn.nextElementSibling.style.display = expanded ? 'none' : 'block'
  })
})
```

**Astro component `<script>` block (TypeScript):**
```ts
const buttons = document.querySelectorAll<HTMLButtonElement>('.faq-question')
buttons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true'
    btn.setAttribute('aria-expanded', String(!expanded))
    const answer = btn.nextElementSibling as HTMLElement | null
    if (answer) answer.style.display = expanded ? 'none' : 'block'
  })
})
```

For mobile menu and scroll animation JS, same pattern: add DOM query types, add event handler types, cast `nextElementSibling` and `querySelector` results explicitly.

### 3.3 Content collection schemas

Define a Zod schema for every collection so bad frontmatter fails at build time, not in production.

```ts
// src/content/config.ts
import { defineCollection, z } from 'astro:content'

const pages = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().max(160),
    ctaText: z.string().optional(),
    ctaHref: z.string().optional(),
    draft: z.boolean().optional().default(false),
  }),
})

const services = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().max(160),
    hero: z.string(),
    order: z.number(),
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

---

## 4. Sitemap and robots.txt

### 4.1 Sitemap

`@astrojs/sitemap` generates `sitemap-index.xml` automatically on every `astro build`. It reads from the `site:` URL in `astro.config.mjs` — this must be set to the production domain before the first deploy.

Pages with `draft: true` filtered out of the collection are not routed, so they don't appear in the sitemap. No manual exclusion needed for draft content.

Verify the sitemap exists after build:
```bash
ls dist/sitemap*.xml
```

Submit to Google Search Console after go-live. Point the GSC sitemap URL to `https://clientdomain.com.au/sitemap-index.xml`.

### 4.2 robots.txt

Create `public/robots.txt`. This ships verbatim — it belongs in `public/` because it must not be processed or hashed by Astro's pipeline.

**Staging / pre-launch:**
```
User-agent: *
Disallow: /

Sitemap: https://clientdomain.com.au/sitemap-index.xml
```

**Production (go-live):**
```
User-agent: *
Disallow:

Sitemap: https://clientdomain.com.au/sitemap-index.xml
```

Switch from staging to production robots before DNS cutover. Committing the staging version and forgetting to flip it before go-live is a common SEO mistake — add it to the go-live checklist.

---

## 5. SEO layer

Astro outputs clean HTML but ships nothing for meta tags, JSON-LD, or canonical URLs. This must be wired up once in `BaseHead.astro` and then applied per page.

### 5.1 BaseHead component

```astro
---
interface Props {
  title: string
  description: string
  image?: string
  canonicalURL: string
}

const { title, description, image, canonicalURL } = Astro.props
const siteTitle = 'Client Name'
---

<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width" />
<title>{title} | {siteTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalURL} />

<!-- Open Graph -->
<meta property="og:type" content="website" />
<meta property="og:url" content={canonicalURL} />
<meta property="og:title" content={`${title} | ${siteTitle}`} />
<meta property="og:description" content={description} />
{image && <meta property="og:image" content={image} />}

<!-- Twitter Card -->
<meta property="twitter:card" content="summary_large_image" />
<meta property="twitter:url" content={canonicalURL} />
<meta property="twitter:title" content={`${title} | ${siteTitle}`} />
<meta property="twitter:description" content={description} />
{image && <meta property="twitter:image" content={image} />}

<!-- Robots -->
<meta name="robots" content="max-image-preview:large" />

<!-- Sitemap -->
<link rel="sitemap" href="/sitemap-index.xml" />
```

Pass `title` and `description` from each page's frontmatter. Pass `canonicalURL={Astro.url.href}` from the layout.

### 5.2 JSON-LD for local businesses

Inject a `LocalBusiness` schema block in `BaseLayout.astro` (or in a dedicated JSON-LD component) using data from the client's `docs/client-overview.md`:

```astro
---
const schema = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Client Name",
  "description": "...",
  "url": "https://clientdomain.com.au",
  "telephone": "+61 X XXXX XXXX",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "...",
    "addressLocality": "...",
    "addressRegion": "NSW",
    "postalCode": "...",
    "addressCountry": "AU"
  }
}
---

<script type="application/ld+json" set:html={JSON.stringify(schema)} />
```

For multi-location businesses, generate one `LocalBusiness` block per location and inject it on the relevant location page, not site-wide.

### 5.3 Per-page SEO

- Title tags: unique per page, front-load the meaningful word (service or location name first)
- Meta descriptions: 120–155 characters, written for humans reading search results, not stuffed with keywords
- Canonical: always set via `canonicalURL={Astro.url.href}` — never let it default to something ambiguous

---

## 6. Common build issues (reference)

### Hydration and JavaScript

1. **Overusing `client:load`.** Hydrating everything immediately throws away the main reason to use Astro. Most interactive components can wait — `client:idle` or `client:visible` for below-the-fold content.
2. **Adding `client:*` when no JS is needed.** Cards, CSS-controlled accordions, and static layouts often get a directive out of habit. If a component doesn't need browser state, it ships as static HTML.
3. **Treating `.astro` components like React.** Frontmatter runs at build/request time, not in the browser. No `useState`-style reactivity in frontmatter.
4. **Hydration mismatches.** Non-deterministic rendering (dates, `Math.random`, locale) differing between server and client breaks interactive components silently.
5. **Third-party packages using browser APIs during SSR.** A dependency that touches `window` or `document` at import time crashes the build. Fix with `client:only`, a dynamic `import()`, or a package that supports SSR.

### Rendering and config

6. **Forgetting `export const prerender = true` in server mode.** With `output: 'server'`, every page re-renders on each request unless explicitly prerendered.
7. **Node version mismatches.** Wrong Node silently fails on newer Astro entrypoints. Check the Astro release notes for supported Node versions.
8. **Adapter and integration version drift.** Avoid beta adapters on production builds.
9. **Local builds passing but deploys failing.** Check Node version parity, reinstall dependencies, clear build cache.
10. **Bloated config with too many integrations.** Start minimal, add one at a time.

### Images

11. **Putting hero/content images in `public/`.** Only files in `src/assets/` go through the optimization pipeline. `public/` ships byte-for-byte.
12. **Missing `width` and `height`.** Leads to Cumulative Layout Shift — hurts both UX and Core Web Vitals.
13. **Lazy-loading the LCP image.** Never. Preload the hero with `fetchpriority="high"`, no `loading="lazy"`.
14. **Sharp not installed.** Image optimization fails quietly. Verify Sharp is installed (`npm install sharp`).

### Content

15. **Skipping content collection schemas.** Without Zod, frontmatter typos ship to production. Schemas catch them at build time.
16. **Misusing live collections.** Live collections fetch at runtime on each request. Don't use them for stable content.

### Assets

17. **Manually inlining large CSS/JS blocks.** Past ~4KB you lose cacheability and slow first paint. Astro inlines small critical CSS automatically — let it.
18. **Dropping CSS/JS in `public/` and hand-linking.** This opts out of bundling, minification, and content hashing. Keep assets inside Astro's pipeline.

---

## 7. Best practice checklist

### Hydration
- Assume every component ships as plain HTML. Prove browser interaction is needed before adding a client directive.
- `client:load` — interactive immediately (nav menu)
- `client:idle` — can wait (toggles, below-fold accordions)
- `client:visible` — below the fold
- `client:only` — browser-only libraries, no SSR

### Build and config
- Pin Node version. Use `.nvmrc` or `engines` in `package.json`.
- Set `prerender` deliberately in server mode.
- Run `astro build` locally before every deploy. Confirm environment parity.
- Keep config minimal. Add integrations one at a time and build-test between each.

### Images
- `src/assets/` for hero and content images — use `<Image>` for optimization.
- Always set `width` and `height`.
- Descriptive `alt` text under ~125 characters. `alt=""` for decorative images; missing `alt` is a bug.
- Preload the LCP image: `<link rel="preload" as="image" href="..." fetchpriority="high" />`

### Content
- Zod schema for every collection.
- Filter drafts in production: `import.meta.env.PROD && entry.data.draft`.
- Define taxonomy and pagination deliberately.

### Assets
- Component `<style>` blocks for scoped CSS.
- `import './styles.css'` in frontmatter for shared CSS.
- Plain `<script>` in `.astro` files — Astro bundles and hashes these. Use `is:inline` only for tiny must-run-before-paint scripts.
- Self-host fonts. Use `@fontsource` packages or download and serve from `public/fonts/`. Preload primary text weights.

### Quality assurance
- Validate internal links post-build (e.g. with `muffet` or a custom script against `dist/`).
- TypeScript errors at build time, not in production — run `astro check` in CI.
- Verify `sitemap-index.xml` exists in `dist/` after every build.
- Flip `robots.txt` from staging to production before DNS cutover.

---

## 8. Worth adding to most builds

- **Accessibility.** Semantic HTML, descriptive `alt`, visible focus states, sufficient colour contrast, keyboard-navigable interactive components.
- **Security headers.** Set CSP, `X-Content-Type-Options`, `Referrer-Policy`, HSTS at the host level (Cloudflare Pages or Vercel config). A strict CSP without `unsafe-inline` is one of the better XSS protections — another reason to keep scripts in Astro's pipeline.
- **Redirects.** Configure in `astro.config.mjs` (`redirects`) or at the host, not client-side JS, so old URLs keep their link equity.
- **Custom 404.** `src/pages/404.astro`. The Cloudflare/Vercel default is bare.
- **View Transitions.** `<ClientRouter />` gives SPA-like navigation with minimal JS. Test against hydrated islands to avoid state-loss issues.
- **RSS.** `@astrojs/rss` for content sites — cheap to add, useful for syndication and some AI ingestion pipelines.
- **`llms.txt`.** Consider adding to `public/` to expose your content structure to AI agents.
