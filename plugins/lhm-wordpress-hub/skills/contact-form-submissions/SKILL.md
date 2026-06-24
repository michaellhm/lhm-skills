---
name: contact-form-submissions
description: This skill should be used when the user wants to "set up contact form submissions", "wire up a contact form", "add form handling to Cloudflare Pages", "save form submissions to D1", "add Turnstile spam protection", "set up email notifications for forms", "create a thank-you page for a form", "add an admin submissions page", or "integrate a form with Cloudflare Pages Functions". Provides the complete implementation workflow for reliable, spam-protected, tracked contact form submissions on Astro/Cloudflare Pages sites.
---

# Contact Form Submissions — Cloudflare Pages

Complete implementation workflow for contact form submissions on Astro/Cloudflare Pages projects. Covers spam protection (Turnstile), D1 persistence, email notifications, GA-trackable thank-you pages, and a protected admin view.

## Before Starting — Gather Project Details

Before editing any files, ask the user for:

1. **DB name** — what Cloudflare D1 database name should be used? (e.g. `myclient-contact-db`)
2. **Database ID** — the D1 database ID from the Cloudflare dashboard (or confirm it needs to be created)
3. **Notification email** — which email address should receive form submissions?
4. **CC email** — should any address be CC'd? (leave blank if not)
5. **Sender address** — what should the From address be? (e.g. `website@clientdomain.com.au`)
6. **Email provider** — Mailgun, Postmark, Resend, or other?
7. **Turnstile site key** — the public site key from the Cloudflare Turnstile dashboard
8. **Forms to connect** — which pages/forms should be wired up?
9. **Thank-you URLs** — what URL should each form redirect to on success? (e.g. `/contact/thank-you/`)
10. **Admin username** — what username for the `/admin/submissions` page? Do not ask for the admin password in chat — tell the user to add `ADMIN_PASSWORD` as a secret in Cloudflare Pages settings.

Do not proceed to editing files until these answers are confirmed.

---

## Step 1 — Discover Project Structure

Before touching anything:

- Check for `wrangler.toml` at the project root
- Check for a `functions/` directory (Pages Functions live here, not in `src/pages/`)
- Locate the shared layout component (commonly `src/layouts/BaseLayout.astro`)
- Find all existing contact form markup — search for `<form` across `src/`
- Identify if forms are generated from a renderer (content collections, markdown page renderer) rather than static HTML — if so, update the renderer, not just one page
- Check for existing thank-you pages
- Read the build command and output directory from `wrangler.toml` or `package.json`

**Deployment model check:** Determine if this is Git-connected Cloudflare Pages (most common) or Wrangler direct upload. Do not change the deployment model. See [deployment warnings](references/deployment-warnings.md).

---

## Step 2 — D1 Migration

Create `migrations/0001_contact_submissions.sql` (or the next numbered migration if one already exists — inspect the `migrations/` folder first):

```sql
CREATE TABLE IF NOT EXISTS contact_submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  submitted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT NOT NULL,
  preferred_time TEXT,
  message TEXT NOT NULL,
  source_path TEXT,
  form_name TEXT,
  user_agent TEXT,
  turnstile_verified INTEGER NOT NULL DEFAULT 0,
  email_status TEXT NOT NULL DEFAULT 'pending',
  crm_status TEXT NOT NULL DEFAULT 'not_configured',
  admin_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_contact_submissions_submitted_at
  ON contact_submissions (submitted_at);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_source_path
  ON contact_submissions (source_path);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_email_status
  ON contact_submissions (email_status);
CREATE INDEX IF NOT EXISTS idx_contact_submissions_crm_status
  ON contact_submissions (crm_status);
```

`crm_status` is included even if no CRM integration is planned — it avoids a schema migration when GHL/HubSpot is added later.

---

## Step 3 — Update `wrangler.toml`

Ensure the file contains (fill in real values from Step 0):

