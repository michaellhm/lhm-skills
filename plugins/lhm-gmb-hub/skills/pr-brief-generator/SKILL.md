---
name: pr-brief-generator
description: "Generate a press release brief targeting a specific keyword and service page. Use this when the user mentions 'generate a PR brief', 'PR brief', 'press release', 'Signal Genesis', 'write a press release', 'PR distribution', 'press release draft', or wants to create a press release as part of Month 3 link building. Optional skill, only for clients with PR distribution budget."
---

# PR Brief Generator

Identifies a newsworthy angle for the client, writes a press release draft following Signal Genesis formatting, and specifies target link URLs for the service page and GBP listing. Optional skill: only run when the client's plan and budget include PR distribution.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/pr-brief-generator/LEARNED.md`
2. Read `${CLAUDE_PLUGIN_ROOT}/references/anti-ai-writing-guidelines.json`
3. Read `${CLAUDE_PLUGIN_ROOT}/references/ahpra-compliance-framework.md` (if healthcare client)
4. Identify the client and locate their `client_profile.md`
5. Read `[client_folder]/gmb/monthly-optimization/YYYY-MM/service_priorities.md`

## Workflow

### 1. Confirm PR Is Applicable

Check whether PR distribution is part of this client's plan. If unclear, ask the user:

"PR distribution is an optional part of Month 3. Does [Client] have budget for PR distribution this cycle? If not, we can skip this and focus on chambers and sponsorships."

If the user confirms no budget, mark as skipped in `GMBProjectManagement.md` and exit.

### 2. Identify Newsworthy Angle

Search for potential news angles based on the client's situation:

**Strong angles (likely to get pickup):**
- New service launch or expansion
- New location opening or renovation
- Community involvement or charity partnership
- Award or recognition received
- Milestone (10 years in business, 10,000th patient, etc.)
- New team member with notable credentials
- Research or data the business can share

**Weaker angles (may work with good writing):**
- Seasonal service relevance (e.g. "winter sports injuries" for a physio)
- Industry trend commentary
- Response to local health concern or community need

Search the client's website, social media, and recent news for any of these angles. Also ask the user if there are any upcoming milestones or announcements.

### 3. Evaluate Angle Strength

If no strong newsworthy angle exists, tell the user directly:

"I couldn't find a strong newsworthy angle for [Client] this cycle. PR works best when there's a genuine story. Options:
1. **Skip PR this cycle** and allocate budget to additional sponsorships
2. **Brainstorm an angle together** (I can suggest some manufactured angles, but they won't perform as well)
3. **Wait for a natural news moment** and run this skill when something comes up"

Do not force a weak angle into a press release. Bad PR wastes budget and can damage credibility.

### 4. Write Press Release Draft

If a viable angle is confirmed, write the press release following Signal Genesis formatting:

**Structure:**
- **Headline**: Newsworthy, keyword-aware, not promotional. Under 80 characters.
- **Subheadline**: Expands on the headline with location and context
- **Dateline**: [City, State] — [Date]
- **Lead paragraph**: Who, what, where, when, why in the first 2-3 sentences. The most important information first.
- **Body paragraphs** (2-3): Supporting details, context, quotes
- **Quote**: A quote attributed to the business owner or practitioner. Written to sound natural, not corporate.
- **Boilerplate**: Brief company description with location, services, and founding year
- **Contact information**: Business name, phone, email, website

**Link placement:**
- Primary link: target service page URL (in the body, naturally referenced)
- Secondary link: GBP listing URL (in the boilerplate or contact section)
- Do NOT over-link. Two links maximum in the entire release.

### 5. AHPRA Compliance Check

If the client is a healthcare provider:
- Run the press release through the AHPRA compliance framework
- No testimonials or clinical outcome claims
- No before/after references
- No "best" or superlative claims
- No guaranteed results
- Rewrite any flagged sections

### 6. Review Anti-AI Writing

Ensure the press release reads naturally:
- No em dashes
- No triplet structures
- No AI cliche phrases ("in an era of", "seamless integration")
- Varied sentence lengths
- The quote should sound like a real person speaking, not a marketing statement

### 7. Present to User

Present the complete press release draft with:
- The headline and full text
- Target link URLs clearly marked
- The newsworthy angle explanation
- Recommended distribution channels (if known)

Ask the user to review, approve, or request changes. Note that the actual distribution is a manual step handled outside this skill.

### 8. Update Project Doc

Update `GMBProjectManagement.md`:
- Mark the PR brief task as complete with today's date (or mark as "skipped — no viable angle" if that was the outcome)
- Record the target link URLs
- Note the newsworthy angle used

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Web Search | Research newsworthy angles, check client's recent activity | Built-in capability |

This skill has no hard MCP dependencies. It runs entirely on web search and the client profile.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/press_release.md` — Full press release draft with target link URLs
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Task marked complete or skipped
