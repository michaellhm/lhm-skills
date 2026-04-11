# MCP Setup Guide

This plugin uses three optional MCP servers in addition to the already-installed GSC, GA4, and Keywords Everywhere MCPs. Skills will work without them (using manual fallbacks), but they are significantly more powerful with MCPs configured.

## Local Falcon MCP

**What it does:** Runs 169-point geo-grid scans for local keywords, returns Top 3% metrics, trend reports, and competitor data. Used by: run-local-diagnostic, service-priority-selector, neighbourhood-overlay-writer, monthly-cycle-report.

**Auth:** API key (get from your Local Falcon account at localfalcon.com)
**Cost:** Credit-based (each scan costs credits based on grid size)

### Claude Code

```bash
claude mcp add local-falcon -- npx @local-falcon/mcp
```

Then set your API key:
```bash
export LOCAL_FALCON_API_KEY="your-api-key-here"
```

### Claude Desktop / CoWork

Add to your MCP configuration (usually `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "local-falcon": {
      "command": "npx",
      "args": ["@local-falcon/mcp"],
      "env": {
        "LOCAL_FALCON_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Alternative: Remote MCP

Local Falcon also offers a hosted MCP endpoint:
```
https://mcp.localfalcon.com/mcp?local_falcon_api_key=YOUR_KEY
```

---

## DataForSEO MCP

**What it does:** SERP data, keyword research, backlink analysis, domain analytics, business listing data from Google Maps. Used by: gbp-optimiser, entity-mapper, link-gap-finder.

**Auth:** Username + password (get from dataforseo.com)
**Cost:** Pay-per-API-call (e.g. $0.01 per keyword task). Very affordable for typical usage.

### Claude Code

```bash
claude mcp add dataforseo -- npx dataforseo-mcp
```

Then set your credentials:
```bash
export DATAFORSEO_LOGIN="your-login"
export DATAFORSEO_PASSWORD="your-password"
```

### Claude Desktop / CoWork

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "npx",
      "args": ["dataforseo-mcp"],
      "env": {
        "DATAFORSEO_LOGIN": "your-login",
        "DATAFORSEO_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## Screaming Frog MCP

**What it does:** Full site crawl, exports all indexed pages with on-page data. Used by: link-gap-finder.

**Auth:** None (wraps local Screaming Frog CLI)
**Cost:** Screaming Frog licence is 199 GBP/year. Free version crawls up to 500 URLs.
**Requirement:** Screaming Frog must be installed locally on your machine.

### Claude Code

```bash
claude mcp add screaming-frog -- uvx screaming-frog-mcp
```

### Claude Desktop / CoWork

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "screaming-frog": {
      "command": "uvx",
      "args": ["screaming-frog-mcp"]
    }
  }
}
```

---

## Already Installed MCPs

These MCPs should already be configured in your environment:

| MCP | Used By |
|-----|---------|
| Google Search Console (GSC) | run-local-diagnostic, consistency-signal-audit, technical-page-audit, link-gap-finder, monthly-cycle-report |
| Google Analytics (GA4) | service-priority-selector, monthly-cycle-report |
| Keywords Everywhere | run-local-diagnostic, gbp-optimiser, entity-mapper, service-priority-selector, service-page-writer, faq-content-builder, neighbourhood-overlay-writer, monthly-cycle-report |

If any of these are missing, check your Claude Code or Claude Desktop MCP configuration.

## Checking MCP Availability

When a skill needs an MCP, it should attempt to use the tool first. If the tool is not available, display this message template:

```
[MCP Name] is not configured yet. To set it up, see:
${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md

In the meantime, you can provide the data manually:
[Specific manual alternative for this skill]
```
