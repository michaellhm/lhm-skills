---
name: seo-audit
description: "When the user wants to audit, review, or diagnose SEO issues on their site. Also use when the user mentions 'SEO audit,' 'technical SEO,' 'why am I not ranking,' 'SEO issues,' 'on-page SEO,' 'meta tags review,' 'SEO health check,' 'internal linking audit,' 'crawlability,' 'indexation issues,' or 'site speed audit.' Covers technical SEO, on-page optimization, internal linking, content quality, and CORE-EEAT quick scan."
---

# SEO Audit

Identifies SEO issues and provides actionable recommendations to improve organic search performance. Covers technical foundations, on-page optimization, internal linking, content quality, and E-E-A-T signals.

## Initial Assessment

**Check for client profile first:**
If `client_profile.md` exists, read it before asking questions. Use that context and only ask for information not already covered.

Before auditing, understand:

1. **Site Context** — type (SaaS, e-commerce, blog), primary SEO goal, priority keywords/topics
2. **Current State** — known issues, current organic traffic, recent changes/migrations
3. **Scope** — full site or specific pages, technical + on-page or one focus, Search Console access

---

## Audit Framework

### Priority Order
1. **Crawlability & Indexation** — can Google find and index it?
2. **Technical Foundations** — is the site fast and functional?
3. **On-Page Optimization** — is content optimized?
4. **Internal Linking** — is link equity flowing correctly?
5. **Content Quality & E-E-A-T** — does it deserve to rank?

---

## 1. Crawlability & Indexation

### Robots.txt
- Check for unintentional blocks
- Verify important pages allowed
- Check sitemap reference
- Verify AI crawler directives (GPTBot, ClaudeBot, Bingbot)

### XML Sitemap
- Exists and accessible
- Submitted to Search Console
- Contains only canonical, indexable URLs
- Updated regularly
- No non-200 URLs included

### Site Architecture
- Important pages within 3 clicks of homepage
- Logical hierarchy
- No orphan pages (every page has internal links)

### Index Status
- `site:domain.com` check
- Search Console coverage report
- Compare indexed vs. expected page count

### Indexation Issues
- Noindex tags on important pages
- Canonicals pointing wrong direction
- Redirect chains/loops (3+ hops)
- Soft 404s
- Duplicate content without canonicals

### Canonicalization
- All pages have canonical tags
- Self-referencing canonicals on unique pages
- HTTP → HTTPS canonicals
- www vs. non-www consistency
- Trailing slash consistency

---

## 2. Technical SEO

