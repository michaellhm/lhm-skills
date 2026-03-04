---
name: quality-controller
description: "Apply anti-AI refinement, compliance review, and quality control to blog content and social posts. Use this when the user mentions 'quality check', 'quality control', 'anti-AI pass', 'compliance review', 'refine content', 'content QA', or 'review for AI patterns'. Removes repetitive phrasing, breaks AI sentence rhythm, enforces compliance, ensures distinct positioning from published articles, and outputs a compliance confidence score (high/medium/low). Halts publishing if confidence is low."
---

# Quality Controller

Applies anti-AI refinement, compliance review, and quality control to blog articles and social posts. This is the final content gate before publishing. Removes AI writing patterns, verifies medical compliance, ensures the content is distinct from published articles, and assigns a compliance confidence score.

## When to Use This Skill

- After blog and social posts are written, before publishing
- Called by the run-batch orchestrator as step 4 per article
- When the user wants a quality and compliance review of content
- When content needs anti-AI refinement

## Input

```json
{
  "blog_markdown": "",
  "social_posts": [],
  "faq_schema_json_ld": {},
  "client_folder": "/clients/{client-name}/articles/"
}
```

## Instructions

### 1. Load Review Context

Read the following files from the client folder:
- `compliance.md` - client-specific compliance rules
- `anti-ai-writing.json` - client-specific anti-AI overrides (if exists, otherwise use plugin default)
- `published-articles.json` - previously published articles for distinctness check

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

Read `${CLAUDE_PLUGIN_ROOT}/skills/quality-controller/LEARNED.md` and apply any relevant entries.

### 2. Anti-AI Refinement Pass

Scan the blog markdown and all social posts for these patterns and fix each one found:

**Structural patterns**:
- Rule of 3 violations: ideas grouped in triplets. Regroup into 2, 4, or asymmetric structures.
- Uniform paragraph length: all paragraphs roughly the same size. Vary them.
- Odd-numbered structure: exactly 5, 7, or 9 paragraphs. Adjust section count.

**Phrasing patterns**:
- Contrast framing: "while X, Y" and "although X, Y" constructions. Rewrite as direct statements.
- Poetic shift phrases: "in a world where," "in an era of," "in a landscape defined by." Remove entirely.
- Hypophora: question immediately followed by its answer. Separate or restructure.
- Formulaic transitions: "Let's explore," "Let's dive into," "Now, let's turn to." Replace with natural connectors.
- Forced inspirational endings: vague emotional statements at paragraph ends. Replace with substantive points.
- Em dashes: replace all with commas, periods, or parentheses.
- Excessive -ly adverbs: significantly, dramatically, effectively, incredibly, remarkably. Replace with stronger verbs.
- Marketing cliches: "seamless," "robust," "game-changing," "cutting-edge," "holistic approach." Replace with specific language.

**Rhythm patterns**:
- Sentences all similar length. Vary sentence length within paragraphs.
- Every paragraph starts the same way. Vary opening structures.
- Predictable cadence (short-medium-long repeating). Break the pattern.

### 3. Compliance Review

Check every sentence in the blog and social posts against:

**AHPRA compliance**:
- No guaranteed outcomes ("will fix," "cures," "eliminates")
- No specific recovery timelines ("you'll be back in 2 weeks")
- No comparative superiority claims ("best treatment," "most effective")
- No testimonial-style language ("patients love," "everyone recommends")
- No diagnostic statements without qualification ("you have X" vs "this may indicate X")

**Client-specific compliance** (from `compliance.md`):
- Apply all client-specific rules
- Flag any content that conflicts with client constraints

**Medical accuracy**:
- Claims should be evidence-based or qualified with "may," "commonly," "research suggests"
- No scope-of-practice violations (e.g., physio content making chiropractic claims)

### 4. Distinctness Check

Compare the blog content against `published-articles.json`:
- No recycled introductions or conclusions from previous articles
- Different structural approach from the closest related article
- Unique angle even if the broader topic overlaps
- No copied paragraphs or near-duplicate sections

### 5. Human Tone Improvement

Final pass focused on readability:
- Break up any sentences over 30 words
- Replace passive voice with active where it improves clarity
- Add specificity where statements are vague ("many patients" → "about 1 in 4 adults over 40")
- Ensure conversational flow without being too casual for clinical content
- Moderate keyword density (flag if any keyword appears more than 2.5% density)

### 6. Assign Compliance Confidence

Based on the review, assign a confidence score:

- **high** - no compliance issues found, all anti-AI patterns resolved, content is distinct
- **medium** - minor issues fixed during review, all resolved in output, no remaining concerns
- **low** - significant compliance risk remains that requires human review before publishing (e.g., medical claims that can't be safely rephrased, potential AHPRA violation, scope-of-practice concern)

**If compliance_confidence = low**: include specific reasons in the output and recommend halting publishing.

## Output

```json
{
  "blog_final": "",
  "social_final": [
    { "label": "01", "content": "" },
    { "label": "02", "content": "" },
    { "label": "03", "content": "" }
  ],
  "faq_schema_final": {},
  "compliance_confidence": "high | medium | low",
  "compliance_notes": [],
  "changes_made": {
    "ai_patterns_fixed": 0,
    "compliance_issues_fixed": 0,
    "distinctness_adjustments": 0,
    "readability_improvements": 0
  }
}
```

## Validation Checkpoints

- [ ] All anti-AI writing patterns identified and resolved
- [ ] No em dashes remain in any output
- [ ] No exaggerated medical claims remain
- [ ] AHPRA compliance verified for all content
- [ ] Client-specific compliance rules applied
- [ ] Content is distinct from published articles
- [ ] Keyword density is between 1-2.5% for primary keyword
- [ ] Compliance confidence score assigned with supporting notes
- [ ] If low confidence, clear reasons provided and publishing halt recommended

## Related Skills

- **write-blog** - produces the blog content reviewed here
- **generate-social-posts** - produces the social posts reviewed here
- **publish-google-doc** - consumes the output of this skill (only if confidence != low)
- **run-batch** - orchestrates this skill and handles the low-confidence halt
