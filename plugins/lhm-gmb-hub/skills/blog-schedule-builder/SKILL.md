---
name: blog-schedule-builder
description: "Generate a 3-month blog content schedule (topics, target keywords, publish dates) for a client, matching the GMB program's 3-month cycle length. Posts-per-month is client-specific, read from GMBProjectManagement.md. Use this when the user mentions 'blog schedule for [Client]', 'blog content calendar', 'blog plan', 'quarterly blog schedule', or '3 month blog plan'."
---

# Blog Schedule Builder

Generates a 3-month blog content schedule for a client: topics, target keywords, publish dates, and internal-link targets. Scoped to 3 months to match the GMB program's cycle length (see `gmb-project-manager`) — regenerate a fresh schedule at the start of each new cycle rather than planning a year at once.

Posts-per-month varies by client (budget, content team capacity, existing cadence) and is not assumed — it's read from `GMBProjectManagement.md`, confirmed with the user, and stored there for future runs.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/blog-schedule-builder/LEARNED.md` if it exists
2. Read `client_profile.md` for services, modality, ICP, brand voice, and location
3. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
4. If healthcare client: read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md`
5. Read `[client_folder]/gmb/GMBProjectManagement.md`

## Workflow

### 1. Determine posts per month

Read the **Blog Posts Per Month** field from the PM doc's Overview section.

- **If present:** use it, but sanity-check against reality — look for an existing blog folder or content plan (e.g. `content-strategy/*.csv`, `blog_draft/`) and compare actual recent publishing cadence against the stated figure. If they've drifted apart, flag the mismatch to the user before proceeding rather than silently trusting the stale number.
- **If missing:** this is a legacy client doc from before this field existed. Look for an existing content plan or blog folder to infer a sensible default cadence (count posts published over a recent 3-month window), propose it to the user, confirm, then write it into the PM doc's Overview section via the `gmb-project-manager` skill so future runs don't need to ask again.
- **If no signal at all:** ask the user directly. Don't default silently — cadence has real cost/resourcing implications for the team.

### 2. Gather topic inputs

Pull topic candidates from whatever's already been produced for this client, in priority order:
1. `gmb/onboarding/entity_map.md` (if it exists) — competitor content-gap analysis is the strongest signal for what to write about next
2. `gmb/onboarding/site_architecture.md` (if it exists) — flags missing page types/silos
3. Any existing `content-strategy/*.csv` or similar content plan — check what's already been covered so you don't repeat a topic, and match the existing format/column conventions if the client already has one
4. `client_profile.md` — services, ICP, objections, revenue drivers, key differentiators
5. If none of the above exist yet, do lightweight competitor/keyword research directly (reuse `run-local-diagnostic` output if available) rather than inventing topics from nothing

Prioritise topics that a) fill a confirmed content gap, b) target genuine search demand, and c) tie into services/pages the client actually wants more bookings for. Don't just generate generic "10 tips for X" filler.

### 3. Build the schedule

Total posts = (posts per month) × 3. Distribute roughly evenly across the 3 months (some clustering is fine — don't force perfectly even spacing if a topic genuinely belongs earlier, e.g. seeding content ahead of a page launch).

For each post, produce:
- **Publish Date** (spread across the 3-month window, matching the client's usual weekday if there's an existing cadence — e.g. Align Health Co has historically published biweekly on Tuesdays)
- **Article Title**
- **Main Keyword**
- **Search Volume / Competition** (if keyword data is available via a keywords/SEO MCP; otherwise estimate qualitatively and say so)
- **Target URL** (new or existing page it should live at / support)
- **Modality/Service** it supports
- **ICP** (who this is for, pulled from `client_profile.md`)
- **Internal Link Destinations** (which existing pages it should link to/from)
- **Strategic Note** (why this topic, why now — tie back to the gap/objection/priority it addresses)

Match column conventions to any existing content plan CSV for this client if one exists, so the new schedule slots into the same tracking sheet rather than creating a second incompatible format.

### 4. Compliance pass

For healthcare/regulated clients, sanity-check every title/angle against the AHPRA framework (or equivalent) before finalising — no outcome guarantees, no superlative claims, no testimonial-driven titles.

### 5. Output as CSV

```
Publish Date, Article Title, Main Keyword, Monthly Search Volume, Competition Score, Target URL, Modality, ICP, Internal Link Destination, Strategic Note
```

### 6. Update GMBProjectManagement.md

Mark "Blog content schedule generated (3 months)" as complete with today's date. Note the posts-per-month figure used and where it came from (existing field / inferred / user-confirmed).

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Keyword research MCP (e.g. `keywords-everywhere`) | Search volume / competition data | Estimate qualitatively, label as unverified |
| GSC MCP | Cross-check against actual query data | Skip, use keyword tool or profile-based estimate only |

## Output

- `[client_folder]/content-strategy/blog_schedule_[start-month]-[end-month]-[year].csv` (match existing naming convention if a content-strategy folder already exists) — falls back to `[client_folder]/gmb/onboarding/blog_schedule_3_months.csv` if there's no existing content-strategy folder
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` (task completion + Blog Posts Per Month field if it was missing/inferred)
- Note: schedule needs human review for priority/voice before writers start producing drafts
