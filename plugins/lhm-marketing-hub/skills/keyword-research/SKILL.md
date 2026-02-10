---
name: keyword-research
description: "Discovers high-value keywords with search intent analysis, difficulty assessment, and content opportunity mapping. Use this when the user mentions 'keyword research', 'find keywords', 'keyword opportunities', 'search intent', 'topic clusters', 'keyword difficulty', 'content keywords', 'SEO keywords', 'long-tail keywords', 'keyword gap', or needs help planning which keywords to target for content or ads."
license: MIT
---

# Keyword Research

This skill helps you discover, analyze, and prioritize keywords for SEO and content strategies. It identifies high-value opportunities based on search volume, competition, intent, and business relevance.

## When to Use

- Starting a new content strategy or campaign
- Expanding into new topics or markets
- Finding keywords for a specific product or service
- Identifying long-tail keyword opportunities
- Understanding search intent for your industry
- Planning content calendars
- Researching keywords for GEO optimization

## What This Skill Does

1. **Keyword Discovery**: Generates comprehensive keyword lists from seed terms
2. **Intent Classification**: Categorizes keywords by user intent (informational, navigational, commercial, transactional)
3. **Difficulty Assessment**: Evaluates competition level and ranking difficulty
4. **Opportunity Scoring**: Prioritizes keywords by potential ROI
5. **Clustering**: Groups related keywords into topic clusters
6. **GEO Relevance**: Identifies keywords likely to trigger AI responses

## How to Use

### Basic Keyword Research

```
Research keywords for [topic/product/service]
```

### With Specific Goals

```
Find low-competition keywords for [topic] with commercial intent
```

### Competitive Research

```
What keywords is [competitor URL] ranking for that I should target?
```

## Data Sources

**With Google Search Console MCP connected:**
Automatically pull current rankings, search volume data, and keyword performance. The skill will fetch seed keyword metrics and search trend data.

**With manual data only:**
Ask the user to provide:
1. Seed keywords or topic description
2. Target audience and geographic location
3. Business goals (traffic, leads, sales)
4. Current domain authority (if known) or site age
5. Any known keyword performance data or search volume estimates

## Instructions

When a user requests keyword research:

### 1. Understand the Context

Ask clarifying questions if not provided:
- What is your product/service/topic?
- Who is your target audience?
- What is your business goal? (traffic, leads, sales)
- What is your current domain authority? (new site, established, etc.)
- Any specific geographic targeting?

### 2. Generate Seed Keywords

Start with:
- Core product/service terms
- Problem-focused keywords (what issues do you solve?)
- Solution-focused keywords (how do you help?)
- Audience-specific terms
- Industry terminology

### 3. Expand Keyword List

For each seed keyword, generate variations:

**Modifiers:**
- Best [keyword], Top [keyword]
- [keyword] for [audience]
- [keyword] near me, [keyword] [year]
- How to [keyword], What is [keyword]
- [keyword] vs [alternative]
- [keyword] examples, tools, template, checklist, guide

**Long-tail Variations:**
- [keyword] for beginners / for small business
- Free [keyword]
- [keyword] software/tool/service

### 4. Classify Search Intent

| Intent | Signals | Example | Content Type |
|--------|---------|---------|--------------|
| Informational | what, how, why, guide, learn | "what is SEO" | Blog posts, guides |
| Navigational | brand names, specific sites | "google analytics login" | Homepage, product pages |
| Commercial | best, review, vs, compare | "best SEO tools 2024" | Comparison posts, reviews |
| Transactional | buy, price, discount, order | "buy SEO software" | Product pages, pricing |

### 5. Assess Keyword Difficulty

Score each keyword (1-100 scale):

| Difficulty | Range | Signals |
|-----------|-------|---------|
| High | 70-100 | Major brands ranking, high DA competitors, 1000+ backlinks, paid ads dominating |
| Medium | 40-69 | Mix of authority and niche sites, moderate backlink requirements |
| Low | 1-39 | Few authoritative competitors, thin/outdated content, long-tail, emerging topics |

### 6. Calculate Opportunity Score

Formula: `Opportunity = (Volume x Intent Value) / Difficulty`

| Scenario | Volume | Difficulty | Intent | Priority |
|----------|--------|------------|--------|----------|
| Quick Win | Low-Med | Low | High | 5 stars |
| Growth | High | Medium | High | 4 stars |
| Long-term | High | High | High | 3 stars |
| Research | Low | Low | Low | 2 stars |

### 7. Identify GEO Opportunities

Keywords likely to trigger AI responses:

**High GEO Potential:**
- Question formats: "What is...", "How does...", "Why is..."
- Definition queries: "[term] meaning", "[term] definition"
- Comparison queries: "[A] vs [B]", "difference between..."
- List queries: "best [category]", "top [number] [items]"
- How-to queries: "how to [action]", "steps to [goal]"

### 8. Create Topic Clusters

Group keywords into content clusters:

```
## Topic Cluster: [Main Topic]

**Pillar Content**: [Primary keyword]
- Search volume: [X] | Difficulty: [X]
- Content type: Comprehensive guide

**Cluster Content**:
1. [Secondary keyword] — Volume: [X] | Difficulty: [X] | Links to: Pillar
2. [Secondary keyword] — Volume: [X] | Difficulty: [X] | Links to: Pillar + #1
```

### 9. Generate Output Report

```
# Keyword Research Report: [Topic]

**Date**: [Date]
**Target Audience**: [Audience]
**Business Goal**: [Goal]

## Executive Summary
- Total keywords analyzed: [X]
- High-priority opportunities: [X]
- Estimated traffic potential: [X]/month
- Recommended focus areas: [List]

## Quick Wins (Low difficulty, High value)
| Keyword | Volume | Difficulty | Intent | Score |
|---------|--------|------------|--------|-------|

## Growth Keywords (Medium difficulty, High volume)
| Keyword | Volume | Difficulty | Intent | Score |
|---------|--------|------------|--------|-------|

## GEO Opportunities (AI-citation potential)
| Keyword | Type | AI Potential | Recommended Format |
|---------|------|--------------|-------------------|

## Topic Clusters
[Cluster maps]

## Content Calendar Recommendations
| Month | Content | Target Keyword | Type |
|-------|---------|----------------|------|

## Next Steps
1. [Action item]
2. [Action item]
```

## Output File

Save to: `seo/YYYY-MM/keyword-research-[topic].md`

## Tips

1. **Start with seed keywords** that describe your core offering
2. **Don't ignore long-tail** — they often have highest conversion rates
3. **Match content to intent** — informational queries need guides, not sales pages
4. **Group into clusters** for topical authority
5. **Prioritize quick wins** to build momentum and credibility
6. **Include GEO keywords** in your strategy for AI visibility
7. **Review quarterly** — keyword dynamics change over time

## Related Skills

- **Competitive Analysis**: See what keywords competitors rank for
- **Content Strategy**: Plan content around target keywords
- **SEO Audit**: Assess current keyword performance
- **Programmatic SEO**: Scale SEO pages for keyword clusters
