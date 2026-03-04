---
name: generate-outline
description: "Generate a structured article outline from an approved CSV row and client context files. Use this when the user mentions 'generate outline', 'create outline', 'article outline', 'plan the article', 'outline from CSV', or 'topic outline'. Reads client-background.md, brand-voice.md, compliance.md, published-articles.json, and the brief file. Detects topic overlap, aligns to ICP and search intent, avoids cannibalisation, and outputs structured JSON with slug, meta fields, section outline, social angles, and internal link plan."
---

# Generate Outline

Generates a structured article outline from an approved CSV row and client context files. Detects topic overlap with published content, aligns to the target ICP and search intent, avoids cannibalisation, and produces a JSON outline ready for the write-blog skill.

## When to Use This Skill

- Processing an approved row from the content CSV
- Planning a new article for an allied health client
- Creating an outline before writing begins
- Called by the run-batch orchestrator as step 1 per article

## Input

This skill expects a JSON object with the following structure:

```json
{
  "csv_row": {
    "client_name": "",
    "topic": "",
    "primary_keyword": "",
    "secondary_keywords": "",
    "icp": "",
    "intent": "",
    "word_count": 0,
    "internal_links": "",
    "brief_filename": "",
    "status": "Approved"
  },
  "client_folder": "/clients/{client-name}/articles/"
}
```

## Instructions

### 1. Load Client Context

Read the following files from the client folder. If any required file is missing, halt and report which file is absent.

- `client-background.md` - business overview, services, locations
- `brand-voice.md` - tone, vocabulary, style preferences
- `compliance.md` - client-specific compliance rules
- `published-articles.json` - array of published article slugs and topics
- `briefs/{brief_filename}` - the specific brief for this article

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` before producing any text.

Read `${CLAUDE_PLUGIN_ROOT}/skills/generate-outline/LEARNED.md` and apply any relevant entries.

### 2. Detect Topic Overlap

Compare the current topic and primary keyword against every entry in `published-articles.json`.

Check for:
- **Exact match** - same primary keyword already published (halt and flag)
- **Semantic overlap** - closely related topic that could cannibalise rankings
- **Complementary angle** - related topic that can cross-link without competing

If exact match found: halt processing for this row, set status recommendation to "Duplicate - Needs Review", and return error JSON.

If semantic overlap found: note it in the outline and adjust the angle to differentiate.

### 3. Align to ICP and Search Intent

Using the `icp` field from the CSV row:
- Frame the outline for that specific audience segment
- Choose language complexity appropriate to the ICP
- Select section topics that address ICP pain points and questions

Using the `intent` field:
- **Informational** - structure as educational content, mechanism explanations, "what to expect" framing
- **Commercial** - include comparison elements, service positioning, decision-support sections
- **Transactional** - shorter, action-oriented, clear booking CTAs
- **Navigational** - service-specific, location-aware, direct answers

### 4. Build the Outline Structure

Structure the article following this pattern (adjust based on topic and intent):

1. **Introduction** - hook relevant to ICP, establish the problem or question
2. **Numbered educational sections** - mechanism explanations, what the condition/treatment involves
3. **"When this applies" section** - who benefits, when to seek treatment
4. **"When this may not apply" section** - honest limitations, when to consider alternatives
5. **Practical guidance** - what to expect, preparation, recovery considerations
6. **Final thoughts** - summary without being repetitive
7. **Booking CTA** - clear call to action at the end

Vary the number of sections based on word count target. Do not force every article into the same structure.

### 5. Generate Slug

Rules:
- Lowercase
- Hyphenated (replace spaces with hyphens)
- Maximum 60 characters
- No stop words unless needed for clarity
- Clean and human-readable
- Include primary keyword where natural

### 6. Generate Meta Fields

**Meta title**:
- Maximum 60 characters
- Include primary keyword (preferably near the start)
- Natural language, not keyword-stuffed
- No exaggerated claims

**Meta description**:
- 140-160 characters
- Include primary keyword
- Compelling value proposition
- No exclamation marks or superlatives

### 7. Plan Social Angles

Identify 2-4 social post angles derived from the article content. Each angle should target a different engagement type:
- Educational hook
- Problem/solution framing
- Practical tip or takeaway
- Quote-worthy statement from the article

### 8. Plan Internal Links

Using the `internal_links` field from the CSV and the `services.json` file:
- Map which internal links should appear in which sections
- Only use links confirmed in the client's context files
- Never hallucinate or guess internal URLs
- Suggest anchor text that reads naturally

## Output

Return a single JSON object. No markdown wrapping, no commentary outside the JSON.

```json
{
  "slug": "",
  "meta_title": "",
  "meta_description": "",
  "outline": {
    "title": "",
    "sections": [
      {
        "heading": "",
        "type": "h2",
        "key_points": [],
        "target_word_count": 0,
        "keywords_to_include": []
      }
    ]
  },
  "social_angles": [
    {
      "angle": "",
      "type": "educational | problem_solution | tip | quote"
    }
  ],
  "internal_link_plan": [
    {
      "url": "",
      "anchor_text": "",
      "target_section": ""
    }
  ]
}
```

## Error Output

If the skill cannot proceed, return:

```json
{
  "error": true,
  "reason": "",
  "recommendation": ""
}
```

## Validation Checkpoints

- [ ] All required client files loaded successfully
- [ ] No exact keyword match with published articles
- [ ] Outline aligns to specified ICP
- [ ] Outline matches search intent type
- [ ] Slug is under 60 characters, lowercase, hyphenated
- [ ] Meta title is under 60 characters with primary keyword
- [ ] Meta description is 140-160 characters
- [ ] Internal links are all verified from client context
- [ ] No exaggerated medical claims in any text

## Related Skills

- **write-blog** - takes this outline as input to write the full article
- **run-batch** - orchestrates this skill as step 1 per CSV row
