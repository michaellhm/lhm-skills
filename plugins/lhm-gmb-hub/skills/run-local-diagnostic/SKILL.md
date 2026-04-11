---
name: run-local-diagnostic
description: "Run a Local Falcon grid scan and competitor audit to diagnose a client's local SEO position. Use this when the user mentions 'run a local diagnostic for [Client]', 'local diagnostic', 'grid scan', 'baseline diagnostic', 're-run diagnostic', 'Local Falcon scan', '169 point grid', 'Top 3%', or 'competitor audit'. Used during Month 0 (baseline) and Month 2 (re-run comparison)."
---

# Run Local Diagnostic

Runs a 169-point grid scan for the client's primary keyword, records the Top 3% metric and colour breakdown, identifies where authority drops off, audits top 3 competitors, and determines whether the client has a topical relevance problem or a proximity problem.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/run-local-diagnostic/LEARNED.md`
2. Read `client_profile.md` for client details, primary keyword, and location
3. Check `GMBProjectManagement.md` to determine if this is a Month 0 baseline or Month 2 re-run

## Workflow

### 1. Determine Diagnostic Type

Read the client's `GMBProjectManagement.md` to determine:
- **Baseline (Month 0):** First diagnostic for this cycle. No previous data to compare against.
- **Re-run (Month 2):** Previous baseline exists. Will compare against it to show trend.

### 2. Run 169-Point Grid Scan

Use the Local Falcon MCP to run a grid scan for the client's primary keyword.

**If Local Falcon MCP is not available:**
```
Local Falcon MCP is not configured. To set it up:

Claude Code:   claude mcp add local-falcon -- npx @local-falcon/mcp
Claude Desktop: Add to claude_desktop_config.json (see mcp-setup-guide.md)
CoWork:         Add to MCP settings (see mcp-setup-guide.md)

In the meantime, you can:
1. Run a scan at localfalcon.com manually
2. Paste the results here (Top 3%, position breakdown, grid image URL)
```

### 3. Record Grid Results

Capture from the scan:
- **Top 3% metric** (percentage of grid points ranking in positions 1-3)
- **Colour breakdown:** green (positions 1-3), yellow (positions 4-6), red (positions 7+)
- **Authority cliff:** identify the geographic boundary where rankings drop from green/yellow to red

### 4. Identify Where Authority Falls Off

Analyse the grid pattern:
- If red dominates the edges: proximity problem (rankings strong near business, weak far away)
- If red is scattered or dominates overall: topical relevance problem (Google doesn't associate the business strongly enough with this keyword)

### 5. Run Competitor Audit

Google the primary keyword and identify the top 3 competitors appearing in the Map Pack:
1. For each competitor, run a `site:domain.com` search to count indexed pages
2. Record: competitor name, domain, indexed page count, estimated Top 3% (if available)
3. Note what types of content they have (service pages, FAQ pages, location pages, blog)

### 6. Calculate Threshold

Calculate 25-50% of the top competitor's Top 3% score:
- If client's Top 3% is **below** this threshold: topical relevance problem (need more/better content)
- If client's Top 3% is **at or above** this threshold: proximity problem (need geo-targeted content)

### 7. Determine Direction

Based on threshold analysis:
- **Below threshold:** Direction = Topical Relevance. Focus on service pages, entity coverage, and supporting content.
- **At/above threshold:** Direction = Proximity. Focus on neighbourhood overlay pages and geo-targeted content.
- **Mixed:** Some keywords below, some above. Note which are which.

### 8. Compare Against Previous (Re-run Only)

If this is a Month 2 re-run:
1. Read the previous diagnostic from `onboarding/diagnostic_report.md`
2. Compare Top 3% metrics (improvement/decline)
3. Compare colour breakdown (more green = improving)
4. Note which areas of the grid improved or declined
5. Assess whether the original direction recommendation still holds

### 9. Save Diagnostic Report

Write the full diagnostic report including:
- Grid scan results (Top 3%, colour breakdown, authority cliff description)
- Competitor audit (3 competitors with indexed page counts)
- Threshold calculation and direction recommendation
- If re-run: comparison table against previous diagnostic

### 10. Update GMBProjectManagement.md

- Record the Top 3% metric in the ranking history table
- Record the threshold decision and diagnostic direction in the Cycle Focus section
- Mark the diagnostic task as complete with today's date
- Add any notes about the findings

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| Local Falcon | 169-point grid scan | Manual scan results pasted by user |
| GSC | Indexed page data, search performance | Web search for competitor analysis |
| Keywords Everywhere | Search volume for keywords | Skip volume data, note as unavailable |

## Output

- **Month 0 baseline:** `[client_folder]/gmb/onboarding/diagnostic_report.md`
- **Month 2 re-run:** `[client_folder]/gmb/monthly-optimization/YYYY-MM/diagnostic_rerun.md`
- **Always updates:** `[client_folder]/gmb/GMBProjectManagement.md`
