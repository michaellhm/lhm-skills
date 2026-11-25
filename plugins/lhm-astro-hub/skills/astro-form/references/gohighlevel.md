# GoHighLevel path (inbound webhook)

Use this path when the client has a GoHighLevel account. The form posts to a Turnstile-checked Pages Function, which forwards the lead as JSON to a GoHighLevel inbound webhook. There is no D1 database, no R2 bucket and no admin page on this path: GoHighLevel is the record of the lead.

**LHM does all of the GoHighLevel setup. The client never does.** If LHM does not yet have access to the client's GoHighLevel account or sub-account, stop and get that access arranged first. Do not ask the client to build a Workflow or copy a URL.

## 1. Set up the Workflow in GoHighLevel (LHM)

1. In the client's account, create a Workflow with the **Inbound Webhook** trigger. Inbound Webhook is a premium trigger, so check the client's plan includes it (see the fallback below if it does not).
2. Copy the webhook URL GoHighLevel generates. Treat it as a secret: anyone who has it can create leads.
3. Send one test request (Step 3 below, from the command line or the deployed form) so GoHighLevel captures a sample payload, then map the fields in the Workflow: create or update the contact from `name`, `email` and `phone`, add the message as a note, tag by `form_name`, and add the action the client wants (notification, pipeline stage, follow-up). Check the current GoHighLevel documentation for the exact action names, as the interface changes.
4. Publish the Workflow only after the test lead looks right in the contact record.

## 2. Store the webhook URL as a Cloudflare secret

The URL lives in the Cloudflare Pages secret `GHL_WEBHOOK_URL`. Set it from `site/`:

```bash
npx wrangler pages secret put GHL_WEBHOOK_URL --project-name <pages-project-name>
```

Paste the URL at the prompt. Also set `TURNSTILE_SECRET_KEY` the same way. Set the secret for the production environment and, if previews are used, the preview environment too.

Never commit the webhook URL. It must not appear in `wrangler.toml`, `.dev.vars` under version control, the README, the brain notes, the project file, chat messages or any log. `wrangler.toml` holds only the public values (for example `PUBLIC_TURNSTILE_SITE_KEY`). For local testing, put the secret in `site/.dev.vars` and confirm `.dev.vars` is in `.gitignore` before the first commit. If the URL is ever exposed, rotate it by creating a new Inbound Webhook trigger in GoHighLevel, update the secret, and delete the old trigger.

## 3. The Pages Function

`site/functions/api/contact.js`. Verification order matches the D1 reference in [contact-function.md](contact-function.md): method, honeypot, Turnstile, required fields, timing, validation, content filter, then the webhook call. The validation helpers (`cleanField`, `validateEmail`, `validatePhone`, `validateSubmissionTiming`, `findContentSpamReason`, `jsonResponse`) are the same ones as in that file; copy them across unchanged. Because there is no D1 here, rejected attempts are only written to the function log with `console.warn`.

