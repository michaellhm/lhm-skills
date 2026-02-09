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

### Step 3: Generate 15 Headlines

Create 15 unique headlines (30 characters max each):
- 3-4 keyword-focused headlines
- 2-3 benefit headlines
- 2-3 credential/trust headlines
- 2-3 CTA headlines
- 2-3 location/convenience headlines
- 2-3 unique angle headlines

### Step 4: Generate 4 Descriptions

Create 4 unique descriptions (90 characters max each):
- Description 1: Core service + benefit
- Description 2: Credentials + trust
- Description 3: CTA + urgency (compliant)
- Description 4: Differentiator + value

### Step 5: AHPRA Compliance Check

Every headline and description is checked against AHPRA rules:

**Prohibited:**
- ❌ Guaranteed outcomes
- ❌ Superlatives without proof
- ❌ Therapeutic claims
- ❌ Success rates
- ❌ Before/after promises

**Safe:**
- ✅ Evidence-based language
- ✅ Qualification statements
- ✅ Experience-based claims
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
- USPs: 15 years experience, work with local sports teams, AHPRA registered
- Promotion: Free initial assessment for new patients

Claude: Great! Let me extract the key messaging from your landing page
and generate AHPRA-compliant ad copy...

## Generated Headlines (15)

| # | Headline | Chars | AHPRA Status | Notes |
|---|----------|-------|--------------|-------|
| 1 | Sports Physio Gold Coast | 24 | ✅ COMPLIANT | Keyword + location |
| 2 | 15 Years Sports Physio Exp | 26 | ✅ COMPLIANT | Experience claim |
...

## Generated Descriptions (4)

| # | Description | Chars | AHPRA Status | Notes |
|---|-------------|-------|--------------|-------|
| 1 | Expert sports physiotherapy... | 88 | ✅ COMPLIANT | Service + benefit |
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
   - AHPRA registered
   - Years experience
   - Qualifications

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
   - Specialisations

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
- Therapeutic claims (cures, fixes)
- Success rates or statistics
- Before/after promises

**Action:** Use provided compliant alternative.

## Outputs

### 1. Ad Copy CSV

**Filename:** `ad-copy-[client]-[date].csv`

```csv
Type,Position,Copy,Characters,AHPRA Status,Notes
Headline,1,Sports Physio Gold Coast,24,COMPLIANT,Keyword + location
Headline,2,15 Years Sports Physio Exp,26,COMPLIANT,Experience claim
Headline,3,AHPRA Registered Team,20,COMPLIANT,Credential
...
Description,1,Expert sports physiotherapy on the Gold Coast. Book your assessment today.,71,COMPLIANT,Core + CTA
Description,2,AHPRA registered practitioners with 15+ years experience treating athletes.,78,COMPLIANT,Credential + trust
...
```

### 2. Implementation Summary (Markdown)

```markdown
## Ad Copy - Gold Coast Physio
**Campaign:** Generic
**Ad Group:** Sports Physio
**Date:** [Date]

### Compliance Summary
- Headlines: 15/15 COMPLIANT
- Descriptions: 4/4 COMPLIANT

### Headlines for Google Ads
1. Sports Physio Gold Coast (24 chars)
2. 15 Years Sports Physio Exp (26 chars)
[etc.]

### Descriptions for Google Ads
1. Expert sports physiotherapy on the Gold Coast. Book your assessment today. (71 chars)
[etc.]

### Pinning Recommendations
- Pin "Sports Physio Gold Coast" to Position 1 (keyword relevance)
- Consider pinning CTA to Position 3

### Next Steps
1. Create new RSA in Google Ads
2. Copy headlines exactly as shown
3. Copy descriptions exactly as shown
4. Set up A/B test against current ads
5. Review performance after 14 days
```

### 3. Flagged Items Report (if any)

```markdown
## AHPRA Compliance Flags

### Headline 8 - NON-COMPLIANT
**Original:** "Guaranteed Pain Relief Today"
**Issue:** "Guaranteed" outcome claim
**Rule:** AHPRA prohibits guaranteed outcomes
**Alternative:** "Effective Pain Management"

### Description 3 - REVIEW REQUIRED
**Original:** "Our proven techniques help most patients..."
**Issue:** "Proven" may imply clinical evidence
**Rule:** Therapeutic claims need substantiation
**Alternative:** "Our evidence-based approach aims to support your recovery..."
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
- "AHPRA registered practitioners"
- "Qualified physiotherapy team"
- "X years experience"
- "Member of [association]"
- "University qualified"

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
