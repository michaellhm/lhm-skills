---
name: pmax-campaign-setup
description: Build a complete Performance Max campaign spec for an Australian local-service business (clinic, allied health, cosmetic, professional services - not eCommerce). Use this when the user mentions "set up a PMax campaign", "new Performance Max", "build a PMax campaign", "PMax setup", "launch Performance Max", "performance max for clinic", "performance max for practice", or "PMax for local business". Outputs a full campaign-build spec ready to enter into Google Ads Editor or the UI, covering objective, conversion goals, geo targeting, bid strategy, asset group structure, audience signals, budget, account-level assets, and a launch checklist.
---

# PMax Campaign Setup (Local Business)

## Purpose

Plan a complete Performance Max campaign for an **Australian local-service business** - clinics, allied health, cosmetic, and professional services that drive **leads, calls, and store visits**, not online sales. Produce a single Markdown build spec the operator hands into Google Ads Editor or the UI.

This skill does NOT auto-build the campaign in Google Ads. It plans, validates, and writes the spec. Final entry happens in the Google Ads UI / Editor.

## CRITICAL - Local Business Only

Refuse and reroute if any of the following are true:

- The business is an eCommerce / Shopping site with a product feed.
- The user wants Merchant Center, product groups, or Shopping ads under the PMax umbrella.
- The conversion goal is online product purchase, not a lead, call, or visit.

For eCommerce PMax, this skill does not apply. Tell the user and stop.

## When to Use

- Launching a brand-new PMax campaign for a clinic or service business
- Replacing an old Search-only campaign with a Search + PMax structure
- Adding a second PMax campaign (e.g. one per service line) once an existing PMax has hit scale
- Migrating from Smart Campaigns or Local Campaigns to a modern PMax setup

## Prerequisites

Before doing anything else, read three files:

1. `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json` - applies to every line of output you write into the spec.
2. `${CLAUDE_PLUGIN_ROOT}/skills/pmax-campaign-setup/LEARNED.md` - apply any prior-session learnings to this run.
3. `client_profile.md` for the active client.

Then verify these prerequisites. If any are missing, route the user to the named skill before continuing.

| Prerequisite | If missing, route to |
|--------------|----------------------|
| Landing page exists and converts | `landing-page-optimizer` |
| Conversion tracking validated (form, call ≥30s, location action) | `analytics-tracking` or `ga-event-config` |
| PMax creative CSV (headlines, descriptions, image prompts) | `pmax-banner-generator` |
| Account access under MCC `394-736-1921` | Confirm CID via `mcp__GoogleAds__list_accessible_accounts` |
| Google Business Profile linked at the account level | Ask the user to link before launch |

The skill should refuse to write the spec if **any** of the first three are missing. Confirm gates explicitly with the user.

## Mandatory Discovery Questions

Ask these as a single block (use the `AskUserQuestion` tool where multi-select makes sense). Do not invent answers.

1. **Clinic / business name** and **child account CID**.
2. **Service lines to promote in this campaign** (max 3 per campaign - split into a second PMax if more are needed).
3. **Service area**: primary location address + radius in km, plus any named suburb inclusions and exclusions.
4. **Monthly budget** in AUD.
5. **Target CPL** (cost per lead, AUD).
6. **Primary call-to-action**: book online, call now, or form submit.
7. **Brand exclusion list**: any sister clinics or competitor brands to suppress.
8. **Existing PMax campaigns** under this account (if any - pull via GAQL to confirm naming collisions).

If the user can't supply target CPL, derive a placeholder from `client_profile.md` and flag it for the user to confirm before launch.

## Build the Campaign Spec

Each subsection below becomes a section in the output `.md` file. Apply the local-business default unless the user has a specific override.

For the full field-by-field defaults table with rationale for each value, read `references/local-business-config.md`.

### Objective
Set to **Leads**. Never Sales. Never "Drive Online Sales". The Local Store Visits secondary goal can be added once Google Business Profile is linked.

