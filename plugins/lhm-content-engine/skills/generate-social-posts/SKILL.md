---
name: generate-social-posts
description: "Generate 3 GMB-style social posts from a finished blog article. Use this when the user mentions 'social posts', 'GMB posts', 'Google Business posts', 'social content from blog', 'generate social', or 'create social posts'. Produces 3 distinct posts (educational hook, problem-focused, quote/bullet style) at 120-200 words each, with emojis, hashtags, and booking CTAs. No exaggerated claims."
---

# Generate Social Posts

Generates 3 GMB-style social media posts from a finished blog article. Each post targets a different engagement style: educational, problem-focused, and quote/bullet format. Posts are formatted for Google Business Profile but work across social platforms.

## When to Use This Skill

- Creating social posts to accompany a published blog article
- Called by the run-batch orchestrator as step 3 per article
- When the user needs social content derived from existing blog content

## Input

```json
{
  "blog_markdown": "",
  "primary_keyword": "",
  "slug": "",
  "client_name": "",
  "client_folder": "/clients/{client-name}/articles/"
}
```

## Instructions

### 1. Load Context

Read `brand-voice.md` from the client folder to match tone.

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

Read `${CLAUDE_PLUGIN_ROOT}/skills/generate-social-posts/LEARNED.md` and apply any relevant entries.

### 2. Analyse the Blog Content

Before writing posts, identify:
- The core educational takeaway
- The primary problem the article addresses
- 2-4 specific facts or tips that stand alone as social content
- The booking/action CTA from the article

### 3. Write Post 1: Educational Hook

**Purpose**: Teach something specific. Stop the scroll with a fact or insight.

Structure:
- Opening line: attention-grabbing educational statement or surprising fact
- 2-4 short paragraphs expanding on the insight
- Emoji use is acceptable (2-4 per post, not excessive)
- Link reference: `[Read more: {link placeholder}]`
- 4-6 relevant hashtags at the end

**Tone**: informative, approachable, professional. Like a clinician explaining something to a friend.

### 4. Write Post 2: Problem-Focused

**Purpose**: Connect with the reader's pain point and guide toward action.

Structure:
- Opening line: describe the problem or frustration the ICP experiences
- 2-4 short paragraphs that validate the problem and introduce the solution path
- Conversion-oriented: guide toward booking or learning more
- Include local relevance where the client context supports it (suburb, city, region)
- Link reference placeholder
- 4-6 relevant hashtags

**Tone**: empathetic, direct, solution-oriented. Acknowledge the struggle before presenting the path forward.

### 5. Write Post 3: Quote-Style or Bullet-Style

**Purpose**: Scannable, shareable content that works in feeds.

Structure (choose one format based on content):

**Quote style**:
- Pull a key statement from the article
- Frame it as authoritative clinic insight
- Brief context below the quote
- CTA to book

**Bullet style**:
- 4-6 bullet points (tips, signs, steps)
- Each bullet is one concise line
- Brief intro above the bullets
- CTA to book below

Both formats: 4-6 hashtags at the end.

### 6. Post Requirements (All 3)

Every post must:
- Be 120-200 words (count carefully)
- Contain no exaggerated medical or recovery claims
- Avoid diagnostic language
- Match the client's brand voice
- Include a booking CTA (not identical across all 3 posts, vary the phrasing)
- Use the primary keyword at least once, naturally
- Follow anti-AI writing guidelines (no rule of 3, no em dashes, no poetic shifts)

## Output

Return a single JSON object:

```json
{
  "social_posts": [
    {
      "label": "01",
      "type": "educational",
      "content": "",
      "word_count": 0
    },
    {
      "label": "02",
      "type": "problem_focused",
      "content": "",
      "word_count": 0
    },
    {
      "label": "03",
      "type": "quote_or_bullet",
      "content": "",
      "word_count": 0
    }
  ]
}
```

## Validation Checkpoints

- [ ] All 3 posts are 120-200 words each
- [ ] Post types are distinct (educational, problem-focused, quote/bullet)
- [ ] No exaggerated medical claims in any post
- [ ] Primary keyword appears naturally in each post
- [ ] Booking CTAs vary across the 3 posts (not copy-pasted)
- [ ] Hashtags are relevant and not excessive (4-6 per post)
- [ ] Brand voice matches client's brand-voice.md
- [ ] Anti-AI guidelines applied (no em dashes, no rule of 3, etc.)
- [ ] Each post can stand alone without the article for context

## Related Skills

- **write-blog** - produces the blog content this skill draws from
- **quality-controller** - reviews and refines these posts
