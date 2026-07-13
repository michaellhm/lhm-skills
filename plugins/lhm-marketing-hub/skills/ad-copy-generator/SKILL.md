---
name: ad-copy-generator
description: Generate AHPRA-compliant responsive search ads (RSAs) for Australian healthcare clients with 15 headlines and 4 descriptions. Use this when users request ad copy, RSA creation, responsive search ads, healthcare ads, AHPRA compliant ads, or ad refresh for physio, chiro, podiatry, optometry, or naturopathy clients.
license: MIT
---

# Ad Copy Generator

## Purpose

Generate AHPRA-compliant responsive search ads (RSAs) for Australian healthcare clients. Create 15 headlines and 4 descriptions with built-in compliance checking to ensure your ads meet regulatory requirements before publishing.

## When to Use

- **New campaigns** - Creating ads for a new ad group
- **Poor ad performance** - Current ads have low CTR or conversion rate
- **Ad refresh** - Testing new messaging angles
- **Compliance check** - Reviewing existing ads for AHPRA compliance
- **After keyword optimization** - Aligning ads with updated keyword focus

## Prerequisites

- Client name and industry (physio, chiro, podiatry, optometry, naturopathy)
- Target campaign/ad group
- Target keywords for the ad group
- Landing page URL or copy
- Any specific promotions, USPs, or offers
- Understanding of AHPRA advertising guidelines

## How It Works

### Step 1: Gather Information

I'll ask you for:

1. **Client Name**: Which client?
2. **Industry**: What type of healthcare?
3. **Campaign/Ad Group**: Where will these ads run?
4. **Target Keywords**: What keywords trigger this ad group?
5. **Landing Page**: URL or paste the content
6. **USPs**: What makes this practice unique?
7. **Current Promotion**: Any offers to include?

### Step 2: Extract Landing Page Content

From the landing page, I'll identify:
- Services offered
- Practitioner credentials
- Unique selling points
- Location/convenience factors
- Trust signals (years experience, qualifications)
- Call-to-action style

## Multi-Model Creative Process

RSA generation uses a creative director model — two models contribute, Claude curates and compliance-checks.

### Pass 1 — Claude generates (AHPRA-anchored)
Generate 10 headlines and 4 descriptions. Anchor to:
- The client brief and value proposition
- AHPRA compliance rules (if `is_health_client = true`): no testimonials, no guaranteed outcomes, no before/after claims, no comparative claims without substantiation
- Character limits: headlines ≤ 30 characters, descriptions ≤ 90 characters

### Pass 2 — GPT-4o generates (different angles)
Use OpenRouter MCP `send-message` with model `openai/gpt-4o`.

Prompt:
"You are a Google Ads copywriter. Generate 10 RSA headlines and 4 descriptions for the following brief. Deliberately choose different creative angles than you would typically default to — avoid generic benefit statements, focus on specificity, urgency, differentiation, and curiosity. Do NOT use em dashes. Keep headlines under 30 characters, descriptions under 90 characters. Brief: [brief]. [If health client: These ads are for a healthcare business in Australia — do not include testimonials, guaranteed outcomes, before/after claims, or comparative claims.]"

### Pass 3 — Claude curates
From the combined pool of 20 headlines and 8 descriptions:
1. Remove any that exceed character limits
2. Remove AHPRA violations (health clients only) — flag them to the user as removed and why
3. Remove obvious duplicates (same idea, different words)
4. Select the strongest 15 headlines and 4 descriptions based on: specificity, differentiation, relevance to search intent, likely CTR
5. Present the curated set to the user — do not present raw outputs from both models separately

AHPRA compliance review is always Claude's responsibility. No GPT-4o line goes to the client without Claude reviewing it first.

### Step 3: Generate 15 Headlines

Create 15 unique headlines (30 characters max each):
- 3-4 keyword-focused headlines
- 2-3 benefit headlines
- 2-3 credential/trust headlines (qualifications, experience, association membership — never "AHPRA registered")
- 2-3 CTA headlines
- 2-3 location/convenience headlines
- 2-3 unique angle headlines

### Step 4: Generate 4 Descriptions

Create 4 unique descriptions (90 characters max each). **Write every description in Title Case** — capitalise every major word, matching the headline styling.
- Description 1: Core service + benefit
- Description 2: Credentials + trust
- Description 3: CTA + value (compliant)
- Description 4: Differentiator + value

### Step 5: AHPRA Compliance Check

Every headline and description is checked against AHPRA rules:

