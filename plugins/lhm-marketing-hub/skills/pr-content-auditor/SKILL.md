---
name: pr-content-auditor
description: "Rewrite rejected Digital PR articles to pass distributor quality checks. Audits against 25 PR writing guidelines plus CORE-EEAT, copy editing, and SEO baselines, then rewrites the full article. Use this when the user mentions 'rejected PR', 'PR rewrite', 'PR got rejected', 'fix the PR', 'rewrite the press release', 'digital PR audit', 'PR content audit', 'distributor rejected', 'PR not published', 'unpublished PR', or 'resubmit PR'."
---

# PR Content Auditor

Rewrites rejected Digital PR articles so they pass distributor quality checks on resubmission. Takes the rejected content, silently audits it against 25 PR writing guidelines and a quality baseline drawn from CORE-EEAT, copy editing, and SEO best practices, then produces a fully rewritten version ready to resubmit.

## When to Use This Skill

- A Digital PR has been rejected or unpublished by a distributor
- A PR is stuck in "unpublished" status after manual republishing attempts
- The user wants to rewrite a PR before resubmitting to the same platform
- The user has rejection feedback from a publisher and wants the content fixed

## Initial Assessment

1. **Load client context.** Read `client_profile.md` from the client folder. Note the brand voice, practitioner names, clinic locations, and any compliance requirements.

2. **Read the LEARNED.md file** from this skill's directory (`${CLAUDE_PLUGIN_ROOT}/skills/pr-content-auditor/LEARNED.md`). Apply any relevant entries.

3. **Get the rejected PR content.** Accept it in any format:
   - A markdown file path (read the file)
   - A Google Doc URL (fetch via Google Drive MCP)
   - Text pasted directly into chat

4. **Identify the target keyword.** Look for the modality + location keyword in the intro and outro (e.g. "Osteopath Newport", "Physio Melbourne CBD"). If not obvious, ask the user to confirm.

5. **Check for rejection feedback.** Ask: "Did the publisher give any feedback on why it was rejected?" Accept text, screenshots, or "no feedback." This is optional context, not a blocker.

## Mandatory: Route Long-Form Writing Through content-writer Agent

Long-form content (over 300 words or page-level web/blog copy) goes through the 8-pass pipeline. This skill is responsible for:

1. Research and brief construction
2. Outline planning
3. Building a `structured_brief` for the content-writer (target keyword, intent, outline, internal/external link targets, client voice notes from `client_profile.md` or product marketing context)
4. Calling the content-writer agent with `content_type: "blog-post"` and the structured brief
5. Saving returned content to the agreed output path
6. Final SEO validation (primary keyword density, internal link count, meta description) where applicable

Do not generate the body content directly. Delegate to content-writer.

## Rewrite Process

Read the PR writing guidelines from `${CLAUDE_PLUGIN_ROOT}/skills/pr-content-auditor/references/pr-writing-guidelines.json` and the plugin-wide anti-AI writing guidelines from `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`.

Audit the full PR (intro + body + outro) internally against everything below. Do not present a detailed audit to the user. Use the audit findings to inform the rewrite.

### Layer 1: PR Writing Guidelines (25 rules)

**Anti-AI Writing (w1-w10):**
Scan for and fix these patterns in the rewrite:
- Triplet structures (w1): vary groupings to 2, 4, or 5 items
- Contrast framing (w2): remove "while X, Y" and "although X, Y" constructions
- Poetic scene-setting (w3): replace "in a world where" openers with direct first sentences
- Odd-numbered paragraph counts (w4): write to natural stopping points
- Hypophora (w5): remove question-then-answer filler patterns
- Adverb reliance (w6): replace "significantly", "dramatically", "effectively" with stronger verbs or data
- Cliche pairings (w7): replace "seamless integration", "robust solution", "game-changing" with specific language
- Signpost transitions (w8): remove "let's explore", "let's dive in", connect ideas through logic
- Inspirational closers (w9): end paragraphs with substance, not vague emotional statements
- Em dashes (w10): replace all em dashes with commas, parentheses, or restructured sentences

**Digital PR for SEO (pr1-pr12):**
Ensure the rewrite satisfies these principles:
- Newsworthy angle leads, not the keyword (pr1)
- Original data or first-party insights where possible (pr2)
- Topical authority matches the client's niche (pr3)
- Content quality meets editorial publication standards (pr4)
- The asset is complete and linkable (pr5)
- Interactive or embed-only elements where feasible (pr6)
- Expert positioning for the practitioner or founder (pr8)
- AHPRA compliance for healthcare clients (pr11)

