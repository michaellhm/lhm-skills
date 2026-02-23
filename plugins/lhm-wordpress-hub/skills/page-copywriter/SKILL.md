---
name: page-copywriter
description: "Write page content from a page brief. Produces complete page copy with YAML frontmatter, SEO metadata, section-by-section content, and component declarations. Use this when the user says 'write page content', 'write the copy', 'write homepage', 'content from brief', 'fill in the content', or 'write [page name] page'. Phase C of the website build. Requires page briefs from Phase B."
---

# Page Copywriter

Write complete page content from a page brief. Each content file includes SEO metadata, section-by-section copy, and component declarations that the WordPress builder will use.

## Before Starting

1. **Read client context** — read `/client/client_profile.md` for brand voice, audience, and key facts
2. **Read the page brief** — read the specific brief from `/seo/page_briefs/{slug}.md`
3. **Read any existing content** — if `/content/{slug}.md` already exists, read it first
4. If no brief exists for the requested page, offer to run the Page Brief Generator first

### Cross-Plugin Integration

For copywriting best practices, you can reference the marketing hub's copywriting skill:

Reference: `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/skills/copywriting/SKILL.md`

## Step 1: Scope

Use the `AskUserQuestion` tool to confirm:

> "Which page should I write content for?"

Options based on available briefs in `/seo/page_briefs/`. If the user wants all pages, work through them one at a time, presenting each for review before moving to the next.

## Step 2: Write the Content File

Create `/content/{slug}.md` (or `/content/services/{slug}.md` for service pages, `/content/locations/{slug}.md` for location pages).

### File Format

```markdown
---
title: "Page Title"
seo_title: "SEO Optimized Title | Brand Name"
meta_description: "Compelling 155-character meta description with primary keyword."
slug: /page-slug
template: default
status: draft
primary_keyword: "target keyword"
schema_type: WebPage
---

## Hero Section
<!-- component: hero-banner -->

# Headline That Communicates the Core Value

Supporting subheadline that expands on the headline and addresses the visitor's primary need.

**CTA:** Get Started | /contact

---

## [Section Name]
<!-- component: [pattern-name] -->

Section copy here. Written in the client's brand voice, targeting the primary audience.

Key points presented clearly:

- **Benefit one** — expanded explanation
- **Benefit two** — expanded explanation
- **Benefit three** — expanded explanation

---

## Call to Action
<!-- component: cta-section -->

Strong closing message that reinforces the value proposition and creates urgency.

**CTA:** Book Your Free Consultation | /contact
```

## Writing Rules

### Voice & Tone
- Match the brand voice from `client_profile.md`
- Write for the target audience, not the client
- Use the client's customers' language, not industry jargon
- Be specific — replace vague claims with concrete details from client files

### SEO
- Include the primary keyword in the H1, first paragraph, and at least one subheading
- Use secondary keywords naturally throughout
- Write for humans first, search engines second
- Keep sentences scannable — short paragraphs, bullet points, clear headers

### Structure
- Every section starts with `## Section Name` and a `<!-- component: name -->` declaration
- The component declaration tells the WordPress builder which block pattern to use
- CTAs include the link text and destination: `**CTA:** Text | /path`
- Use `---` between sections for visual separation

### Content Quality
- **No filler** — every sentence earns its place
- **No unsupported claims** — only include facts from client files or common knowledge
- **Specificity** — use real numbers, real service names, real locations from client context
- **Social proof** — reference testimonials or credentials if available in client files
- **Compliance** — check `/client/constraints.md` for regulatory requirements (e.g. AHPRA, NDIS)

## Step 3: SEO Validation

After writing, check:

1. **Title tag** — under 60 characters, includes primary keyword
2. **Meta description** — under 155 characters, includes primary keyword, has a call to action
3. **H1** — exactly one H1, includes primary keyword
4. **Keyword usage** — primary keyword appears 3-5 times naturally
5. **Internal links** — page references other pages as specified in the brief
6. **Word count** — meets the target from the brief (±10%)

## Step 4: Approval Gate

Present the completed page content. Show:
- Page title and slug
- SEO title and meta description
- Section list with component declarations
- Word count
- Keywords used

Use the `AskUserQuestion` tool:

> "Content written for **[Page Name]**. Review `/content/{slug}.md`. Approved?"

Options:
- "Approved — write the next page"
- "Needs edits" (then discuss changes)
- "Approved — all pages done, proceed to Phase D: Design"
