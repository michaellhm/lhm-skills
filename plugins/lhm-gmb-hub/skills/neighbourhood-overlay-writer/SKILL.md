---
name: neighbourhood-overlay-writer
description: "Write hyper-local neighbourhood overlay pages targeting specific suburbs and landmarks near a client's business. Use this when the user mentions 'write neighbourhood overlay pages', 'overlay pages', 'geo pages', 'location pages', 'neighbourhood pages', 'suburb pages', 'areas we serve pages', or wants to produce Month 2 content using the overlay/proximity path. Uses Local Falcon grid data to identify yellow grid points (positions 4-6) and targets nearby landmarks."
---

# Neighbourhood Overlay Writer

Uses Local Falcon scan data to identify grid points where the client ranks 4th-6th (the "yellow zone" easiest to push into top 3), finds Google Maps landmarks near those points, and produces hyper-local location pages via the content-writer agent. Each page targets a specific "[Service] near [Landmark] in [City]" keyword and includes real neighbourhood details, not generic suburb-swapped templates.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/neighbourhood-overlay-writer/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
3. Read `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md`
4. Read `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/location-page.md`
5. Read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md` (if healthcare client)
6. Identify the client and locate their `client_profile.md`
7. Read `[client_folder]/gmb/onboarding/entity_map.md`

## Workflow

### 1. Get Local Falcon Grid Data

Attempt to retrieve the Local Falcon scan report for the primary service keyword.

**If Local Falcon MCP is available:**
- Pull the most recent grid scan for the service keyword
- Identify all grid points with positions 4, 5, or 6 (the yellow zone)
- Record the geographic coordinates of each yellow point

**If Local Falcon MCP is NOT available:**
- Display MCP setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`
- Ask the user: "Can you share your Local Falcon scan results? I need to know which grid points show positions 4-6 for [keyword]. Alternatively, tell me which suburbs or areas around [business location] you'd like to target."
- If the user provides manual input, proceed with that data

### 2. Identify Landmarks Near Yellow Points

For each yellow grid point (or user-specified suburb):
- Search Google Maps for notable landmarks near the coordinates: suburbs, parks, shopping centres, schools, major intersections, train stations, hospitals, sporting complexes
- Record each landmark with its approximate distance from the client's business
- Note which service keyword + landmark combinations make viable page targets

### 3. Present Target Options

Compile 10-20 potential overlay targets in a table:

```
| # | Landmark/Area | Grid Position | Distance | Suggested Page Title |
|---|--------------|---------------|----------|---------------------|
| 1 | [Landmark] | Pos 5 | 3.2km | [Service] near [Landmark] in [City] |
| 2 | [Suburb] | Pos 4 | 2.8km | [Service] in [Suburb] |
...
```

Present to the user and ask them to select 3-5 targets to build pages for.

### 4. Research Each Selected Target

For each user-selected target:

**Local area research:**
- Demographics of the neighbourhood (population, age distribution, household types)
- Local conditions relevant to the service (e.g. sporting clubs nearby for a physiotherapy client, schools for a paediatric dentist)
- Driving routes from the landmark to the client's business (with approximate travel time)
- Parking availability near the client's location
- Public transport options from that area

**Keyword data:**
- Use Keywords Everywhere `get_keyword_data` for "[service] near [landmark]", "[service] [suburb]", and related variants
- Record search volumes where available

### 5. Build Briefs and Generate Content

For each selected target, build a structured brief:

```
Target: [Service] near [Landmark] in [City]
Primary Keyword: [keyword]
Landmark/Area: [Landmark name and details]
Distance from Business: [X km, Y min drive]

Local Context:
- Demographics: [area demographics]
- Relevant local conditions: [specifics]
- Driving route: [from landmark to business]
- Parking/transport: [details]

Entity Requirements: [from entity map]
Parent Service Page: [URL to link back to]
```

Hand off to content-writer agent with:
- `content_type`: "location-page"
- `structured_brief`: the location-specific brief
- `client_context`: client_profile.md data
- `target_keyword`: "[service] near [landmark] in [city]"
- `location`: specific suburb/landmark area

The content-writer runs the 8-pass pipeline. Location page guardrails ensure the content is genuinely local (not a service page with a suburb name swapped in).

### 6. AHPRA Compliance Check

If the client is a healthcare provider:
- Run each page through the AHPRA compliance framework
- Flag and rewrite any non-compliant sections

### 7. Generate Internal Linking Instructions

For each overlay page, produce:
- Link instructions for the "Areas We Serve" page (add this suburb/landmark with a link)
- Link back to the parent service page with natural anchor text
- Cross-links between overlay pages where geographically relevant (e.g. nearby suburbs can reference each other)

### 8. Present to User

Present all completed overlay pages with their linking instructions. Ask the user to review and approve.

### 9. Save and Update Project Doc

Save each approved page to `[client_folder]/gmb/monthly-optimization/YYYY-MM/[service]-near-[landmark-slug].md`.

Update `GMBProjectManagement.md`:
- Mark each overlay page as a completed sub-task with today's date
- Record the output file paths
- Note the internal linking instructions for implementation

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Local Falcon | Grid scan data to identify yellow (4-6) positions | Ask user to provide scan results manually or specify target suburbs |
| Keywords Everywhere | Keyword volume for location-based terms | Proceed without volume data |
| Web Search | Local area research, demographics, landmarks | Built-in capability |

If Local Falcon is not available, the skill can still run with user-supplied suburb/area targets. Display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/[service]-near-[landmark-slug].md` — One file per overlay page (includes content, metadata, schema, linking instructions)
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Sub-tasks marked complete
