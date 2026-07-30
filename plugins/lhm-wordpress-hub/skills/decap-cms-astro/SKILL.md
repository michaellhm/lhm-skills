---
name: decap-cms-astro
description: Add and configure Decap CMS (also called Decap CRM by users) for an Astro website hosted on Cloudflare Pages. Use when asked to add a CMS, client content editing, Git-backed editorial approval, draft or scheduled blog publishing, or full-page deploy previews to an Astro build.
---

# Add Decap CMS to Astro

Build a client-safe, Git-backed editing workflow into an existing Astro site.

## Start

1. Determine the plugin workflow required by `CLAUDE.md`.
2. Read `LEARNED.md`.
3. Inspect the Astro project, content collections, routes, Git remote, current branch, Cloudflare Pages configuration, and existing uncommitted work.
4. Read [references/implementation.md](references/implementation.md) in full.
5. Default to an isolated `decap-staging` branch and Cloudflare preview environment. Do not modify the production branch until the user approves the pilot.
6. Preserve unrelated changes. Never commit OAuth secrets.

## Adapt the CMS to the project

- Expose only the pages and fields the user names. Do not make layout-critical templates freely editable.
- Derive Decap fields from the real Astro content schema and frontmatter. Do not paste a fixed sample schema.
- Use rich text for normal blog content. Use raw Markdown for pages containing component markers, HTML, shortcodes, or other fragile structure.
- Keep repeatable complex sections structured through Decap object/list widgets when practical. Otherwise keep protected component markers and explain that layout changes remain agency-managed.
- Configure editorial workflow so Save creates a draft change, review happens through Decap/GitHub, and Publish merges the approved change into the configured publication branch.

## Implement

Use the templates in `assets/` as secure starting points and replace every `__PLACEHOLDER__`:

- `admin-index.html`: CMS entry page.
- `auth.js` and `callback.js`: Cloudflare Pages Functions for GitHub OAuth.
- `decap-deploy-preview.yml`: commit-status bridge for Cloudflare branch previews. Adapt `resolve_preview_path` to every editable collection and route.
- `scheduled-publish.yml`: optional scheduled Cloudflare rebuild for future-dated posts.

Create `public/admin/config.yml` from the project’s actual collections. Require:

- GitHub backend, publication branch, OAuth endpoint, and repository.
- `publish_mode: editorial_workflow`.
- `local_backend: true`.
- `preview_context: Decap Deploy Preview` and `show_preview_links: true`.
- Correct `preview_path` for every editable page and post.
- `delete: false` unless deletion is explicitly required.
- Clear labels, hints, validation, safe defaults, and hidden implementation fields.

Add noindex and no-store headers for `/admin`, `/auth`, and `/callback`. Block the entire staging deployment from indexing.

Make draft preview builds include the edited entry, including drafts and future-dated posts. Keep normal builds restricted to approved, non-draft entries whose publication time has passed. Centralize this rule and reuse it on blog detail pages, listings, feeds, and sitemaps.

If scheduled publishing is requested, add a scheduled rebuild. Decap approval alone cannot make a future-dated entry appear later because Astro is static.

## Configure external services

Pause only for actions requiring the user’s identity or secret access:

1. Create or confirm the GitHub OAuth app callback URL.
2. Add `GITHUB_OAUTH_CLIENT_ID` and encrypted `GITHUB_OAUTH_CLIENT_SECRET` to the Cloudflare Preview environment.
3. Add the deploy-hook secret when scheduled rebuilds are enabled.

Use the browser for these steps when the user authorizes it. Never display, log, or commit secrets.

## Verify

Run all relevant project checks and complete this acceptance test:

1. Build normally and confirm drafts and future posts are absent.
2. Build with `CF_PAGES_BRANCH=cms/test-entry` and confirm the same entry is present.
3. Open `/admin/` locally and on staging.
4. Save a page edit and confirm Decap creates a CMS branch and pull request.
5. Wait for both Cloudflare Pages and `Decap Deploy Preview`.
6. Open the Decap preview and confirm the correct route renders the unpublished edit.
7. Move the entry through Draft, In Review, and Ready/Publish.
8. Confirm a future-dated approved post remains hidden on the normal site.
9. Confirm staging and draft previews send `noindex`.

Do not call the implementation complete if only metadata is editable, the preview links to a missing Cloudflare alias, or a future post appears in a normal build.

## Finish

Report the staging CMS URL, editable collections, approval flow, scheduling behaviour, required user actions, and checks performed. Keep production unchanged unless the user explicitly authorizes promotion.

If a reusable issue was discovered, append one dated line to `LEARNED.md`, respecting the plugin’s 50-entry cap.