### Core Web Vitals
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4s | > 4s |
| INP (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 |

### Speed Factors
- Server response time (TTFB < 800ms)
- Image optimization (WebP, compressed, lazy loaded)
- JavaScript execution and bundle size
- CSS delivery (critical CSS inlined)
- Caching headers set
- CDN usage
- Font loading (font-display: swap)

### Mobile-Friendliness
- Responsive design (not separate m. site)
- Tap target sizes (48px minimum)
- Viewport configured
- No horizontal scroll
- Same content as desktop

### Security & HTTPS
- HTTPS across entire site
- Valid SSL certificate
- No mixed content
- HTTP → HTTPS redirects
- HSTS header

### URL Structure
- Readable, descriptive URLs
- Keywords in URLs where natural
- Lowercase and hyphen-separated
- No unnecessary parameters
- Consistent structure

---

## 3. On-Page SEO

### Title Tags
**Check**: Unique per page, primary keyword near beginning, 50-60 chars, compelling, brand at end.
**Issues**: Duplicates, too long/short, keyword stuffing, missing entirely.

### Meta Descriptions
**Check**: Unique per page, 150-160 chars, includes keyword, clear value prop, CTA.
**Issues**: Duplicates, auto-generated, no compelling reason to click.

### Heading Structure
**Check**: One H1 per page with primary keyword, logical H1→H2→H3 hierarchy, headings describe content.
**Issues**: Multiple H1s, skipped levels, headings used for styling only.

### Content Optimization
- Keyword in first 100 words
- Related keywords naturally used
- Sufficient depth for topic
- Answers search intent
- Better than top competitors

### Image Optimization
- Descriptive file names
- Alt text on all images (describes image, includes keyword where natural)
- Compressed file sizes (< 200KB for most images)
- Modern formats (WebP/AVIF)
- Lazy loading + responsive images

### Keyword Targeting
**Per page**: Clear primary keyword, title/H1/URL aligned, content satisfies intent, no cannibalization.
**Site-wide**: Keyword mapping exists, no major topic gaps, logical clusters.

---

## 4. Internal Linking

### Link Structure Analysis
- Homepage link equity distribution
- Click depth for key pages (target: 3 clicks max)
- Link distribution across site sections
- Navigation vs. contextual links ratio

### Orphan Pages
Identify pages with zero internal links pointing to them:
```markdown
### Orphan Pages Found

| URL | Page Type | Priority | Fix |
|-----|----------|----------|-----|
| [url] | [type] | High/Med/Low | [add links from X, Y, Z] |
```

### Anchor Text Distribution
- Descriptive anchor text (not "click here")
- Varied but relevant anchors per target page
- No over-optimization (exact match anchor text)

### Topic Cluster Links
- Pillar pages link to all cluster pages
- Cluster pages link back to pillar
- Related cluster pages interlink
- Contextual links within body content (not just nav)

### Link Issues
- Broken internal links (404s)
- Excessive links per page (keep reasonable, under 100)
- Important pages buried (high click depth)
- Redirect chains in internal links (link to final URL)

---

## 5. Content Quality & E-E-A-T

### CORE-EEAT Quick Scan

Quick check of the 17 highest-impact items:

```markdown
### CORE-EEAT Quick Scan

| ID | Item | Status | Notes |
|----|------|--------|-------|
| C01 | Intent alignment (title = content) | ✅/⚠️/❌ | |
| C02 | Direct answer in first 150 words | ✅/⚠️/❌ | |
| C05 | Quotable standalone statements | ✅/⚠️/❌ | |
| C09 | FAQ section with schema | ✅/⚠️/❌ | |
| O01 | Heading hierarchy correct | ✅/⚠️/❌ | |
| O03 | Data in tables, not prose | ✅/⚠️/❌ | |
| O05 | JSON-LD schema markup | ✅/⚠️/❌ | |
| R01 | 5+ data points with units | ✅/⚠️/❌ | |
| R02 | 1+ citation per 500 words | ✅/⚠️/❌ | |
| R04 | Claims backed by evidence | ✅/⚠️/❌ | |
| R10 | No contradictions | ✅/⚠️/❌ | |
| Exp01 | First-hand experience shown | ✅/⚠️/❌ | |
| Ept01 | Technical depth appropriate | ✅/⚠️/❌ | |
| A01 | Author credentials visible | ✅/⚠️/❌ | |
| T01 | Facts verified correct | ✅/⚠️/❌ | |
| T04 | Disclosure & transparency | ✅/⚠️/❌ | |
| T10 | "Last updated" date visible | ✅/⚠️/❌ | |

**Quick verdict**: [X]/17 passing — [rating]
```

For a full 80-item audit, use the **content-quality-auditor** skill.

### E-E-A-T Signals
- **Experience**: First-hand experience, original insights, real examples
- **Expertise**: Author credentials, accurate information, sourced claims
- **Authoritativeness**: Recognized in space, cited by others
- **Trustworthiness**: Accurate, transparent, contact info, HTTPS

---

## Common Issues by Site Type

### SaaS/Product Sites
Product pages lack depth, blog disconnected from product, missing comparison/alternative pages, thin feature pages.

### E-commerce
Thin category pages, duplicate product descriptions, missing product schema, faceted navigation duplicates, mishandled out-of-stock pages.

### Content/Blog Sites
Outdated content, keyword cannibalization, no topical clustering, poor internal linking, missing author pages.

### Local Business
Inconsistent NAP, missing local schema, no Google Business Profile optimization, no location pages.

---

## Output Format

### Audit Report Structure

**Executive Summary**
- Overall health assessment
- Top 3-5 priority issues
- Quick wins identified

**Findings** (per section)
- **Issue**: What's wrong
- **Impact**: High/Medium/Low
- **Evidence**: How you found it
- **Fix**: Specific recommendation
- **Priority**: 1-5

**Prioritized Action Plan**
1. Critical fixes (blocking indexation/ranking)
2. High-impact improvements
3. Quick wins (easy, immediate benefit)
4. Long-term recommendations

---

## References

- [AI Writing Detection](references/ai-writing-detection.md): Common AI writing patterns to avoid
- [AEO & GEO Patterns](references/aeo-geo-patterns.md): Content patterns for AI citation

---

## Related Skills

- **content-quality-auditor** — full 80-item CORE-EEAT audit
- **schema-markup** — implementing structured data
- **meta-tags-optimizer** — optimizing title tags and descriptions
- **content-refresher** — updating underperforming content
- **programmatic-seo** — building SEO pages at scale
- **analytics-tracking** — measuring SEO performance
