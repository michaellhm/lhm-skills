---
name: geo-content-optimizer
description: "Optimizes content for Generative Engine Optimization (GEO) to increase chances of being cited by AI systems like ChatGPT, Claude, Perplexity, and Google AI Overviews. Use this when the user mentions 'GEO,' 'AI citations,' 'AI overviews,' 'generative engine optimization,' 'get cited by AI,' 'Perplexity optimization,' 'ChatGPT citations,' 'AI-friendly content,' or 'quotable content.' Makes content AI-citeable while maintaining SEO value."
---

# GEO Content Optimizer

Optimizes content to appear in AI-generated responses. As AI systems increasingly answer user queries directly, getting cited by these systems is crucial for visibility.

## When to Use This Skill

- Optimizing existing content for AI citations
- Creating new content designed for both SEO and GEO
- Improving chances of appearing in Google AI Overviews
- Making content more quotable by AI systems
- Adding authority signals that AI systems trust
- Competing for visibility in the AI-first search era

## What This Skill Does

1. **Citation Optimization** — makes content more likely to be quoted by AI
2. **Structure Enhancement** — formats content for AI comprehension
3. **Authority Building** — adds signals that AI systems trust
4. **Factual Enhancement** — improves accuracy and verifiability
5. **Quote Creation** — creates memorable, citeable statements
6. **Source Attribution** — adds proper citations that AI can verify
7. **GEO Scoring** — evaluates content's AI-friendliness

## Instructions

When a user requests GEO optimization:

### 1. Analyze Current Content

```markdown
## GEO Analysis: [Content Title]

| Factor | Score (1-5) | Notes |
|--------|-------------|-------|
| Clear definitions | [X] | [notes] |
| Quotable statements | [X] | [notes] |
| Factual density | [X] | [notes] |
| Source citations | [X] | [notes] |
| Q&A format | [X] | [notes] |
| Authority signals | [X] | [notes] |
| Content freshness | [X] | [notes] |
| Structure clarity | [X] | [notes] |

**Overall GEO Score**: [X]/40

**Quick Wins**:
1. [Quick improvement 1]
2. [Quick improvement 2]
```

### 2. Optimize Definitions

AI systems love clear, quotable definitions.

**Template**: "[Term] is [clear category] that [primary function], [key characteristic]."

**Checklist**:
- [ ] Starts with the term being defined
- [ ] Provides clear category
- [ ] Explains primary function
- [ ] Uses precise, unambiguous language
- [ ] Can stand alone as a complete answer
- [ ] Is 25-50 words for optimal citation length

**Before** (weak): "SEO is really important for businesses and involves various techniques to improve visibility."

**After** (strong): "**Search Engine Optimization (SEO)** is the practice of optimizing websites and content to rank higher in search engine results pages (SERPs), increasing organic traffic and visibility."

### 3. Create Quotable Statements

Transform vague content into citeable facts.

**Types of quotable content**:

1. **Statistics** — "According to [Source], [specific stat] as of [date]."
2. **Facts** — "[Subject] was [fact], according to [authoritative source]."
3. **Comparisons** — "Unlike [A], [B] [specific difference], which means [implication]."
4. **How-to steps** — "To [achieve goal]: 1) [step], 2) [step], 3) [step]."

**Before**: "Email marketing is pretty effective and lots of companies use it."

**After**: "Email marketing delivers an average ROI of $42 for every $1 spent, making it one of the highest-performing digital marketing channels (Data & Marketing Association)."

### 4. Add Authority Signals

```markdown
### Authority Enhancements

- [ ] Author byline with credentials
- [ ] Expert quotes with attribution
- [ ] Citations to research/studies
- [ ] References to recognized authorities
- [ ] Original data or research
- [ ] Case studies with named companies
- [ ] Industry statistics with sources
```

### 5. Optimize Content Structure

AI systems parse structured content more effectively:

**Q&A format** — transform headings into question format:
```
## What is [Topic]?
[Direct answer in 40-60 words]
```

**Comparison tables** — for comparison queries:
```
| Feature | Option A | Option B |
|---------|----------|----------|
| [Factor] | [Specific value] | [Specific value] |
```

**Numbered lists** — for process queries:
```
1. **Step 1: [Action]** — [Brief explanation]
2. **Step 2: [Action]** — [Brief explanation]
```

**Key insight callouts**:
```
> **Key insight**: [Memorable, quotable statement with source]
```

### 6. Enhance Factual Density

Replace vague claims with verified facts:

**Low density**: "Social media marketing is very popular. Many businesses use it."

**High density**: "Social media marketing reaches 4.9 billion users globally (Statista, 2024). Businesses using social media report 66% higher lead generation rates (HubSpot, 2024)."

**Checklist**:
- [ ] Add specific statistics with sources
- [ ] Include exact numbers, dates, percentages
- [ ] Replace vague claims with verified facts
- [ ] Add recent data (within last 2 years)
- [ ] Cross-reference with authoritative sources

### 7. Add FAQ Schema

FAQ sections are highly effective for GEO:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "[Question text]",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "[Answer text]"
    }
  }]
}
```

### 8. Generate GEO Report

```markdown
## GEO Optimization Report

### Changes Made

**Definitions added**: [count]
**Quotable statements created**: [count]
**Authority signals added**: [count]
**Structural improvements**: [count]

### Before/After Score

| Factor | Before | After | Change |
|--------|--------|-------|--------|
| Clear definitions | [X] | [X] | +[X] |
| Quotable statements | [X] | [X] | +[X] |
| Factual density | [X] | [X] | +[X] |
| Source citations | [X] | [X] | +[X] |
| Q&A format | [X] | [X] | +[X] |
| Authority signals | [X] | [X] | +[X] |
| **Total** | [X]/30 | [X]/30 | +[X] |

### AI Query Coverage

This content is now optimized to answer:
- "What is [topic]?" ✅
- "How does [topic] work?" ✅
- "Why is [topic] important?" ✅
- "[Topic] vs [alternative]" ✅
```

## How AI Systems Select Content to Cite

| Factor | Google AI Overviews | ChatGPT | Perplexity | Claude |
|--------|---------------------|---------|------------|--------|
| Freshness bias | High | Medium | Very high | N/A |
| Authority weight | Very high | High | High | High |
| Structure importance | High | Medium | Very high | Medium |
| Citation count | 3-8 | 1-6 | 5-10 | N/A |
| Quotable focus | High | Medium | Very high | High |
| Factual density | High | High | Very high | Very high |

See [AI Citation Patterns](./references/ai-citation-patterns.md) for detailed behavior by AI system.

## Validation Checkpoints

- [ ] At least 3 clear, quotable definitions added
- [ ] At least 5 verifiable statistics with sources
- [ ] All claims have source citations
- [ ] Q&A format sections cover top 5 user queries
- [ ] GEO score improved by at least 50% from baseline

## Tips for Success

1. **Answer the question first** — put the answer in the first sentence
2. **Be specific** — vague content doesn't get cited
3. **Cite sources** — AI systems trust verifiable information
4. **Stay current** — update statistics and facts regularly
5. **Match query format** — questions deserve direct answers
6. **Build authority** — expert credentials increase citation likelihood

## Reference Materials

- [AI Citation Patterns](./references/ai-citation-patterns.md) — how Google AI Overviews, ChatGPT, Perplexity, and Claude select sources
- [Quotable Content Examples](./references/quotable-content-examples.md) — 10 before/after examples of content optimized for AI citation

## Related Skills

- **seo-content-writer** — create SEO content to optimize
- **schema-markup** — add structured data for AI comprehension
- **content-refresher** — update content for freshness
- **content-quality-auditor** — full CORE-EEAT quality audit
- **content-gap-analysis** — find gaps in AI citation coverage