```toml
pages_build_output_dir = "dist"

[[d1_databases]]
binding = "DB"
database_name = "PROJECT_CONTACT_DB_NAME"
database_id = "REPLACE_WITH_D1_DATABASE_ID"
migrations_dir = "migrations"

[vars]
CONTACT_NOTIFICATION_TO = "client@example.com"
CONTACT_NOTIFICATION_FROM = "website@example.com"
CONTACT_NOTIFICATION_CC = ""
PUBLIC_TURNSTILE_SITE_KEY = "REPLACE_WITH_TURNSTILE_SITE_KEY"
MAILGUN_DOMAIN = "REPLACE_WITH_MAILGUN_DOMAIN"
MAILGUN_REGION = "us"
```

**Secrets — never in `wrangler.toml`.** Tell the user to add these in Cloudflare Pages → Settings → Environment variables → Secrets:
- `TURNSTILE_SECRET_KEY`
- `MAILGUN_API_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

---

## Step 4 — Pages Function: Form Handler

Create `functions/api/contact.js`. See the full reference implementation in [references/contact-function.md](references/contact-function.md).

Key requirements:
- Accept POST only; return 405 for other methods
- Parse `FormData` from the request
- Silently pass (return success, store nothing) if honeypot field `website` is filled
- Validate required fields: `name`, `email`, `message`
- Clean and truncate all fields to sane lengths (name: 100, email: 254, message: 5000, etc.)
- Verify Turnstile token via `TURNSTILE_SECRET_KEY`; if key is missing (local dev), allow but set `turnstile_verified = 0`
- **Save to D1 first**, before attempting email
- Attempt email via `sendNotification(submission, env)` — email failure must not fail the user-facing response; update `email_status = 'failed'` on error
- Return `{ ok: true, message: "..." }` or `{ ok: false, message: "..." }`

Email provider abstraction: wrap provider logic in `sendNotification()` so swapping providers only changes one function. Default: Mailgun. See [references/email-providers.md](references/email-providers.md) for Mailgun, Postmark, and Resend implementations.

---

## Step 5 — Turnstile Setup

In the shared layout (`src/layouts/BaseLayout.astro`):

```astro
---
const { robots } = Astro.props;
const turnstileSiteKey = import.meta.env.PUBLIC_TURNSTILE_SITE_KEY;
---
<head>
  <!-- existing head content -->
  {robots && <meta name="robots" content={robots} />}
  {turnstileSiteKey && <meta name="turnstile-site-key" content={turnstileSiteKey} />}
  <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" async defer></script>
</head>
```

**Hostname gotcha:** Turnstile validates by hostname. Add every hostname that will be tested:
- Production domain (e.g. `www.clientsite.com.au`)
- Apex domain (e.g. `clientsite.com.au`)
- Pages.dev domain (e.g. `project-name.pages.dev`)
- Any active preview hash (e.g. `9b71b720.project-name.pages.dev`) — each hash is a separate hostname

If the Turnstile widget is regenerated, update both the site key in code and the secret key in Cloudflare.

---

## Step 6 — Form Markup

Update every contact form to use the `data-contact-form` pattern:

```html
<form
  class="contact-form"
  data-contact-form
  data-thank-you="/contact/thank-you/"
  action="/api/contact"
  method="post"
>
  <input type="hidden" name="source_path" value="/contact/">
  <input type="hidden" name="form_name" value="Contact Form">

  <!-- Honeypot — hidden from real users, traps bots -->
  <div class="contact-form__field contact-form__field--hidden" aria-hidden="true">
    <label for="cf-website">Website</label>
    <input type="text" id="cf-website" name="website" tabindex="-1" autocomplete="off">
  </div>

  <!-- Turnstile widget injected here by JS -->
  <div class="contact-form__turnstile" data-turnstile-container hidden></div>

  <!-- visible fields here -->
