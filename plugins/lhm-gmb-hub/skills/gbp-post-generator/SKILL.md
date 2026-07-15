---
name: gbp-post-generator
description: "Generate 13 weekly Google Business Profile posts (one 3-month cycle) for a client, rotating between service highlights, tips, seasonal content, and team spotlights. Use this when the user mentions 'generate GBP posts for [Client]', 'GBP posts', 'weekly posts', 'Google Business posts', 'GBP content calendar', or 'post schedule'. Also use this to shorten an existing 52-week/12-month calendar down to the current 3-month cycle length."
---

# GBP Post Generator

Generates one 3-month cycle's worth (13 weekly posts) of Google Business Profile posts in CSV format, rotating between service highlights, tips, seasonal content, and team spotlights. All posts are AHPRA compliant and follow anti-AI writing guidelines.

The GMB program runs in 3-month cycles (see `gmb-project-manager`) — the post calendar is scoped to match, so it's fully consumed and reviewed within the cycle it belongs to rather than going stale for 9 months. Generate a fresh 13-post batch at the start of each new cycle (Month 0) rather than trying to plan a year up front.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gbp-post-generator/LEARNED.md`
2. Read `client_profile.md` for services, modality, brand voice, and location
3. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
4. If healthcare client: read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`
5. Check `[client_folder]/gmb/onboarding/` for an existing calendar file. If one exists with more than 13 rows (e.g. a legacy `gbp_posts_52_weeks.csv` from before the 3-month scope change), **don't regenerate from scratch** — go to Step 0 below instead.

## Step 0: Shortening an existing long calendar (legacy clients only)

If a legacy 52-week/12-month calendar file already exists for this client:
1. Read it in full.
2. Keep only the first 13 rows (weeks 1–13 / the first ~3 months from its start date) — these are the posts closest to being reviewed/scheduled and most likely already brand-voice-approved or in progress.
3. Write the trimmed result to `[client_folder]/gmb/onboarding/gbp_posts_3_months.csv` (new filename — see Output). Do not overwrite the original file; leave it in place as a historical artifact.
4. Note in `GMBProjectManagement.md` that the calendar was shortened from 52 to 13 weeks to match the 3-month cycle length, and that weeks 14–52 of the old file were dropped (a fresh 13-post batch will be generated at the start of the next cycle instead).
5. Skip Steps 1–4 below — go straight to Step 5 (CSV output, already done) and Step 6 (update PM doc).

If no existing calendar (or an existing 13-or-fewer-row one) is found, proceed with the normal generation workflow below.

## Workflow

### 1. Gather Client Context

From `client_profile.md`, extract:
- All services offered (for service highlight posts)
- Primary modality and specialisations
- Brand voice and tone preferences
- Location and local area details (for seasonal/local content)
- Team information (if available, for team spotlight posts)

### 2. Plan Post Rotation

Distribute 13 posts (one 3-month cycle, weekly) across 4 categories:
- **Service highlights** (4 posts): Showcase individual services, what they involve, who they help
- **Tips and advice** (4 posts): Practical tips related to the client's field
- **Seasonal content** (3 posts): Tie services to the actual season/local events/awareness weeks falling within this specific 3-month window — don't reach for a generic year-round rotation, use what's genuinely current
- **Team spotlights** (2 posts): Introduce team members, qualifications, specialisations

Vary the rotation so the same category never appears 3 weeks in a row.

### 3. Generate First 4 Posts for Review

Write the first 4 posts (one from each category, or as close as the 13-post split allows) and present to the user:
- Each post: 150-300 words
- Natural, conversational tone (not marketing-speak)
- AHPRA compliant (no outcome claims, no superlatives, no testimonials)
- Follows anti-AI writing guidelines (no em dashes, no rule of 3, varied structure)
- Include a CTA linking to a relevant page on the client's website

Ask the user: "Here are the first 4 posts as samples. Are you happy with the tone and style? Any adjustments before I generate the remaining 9?"

### 4. Generate All 13 Posts

Once the user approves the samples, generate all 13 posts following the same style and guidelines.

For each post, include:
- **Week Number** (1-13)
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

Mark "13 weekly GBP posts generated (3-month cycle)" as complete with today's date.

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| None required | — | Fully functional without any MCPs |

## Output

- `[client_folder]/gmb/onboarding/gbp_posts_3_months.csv`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Note: Posts need human review for brand voice before scheduling in GBP
