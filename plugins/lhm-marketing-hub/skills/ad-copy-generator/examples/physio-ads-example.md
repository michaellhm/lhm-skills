# Physio Ads Example: Sunshine Coast Physiotherapy

> Complete interaction showing RSA generation with AHPRA compliance checking, ending in the two deliverables: a Google Ads Editor RSA CSV and a one-page summary.

---

## The Setup

**Date**: 5th August 2024

**Client**: Sunshine Coast Physiotherapy
- Industry: Physiotherapy
- Campaign: Generic
- Ad Group: Sports Physio
- Target CPA: $55

**Request**: Generate new ad copy for the sports physio ad group. Current ads have low CTR (2.1%) and we want to test new messaging.

---

## The Conversation

### User Input

```
[Pastes SKILL.md content]

I need ad copy for Sunshine Coast Physiotherapy. Here's the details:

**Client:** Sunshine Coast Physiotherapy
**Industry:** Physiotherapy
**Ad Group:** Generic - Sports Physio

**Target Keywords:**
- sports physiotherapy sunshine coast
- sports physio maroochydore
- athlete recovery physio
- sports injury treatment

**Landing Page Content:**
- University qualified physiotherapists
- 12 years serving local athletes
- Work with local rugby, surf, and triathlon clubs
- Services: injury assessment, sports massage, rehabilitation programs
- Located in Maroochydore, free parking
- Same-day appointments available
- Bulk billing available for eligible patients

**USPs:**
- Sports injury focus
- Work with local clubs
- Same-day appointments
- Free parking

**Promotion:** Free initial assessment for new patients (worth $85)

Final URL: https://example.com/sports-physio

Current headlines are generic - we want more sports-focused messaging.
```

### Claude's Analysis and Generation

```
Ad Copy Generation: Sunshine Coast Physiotherapy
Ad Group: Generic - Sports Physio
Date: 5th August 2024

## Landing Page Extraction

- University qualified (credential)
- 12 years experience (credential)
- Local sports club partnerships (differentiator)
- Maroochydore location (location)
- Free parking (convenience)
- Same-day appointments (convenience)
- Free initial assessment (promotion)
- Bulk billing available (value)

Services: injury assessment, sports massage, rehabilitation programs

## Generated Headlines (15)

| # | Headline | Chars | Category | AHPRA Status |
|---|----------|-------|----------|--------------|
| 1 | Sports Physio Sunshine Coast | 28 | Keyword | ✅ COMPLIANT |
| 2 | Sports Physio Maroochydore | 26 | Keyword | ✅ COMPLIANT |
| 3 | Athlete Recovery Care | 21 | Keyword | ✅ COMPLIANT |
| 4 | Sports Injury Assessment | 24 | Keyword | ✅ COMPLIANT |
| 5 | Supporting Active Recovery | 26 | Benefit | ✅ COMPLIANT |
| 6 | Supporting Return To Sport | 26 | Benefit | ✅ COMPLIANT |
| 7 | 12 Years Sports Physio Exp | 26 | Credential | ✅ COMPLIANT |
| 8 | University Qualified Team | 25 | Credential | ✅ COMPLIANT |
| 9 | Book Your Assessment | 20 | CTA | ✅ COMPLIANT |
| 10 | Free Initial Assessment | 23 | CTA/Promo | ✅ COMPLIANT |
| 11 | Same Day Appointments | 21 | Convenience | ✅ COMPLIANT |
| 12 | Free Parking Available | 22 | Convenience | ✅ COMPLIANT |
| 13 | Local Sports Club Partner | 25 | Differentiator | ✅ COMPLIANT |
| 14 | Rugby & Surf Injury Care | 24 | Differentiator | ✅ COMPLIANT |
| 15 | Evidence-Based Care | 19 | Differentiator | ✅ COMPLIANT |

## Generated Descriptions (4) — Title Case

| # | Description | Chars | AHPRA Status |
|---|-------------|-------|--------------|
| 1 | Sports Physiotherapy On The Sunshine Coast. Supporting Athletes At Every Level. Book Today. | 90 | ✅ COMPLIANT |
| 2 | University Qualified Physios With 12 Years Experience. Trusted By Local Rugby And Surf Clubs. | 90 | ✅ COMPLIANT |
| 3 | Free Initial Assessment For New Patients. Same-Day Appointments Available In Maroochydore. | 88 | ✅ COMPLIANT |
| 4 | Sports Injury Rehabilitation Care. Evidence-Based Treatment Tailored To Your Goals. | 82 | ✅ COMPLIANT |

## Compliance Summary
- Headlines: 15/15 compliant
- Descriptions: 4/4 compliant

### Compliance notes
- Headline 3: started as "Athlete Recovery Specialists" → "Athlete Recovery Care" (AHPRA: no "specialist")
- Headline 8: started as "AHPRA Registered Team" → "University Qualified Team" (AHPRA: don't advertise registration)
- Headline 14: started as "Rugby & Surf Specialists" → "Rugby & Surf Injury Care" (AHPRA: no "specialist")
- Headline 6: started as "Back To Your Sport Faster" → "Supporting Return To Sport" (AHPRA: "faster" implies an outcome promise)

Ready to generate the CSV and 1-pager?
```

