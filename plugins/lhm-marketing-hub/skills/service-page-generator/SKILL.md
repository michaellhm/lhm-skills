---
name: service-page-generator
description: "Generate SEO-optimized service or condition pages for healthcare and service-based businesses. Use this skill when the user mentions 'condition page', 'service page', 'write a service page', 'create a condition page', 'new page for [condition/service]', 'build out a page for [topic]', or wants to create a dedicated website page for a specific service, treatment, or condition. Also trigger when the user provides a client brief and page layout template and wants a full page written. This skill handles the full pipeline: keyword research, page copywriting, anti-AI refinement, citation sourcing, schema markup, and companion blog post recommendations."
---

# Service Page Generator

Generates complete, SEO-optimized service or condition pages from a client brief and page layout template. Handles keyword research, copywriting, citation sourcing, anti-AI writing refinement, schema markup, and companion content recommendations in a single workflow.

## When to Use This Skill

- Client has provided a brief (or you have enough context about the service/condition)
- There's a page layout template to follow (or you'll use the default template in references/)
- The goal is a full website page, not a blog post or article
- The page needs to rank in search engines for the target condition or service

## Inputs

The skill works best with two inputs, but can operate with just one:

1. **Client brief** (required): the subject matter expert's notes on symptoms, causes, treatments, FAQs, and differentiators. This can be a formal brief document, a transcript, or even bullet points from a conversation.
2. **Page layout template** (optional): the HTML/section structure the page should follow. If not provided, use the default template in `references/default-page-template.md`.

If the client brief is missing, gather the essential information by asking the user directly. Don't proceed to writing without understanding: what the condition/service is, who the target patient/client is, what treatments or approaches the business offers, and what makes them different.

## Mandatory: Route Long-Form Writing Through content-writer Agent

Long-form content (over 300 words or page-level web/blog copy) goes through the 8-pass pipeline. This skill is responsible for:

1. Research and brief construction
2. Outline planning
3. Building a `structured_brief` for the content-writer (target keyword, intent, outline, internal/external link targets, client voice notes from `client_profile.md` or product marketing context)
4. Calling the content-writer agent with `content_type: "page-copy"` and the structured brief
5. Saving returned content to the agreed output path
6. Final SEO validation (primary keyword density, internal link count, meta description) where applicable

Do not generate the body content directly. Delegate to content-writer.

## Workflow

Follow these steps in order. Each step builds on the previous one.

### Step 1: Keyword Research

Before writing a single word of copy, build a keyword map. The page needs to be grounded in what people actually search for.

**Using Keywords Everywhere (required):**
- Start with the primary condition/service term (e.g. "lower back pain", "teeth whitening", "couples counselling")
- Pull related keywords using `get_related_keywords` (30 results)
- Get volume, CPC, and competition data for 8-12 candidate keywords using `get_keyword_data` with country set to the client's market (usually `au` for Australian clients)
- Look for PASF (People Also Search For) terms using `get_pasf_keywords` for FAQ and long-tail opportunities

**Using Google Search Console (if available):**
- Check `get_search_analytics` for the client's domain to see if they have any existing visibility for the target terms
- Check `get_search_by_page_query` if a related page already exists
- This reveals where the client sits today and what gap the new page needs to fill

**Keyword Selection:**
Organise findings into:
- **Primary keyword**: highest volume, broadest match for the page topic (goes in H1, title, intro, conclusion)
- **Secondary keywords** (4-8): related terms with meaningful search volume (woven into H2s and body copy)
- **Long-tail / FAQ keywords**: question-based queries and specific variants (used in FAQ section and subsections)
- **Local modifiers**: suburb, city, or region terms relevant to the business (used in CTAs and location sections)

