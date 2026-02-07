---
name: client-onboarding
description: "Establish client context by creating or enriching client_profile.md. Use this when a new client folder is created, client_profile.md is missing or empty, or the user wants to update client context."
---

# Client Onboarding

Create or enrich the `client_profile.md` file in the client's folder.

## Rules

- **Never overwrite** existing content in `client_profile.md`
- If the file exists and has content, read it first and only ask about missing fields
- If the file does not exist or is empty, gather all fields below

## Fields to Gather

Ask the user for the following. Skip any that already exist in `client_profile.md`.

### Business Basics
- **Business name**
- **Website URL**
- **Industry / vertical**
- **Location(s)** — where they operate or serve clients
- **Business type** — e.g. local service, SaaS, ecommerce, agency

### Marketing Context
- **Primary goal** — e.g. more bookings, more leads, brand awareness, revenue growth
- **Target audience** — who are they trying to reach
- **Key services or products** — what they sell or offer
- **Competitors** — who they compete with (if known)

### Advertising
- **Google Ads account ID** — (if applicable)
- **Monthly ad budget** — approximate
- **Other ad platforms** — e.g. Meta, LinkedIn, TikTok (if any)

### Compliance (if applicable)
- **Regulatory requirements** — e.g. AHPRA for healthcare, ASIC for finance
- **Practitioner type** — e.g. physiotherapist, chiropractor, dentist (if healthcare)

### Notes
- Any other context the user wants to record

## Output

Write the gathered information to `client_profile.md` in the client folder using this format:

```markdown
# Client Profile: [Business Name]

## Business
- **Website:** [url]
- **Industry:** [industry]
- **Location:** [location]
- **Type:** [business type]

## Marketing
- **Primary Goal:** [goal]
- **Target Audience:** [audience]
- **Key Services/Products:** [services]
- **Competitors:** [competitors]

## Advertising
- **Google Ads ID:** [id or N/A]
- **Monthly Budget:** [budget]
- **Other Platforms:** [platforms or None]

## Compliance
- **Regulatory:** [requirements or None]
- **Practitioner Type:** [type or N/A]

## Notes
[any additional context]
```

If enriching an existing file, append new sections or fill in missing fields without disturbing existing content.

Narrate when done: "Client profile saved."
