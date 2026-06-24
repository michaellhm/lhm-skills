# WordPress Pre-Launch Checklist — Full Reference

Full item list with instructions for each check. Used by the site-launch-qa skill when running manual prompts or when the user asks for detail on a specific item.

---

## Content Integration

| Item | How to Check |
|------|-------------|
| Text checked (spelling, grammar, formatting) | Human review of all pages. Use Grammarly or similar. |
| Page titles and meta descriptions unique and descriptive | Rank Math / Yoast → check each page has a custom title and description |
| Images have appropriate alt text | WP Media Library → filter by "no alt text" OR use Rank Math bulk check |
| Navigation easy to find, all links working | Click every nav and footer link manually |
| 404 page created and serving correctly | Visit `/this-page-does-not-exist` — should show custom 404 |
| Footer copyright notice included and year correct | Check footer on every page template |
| AdWords landing pages checked and imported | Check with the Ads manager — confirm all LP URLs are live |
| Other marketing campaign landing pages imported | Confirm with client which pages are needed |
| AdWords manager notified of new pages and redirections | Email or Slack the Ads manager |
| Author pages updated to client's name | WP Admin → Users → edit user → update display name and bio |
| Thank You pages working and connected on all forms | Submit each form and confirm redirect to Thank You page |

---

## Design Utilities (WordPress / Elementor)

| Item | How to Check |
|------|-------------|
| Global Style Settings updated | Elementor → Hamburger Menu → Site Settings → check fonts, colours match brand |
| Unused Global Style Settings removed | Elementor → Hamburger Menu → Site Settings → remove unused presets |
| Unused pages removed | WP Admin → Pages → check for demo/placeholder pages |
| Unused templates removed | Elementor → Templates → Saved Templates → delete unused |
| Contact forms renamed | WP Admin → WPForms / CF7 → confirm all forms have descriptive names, not "Form 1" |

---

## Functionality

| Item | How to Check |
|------|-------------|
| WordPress on latest version | WP Admin → Dashboard → Updates |
| All plugins on current versions | WP Admin → Plugins → check for updates |
| WP Mail SMTP activated and configured | WP Admin → WP Mail SMTP → Settings → run the email test |
| Captcha on all web forms | Submit a form — verify captcha appears and works. Check honeypot or reCAPTCHA API key is set |

---

## Communication

| Item | How to Check |
|------|-------------|
| Forms working with captcha and email notifications | Submit each form with a test entry and verify email arrives |
| Contact details correct and easy to find | Check phone, email, address on contact page and footer |
| Images have appropriate alt text | (Duplicated from Content Integration — cross-reference) |
| Social media links set up | Click each social icon — confirm it goes to the correct profile |
| Comments & Pings turned off | WP Admin → Settings → Discussion → uncheck "Allow comments" and "Allow link notifications" |

---

## Benchmarks & Performance

| Item | How to Check |
|------|-------------|
| HTML W3C valid | https://validator.w3.org/ — paste the page URL |
| CSS W3C valid | https://jigsaw.w3.org/css-validator/ |
| No JavaScript console logs/errors/warnings | Open Chrome DevTools → Console → reload the page |
| No WordPress / PHP errors (Debug Mode) | Check WP_DEBUG is false in production. Check debug.log if enabled |
| Website through PageSpeed Insights | https://pagespeed.web.dev/ — record mobile and desktop scores |
| Website through Mobile Friendly Test | https://search.google.com/test/mobile-friendly |
| HTML, CSS, JS minified | Check via caching plugin settings or Cloudflare |
| Images compressed | Check file sizes in WP Media Library. Use Smush or ShortPixel |

---

## Compatibility

| Item | How to Check |
|------|-------------|
| Chrome | Open site in Chrome — test navigation, forms, scroll |
| Firefox | Open site in Firefox — test navigation, forms, scroll |
| Safari | Open site in Safari — test navigation, forms, scroll |
| Edge | Open site in Edge — test navigation, forms, scroll |
| iOS (real device) | Open site on iPhone in Safari — check mobile layout and forms |
| Android (real device) | Open site on Android in Chrome — check mobile layout and forms |
| Favicon and touch icons present | Check browser tab for favicon. On iOS: "Add to Home Screen" for touch icon |
| Site functions with JavaScript disabled | Chrome → Settings → Site Settings → JavaScript → disable → reload site |

---

## Accessibility

| Item | How to Check |
|------|-------------|
| Links are recognisable and have clear focus state | Tab through the page — links should have a visible focus ring |
| All form fields have labels (not just placeholder text) | Inspect form fields — each `<input>` should have a matching `<label>` |
| ARIA landmark roles used where appropriate | Use a screen reader or browser accessibility tool to check nav/main/footer roles |
| Colour contrast is appropriate | Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/ |
| Site tested and useable with a screen reader | Run VoiceOver (Mac/iOS) or NVDA (Windows) — navigate the home page |

---

## Infrastructure

| Item | How to Check |
|------|-------------|
| Domain and web hosting set up and linked | Visit the domain — site loads correctly |
| Automatic backups configured and working | ManageWP → Backups → confirm schedule and last successful backup |
| SSL certificate installed | Padlock icon in browser. Check expiry date |
| Files integrated with version control | Confirm Git repo exists and latest code is pushed |
| Admin email updated | WP Admin → Settings → General → Administration Email Address |
| Client user account set up | WP Admin → Users → confirm client user exists with correct role (Editor or Admin) |
| Client user signed up for Gravatar | Go to https://gravatar.com/ — confirm account linked to client email |
| Stripe Live Mode enabled | If using WooCommerce or Stripe plugin — switch from test to live mode |

---

## Analytics

| Item | How to Check |
|------|-------------|
| Analytics tracking installed and working | GA4 Real-Time report — visit the site and confirm active user appears |
| Event tracking set up for key metrics | Trigger a form submission, call click, or booking — confirm event fires in GA4 |
| Search Console set up and linked | GSC → Property settings — confirm site is verified |
| Sitemap submitted to GSC | GSC → Sitemaps → confirm `sitemap.xml` is submitted and indexed |
| GTM connected (if applicable) | GTM → Preview mode → visit the site and confirm tags fire |

---

## .htaccess & Robots

| Item | How to Check |
|------|-------------|
| GZIP/Brotli enabled | https://www.giftofspeed.com/gzip-test/ OR check Cloudflare settings |
| 301 redirects set up for old pages | Test old URLs — confirm they redirect to new equivalents |
| Expires caching activated | Check via caching plugin (LiteSpeed Cache, WP Rocket) or Cloudflare |
| Clean URL rewrites in place | Permalinks use `/slug/` format, not `?p=123` |
| All URL versions redirect to same format | Test: http://, https://, www., non-www — all should end at same canonical |
| robots.txt not blocking crawlers | Visit `/robots.txt` — no `Disallow: /` for Googlebot |
| Search engine indexing enabled | WP Admin → Settings → Reading → uncheck "Discourage search engines from indexing this site" |