Present the keyword research summary to the user before proceeding to writing. This is a checkpoint. The user may want to adjust targeting, exclude certain terms (e.g. "exercises" if they don't want to give away the service for free), or add terms you missed.

### Step 2: Write the Page

Read the page layout template (either the user-provided one or `references/default-page-template.md`) and follow its section structure exactly. The template defines what sections appear and in what order. Your job is to fill each section with copy that integrates the keyword research and client brief.

**General writing principles:**

The copy should sound like it was written by a knowledgeable practitioner who genuinely cares about helping people, not by a marketing agency. Use second person ("you", "your") for the reader and first person plural ("we", "our") for the business. Keep sentences varied in length. Mix short punchy statements with longer explanatory ones.

Avoid the trap of writing generic health content that could appear on any website. The client brief exists because the business has specific opinions, approaches, and differentiators. Weave those in. If the physio uses AXIT technology, mention it. If the psychologist specialises in EMDR, explain it. The brief is the source of truth for what makes this page different from the 50 other pages ranking for the same keyword.

**Section-by-section guidance:**

**Header / Hero:** Lead with the condition or service name. The opening paragraph should acknowledge the reader's pain point or situation, state what the business does about it, and set the tone for the rest of the page. Include the primary keyword in the first 100 words. Keep it to 2-4 short paragraphs.

**What Is [Condition] / About [Service]:** Define the condition or service in plain language. Include prevalence stats where available (these become citation opportunities). Reassure the reader where appropriate. Don't make this section too long; readers scanning the page will skip past lengthy definitions.

**Symptoms / What to Expect:** Use a bullet list for symptoms or service features. Keep each bullet to one line where possible. Add a subsection for any important variants (e.g. nerve-related symptoms for back pain, different types of anxiety for a psychology page).

**Causes / Why This Happens:** Use bold subheadings for each cause or factor. Write 2-4 sentences per cause. This is where you earn the reader's trust by showing depth of understanding. Connect causes back to what the business can do about them.

**Types / Variations:** If the condition or service has distinct categories, cover them here. Keep descriptions concise. This section helps capture long-tail keyword variants.

**FAQ Section:** Write 5-7 questions and answers. Pull questions from: the client brief (myths and misconceptions make great FAQs), PASF keyword research, and common questions you'd expect a patient or client to ask before booking. Answers should be 40-80 words each. Direct, factual, reassuring. Format as bold question followed by answer paragraph.

**How [Business] Can Help / Treatment Approach:** This is the most important section for conversion. Structure it as subsections (H3s) covering: assessment approach, treatment methods, specific programs or services, education and self-management guidance, and return-to-activity or ongoing support. Reference specific equipment, techniques, and approaches from the client brief. This section should feel specific to the business, not generic.

**Risk Factors / Who This Affects:** Optional section. Include if the client brief covers risk factors. Split into modifiable and non-modifiable where relevant.

**Self-Management / What You Can Do:** Brief guidance on what the reader can do between appointments or before booking. Keep this practical and specific. Don't turn it into a substitute for the service (the user may specifically want to avoid giving away free advice).

**When to Seek Help:** Clear triggers for booking. Include a separate subsection for red flags or urgent situations if clinically relevant.

**Location CTA:** Mention the business location, surrounding suburbs or service area, and include a clear booking CTA. This section supports local SEO.

**Footer CTA:** A catch-all for readers who aren't sure if this page is relevant to them. Reassure them that they don't need a diagnosis to book.

### Step 3: Add Citations and References

After writing the page, search for authoritative sources to cite inline. The goal is 4-8 citations from credible sources. These build E-E-A-T signals and give the page substance.

**Where to look:**
- Government health bodies (AIHW, NHS, CDC, WHO)
- Professional associations (APA, ADA, APS, relevant college or society)
- Clinical guidelines and care standards
- Peer-reviewed research (PubMed, PMC) for specific claims
- Peak industry bodies (e.g. Painaustralia, Cancer Council, Heart Foundation)

**How to cite:**
- Use inline markdown links in the page copy: `[anchor text](URL)`
- Add a numbered References section at the bottom of the page (before schema markup)
- Link the most important stats and claims (prevalence data, guideline recommendations, research findings)
- Don't over-cite. 4-8 well-placed citations are better than 15 scattered ones.

Use `WebSearch` to find sources. Search for: `[condition] statistics [country] site:gov.au OR site:org.au` and `[condition] clinical guidelines [professional association]`.

### Step 4: Anti-AI Writing Refinement

Run a systematic check against common AI writing patterns. This step catches things that make the page sound machine-generated.

Use `references/anti-ai-checklist.md` for the full checklist. The key checks are:

1. **Em dashes**: Search for `—` in the copy. Replace with commas, periods, or parentheses.
2. **Rule of 3**: Look for lists or examples that consistently group in threes. Vary the count.
3. **Contrast framing**: Find "While X, Y" or "Although X, Y" constructions. Rewrite to remove the artificial tension.
4. **Poetic shifts**: Remove "In a world where...", "In an era of...", "In today's..." openers.
5. **Adverb overuse**: Check frequency of -ly adverbs. If any appears 3+ times, reduce to 1-2.
6. **Marketing clichés**: Remove "seamless", "robust", "holistic", "cutting-edge", "comprehensive care", "state-of-the-art".
7. **Formulaic transitions**: Remove "Let's explore", "Let's dive into", "Now, let's turn to".
8. **Forced inspirational endings**: Remove "journey", "empower", "transform", "unlock", "embrace" from paragraph endings.

Run these checks programmatically using grep/bash, not by eyeballing. Report what was found and what was fixed.

### Step 5: Schema Markup

Generate JSON-LD schema for the page:

1. **FAQPage schema**: Convert all FAQ questions and answers into structured data.
2. **LocalBusiness or MedicalBusiness schema**: Include business name, address, phone, opening hours, service area, and medical specialty where applicable.

Include both schemas at the bottom of the output file.

### Step 6: SEO Score and Keyword Map

Add a final section to the output with:

- On-page SEO checklist (title, meta description, H1, keyword placement, internal links, external links, FAQ, word count)
- Keyword integration summary showing where each target keyword was used
- Overall SEO score out of 10

### Step 7: Companion Blog Post Recommendations

Create a separate file with 2-4 blog post recommendations that support the service page. Each recommendation should include:

- Post title
- Primary keyword and AU search volume
- Secondary keywords
- Search intent classification
- Target word count
- Suggested slug
- Why this post (strategic rationale)
- Suggested angle (what makes it different from competing content)
- Internal link strategy (how it connects back to the service page)

**Important filter:** Prioritise blog topics with commercial or investigation intent. Topics where the reader is worried, confused, or actively considering professional help convert better than purely informational topics. Avoid topics that substitute for the service (e.g. "exercises you can do at home" for a physio clinic) unless the user specifically wants that.

End the recommendations file with a cluster summary table showing all posts, their keywords, volume, intent, and priority.

## Output Structure

Save all outputs to the client's folder under a skill-specific subfolder:

```
[client-folder]/content/YYYY-MM/
├── [condition]-service-page.md        (the full page with meta, copy, schema, SEO score)
└── [condition]-blog-recommendations.md (companion blog post recommendations)
```

## Meta Tag Format

Include a META table at the top of the service page:

| Field | Value |
|-------|-------|
| **META Title** | [Primary Keyword] Support in [Location] | [Business Name] |
| **META Description** | [150-160 chars, includes primary keyword, value proposition, CTA] |
| **Target Keywords** | [comma-separated list of all target keywords] |
| **Slug** | /conditions/[slug] or /services/[slug] |
| **Existing Page** | [URL if replacing existing page, or N/A] |

Meta title should be under 60 characters. Meta description should be 150-160 characters and include the primary keyword, what the business does, and a call to action.

## Quality Standards

- Word count: 2,000-3,000 words for the page copy (excluding schema and SEO score sections)
- FAQ: minimum 5 questions
- Citations: 4-8 inline citations from authoritative sources
- Schema: FAQPage + LocalBusiness/MedicalBusiness JSON-LD
- Anti-AI check: all 8 pattern checks must pass before delivery
- Keyword density: primary keyword at 1-2%, secondary keywords present in relevant H2/H3 sections

## Tips

- Read the client brief carefully. The differentiators are in there. A generic page that doesn't reflect the specific business is a wasted page.
- Don't frontload every section with the primary keyword. Use it in the H1, intro, one H2, and conclusion. Let secondary keywords carry the other sections.
- The FAQ section is one of the highest-value sections for SEO. Questions map directly to "People Also Ask" features in Google. Write answers that could be pulled as featured snippets (40-60 words, direct answer first).
- Local suburbs and service area mentions in the location CTA section help with local search visibility. Don't force them into the main copy.
- When the user gives feedback like "don't include exercises" or "I don't want to give away the service for free", that's a strategic filter for the blog recommendations too. Apply it consistently.

## Related Skills

- **keyword-research**: for deeper keyword discovery beyond what this skill covers
- **seo-content-writer**: for blog posts recommended by this skill
- **meta-tags-optimizer**: for refining meta tags after the page is written
- **content-quality-auditor**: for a full CORE-EEAT audit of the finished page
- **schema-markup**: for additional schema types beyond FAQ and LocalBusiness
- **geo-content-optimizer**: for optimising the page for AI citations
