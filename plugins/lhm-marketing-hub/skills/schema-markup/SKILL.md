---
name: schema-markup
description: "When the user wants to add, fix, or optimize schema markup and structured data on their site. Also use when the user mentions 'schema markup,' 'structured data,' 'JSON-LD,' 'rich snippets,' 'schema.org,' 'FAQ schema,' 'product schema,' 'review schema,' 'breadcrumb schema,' 'HowTo schema,' 'LocalBusiness schema,' or 'rich results.' Covers all schema types with content-type mapping and validation."
---

# Schema Markup

Implements schema.org markup in JSON-LD format to help search engines and AI systems understand content and enable rich results in search.

## Initial Assessment

**Check for client profile first:**
If `client_profile.md` exists, read it before asking questions.

Before implementing schema, understand:
1. **Page Type** — what kind of page, primary content, possible rich results
2. **Current State** — existing schema, errors, which rich results already appear
3. **Goals** — which rich results targeted, business value

---

## Content-Type to Schema Mapping

Use this table to select the right schema for each content type:

| Content Type | Required Schema | Conditional Schema |
|-------------|----------------|-------------------|
| Blog (guide) | Article, Breadcrumb | FAQ, HowTo |
| Blog (tools/review) | Article, Breadcrumb | FAQ, Review |
| Comparison/Alternative | Article, Breadcrumb, FAQ | AggregateRating |
| Best-of/Listicle | ItemList, Breadcrumb, FAQ | AggregateRating per item |
| FAQ page | FAQPage, Breadcrumb | — |
| Landing page | SoftwareApplication, Breadcrumb, FAQ | WebPage |
| Product page | Product, Breadcrumb | FAQ, Review |
| Local business | LocalBusiness, Breadcrumb | FAQ |
| Event | Event, Breadcrumb | — |
| How-to/Tutorial | HowTo, Article, Breadcrumb | FAQ |

---

## Core Principles

1. **Accuracy First** — schema must accurately represent visible page content
2. **Use JSON-LD** — Google's recommended format, place in `<head>` or before `</body>`
3. **Follow Google's Guidelines** — only use markup Google supports for rich results
4. **Validate Everything** — test before deploying, monitor Search Console

---

## Schema Types & Templates

### Organization (Company Page)
Required: name, url | Recommended: logo, sameAs, contactPoint

### Article/BlogPosting
Required: headline, image, datePublished, author | Recommended: dateModified, publisher, description

### Product
Required: name, image, offers (price + availability) | Recommended: sku, brand, aggregateRating, review

### FAQPage
Required: mainEntity (array of Question/Answer pairs)

### HowTo
Required: name, step (array of HowToStep) | Recommended: totalTime, estimatedCost

### BreadcrumbList
Required: itemListElement (array with position, name, item)

### LocalBusiness
Required: name, address | Recommended: geo, telephone, openingHoursSpecification

### Event
Required: name, startDate, location | Recommended: endDate, offers, performer

**For complete JSON-LD code examples**: See [references/schema-examples.md](references/schema-examples.md)

---

## Rich Result Eligibility

| Rich Result Type | Schema Required | Impact |
|-----------------|----------------|--------|
| FAQ dropdowns | FAQPage | High — expands SERP presence |
| How-To steps | HowTo | Medium — shows steps in SERP |
| Product price/stars | Product + Offer + AggregateRating | High — shows price, availability |
| Review stars | Review or AggregateRating | High — shows star ratings |
| Article info | Article | Medium — shows date, author |
| Breadcrumbs | BreadcrumbList | Medium — shows navigation path |
| Video thumbnail | VideoObject | High — shows video in SERP |
| Sitelinks searchbox | WebSite + SearchAction | Medium — enables site search |

---

## Combining Multiple Schema Types

Use `@graph` to combine multiple schema types on one page:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", ... },
    { "@type": "WebSite", ... },
    { "@type": "BreadcrumbList", ... },
    { "@type": "Article", ... },
    { "@type": "FAQPage", ... }
  ]
}
```

---

## Validation and Testing

### Tools
- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Schema.org Validator**: https://validator.schema.org/
- **Search Console**: Enhancements reports

### Common Errors
- **Missing required properties** — check Google docs for required fields
- **Invalid values** — dates must be ISO 8601, URLs fully qualified
- **Mismatch with page content** — schema doesn't match what's visible
- **Trailing commas** — JSON syntax error
- **Relative URLs** — must be absolute

### Validation Checklist
- [ ] JSON syntax validates (no trailing commas, proper quotes)
- [ ] All required properties present for chosen schema type
- [ ] URLs are absolute, not relative
- [ ] Dates in ISO 8601 format
- [ ] Schema content matches visible page content exactly
- [ ] Passes Rich Results Test with no errors
- [ ] No policy violations (no markup for hidden content)

---

## Implementation

### Static Sites
Add JSON-LD directly in HTML template head.

### Dynamic Sites (React, Next.js)
Component that renders schema, server-side rendered.

### CMS / WordPress
Plugins (Yoast, Rank Math, Schema Pro) or theme modifications.

### Placement
```html
<head>
  <script type="application/ld+json">
    { ... your schema ... }
  </script>
</head>
```

---

## Output Format

For each page, provide:
1. **Schema type recommendation** with reasoning
2. **Complete JSON-LD code block** ready to copy
3. **Testing checklist** results
4. **SERP preview** showing expected rich result

---

## Related Skills

- **seo-audit** — broader SEO including schema review
- **meta-tags-optimizer** — meta tags alongside structured data
- **geo-content-optimizer** — FAQ schema helps GEO optimization
- **seo-content-writer** — create content worth marking up
- **programmatic-seo** — templated schema at scale
