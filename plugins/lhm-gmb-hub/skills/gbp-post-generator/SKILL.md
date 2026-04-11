---
name: gbp-post-generator
description: "Generate 52 weekly Google Business Profile posts for a client, rotating between service highlights, tips, seasonal content, and team spotlights. Use this when the user mentions 'generate 52 GBP posts for [Client]', 'GBP posts', 'weekly posts', 'Google Business posts', 'GBP content calendar', or 'post schedule'."
---

# GBP Post Generator

Generates a full year of 52 weekly Google Business Profile posts in CSV format, rotating between service highlights, tips, seasonal content, and team spotlights. All posts are AHPRA compliant and follow anti-AI writing guidelines.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gbp-post-generator/LEARNED.md`
2. Read `client_profile.md` for services, modality, brand voice, and location
3. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
4. If healthcare client: read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`

## Workflow

### 1. Gather Client Context

From `client_profile.md`, extract:
- All services offered (for service highlight posts)
- Primary modality and specialisations
- Brand voice and tone preferences
- Location and local area details (for seasonal/local content)
- Team information (if available, for team spotlight posts)

### 2. Plan Post Rotation

Distribute 52 posts across 4 categories:
- **Service highlights** (~15 posts): Showcase individual services, what they involve, who they help
- **Tips and advice** (~15 posts): Practical tips related to the client's field
- **Seasonal content** (~12 posts): Tie services to seasons, holidays, local events, awareness months
- **Team spotlights** (~10 posts): Introduce team members, qualifications, specialisations

Vary the rotation so the same category never appears 3 weeks in a row.

### 3. Generate First 4 Posts for Review

Write the first 4 posts (one from each category) and present to the user:
- Each post: 150-300 words
- Natural, conversational tone (not marketing-speak)
- AHPRA compliant (no outcome claims, no superlatives, no testimonials)
- Follows anti-AI writing guidelines (no em dashes, no rule of 3, varied structure)
- Include a CTA linking to a relevant page on the client's website

Ask the user: "Here are the first 4 posts as samples. Are you happy with the tone and style? Any adjustments before I generate all 52?"

### 4. Generate All 52 Posts

Once the user approves the samples, generate all 52 posts following the same style and guidelines.

For each post, include:
- **Week Number** (1-52)
- **Post Date** (starting from the next Monday after today, weekly)
- **Post Type** (Service Highlight / Tip / Seasonal / Team Spotlight)
- **Post Content** (150-300 words)
- **CTA Link** (URL to relevant page on client's website)

### 5. Output as CSV

Format the output as a CSV file with columns:
```
Week Number, Post Date, Post Type, Post Content, CTA Link
```

Ensure the Post Content column properly escapes any commas or quotes.

### 6. Update GMBProjectManagement.md

Mark "52 weekly GBP posts generated" as complete with today's date.

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| None required | — | Fully functional without any MCPs |

## Output

- `[client_folder]/gmb/onboarding/gbp_posts_52_weeks.csv`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Note: Posts need human review for brand voice before scheduling in GBP
