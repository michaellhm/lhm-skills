---
name: gbp-optimiser
description: "Research competitor GBP profiles and generate a full Google Business Profile optimisation plan including categories, services, business description, and profile completion checklist. Use this when the user mentions 'optimise GBP for [Client]', 'GBP optimisation', 'Google Business Profile', 'optimise the profile', 'GBP categories', 'GBP services', 'business description', or 'profile optimisation'."
---

# GBP Optimiser

Researches competitor Google Business Profiles, recommends up to 10 categories, generates 30+ specific service listings with descriptions, writes a 750-character business description, and produces a full profile completion checklist with NAP consistency checks.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/gbp-optimiser/LEARNED.md`
2. Read `client_profile.md` for current business details, modality, services, and location
3. Locate the client's `gmb/` folder

## Workflow

### 1. Read Client Context

From `client_profile.md`, extract:
- Business name, address, phone number
- Primary modality and all services offered
- Current GBP categories (if known)
- Website URL

### 2. Research Competitor GBP Categories

Identify the top 3 competitors from the diagnostic report (or Google the primary keyword if no diagnostic exists yet).

For each competitor:
- Look up their GBP listing
- Note their primary and secondary categories
- Note their service listings

Use DataForSEO MCP or Keywords Everywhere MCP to gather competitor data.

**If DataForSEO MCP is not available:**
```
DataForSEO MCP is not configured. To set it up:

Claude Code:   claude mcp add dataforseo -- npx dataforseo-mcp
Claude Desktop: Add to claude_desktop_config.json (see mcp-setup-guide.md)
CoWork:         Add to MCP settings (see mcp-setup-guide.md)

In the meantime, I'll use web search to research competitor GBP categories.
```

### 3. Recommend Up to 10 Categories

Based on competitor research and the client's actual services:
- Select 1 primary category (most relevant to the primary modality)
- Select up to 9 secondary categories
- Each category must represent a real service the client offers
- Explain the reasoning for each category choice

### 4. Generate 30+ Service Listings

Create specific, granular service listings (not broad categories):
- Each service needs a name and short description
- Be specific: "Sports Physiotherapy Assessment" not just "Physiotherapy"
- Cover all services the client actually provides
- Aim for 30-40 listings that comprehensively represent the business
- Group by category for easy review

### 5. Write 750-Character Business Description

Write a business description that:
- Uses the FULL 750 characters (this is important for GBP ranking signals)
- Leads with the primary modality and location
- Mentions key services naturally
- Includes relevant entity terms from the client's field
- Follows anti-AI writing guidelines
- Is AHPRA compliant (if healthcare client)

### 6. Generate Profile Completion Checklist

Create a checklist covering all GBP fields:
- Business name (matches real-world name)
- Primary category
- Secondary categories (up to 9)
- Services (30+)
- Business description (750 chars)
- Attributes (relevant to business type)
- Address (matches website exactly)
- Phone number (matches website exactly)
- Business hours
- Photos (minimum recommendations)
- Logo
- Cover photo

### 7. Flag NAP Inconsistencies

Compare the client's website NAP (Name, Address, Phone) against their GBP listing:
- Character-for-character match required
- Flag any differences in formatting (e.g. "St" vs "Street", phone format)
- Note if website address is missing or differs

### 8. Present Plan for Review

Present the complete optimisation plan to the user:
- Recommended categories with reasoning
- Full service listings
- Business description
- Profile completion checklist with current status
- Any NAP inconsistencies flagged

Ask the user to review and approve before marking as complete.

### 9. Update GMBProjectManagement.md

Mark the following tasks as complete (as applicable):
- GBP categories optimised
- GBP services listed
- 750-char business description written
- All GBP profile fields completed

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| DataForSEO | Competitor GBP data | Web search for competitor categories |
| Keywords Everywhere | Service keyword research | Skip volume data, use client profile |

## Output

- `[client_folder]/gmb/onboarding/gbp_optimisation_plan.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
- Note: Changes must be manually applied in the GBP dashboard. This skill generates the plan only.
