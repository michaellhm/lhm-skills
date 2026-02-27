---
name: lp-copy
description: "Write landing page copy for each ad group in a PPC campaign. Use this when the user says 'write landing page copy', 'write copy for the campaign', 'lp-copy', 'write the landing pages', 'create copy for the ad groups', or provides a list of ad groups and keywords. Requires client_profile.md. Produces one copy file per ad group in /lp/copy/."
---

# LP Copy

Write focused, conversion-oriented landing page copy for each ad group in the campaign. Each ad group gets its own page because ad relevance depends on matching the landing page content to the search intent.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/lp-copy/LEARNED.md` — apply any relevant entries
2. Read `client_profile.md` for clinic name, services, tone, USPs, and any brand voice guidelines
3. Read `lp/lp_state.md` if it exists — check the Campaign section for existing ad groups
4. Do NOT write SEO content (no keyword stuffing, no meta descriptions, no schema). This is pure ad landing page copy focused on conversion.

## Step 1: Capture Campaign Structure

The user should provide this in their prompt. If they didn't, ask:

> "Please paste the campaign structure — the ad groups and their main keywords. For example:
>
> **Ad Group: Physiotherapy**
> Keywords: physiotherapy [suburb], physio near me, physiotherapy clinic
>
> **Ad Group: Back Pain**
> Keywords: back pain treatment, back pain physio, back pain specialist"

Parse each ad group name and its primary keywords. Identify the **core search intent** for each:
- What problem is the searcher trying to solve?
- What outcome are they hoping for?
- How urgent is the search?

## Step 2: Plan the Page Structure

Every landing page follows this section sequence. It maps to the health theme prototype sections.

| Section | Purpose |
|---------|---------|
| **Hero** | Match the search intent immediately. Headline + subheadline + CTA |
| **Trust bar** | Google rating, review count, years in practice, qualifications |
| **Pain points** | Name the problem the searcher has. 2-4 specific pains |
| **Solution intro** | Introduce the clinic as the answer. 2-3 sentences |
| **Service features** | 4-6 key things they get. Short and specific |
| **Social proof** | 2-3 testimonials relevant to this ad group's intent |
| **How it works** | 3-4 step process. Reduces friction. |
| **FAQ** | 3-5 objection-handling questions |
| **Locations CTA** | Book now block with nearest clinic details |

## Step 3: Write Copy for Each Ad Group

For each ad group, create `/lp/copy/[ad-group-slug]-copy.md`.

Apply the anti-AI writing guidelines from `client_profile.md` (if present) and from the plugin's CLAUDE.md. Write like a human who knows this specific clinic and these specific patients — not like an agency brief.

**Headline principles:**
- Lead with the outcome or the relief, not the service name
- Match the searcher's language precisely (if they search "back pain physio", say "back pain" not "lumbar dysfunction")
- Be specific: "Back to sport in 4 sessions" outperforms "Expert Sports Physio"

**Copy file template:**

```markdown
---
ad_group: [AD GROUP NAME]
slug: [ad-group-slug]
primary_keywords: [keyword1, keyword2, keyword3]
intent: [pain relief / recovery / performance / prevention]
---

# [AD GROUP NAME] — Landing Page Copy

## Hero Section
**Headline (H1):** [Specific, benefit-led headline matching search intent]
**Subheadline:** [Supporting sentence that qualifies the offer and adds specificity]
**Primary CTA:** [Book Online / Book Your Assessment / Claim Your First Session]
**CTA subtext:** [e.g. "No referral needed. Same-week appointments available."]

## Trust Bar
**Google Rating:** [X.X Stars]
**Review Count:** [Based on [N]+ Google Reviews]
**Supporting stat 1:** [e.g. "15+ years treating [suburb] patients"]
**Supporting stat 2:** [e.g. "AHPRA registered practitioners"]

## Pain Points
**Section heading:** [e.g. "Still struggling with [pain]?"]
- [Specific pain point 1 — what does this feel like for them?]
- [Specific pain point 2]
- [Specific pain point 3]
[Optional line 4]

## Solution Intro
**Subheading:** [e.g. "There's a better way forward."]
[2-3 sentences. Introduce the clinic. What makes the approach different? What result can they expect?]

## Service Features
**Section heading:** [e.g. "What your treatment includes"]
- **[Feature 1]:** [One sentence. Specific, not generic.]
- **[Feature 2]:** [...]
- **[Feature 3]:** [...]
- **[Feature 4]:** [...]
[4-6 features total]

## Social Proof
**Section heading:** [e.g. "What our patients say"]
[Pick 2-3 testimonials from client_profile.md that are relevant to this ad group's pain point. If none exist, write placeholder testimonials that feel authentic and ask Michael to replace them.]

**Testimonial 1:**
> "[Quote]"
> — [First name, Location]

**Testimonial 2:**
> "[Quote]"
> — [First name, Location]

## How It Works
**Section heading:** [e.g. "Getting started is simple"]
1. **[Step title]:** [One sentence description]
2. **[Step title]:** [...]
3. **[Step title]:** [...]
[3-4 steps. The goal: make booking feel low-risk and easy.]

## FAQ
**Section heading:** [e.g. "Common questions"]

**Q: [Objection or practical question 1]**
A: [Direct answer. No fluff. 1-3 sentences.]

**Q: [Question 2]**
A: [...]

**Q: [Question 3]**
A: [...]

[3-5 FAQs. Prioritise cost, time commitment, what to expect, whether a referral is needed.]

## Locations CTA Section
**Section heading:** [e.g. "Book your appointment today"]
**Body copy:** [1-2 sentences. Urgency without being pushy. e.g. "Most patients are seen within 2-3 days."]
**CTA button:** [Primary CTA text]
**Secondary CTA:** [e.g. "Call us: [PHONE]"]
```

## Step 4: Calibrate Across Ad Groups

After writing all ad group copy files, review them side by side. Check:
- Each hero headline is distinct and matches its specific search intent
- Pain points are different enough across pages (back pain ≠ neck pain ≠ sports injury)
- Testimonials are varied (don't use the same quote twice)
- CTAs are consistent in tone but can vary in phrasing

If any two pages feel interchangeable, revise the hero and pain points sections to be more specific.

## Step 5: Update State File

Update `/lp/lp_state.md` — Campaign section:

```markdown
## Campaign
- **Brief**: /lp/campaign_brief.md
- **Ad Groups**:
  - [ad-group-slug-1]: /lp/copy/[ad-group-slug-1]-copy.md ✅
  - [ad-group-slug-2]: /lp/copy/[ad-group-slug-2]-copy.md ✅
```

Also write `/lp/campaign_brief.md`:

```markdown
# Campaign Brief

## Client
[CLINIC_NAME]

## Campaign Goal
[What the ads are trying to achieve — bookings, calls, form fills]

## Ad Groups and Keywords

### [Ad Group 1]
- **Primary keyword**: [keyword]
- **Supporting keywords**: [keyword2, keyword3]
- **Intent**: [pain relief / recovery / performance]
- **Copy file**: /lp/copy/[slug]-copy.md

### [Ad Group 2]
...
```

## Step 6: Handoff

Tell the user:

> "Copy written for [N] ad groups:
>
> [List each ad group with file path]
>
> Review the copy files and mark any sections for revision before running **lp-prototype**. Key things to check: hero headlines feel specific to the search intent, pain points sound like things real patients say, testimonials are real (replace placeholders if I've added any)."
