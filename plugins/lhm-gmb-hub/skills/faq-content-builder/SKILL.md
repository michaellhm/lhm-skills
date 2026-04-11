---
name: faq-content-builder
description: "Discover real questions people ask about a service and build FAQ/supporting content pages. Use this when the user mentions 'build FAQ content for [Service] for [Client]', 'FAQ pages', 'supporting content', 'PAA content', 'build FAQs', 'questions people ask about [Service]', 'create supporting pages', or wants to produce Month 2 content using the FAQ path. Discovers PAA questions and Reddit questions, then hands to content-writer agent for 8-pass writing."
---

# FAQ Content Builder

Discovers real questions people ask about a service through Google PAA expansion and local Reddit threads, rewords them to avoid duplication flags, prioritises by volume and relevance, and produces full supporting content pages via the content-writer agent. Each page also generates a brief answer and editorial link for the parent service page.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/faq-content-builder/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
3. Read `${CLAUDE_PLUGIN_ROOT}/references/8-pass-writing-engine.md`
4. Read `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/supporting-content.md`
5. Read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md` (if healthcare client)
6. Identify the client and locate their `client_profile.md`
7. Read `[client_folder]/gmb/onboarding/entity_map.md`

## Workflow

### 1. Confirm Service and Context

Confirm which service to build FAQ content for. Check `GMBProjectManagement.md` for which services were optimised in Month 1 and which supporting content tasks are outstanding.

Identify the parent service page URL (the page this FAQ content will link back to and support).

### 2. Question Discovery — Google PAA

Search Google for the service keyword WITHOUT a location modifier (e.g. "physiotherapy" not "physiotherapy Geelong"):
- Expand the People Also Ask section
- Collect 20-30 unique questions
- Note the question phrasing exactly as Google displays it

Use Keywords Everywhere `get_pasf_keywords` for additional question-based queries around the service keyword (request 30 results).

### 3. Question Discovery — Reddit

Search for local Reddit threads where people ask real questions about this service in the client's area:
- Search: `site:reddit.com [service] [city/state]`
- Search: `site:reddit.com [service] Australia` (or relevant country)
- Search: `site:reddit.com recommend [service] [city]`

Collect 5-10 unique questions or discussion topics from Reddit threads. These often reveal questions that PAA misses, particularly around cost, what to expect, and how to choose a provider.

### 4. Reword All Questions

Take every collected question and reword it. Change the phrasing and word order to avoid PAA duplication flags from Google. The meaning stays the same, but the wording is distinct.

Example:
- PAA original: "How long does physiotherapy take to work?"
- Reworded: "When will I notice results from physiotherapy?"

Do this for ALL questions, not just the ones that will become pages. The reworded versions are what appear as page titles and H1s.

### 5. Prioritise and Present

For each reworded question, get search volume data using Keywords Everywhere `get_keyword_data` (batch the questions as keywords).

Rank questions by:
1. Search volume (higher = more valuable)
2. Relevance to the parent service (directly related > tangentially related)
3. Conversion intent (questions from people close to booking > purely informational)

Present the top 6-10 questions to the user in a ranked table:

```
| # | Question | Volume | Relevance | Recommendation |
|---|----------|--------|-----------|---------------|
| 1 | [question] | [vol] | High | Build page |
| 2 | [question] | [vol] | High | Build page |
...
```

Ask the user to select 2-4 questions to build full pages for this cycle.

### 6. Build Content for Each Selected Question

For each user-selected question:

**Build a structured brief:**
- The specific question being answered
- Related sub-questions that should also be addressed
- Relevant entities from the entity map
- Local context from client_profile.md
- The parent service page URL (for linking)
- Target word count: 300-500+ words per page

**Hand off to content-writer agent with:**
- `content_type`: "supporting-content"
- `structured_brief`: the question-specific brief
- `client_context`: client_profile.md data
- `target_keyword`: the reworded question
- `location`: city/suburb

The content-writer runs the 8-pass pipeline and returns finished content.

### 7. Generate Brief Answers and Editorial Links

For each FAQ page, also produce:
- A **brief answer** (2-3 sentences) that summarises the page content
- An **editorial link sentence** that can be added to the parent service page, naturally incorporating a link to the FAQ page

Example:
> Brief answer: "Most people notice improvement from physiotherapy within 4-6 sessions, though chronic conditions may take longer. Your physiotherapist will set specific milestones at your first appointment."
>
> Editorial link for parent page: "If you're wondering when you'll start seeing results, we've written about [how quickly physiotherapy works](/physiotherapy-results-timeline) based on the conditions we treat most often."

### 8. AHPRA Compliance Check

If the client is a healthcare provider:
- Run each page through the AHPRA compliance framework
- Flag and rewrite any non-compliant claims

### 9. Present to User

Present all completed FAQ pages with their brief answers and editorial link text. Ask the user to review and approve.

### 10. Save and Update Project Doc

Save each approved page to `[client_folder]/gmb/monthly-optimization/YYYY-MM/faq-[question-slug].md`.

Update `GMBProjectManagement.md`:
- Mark each FAQ page as a completed sub-task with today's date
- Record the output file paths
- Note the brief answers and editorial links (for when the parent service page is updated)

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Keywords Everywhere | Search volume data, PASF questions | Proceed without volume data; prioritise by relevance only |
| Web Search | PAA expansion, Reddit question discovery | Built-in capability |

If Keywords Everywhere is not available, display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`. The skill can still discover questions through PAA and Reddit, but will lack volume data for prioritisation.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/faq-[question-slug].md` — One file per FAQ page (includes content, metadata, schema)
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Sub-tasks marked complete
