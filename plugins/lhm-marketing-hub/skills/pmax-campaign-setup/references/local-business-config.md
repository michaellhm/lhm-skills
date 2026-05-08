# Local Business PMax Configuration - Field-by-Field Defaults

This is the canonical defaults table for an Australian local-service-business PMax campaign. The setup skill writes these into the build spec unless the user explicitly overrides them.

## Campaign Settings

| Field | Local-Business Default | Why |
|-------|------------------------|-----|
| Objective | Leads | PMax for local services drives leads, calls, and visits. Sales objective is for eCommerce. |
| Campaign type | Performance Max | The campaign type itself. |
| Campaign sub-type | None | PMax doesn't have a "for local lead gen" sub-type - settings below configure it. |
| Conversion goals | Account-level conversion goals, primary = form submit + qualified call. Secondary = location actions, lead form, contact-page view. | Mixed-mix matches how local clients convert. Calls are dominant for clinics. |
| Bid strategy | Maximise Conversions, optionally with tCPA = target CPL × 0.9 | Smart bidding works without targets early; introduce tCPA when conv data is reliable (≥ 50/30 days). |
| Daily budget | (target CPL × monthly lead target) ÷ 30 | Simple derivation. Floor: 2 × tCPA so the bid algorithm has room. |
| Customer acquisition | "Bid equally for new and existing customers" by default | Prevents over-spend on already-known customers; flip if remarketing-only is the goal. |
| Final URL expansion | OFF for first 30 days | Locks traffic to the approved LP while there's only one. Re-evaluate at 30-day mark. |
| URL exclusions | Add `/blog/*`, `/news/*`, `/jobs/*`, `/careers/*` | Common irrelevant URLs that sometimes leak in if expansion is later turned on. |

## Geo Targeting

| Field | Local-Business Default | Why |
|-------|------------------------|-----|
| Location options | "Presence: People in or regularly in your targeted locations" | NEVER "Interest". Interest sends ads to people merely searching about a location. |
| Locations | Radius around primary clinic + named suburbs | Layered approach beats a single city radius. |
| Default radius (metro) | 10–20 km | Adjust to match how far patients realistically travel. |
| Default radius (regional) | 30–50 km | Larger catchment in regional Australia. |
| Location exclusions | Suburbs the clinic does not service | Reduces wasted spend when the radius accidentally bleeds into them. |

## Languages

- **English** by default.
- Add additional languages **only** if a translated landing page exists. Setting a language without a translated LP wastes spend.
- Common additions for clinics: Mandarin, Cantonese, Vietnamese, Arabic, Greek, Italian.

## Ad Schedule

- **24/7** by default.
- Restrict to business hours + 1 hour either side **only after** week-4 data shows calls outside hours don't convert.
- Never restrict at launch - the algorithm needs every signal it can get.

## Devices

- All devices, default bid adjustment.
- Do not bid-adjust by device at launch. PMax handles it.

## Conversion Tracking

- Form submit (web event tag).
- Phone call ≥ 30 seconds (call asset OR call-conversion code on website).
- Location action (linked from Google Business Profile).
- Lead form asset submit (only if lead form asset is used).
- Contact-page view (counted as Secondary, not Primary, to avoid inflating the conversion count).

## Account-Level Assets (required vs optional)

| Asset | Status | Notes |
|-------|--------|-------|
| Sitelinks (4–8) | Required | Services, About, Contact, Book Online, Locations |
| Callouts (4–6) | Required | "AHPRA Registered", "HICAPS On-Site", "Bulk-Billed Available" (only if true) |
| Structured snippets | Required | Header = "Services" |
| Location asset | Required | Linked Google Business Profile |
| Call asset | Required | Tracked call-forwarding number recommended |
| Lead form asset | Optional | Useful for top-of-funnel asset groups |
| Promotion asset | Optional | Only if a real, time-bounded promotion exists |
| Image extensions | N/A in PMax | Images live in asset groups |
| Price asset | Avoid for AHPRA | Pricing claims can breach AHPRA |

## Bid Strategy Switch Points

| Trigger | Action |
|---------|--------|
| Day 1–14 | Maximise Conversions, no target |
| Day 15–30 | Hold the strategy, observe pacing and CPL |
| ≥ 50 conv in 30 days AND CPL stable | Switch to tCPA = target CPL × 0.9 |
| < 30 conv in 30 days at week 4 | Stay on Maximise Conversions; review LP, audience signals, asset coverage in `pmax-optimizer` |

## What Local-Business PMax Is NOT

- Not Shopping. No product feed.
- Not Discovery. PMax replaces Discovery as of 2024 anyway.
- Not Smart Campaigns. Smart Campaigns are deprecated for advertisers running modern PMax.
- Not Local Campaigns. Local Campaigns were folded into PMax in 2022. Use the location asset + store-visit goal instead.

## When to Run a Second PMax (Not One Mega-Campaign)

Run a second PMax when **one of these** is true:

- Distinct service lines have very different target CPLs (> 1.5× variance).
- One service line accounts for > 60% of the budget and is being held back by the others.
- Campaign hits ≥ $5,000 / month spend and has stable, distinct asset groups by service.

Otherwise, keep services as **separate asset groups** within a single PMax until scale justifies a split.
