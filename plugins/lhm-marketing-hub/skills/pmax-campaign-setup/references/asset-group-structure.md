# Asset Group Structure for Local-Business PMax

PMax campaigns lean on asset groups the way old Search campaigns lean on ad groups. Get the split right and everything else gets easier.

## The Rule for Local Services

**Split asset groups by service line, not by suburb.**

A single dental practice with implants, Invisalign, and cosmetic should run **three asset groups in one PMax**. Not three campaigns. Not three suburb-themed groups. Three service-line groups, each with its own copy, image set, audience signal, and final URL pointing at the matching service landing page.

Suburb splits only become useful at the 90-day strategic review when there's enough data to prove a suburb-specific group converts differently from the same group on average.

## Naming Convention

Use this format so the operator can read the spec at a glance:

```
[Service Line] - [Funnel Stage] - [Theme/CTA]
```

Examples:
- `Implants - BOF - Free Consult`
- `Invisalign - MOF - How It Works`
- `Cosmetic - TOF - Education`

Funnel-stage tags map to the `pmax-banner-generator` outputs:
- **TOF** - top of funnel, no offer, education-led, "Learn more" CTA.
- **MOF** - middle of funnel, process-led, "Check availability" CTA.
- **BOF** - bottom of funnel, action-led, "Book online" / "Call now" CTA.

Most local clinics run TOF + BOF for each service. Add MOF only when there's a genuine consideration phase (high-ticket cosmetic, surgery, big-decision allied health).

## Slot Coverage Per Group

Aim to fill every slot. PMax rewards asset coverage.

| Asset type | Slots | Source |
|------------|-------|--------|
| Headlines (≤ 30 chars) | 15 max | `pmax-banner-generator` CSV |
| Long headlines (≤ 90 chars) | 5 max | `pmax-banner-generator` CSV |
| Descriptions (≤ 90 chars) | 5 max | `pmax-banner-generator` CSV |
| Images (1.91:1, 1:1, 4:5) | 20 max combined | Generated from image prompts |
| Logos (1:1 + 4:1) | 5 max combined | Brand assets |
| Videos (≥ 10s, 9 different orientations) | 5 max | Optional but recommended; auto-generated from images if not supplied |
| Business name | 1 (campaign level) | `client_profile.md` |
| Final URL | 1 per group | Service-specific LP |
| Display path 1 + 2 | 1 each | Match the LP |
| Call to action | 1 from Google's preset list | Funnel-stage match |

A group missing logos or video will be marked "Incomplete" by Google and may serve less. Always note logo/video gaps in the spec.

## Final URL Per Group

Each asset group **must** point to the service-specific landing page. Never to the homepage. Never to a generic "services" page.

If the LP doesn't exist yet, route the operator to `landing-page-optimizer` before continuing.

## When to Add a Suburb Layer

After the first 90-day review, consider a suburb-themed group **if**:

- One suburb consistently spends > 25% of the campaign's budget AND
- That suburb's CPL is > 30% better or worse than the campaign average AND
- A suburb-specific landing page exists or is being built

Suburb splits without a matching landing page are wasted effort.

## Common Splits to Avoid

- **One mega-group with everything in it.** PMax can't optimise creative when "Implants" and "Invisalign" headlines are mixed.
- **Splitting by ad type** ("video group", "image group"). Asset groups already handle this - they're a creative bundle, not a media-type bundle.
- **Splitting by audience signal** (e.g. "Existing customers" group, "New customers" group). Use the campaign-level customer-acquisition setting and audience signals instead.
- **Splitting by intent stage** without service-line context (e.g. one "TOF" group across all services). Education content for implants is not the same as education for Invisalign.

## Worked Example - 3-Service Dental Clinic

Single PMax campaign, 6 asset groups:

1. `Implants - TOF - Education`
2. `Implants - BOF - Free Consult`
3. `Invisalign - TOF - Education`
4. `Invisalign - BOF - Book Assessment`
5. `Cosmetic - TOF - Education`
6. `Cosmetic - BOF - Book Consult`

Each with its own LP, audience signal, and AHPRA-checked copy. Total: 6 groups. Manageable, distinct, and gives the algorithm clear creative buckets.

## Worked Example - 1-Service Solo Practitioner (Physio)

Single PMax campaign, 2 asset groups:

1. `General Physio - TOF - Pain Education`
2. `General Physio - BOF - Book Assessment`

Don't over-engineer. Two well-built groups beat six half-finished ones.
