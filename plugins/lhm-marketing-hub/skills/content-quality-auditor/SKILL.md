---
name: content-quality-auditor
description: "Runs a full CORE-EEAT 80-item quality audit on any piece of content, scoring GEO readiness and SEO strength across 8 dimensions. Use this when the user mentions 'content quality,' 'CORE-EEAT audit,' 'content audit,' 'quality score,' 'is this content good enough,' 'GEO readiness,' 'E-E-A-T check,' or 'content benchmark.' Produces dimension scores, weighted totals, and a prioritized action plan."
---

# Content Quality Auditor

Runs the full CORE-EEAT 80-item benchmark across 8 dimensions to evaluate content quality for both GEO (AI citation potential) and SEO (search ranking strength).

In a staged Content Department workflow, this skill is also the independent editorial QA gate defined in `${CLAUDE_PLUGIN_ROOT}/references/content-departmental-delivery.md`. The two modes are distinct:

1. **Benchmark mode**: run the full CORE-EEAT audit and improvement plan.
2. **Implementation-copy QA mode**: verify one exact copy version against its accepted brief and return a pass/fail-style verdict without rewriting it.

## Implementation-copy QA mode

Require the accepted `content_brief`, exact copy version, immutable digest and content type. Check:

- every requested placement has one exact replacement;
- protected copy, offers, claims and CTA destinations remain unchanged;
- claims map to accepted evidence and no unsupported specificity was introduced;
- the wording matches audience intent, brand sources and channel constraints;
- healthcare and other applicable compliance constraints pass;
- `anti-ai-writing-guidelines.json` is satisfied, including a mechanical em dash count of zero;
- page-level or over-300-word copy contains evidence that the eight-pass writing route was used;
- no audit note, placeholder, unresolved alternative or internal instruction appears in executable copy.

Return exactly one verdict: `pass`, `correction_required`, `needs_evidence`, `needs_approval`, `waiting_on_capability` or `failed`.

```yaml
content_editorial_qa:
  schema_version: 1
  parent_id: "stable production parent"
  action_id: "stable content action"
  brief_version: 1
  copy_version: 1
  content_digest: "immutable digest"
  verdict: "pass"
  checks:
    brief_conformance: pass
    exact_placements: pass
    preserved_content: pass
    factual_support: pass
    brand_voice: pass
    compliance: "pass | not_applicable"
    channel_constraints: pass
    anti_ai: pass
    em_dash_count: 0
    writing_route: "eight_pass | constrained_short_form"
  issues: []
  next_owner: "Content Lead"
```

Do not repair the copy inside QA. On `correction_required`, return a bounded issue list with placement or line references. Content Lead returns that list to the same writer and submits a new copy version for another QA run.

## When to Use This Skill

- Before publishing content — quality gate check
- Evaluating existing content for improvement opportunities
- Benchmarking content against quality standards
- Comparing content quality across pages or competitors
- Assessing GEO readiness (will AI cite this?)
- Assessing SEO strength (does this deserve to rank?)

## What This Skill Does

1. **Full 80-Item Audit** — scores every item as Pass (10), Partial (5), or Fail (0)
2. **8 Dimension Scores** — calculates 0-100 score per dimension
3. **GEO Score** — average of CORE dimensions (C + O + R + E) / 4
4. **SEO Score** — average of EEAT dimensions (Exp + Ept + A + T) / 4
5. **Weighted Scoring** — applies content-type-specific weights
6. **Veto Detection** — flags critical trust violations
7. **Action Plan** — prioritized top 5 improvements by weighted impact

## The 8 Dimensions

| Dimension | Code | Focus | Priority |
|-----------|------|-------|----------|
| Citability | C | Can AI extract and quote this content? | GEO-First |
| Organization | O | Is content structured for AI + human scanning? | Dual |
| Reliability | R | Are claims backed by verifiable evidence? | GEO-First |
| Engagement | E | Does content hold attention and add unique value? | Dual |
| Experience | Exp | Does the author show first-hand experience? | SEO-First |
| Expertise | Ept | Does content demonstrate deep subject knowledge? | Dual |
| Authoritativeness | A | Is the source recognized in this topic? | SEO-First |
| Trustworthiness | T | Is content transparent, accurate, and honest? | Dual |

## Scoring System

- **Pass** = 10 points (fully meets the standard)
- **Partial** = 5 points (partially meets, room for improvement)
- **Fail** = 0 points (does not meet the standard)

**Dimension score** = (sum of item scores / max possible) x 100

**Rating scale**:
- 90-100: Excellent
- 70-89: Good
- 50-69: Needs Improvement
- 40-49: Poor
- 0-39: Critical

## Veto Items

Three items can cap the overall score at "Poor" regardless of other scores:
- **T04** — Disclosure & transparency (no deceptive practices)
- **C01** — Intent alignment (title matches content delivery)
- **R10** — Content consistency (no contradictions within content)

## Instructions

When a user requests a content quality audit:

### 1. Identify Content Type

Determine the content type to load the correct weight profile:

