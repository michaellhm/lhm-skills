# Decap CMS on Astro and Cloudflare Pages

## Contents

- Architecture
- Project discovery
- Decap configuration
- Content safety
- Preview builds
- GitHub OAuth
- Cloudflare deploy previews
- Scheduled publishing
- Security
- Validation

## Architecture

Use this flow:

`Decap editor -> GitHub CMS branch/PR -> Cloudflare branch deployment -> Decap preview link -> approval/merge -> publication branch deployment`

Decap manages content in Git. Astro renders it. Cloudflare Pages hosts both the staging CMS and branch previews. Cloudflare Pages Functions handle GitHub OAuth.

## Project discovery

Resolve these values from the project and provider before editing:

- GitHub owner/repository and whether it is private.
- Publication branch, normally `decap-staging` for the pilot.
- Cloudflare Pages project name and branch alias.
- Content collection folders, schemas, required frontmatter, and routes.
- Page files the client may edit.
- Blog detail, listing, RSS/feed, sitemap, search index, and related-post filters.
- Existing Cloudflare Functions, headers, redirects, and workflows.

Ask only for values that cannot be discovered. Do not assume the sample Local Health Marketing paths.

## Decap configuration

Place the editor at `public/admin/index.html` and configuration at `public/admin/config.yml`.

Baseline:

```yaml
backend:
  name: github
  repo: OWNER/REPOSITORY
  branch: decap-staging
  base_url: https://decap-staging.PROJECT.pages.dev
  auth_endpoint: auth
  auth_scope: repo
  preview_context: Decap Deploy Preview
  squash_merges: true

site_url: https://decap-staging.PROJECT.pages.dev
display_url: https://decap-staging.PROJECT.pages.dev
show_preview_links: true
publish_mode: editorial_workflow
local_backend: true

media_folder: public/images/uploads
public_folder: /images/uploads
```

Build collection fields from the real content schema. Every field name and type must serialize to a value accepted by Astro/Zod. Include the body explicitly:

```yaml
- label: Page Content
  name: body
  widget: richtext
  modes: [raw]
```

For a file collection, use the rendered route:

```yaml
- name: about
  label: About Page
  file: src/content/pages/about.md
  preview_path: about
```

For posts:

```yaml
folder: src/content/blog
create: true
slug: "{{slug}}"
preview_path: blog/{{slug}}
```

Set `editor.preview: false` when the project does not implement an accurate in-editor preview. The external `View Preview` link is the full rendered Astro site.

## Content safety

Let clients edit copy and structured fields. Keep layout and code controlled.

- Use object/list widgets for repeatable cards, FAQs, testimonials, team members, and CTAs when the Astro content model supports them.
- If a page body contains component comments, HTML, or shortcode-style markers, use raw mode and add a field hint telling editors not to remove them.
- Prefer unambiguous matching open/close markers such as `[card]...[/card]`. Do not accept mismatched brackets.
- Set `delete: false` for pages and for review pilots.
- Use hidden fields only for stable implementation values.

## Preview builds

Cloudflare exposes `CF_PAGES_BRANCH` during Pages builds. Centralize visibility:

```ts
const cloudflareBranch = process.env.CF_PAGES_BRANCH ?? '';

export const isCmsPreview = cloudflareBranch.startsWith('cms/');

export function includePublishedEntry({
  draft,
  publishedAt,
}: {
  draft: boolean;
  publishedAt: Date;
}) {
  return isCmsPreview || (!draft && publishedAt <= new Date());
}
```

Use the same predicate everywhere an entry can surface. A common failure is filtering the detail page correctly but leaking future posts into the listing, feed, or sitemap.

If the project uses another approval flag, include it in the normal-build clause. On CMS preview branches, include the entry being reviewed.

## GitHub OAuth

Use the Pages Functions templates in `assets/`. Configure the OAuth app:

- Homepage: staging branch alias.
- Callback: `https://STAGING_ALIAS/callback`.

Configure only the client ID and secret in Cloudflare environment variables. Keep the secret encrypted. Use Preview environment variables for a staging-only CMS.

## Cloudflare deploy previews

Decap expects a GitHub commit status matching `backend.preview_context`. Cloudflare’s own status links to its dashboard, so add the `decap-deploy-preview.yml` workflow.

Cloudflare branch aliases:

1. Lowercase the Git branch.
2. Replace non-alphanumeric characters with hyphens.
3. Truncate the alias segment to 28 characters.
4. Append `.<PROJECT>.pages.dev`.

The workflow must post a pending status first, poll the actual rendered route until HTTP 200, and only then post success. Posting success immediately causes Decap to expose a preview link before Cloudflare has created the alias, producing “Nothing is here yet.”

Keep the status target at the branch root. Decap appends the collection’s `preview_path`.

Adapt the workflow’s `resolve_preview_path` case statement to the project’s page names and routes. For posts, derive the slug only when Decap branch naming matches the route slug. Otherwise query content or generate a deterministic mapping.

## Scheduled publishing

Decap’s editorial workflow approves and merges content. It does not run a future Astro build.

For future-dated posts:

1. Merge approved posts to the publication branch.
2. Exclude `publishedAt > now` from normal builds.
3. Trigger Cloudflare rebuilds on a schedule using a branch-specific deploy hook.
4. Store the hook URL as `CLOUDFLARE_DEPLOY_HOOK`, never in source.

An hourly rebuild is usually enough. Scheduled GitHub workflows run from the default branch, so ensure the workflow exists there when the CMS is promoted. For a staging-only pilot, a Cloudflare Cron Trigger or another scheduler may be easier if the default branch must remain untouched.

Time handling:

- Store timestamps with an explicit offset or UTC `Z`.
- Set Decap’s date/time picker deliberately.
- Compare real `Date` values at build time.
- Explain that publication occurs on the first successful scheduled build after the selected time.

## Security

- Add `X-Robots-Tag: noindex, nofollow, noarchive` and `Cache-Control: no-store` to `/admin`, `/auth`, and `/callback`.
- Block staging globally using both `robots.txt` and response headers when possible.
- Validate OAuth `state`.
- Restrict `postMessage` to the callback page’s exact origin.
- Add no-store, CSP, referrer, and content-type headers to the callback.
- Never expose the GitHub access token outside the OAuth popup exchange.
- Do not place client secrets in Decap config, GitHub workflows, documentation, or commits.

## Validation

At minimum:

```bash
npm run check
npm run build
CF_PAGES_BRANCH='cms/test-entry' npm run build
```

Use the project’s package manager and scripts rather than assuming npm.

Verify generated output, not just successful commands. Check absence/presence of a known draft and future-dated post in both build modes. Test the deployed editorial workflow because `local_backend` does not reproduce GitHub PR approval or Cloudflare status links.