```js
// site/functions/api/contact.js  (GoHighLevel inbound webhook)
// Helpers cleanField, cleanMessage, jsonResponse, validateEmail, validatePhone,
// validateSubmissionTiming, findContentSpamReason: copy from contact-function.md.

export async function onRequestPost({ request, env }) {
  if (!env.GHL_WEBHOOK_URL) {
    return jsonResponse({ ok: false, message: 'Form delivery is not configured yet.' }, 500);
  }

  let formData;
  try {
    formData = await request.formData();
  } catch {
    return jsonResponse({ ok: false, message: 'Invalid request.' }, 400);
  }

  // Honeypot: pretend success, send nothing.
  if (cleanField(formData.get('website'), 100)) {
    console.warn('rejected: honeypot');
    return jsonResponse({ ok: true, message: 'Thanks, your message has been sent.' });
  }

  // Turnstile first, before anything is trusted or forwarded.
  const turnstile = await verifyTurnstile(formData.get('cf-turnstile-response'), request, env);
  if (!turnstile.success) {
    console.warn('rejected: turnstile_failed');
    return jsonResponse({ ok: false, message: 'Please refresh the page and try again.' }, 400);
  }

  const lead = {
    name: cleanField(formData.get('name'), 120),
    phone: cleanField(formData.get('phone'), 60),
    email: cleanField(formData.get('email'), 254),
    preferred_time: cleanField(formData.get('preferred_time'), 160),
    message: cleanMessage(formData.get('message')),
    source_path: cleanField(formData.get('source_path'), 240) || '/contact/',
    form_name: cleanField(formData.get('form_name'), 100) || 'Contact Form',
  };

  if (!lead.name || !lead.phone || !lead.email || !lead.message) {
    return jsonResponse({ ok: false, message: 'Please complete the required fields.' }, 400);
  }
  const timingReason = validateSubmissionTiming(cleanField(formData.get('form_started_at'), 40));
  if (timingReason) {
    console.warn('rejected: timing_check_failed', timingReason);
    return jsonResponse({ ok: false, message: 'Please check the form and try again.' }, 400);
  }
  if (!validateEmail(lead.email)) {
    return jsonResponse({ ok: false, message: 'Please enter a valid email address.' }, 400);
  }
  if (!validatePhone(lead.phone)) {
    return jsonResponse({ ok: false, message: 'Please enter a valid phone number.' }, 400);
  }
  const spamReason = findContentSpamReason(lead);
  if (spamReason) {
    console.warn('rejected: content_filter', spamReason);
    return jsonResponse({ ok: false, message: 'Please call directly if your message will not submit.' }, 400);
  }

  // Forward to the GoHighLevel inbound webhook as JSON.
  let response;
  try {
    response = await fetch(env.GHL_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ ...lead, submitted_at: new Date().toISOString() }),
    });
  } catch (error) {
    console.error('GoHighLevel webhook request failed', error);
    return jsonResponse({ ok: false, message: 'Could not send your message. Please call us directly.' }, 502);
  }
  if (!response.ok) {
    console.error('GoHighLevel webhook returned', response.status);
    return jsonResponse({ ok: false, message: 'Could not send your message. Please call us directly.' }, 502);
  }

  return jsonResponse({ ok: true, message: 'Thanks, your message has been sent.' });
}

export async function onRequest() {
  return jsonResponse({ ok: false, message: 'Method not allowed.' }, 405);
}

// verifyTurnstile: same as contact-function.md (TURNSTILE_SECRET_KEY, siteverify).
```

Do not log the webhook URL, the lead's details or the GoHighLevel response body. On a non-2xx response the user sees an error and is not redirected to the thank-you page: a lead that never reached GoHighLevel must not look like a success.

## 4. Fallback: plan without inbound webhooks

If the client's GoHighLevel plan does not include the Inbound Webhook trigger, use the GoHighLevel API v2 contact upsert instead. The Function is identical up to the point of the `fetch`, which then calls the contacts upsert endpoint with a private integration token held in the Cloudflare secret `GHL_PRIVATE_TOKEN` (set with `wrangler pages secret put`, never committed). Also store the location ID the same way or as a non-secret variable.

Do not copy endpoint paths, header names or API version values from memory. Check the current official GoHighLevel API v2 documentation for the contacts upsert endpoint and its required headers and version before writing the call, and for the scopes the private integration token needs. Create the private integration in the client's account as LHM, never through the client. Ask the user before choosing this fallback, because it is a different permission to hold.

## 5. Both paths still need

- The thank-you page (`noindex, nofollow`) and the `data-thank-you` redirect in the form markup.
- GA tracking: the thank-you page view is the conversion, so confirm the GA4 key event fires there (and only there).
- The anti-spam stack on the form itself: Turnstile widget, honeypot and `form_started_at`.

## 6. Verification

- [ ] `node --check site/functions/api/contact.js`
- [ ] Local: `npx wrangler pages dev` with `site/.dev.vars` (gitignored) holding `GHL_WEBHOOK_URL` and a Turnstile test secret
- [ ] A test submission creates or updates the contact in the client's GoHighLevel account with the right fields, tag and Workflow action
- [ ] A submission with the honeypot filled and one with a bad Turnstile token create nothing in GoHighLevel
- [ ] With the webhook URL deliberately wrong in a preview environment, the form shows the error and does not redirect
- [ ] `git grep` for the webhook URL host and for `GHL_WEBHOOK_URL=` finds nothing in the repo or its history
- [ ] The thank-you page returns `noindex, nofollow` and fires the GA4 event once
