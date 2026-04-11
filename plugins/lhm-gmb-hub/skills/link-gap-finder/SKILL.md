---
name: link-gap-finder
description: "Find pages on a client's site that have zero or insufficient external backlinks. Use this when the user mentions 'find pages missing external links', 'link gap', 'pages without links', 'link audit', 'backlink gap', 'which pages need links', 'link gap analysis', or wants to start Month 3 link building by identifying which pages to prioritise. Crawls the sitemap, pulls backlink data per page, and produces a prioritised report with a tracking spreadsheet."
---

# Link Gap Finder

Identifies pages on the client's site that have zero or insufficient external backlinks, prioritises them by page type and business value, and produces a tracking spreadsheet template for managing link acquisition throughout Month 3.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/link-gap-finder/LEARNED.md`
2. Identify the client and locate their `client_profile.md`
3. Read `[client_folder]/gmb/GMBProjectManagement.md` to understand which pages have been created in Months 1-2

## Workflow

### 1. Get Full Page List

Gather a complete list of the client's important pages using the best available method:

**Method A — Screaming Frog MCP (preferred):**
- Crawl the site to get all URLs with status codes, page types, and internal link counts

**Method B — GSC Indexed Pages:**
- Use GSC MCP `get_advanced_search_analytics` with dimension "page" to pull all indexed pages
- This gives pages that Google knows about, sorted by impressions

**Method C — Manual Sitemap + Site Search:**
- Fetch the XML sitemap from the site
- Supplement with a `site:domain.com` search to catch pages not in the sitemap
- Ask the user for any additional pages they know about

### 2. Pull Backlink Data Per Page

For each page in the list:

**If DataForSEO MCP is available:**
- Pull referring domains count per page
- Pull total backlinks per page

**If DataForSEO is NOT available, use Keywords Everywhere:**
- Use `get_page_backlinks` for each priority page (service pages first)
- Use `get_unique_page_backlinks` for unique referring domain counts

**If neither is available:**
- Use GSC MCP `get_advanced_search_analytics` with the "page" dimension to see which pages get impressions (proxy for authority)
- Ask the user: "Do you have access to Ahrefs, Moz, or Semrush? Export the backlink report per page and paste the data here."

### 3. Identify Gap Pages

Flag pages as "needs links" based on:
- **Zero external links**: highest priority
- **1-2 external links**: moderate priority (especially if competitors have more for the same keyword)
- **Low-quality links only**: links from directories or low-DA sites without any editorial links

### 4. Prioritise Pages

Rank the pages that need links:

1. **Service pages** (highest priority) — these are the money pages that drive conversions
2. **FAQ/supporting content pages** — these support topical authority for service pages
3. **Location/overlay pages** — these support proximity signals
4. **Category pages** — hub pages that distribute link equity
5. **Homepage** — usually already has the most links

Present the prioritised list:

```
| Priority | Page URL | Page Type | Current Links | Referring Domains | Action |
|----------|----------|-----------|---------------|-------------------|--------|
| 1 | /physiotherapy | Service | 0 | 0 | Needs editorial links |
| 2 | /sports-physio | Service | 1 | 1 | Needs more links |
...
```

### 5. Generate Link Tracking Spreadsheet

Create a CSV tracking template:

```csv
Page URL,Page Type,Priority,Link Source,Link Type,Contact,Status,Date Acquired,Notes
/physiotherapy,Service,1,,,,Not Started,,
/sports-physio,Service,2,,,,Not Started,,
```

Link Type values: Editorial, Chamber, Sponsorship, Directory, PR, Guest Post, Resource Page

### 6. Generate Link Acquisition Recommendations

For each priority page, suggest specific link strategies:
- "Not AI slop" editorial links: reach out to local bloggers, health publications, community sites
- Which pages would benefit most from chamber of commerce links
- Which pages suit sponsorship mentions
- Any natural linking opportunities from existing relationships

### 7. Update Project Doc

Update `GMBProjectManagement.md`:
- Mark the link gap audit task as complete with today's date
- Record the total number of pages needing links
- Note the priority order for link building

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| DataForSEO | Per-page backlink data | Use Keywords Everywhere backlink tools or GSC external links |
| Screaming Frog | Full site crawl for page inventory | GSC indexed pages or manual sitemap fetch |
| GSC | Indexed pages, external links report | Site: search + manual sitemap |
| Keywords Everywhere | Page backlinks if DataForSEO unavailable | Web search for manual checking |

The skill degrades gracefully. Even without DataForSEO and Screaming Frog, it can produce a useful gap report using GSC data and manual input. Display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md` for any missing MCPs.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/link_gap_report.md` — Prioritised list of pages needing links with recommendations
- `[client_folder]/gmb/monthly-optimization/YYYY-MM/link_tracking.csv` — Tracking spreadsheet template
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Task marked complete
