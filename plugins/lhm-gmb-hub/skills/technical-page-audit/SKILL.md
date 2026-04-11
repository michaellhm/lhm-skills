---
name: technical-page-audit
description: "Run a technical SEO audit on a specific page URL. Use this when the user mentions 'run a technical audit on [URL]', 'technical audit', 'check page technical', 'schema check', 'indexing check', 'is the page indexed', 'check schema markup', 'page speed check', or wants to validate that a newly published service page meets all technical requirements. Covers schema validation, broken links, indexing status, page speed, and mobile responsiveness."
---

# Technical Page Audit

Validates that a page meets all technical SEO requirements for local search: schema markup present and valid, no broken internal links, indexed in GSC, fast load time, mobile responsive, and included in the sitemap. Produces a pass/fail checklist with specific fixes for any failures.

## Before Starting

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/technical-page-audit/LEARNED.md`
2. Get the target URL from the user (or from the current workflow context)
3. Determine the page type: service page, location page, FAQ/supporting page, or homepage. This affects which schema types are expected.

## Workflow

### 1. Fetch the Live Page

Use web fetch to retrieve the live page at the target URL. If the page returns a non-200 status code, report immediately and stop the audit.

Record the page type based on content and URL pattern:
- Service page: expects Service schema + LocalBusiness schema
- Location page: expects LocalBusiness schema
- FAQ/supporting page: expects FAQ schema (if FAQ section present)
- Homepage: expects LocalBusiness schema + Organization schema

### 2. Schema Markup Validation

Check the page source for JSON-LD structured data:

- **Service Schema** (service pages): Verify `@type: Service` is present with `name`, `description`, `provider`, and `areaServed` fields populated
- **LocalBusiness Schema** (all page types): Verify `@type: LocalBusiness` (or appropriate subtype like `Physiotherapist`, `Dentist`) with `name`, `address`, `telephone`, `openingHours`
- **FAQ Schema** (FAQ pages): Verify `@type: FAQPage` with `mainEntity` array containing `Question` and `acceptedAnswer` pairs
- **Schema validates**: Check for common errors: missing required fields, malformed JSON, incorrect nesting

Mark each as PASS or FAIL with specific details.

### 3. Internal Link Check

Scan all internal links on the page:
- Extract every `<a href>` pointing to the same domain
- Check each for a 200 response (or identify redirects, 404s, 500s)
- Flag any broken links with the URL and suggested fix

### 4. GSC Indexing Status

Using the GSC MCP:
- Check whether the URL is indexed (`inspect_url_enhanced`)
- If not indexed: check the reason (noindex tag, crawl error, not yet discovered)
- If indexed: note the last crawl date

**If not indexed and no blocking issue exists:**
- Ask the user: "This page is not yet indexed. Should I submit it for indexing via GSC?"
- If approved, submit using the GSC MCP

### 5. Page Speed Check

Fetch the page and evaluate:
- Total page load time (target: under 3 seconds)
- Check for large uncompressed images
- Check for render-blocking JavaScript
- Check for missing caching headers

Report findings with specific recommendations for any issues.

### 6. Mobile Responsiveness

Check the page for mobile-friendliness:
- Viewport meta tag present
- No horizontal scroll issues (content width fits viewport)
- Tap targets appropriately sized
- Text readable without zooming
- No fixed-width elements that overflow

### 7. Sitemap Check

Verify the page URL appears in the site's XML sitemap:
- Fetch the sitemap (typically `/sitemap.xml` or check `robots.txt` for sitemap location)
- Search for the target URL
- If missing, flag for addition

### 8. Generate Audit Report

Compile a pass/fail checklist:

```
Technical Audit — [URL]
Date: [Today]
Page Type: [Type]

| Check | Status | Details |
|-------|--------|---------|
| Service Schema | PASS/FAIL | [details] |
| LocalBusiness Schema | PASS/FAIL | [details] |
| Schema validates | PASS/FAIL | [details] |
| No broken internal links | PASS/FAIL | [X broken links found] |
| Indexed in GSC | PASS/FAIL | [status] |
| Page load < 3s | PASS/FAIL | [actual time] |
| Mobile responsive | PASS/FAIL | [issues] |
| In sitemap | PASS/FAIL | [details] |

Overall: X/Y checks passing

Action Items:
1. [Specific fix for each FAIL]
```

### 9. Update Project Doc

Update `GMBProjectManagement.md`:
- Mark the technical audit task as complete with today's date
- Record the overall pass/fail count
- Note any items that need manual fixing (e.g. adding page to sitemap, fixing schema)

## MCP Dependencies

| MCP | Purpose | Fallback |
|-----|---------|----------|
| GSC | Indexing status check, submit for indexing | Ask user to check GSC manually; skip indexing submission |
| Web Fetch | Page retrieval, link checking | Built-in web search capability |

If GSC is not available, display setup instructions from `${CLAUDE_PLUGIN_ROOT}/references/mcp-setup-guide.md`. The audit can still run for schema, links, speed, and mobile checks. Indexing status will need to be verified manually by the user.

## Output

- `[client_folder]/gmb/monthly-optimization/YYYY-MM/technical_audit.md` — Pass/fail checklist with action items
- Updates: `[client_folder]/gmb/GMBProjectManagement.md` — Task marked complete
