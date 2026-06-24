# functions/api/contact.js — Reference Implementation

Full Cloudflare Pages Function for form submission handling.

```js
// functions/api/contact.js

export async function onRequestPost(context) {
  const { request, env } = context;

  let formData;
  try {
    formData = await request.formData();
  } catch {
    return jsonResponse({ ok: false, message: 'Invalid request.' }, 400);
  }

  // Honeypot check — silent pass if bot filled the field
  if (formData.get('website')) {
    return jsonResponse({ ok: true, message: "Thanks, your message has been sent." });
  }

  // Extract and clean fields
  const name        = clean(formData.get('name'), 100);
  const email       = clean(formData.get('email'), 254);
  const phone       = clean(formData.get('phone'), 30);
  const preferredTime = clean(formData.get('preferred_time'), 100);
  const message     = clean(formData.get('message'), 5000);
  const sourcePath  = clean(formData.get('source_path'), 200);
  const formName    = clean(formData.get('form_name'), 100);
  const cfToken     = formData.get('cf-turnstile-response') || '';
  const userAgent   = request.headers.get('user-agent') || '';

  // Validate required fields
  if (!name || !email || !message || !email.includes('@')) {
    return jsonResponse({ ok: false, message: 'Please complete the required fields.' }, 422);
  }

  // Verify Turnstile
  let turnstileVerified = 0;
  if (env.TURNSTILE_SECRET_KEY) {
    const tsResult = await verifyTurnstile(cfToken, env.TURNSTILE_SECRET_KEY, request);
    if (!tsResult.success) {
      return jsonResponse({ ok: false, message: 'Security check failed. Please try again.' }, 422);
    }
    turnstileVerified = 1;
  }
  // If no secret key (local dev), allow through with turnstile_verified = 0

  // Save to D1 first — before any email/CRM action
  let emailStatus = 'pending';
  let submissionId;
  try {
    const stmt = env.DB.prepare(`
      INSERT INTO contact_submissions
        (name, phone, email, preferred_time, message, source_path, form_name, user_agent, turnstile_verified, email_status, crm_status)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', 'not_configured')
    `);
    const result = await stmt.bind(
      name, phone, email, preferredTime, message,
      sourcePath, formName, userAgent, turnstileVerified
    ).run();
    submissionId = result.meta?.last_row_id;
  } catch (err) {
    console.error('D1 insert failed:', err);
    return jsonResponse({ ok: false, message: 'Could not save your submission. Please try again.' }, 500);
  }

  // Attempt email notification — failure must not fail the user response
  const submission = { name, phone, email, preferredTime, message, sourcePath, formName };
  try {
    await sendNotification(submission, env);
    emailStatus = 'sent';
  } catch (err) {
    console.error('Email notification failed:', err);
    emailStatus = 'failed';
  }

  // Update email_status in D1
  if (submissionId) {
    try {
      await env.DB.prepare(
        'UPDATE contact_submissions SET email_status = ? WHERE id = ?'
      ).bind(emailStatus, submissionId).run();
    } catch (err) {
      console.error('Failed to update email_status:', err);
    }
  }

  return jsonResponse({ ok: true, message: "Thanks, your message has been sent." });
}

export async function onRequest(context) {
  if (context.request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }
  return onRequestPost(context);
}

// --- Helpers ---

function clean(value, maxLen) {
  if (!value) return '';
  return String(value).trim().slice(0, maxLen);
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

async function verifyTurnstile(token, secretKey, request) {
  const ip = request.headers.get('CF-Connecting-IP') || '';
  const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ secret: secretKey, response: token, remoteip: ip }),
  });
  return res.json();
}

// --- Email provider abstraction ---
// Swap provider by changing this function only.

async function sendNotification(submission, env) {
  const provider = detectProvider(env);
  if (provider === 'mailgun') return sendMailgun(submission, env);
  if (provider === 'postmark') return sendPostmark(submission, env);
  if (provider === 'resend') return sendResend(submission, env);
  throw new Error('No email provider configured');
}

function detectProvider(env) {
  if (env.MAILGUN_API_KEY) return 'mailgun';
  if (env.POSTMARK_API_KEY) return 'postmark';
  if (env.RESEND_API_KEY) return 'resend';
  return null;
}

async function sendMailgun(submission, env) {
  const region = (env.MAILGUN_REGION || 'us').toLowerCase();
  const apiBase = region === 'eu'
    ? 'https://api.eu.mailgun.net'
    : 'https://api.mailgun.net';

  const body = new URLSearchParams({
    from: `${env.CONTACT_NOTIFICATION_FROM || 'website@example.com'}`,
    to: env.CONTACT_NOTIFICATION_TO,
    subject: `New form submission — ${submission.formName || 'Contact'}`,
    'h:Reply-To': submission.email,
    text: formatEmailText(submission),
  });
  if (env.CONTACT_NOTIFICATION_CC) {
    body.set('cc', env.CONTACT_NOTIFICATION_CC);
  }

  const res = await fetch(`${apiBase}/v3/${env.MAILGUN_DOMAIN}/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${btoa('api:' + env.MAILGUN_API_KEY)}`,
    },
    body,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Mailgun error ${res.status}: ${text}`);
  }
}

async function sendPostmark(submission, env) {
  const body = {
    From: env.CONTACT_NOTIFICATION_FROM || 'website@example.com',
    To: env.CONTACT_NOTIFICATION_TO,
    Subject: `New form submission — ${submission.formName || 'Contact'}`,
    ReplyTo: submission.email,
    TextBody: formatEmailText(submission),
  };
  if (env.CONTACT_NOTIFICATION_CC) body.Cc = env.CONTACT_NOTIFICATION_CC;

  const res = await fetch('https://api.postmarkapp.com/email', {
    method: 'POST',
    headers: {
      'X-Postmark-Server-Token': env.POSTMARK_API_KEY,
      'content-type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Postmark error ${res.status}: ${text}`);
  }
}

async function sendResend(submission, env) {
  const body = {
    from: env.CONTACT_NOTIFICATION_FROM || 'website@example.com',
    to: [env.CONTACT_NOTIFICATION_TO],
    subject: `New form submission — ${submission.formName || 'Contact'}`,
    reply_to: submission.email,
    text: formatEmailText(submission),
  };
  if (env.CONTACT_NOTIFICATION_CC) body.cc = [env.CONTACT_NOTIFICATION_CC];

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Resend error ${res.status}: ${text}`);
  }
}

function formatEmailText(s) {
  return [
    `New submission from: ${s.formName || 'Contact Form'}`,
    `Page: ${s.sourcePath || '(unknown)'}`,
    '',
    `Name: ${s.name}`,
    `Email: ${s.email}`,
    s.phone ? `Phone: ${s.phone}` : null,
    s.preferredTime ? `Preferred time: ${s.preferredTime}` : null,
    '',
    `Message:`,
    s.message,
  ].filter(l => l !== null).join('\n');
}
```
