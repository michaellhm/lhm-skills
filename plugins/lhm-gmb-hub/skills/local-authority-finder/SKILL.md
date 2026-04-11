---
name: local-authority-finder
description: "Find local authority link opportunities including Chambers of Commerce, sponsorships, and community organisations. Use this when the user mentions 'find local authority link opportunities', 'chamber of commerce', 'sponsorship links', 'local links', 'authority links', 'community links', '.edu links', 'local sponsorship', or wants to identify high-value local backlink sources during Month 3. Searches within a 70-80km radius and estimates costs."
---

# Local Authority Finder

Searches for Chambers of Commerce, local sponsorship opportunities, community organisations, and educational institutions within 70-80km of the client's business. Estimates costs, assesses link value, and produces a prioritised outreach plan with contact details.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/local-authority-finder/LEARNED.md`
2. Identify the client and locate their `client_profile.md`
3. Extract the business address, modality, and target location from the client profile

## Workflow

### 1. Define Search Radius

Using the client's business address as the centre point, define a search area covering approximately 70-80km radius. Identify the major suburbs, towns, and council areas within this radius. This wide radius captures smaller suburban chambers that many businesses overlook.

### 2. Search for Chambers of Commerce

Search for every Chamber of Commerce within the radius:

- Search: "[city/region] chamber of commerce"
- Search: "[suburb] business chamber" for each major suburb
- Search: "[council area] chamber of commerce"
- Search: "chamber of commerce near [business address]"
- Check state-level chamber directories for local chapter listings

For each chamber found:
- Record the chamber name and location
- Find the membership page and pricing (typically $200-300/year)
- Check if membership includes a website listing with a backlink
- Record the contact email/phone and membership application URL
- Note the domain authority of the chamber website (if visible from search results)

Target: identify 5-10 chambers, recommend joining 2-5 based on link value and cost.

### 3. Search for Sponsorship Opportunities

Search for local organisations that offer sponsor acknowledgement pages (with backlinks):

**Youth sports leagues and clubs:**
- Search: "[suburb] junior [sport] club sponsors"
- Search: "[city] youth sports sponsorship"
- Check local football, cricket, netball, basketball, soccer club websites for sponsor pages

**Local charities and community organisations:**
- Search: "[city] charity sponsors"
- Search: "[suburb] community organisation partnership"
- Check local Rotary, Lions, community foundations

**Community events:**
- Search: "[city] community events sponsors [current year]"
- Search: "[suburb] festival sponsors"
- Check local council event pages for sponsorship opportunities

**Schools and colleges (potential .edu links):**
- Search: "[city] school sponsors"
- Search: "[suburb] college partnership"
- Note: .edu links are particularly valuable for domain authority

**TEDx and professional events:**
- Search: "TEDx [city] sponsors"
- Search: "[industry] conference [city] sponsors"

For each opportunity found:
- Record the organisation name and website
- Estimate sponsorship cost (typically $100-500)
- Assess link value: does the sponsor page include dofollow links? What is the domain authority?
- Record contact information
- Note the sponsorship period and what's included

### 4. Assess and Prioritise

Score each opportunity on:

1. **Link value** (weight: 40%)
   - .edu domains = highest value
   - Chambers of Commerce = high value (established, trusted domains)
   - Community organisations = moderate value
   - Sports clubs = moderate value (depends on domain)

2. **Cost efficiency** (weight: 30%)
   - Cost per link acquired
   - Whether the link is annual (needs renewal) or permanent
   - Whether additional benefits come with membership/sponsorship

3. **Relevance** (weight: 20%)
   - How relevant is the organisation to the client's modality?
   - Will the association make sense to Google and users?

4. **Effort** (weight: 10%)
   - How easy is the sign-up process?
   - Is it self-serve or does it require negotiation?

### 5. Generate Outreach Plan

Produce a structured outreach plan:

```
## Local Authority Link Opportunities — [Client Name]

### Tier 1: Chambers of Commerce (Budget: $600-1,500)
| Chamber | Location | Annual Cost | Link Type | Contact | Action |
|---------|----------|-------------|-----------|---------|--------|
| [Name] | [City] | $[cost] | Member directory listing | [email/URL] | Apply for membership |

### Tier 2: High-Value Sponsorships (Budget: $200-1,000)
| Organisation | Type | Cost | Link Value | Contact | Action |
|-------------|------|------|-----------|---------|--------|
| [Name] | [type] | $[cost] | [assessment] | [email/URL] | Reach out to [contact] |

### Tier 3: Community Links (Budget: $0-500)
| Organisation | Type | Cost | Link Value | Contact | Action |
|-------------|------|------|-----------|---------|--------|
| [Name] | [type] | $[cost] | [assessment] | [email/URL] | [action] |

### Budget Summary
- Recommended minimum spend: $[amount]
- Expected links acquired: [count]
- Estimated timeline: [weeks]
```

### 6. Budget Guidance

Provide budget recommendations:
- Chambers: ~$200-300 each, aim for 2-5 memberships
- Sponsorships: ~$100-500 each, aim for 2-4 sponsorships
- Total recommended budget: $600-2,500 depending on availability and client budget
- Note: actual outreach and sign-ups are manual. This skill finds and plans, it does not execute.

### 7. Present to User

Present the outreach plan and budget summary. Ask the user which opportunities to pursue this cycle.

### 8. Update Project Doc

Update `GMBProjectManagement.md`:
- Mark the local authority opportunities task as complete with today's date
- Record the number of opportunities identified per tier
- Note any that the user has approved for outreach

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Web Search | Finding chambers, sponsorships, community organisations | Built-in capability (this skill runs entirely on web search) |

This skill has no hard MCP dependencies. It runs entirely on web search, which is always available.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/local_authority_opportunities.md` — Prioritised outreach plan with contact details and budget guidance
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Task marked complete
