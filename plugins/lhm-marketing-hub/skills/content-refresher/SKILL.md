---
name: content-refresher
description: "Identifies outdated or underperforming content and creates a refresh plan to recover lost rankings and traffic. Use this when the user mentions 'content refresh,' 'update old content,' 'declining traffic,' 'outdated blog posts,' 'content decay,' 'recover rankings,' or 'republish strategy.' Covers performance analysis, gap identification, GEO enhancement, and republishing tactics."
---

# Content Refresher

Systematically identifies underperforming content and guides its improvement through data-driven analysis, fresh information, GEO optimization, and strategic republishing.

## When to Use This Skill

- Content has lost rankings or traffic over time
- Blog posts contain outdated statistics or examples
- Competitors have published better content on the same topic
- Pages rank on page 2-3 but could reach page 1 with updates
- Content was published 12+ months ago without updates
- Pages get impressions but low CTR (title/description need refresh)
- Content lacks GEO optimization for AI citation

## Instructions

When a user requests a content refresh:

### 1. Identify Refresh Candidates

Use Search Console data or user-provided metrics:

```markdown
### Refresh Candidates

| URL | Published | Last Updated | Traffic Trend | Avg Position | Priority |
|-----|-----------|-------------|---------------|-------------|----------|
| [url] | [date] | [date] | ↓ declining | [pos] | High/Med/Low |

**Selection criteria applied**:
- ✅ Published 6+ months ago
- ✅ Traffic declining or flat
- ✅ Ranking position 5-30 (improvable)
- ✅ Topic still relevant to business
```

### 2. Analyze Individual Content

For each candidate, perform a deep analysis:

```markdown
### Content Analysis: [Title]

**Current performance**:
- Position: [X] (was [Y] at peak)
- Monthly traffic: [X] (was [Y] at peak)
- CTR: [X]% (benchmark: [Y]%)

**Content issues identified**:

| Issue | Severity | Details |
|-------|----------|---------|
| Outdated statistics | High/Med/Low | [which stats, how old] |
| Missing subtopics | High/Med/Low | [what competitors cover that we don't] |
| Thin sections | High/Med/Low | [which sections need expansion] |
| Poor structure | High/Med/Low | [what needs restructuring] |
| Weak title/meta | High/Med/Low | [current vs recommended] |
| No GEO optimization | High/Med/Low | [missing definitions, stats, Q&A] |
| Broken links | High/Med/Low | [count and locations] |
| Missing images | High/Med/Low | [where visuals would help] |

**Competitor comparison**:
- Top ranker word count: [X] vs yours: [Y]
- Top ranker sections: [list key sections they have that you don't]
- Top ranker freshness: [last updated date]
```

### 3. Create Refresh Plan

```markdown
### Refresh Plan: [Title]

**Goal**: Move from position [X] to [Y], increase traffic by [X]%

**Content changes**:
1. **Update statistics** — replace [X] outdated data points with current sources
2. **Add missing sections**: [list new sections to add]
3. **Expand thin sections**: [list sections to deepen]
4. **Improve structure** — [restructuring needed]
5. **Update examples** — replace dated examples with current ones

**Title tag refresh**:
- Before: "[current title]"
- After: "[new title]" — [reasoning]

**Meta description refresh**:
- Before: "[current meta]"
- After: "[new meta]" — [reasoning]

**Internal linking updates**:
- Add links to: [newer related content]
- Add links from: [high-authority pages on the site]
```

### 4. GEO Enhancement

Add elements that make refreshed content citeable by AI systems:

```markdown
### GEO Enhancements

**Definitions to add**:
- [Term]: "[Clear, standalone definition in 25-50 words]"

**Quotable statistics to add**:
- "According to [Source], [specific stat] as of [year]."

**FAQ section** (add or expand):
- Q: [Question matching common search query]
  A: [Direct answer in 40-60 words]

**Comparison tables** (add where relevant):
| [Factor] | [Option A] | [Option B] |
|----------|-----------|-----------|

**Structured data**: [FAQ schema / HowTo schema / Article schema to add]
```

### 5. Republishing Strategy

```markdown
### Republishing Plan

**URL handling**: [Keep same URL — do NOT change]
**Date update**: Update `dateModified` in schema; update visible "Last updated" date
**Redirect**: [Not needed if URL unchanged]

**Promotion plan**:
1. Share on social with "Updated for [Year]" framing
2. Send to email list as refreshed resource
3. Update internal links pointing to this page
4. Submit URL for re-indexing in Search Console

**Monitoring** (check at 2 weeks, 4 weeks, 8 weeks):
- Position change: [baseline] → [target]
- Traffic change: [baseline] → [target]
- CTR change: [baseline] → [target]
```

## Validation Checkpoints

- [ ] Refresh candidates selected using data (not gut feel)
- [ ] Each candidate has documented issues and a specific plan
- [ ] Outdated statistics replaced with sourced, current data
- [ ] GEO elements added (definitions, stats, FAQ, tables)
- [ ] Title and meta description refreshed
- [ ] Internal links updated
- [ ] Republishing checklist completed

## Tips for Success

1. **Don't just update the date** — Google detects superficial updates. Make substantive changes
2. **Keep the same URL** — changing URLs loses all existing link equity
3. **Focus on pages with existing authority** — refreshing a page with backlinks is easier than creating new content
4. **Add 20-30% new content** — aim for meaningful expansion, not padding
5. **Update schema markup** — especially `dateModified` and any FAQ schema

## Related Skills

- **content-gap-analysis** — identify what's missing across your content
- **seo-content-writer** — write the new/expanded sections
- **geo-content-optimizer** — deep GEO optimization for refreshed content
- **meta-tags-optimizer** — optimize refreshed title and description
- **content-quality-auditor** — run a full quality audit on refreshed content
