# Content Guardrail — Web Copy

Loaded by the content-writer agent for WordPress website copy (homepage, service pages, location pages, supporting pages).

## Required structure (per page)

- H1 with primary keyword
- Intro that confirms the visitor is in the right place (within 50 words)
- Trust signals near the top (credentials, accreditations, social proof)
- Service-specific or location-specific content body
- Internal links to related pages on the same site
- CTA block (book, call, enquire) — context-appropriate for the page type

## AHPRA compliance (healthcare clients)

- No outcome claims
- No guarantees
- No testimonials that imply clinical results
- No "best", "most effective", or comparative superlatives about treatment
- Refer to the AHPRA framework if available

## Voice and tone

- Match the client's Campaign Playbook
- Specific over generic
- Active voice, plain language
- Australian spelling (where applicable)

## SEO

- Primary keyword in H1, intro paragraph, one H2 minimum
- Schema markup applied at theme level (LocalBusiness, MedicalClinic, etc.)
- Title tag and meta description per page brief

## Anti-AI rules

Loaded from `${CLAUDE_PLUGIN_ROOT}/../lhm-marketing-hub/references/anti-ai-writing-guidelines.json`. The 8-pass engine enforces these.
