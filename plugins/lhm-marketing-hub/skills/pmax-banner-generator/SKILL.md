---
name: pmax-banner-generator
description: Generate AHPRA-compliant Performance Max banner ad copy and image prompts for Australian healthcare and cosmetic clinics. Outputs a single CSV file ready for Google Ads Editor import with multiple funnel-based asset groups. Use this when users request PMax banners, performance max assets, display ad copy, image prompts, or banner creative for physio, chiro, podiatry, psychology, or cosmetic clients.
---

# PMax Banner Generator

## Purpose

Generate compliant Google Performance Max banner ad copy and image prompts for Australian healthcare and cosmetic clinics. Create structured CSV output with funnel-based asset groups ready for Google Ads Editor import.

This skill focuses on strategy, compliance, copy, and structured output. It does NOT design final banners or export images.

## Supported Industries

- Physiotherapy
- Chiropractic
- Podiatry
- Psychology
- Cosmetic / Aesthetic
- Other healthcare (user-defined)

Industry selection determines compliance strictness and language rules.

## How It Works

### Step 1: Mandatory Questions

Before generating anything, gather these inputs:

**1. Clinic Context**
- What type of clinic is this? (select from supported list or free text)

**2. Conversion Goal**
- Online booking
- Phone calls
- Form enquiries
- Other

**3. Offer Clarity**
- No offer
- Free consult (e.g. 15-minute)
- Intro price
- Other
- Any conditions? (time-limited, new patients only, location-specific)

**4. Landing Page Check**
- Dedicated service page
- General booking page
- Not built yet

**Hard rule:** If no landing page exists, stop and instruct the user to run the **Landing Page Optimizer** skill before continuing.

### Step 2: Brand Inputs

Assume available from context:
- Brand style guide accessible
- Logo, colours, fonts defined
- Image tone can be inferred from brand guide

No brand questions required in this skill.

### Step 3: Generate Funnel-Based Asset Groups

Always produce three or more asset groups grouped by funnel stage:

**Top of Funnel (TOF)**
- Goal: Awareness and education
- Rules: No offers, no urgency, neutral service-led language
- CTA examples: Learn more, Find out more

**Middle of Funnel (MOF)**
- Goal: Consideration and fit
- Rules: May explain approach or process, no testimonials or superiority claims
- CTA examples: Check availability, See how it works

**Bottom of Funnel (BOF)**
- Goal: Action
- Rules: Offers allowed if supplied, clear but not aggressive
- CTA examples: Book online, Call now

### Step 4: Apply Asset Group Naming

Each asset group must follow this format:
```
[FUNNEL STAGE] - [THEME] - [OFFER or ACTION]
```

This allows multiple themes per funnel stage for testing in one PMax campaign.

### Step 5: Generate Copy

**Character Limits:**

| Asset Type | Max Characters | Quantity |
|-----------|---------------|----------|
| Headlines | 30 | Up to 15 per group |
| Long headlines | 90 | Up to 5 per group |
| Descriptions | 90 | Up to 5 per group |
| Business name | 25 | 1 per campaign |

Aim to fill all available slots unless clearly unnecessary.

### Step 6: AHPRA Compliance Check

Every piece of copy is checked against AHPRA rules. See `references/ahpra-pmax.md` for full compliance guide.

**Global Blocked Language:**
- best, guaranteed, cure
- expert, specialist (without qualification)
- testimonials or implied reviews
- before/after claims
- absolute outcomes (fix, eliminate, permanent)

If rewriting occurs, note why in the output.

### Step 7: Generate Image Prompts

Each asset group must include image prompts that:
- Avoid before/after framing
- Avoid exaggerated bodies or transformations
- Avoid text or logos in images
- Prefer real-world, clinical, or neutral visuals

**Prompt Structure:**
- Scene description
- Subject type
- Mood
- Lighting
- Composition
- Negative prompts (what to avoid)

### Step 8: Output CSV

Generate a single CSV file ready for Google Ads Editor import. See `references/csv-format.md` for column specifications.

## Expected Interaction Flow

```
You: I need PMax banners for Bondi Physio - they have a free 15-min consult offer for new patients.

Claude: I'll help create PMax banner assets for Bondi Physio. First, let me gather the required information:

1. **Clinic Type**: Physiotherapy (confirmed)

2. **Conversion Goal**: What's the primary conversion?
   - Online booking
   - Phone calls
   - Form enquiries

3. **Offer**: Free 15-min consult for new patients
   - Any time limit on this offer?
   - Location-specific conditions?

4. **Landing Page**: Where will traffic land?
   - Dedicated service page
   - General booking page
   - Not built yet

You: Online booking, offer runs until March, landing page is ready at bondiphysio.com.au/sports-physio

Claude: Perfect! Generating funnel-based asset groups...

## PMax Assets: Bondi Physio

### Asset Groups Generated

| Group | Funnel | Theme | Headlines | Long Headlines | Descriptions |
|-------|--------|-------|-----------|----------------|--------------|
| TOF - Sports Recovery - Learn More | Top | Education | 15 | 5 | 5 |
| MOF - Our Approach - Check Availability | Middle | Process | 15 | 5 | 5 |
| BOF - Free Consult - Book Now | Bottom | Offer | 15 | 5 | 5 |

### Compliance Summary
- 45/45 headlines COMPLIANT
- 15/15 long headlines COMPLIANT
- 15/15 descriptions COMPLIANT
- 3/3 image prompts COMPLIANT

Ready to generate the CSV file?
```