**Prohibited:**
- ❌ Guaranteed outcomes
- ❌ Superlatives without proof
- ❌ Therapeutic claims
- ❌ Success rates
- ❌ Before/after promises
- ❌ "Specialise", "specialist", "expert" (and variants) — AHPRA restricts these unless a recognised specialist title is held
- ❌ "AHPRA registered" — do not put this phrase in ad copy
- ❌ Bold / absolute statements (e.g. "the only", "guaranteed to", "always works")

**Safe:**
- ✅ Evidence-based language
- ✅ Qualification statements (university qualified, association member)
- ✅ Experience-based claims (e.g. "15 years experience")
- ✅ Consultation-focused CTAs

### Step 6: Flag Non-Compliant Copy

For any flagged copy:
- Identify the specific issue
- Explain why it violates AHPRA
- Provide a compliant alternative

### Step 7: Generate Outputs

- CSV ready for Google Ads
- Markdown summary with compliance notes
- Implementation instructions

## Expected Interaction Flow

```
You: [Paste this SKILL.md content]

I need ad copy for Gold Coast Physio. Here's the info:
- Industry: Physiotherapy
- Ad Group: Generic - Sports Physio
- Keywords: sports physiotherapy, sports physio gold coast, athlete recovery
- Landing page: [URL or content]
- USPs: 15 years experience, work with local sports teams, university qualified
- Promotion: Free initial assessment for new patients

Claude: Great! Let me extract the key messaging from your landing page
and generate AHPRA-compliant ad copy...

## Generated Headlines (15)

| # | Headline | Chars | AHPRA Status | Notes |
|---|----------|-------|--------------|-------|
| 1 | Sports Physio Gold Coast | 24 | ✅ COMPLIANT | Keyword + location |
| 2 | 15 Years Sports Physio Exp | 26 | ✅ COMPLIANT | Experience claim |
...

## Generated Descriptions (4) — Title Case

| # | Description | Chars | AHPRA Status | Notes |
|---|-------------|-------|--------------|-------|
| 1 | Sports Physiotherapy On The Gold Coast. Book Your Assessment Today. | 67 | ✅ COMPLIANT | Service + CTA |
...

## Compliance Summary
- 15/15 headlines compliant
- 4/4 descriptions compliant

Ready to generate the implementation CSV?

You: Yes, but can you give me an alternative for headline 8?
It feels too generic.

Claude: [Provides alternatives and regenerates]
```

## RSA Structure Requirements

### Headlines (15 required)

| Character Limit | 30 characters max |
|----------------|-------------------|
| Quantity | 15 headlines |
| Variety | Mix of keyword, benefit, CTA, trust |

**Headline Types to Include:**

1. **Keyword Headlines** (3-4)
   - Include primary keywords
   - Location modifiers

2. **Benefit Headlines** (2-3)
   - What patient gets
   - Outcome-focused (compliant)

3. **Credential Headlines** (2-3)
   - Years experience
   - University qualified
   - Association membership (e.g. APA member)
   - Never "AHPRA registered", "specialist", or "expert"

4. **CTA Headlines** (2-3)
   - Book consultation
   - Get assessment
   - Call today

5. **Location/Convenience** (2-3)
   - Suburb names
   - "Near you"
   - Parking/access

6. **Differentiator Headlines** (2-3)
   - Unique aspects
   - Areas of focus (never worded as "specialist"/"expert")

### Descriptions (4 required)

| Character Limit | 90 characters max |
|----------------|-------------------|
| Quantity | 4 descriptions |
| Structure | Complete thoughts, CTAs |

**Description Structure:**

1. **Description 1**: Core service + key benefit
2. **Description 2**: Credentials + trust element
3. **Description 3**: CTA + value proposition
4. **Description 4**: Differentiator + secondary benefit

## AHPRA Compliance Status Values

### ✅ COMPLIANT

Safe to publish. Meets all AHPRA advertising guidelines.

**Indicators:**
- Evidence-based language
- Qualification-focused
- Consultation-oriented CTAs
- No outcome promises

### ⚠️ REVIEW REQUIRED

May be acceptable but needs human review.

**Common Reasons:**
- Borderline phrasing
- Context-dependent claim
- Regional variation possible

**Action:** Review with compliance knowledge before publishing.

### ❌ NON-COMPLIANT

Must be revised before publishing.