### Conversion Goals
- **Primary**: form submit + qualified phone call (≥ 30 seconds, recorded via call asset or call-only conversion).
- **Secondary**: location actions (directions, calls from Maps), contact-page view, lead form asset submit.
- Each goal weighted (e.g. form submit = 1.0, qualified call = 1.0, location action = 0.3, page view = 0.1). Document weights in the spec.

For full setup detail and a verification GAQL query, read `references/conversion-tracking-checklist.md`.

### Bid Strategy
Default: **Maximise Conversions** with optional `tCPA = target CPL × 0.9`.

Note in the spec:
- Switch to tCPA only after the campaign has > 50 conversions in 30 days.
- Avoid Max Conversion Value with tROAS for lead-gen local until lead values are reliable and > 50 weighted conversions/month.

### Budget
`Daily budget = (target CPL × target leads / month) ÷ 30`.
Floor: at least `2 × tCPA` so the algorithm has bid room.
Note in the spec: PMax under-pacing is common in week 1; allow 14 days before adjusting.

### Geo Targeting
- **Location options → "Presence: People in or regularly in your targeted locations"**. NEVER "Interest". This is a hard rule.
- Include: primary address radius (default 10–20 km for metro, 30–50 km for regional) **plus** named suburbs from the discovery questions.
- Exclusions: any suburbs the clinic does not service. List them explicitly in the spec.

### Languages
- English by default.
- Add community languages if the clinic markets to specific community groups (e.g. Mandarin, Vietnamese, Arabic) and the LP has a translated variant.

### Final URL Expansion
**OFF** for the first 30 days. Re-evaluate at the 30-day mark in the optimisation skill. Reasoning to record in the spec: prevents the algorithm from sending traffic to non-relevant pages while there's only one approved LP.

### Ad Schedule
Run 24/7 by default. If the conversion goal is calls-only, restrict to business hours + 1 hour buffer either side, but only after launch data justifies it (week 4+).

### Asset Groups
One asset group per service line. Reuse the CSV produced by `pmax-banner-generator`.

For local-business asset group structure, splitting rules, and naming, read `references/asset-group-structure.md`.

### Audience Signals (per asset group)
PMax audience signals are **suggestions**, not targeting. Provide them anyway - they meaningfully improve early performance.

For each asset group, provide:
- **Customer Match** list (existing patient list - only if compliant under privacy rules; see `references/audience-signals.md` for AHPRA / Privacy Act considerations).
- **Custom Segments** (intent-based search terms specific to the service line).
- **In-market** segments (Health & Wellness, Home & Garden Services, etc., depending on the service).
- **Detailed Demographics** where relevant (life events, parental status - only when truly relevant; demographic targeting cannot be used to discriminate).

For the full configuration with examples, read `references/audience-signals.md`.

### Account-Level Assets
List in the spec, marking each as required or optional:
- **Sitelinks** (4–8): Services, About, Contact, Book Online, Locations, Pricing (where AHPRA-compliant).
- **Callouts** (4–6): "AHPRA Registered", "HICAPS On-Site", "Open Saturdays" (only if true), etc.
- **Structured snippets**: "Services" header listing each service.
- **Location assets**: Google Business Profile linked. Required for local PMax.
- **Call assets**: Required. Use a tracked call-forwarding number.
- **Lead form asset**: Optional. Useful for top-of-funnel asset groups.
- **Promotion assets**: Only if a real promotion exists; AHPRA-compliant copy only.

All asset copy must pass the AHPRA banned-language check.

### Brand Exclusions and Negative Keywords
- **Brand exclusions list** (account level): apply branded competitor terms the client wants suppressed.
- **Account-level negative keyword list**: Pull existing list via GAQL. If none exists, create one named `[Client] – Master Negatives` and seed with: free, jobs, careers, salary, course, training, DIY, near me [unrelated suburb], plus any banned non-target services.

For the GAQL queries to verify both, read `references/launch-checklist.md`.

### Conversion Action Validation
Before launch, run the verification GAQL queries in `references/conversion-tracking-checklist.md` to confirm each conversion action is **Active**, has the correct counting method (One vs Every), and is included in the Goals page used by the campaign.

