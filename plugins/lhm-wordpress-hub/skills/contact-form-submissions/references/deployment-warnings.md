# Cloudflare Pages Deployment Warnings

Accumulated from real project sessions. Consult before touching deployment config.

---

## Git-Connected Pages vs Wrangler Deploy

**Rule:** For Git-connected Cloudflare Pages projects, NEVER add `npx wrangler pages deploy` as a deploy command inside the Cloudflare dashboard.

- Git-connected deployment uses Cloudflare Pages' internal build/publish flow:
  - Product: Cloudflare Pages, not Worker
  - GitHub repo connected directly to the Pages project
  - Production branch: `main`
  - Build command: `npm run build`
  - Build output directory: `dist`
  - Root directory: empty unless the app is in a subfolder (e.g. `astro`)
  - Deploy command: empty / not used
  - No `CLOUDFLARE_API_TOKEN` required for deployment
- Wrangler direct upload is a separate model — do not mix the two
- If you add `wrangler pages deploy` to a Git-connected project, deploys may duplicate, conflict, or fail with cryptic authentication errors
- If the Cloudflare UI requires a deploy command, treat that as a red flag that you may be in a Worker/direct-upload style app or the wrong project flow. Do not enter `true`, `echo ok`, `npx wrangler deploy`, or `npx wrangler pages deploy` as a workaround until the project type is confirmed.

**Only use `npx wrangler pages deploy dist --project-name PROJECT_NAME` from external CI/direct upload workflows where an API token is intentionally configured.**

## Authentication error [code: 10000]

This Wrangler error does not always mean bad credentials. It can also mean:
- Wrong project type (Worker vs Pages)
- Wrong project name or account
- Wrong deployment model (Wrangler vs Git-connected)
- Calling Pages deploy from inside a Git-connected Pages build

Diagnose the project type before assuming credential issues.

## Pages Functions Location

Pages Functions live in `functions/` at the project root — NOT inside `src/pages/`.

```
project-root/
  functions/
    api/
      contact.js       ← correct
    admin/
      submissions.js   ← correct
  src/
    pages/             ← Astro routes, NOT Pages Functions
```

Putting a `contact.js` inside `src/pages/api/` creates an Astro API route that requires SSR mode — that is a different thing entirely.

## Cloudflare Email Sending (`send_email` binding)

The `send_email` binding is not valid in Cloudflare Pages config. It appeared to work in Workers but was rejected in Pages `wrangler.toml`. Use an external provider instead:
- Mailgun
- Postmark
- Resend

Do not add `[[send_email]]` bindings to a Pages project.

## D1 Migrations

When applying D1 migrations:
- Local: `npx wrangler d1 migrations apply DB --local`
- Remote: `npx wrangler d1 migrations apply DB --remote`

For Git-connected projects, the remote migration must be applied manually via Wrangler CLI or the Cloudflare dashboard. It does not run automatically on deploy.

## File Upload Compatibility Date

Every Pages project with a multipart file form must set a modern compatibility date:

```toml
compatibility_date = "YYYY-MM-DD"
```

Without a compatibility date, an older Pages runtime can convert uploaded files into strings, so `request.formData().get("upload")` is not a `File`. This often looks like a client upload bug even though the same code passes in local Wrangler, because local Wrangler may default to today's date.

Do not add this redundant flag when the compatibility date is `2021-11-03` or newer:

```toml
compatibility_flags = ["formdata_parser_supports_files"]
```

Current Cloudflare deploys reject it with: `The compatibility flag formdata_parser_supports_files became the default ... so does not need to be specified anymore.`

Validate the deployed configuration by submitting a real multipart file. A successful build is not proof that upload parsing, R2, or D1 metadata works.

## Turnstile Hostname Registration

Each hostname must be explicitly allowed in the Turnstile widget settings:
- Production domain: `www.example.com.au`
- Apex domain: `example.com.au`
- Pages.dev domain: `project-name.pages.dev`
- Preview hash: `9b71b720.project-name.pages.dev` — each hash is a unique hostname

When a form fails on a preview URL with a Turnstile error, add the preview hostname to the widget in the Cloudflare dashboard. If you regenerate the widget (new site key), update both:
1. `PUBLIC_TURNSTILE_SITE_KEY` in `wrangler.toml` / code
2. `TURNSTILE_SECRET_KEY` secret in Cloudflare Pages settings