| Content Type | C | O | R | E | Exp | Ept | A | T |
|-------------|---|---|---|---|-----|-----|---|---|
| Blog (guide) | 15 | 12 | 15 | 10 | 8 | 12 | 10 | 18 |
| Blog (tools/review) | 12 | 10 | 18 | 10 | 12 | 15 | 8 | 15 |
| Comparison/Alternative | 15 | 15 | 18 | 8 | 8 | 12 | 8 | 16 |
| Landing page | 10 | 12 | 12 | 15 | 10 | 10 | 8 | 23 |
| FAQ page | 18 | 15 | 15 | 8 | 5 | 12 | 10 | 17 |
| How-to guide | 12 | 15 | 15 | 12 | 15 | 10 | 5 | 16 |
| Case study | 10 | 10 | 15 | 15 | 18 | 10 | 8 | 14 |
| Product review | 10 | 10 | 18 | 12 | 18 | 12 | 5 | 15 |

### 2. Run the Audit

Score each dimension's 10 items. Here are the key items per dimension:

**Citability (C01-C10)**:
- C01: Intent alignment (title = content) — **VETO ITEM**
- C02: Direct answer in first 150 words
- C03: Entity-rich content (people, orgs, products named precisely)
- C04: Key terms defined on first use
- C05: Quotable standalone statements
- C06: Audience explicitly stated
- C07: Clear scope boundaries
- C08: Comparison/contrast structures
- C09: Structured FAQ with schema
- C10: Semantic closure (conclusion answers opening question)

**Organization (O01-O10)**:
- O01: Heading hierarchy (H1→H2→H3, no skipping)
- O02: Summary box / key takeaways
- O03: Data in tables, not prose
- O04: Anchor links / table of contents
- O05: JSON-LD schema markup
- O06: Section chunking (each section = single topic)
- O07: Visual breaks every 300 words
- O08: Consistent formatting patterns
- O09: Information density (no filler)
- O10: Scannable highlights (bold, callouts)

**Reliability (R01-R10)**:
- R01: Data precision (5+ numbers with units)
- R02: Citation density (1+ external citation per 500 words)
- R03: Source quality (peer-reviewed, official, recognized)
- R04: Evidence-claim mapping (every claim backed)
- R05: Recency (stats within 2 years)
- R06: Methodology transparency
- R07: Entity precision (full names, not "a study")
- R08: Counterpoint acknowledgment
- R09: Reproducibility (can reader verify?)
- R10: Content consistency (no contradictions) — **VETO ITEM**

**Engagement (E01-E10)**:
- E01: Original first-party data
- E02: Unique framework or model
- E03: Concrete examples (3+)
- E04: Narrative hooks
- E05: Interactive elements or tools
- E06: Visual data (charts, diagrams)
- E07: Practical templates or checklists
- E08: Real-world case studies
- E09: Reader questions anticipated and answered
- E10: Clear next steps / CTA

**Experience (Exp01-Exp10)**, **Expertise (Ept01-Ept10)**, **Authoritativeness (A01-A10)**, **Trustworthiness (T01-T10)**: See [CORE-EEAT Benchmark](./references/core-eeat-benchmark.md) for all 80 items.

### 3. Generate Scorecard

```markdown
## CORE-EEAT Audit: [Content Title]

**Content type**: [type]
**URL**: [url]
**Audit date**: [date]

### Dimension Scores

| Dimension | Score | Rating | Weight | Weighted |
|-----------|-------|--------|--------|----------|
| Citability (C) | [X]/100 | [rating] | [w]% | [X] |
| Organization (O) | [X]/100 | [rating] | [w]% | [X] |
| Reliability (R) | [X]/100 | [rating] | [w]% | [X] |
| Engagement (E) | [X]/100 | [rating] | [w]% | [X] |
| Experience (Exp) | [X]/100 | [rating] | [w]% | [X] |
| Expertise (Ept) | [X]/100 | [rating] | [w]% | [X] |
| Authoritativeness (A) | [X]/100 | [rating] | [w]% | [X] |
| Trustworthiness (T) | [X]/100 | [rating] | [w]% | [X] |

**GEO Score** (C+O+R+E avg): [X]/100
**SEO Score** (Exp+Ept+A+T avg): [X]/100
**Weighted Total**: [X]/100
**Overall Rating**: [Excellent/Good/Needs Improvement/Poor/Critical]

### Veto Check
- T04 (Disclosure): ✅/❌
- C01 (Intent alignment): ✅/❌
- R10 (Consistency): ✅/❌
```

### 4. Generate Action Plan

```markdown
### Top 5 Priority Improvements

| Rank | Item | Current | Target | Impact | Action |
|------|------|---------|--------|--------|--------|
| 1 | [ID] | Fail | Pass | [weighted impact] | [specific action] |
| 2 | [ID] | Fail | Pass | [weighted impact] | [specific action] |
| 3 | [ID] | Partial | Pass | [weighted impact] | [specific action] |
| 4 | [ID] | Fail | Pass | [weighted impact] | [specific action] |
| 5 | [ID] | Partial | Pass | [weighted impact] | [specific action] |

**Estimated score after fixes**: [X]/100 → [Y]/100
```

## Validation Checkpoints

- [ ] Content type correctly identified and weight profile loaded
- [ ] All 80 items scored (Pass/Partial/Fail)
- [ ] Veto items checked first
- [ ] Dimension scores calculated correctly
- [ ] Weighted total uses content-type weights
- [ ] Action plan ranked by weighted impact

## Reference Materials

- [CORE-EEAT Benchmark](./references/core-eeat-benchmark.md) — full 80-item checklist with Pass/Partial/Fail criteria for all items

## Related Skills

- **seo-content-writer** — create content that scores well
- **geo-content-optimizer** — optimize for AI citations (GEO score)
- **content-refresher** — update content to improve scores
- **seo-audit** — broader site-level SEO diagnostics
