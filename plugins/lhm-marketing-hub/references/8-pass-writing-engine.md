# 8-Pass Human-Like Writing Engine

This document defines the writing pipeline used by the content-writer agent for ALL long-form content produced by this plugin. No content-producing skill should generate content in a single pass. Every piece of content goes through all 8 passes.

## Why 8 Passes?

One prompt, one model, one pass produces content that reads like AI wrote it, because it did. One consistent tone, predictable sentence lengths, robotic rhythm. That is not how humans write.

Humans write section by section. They take breaks. They come back. The tone shifts slightly between sections. Sentence lengths vary. The 8-pass pipeline mimics this natural variation.

## Content Guardrails

Before every pass, load the content-type-specific guardrail file:

- Service pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/service-page.md`
- Category pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/category-page.md`
- Location/geo pages: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/location-page.md`
- Supporting/FAQ content: `${CLAUDE_PLUGIN_ROOT}/references/content-guardrails/supporting-content.md`

Also load: `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`

The guardrail prompt sits on top of every pass to prevent the writing from drifting off-brief.

---

## Pass 1: Research Synthesis

**Input:** Raw research from the calling skill (PAA questions, Reddit threads, competitor page content, local landmarks, entity map entries, search volume data)

**Output:** A structured content brief

**What this pass does:**

Takes all of the raw research and compresses it into a focused writing plan:
- What specific questions does this page need to answer?
- What local details should be woven into the content?
- What angles are competitors covering that we need to cover better?
- What entities from the entity map must appear naturally?
- What is the primary search intent we're targeting?
- What makes this page distinct from every other page on the internet about this topic?

The brief should be 200-400 words. It is the foundation for every subsequent pass.

---

## Pass 2: Strategic Outline

**Input:** The content brief from Pass 1

**Output:** Full page architecture

**What this pass does:**

Builds the page structure from the brief:
- Every H2 heading with its specific angle
- What each section needs to accomplish (not just a topic, but the goal)
- How sections connect to each other (the logical flow from top to bottom)
- Where CTAs should appear naturally
- Where local details should be concentrated
- Approximate word count per section

This is NOT just a list of headings. It maps the logical progression of the entire page. Most AI tools skip this step and just start writing, which is why their content wanders.

---

## Pass 3: Section Draft (Independent Calls)

**Input:** The outline from Pass 2 + content brief from Pass 1 + guardrails

**Output:** First draft of each section

**What this pass does:**

Each H2 section is written with a SEPARATE, INDEPENDENT call. For each section:

1. Load the content brief and guardrails
2. Load ONLY this section's context from the outline (what it needs to accomplish, its angle)
3. Load the preceding section's final paragraph (for transition continuity only)
4. Write JUST this section (target word count from outline)
5. Do NOT reference other sections' exact wording

The separate calls produce slightly different tone, energy, and word choice per section. This mimics how a real writer drafts an article over the course of a day, coming back to each section with fresh energy.

**Implementation note:** Use separate tool calls or separate prompt constructions for each section. The point is that each section gets its own generation context.

---

## Pass 4: Burstiness

**Input:** The assembled first draft (all sections combined)

**Output:** Draft with varied rhythm

**What this pass does:**

AI typically writes in a consistent rhythm. Sentences tend to be about the same length. Paragraphs follow the same cadence. Humans don't write this way.

This pass goes through the entire draft and:
- Varies sentence length: long sentence, then short. Then two medium. Then a fragment.
- Mixes paragraph lengths: a 4-sentence paragraph, then a 1-sentence paragraph, then 3 sentences
- Breaks up any sequences of similarly-structured sentences
- Adds the kind of irregular pacing that makes content feel alive

**Do NOT change the meaning or content.** Only adjust rhythm and structure.

---

## Pass 5: Perplexity Injection

**Input:** The burstiness-adjusted draft

**Output:** Draft with AI patterns removed

**What this pass does:**

Finds predictable AI word patterns and replaces them with words a human would actually use. AI has favourite words and constructions that immediately flag content as machine-generated.

**Kill these words/patterns:**
- "robust" → specific alternative (e.g. "solid", "reliable", or just remove)
- "leverage" → "use", "apply", or rephrase
- "streamline" → "simplify", "speed up", or specific description
- "comprehensive" → "full", "complete", or just remove
- "utilize" → "use"
- "facilitate" → "help", "support", or rephrase
- "significant improvements" → specific description of what improved
- "ensure" → "make sure", "check", or rephrase
- "delve into" → remove or rephrase
- "it's important to note" → remove (just state the thing)
- "in today's [noun]" → remove or be specific
- "whether you're [X] or [Y]" → remove or rephrase
- Em dashes (—) → replace with commas, periods, or parentheses

**Also check against:** `anti-ai-writing-guidelines.json` for the full pattern list.

**Do NOT change the meaning.** Same information, different word choice.

---

## Pass 6: Human Bookends

**Input:** The perplexity-adjusted draft

**Output:** Draft with rewritten opening and closing

**What this pass does:**

Rewrites the FIRST 2 sentences and LAST 2 sentences of the article with extremely conversational, opinionated language. These sentences matter more than the rest of the article combined because:

1. Google's algorithm weighs the opening and closing most heavily
2. AI systems (ChatGPT, Perplexity, etc.) weight the opening when deciding to cite content
3. Searchers read the first couple of sentences, then scroll to the bottom and read the last couple

**Opening sentences must:**
- Address the reader's immediate problem directly
- Sound like a real person talking, not a textbook
- Contain an opinion or perspective (not just facts)
- Be specific to the local area where possible

**Closing sentences must:**
- Circle back to the reader's problem
- Include a natural call to action
- Sound conversational, not like a corporate sign-off
- NOT be a generic "Contact us today!" type ending

---

## Pass 7: Conversion Injection

**Input:** The bookends-adjusted draft

**Output:** Draft with natural CTAs and conversion elements

**What this pass does:**

Goes through the content and naturally injects calls to action, phone numbers, and conversational urgency. Not spammy. Not banner ads dropped in the middle of paragraphs. The kind of lines that make someone stop reading and pick up the phone.

**This pass is DIFFERENT for each content type:**

**Service pages:** Direct CTAs, click to call, get directions, book online. Multiple touchpoints throughout. Phone number in at least 2 places. "If you're dealing with [problem], give us a call on [number]" type language woven into the content.

**Location/geo pages:** Local-specific CTAs with driving directions or proximity references. "We're a [X] minute drive from [landmark]" type language. Local phone number prominent.

**FAQ/supporting pages:** Soft CTAs linking back to the parent service page. "If you'd like to discuss your specific situation, see our [service] page or call us on [number]." Less aggressive, more helpful.

**Category pages:** Editorial links to child service pages with action-oriented language. "Ready to explore [sub-service]? Here's what to expect" type transitions.

**Do NOT:**
- Drop a CTA box in the middle of a paragraph
- Use "Contact us today!" or "Don't wait!" type language
- Add more than 3-4 conversion touchpoints per page
- Make every paragraph end with a CTA

---

## Pass 8: Final QC

**Input:** The conversion-adjusted draft

**Output:** Final content ready for delivery

**What this pass does:**

Evaluates the ENTIRE article as a whole:

1. **Cohesion check:** Do sections flow together despite being written independently? Fix any jarring transitions.
2. **Brief adherence:** Does the content cover everything from the original content brief (Pass 1)? Flag and fill any gaps.
3. **Outline adherence:** Does the structure match the strategic outline (Pass 2)? Fix any drift.
4. **Word count check:** Is the total within the target range for this content type?
   - Service pages: 1,500-2,500 words
   - Location/geo pages: 800-1,500 words
   - FAQ/supporting pages: 400-800 words
   - Category pages: 1,000-1,800 words
5. **AI pattern scan:** Any leftover AI patterns that slipped through Passes 4-5? Fix them.
6. **AHPRA compliance:** For healthcare clients, run final compliance sweep against the AHPRA framework.
7. **Anti-AI guidelines:** Final check against all 10 rules from anti-ai-writing-guidelines.json.
8. **Entity check:** Did the required entities from the entity map appear naturally? Add any missing ones.
9. **Local check:** Does the content sound genuinely local? Or could this page be about any city?

Anything that doesn't meet standard gets rewritten in this pass. This is the quality control layer that catches what the other seven passes may have missed.

---

## Parallel Steps (Generated Alongside Pass 8)

These are produced at the same time as the final QC:

### Meta Tags
- **Title tag:** [Service/Topic] [City] | [Brand Name] (max 60 chars)
- **Meta description:** Action-oriented, includes keyword, max 155 chars
- **H1:** Natural variation of the title tag

### FAQ Section
- 3-5 questions with concise answers
- Based on PAA research from the content brief
- Formatted for FAQ schema markup

### Schema Markup
- **Service pages:** Service schema (serviceType, provider, areaServed)
- **Location pages:** LocalBusiness schema (address, geo, openingHours)
- **FAQ pages:** FAQPage schema (mainEntity array)
- Output as JSON-LD ready for insertion

### External Authority Links
- 2-3 outbound links to authoritative sources
- Government health sites, peak body websites, published research
- Natural anchor text, placed where they add genuine value
- Do NOT link to competitors

### Image Prompts
- 1-2 image descriptions per major section
- Describe what the image should show (for manual sourcing or AI generation)
- Prefer: clinic/practice photos, equipment, team at work, local area shots
- Avoid: generic stock photo descriptions

---

## Content-Writer Agent Handoff Protocol

When a skill calls the content-writer agent, it provides:

```
content_type: "service-page" | "category-page" | "location-page" | "supporting-content"
structured_brief: {
  target_keyword: "[primary keyword]",
  location: "[city/suburb]",
  client_name: "[business name]",
  client_phone: "[phone number]",
  client_address: "[address]",
  entity_map: [list of entities to include],
  research: {
    paa_questions: [...],
    competitor_angles: [...],
    local_context: [...],
    reddit_questions: [...]
  },
  parent_service_page: "[URL, if applicable]",
  word_count_target: [number],
  ahpra_required: true/false
}
```

The content-writer agent returns:

```
content_markdown: "[full page content in markdown]",
meta_title: "[title tag]",
meta_description: "[meta description]",
h1: "[H1 heading]",
faq_section: "[FAQ markdown]",
schema_json_ld: "[JSON-LD schema markup]",
external_links: [{url, anchor_text, placement}],
image_prompts: [{section, description}],
word_count: [actual count],
passes_completed: 8
```