**Combined Principles (c1-c3):**
- Replace vague claims with specific numbers, names, or locations (c1)
- Write for the human reader first, optimise second (c2)
- Maintain consistent voice throughout (c3)

### Layer 2: Quality Baseline

These checks fill the gap between "doesn't read like AI" and "actually publishable, rankable content."

**CORE-EEAT:**
- Core answer or main point appears in the first 150 words
- At least 3 standalone quotable facts a journalist or AI could extract and cite
- Entity precision: full names for people, organisations, products (no vague references)
- At least 1 external citation per 500 words
- Statistics within 2 years of publication date
- Every claim backed by evidence (data, source, or first-hand account)
- No contradictions within the content
- First-person account where appropriate ("we found...", "in our experience...")
- Specific results from own work, not generic claims
- Limitation acknowledgment where honest ("this approach works best for...")
- Transparent disclosure of affiliations

**Copy Editing:**
- "So What" test: every claim answers "why should the reader care?" with a concrete benefit
- "Prove It" test: unsubstantiated claims ("trusted by thousands", "industry-leading") get evidence or removal
- Specificity upgrades: replace "improve", "enhance", "optimise" with concrete numbers and timeframes
- Word-level cuts: remove weak intensifiers (very, really, extremely), filler (just, actually, basically), corporate speak (utilize, leverage, facilitate, robust, seamless)
- One idea per sentence, max 25 words per sentence (usually)
- One topic per paragraph, 2-4 sentences for web
- Vary sentence length (mix short and long)
- Front-load important information in each paragraph

**SEO:**
- Primary keyword (modality + location) in the title
- Primary keyword in the first 100 words
- Primary keyword in at least one H2
- Primary keyword in the conclusion
- Title under 60 characters with the primary keyword
- Meta description 150-160 characters with primary keyword, value proposition, and CTA
- H1 -> H2 -> H3 hierarchy, no level skipping
- Short paragraphs (2-4 sentences)
- Bold key phrases for scannability
- 2-3 authoritative external sources linked within the body
- Internal links to relevant client pages where applicable

### Layer 3: Publisher Feedback (if provided)

If the user provided rejection feedback, cross-reference it with the violations found above. Prioritise fixing anything the publisher specifically called out, even if it seems minor by the guidelines.

## Rewrite Execution

Rewrite the full article (intro + body + outro) applying all fixes from the three layers above. Preserve:
- The same target keyword (modality + location)
- The core message and topic of the original article
- The client's brand voice (from client_profile.md)
- Any factual claims that are already well-supported

Do not add a detailed audit or violation list to the output. The rewrite IS the deliverable.

## Output

### In Chat

Present a brief summary of what changed. 3-5 bullet points maximum. Example:

> Rewrote the PR for "Osteopath Newport". Main changes:
> - Replaced generic intro with a specific local angle referencing Newport demographics
> - Removed 4 AI-pattern phrases (em dashes, "in a world where" opener, triple-structure paragraphs)
> - Added 2 external citations and replaced 3 vague claims with specific data points
> - Tightened the outro to end on a concrete claim rather than an inspirational closer
> - Ensured keyword placement in title, first 100 words, one H2, and conclusion

### File Output

Save the rewritten PR to `client/pr-audit/YYYY-MM/[keyword-slug]-rewrite.md`:

```markdown
# [Article Title]

**Target Keyword:** [modality + location]
**Original PR:** [filename or "pasted"]
**Date:** YYYY-MM-DD

---

[Full rewritten article with intro, body, and outro]
```

Include the meta description as a comment at the top of the article body:

```markdown
<!-- Meta: [150-160 char meta description] -->
```

## What This Skill Does NOT Do

- No scoring, pass/fail table, or per-rule violation breakdown in the output
- No keyword strategy changes (the target keyword stays the same)
- No distribution or pitch strategy advice
- No AHPRA compliance review (use `landing-page-optimizer` for that)

## Related Skills

- `content-quality-auditor` for a full CORE-EEAT 80-item audit (different purpose, much more comprehensive)
- `copy-editing` for general copy review on any content type
- `seo-content-writer` for writing new SEO content from scratch
