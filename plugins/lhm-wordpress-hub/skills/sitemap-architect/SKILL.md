---
name: sitemap-architect
description: "Build the site information architecture — keyword map, sitemap, and page hierarchy. Use this when the user says 'plan the sitemap', 'site structure', 'information architecture', 'IA planning', 'page hierarchy', 'keyword mapping', or 'site map'. Phase 2 of the website build. Requires client profile from Phase 1."
---

# Sitemap Architect

Build the site information architecture: keyword map, sitemap hierarchy, and page list. This defines what pages the site will have and why.

## Before Starting

1. **Read client context** — read all files in `/client/` (especially `client_profile.md`, `services.md`, `locations.md`)
2. **Check for existing SEO work** — if `/seo/keyword_map.md` or `/seo/sitemap.md` exist, read them and build on them
3. If client context is insufficient, tell the user what's missing and offer to run Client Context Intake first

## Step 1: Keyword Research

**Important:** Treat client website briefs as input, not gospel. Use keyword volume data to validate and override page structure decisions. The client may propose pages with no search demand or miss high-opportunity pages.

Build the keyword map. For each potential page, identify:

- **Primary keyword** — the main search term this page targets
- **Secondary keywords** — related terms and long-tail variations
- **Search intent** — informational, navigational, transactional, commercial investigation
- **Estimated volume** — high / medium / low (use Search Console data if available, or estimate from industry knowledge)
- **Competition** — high / medium / low

### Cross-Plugin Integration

If the marketing hub is available, you can load the keyword-research skill for deeper research:

Reference: `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/skills/keyword-research/SKILL.md`

And for competitive analysis: `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/skills/competitive-analysis/SKILL.md`

Ask the user if they want to use these before proceeding.

### Output: `/seo/keyword_map.md`

```markdown
# Keyword Map

## Homepage
| Keyword | Type | Intent | Volume | Competition |
|---------|------|--------|--------|-------------|
| [primary keyword] | Primary | Commercial | High | Medium |
| [secondary keyword] | Secondary | Informational | Medium | Low |

## About Page
...

## [Service Name] Page
...
```

## Step 2: Sitemap Architecture

Design the page hierarchy. Consider:

- **Flat architecture** — most pages within 2-3 clicks of homepage
- **Service/location structure** — if the client has multiple services and locations
- **Content hub model** — if there's a blog or resource section
- **SEO silos** — grouping related content under topic clusters

### Common Structures for Service Businesses

```
Home
├── About
├── Services
│   ├── Service A
│   ├── Service B
│   └── Service C
├── Locations (if multi-location)
│   ├── Location A
│   └── Location B
├── Blog / Resources
├── FAQ
├── Contact
└── Privacy Policy / Terms
```

### Output: `/seo/sitemap.md`

```markdown
# Sitemap

## Page Hierarchy

| Page | URL | Parent | Template | Priority |
|------|-----|--------|----------|----------|
| Home | / | — | homepage | Primary |
| About | /about | — | default | Secondary |
| Services | /services | — | default | Primary |
| Service A | /services/service-a | Services | service | Primary |
| Contact | /contact | — | contact | Primary |
| FAQ | /faq | — | default | Secondary |
| Privacy | /privacy-policy | — | default | Utility |

## Navigation Structure

### Primary Navigation
- Home
- About
- Services (dropdown)
  - Service A
  - Service B
- Contact

### Footer Navigation
- Privacy Policy
- Terms of Service
- Sitemap

## Internal Linking Strategy

[Notes on how pages should link to each other, topic clusters, and link equity flow]
```

## Step 3: Validation

Before finalizing, check:

1. **Every service** in `/client/services.md` has a corresponding page
2. **Every location** in `/client/locations.md` has a page (if location pages are warranted)
3. **No orphan pages** — every page is reachable from navigation or internal links
4. **No keyword cannibalization** — each page targets a unique primary keyword
5. **Depth ≤ 3** — most important pages within 3 clicks of homepage
6. **Merge thin pages** — combine problem/symptom pages that share the same root cause rather than creating separate thin pages. E.g. "swollen door" + "door won't close" + "door sticking" are all moisture-related and belong on one comprehensive page. Thin pages cannibalize each other.
7. **Branded product pages** — proprietary/branded product pages will have near-zero organic search volume when the brand is unknown. Their SEO value comes from internal cross-linking, not direct organic traffic. Build these pages for conversion, not discovery.

## Step 4: Approval Gate

Present the complete sitemap and keyword map to the user. Use the `AskUserQuestion` tool:

> "Here's the proposed site architecture with X pages. Review the sitemap and keyword map. Approved — proceed to **Page Briefs**?"

Options:
- "Approved — generate page briefs"
- "Changes needed" (then discuss modifications)
- "I want to add more pages"

Once approved, offer to run the **Page Brief Generator** skill for each page.
