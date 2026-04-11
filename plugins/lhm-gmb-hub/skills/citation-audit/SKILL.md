---
name: citation-audit
description: "Search major directories for existing business listings and check NAP consistency. Use this when the user mentions 'run a citation audit for [Client]', 'citation audit', 'directory check', 'NAP check', 'citations', 'directory listings', 'business directories', or 'citation cleanup'."
---

# Citation Audit

Searches major Australian and industry-specific directories for existing business listings, checks NAP (Name, Address, Phone) consistency against the client's GBP data, and generates an action plan for new submissions and corrections.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/citation-audit/LEARNED.md`
2. Read `client_profile.md` for NAP details (business name, address, phone number)
3. Confirm the exact NAP format from the client's GBP listing (character-for-character)

## Workflow

### 1. Establish Canonical NAP

From `client_profile.md`, record the exact canonical NAP:
- **Name:** Exact business name as it appears on GBP
- **Address:** Exact address format (including unit/suite format, abbreviations)
- **Phone:** Exact phone number format (with area code, spacing)

This is the reference standard. Every directory listing must match this exactly.

### 2. Search Major Directories

Search each of the following directories for the client's business listing:

**General directories:**
- Apple Maps
- Bing Places
- Yelp
- True Local
- Hotfrog
- Yellow Pages Australia

**Industry-specific directories** (based on client's modality):
- For healthcare: HealthEngine, HotDoc, Book A Specialist
- For dental: Dental.com.au
- For allied health: relevant professional association directories
- Other: research and add 2-3 directories specific to the client's industry

### 3. Check Each Listing

For each directory, record:
- **Found:** Yes/No (does a listing exist?)
- **Name match:** Exact/Partial/Wrong/N/A
- **Address match:** Exact/Partial/Wrong/N/A
- **Phone match:** Exact/Partial/Wrong/N/A
- **Notes:** Any other issues (wrong website URL, outdated hours, duplicate listings)

"Partial" means minor formatting differences (e.g. "St" vs "Street"). "Wrong" means factually incorrect information.

### 4. Identify Industry-Specific Directories

Research additional directories specific to the client's modality:
- Search for "[modality] directory Australia"
- Check if competitors are listed on directories the client is not
- Add any relevant directories to the audit

### 5. Generate Action Plan

Categorise each directory into:
- **New submission required:** Client has no listing, needs to create one
- **Correction required:** Listing exists but NAP doesn't match exactly
- **No action needed:** Listing exists and NAP matches perfectly
- **Duplicate removal:** Multiple listings found, need to claim and merge

For corrections, specify exactly what needs to change (e.g. "Change phone from 03 9123 4567 to (03) 9123 4567").

### 6. Update GMBProjectManagement.md

- Mark "Citation audit completed" as complete with today's date
- Add a note listing the total: X directories checked, Y need new submissions, Z need corrections

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| None required | Uses web search | Fully functional without any MCPs |

## Output

- `[client_folder]/gmb/onboarding/citation_audit.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Note: Manual submission and correction is still required. This skill identifies what needs doing.
