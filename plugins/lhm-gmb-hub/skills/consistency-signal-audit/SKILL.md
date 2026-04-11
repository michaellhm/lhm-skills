---
name: consistency-signal-audit
description: "Audit the 8 homepage consistency signals that align the client's website with their Google Business Profile. Use this when the user mentions 'audit consistency signals for [Client]', 'homepage audit', 'consistency signals', '8 signals check', 'NAP consistency', 'homepage signals', 'location page audit', or 'GBP website alignment'."
---

# Consistency Signal Audit

Checks all 8 consistency signals on the client's homepage (or individual location pages for multi-location businesses) to verify the website properly mirrors the Google Business Profile data. Each signal gets a pass/fail grade with specific fix instructions.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/consistency-signal-audit/LEARNED.md`
2. Read `client_profile.md` for GBP data (business name, address, phone, categories, website URL)
3. Determine if the client is single-location or multi-location (from client profile)

## Workflow

### 1. Determine Audit Target

- **Single location:** Audit the homepage
- **Multi-location:** Audit each location page individually (each GBP listing should point to its own location page, not the homepage)

### 2. Fetch the Target Page(s)

Use web fetch to retrieve the live page HTML for analysis.

For multi-location clients, fetch each location page separately.

### 3. Check All 8 Consistency Signals

For each target page, check:

**Signal 1: Title Tag**
- Must contain: Primary GBP category + city name
- Example: "Physiotherapy Brisbane | [Business Name]"
- Pass if both the primary category and city appear in the title tag

**Signal 2: H1 Heading**
- Must contain: Primary GBP category + city name (matches title intent)
- Does not need to be identical to the title tag, but must convey the same meaning
- Pass if primary category and city are present

**Signal 3: Google Maps Embed**
- Must have: A functional Google Maps embed showing the specific GBP location
- Check for an iframe with a Google Maps URL
- Pass if embed exists and loads the correct business location

**Signal 4: Secondary Categories**
- Must have: Secondary GBP categories mentioned as H2s or within body content
- Check that at least the top 3-5 secondary categories appear on the page
- Pass if secondary categories are referenced on the page

**Signal 5: Review Widget**
- Must have: A widget displaying actual Google reviews
- Check for review schema, third-party review widgets, or embedded Google reviews
- Pass if real reviews are visible on the page

**Signal 6: Address**
- Must match: GBP address character-for-character
- Check the page for address text and compare against the GBP canonical address
- Pass only if it matches exactly (including abbreviations, unit format, postcode)

**Signal 7: Phone Number**
- Must match: GBP phone number character-for-character
- Check the page for phone number and compare against GBP canonical phone
- Pass only if it matches exactly (including area code format, spacing)

**Signal 8: Local Business Schema**
- Must have: LocalBusiness (or appropriate subtype) schema markup implemented
- Check for JSON-LD schema in the page source
- Validate that schema contains correct NAP data matching GBP
- Pass if schema exists, validates, and contains accurate data

### 4. Generate Pass/Fail Report

For each signal:
- **Pass:** Signal is correctly implemented
- **Fail:** Signal is missing or incorrect, with specific details on what's wrong and how to fix it

Include a summary score: X/8 signals passing.

### 5. Multi-Location Additional Checks

For multi-location clients, also verify:
- Each GBP listing's website URL points to its specific location page (not the homepage)
- Each location page has unique content (not duplicated across locations)
- Each location page has its own Local Business Schema with the correct location data

Flag any GBP listings that point to the wrong page.

### 6. Update GMBProjectManagement.md

- Mark "Homepage consistency signal audit" as complete with today's date
- Expand the task with sub-items for each of the 8 signals (pass/fail)
- Note the overall score (X/8)

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| GSC | Page indexing verification | Skip indexing check |
| Web fetch | Retrieve live page HTML | Ask user to paste page source |

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/consistency_audit.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
