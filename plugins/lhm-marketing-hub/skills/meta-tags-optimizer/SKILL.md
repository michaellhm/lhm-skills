---
name: meta-tags-optimizer
description: "Creates and optimizes title tags, meta descriptions, Open Graph tags, and Twitter cards for maximum CTR and SERP visibility. Use this when the user mentions 'meta tags,' 'title tags,' 'meta descriptions,' 'Open Graph,' 'OG tags,' 'Twitter cards,' 'SERP snippets,' 'click-through rate,' or 'CTR optimization.' Covers all page types including homepages, blogs, products, and services."
---

# Meta Tags Optimizer

Creates compelling, keyword-optimized meta tags that improve click-through rates and SERP visibility. Covers title tags, meta descriptions, Open Graph tags, and Twitter cards.

## When to Use This Skill

- Writing or rewriting title tags for better rankings and CTR
- Creating meta descriptions that drive clicks
- Setting up Open Graph tags for social sharing
- Configuring Twitter cards
- Auditing existing meta tags for improvements
- Optimizing CTR for pages that rank but don't get clicks

## Instructions

When a user requests meta tag optimization:

### 1. Gather Page Information

```markdown
### Page Details

**URL**: [page URL]
**Page type**: [homepage/blog/product/service/landing/category]
**Primary keyword**: [target keyword]
**Secondary keywords**: [2-3 related keywords]
**Current title**: [existing title tag, if any]
**Current description**: [existing meta description, if any]
**Search intent**: [informational/commercial/transactional/navigational]
```

### 2. Create Title Tag Options

**Requirements:**
- Include primary keyword (preferably near the start)
- 50-60 characters for full SERP display
- Compelling and click-worthy
- Match search intent

**Title formulas to consider:**

| Formula | Example |
|---------|---------|
| Keyword \| Benefit \| Brand | "SEO Audit Checklist \| Free Template \| Brand" |
| How to [Goal] in [Timeframe] | "How to Rank on Google in 30 Days" |
| [Number] [Adjective] [Topic] ([Year]) | "7 Proven SEO Tips (2026)" |
| [Topic]: The Complete Guide | "Technical SEO: The Complete Guide" |
| [Option A] vs [Option B]: Which Is Better? | "Ahrefs vs SEMrush: Which Is Better?" |

```markdown
### Title Tag Options

1. **[Title option 1]** ([X] chars)
   - Keyword position: [front/middle]
   - Power words: [list]

2. **[Title option 2]** ([X] chars)
   - Keyword position: [front/middle]
   - Power words: [list]

3. **[Title option 3]** ([X] chars)
   - Keyword position: [front/middle]
   - Power words: [list]

**Recommended**: Option [X] — [reasoning]
```

### 3. Write Meta Description

**Requirements:**
- 150-160 characters
- Include primary keyword naturally
- Clear value proposition
- Call-to-action or curiosity hook
- Match search intent

```markdown
### Meta Description

"[Description text]" ([X] characters)

**Elements included**:
- ✅ Primary keyword
- ✅ Value proposition
- ✅ CTA or curiosity hook
- ✅ Matches search intent
```

### 4. Create Open Graph Tags

```markdown
### Open Graph Tags

```html
<meta property="og:title" content="[Title — can be longer than SERP title, up to 95 chars]">
<meta property="og:description" content="[Description optimized for social — up to 200 chars]">
<meta property="og:type" content="[article/website/product]">
<meta property="og:url" content="[canonical URL]">
<meta property="og:image" content="[image URL — 1200x630px recommended]">
<meta property="og:site_name" content="[Brand Name]">
```
```

### 5. Create Twitter Card Tags

```markdown
### Twitter Card Tags

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[Title — up to 70 chars]">
<meta name="twitter:description" content="[Description — up to 200 chars]">
<meta name="twitter:image" content="[image URL — 1200x628px]">
```
```

### 6. CTR Analysis (for existing pages)

If optimizing existing pages, check Search Console data:

```markdown
### CTR Analysis

| Page | Avg Position | Impressions | Clicks | CTR | Benchmark |
|------|-------------|-------------|--------|-----|-----------|
| [url] | [pos] | [imp] | [clicks] | [ctr]% | [expected]% |

**CTR verdict**: [Above/Below benchmark]
**Likely cause**: [title not compelling / description generic / wrong intent / etc.]
**Recommended change**: [specific improvement]
```

### 7. Compile Full Tag Set

```markdown
### Complete Meta Tags

```html
<!-- Primary Meta Tags -->
<title>[Optimized title]</title>
<meta name="description" content="[Optimized description]">

<!-- Open Graph -->
<meta property="og:title" content="[OG title]">
<meta property="og:description" content="[OG description]">
<meta property="og:type" content="[type]">
<meta property="og:url" content="[URL]">
<meta property="og:image" content="[image URL]">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[Twitter title]">
<meta name="twitter:description" content="[Twitter description]">
<meta name="twitter:image" content="[image URL]">
```
```

## Page-Type Templates

### Homepage
- Title: `[Brand] — [Value Proposition] | [Category]` (e.g. "Acme — Project Management for Teams | Free Trial")
- Description: Focus on brand value prop + CTA

### Blog Post
- Title: `[Primary Keyword] — [Hook/Benefit]` (e.g. "Email Marketing Tips — 7 Tactics That Actually Work")
- Description: Summarize what reader will learn + curiosity hook

### Product Page
- Title: `[Product Name] — [Key Benefit] | [Brand]`
- Description: Feature highlights + pricing signal + CTA

### Service Page
- Title: `[Service] in [Location] — [Differentiator] | [Brand]`
- Description: Service overview + trust signal + CTA

## Validation Checkpoints

- [ ] Title tag is 50-60 characters and includes primary keyword
- [ ] Meta description is 150-160 characters with CTA
- [ ] Open Graph tags set with 1200x630px image
- [ ] Twitter card tags configured
- [ ] All tags match search intent
- [ ] No duplicate titles or descriptions across the site

## Related Skills

- **seo-content-writer** — create the content these tags describe
- **seo-audit** — broader SEO diagnostics including meta tag review
- **geo-content-optimizer** — optimize content for AI citations
- **schema-markup** — add structured data alongside meta tags
