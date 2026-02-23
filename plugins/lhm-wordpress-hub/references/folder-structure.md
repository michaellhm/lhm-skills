# Canonical Project Folder Structure

This is the single source of truth for every WordPress website project. All agents and skills reference this structure. Do not deviate.

## Structure

```
/project-root/
  /client/
    client_profile.md          # Business facts, contact info, goals
    services.md                # Service offerings with descriptions
    locations.md               # Service areas and location details
    constraints.md             # Budget, timeline, tech, compliance constraints
    clarifications.md          # Q&A log from client conversations
  /seo/
    keyword_map.md             # Master keyword research with clusters
    sitemap.md                 # Site information architecture
    /page_briefs/
      home.md                  # Homepage brief
      about.md                 # About page brief
      contact.md               # Contact page brief
      service-{name}.md        # One brief per service page
      location-{name}.md       # One brief per location page
  /content/
    home.md                    # Homepage copy
    about.md                   # About page copy
    contact.md                 # Contact page copy
    /services/
      {service-name}.md        # One file per service page
    /locations/
      {location-name}.md       # One file per location page
    faq.md                     # FAQ content
  /design/
    brand_guidelines.md        # Brand colors, typography, tone, imagery
    design_system.md           # Design tokens, spacing, component specs
    blocks.md                  # Block architecture decisions
    /prototype/
      /homepage/               # Approved frontend HTML prototype (mandatory)
        index.html             # (or v1.html, v2.html if multi-version)
        /assets/
          /css/style.css
          /js/main.js
          /images/
  /wp/
    theme/                     # Custom block theme files
    blocks/                    # Custom block definitions
    wp_state.md                # Current WordPress build state log
  /qa/
    /home/                     # QA screenshots and report for homepage
      prototype-desktop-standard.png
      wordpress-desktop-standard.png
      prototype-mobile-standard.png
      wordpress-mobile-standard.png
      qa-report.md
    /about/                    # QA screenshots and report for about page
    /[page-slug]/              # One folder per tested page
  /ops/
    performance.md             # Performance audit and optimizations
    security.md                # Security hardening checklist
    editor_notes.md            # Client editor training notes
```

## Rules

1. **Filesystem is source of truth** — WordPress mirrors what's in these files, not the other way around.
2. **One file per page** — every page gets its own content file with YAML frontmatter.
3. **Phases build on each other** — `/client/` feeds `/seo/`, which feeds `/content/`, which feeds `/wp/`.
4. **Never overwrite** — if a file exists, read it first. Append or version, don't replace.
5. **Slugs as filenames** — use kebab-case filenames matching the intended URL slug.

## Content File Format

Every content `.md` file uses this frontmatter:

```yaml
---
title: "Page Title"
seo_title: "SEO Optimized Title | Brand"
meta_description: "155 character meta description"
slug: /page-slug
template: default
status: draft | review | approved
---
```

Followed by section-by-section copy with component declarations:

```markdown
## Hero Section
<!-- component: hero-banner -->

Headline copy here.

Subheadline copy here.

**CTA:** Book a Free Consultation | /contact

## Services Overview
<!-- component: card-grid -->

...
```

## Phase Detection

The orchestrator detects the current phase by inspecting which folders exist:

| Folders Present | Next Phase |
|----------------|------------|
| None | A — Client Intake |
| `/client/` only | B — SEO & IA |
| `/client/` + `/seo/` | C — Content |
| `/client/` + `/seo/` + `/content/` | D — Design |
| `/client/` + `/seo/` + `/content/` + `/design/` | E — WP Build |
| All above + `/wp/` | F — Ops |
| All folders present | Post-launch — Site Extension |
