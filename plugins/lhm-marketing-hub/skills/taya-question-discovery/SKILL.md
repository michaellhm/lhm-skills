---
name: taya-question-discovery
description: "Run a full 'They Ask, You Answer' question discovery process for a business or industry. Use this when the user mentions 'They Ask You Answer', 'TAYA', 'content questions', 'buyer questions', 'what questions should I answer', 'question bank', 'Big 5 content', 'what are my customers searching for', or wants to build an article marketing plan based on real buyer questions. Also trigger when a user asks to identify content gaps using buyer intent, build a question-driven content calendar, or discover what their audience is asking online."
---

# They Ask, You Answer — Question Discovery Skill

## What This Skill Does

Runs a structured question discovery process for any business or industry, grounded in Marcus Sheridan's They Ask, You Answer methodology. The output is a prioritised question bank organised by the Big 5 content categories, ready to feed into an article marketing calendar.

The process combines web research (search trends, competitor content, forums, review sites) with structured prompting to surface the questions real buyers are asking. This replaces the manual "sit down and brainstorm" approach with a research-backed question list.

---

## Before Starting

1. **Read client context** — check for `client_profile.md` in the client folder. Use business type, services, location, target audience, and any compliance constraints already captured there. Only ask for what's missing.
2. **Read LEARNED.md** — check this skill's LEARNED.md for any accumulated learnings from previous runs.

---

## The Big 5 Framework

Always organise discovered questions into these five buckets. They represent the content categories with the highest buyer intent and trust-building potential:

1. **Pricing and Costs** — What does it cost? How is pricing calculated? What affects the price? Why is it expensive/cheap compared to alternatives?
2. **Problems and Negatives** — What are the downsides? When is this NOT the right choice? What can go wrong? What are the limitations?
3. **Comparisons** — How does this compare to alternatives? [Option A] vs [Option B]? Should I choose X or Y?
4. **Reviews and Best-of** — Best [service type] in [location]? How do I find a good [provider]? What should I look for?
5. **Case Studies and Outcomes** — What results do real clients get? How long does it take to work? What does success look like?

Questions outside these five categories still have value but these are the priority content plays.

---

## Discovery Process

### Step 1: Clarify the Business Context

Before researching, confirm these details. If `client_profile.md` already covers them, skip to Step 2.

Use the `AskUserQuestion` tool to gather anything missing:
- Business type and specific services (e.g. "physiotherapy clinic" is better than "healthcare")
- Primary location/market if local (e.g. "Melbourne, Australia")
- Target patient/customer profile (e.g. "adults 35-60 with chronic pain")
- Any services or topics the client has flagged as sensitive or off-limits

---

### Step 2: Web Research (Run These Searches)

Use `WebSearch` and `WebFetch` to gather question data from multiple sources. Run searches in this order:

**2a. Google Autocomplete and PAA Mining**
Search for the core service terms with question prefixes to simulate what Google surfaces:
- `[service] how much does it cost`
- `[service] vs [main alternative]`
- `is [service] worth it`
- `[service] near me questions`
- `best [service] [location]`
- `[service] problems side effects risks`
- `how long does [service] take to work`
- `what to expect [service] first appointment`

**2b. Reddit and Forum Research**
Search: `site:reddit.com [service] questions` and `[service] forum questions`
Look for threads where people ask about costs, comparisons, fears, and outcomes. These are the unfiltered questions buyers actually have.

**2c. Competitor Content Analysis**
Search: `[service type] FAQ [location]` and `[service] common questions`
Look at what the top-ranking practices are already answering. These are proven content topics. Note any gaps — questions people are asking that no one is properly answering.

**2d. Review Mining**
Search: `[service] reviews complaints` and look at Google Maps reviews for the service type.
One-star and two-star reviews almost always reveal unanswered questions. A complaint like "I didn't know how many sessions I'd need" is a content gap: an article titled "How many physio sessions will I need?" would have prevented that frustration.

**2e. Search Console Data** (if GSC MCP is connected)
Use `get_advanced_search_analytics` to check existing search queries driving impressions but low clicks. Filter for question-format queries. These are questions Google thinks the site is relevant for but the content isn't satisfying. These are high-priority content gaps.

---

### Step 3: Internal Question Sources (Prompt the User)

After completing the web research, present the user with these prompts to add internally-known questions the research may have missed:

> "Here's what I found from research. To fill in the gaps, it helps to add questions your team hears directly. Can you share:
> - The most common question asked before someone books for the first time?
> - The most common question asked when someone finds out the price?
> - The question that makes prospects hesitate or delay?
> - Any question you get asked so often it's become annoying to answer?
> - Anything you wish people knew before coming in?"

Add these to the question bank and categorise them.

---

### Step 4: Compile and Categorise

Organise all discovered questions into the Big 5 categories. For each question include:
- The question itself (written as a searcher would type it)
- Buyer stage: Awareness / Consideration / Decision
- Estimated priority: High / Medium / Low (based on search frequency and buyer intent signals)
- Data source: where it was found (Reddit, review mining, GSC, etc.)

Format as a table for readability.

---

### Step 5: Identify the Content Priorities

After presenting the full list, highlight:

**Quick wins** — Questions with clear buyer intent that no competitor is answering well. These should be written first.

**Trust builders** — The pricing and problems/negatives questions. Most businesses avoid these. Answering them honestly creates disproportionate trust.

**Comparison content** — Any vs/comparison questions for the specific service type. These rank well and capture high-intent traffic.

**Local SEO opportunities** — Best-of and location-specific questions that can drive Google Maps visibility.

---

### Step 6: Output Format

Deliver results as:

1. **Full question bank table** — All questions organised by Big 5 category with priority and buyer stage
2. **Top 10 priority articles** — The highest-impact content to write first, with a suggested title for each
3. **Content gap summary** — 2-3 sentences on where the biggest opportunity sits based on what competitors aren't covering

---

## Notes for Healthcare Clients

When running this process for allied health clients (physio, chiro, podiatry, naturopathy, etc.):

- Pricing questions are especially valuable because most Australian practices don't publish fees online. Being the practice that does is an immediate trust signal.
- AHPRA compliance applies to any content generated from these questions. Questions about outcomes and results need careful framing — avoid before/after language, guarantees, or testimonial-style claims.
- Medicare and private health insurance questions almost always appear in the question bank for healthcare clients. These are high-intent topics worth covering in detail.
- "What's the difference between [modality A] and [modality B]" questions are extremely common in healthcare (physio vs chiro, osteo vs physio, etc.) and perform well.

---

## Example Output Structure

```
## Question Bank: [Business Name/Type] — They Ask, You Answer Discovery

### 1. Pricing and Costs
| Question | Buyer Stage | Priority | Source |
|---|---|---|---|
| How much does physiotherapy cost in Melbourne? | Decision | High | GSC + Reddit |
| Is physio covered by Medicare? | Consideration | High | Autocomplete |
| Why does physio cost more at some clinics? | Consideration | Medium | Review mining |

### 2. Problems and Negatives
...

### Top 10 Priority Articles
1. "How Much Does Physiotherapy Cost in Melbourne? (And What Affects the Price)"
2. ...

### Content Gap Summary
...
```

---

## Output File

Save to: `content-strategy/YYYY-MM/taya-question-discovery-[business-type].md`

---

## Related Skills

- **content-gap-analysis** — Deeper competitive content gap analysis
- **keyword-research** — Pull volume and difficulty data for discovered questions
- **content-strategy** — Plan the full content calendar from the question bank
- **seo-content-writer** — Write the articles from the priority list
- **competitor-alternatives** — Build comparison pages from the vs/comparison questions
