---
name: service-priority-selector
description: "Select the top 3 priority services to focus on for the current optimisation cycle based on ranking data, search volume, and the decision framework. Use this when the user mentions 'select priority services for [Client] this cycle', 'pick services', 'which services should we focus on', 'service priorities', 'priority selection', 'what should we work on this cycle', or 'choose services'."
---

# Service Priority Selector

Cross-references current ranking data, search volume, and competition data to recommend the top 3 services for the current optimisation cycle. Uses the decision framework from the GMB ranking principles to match the client's situation to the right strategy.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/service-priority-selector/LEARNED.md`
2. Read `client_profile.md` for business details, services, and modality
3. Read the most recent diagnostic report (`onboarding/diagnostic_report.md` or `monthly-optimization/YYYY-MM/diagnostic_rerun.md`)
4. Read `${CLAUDE_PLUGIN_ROOT}/references/gmb-ranking-principles.md` for the decision framework

## Workflow

### 1. Gather Current Ranking Data

Ask the user via AskUserQuestion: "Would you like to supply current rankings, or should I pull from GSC/Local Falcon?"

**If manual:** Ask for each service keyword's current local pack position and Top3% metric (if available).

**If auto-pull:** Use GSC MCP and Local Falcon MCP to gather current ranking data.

**If Local Falcon MCP is not available:**
```
Local Falcon MCP is not configured. To set it up:

Claude Code:   claude mcp add local-falcon -- npx @local-falcon/mcp
Claude Desktop: Add to claude_desktop_config.json (see mcp-setup-guide.md)
CoWork:         Add to MCP settings (see mcp-setup-guide.md)

In the meantime, please supply the current rankings manually.
```

### 2. Gather Search Volume and Competition Data

Use Keywords Everywhere MCP (or web search) to get:
- Monthly search volume for each service keyword + city
- Competition level
- Related keyword variations

Use GA4 MCP (if available) to check:
- Which service pages currently drive the most traffic
- Which services generate the most conversions

### 3. Cross-Reference Data

Build a comparison table for all client services:

| Service | Local Pack Position | Top3% | Monthly Volume | Competition | Current Traffic |
|---------|-------------------|-------|----------------|-------------|----------------|

### 4. Apply Decision Framework

Based on the client's situation, apply the appropriate scenario from `gmb-ranking-principles.md`:

**Scenario A: Not ranking #1 for primary modality**
- Pick: Primary modality + 2 highest-volume sub-services
- Reasoning: Must establish authority for the core modality first

**Scenario B: Ranking #1 locally for primary modality**
- Pick: 2-3 sub-services the client is NOT yet ranking for
- Reasoning: Primary modality is handled, expand into sub-services

**Scenario C: Ranking well locally, wants surrounding suburbs**
- Pick: Primary modality + location combo variations
- Reasoning: Proximity is the issue, need geo-targeted content

**Scenario D: Multi-modality practice**
- Pick: Strongest revenue modality first, then next 2 highest-potential services
- Reasoning: Establish dominance in one modality before spreading thin

### 5. Present Recommendation

Present the top 3 recommended services with:
- The service name and target keyword
- Current ranking position
- Search volume
- Why this service was selected (which scenario applies)
- What content will be created for each

### 6. Require Approval

Display prominently: **"Confirm with Michael before proceeding."**

Do not mark as complete or update the project doc until the user confirms the selection has been approved.

### 7. Update GMBProjectManagement.md

Once approved:
- Record the 3 priority services in the Cycle Focus section
- Record the selection reasoning and which scenario was applied
- Record who approved and when
- Update the Month 1 task list to replace "[Service 1/2/3]" with actual service names

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Local Falcon | Current grid rankings | Manual ranking input from user |
| GSC | Search performance data | Manual ranking input from user |
| GA4 | Traffic and conversion data | Skip conversion data |
| Keywords Everywhere | Search volume and competition | Web search for volume estimates |

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/service_priorities.md`
- Updates: `[client_folder]/gmb/GMBProjectManagement.md`
