# WordPress Push — Rank Math REST Recipes

All snippets are tested patterns. They assume Rank Math is the SEO plugin (check the crawl: Rank Math emits `rank_math` markers in page HTML; the admin bar shows "Rank Math SEO"). For Yoast sites, the equivalent meta keys are `_yoast_wpseo_title` / `_yoast_wpseo_metadesc` and there is no updateMeta endpoint — use the core REST meta route if exposed, or stop and tell the user.

## Auth path A — Application Password (try first)

Credentials from `[client-folder]/wp-access.md`. Test:

```
GET {site}/wp-json/wp/v2/pages/{id}?context=edit
Authorization: Basic base64("{username}:{application password}")
```

- 200 with an `id` → authenticated, proceed server-side or via browser fetch with the header.
- 401 `rest_forbidden_context` despite correct credentials → the host is stripping the Authorization header (very common on managed/staging hosts). Fall back to path B. Tell the user, and suggest asking the host to enable the `HTTP_AUTHORIZATION` rewrite for future automation.

## Auth path B — logged-in browser session + REST nonce

Requires the Claude in Chrome tools and the user logged into wp-admin (they usually are, on staging).

1. Navigate a tab to any wp-admin page (e.g. `/wp-admin/profile.php`).
2. `wpApiSettings.nonce` is available in page JS. All REST calls become:

```js
fetch('/wp-json/...', {credentials:'include', headers:{'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type':'application/json'}, ...})
```

Notes for browser JS execution: no top-level `await` in some execution contexts — wrap in `(async()=>{...})()`; tool output truncates around 1,500 characters, so return compact per-ID status strings, never full JSON dumps; avoid returning raw page HTML (extension data-leak filters may block responses containing cookie/query-string-like content).

## Discover routes

`GET /wp-json/rankmath/v1` lists available routes. Expect `updateMeta`, `updateMetaBulk`, `updateRedirection`, `updateSchemas`.

## Update titles/descriptions

One page first, verify, then batch:

```js
POST /wp-json/rankmath/v1/updateMeta
{"objectType":"post","objectID":51,"meta":{"rank_math_title":"...","rank_math_description":"..."}}
```

- Response `{"slug":true,...}` = success. Works for pages, posts, and custom post types (all are objectType "post" with their post ID).
- Note: `rank_math_title`/`rank_math_description` are NOT exposed through core `wp/v2` meta (you'll see only `footnotes`), which is why the Rank Math endpoint is required.
- Batch pattern: sequential awaited fetches in one script, collect `id:status` pairs, return the joined string.

## Slug changes with 301

Order matters — create the redirect before renaming, so there is no window where the old URL 404s:

1. Create redirect:
```js
POST /wp-json/rankmath/v1/updateRedirection
{"redirectionSources":["old-slug-path"],"redirectionUrl":"{site}/new-slug-path/","redirectionType":"301","hasRedirect":true,"objectID":<post id>}
```
If the payload is rejected, GET the route's schema from `/wp-json/rankmath/v1` (args are listed) and adapt; Rank Math versions vary. Requires the Redirections module enabled in Rank Math — check, and enable via Settings if the user approves.
2. Rename: `POST /wp-json/wp/v2/{rest_base}/{id}` with `{"slug":"new-slug"}` (rest_base from `/wp-json/wp/v2/types` — pages use `pages`, CPTs use their own).
3. Verify: old URL returns 301 → new URL returns 200 with the correct title.

If the user's `rank-math-301-redirect` skill (WordPress hub plugin) is installed, prefer invoking it for step 1 — it's the maintained implementation.

## Verification pass (always)

Re-fetch every updated page with a cache-buster (`?v=<timestamp>`), parse rendered `<title>` and `meta[name=description]`, compare exact-match against the approved spreadsheet. Report N/N matched. Any mismatch: re-push that page, check for page-builder overrides or caching plugins, and if a CDN/cache layer is active, flush it or note the TTL.
