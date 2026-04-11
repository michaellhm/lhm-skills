---
name: entity-mapper
description: "Extract expert-level entities, concepts, and technical terms from top-ranking competitor content to build an entity map that proves topical authority. Use this when the user mentions 'run entity mapping for [Client]', 'entity mapping', 'entity map', 'extract entities', 'topical authority', 'entity gaps', or 'competitor entities'."
---

# Entity Mapper

Identifies top-ranking competitors, fetches their service page content, and extracts the entities, concepts, and technical terms that Google associates with genuine expertise in the client's modality. The resulting entity map is referenced by all content-producing skills to ensure the client's content demonstrates real authority.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/entity-mapper/LEARNED.md`
2. Read `client_profile.md` for client details, modality, and services
3. Read `onboarding/diagnostic_report.md` for the identified top 3 competitors (if available)

## Workflow

### 1. Identify Top 3 Competitors

If `diagnostic_report.md` exists, use the competitors already identified there.

If not, Google the client's primary keyword (e.g. "physiotherapy [city]") and identify the top 3 competitors appearing in the Map Pack or organic results.

### 2. Fetch Competitor Content

For each competitor, fetch the content from their top-ranking pages:
- Homepage / GBP landing page
- Primary service pages (related to the client's modality)
- Any supporting content pages (FAQs, condition pages, treatment pages)

Use DataForSEO MCP or web search to access competitor content.

**If DataForSEO MCP is not available:**
```
DataForSEO MCP is not configured. To set it up:

Claude Code:   claude mcp add dataforseo -- npx dataforseo-mcp
Claude Desktop: Add to claude_desktop_config.json (see mcp-setup-guide.md)
CoWork:         Add to MCP settings (see mcp-setup-guide.md)

In the meantime, I'll use web search to access competitor page content.
```

### 3. Extract Entities and Concepts

From competitor content, extract entities that prove expertise. These are NOT just keywords. They are the concepts, terms, and references that a genuine expert in this field would naturally include.

Organise into categories:
- **Medical/technical terms:** Clinical terminology, procedure names, diagnostic terms
- **Equipment and tools:** Specific equipment, technology, or tools used in treatment
- **Conditions treated:** Specific conditions, injuries, or health issues addressed
- **Treatment approaches:** Methodologies, techniques, protocols, evidence-based approaches
- **Anatomy references:** Body parts, systems, and anatomical terms relevant to the modality

### 4. Score Entity Frequency

For each entity, note:
- How many of the 3 competitors mention it
- Whether it appears on service pages, supporting content, or both
- Estimated importance (entities all 3 competitors use are likely essential)

### 5. Cross-Reference with Client Content

Compare the entity map against the client's existing website content:
- Which entities does the client already cover well?
- Which entities are completely missing? (These are entity gaps)
- Which entities are mentioned but not developed enough?

Flag the gaps, as these represent the biggest opportunities for content improvement.

### 6. Save Structured Entity Map

Write the entity map with:
- Entity categories and all extracted entities
- Frequency scores (how many competitors use each)
- Gap analysis against client's current content
- Priority entities to incorporate in future content

### 7. Update GMBProjectManagement.md

- Mark "Entity mapping completed" as complete with today's date
- Note the total entity count and number of gaps identified

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| DataForSEO | Competitor page content and SERP data | Web search for competitor content |
| GSC | Client's current indexed content | Skip client content comparison |
| Keywords Everywhere | Entity search volume context | Skip volume data |

## Output

- `[client_folder]/gmb/onboarding/entity_map.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Note: The entity map is referenced automatically by all content-producing skills (service-page-writer, faq-content-builder, neighbourhood-overlay-writer)
