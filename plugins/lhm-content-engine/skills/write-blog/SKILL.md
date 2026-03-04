---
name: write-blog
description: "Write a full blog article in Markdown from a structured outline. Use this when the user mentions 'write blog', 'write article', 'write the post', 'generate blog content', 'draft the article', or 'blog from outline'. Takes the JSON outline from generate-outline, applies brand voice and compliance rules, writes the full article with FAQ schema, and returns structured JSON with blog markdown and JSON-LD."
---

# Write Blog

Writes a complete blog article in Markdown from the structured outline produced by generate-outline. Applies brand voice, compliance rules, anti-AI writing guidelines, and produces the article with FAQ JSON-LD schema markup.

## When to Use This Skill

- Writing a blog article from an approved outline
- Called by the run-batch orchestrator as step 2 per article
- When the user has an outline and needs the full article written

## Input

```json
{
  "outline": {
    "slug": "",
    "meta_title": "",
    "meta_description": "",
    "outline": {
      "title": "",
      "sections": []
    },
    "social_angles": [],
    "internal_link_plan": []
  },
  "csv_row": {
    "primary_keyword": "",
    "secondary_keywords": "",
    "word_count": 0,
    "icp": "",
    "intent": ""
  },
  "client_folder": "/clients/{client-name}/articles/"
}
```

## Instructions

### 1. Load Writing Context

Read the following files from the client folder:
- `brand-voice.md` - tone, vocabulary, style rules
- `compliance.md` - medical/legal compliance constraints

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

Read `${CLAUDE_PLUGIN_ROOT}/skills/write-blog/LEARNED.md` and apply any relevant entries.

### 2. Write the Article

Follow the outline structure. Write each section according to its heading, key points, and target word count.

**Article structure pattern** (adapt per outline):

1. **Introduction** - 100-150 words. Hook the reader with a relatable scenario or question relevant to the ICP. Establish the topic. Include the primary keyword within the first 100 words. No "In this article, we'll cover..." framing.

2. **Numbered educational sections** - the bulk of the article. Each section should:
   - Open with a clear, specific statement (not a question followed by its answer)
   - Explain mechanisms in plain language (how the condition works, what the treatment does)
   - Use concrete examples where possible
   - Vary paragraph length (2-4 sentences, not uniform blocks)
   - Include sub-headings (H3) where sections run longer than 250 words

3. **"When not used" or limitations section** - honest discussion of when the treatment or approach may not be appropriate. This builds trust and satisfies AHPRA compliance.

4. **Final thoughts** - 80-120 words. Summarise the key takeaway without repeating the intro. No forced inspirational closing.

5. **Booking CTA** - clear, specific call to action. Reference the clinic name and service. Include a booking link placeholder if available from the internal link plan.

### 3. Keyword Integration

- **Primary keyword**: in H1 (title), first 100 words, at least one H2, and the conclusion. Target 1-2% density.
- **Secondary keywords**: distribute across H2s and body paragraphs. Each secondary keyword should appear 1-2 times naturally.
- **No keyword stuffing** - if a keyword doesn't fit naturally, skip it. Forced keywords read worse than missing ones.

### 4. Internal Link Integration

Using the `internal_link_plan` from the outline:
- Place each link in its designated section
- Use the specified anchor text
- Links should read as natural recommendations, not forced insertions
- Use relative paths (e.g. `/services/physiotherapy`) not absolute URLs
- Only use links provided in the plan. Never guess or fabricate URLs.

### 5. Compliance Check During Writing

As you write each section, verify:
- No promises of outcomes or recovery timelines
- No diagnostic language ("you have X" vs "X is commonly characterised by")
- No comparative claims against other providers or treatments
- No testimonial-style language
- Evidence-based framing where clinical claims are made

### 6. Generate FAQ Schema

Create 4-6 FAQ items based on the article content. Each FAQ should:
- Be a genuine question someone would search for
- Have a direct answer in 40-60 words
- Include the primary or a secondary keyword where natural
- Not repeat the article sections verbatim (rephrase and condense)

Format as JSON-LD:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": ""
      }
    }
  ]
}
```

### 7. Word Count Verification

After writing, verify the total word count meets the target from the CSV row (within 10% tolerance). If under target, expand the sections that have the most room for additional detail. If over target by more than 15%, trim the least essential sections.

## Output

Return a single JSON object:

```json
{
  "blog_markdown": "",
  "faq_schema_json_ld": {},
  "actual_word_count": 0,
  "primary_keyword_count": 0,
  "sections_written": 0
}
```

The `blog_markdown` field contains the full article in Markdown format with:
- H1 title
- H2 section headings
- H3 sub-headings where used
- Internal links as markdown links
- No frontmatter (meta fields are handled separately)

## Validation Checkpoints

- [ ] Article follows the outline structure
- [ ] Word count within 10% of target
- [ ] Primary keyword in title, first 100 words, at least one H2, conclusion
- [ ] Secondary keywords distributed naturally
- [ ] All internal links from plan are placed (none fabricated)
- [ ] No exaggerated medical claims
- [ ] No em dashes
- [ ] No AI pattern phrasing (rule of 3, contrast framing, poetic shifts)
- [ ] FAQ schema has 4-6 questions with 40-60 word answers
- [ ] Brand voice matches client's brand-voice.md

## Related Skills

- **generate-outline** - produces the outline this skill consumes
- **generate-social-posts** - takes the blog content to create social posts
- **quality-controller** - reviews and refines the output of this skill
