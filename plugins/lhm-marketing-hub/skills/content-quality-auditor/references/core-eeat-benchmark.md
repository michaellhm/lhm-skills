# CORE-EEAT Content Benchmark

## Framework Overview

Two-system architecture combining GEO (Generative Engine Optimization) and SEO quality signals.

- **CORE** (C, O, R, E) — optimizes for AI engine citation
- **EEAT** (Exp, Ept, A, T) — optimizes for search engine trust

Each dimension has 10 items (80 total). Each item scores Pass (10), Partial (5), or Fail (0).

## 8 Dimensions

| Code | Dimension | Focus |
|------|-----------|-------|
| C | Citability | Can AI extract and quote this content? |
| O | Organization | Is content structured for scanning? |
| R | Reliability | Are claims backed by evidence? |
| E | Engagement | Does content add unique value? |
| Exp | Experience | Does the author show first-hand experience? |
| Ept | Expertise | Does content show deep subject knowledge? |
| A | Authoritativeness | Is the source recognized? |
| T | Trustworthiness | Is content transparent and honest? |

## Priority Tags

- **GEO-First** — highest impact on AI citation
- **SEO-First** — highest impact on search ranking
- **Dual** — impacts both equally

## Content-Type Weight Table

Weights must sum to 100 for each content type.

| Content Type | C | O | R | E | Exp | Ept | A | T |
|-------------|---|---|---|---|-----|-----|---|---|
| Blog (guide) | 15 | 12 | 15 | 10 | 8 | 12 | 10 | 18 |
| Blog (tools/review) | 12 | 10 | 18 | 10 | 12 | 15 | 8 | 15 |
| Comparison | 15 | 15 | 18 | 8 | 8 | 12 | 8 | 16 |
| Landing page | 10 | 12 | 12 | 15 | 10 | 10 | 8 | 23 |
| FAQ page | 18 | 15 | 15 | 8 | 5 | 12 | 10 | 17 |
| How-to guide | 12 | 15 | 15 | 12 | 15 | 10 | 5 | 16 |
| Case study | 10 | 10 | 15 | 15 | 18 | 10 | 8 | 14 |
| Product review | 10 | 10 | 18 | 12 | 18 | 12 | 5 | 15 |
| Best-of | 12 | 15 | 18 | 10 | 10 | 12 | 8 | 15 |

## Veto Items

These items cap the overall score at "Poor" if they fail:

- **T04** — Disclosure & transparency
- **C01** — Intent alignment (title must match content)
- **R10** — Content consistency (no contradictions)

## Rating Scale

| Score | Rating |
|-------|--------|
| 90-100 | Excellent |
| 70-89 | Good |
| 50-69 | Needs Improvement |
| 40-49 | Poor |
| 0-39 | Critical |

---

## Complete 80-Item Checklist

### Citability (C01-C10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| C01 | Intent alignment | Title promise = content delivery | Title partially matches | Misleading title | **VETO** |
| C02 | Direct answer | Core answer in first 150 words | Answer within first 300 words | No direct answer | GEO-First |
| C03 | Entity richness | People, orgs, products named precisely | Some entities named | Vague references only | GEO-First |
| C04 | Term definitions | Key terms defined on first use | Some terms defined | No definitions | GEO-First |
| C05 | Quotable statements | 3+ standalone quotable facts | 1-2 quotable statements | No standalone quotes | GEO-First |
| C06 | Audience targeting | "This article is for..." stated | Audience implied | No audience clarity | Dual |
| C07 | Scope boundaries | Clear what's covered and not | Scope mostly clear | Unclear scope | GEO-First |
| C08 | Comparison structures | Tables/lists comparing options | Some comparisons in prose | No comparisons | GEO-First |
| C09 | FAQ with schema | FAQ section + FAQPage schema | FAQ section, no schema | No FAQ | GEO-First |
| C10 | Semantic closure | Conclusion answers opening question + next steps | Partial conclusion | No conclusion | Dual |

