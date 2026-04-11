---
name: site-architecture-mapper
description: "Generate a siloed site hierarchy that mirrors the client's GBP structure, mapping internal linking between homepage, category pages, and service pages. Use this when the user mentions 'map the site architecture for [Client]', 'site architecture', 'silo structure', 'site map', 'page hierarchy', 'internal linking map', or 'site structure'."
---

# Site Architecture Mapper

Generates a siloed website hierarchy that mirrors the client's Google Business Profile structure. Maps the relationship between the homepage (GBP landing page), category pages, and child service pages, with editorial internal linking instructions.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/site-architecture-mapper/LEARNED.md`
2. Read `client_profile.md` for business details, services, and location(s)
3. Read `onboarding/gbp_optimisation_plan.md` for the recommended GBP categories and service listings

## Workflow

### 1. Gather GBP Structure

From `gbp_optimisation_plan.md`, extract:
- Primary category
- Secondary categories (up to 9)
- All service listings (30+)
- Number of locations (single vs multi-location)

### 2. Generate Siloed Hierarchy

Build the site structure following the GBP-mirrored silo pattern:

**Single location:**
```
Homepage (GBP landing page)
├── Category Page: [Primary Category]
│   ├── Service Page: [Service 1]
│   ├── Service Page: [Service 2]
│   └── Service Page: [Service 3]
├── Category Page: [Secondary Category 1]
│   ├── Service Page: [Service 4]
│   └── Service Page: [Service 5]
├── Category Page: [Secondary Category 2]
│   └── ...
└── Supporting Pages (FAQ, About, Contact)
```

**Multi-location:** Each location gets its own landing page:
```
Homepage
├── Location Page: [Location 1] (GBP landing page for Location 1)
│   ├── Category Page: [Primary Category] [Location 1]
│   │   └── Service Pages...
│   └── ...
├── Location Page: [Location 2] (GBP landing page for Location 2)
│   ├── Category Page: [Primary Category] [Location 2]
│   │   └── Service Pages...
│   └── ...
└── Supporting Pages
```

### 3. Map Internal Linking Structure

For each level of the hierarchy, specify the editorial linking pattern:
- **Homepage** links to each category page within paragraph content (not just navigation)
- **Category pages** link to their child service pages within paragraph content
- **Service pages** link back to their parent category page and cross-link to related services
- All internal links should be editorial (within paragraph text), not just navigation menu links

Specify link anchor text recommendations for each connection.

### 4. Identify Existing vs New Pages

Compare the architecture against the client's current website:
- Which pages already exist and match the planned structure?
- Which pages need to be created?
- Which existing pages need restructuring or renaming?
- Are there orphan pages that don't fit the silo?

### 5. Handle Multi-Location Considerations

If the client has 2+ locations:
- Each GBP listing's website URL must point to its specific location page (not the homepage)
- Each location page acts as the GBP landing page for that location
- Flag if current GBP website URLs point to the wrong page

### 6. Present Architecture for Review

Display the complete architecture to the user:
- Full page hierarchy tree
- Internal linking map with anchor text suggestions
- List of pages to create vs existing pages
- Multi-location URL recommendations (if applicable)

Ask the user to review and confirm before finalising.

### 7. Update GMBProjectManagement.md

- Mark "Site architecture mapped" as complete with today's date
- Note the total page count (existing + new)

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| None required | — | Fully functional without any MCPs |

## Output

- `[client_folder]/gmb/onboarding/site_architecture.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