### User Approval

```
Yes, use those. Can you also tell me what to pin?

Generate the files please.
```

### Claude's Final Output

```
## Output File 1: Google Ads Editor RSA CSV

**Filename:** `ad-copy-sunshine-coast-physio-2024-08-05.csv`

One row = one responsive search ad. Descriptions in Title Case. Imports straight into Google Ads Editor.

```csv
Campaign,Ad Group,Headline 1,Headline 2,Headline 3,Headline 4,Headline 5,Headline 6,Headline 7,Headline 8,Headline 9,Headline 10,Headline 11,Headline 12,Headline 13,Headline 14,Headline 15,Description 1,Description 2,Description 3,Description 4,Path 1,Path 2,Final URL
Generic,Sports Physio,Sports Physio Sunshine Coast,Sports Physio Maroochydore,Athlete Recovery Care,Sports Injury Assessment,Supporting Active Recovery,Supporting Return To Sport,12 Years Sports Physio Exp,University Qualified Team,Book Your Assessment,Free Initial Assessment,Same Day Appointments,Free Parking Available,Local Sports Club Partner,Rugby & Surf Injury Care,Evidence-Based Care,Sports Physiotherapy On The Sunshine Coast. Supporting Athletes At Every Level. Book Today.,University Qualified Physios With 12 Years Experience. Trusted By Local Rugby And Surf Clubs.,Free Initial Assessment For New Patients. Same-Day Appointments Available In Maroochydore.,Sports Injury Rehabilitation Care. Evidence-Based Treatment Tailored To Your Goals.,sports-physio,maroochydore,https://example.com/sports-physio
```

## Output File 2: One-Pager

**Filename:** `ad-copy-sunshine-coast-physio-2024-08-05.md`

---

## Ad Copy: Sunshine Coast Physiotherapy — Generic / Sports Physio
**Date:** 5th August 2024 | Compliance: 15/15 headlines, 4/4 descriptions ✅

### Headlines (30 char max)
1. Sports Physio Sunshine Coast (28)
2. Sports Physio Maroochydore (26)
3. Athlete Recovery Care (21)
4. Sports Injury Assessment (24)
5. Supporting Active Recovery (26)
6. Supporting Return To Sport (26)
7. 12 Years Sports Physio Exp (26)
8. University Qualified Team (25)
9. Book Your Assessment (20)
10. Free Initial Assessment (23)
11. Same Day Appointments (21)
12. Free Parking Available (22)
13. Local Sports Club Partner (25)
14. Rugby & Surf Injury Care (24)
15. Evidence-Based Care (19)

### Descriptions (90 char max, Title Case)
1. Sports Physiotherapy On The Sunshine Coast. Supporting Athletes At Every Level. Book Today. (90)
2. University Qualified Physios With 12 Years Experience. Trusted By Local Rugby And Surf Clubs. (90)
3. Free Initial Assessment For New Patients. Same-Day Appointments Available In Maroochydore. (88)
4. Sports Injury Rehabilitation Care. Evidence-Based Treatment Tailored To Your Goals. (82)

### Pinning
- Pin "Sports Physio Sunshine Coast" to Headline position 1. Leave the rest unpinned so Google can optimise.

### Compliance notes
- Headline 3: "Athlete Recovery Specialists" → "Athlete Recovery Care" (AHPRA: no "specialist")
- Headline 8: "AHPRA Registered Team" → "University Qualified Team" (AHPRA: don't advertise registration)
- Headline 14: "Rugby & Surf Specialists" → "Rugby & Surf Injury Care" (AHPRA: no "specialist")
- Headline 6: "Back To Your Sport Faster" → "Supporting Return To Sport" (AHPRA: no outcome promise)

---
```

---

## Key Takeaways from This Example

### What Made This Ad Copy Effective

1. Keyword-rich headlines for relevance
2. Local focus — Sunshine Coast, Maroochydore named
3. Sports injury angle matches the ad group theme
4. Trust signals — qualifications, 12 years, local clubs
5. Clear CTAs — book, assessment, appointments
6. Promotion included — free initial assessment

### AHPRA Compliance Handling

1. Removed "specialist" everywhere — replaced with "care"
2. Removed "AHPRA Registered" — replaced with "University Qualified"
3. Flagged "faster" as an outcome implication and swapped it out
4. Credential language stayed safe — qualifications, experience, evidence-based

### RSA Best Practices Applied

1. All 15 headlines used for maximum variety
2. All 4 descriptions used, every one in Title Case
3. Character limits respected (30 / 90)
4. Light pinning — keyword to position 1 only, rest left to Google
5. Category balance — keywords, benefits, CTAs, credentials, convenience, differentiators

---

*Example from AdPulse Quadrant Ad Copy Generation*
