# Astro Pre-Launch Checklist — Full Reference

Full item list for Astro static/SSR sites deployed to Vercel or Netlify. Used by the site-launch-qa skill for Astro platform projects.

---

## Content Integration

| Item | How to Check |
|------|-------------|
| Text checked (spelling, grammar, formatting) | Human review of all pages. Use Grammarly or similar. |
| Page titles and meta descriptions unique and descriptive | Inspect `<title>` and `<meta name="description">` on each page via browser DevTools |
| Images have appropriate alt text | Inspect `<img>` tags — each should have a non-empty `alt` attribute |
| Navigation easy to find, all links working | Click every nav and footer link manually |
| 404 page created and serving correctly | Visit `/this-page-does-not-exist` — should show custom `404.astro` page |
| Footer copyright notice included and year correct | Check footer component across page templates |
| Thank You pages working | Submit each form and confirm redirect to the correct thank you route |

---

## Build & Deployment

| Item | How to Check |
|------|-------------|
| Build runs without errors | Check Vercel/Netlify deploy log — no red errors, all pages generated |
| Build runs without warnings | Review build output for deprecation or config warnings |
| All environment variables set in production | Vercel/Netlify → Environment Variables — confirm all required vars present for production |
| No secrets committed to the repo | `git log --all --full-diff -S "SECRET_KEY"` — confirm no env values in history |
| Deployment pipeline working (push → auto-deploy) | Push a trivial change and confirm Vercel/Netlify picks it up automatically |
| Preview deployments working (PRs) | Open a test PR — confirm a preview URL is generated |
| Production domain linked to deployment | Vercel/Netlify → Domains — confirm custom domain is set and SSL is active |

---

## Performance

| Item | How to Check |
|------|-------------|
| PageSpeed Insights score adequate | https://pagespeed.web.dev/ — target Mobile ≥ 60, Desktop ≥ 85 (Astro sites typically score higher) |
| Mobile Friendly Test | https://search.google.com/test/mobile-friendly |
| Images using Astro `<Image>` component | Check source — images should use `import` + `<Image>` or `getImage()`, not raw `<img src>` |
| No unintended large JS bundles | Vercel/Netlify build output shows bundle sizes. Check for any >200KB chunks |
| Fonts loading correctly (no layout shift) | Check CLS score in PageSpeed. Font-display: swap should be set |
| Caching headers set via platform config | Check `vercel.json` or `netlify.toml` for cache-control headers on `/_astro/*` assets |

---

## Routing & Redirects

| Item | How to Check |
|------|-------------|
| Redirects configured in `vercel.json` or `netlify.toml` | Open the config file — confirm all old URLs have redirect rules |
| Old URLs redirect correctly (301) | Test old/legacy URLs in browser — confirm 301 redirects fire |
| Clean URLs in place (no `.html` extensions) | Astro generates clean URLs by default with `trailingSlash` config |
| All URL variants redirect to canonical | Test http://, www., and non-www — all should land at the canonical https://non-www version |
| Dynamic routes working correctly | Test any `[slug].astro` pages with real and invalid slugs |

---

## Sitemap & Robots

| Item | How to Check |
|------|-------------|
| Sitemap generated and accessible | Visit `/sitemap.xml` or `/sitemap-index.xml` — confirm it contains all pages |
| Sitemap submitted to Google Search Console | GSC → Sitemaps → confirm submitted |
| robots.txt present and correct | Visit `/robots.txt` — should exist and not block all crawlers |
| Search engine crawling enabled | robots.txt should not contain `Disallow: /` for Googlebot |

---

## Analytics & Tracking

| Item | How to Check |
|------|-------------|
| GA4 installed and recording sessions | GA4 Real-Time report — visit the site and confirm active user shows up |
| GA4 installed via Partytown or native script | Check page source — confirm gtag script is present and loading |
| Event tracking set up for key conversions | Trigger contact form submit, phone click, booking — confirm events in GA4 |
| Google Search Console verified | GSC → confirm site is verified (DNS or meta tag method) |
| GTM connected (if applicable) | GTM Preview mode → visit site → confirm container tags fire |

---

## Accessibility

| Item | How to Check |
|------|-------------|
| Links have clear focus state | Tab through the page — links should have a visible focus ring |
| All form fields have labels | Inspect form HTML — each `<input>` should have a paired `<label>` |
| ARIA roles used appropriately | Use browser accessibility tree (DevTools → Accessibility) |
| Colour contrast passes WCAG AA | WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/ |
| Site usable with screen reader | VoiceOver (Mac/iOS) or NVDA (Windows) — navigate home page |

---

## Compatibility

| Item | How to Check |
|------|-------------|
| Chrome | Open site in Chrome — test navigation, forms, scroll |
| Firefox | Open site in Firefox |
| Safari | Open site in Safari — especially important for CSS grid/custom properties |
| Edge | Open site in Edge |
| iOS real device | Open in Safari on iPhone — check layout, tap targets, forms |
| Android real device | Open in Chrome on Android |
| Favicon present | Check browser tab. Add touch icon meta tag for iOS home screen |

---

## Infrastructure & Security

| Item | How to Check |
|------|-------------|
| SSL active and auto-renewing | Vercel/Netlify → Domains → SSL status |
| Custom domain correctly configured | DNS A/CNAME records pointing to Vercel/Netlify |
| Source map files not publicly served | Check that `.map` files are excluded from production build if sensitive |
| API routes protected (if using SSR) | Test any API endpoints — confirm auth is required where appropriate |
| Content Security Policy headers set (optional but recommended) | Check response headers via DevTools → Network → any page → Headers |

---

## Astro-Specific Configuration

| Item | How to Check |
|------|-------------|
| Output mode correct (`static` or `server`) | Check `astro.config.mjs` → `output:` field matches intended deployment |
| Adapter installed and configured | For SSR: Vercel or Netlify adapter should be in `astro.config.mjs` |
| `trailingSlash` config matches hosting | Set to `'always'` or `'never'` consistently and matches redirect rules |
| `base` path set correctly (if subdirectory deploy) | If deploying to `/blog/`, `base: '/blog'` must be set in config |
| Hydration directives correct | Interactive components use `client:load`, `client:visible`, or `client:idle` as appropriate |
| No hydration errors in console | Load each page with JS components — DevTools Console should be clean |
| Image optimisation working | Check built pages — images should have `srcset`, `width`, `height`, and `loading="lazy"` |