</form>
```

Each form needs a unique `data-thank-you`, `source_path`, and `form_name`. If forms are generated by a renderer (e.g. Astro content collections), update the renderer rather than individual static files.

CSS for honeypot (add to global styles):
```css
.contact-form__field--hidden { display: none !important; visibility: hidden !important; }
```

**Client-side JS** (`src/scripts/contact-form.js` or equivalent): intercept submit → POST FormData → on success redirect to `form.dataset.thankYou` → on error show inline message and reset Turnstile. Do not redirect on API failure. See [references/client-js.md](references/client-js.md) for the full implementation.

---

## Step 7 — Thank-You Pages

Create a dedicated Astro page for each form under `src/pages/`:

```
src/pages/contact/thank-you/index.astro
src/pages/quote/thank-you/index.astro
```

Template:
```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
---
<BaseLayout title="Thank You" robots="noindex, nofollow">
  <main>
    <h1>Thanks, we've received your message.</h1>
    <p>We'll be in touch within 1 business day.</p>
    <a href="/">Back to home</a>
  </main>
</BaseLayout>
```

Every thank-you page must pass `robots="noindex, nofollow"` to the layout. Ensure `BaseLayout` renders `<meta name="robots" content={robots}>` when the prop is set.

---

## Step 8 — Protected Admin Page

Create `functions/admin/submissions.js`. See [references/admin-function.md](references/admin-function.md) for full implementation.

Key requirements:
- HTTP Basic Auth using `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars
- If credentials missing, return 403 (do not guess or skip auth)
- Query latest 100 rows from D1: `SELECT * FROM contact_submissions ORDER BY submitted_at DESC LIMIT 100`
- Render a plain HTML table — no JS frameworks
- Escape every user-submitted value before rendering (replace `&`, `<`, `>`, `"`, `'`)
- Response headers: `cache-control: no-store`, `x-robots-tag: noindex, nofollow`
- `<meta name="robots" content="noindex, nofollow">` in HTML head
- Do not add this route to site navigation

---

## Step 9 — Verification Checklist

### Local
- [ ] `npm run build` passes without errors
- [ ] `node --check functions/api/contact.js` — no syntax errors
- [ ] `node --check functions/admin/submissions.js` — no syntax errors

### Post-Deploy
- [ ] Submit each form → confirm redirect to correct thank-you URL
- [ ] Check D1 in Cloudflare dashboard → confirm row created
- [ ] Confirm `source_path` and `form_name` values are correct
- [ ] Confirm `email_status = sent` in D1 row
- [ ] Confirm notification email received (check spam)
- [ ] Visit `/admin/submissions` → confirm Basic Auth challenge appears
- [ ] Confirm login works with configured credentials
- [ ] Confirm table shows latest rows
- [ ] Confirm thank-you pages return `noindex, nofollow` in `<head>`
- [ ] If testing on a Cloudflare Pages preview URL, confirm that hostname is registered in Turnstile widget

---

## Files Commonly Edited

| File | Purpose |
|---|---|
| `wrangler.toml` | D1 binding, env vars |
| `migrations/000N_contact_submissions.sql` | D1 schema |
| `functions/api/contact.js` | Form handler Pages Function |
| `functions/admin/submissions.js` | Admin view Pages Function |
| `src/layouts/BaseLayout.astro` | Turnstile script, robots meta prop |
| `src/scripts/contact-form.js` | Client-side form intercept + Turnstile |
| `src/pages/**/thank-you/index.astro` | Thank-you pages per form |
| Content renderer (if applicable) | Form markup generation |

---

## Additional Resources

- [references/contact-function.md](references/contact-function.md) — Full `functions/api/contact.js` implementation
- [references/admin-function.md](references/admin-function.md) — Full `functions/admin/submissions.js` implementation
- [references/client-js.md](references/client-js.md) — Client-side form JS
- [references/email-providers.md](references/email-providers.md) — Mailgun / Postmark / Resend implementations
- [references/deployment-warnings.md](references/deployment-warnings.md) — Cloudflare Pages deployment gotchas
