# Audience Signals for Local-Business PMax

Audience signals tell PMax who to start with. They are **suggestions**, not targeting. Google will go beyond them. Provide them anyway - early-stage performance is materially better with strong signals than without.

## The Four Signal Types

For each asset group, layer signals from these four sources:

### 1. Customer Match (highest-quality signal)

Upload an existing patient/client list. Google matches it against signed-in users and uses it to find lookalikes.

**Eligibility for healthcare clinics under AHPRA + Privacy Act:**
- The list must contain only individuals who have given clear consent to receive marketing.
- The clinic's privacy policy must disclose marketing use of personal information.
- Health information itself is **never** uploaded - only contact identifiers (email, phone, address).
- Customer Match cannot be used for sensitive remarketing categories - see Google's healthcare-specific personalised advertising restrictions.

If consent or policy is unclear, **do not** recommend Customer Match. Skip and rely on the other three signal types.

**Minimum list size**: 1,000 matched users. Lists below this generally fail to populate.

### 2. Custom Segments (intent-based)

The single most useful signal for a service business that doesn't have a Customer Match list.

Build a Custom Segment per asset group from:
- **Search terms** prospective patients have used in the last 7 days. Pull from search-term reports for the same service (or, if launching cold, from `keyword-research` skill output).
- **URLs** competitor clinics rank for, plus the client's own service page.

**Worked example - physio clinic, knee-pain asset group**:
- Search terms: "physio for knee pain", "knee physiotherapist near me", "ACL rehab physio", "torn meniscus treatment Sydney".
- URLs: top three local competitor knee-pain pages, plus the client's `/knee-pain` page.

### 3. In-Market Audiences

Use Google's pre-built in-market segments where one matches the service. Common matches for local services:

| Service | Useful In-Market Segments |
|---------|---------------------------|
| Physio / Chiro / Allied health | Health & Wellness > Healthy Eating; Sports & Fitness; Education > Tertiary Education (for student-athlete demos) |
| Cosmetic / Aesthetic | Beauty & Personal Care > Beauty Salons & Spas; Cosmetic Procedures (where allowed) |
| Dental | Health & Wellness > Dental Care |
| Psychology / Mental health | Health & Wellness > Mental Health (where allowed under personalised-ads policy) |
| Legal / Accounting | Legal Services; Financial Services > Tax & Accounting Services |
| Trades / Home services | Home & Garden > Home Improvement; Real Estate > Properties |

Avoid in-market segments that imply sensitive categories (gambling, dating, certain health conditions). Google blocks these from PMax targeting in many cases.

### 4. Detailed Demographics

Apply only when genuinely relevant and never to discriminate.

| Service | Useful Demographic Filter |
|---------|---------------------------|
| Pre-natal physio / women's health | Parental status: New parents (0–1), Parents with infants |
| Paediatric services | Parental status: Parents (any) |
| University-aged services | Education: Currently in tertiary education |
| Aged care, geriatrics | Marital status, age range (apply with care) |

**What you cannot do**: target based on a sensitive health condition, exclude a protected demographic, or target ages outside Google's allowed ranges for sensitive categories.

## Signals Per Asset Group - Configuration Pattern

For each asset group, recommend a 3-layer signal:

```
Asset group: [Service Line] - [Funnel Stage] - [Theme]

Audience signal:
  Customer Match: [List name OR "Not used - no compliant list"]
  Custom Segment: [Service-specific segment name]
  In-Market: [1–2 relevant segments]
  Detailed Demographics: [If relevant - otherwise omit]
```

## Common Mistakes

- **Treating signals as targeting.** PMax will go beyond them. Adding restrictive demographics doesn't constrain reach - it just nudges the algorithm.
- **Using the same signal across all asset groups.** Each service has different intent. Use different Custom Segments.
- **Uploading a Customer Match list without consent.** Privacy Act + APP 7 + AHPRA + Google's policies all apply. When in doubt, don't.
- **Adding > 5 in-market segments per group.** Dilutes the signal. Pick the 1–2 most relevant.
- **Forgetting to refresh signals.** After 90 days, refresh Custom Segments based on actual converting search terms (handled by `pmax-optimizer`).

## What to Do When the Account Has No Existing Audiences

If `mcp__GoogleAds__execute_gaql` returns no Customer Match lists, no Custom Segments, and no relevant audiences for this campaign:

1. Build the Custom Segment first - it's the single highest-value signal.
2. Layer in 1–2 in-market segments.
3. Skip Customer Match for now; add at the 30-day review if the clinic can supply a compliant list.
4. Note the gap in the build spec so the operator knows there's room to improve.
