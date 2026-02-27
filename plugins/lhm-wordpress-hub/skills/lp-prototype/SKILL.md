---
name: lp-prototype
description: "Build HTML/CSS landing page prototypes for a PPC campaign. Use this when the user says 'build the prototype', 'create the landing page prototype', 'build the HTML for the landing page', 'lp-prototype', or 'create the landing pages'. Reads from /lp/copy/ and the health theme template to produce a pixel-perfect HTML/CSS file per ad group."
---

# LP Prototype

Build self-contained HTML/CSS landing page prototypes — one per ad group — using the approved template structure and the copy written by lp-copy.

These prototypes are the single source of truth for the visual design. WordPress mirrors them, not the other way around.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-prototype/LEARNED.md`
2. Read `client_profile.md` for brand colours, typography, logo, and any design constraints
3. Read `lp/lp_state.md` to confirm which ad groups have copy files ready
4. Read each copy file in `/lp/copy/` for the sections and content
5. Check if a template base file exists at `${CLAUDE_PLUGIN_ROOT}/assets/templates/[INDUSTRY]/index.html`
   - If it exists: use it as the starting point
   - If not: build from the section structure below using the brand variables from client_profile.md

## Step 1: Confirm Scope

Use the `AskUserQuestion` tool:

> "Which ad groups should I build prototypes for?"

Options:
- "All ad groups with copy ready"
- "Just the first one (primary ad group)"
- "Let me specify"

Start with the primary ad group. Once approved, run remaining groups.

## Step 2: Establish Design Variables

Extract these from `client_profile.md`. Map to CSS custom properties:

```css
:root {
  /* Brand colours */
  --color-primary: [HEX];
  --color-primary-dark: [HEX];
  --color-primary-light: [HEX];
  --color-header: [HEX];
  --color-body-text: [HEX];

  /* Typography */
  --font-body: '[GOOGLE_FONT_NAME]', sans-serif;
  --font-heading: '[GOOGLE_FONT_NAME]', sans-serif; /* same if only one font */

  /* Layout */
  --container-max: 1200px;
  --container-padding: 24px;
  --section-padding: 80px 0;
  --section-padding-mobile: 56px 0;

  /* Radius and shadows */
  --radius-card: 12px;
  --shadow-card: 0 4px 16px rgba(0,0,0,0.08);
}
```

## Step 3: Build the HTML Prototype

Create `/lp/prototype/[ad-group-slug]/index.html`.

The file must be self-contained:
- All CSS in a `<style>` block in `<head>` (no external stylesheets except Google Fonts)
- All JS in a `<script>` block before `</body>`
- Images referenced from `/lp/assets/` (create this folder if needed) or use placeholder URLs

### Section Sequence and HTML Patterns

Build sections in this exact order. Each section must have a consistent class name because deploy-2 maps classes to Gutenberg blocks.

---

**Site Header (sticky)**
```html
<header class="site-header" id="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="/" class="site-logo">
        <img src="/lp/assets/logo.png" alt="[CLINIC_NAME]" />
      </a>
      <a href="#book" class="btn btn-primary header-cta">Book Online</a>
    </div>
  </div>
</header>
```

---

**Hero Section**
```html
<section class="hero-section">
  <div class="container">
    <h1 class="hero-headline">[HEADLINE]</h1>
    <p class="hero-subheadline">[SUBHEADLINE]</p>
    <div class="hero-cta-group">
      <a href="#book" class="btn btn-primary hero-cta">[PRIMARY CTA]</a>
      <span class="hero-cta-subtext">[CTA SUBTEXT]</span>
    </div>
  </div>
</section>
```

---

**Trust Bar**
```html
<section class="trust-bar">
  <div class="container">
    <div class="trust-items">
      <div class="trust-item">
        <span class="trust-rating">[RATING]★</span>
        <span class="trust-label">[REVIEW COUNT] Google Reviews</span>
      </div>
      <div class="trust-item trust-divider"></div>
      <div class="trust-item">
        <span class="trust-stat">[STAT 1]</span>
      </div>
      <div class="trust-item trust-divider"></div>
      <div class="trust-item">
        <span class="trust-stat">[STAT 2]</span>
      </div>
    </div>
  </div>
</section>
```

---

**Pain Points**
```html
<section class="pain-points-section">
  <div class="container">
    <h2 class="section-heading">[PAIN SECTION HEADING]</h2>
    <div class="pain-grid">
      <div class="pain-item">
        <p>[PAIN POINT 1]</p>
      </div>
      <!-- repeat for each pain point -->
    </div>
  </div>