### Organization (O01-O10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| O01 | Heading hierarchy | H1→H2→H3, no level skipping | Minor hierarchy issues | Broken hierarchy | Dual |
| O02 | Summary box | TL;DR or Key Takeaways present | Summarized in intro | No summary | GEO-First |
| O03 | Data in tables | Comparisons use tables | Mix of tables and prose | All data in prose | GEO-First |
| O04 | Anchor links | TOC with jump links | Partial TOC | No navigation | Dual |
| O05 | Schema markup | JSON-LD matching content type | Basic schema | No schema | GEO-First |
| O06 | Section chunking | Each section single topic, 3-5 sentence paragraphs | Mostly chunked | Long, unfocused sections | GEO-First |
| O07 | Visual breaks | Break every 300 words (image, table, list) | Some visual breaks | Walls of text | Dual |
| O08 | Consistent formatting | Consistent patterns throughout | Mostly consistent | Inconsistent formatting | Dual |
| O09 | Information density | No filler; consistent terminology | Minor filler | Significant padding | GEO-First |
| O10 | Scannable highlights | Bold, callouts, blockquotes used | Some highlights | No visual emphasis | Dual |

### Reliability (R01-R10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| R01 | Data precision | 5+ precise numbers with units | 2-4 data points | No specific data | GEO-First |
| R02 | Citation density | 1+ external citation per 500 words | Some citations | No citations | GEO-First |
| R03 | Source quality | Peer-reviewed, official, recognized sources | Mix of quality | Low-quality or no sources | GEO-First |
| R04 | Evidence-claim mapping | Every claim backed by evidence | Most claims backed | Unsupported claims | GEO-First |
| R05 | Recency | Stats within 2 years | Stats within 3-5 years | Outdated stats | GEO-First |
| R06 | Methodology transparency | Methods/criteria explained | Partially explained | No methodology | Dual |
| R07 | Entity precision | Full names for people/orgs/products | Mostly full names | Vague references | GEO-First |
| R08 | Counterpoint acknowledgment | Addresses opposing views | Brief mention | One-sided only | Dual |
| R09 | Reproducibility | Reader can verify/reproduce | Partially verifiable | Not verifiable | GEO-First |
| R10 | Content consistency | No contradictions | Minor inconsistencies | Contradictions present | **VETO** |

### Engagement (E01-E10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| E01 | Original data | First-party data or research | Some original insights | All secondhand | GEO-First |
| E02 | Unique framework | Original model or framework | Modified existing framework | No unique angle | Dual |
| E03 | Concrete examples | 3+ real-world examples | 1-2 examples | No examples | GEO-First |
| E04 | Narrative hooks | Compelling opening and transitions | Some hooks | Dry, no hooks | Dual |
| E05 | Interactive elements | Tools, calculators, quizzes | Downloadable resources | Nothing interactive | Dual |
| E06 | Visual data | Charts, diagrams, infographics | Some visuals | Text only | GEO-First |
| E07 | Templates/checklists | Practical downloadable assets | Inline checklists | No practical tools | Dual |
| E08 | Case studies | Named companies with results | Anonymous examples | No case studies | GEO-First |
| E09 | Questions anticipated | Addresses follow-up questions | Some Q&A | No anticipation | GEO-First |
| E10 | Clear next steps | Specific CTA with next action | Generic CTA | No CTA | GEO-First |

### Experience (Exp01-Exp10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| Exp01 | Personal account | "I tested..." / "We found..." | Implied experience | No personal experience | SEO-First |
| Exp02 | Process documentation | Step-by-step from own experience | High-level process | Generic advice | SEO-First |
| Exp03 | Original photos/screenshots | Own screenshots or photos | Stock with context | No visuals | SEO-First |
| Exp04 | Specific results | Named metrics from own work | General results | No results | SEO-First |
| Exp05 | Timeline narrative | "Over 6 months we saw..." | General timeframes | No timeline | SEO-First |
| Exp06 | Tool familiarity | Specific tool tips and workflows | Tool mentions | No tool knowledge | Dual |
| Exp07 | Mistake sharing | "We tried X and it failed because..." | Brief failure mention | Only successes | SEO-First |
| Exp08 | Behind-the-scenes | Process/methodology revealed | Brief process mention | Black box results | SEO-First |
| Exp09 | Contextual advice | "In [situation], do X instead of Y" | Some context | One-size-fits-all | Dual |
| Exp10 | Limitation acknowledgment | "This won't work if..." | Brief limitations | No limitations | GEO-First |

