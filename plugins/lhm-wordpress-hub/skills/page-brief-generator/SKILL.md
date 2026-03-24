---
name: page-brief-generator
description: "Generate per-page content briefs with target keywords, search intent, page sections, and CTAs. Use this when the user says 'create page briefs', 'write a brief', 'page brief', 'content brief', 'brief for homepage', 'brief for service page', or 'section outline'. Phase B of the website build. Requires sitemap and keyword map from the Sitemap Architect."
---

# Page Brief Generator

Generate detailed content briefs for each page in the sitemap. Each brief tells the content writer exactly what to write — keywords to target, sections to include, CTAs to place, and intent to satisfy.

## Before Starting

1. **Read the sitemap** — read `/seo/sitemap.md` for the page list and hierarchy
2. **Read the keyword map** — read `/seo/keyword_map.md` for target keywords per page
3. **Read client context** — read `/client/client_profile.md` and `/client/services.md`
4. If any of these files are missing, tell the user which prerequisite is needed

## Step 1: Scope the Briefs

Use the `AskUserQuestion` tool to ask:

> "I'll generate content briefs for each page. Which pages should I brief?"

Options:
- "All pages in the sitemap"
- "Just the core pages (Home, About, Services, Contact)"
- "Specific pages" (let them list which ones)

## Step 2: Generate Each Brief

**Performance tip:** When generating 20+ briefs, split the work into two parallel agents (e.g. core pages + secondary pages). Provide full context in each agent prompt since they don't share state.

For each page, create a file at `/seo/page_briefs/{slug}.md` with this structure:

```markdown
---
title: "Page Title"
slug: /page-slug
primary_keyword: "main keyword"
secondary_keywords: ["keyword 2", "keyword 3", "keyword 4"]
search_intent: informational | commercial | transactional | navigational
word_count_target: 800
template: default | homepage | service | contact | landing-page
status: draft
---

# Brief: [Page Title]

## Purpose
[One sentence: why this page exists and what it should achieve]

## Target Audience
[Who is landing on this page and what do they need?]

## Search Intent
[What is the user trying to do when they search for the primary keyword?]

## Sections

### 1. Hero Section
- **Component**: hero-banner
- **Headline direction**: [What the headline should communicate]
- **Subheadline direction**: [Supporting message]
- **CTA**: [Primary call to action with destination]

### 2. [Section Name]
- **Component**: [block pattern to use]
- **Content direction**: [What this section should cover]
- **Key points to include**:
  - Point 1
  - Point 2
  - Point 3

### 3. [Section Name]
...

### N. CTA Section
- **Component**: cta-section
- **Message direction**: [Final push / urgency / value reminder]
- **CTA**: [Call to action with destination]

## SEO Requirements
- **Title tag**: [SEO title suggestion — under 60 chars]
- **Meta description**: [Meta description direction — under 155 chars]
- **H1**: [Must include primary keyword]
- **Internal links**: [Which pages to link to and from]
- **Schema type**: [WebPage, LocalBusiness, Service, FAQPage, etc.]

## Tone & Style
[Refer to client profile for brand voice. Note any page-specific tone adjustments.]

## Competitor Reference
[If applicable: what top-ranking competitors cover for this keyword. What gaps exist.]

## Notes
[Anything else the content writer needs to know]
```

## Page-Type Templates

### Homepage Brief Sections
1. Hero — value proposition, primary CTA
2. Problem/Solution — identify the pain, present the answer
3. Services overview — card grid linking to service pages
4. Social proof — testimonials, logos, case study snippets
5. About teaser — brief intro linking to about page
6. CTA — final conversion push

### Service Page Brief Sections
1. Hero — service name, key benefit, CTA
2. Problem — the problem this service solves
3. Solution — how the service works
4. Features/benefits — detailed breakdown
5. Process — how to get started (numbered steps)
6. Testimonials — relevant social proof
7. FAQ — common questions about this service
8. CTA — book / enquire / get started

### About Page Brief Sections
1. Hero — who we are headline
2. Story — founding story, mission
3. Values — what drives the business
4. Team — key people
5. Achievements — credentials, certifications, numbers
6. CTA — work with us

### Contact Page Brief Sections
1. Hero — get in touch headline
2. Contact details — phone, email, address
3. Form — contact form
4. Map — location embed
5. FAQ — common pre-contact questions

## Step 3: Cross-Reference

After generating all briefs, verify:

1. **Internal linking** — every brief references which other pages to link to
2. **No keyword overlap** — each brief targets unique primary keywords
3. **CTA consistency** — CTAs route to logical destinations
4. **Coverage** — every service and location from client files has a corresponding brief

## Step 4: Approval Gate

Present the brief summary to the user. For each page, show:
- Page name and slug
- Primary keyword
- Section count
- Estimated word count

Use the `AskUserQuestion` tool:

> "Page briefs generated for X pages. Review the briefs in `/seo/page_briefs/`. Approved — proceed to **Phase C: Content Writing**?"