</section>
```

---

**Solution Intro**
```html
<section class="solution-section">
  <div class="container solution-inner">
    <h2 class="section-heading">[SOLUTION HEADING]</h2>
    <p class="solution-body">[SOLUTION COPY]</p>
  </div>
</section>
```

---

**Service Features**
```html
<section class="features-section">
  <div class="container">
    <h2 class="section-heading">[FEATURES HEADING]</h2>
    <div class="features-grid">
      <div class="feature-card">
        <h3 class="feature-title">[FEATURE TITLE]</h3>
        <p class="feature-body">[FEATURE DESCRIPTION]</p>
      </div>
      <!-- repeat for each feature -->
    </div>
  </div>
</section>
```

---

**Social Proof / Testimonials**
```html
<section class="testimonials-section">
  <div class="container">
    <h2 class="section-heading">[TESTIMONIALS HEADING]</h2>
    <div class="testimonials-grid">
      <div class="testimonial-card">
        <blockquote class="testimonial-quote">"[QUOTE]"</blockquote>
        <cite class="testimonial-author">— [NAME], [SUBURB]</cite>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

---

**How It Works**
```html
<section class="process-section">
  <div class="container">
    <h2 class="section-heading">[PROCESS HEADING]</h2>
    <div class="process-steps">
      <div class="process-step">
        <span class="step-number">1</span>
        <h3 class="step-title">[STEP TITLE]</h3>
        <p class="step-body">[STEP DESCRIPTION]</p>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

---

**FAQ**
```html
<section class="faq-section">
  <div class="container">
    <h2 class="section-heading">[FAQ HEADING]</h2>
    <div class="faq-list">
      <div class="faq-item" id="book">
        <button class="faq-question" aria-expanded="false">[QUESTION]</button>
        <div class="faq-answer"><p>[ANSWER]</p></div>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

---

**Locations / Booking CTA**
```html
<section class="locations-section">
  <div class="container">
    <h2 class="section-heading">[CTA HEADING]</h2>
    <p class="locations-body">[CTA BODY COPY]</p>
    <div class="locations-grid" id="locations">
      <!-- Populated dynamically from Location CPT in WordPress -->
      <!-- In prototype, include placeholder cards -->
      <div class="location-card">
        <h3 class="location-name">[SUBURB] Clinic</h3>
        <p class="location-address">[ADDRESS]</p>
        <p class="location-phone">[PHONE]</p>
        <a href="[BOOKING_URL]" class="btn btn-primary location-book-btn">Book at [SUBURB]</a>
      </div>
    </div>
  </div>
</section>
```

---

**Site Footer**
```html
<footer class="site-footer">
  <div class="container">
    <div class="footer-inner">
      <p class="footer-logo"><img src="/lp/assets/logo.png" alt="[CLINIC_NAME]" /></p>
      <div class="footer-social">
        <!-- Social media links if provided -->
      </div>
      <p class="footer-legal">© [YEAR] [CLINIC_NAME]. All rights reserved.</p>
    </div>
  </div>
</footer>
```

---

**FAQ accordion JS (add before `</body>`):**
```html
<script>
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !expanded);
      btn.nextElementSibling.style.display = expanded ? 'none' : 'block';
    });
  });
</script>
```

## Step 4: Apply Brand Styling

Write a comprehensive `<style>` block using the CSS custom properties from Step 2. Keep these principles:
- Use `--color-primary` consistently for CTAs, accents, and section backgrounds
- Use `--color-primary-dark` for hover states and header backgrounds
- Keep typography simple: headings in `--font-heading`, body in `--font-body`
- Use the `.container` class to constrain all content to `--container-max`
- Mobile-first media queries: base styles for mobile, `@media (min-width: 768px)` for tablet, `@media (min-width: 1024px)` for desktop

## Step 5: Review and Iterate

After building the prototype:
1. Open it in a browser via a local server: `python3 -m http.server 9000 --directory lp/prototype/[ad-group-slug]`
2. Check at mobile (390px) and desktop (1440px) widths
3. Verify every section from the copy file is present

If revisions are needed, update the prototype file and confirm before proceeding.

## Step 6: Update State File

Update `/lp/lp_state.md` — Pages Built table:

```
| [Ad Group] | /lp/copy/[slug]-copy.md | /lp/prototype/[slug]/index.html | ⏳ | ⏳ | - | Copy + Prototype ready |
```

## Handoff

Tell the user:

> "Prototype complete for [AD GROUP] at `/lp/prototype/[slug]/index.html`. Check it in your browser then run **lp-deploy-1** to push it to WordPress."

If building all ad groups: confirm each prototype before building the next.