### Expertise (Ept01-Ept10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| Ept01 | Technical depth | Deep technical explanation | Moderate depth | Surface-level | Dual |
| Ept02 | Terminology precision | Industry terms used correctly | Mostly correct | Misused terms | Dual |
| Ept03 | Nuanced analysis | "It depends because..." | Some nuance | Black/white only | Dual |
| Ept04 | Cross-domain connections | Links to related fields | Brief connections | Siloed view | Dual |
| Ept05 | Current landscape | References latest developments | Somewhat current | Outdated view | GEO-First |
| Ept06 | Decision frameworks | "Use X when..., Y when..." | Some guidance | No framework | Dual |
| Ept07 | Edge cases | Addresses exceptions | Brief mention | Ignores edge cases | Dual |
| Ept08 | Reasoning transparency | Explains why, not just what | Some reasoning | Just assertions | GEO-First |
| Ept09 | Prerequisite clarity | States what reader needs to know | Partially stated | Assumes knowledge | Dual |
| Ept10 | Depth progression | Basics → advanced in logical flow | Some progression | Random depth | Dual |

### Authoritativeness (A01-A10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| A01 | Author credentials | Relevant qualifications visible | Some credentials | No author info | SEO-First |
| A02 | Publication history | Links to other published work | Brief bio | No history | SEO-First |
| A03 | Industry recognition | Awards, speaking, citations | Some recognition | Unknown author | SEO-First |
| A04 | Expert endorsements | Quotes from recognized experts | Referenced experts | No expert voices | Dual |
| A05 | Organizational authority | Published by recognized org | Known but niche org | Unknown org | SEO-First |
| A06 | Original research | Own studies or surveys | Analysis of others' research | No research | Dual |
| A07 | Media coverage | Referenced by media/press | Some mentions | No coverage | SEO-First |
| A08 | Community engagement | Active comments, discussions | Some engagement | No community | GEO-First |
| A09 | Update frequency | Regular updates with dates | Occasional updates | Never updated | Dual |
| A10 | Cross-referencing | Cited by other authorities | Some external links | Not referenced | SEO-First |

### Trustworthiness (T01-T10)

| ID | Item | Pass | Partial | Fail | Priority |
|----|------|------|---------|------|----------|
| T01 | Factual accuracy | All facts verified correct | Minor inaccuracies | Significant errors | Dual |
| T02 | Source transparency | All sources linked and named | Most sources cited | No sources | Dual |
| T03 | Bias disclosure | Conflicts of interest stated | Implied objectivity | Hidden bias | SEO-First |
| T04 | Disclosure | Clear about sponsorship/affiliation | Partial disclosure | Deceptive practices | **VETO** |
| T05 | Contact information | Real contact info available | Generic contact | No contact info | SEO-First |
| T06 | Editorial standards | Clear editorial policy | Implied standards | No standards | SEO-First |
| T07 | Error correction | Corrections noted and dated | Errors fixed silently | Known errors remain | Dual |
| T08 | Privacy compliance | Privacy policy, cookie consent | Partial compliance | No privacy measures | SEO-First |
| T09 | Secure delivery | HTTPS, no mixed content | HTTPS with minor issues | HTTP or insecure | SEO-First |
| T10 | Content freshness signals | "Last updated [date]" visible | Date somewhere on page | No date information | Dual |

---

## AI Engine Citation Preferences

| Engine | Top Priority Items |
|--------|-------------------|
| Google AI Overview | C02, O03, O05, C09 |
| ChatGPT Browse | C02, R01, R02, E01 |
| Perplexity AI | E01, R03, R05, Ept05 |
| Claude | R04, Ept08, Exp10, R03 |

## Schema by Content Type

| Content Type | Required Schema | Conditional Schema |
|-------------|----------------|-------------------|
| Blog (guide) | Article, Breadcrumb | FAQ, HowTo |
| Blog (tools) | Article, Breadcrumb | FAQ, Review |
| Comparison | Article, Breadcrumb, FAQ | AggregateRating |
| Best-of | ItemList, Breadcrumb, FAQ | AggregateRating |
| FAQ page | FAQPage, Breadcrumb | — |
| Landing page | SoftwareApplication, Breadcrumb, FAQ | WebPage |
| Product review | Review, Breadcrumb | FAQ, Product |
