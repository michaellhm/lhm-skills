---
name: service-page-writer
description: "Write a full service page for a client's GMB optimisation campaign. Use this when the user mentions 'write service page content for [Service] for [Client]', 'write service page', 'create service page', 'service page for [topic]', 'build a service page', or wants to produce a service page as part of Month 1. This skill handles research and context gathering, then hands off to the content-writer agent for the 8-pass writing pipeline."
---

# Service Page Writer

Gathers research, competitor analysis, PAA questions, and local context for a service keyword, builds a structured brief, and hands off to the content-writer agent for 8-pass content generation. The finished page includes SEO metadata, schema markup, and internal linking instructions.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/service-page-writer/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
3. Read `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md`
4. Read `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/service-page.md`
5. Read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md` (if healthcare client)
6. Identify the client and locate their `client_profile.md`
7. Read `[client_folder]/gmb/onboarding/entity_map.md`
8. Read `[client_folder]/gmb/monthly-optimization/YYYY-MM/service_priorities.md`

## Workflow

### 1. Confirm Service and Keyword

Confirm which service page to write. Check `service_priorities.md` for the approved priority services this cycle. If the user hasn't specified, suggest the next unwritten service from the priorities list.

Confirm the primary keyword (e.g. "physiotherapy Geelong", "teeth whitening Brisbane") and the target location.

### 2. Research Phase

**Competitor service pages:**
- Search for the primary keyword in Google (web search)
- Identify the top 3-5 ranking service pages from competitors
- Analyse their content: what sections they cover, what questions they answer, what CTAs they use, approximate word count
- Note what they do well and where they fall short

**PAA questions:**
- Search the service keyword (without location modifier) and collect People Also Ask questions
- Use Keywords Everywhere `get_pasf_keywords` to find additional question-based queries
- Collect 10-15 relevant questions that the service page should address or link to

**Local context:**
- Pull local details from `client_profile.md`: address, suburbs served, landmarks nearby
- Note any location-specific factors that affect the service (e.g. local demographics, climate conditions, common local causes)

**Entity integration:**
- Read `entity_map.md` for expert-level entities and concepts that must appear in the content
- Map which entities fit naturally into which sections

**Keyword data:**
- Use Keywords Everywhere `get_keyword_data` for the primary keyword and 5-8 secondary variations
- Use `get_related_keywords` for additional semantic terms
- Record search volume, CPC, and competition for keyword selection

### 3. Build Structured Brief

Compile research into a structured brief for the content-writer agent:

```
Service: [Service name]
Primary Keyword: [keyword] (volume: X, CPC: $Y)
Secondary Keywords: [list with volumes]
Location: [City/Suburb]
Client: [Name and modality]

Competitor Analysis:
- [Competitor 1]: [strengths, weaknesses, word count]
- [Competitor 2]: [strengths, weaknesses, word count]
- [Competitor 3]: [strengths, weaknesses, word count]

PAA Questions to Address: [list of 5-8 most relevant]
Entity Requirements: [entities from entity map that must appear]
Local Context: [location-specific details to weave in]

Content Direction:
- What this page must do better than competitors: [specifics]
- Target word count: [based on competitor analysis, typically 1500-2500 words]
- Key differentiator for this client: [from client profile]
```

### 4. Hand Off to Content-Writer Agent

Pass the structured brief to the content-writer agent with:
- `content_type`: "service-page"
- `structured_brief`: the research synthesis from step 3
- `client_context`: client_profile.md data
- `target_keyword`: primary keyword
- `location`: city/suburb

The content-writer agent runs the 8-pass pipeline (research synthesis, strategic outline, section drafts, burstiness, perplexity injection, human bookends, conversion injection, final QC) and returns the finished content.

### 5. Receive and Review Content

When the content-writer returns the finished page:
- Verify all entities from the entity map appear naturally
- Verify the primary keyword and secondary keywords are present
- Verify local context is woven in (not just appended)
- Check word count falls within the target range

### 6. AHPRA Compliance Check

If the client is a healthcare provider (check `client_profile.md`):
- Run the content through the AHPRA compliance framework
- Flag any testimonials, before/after claims, superlative claims, or guaranteed outcomes
- Rewrite any flagged sections

### 7. Generate Supporting Assets

Alongside the main content, generate:
- **Title tag**: primary keyword + location + brand, under 60 characters
- **Meta description**: compelling, includes primary keyword, under 160 characters
- **H1 tag**: natural variation of the title tag
- **Service schema markup**: JSON-LD for the service
- **FAQ schema**: if FAQ section is included in the page
- **Internal linking instructions**: what to add to the homepage and category page to link to this new service page, with suggested anchor text

### 8. Present to User

Present the complete service page content to the user for review. Include:
- The full page content
- SEO metadata (title, description, H1)
- Schema markup
- Internal linking instructions
- Word count and keyword usage summary

Ask the user to review and approve, or flag sections for revision.

### 9. Save and Update Project Doc

Save the approved content to `[client_folder]/gmb/monthly-optimization/YYYY-MM/[service-slug].md`.

Update `GMBProjectManagement.md`:
- Mark the service page task as complete with today's date
- Record the output file path
- Add any notes about the content direction or decisions made

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Keywords Everywhere | Keyword data, related keywords, PASF | Web search for keyword ideas; proceed without volume data |
| Web Search | Competitor analysis, PAA questions, local context | Built-in capability |
| GSC | Existing keyword visibility check | Skip; proceed without existing data |

If Keywords Everywhere is not available, display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md` and continue with web search for keyword research. The skill remains functional without it, but keyword volume data will be approximate.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/[service-slug].md` — Full service page content with metadata and schema
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Task marked complete