## Outputs

### 1. PMax Assets CSV

**Filename:** `pmax-assets-[client]-[date].csv`

Single CSV file with all asset groups. Required columns:

```csv
Campaign,Asset Group,Asset Type,Asset Value
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 1,Sports Physio Bondi
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Headline 2,Recovery That Works
...
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Long Headline 1,Professional sports physiotherapy for athletes of all levels
...
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Description 1,AHPRA registered physiotherapists helping you move better. Book your assessment today.
...
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Call to Action,Learn more
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Final URL,https://bondiphysio.com.au/sports-physio
Bondi Physio - PMax,TOF - Sports Recovery - Learn More,Image Prompt,[Scene: Clinical treatment room...]
```

### 2. Implementation Summary (Markdown)

```markdown
## PMax Assets - Bondi Physio
**Date:** [Date]
**Campaign:** Bondi Physio - PMax

### Asset Groups

**TOF - Sports Recovery - Learn More**
- Headlines: 15 (all compliant)
- Long headlines: 5 (all compliant)
- Descriptions: 5 (all compliant)
- CTA: Learn more

**MOF - Our Approach - Check Availability**
[Same structure]

**BOF - Free Consult - Book Now**
[Same structure]

### Image Prompt Summary
1. TOF: Clinical setting, natural light, practitioner with patient
2. MOF: Treatment room, professional equipment, calm atmosphere
3. BOF: Reception area, booking moment, welcoming environment

### Next Steps
1. Import CSV into Google Ads Editor
2. Generate images using prompts (Midjourney/DALL-E/etc)
3. Upload images to asset groups
4. Review and publish campaign
```

### 3. Compliance Report (if issues found)

```markdown
## Compliance Flags

### Headline 8 - REWRITTEN
**Original:** "Best Sports Physio Bondi"
**Issue:** Superlative "best" without substantiation
**Rewritten:** "Trusted Sports Physio Bondi"

### Description 3 - REWRITTEN
**Original:** "Guaranteed to get you moving again"
**Issue:** Outcome guarantee prohibited
**Rewritten:** "Helping you move better, one session at a time"
```

## Funnel Stage Guidelines

### TOF Copy Patterns

**Headlines (30 chars):**
- [Service] in [Location]
- Professional [Service]
- [Condition] Assessment
- Move Better Today
- Your [Body Part] Care Team

**Long Headlines (90 chars):**
- Professional [service] helping [location] residents move with confidence
- Discover how [service] may help manage your [condition] symptoms

**Descriptions (90 chars):**
- AHPRA registered practitioners offering personalised [service] assessments
- Learn about evidence-based approaches to [condition] management

### MOF Copy Patterns

**Headlines:**
- How We Can Help
- Our Treatment Approach
- Assessment Process
- Tailored Care Plans
- Check Availability

**Long Headlines:**
- See how our personalised approach to [service] works for your specific needs
- Book a consultation to discuss your [condition] with our qualified team

**Descriptions:**
- Our experienced team creates individualised treatment plans for each patient
- AHPRA registered practitioners with [X] years combined experience

### BOF Copy Patterns

**Headlines:**
- Book Online Now
- Call [Suburb] Clinic
- Free [X]-Min Consult
- New Patient Offer
- Schedule Today

**Long Headlines:**
- Book your free [X]-minute consultation and take the first step towards better movement
- Limited time offer: Free initial assessment for new patients. Book online today.

**Descriptions:**
- New patients: Claim your free [X]-minute consultation. Online booking available now.
- Ready to start? Book your assessment online or call our friendly team today.

## Reuse Rules

- Copy may be reused across funnel stages if appropriate
- Asset Group names must remain unique
- CTA should match funnel stage intent

## Tips

- **Fill all slots**: Google performs better with more asset variations
- **Vary messaging angles**: Don't repeat the same message 15 ways
- **Match funnel intent**: TOF educates, MOF considers, BOF converts
- **Keep offers for BOF**: Don't waste awareness budget on direct conversion messaging
- **Location matters**: Include suburb names for local healthcare
- **Test multiple themes**: Create 2-3 themes per funnel stage when possible

## Related Skills

- **Landing Page Optimizer**: Run first if no landing page exists
- **Ad Copy Generator**: For RSA copy (not PMax)
- **Google Ads Monthly Review**: Identifies if PMax is the right channel