**Triggers:**
- "Guaranteed" language
- Superlatives (best, #1, leading)
- "Specialise", "specialist", "expert" (and variants)
- Therapeutic claims (cures, fixes)
- Success rates or statistics
- Before/after promises
- Bold / absolute statements (the only, always, guaranteed to)

**Action:** Use provided compliant alternative.

## Outputs

Two deliverables: a **Google Ads Editor CSV** (the import file) and a **short 1-pager** (Markdown). No long implementation document.

### 1. Google Ads Editor RSA CSV

**Filename:** `ad-copy-[client]-[date].csv`

One row = one responsive search ad. Columns are the Google Ads Editor RSA import headers, in this order. Descriptions are in **Title Case**. Final URL and Paths included so it imports cleanly.

```csv
Campaign,Ad Group,Headline 1,Headline 2,Headline 3,Headline 4,Headline 5,Headline 6,Headline 7,Headline 8,Headline 9,Headline 10,Headline 11,Headline 12,Headline 13,Headline 14,Headline 15,Description 1,Description 2,Description 3,Description 4,Path 1,Path 2,Final URL
Generic,Sports Physio,Sports Physio Gold Coast,15 Years Sports Physio Exp,University Qualified Team,Back To Active Living,Supporting Your Recovery,Treating Local Athletes,Book Your Assessment,Schedule A Consultation,Surfers Paradise Clinic,Free Onsite Parking,Open 7 Days A Week,Personalised Treatment,Evidence-Based Care,Same Day Appointments,Sports Injury Care,Sports Physiotherapy On The Gold Coast. Book Your Assessment Today.,University Qualified Physios With 15+ Years Treating Athletes.,Book Your Assessment Today. Treatment Plans Tailored To Your Needs.,Evidence-Based Care For Sports And Work-Related Conditions.,sports-physio,gold-coast,https://example.com/sports-physio
```

Rules:
- **Descriptions in Title Case** (every major word capitalised).
- No "AHPRA registered", "specialist", "specialise", or "expert" anywhere in the file.
- Leave a headline/description cell blank only if you genuinely have fewer than 15/4 — aim for the full set.
- Path 1 / Path 2 are the display URL paths (15 chars each max), optional but recommended.

### 2. Short 1-Pager (Markdown)

**Filename:** `ad-copy-[client]-[date].md`

**One page maximum.** Compliance status, the copy, one pinning note. Nothing else.

```markdown
## Ad Copy: Gold Coast Physio — Generic / Sports Physio
**Date:** [Date] | Compliance: 15/15 headlines, 4/4 descriptions ✅

### Headlines (30 char max)
1. Sports Physio Gold Coast (24)
2. 15 Years Sports Physio Exp (26)
[…through 15]

### Descriptions (90 char max, Title Case)
1. Sports Physiotherapy On The Gold Coast. Book Your Assessment Today. (67)
[…through 4]

### Pinning
- Pin "Sports Physio Gold Coast" to Headline position 1. Leave the rest unpinned.
```

### Compliance flags (inline, not a separate document)

If any copy gets flagged during generation, fix it before output and note it in a short "Compliance notes" line at the bottom of the 1-pager. Do not produce a separate flags document.

```markdown
### Compliance notes
- Headline 8: swapped "Guaranteed Pain Relief" → "Pain Management Options" (AHPRA: no guaranteed outcomes)
- Headline 5: swapped "Sports Injury Experts" → "Sports Injury Care" (AHPRA: no "expert")
```

## Tips

- **Keyword in Headline 1**: Google often shows headline 1 first
- **Vary your angles**: Don't repeat the same message 15 times
- **Include location**: Healthcare is local - suburbs matter
- **Credentials convert**: AHPRA registration builds trust
- **CTA variety**: Book, call, enquire - test different actions
- **Check character counts**: 30/90 limits are strict
- **Don't over-pin**: Pinning reduces Google's optimisation ability

## AHPRA Quick Reference

### Safe Healthcare CTAs
- "Book a consultation"
- "Get a professional assessment"
- "Speak with our team"
- "Schedule your appointment"
- "Contact us to discuss"

### Safe Credential Language
- "Qualified physiotherapy team"
- "X years experience"
- "Member of [association]"
- "University qualified"
- (Never "AHPRA registered", "specialist", or "expert")

### Safe Outcome Language
- "May help manage..."
- "Supporting your recovery"
- "Aiming to improve..."
- "Working towards..."
- "Tailored to your needs"

## Related Skills

- **Google Ads Monthly Review**: Identifies if ad performance is the issue
- **Keyword Optimizer**: Ensure keywords and ads are aligned
- **Landing Page Optimizer**: Ads drive traffic - page converts it

---

*Compliant ads that convert*
