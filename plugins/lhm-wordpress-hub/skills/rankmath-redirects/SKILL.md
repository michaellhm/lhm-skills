---
name: rankmath-redirects
description: Create, import, clean up, and verify Rank Math 301 redirects on WordPress sites during migrations, sitemap replacements, launch QA, or Squarespace-to-WordPress URL changes. Use when the user asks to set up redirects in Rank Math, import a redirect map, redirect old URLs, verify 301s, or troubleshoot Rank Math redirect matching.
---

# Rank Math Redirects

Use this skill to turn an old sitemap or redirect map into verified Rank Math redirects on a WordPress site. Prefer the bundled script when the site exposes Rank Math's authenticated REST endpoint.

## Inputs

Gather these before changing the site:

- WordPress base URL.
- WordPress username and application password, usually from a local env file such as `/private/tmp/<client>-wp-api.env`.
- Old URLs from a sitemap, crawl export, Search Console export, or user-provided redirect map.
- Current WordPress URL inventory from REST, sitemap, or WP-CLI so existing published pages can be skipped.

Env file keys accepted by the bundled script:

```bash
WP_SITE_URL=https://example.com
WP_USERNAME=username
WP_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

## Workflow

1. Extract old URLs and normalize them to path-only sources unless the source must include a full URL.
2. Inventory current published WordPress URLs and skip old URLs that already resolve to the intended current page.
3. Map each remaining old URL to the closest live target. Avoid redirecting to draft or missing target pages unless the user explicitly wants future-path redirects.
4. Create a JSON payload. Use `verifySource` when Rank Math must store one source form but the public request must be tested with another.
5. Run the bundled script with `--dry-run`, then apply, then verify public `301` responses.
6. Report skipped URLs and unresolved decisions clearly.

## Payload Format

Create `rankmath-redirects-payload.json` in the project, or pass another path with `REDIRECT_PAYLOAD`.

```json
{
  "site": "https://example.com",
  "objectID": 29,
  "objectType": "post",
  "redirects": [
    {
      "source": "/old-page",
      "target": "/new-page/",
      "note": "Old page moved to new WordPress slug."
    },
    {
      "source": "/blog/category/IPL+for+Dry+Eye",
      "verifySource": "/blog/category/IPL%2Bfor%2BDry%2BEye",
      "target": "/blog/",
      "note": "Rank Math stores literal plus, public verification uses encoded plus."
    }
  ],
  "skipped": [
    {
      "source": "/privacy-policy",
      "reason": "WordPress draft exists; needs publish/legal decision."
    }
  ]
}
```

Use `objectID` for any published post/page. Rank Math's endpoint creates a redirect record; the object is only used to satisfy the post-editor route.

## Script

Use `scripts/apply_rankmath_redirects.mjs`.

```bash
WP_API_ENV=/private/tmp/client-wp-api.env \
REDIRECT_PAYLOAD=wp/rankmath-redirects-payload.json \
node /path/to/rankmath-redirects/scripts/apply_rankmath_redirects.mjs --dry-run
```

Then apply:

```bash
WP_API_ENV=/private/tmp/client-wp-api.env \
REDIRECT_PAYLOAD=wp/rankmath-redirects-payload.json \
node /path/to/rankmath-redirects/scripts/apply_rankmath_redirects.mjs
```

Verify only:

```bash
WP_API_ENV=/private/tmp/client-wp-api.env \
REDIRECT_PAYLOAD=wp/rankmath-redirects-payload.json \
node /path/to/rankmath-redirects/scripts/apply_rankmath_redirects.mjs --verify-only
```

## Rank Math REST Behavior

Rank Math exposes `/wp-json/rankmath/v1/updateRedirection`. The route is intended for the post editor and hard-codes source comparison to `exact`; do not rely on it for regex, contains, starts-with, or ends-with redirects.

Request body:

```json
{
  "objectType": "post",
  "objectID": 29,
  "hasRedirect": true,
  "redirectionID": "",
  "redirectionSources": "/old-page",
  "redirectionUrl": "/new-page/",
  "redirectionType": "301"
}
```

Delete a known redirect ID by sending `hasRedirect: false` and the `redirectionID`. Only delete entries you created or the user explicitly asked to remove.

## Verification Rules

- Use `fetch(url, { redirect: "manual" })` or `curl -I`.
- Confirm status is `301`.
- Confirm `Location` matches the expected target. Rank Math usually preserves query strings, so accept `target` and `target?...`.
- External targets such as Qualtrics are valid.
- For old Squarespace category paths containing `+`, store the Rank Math source as literal `+` and verify the public request as `%2B` using `verifySource`.

## Guardrails

- Do not redirect old URLs that are already live WordPress pages unless the user explicitly requests canonical consolidation.
- Do not redirect legal pages to unrelated pages casually; if the matching target is only a draft, skip and report the decision.
- Do not use broad destructive cleanup. Rank Math may reuse IDs; delete only known failed/test IDs from the same session.
- Keep a project-local payload file so redirects can be audited and rerun.