## AHPRA Compliance Gate

Every text field in the spec - sitelinks, callouts, promotion copy, structured snippets - runs through the banned-phrase check. Reuse the banned-language list from `pmax-banner-generator/references/ahpra-pmax.md`. Never write "guarantee", "best", "cure", "expert", testimonials, before/after, or sensational outcome claims.

If the client is non-healthcare (e.g. legal, accounting, trades), AHPRA does not apply but the relevant industry compliance equivalent does (e.g. Australian Solicitors Conduct Rules, ACCC misleading-conduct rules). Flag any spec field that makes an outcome claim regardless of industry.

## Google Ads MCP Usage (read-only)

This skill plans the campaign; it does not auto-build. Use the MCP for verification and discovery only:

| Purpose | Tool | Notes |
|---------|------|-------|
| Confirm CID | `mcp__GoogleAds__list_accessible_accounts` | Filter under MCC 394-736-1921 |
| Avoid duplicate campaign names | `mcp__GoogleAds__execute_gaql` | `SELECT campaign.id, campaign.name FROM campaign WHERE campaign.status != 'REMOVED'` |
| List existing conversion actions | `mcp__GoogleAds__execute_gaql` | See `references/conversion-tracking-checklist.md` |
| List existing audiences | `mcp__GoogleAds__execute_gaql` | `SELECT user_list.id, user_list.name, user_list.size_for_display FROM user_list` |
| List existing negative keyword lists | `mcp__GoogleAds__execute_gaql` | `SELECT shared_set.id, shared_set.name FROM shared_set WHERE shared_set.type = 'NEGATIVE_KEYWORDS'` |

If the MCP is unavailable, ask the user for a CSV export and document the gap in the spec.

## Output

Save the spec to:

```
clients/<client-slug>/google_ads/YYYY-MM/pmax-setup-<campaign-slug>-YYYY-MM.md
```

Structure:

```markdown
# PMax Campaign Build Spec - [Client]
Date: [YYYY-MM-DD]
Author: Claude (pmax-campaign-setup)

## Account
- MCC: 394-736-1921
- CID: [child CID]
- Campaign name: [Client – PMax – Service line(s)]

## Objective & Bidding
[Filled section]

## Budget
[Filled section]

## Geo & Schedule
[Filled section]

## Asset Groups
[One subsection per group with reference to the pmax-banner-generator CSV row range]

## Audience Signals
[Per asset group]

## Account-Level Assets
[Sitelinks, callouts, structured snippets, location, call, lead form, promotion]

## Brand Exclusions & Negative Keywords
[Filled section]

## Pre-Launch Checklist
[Pulled from references/launch-checklist.md, checked off]

## Notes / Open Questions
[Anything the operator should clarify before pressing Publish]
```

## Hand-off to Next Skills

At the end of the run, name the next skills the operator should run:

- If creative isn't yet built → `pmax-banner-generator`.
- After the campaign is live → schedule `pmax-optimizer` at +14 days for the first sense-check, then monthly thereafter.
- If conversion tracking gaps surfaced → `analytics-tracking` or `ga-event-config`.

## Related Skills

- **pmax-banner-generator** - generates the asset CSV consumed here.
- **pmax-optimizer** - runs monthly + 90-day optimisation passes once the campaign is live.
- **landing-page-optimizer** - must pass before launch.
- **bid-budget-optimizer** - for budget reallocation across an account that includes this campaign.
- **google-ads-monthly-review** - account-level zone check that may flag this campaign.

## Reference Files

- `references/local-business-config.md` - every campaign field with default + rationale.
- `references/asset-group-structure.md` - service-line vs suburb splits, naming, slot rules.
- `references/audience-signals.md` - Customer Match, Custom Segments, demographics, AHPRA / Privacy Act.
- `references/conversion-tracking-checklist.md` - required conversion actions + verification GAQL.
- `references/launch-checklist.md` - 25-point sign-off list before going live.

---

*Plan it once. Build it right. Then optimise on cadence.*
