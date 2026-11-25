# functions/api/contact.js — Reference Implementation

Full Cloudflare Pages Function for form submission handling. This reference is the default for future Astro builds and includes Turnstile verification, honeypot handling, timing checks, field validation, lightweight content filtering, accepted-submission storage, rejected-attempt logging, and email notifications.

```js
// functions/api/contact.js

const MAX_FIELD_LENGTHS = {
  name: 120,
  phone: 60,
  email: 254,
  preferred_time: 160,
  message: 5000,
  source_path: 240,
  form_name: 100,
  form_started_at: 40,
};

const MIN_SUBMISSION_SECONDS = 3;
const MAX_SUBMISSION_SECONDS = 60 * 60 * 24;
const MAX_LINKS = 1;
const SPAM_PATTERNS = [
  /\bcasino\b/i,
  /\bcrypto(?:currency)?\b/i,
  /\bforex\b/i,
  /\bloan\b/i,
  /\bbacklinks?\b/i,
  /\bguest post\b/i,
  /\blink building\b/i,
  /\bseo services?\b/i,
  /\btraffic to your (?:site|website)\b/i,
  /\brank (?:higher|#?1|number one)\b/i,
  /\bwhatsapp\b/i,
  /\btelegram\b/i,
  /\bviagra\b/i,
  /\bcialis\b/i,
];

export async function onRequestPost({ request, env }) {
  if (!env.DB) {
    return jsonResponse({ ok: false, message: 'Form storage is not configured yet.' }, 500);
  }

  let formData;
  try {
    formData = await request.formData();
  } catch {
    return jsonResponse({ ok: false, message: 'Invalid request.' }, 400);
  }

  const submission = {
    name: cleanField(formData.get('name'), MAX_FIELD_LENGTHS.name),
    phone: cleanField(formData.get('phone'), MAX_FIELD_LENGTHS.phone),
    email: cleanField(formData.get('email'), MAX_FIELD_LENGTHS.email),
    preferred_time: cleanField(formData.get('preferred_time'), MAX_FIELD_LENGTHS.preferred_time),
    message: cleanMessage(formData.get('message')),
    source_path: cleanField(formData.get('source_path'), MAX_FIELD_LENGTHS.source_path) || '/contact/',
    form_name: cleanField(formData.get('form_name'), MAX_FIELD_LENGTHS.form_name) || 'Contact Form',
    form_started_at: cleanField(formData.get('form_started_at'), MAX_FIELD_LENGTHS.form_started_at),
    user_agent: cleanField(request.headers.get('user-agent'), 500),
  };

  if (cleanField(formData.get('website'), 100)) {
    await logRejection(env, 'honeypot', 'website field was filled', submission, request);
    return jsonResponse({ ok: true, message: 'Thanks, your message has been sent.' });
  }

  const turnstileResult = await verifyTurnstile(formData.get('cf-turnstile-response'), request, env);
  if (!turnstileResult.success) {
    return rejectSubmission(env, request, 'turnstile_failed', turnstileResult['error-codes']?.join(',') || 'verification failed', submission, 400, 'Please refresh the page and try again.');
  }

  if (!submission.name || !submission.phone || !submission.email || !submission.message) {
    return rejectSubmission(env, request, 'missing_required_fields', 'name, phone, email, and message are required', submission, 400, 'Please complete the required fields.');
  }

  const timingReason = validateSubmissionTiming(submission.form_started_at);
  if (timingReason) {
    return rejectSubmission(env, request, 'timing_check_failed', timingReason, submission);
  }

  if (!validateEmail(submission.email)) {
    return rejectSubmission(env, request, 'invalid_email', 'email failed format validation', submission, 400, 'Please enter a valid email address.');
  }

  if (!validatePhone(submission.phone)) {
    return rejectSubmission(env, request, 'invalid_phone', 'phone failed format validation', submission, 400, 'Please enter a valid phone number.');
  }

  const contentSpamReason = findContentSpamReason(submission);
  if (contentSpamReason) {
    return rejectSubmission(env, request, 'content_filter', contentSpamReason, submission, 400, 'Please call directly if your message will not submit.');
  }

  let submissionId;
  try {
    const insert = await env.DB.prepare(`
      INSERT INTO contact_submissions (
        name,
        phone,
        email,
        preferred_time,
        message,
        source_path,
        form_name,
        user_agent,
        turnstile_verified,
        email_status,
        crm_status
      )
      VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, 'pending', 'not_configured')
    `)
      .bind(
        submission.name,
        submission.phone,
        submission.email,
        submission.preferred_time,
        submission.message,
        submission.source_path,
        submission.form_name,
        submission.user_agent,
        turnstileResult.skipped ? 0 : 1,
      )
      .run();
    submissionId = insert.meta?.last_row_id;
  } catch (error) {
    console.error('D1 insert failed:', error);
    return jsonResponse({ ok: false, message: 'Could not save your submission. Please try again.' }, 500);
  }

  let emailStatus = 'not_configured';
  try {
    emailStatus = await sendNotification(submission, env);
  } catch (error) {
    emailStatus = 'failed';
    console.error('Contact notification failed', error);
  }

  if (submissionId) {
    try {
      await env.DB.prepare('UPDATE contact_submissions SET email_status = ?1 WHERE id = ?2')
        .bind(emailStatus, submissionId)
        .run();
    } catch (error) {
      console.error('Failed to update email_status:', error);
    }
  }

  return jsonResponse({ ok: true, message: 'Thanks, your message has been sent.' });
}

export async function onRequest() {
  return jsonResponse({ ok: false, message: 'Method not allowed.' }, 405);
}

function cleanField(value, maxLength) {
  return String(value || '').replace(/\s+/g, ' ').trim().slice(0, maxLength);
}

function cleanMessage(value) {
  return String(value || '').replace(/\r\n/g, '\n').trim().slice(0, MAX_FIELD_LENGTHS.message);
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
    },
  });
}

async function verifyTurnstile(token, request, env) {
  if (!env.TURNSTILE_SECRET_KEY) {
    return { success: true, skipped: true };
  }

  if (!token) {
    return { success: false, error: 'missing-token' };
  }

  const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      secret: env.TURNSTILE_SECRET_KEY,
      response: token,
      remoteip: request.headers.get('CF-Connecting-IP') || '',
    }),
  });

  return response.json();
}

async function logRejection(env, reason, detail, submission, request) {
  if (!env.DB) return;

  try {
    await env.DB.prepare(`
      INSERT INTO contact_spam_rejections (
        reason,
        detail,
        name,
        phone,
        email,
        message_preview,
        source_path,
        user_agent,
        ip_address
      )
      VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)
    `)
      .bind(
        reason,
        cleanField(detail, 240),
        cleanField(submission?.name, MAX_FIELD_LENGTHS.name),
        cleanField(submission?.phone, MAX_FIELD_LENGTHS.phone),
        cleanField(submission?.email, MAX_FIELD_LENGTHS.email),
        cleanField(submission?.message, 500),
        cleanField(submission?.source_path, MAX_FIELD_LENGTHS.source_path),
        cleanField(request.headers.get('user-agent'), 500),
        cleanField(request.headers.get('CF-Connecting-IP'), 64),
      )
      .run();
  } catch (error) {
    console.error('Contact spam rejection logging failed', error);
  }
}

async function rejectSubmission(env, request, reason, detail, submission, status = 400, message = 'Please check the form and try again.') {
  await logRejection(env, reason, detail, submission, request);
  return jsonResponse({ ok: false, message }, status);
}

function validateSubmissionTiming(startedAt) {
  const started = Number(startedAt);
  if (!Number.isFinite(started) || started <= 0) {
    return 'missing_or_invalid_timer';
  }

  const elapsedSeconds = (Date.now() - started) / 1000;
  if (elapsedSeconds < MIN_SUBMISSION_SECONDS) {
    return `submitted_too_fast_${elapsedSeconds.toFixed(1)}s`;
  }
  if (elapsedSeconds > MAX_SUBMISSION_SECONDS || elapsedSeconds < -30) {
    return 'stale_or_future_timer';
  }

  return '';
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
}

function validatePhone(phone) {
  const digits = phone.replace(/\D/g, '');
  if (digits.length < 8 || digits.length > 15) return false;
  if (/^(\d)\1+$/.test(digits)) return false;
  return /^[+()\d\s.-]+$/.test(phone);
}

function countLinks(value) {
  const matches = String(value || '').match(/(?:https?:\/\/|www\.|[a-z0-9-]+\.(?:com|net|org|info|biz|io|co|ru|cn|xyz)\b)/gi);
  return matches ? matches.length : 0;
}

function findContentSpamReason(submission) {
  const combined = `${submission.name}\n${submission.email}\n${submission.phone}\n${submission.preferred_time}\n${submission.message}`;
  const linkCount = countLinks(combined);
  if (linkCount > MAX_LINKS) {
    return `too_many_links_${linkCount}`;
  }

  const matchedPattern = SPAM_PATTERNS.find((pattern) => pattern.test(combined));
  if (matchedPattern) {
    return `spam_pattern_${matchedPattern.source.replace(/[^a-z0-9]+/gi, '_').slice(0, 60)}`;
  }

  if (submission.message && submission.message.length < 12) {
    return 'message_too_short';
  }

  return '';
}

async function sendNotification(submission, env) {
  const provider = detectProvider(env);
  if (provider === 'mailgun') return sendMailgun(submission, env);
  if (provider === 'postmark') return sendPostmark(submission, env);
  if (provider === 'resend') return sendResend(submission, env);
  return 'not_configured';
}

function detectProvider(env) {
  if (env.MAILGUN_API_KEY && env.MAILGUN_DOMAIN) return 'mailgun';
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
    from: env.CONTACT_NOTIFICATION_FROM || 'website@example.com',
    to: env.CONTACT_NOTIFICATION_TO,
    subject: `New form submission - ${submission.form_name || 'Contact'}`,
    'h:Reply-To': submission.email,
    text: formatEmailText(submission),
  });
  if (env.CONTACT_NOTIFICATION_CC) {
    body.set('cc', env.CONTACT_NOTIFICATION_CC);
  }

  const response = await fetch(`${apiBase}/v3/${env.MAILGUN_DOMAIN}/messages`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`,
    },
    body,
  });

  if (!response.ok) {
    throw new Error(`Mailgun returned ${response.status}: ${await response.text()}`);
  }

  return 'sent';
}

async function sendPostmark(submission, env) {
  const body = {
    From: env.CONTACT_NOTIFICATION_FROM || 'website@example.com',
    To: env.CONTACT_NOTIFICATION_TO,
    Subject: `New form submission - ${submission.form_name || 'Contact'}`,
    ReplyTo: submission.email,
    TextBody: formatEmailText(submission),
  };
  if (env.CONTACT_NOTIFICATION_CC) body.Cc = env.CONTACT_NOTIFICATION_CC;

  const response = await fetch('https://api.postmarkapp.com/email', {
    method: 'POST',
    headers: {
      'X-Postmark-Server-Token': env.POSTMARK_API_KEY,
      'content-type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Postmark returned ${response.status}: ${await response.text()}`);
  }

  return 'sent';
}

async function sendResend(submission, env) {
  const body = {
    from: env.CONTACT_NOTIFICATION_FROM || 'website@example.com',
    to: [env.CONTACT_NOTIFICATION_TO],
    subject: `New form submission - ${submission.form_name || 'Contact'}`,
    reply_to: submission.email,
    text: formatEmailText(submission),
  };
  if (env.CONTACT_NOTIFICATION_CC) body.cc = [env.CONTACT_NOTIFICATION_CC];

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Resend returned ${response.status}: ${await response.text()}`);
  }

  return 'sent';
}

function formatEmailText(submission) {
  return [
    `New submission from: ${submission.form_name || 'Contact Form'}`,
    `Page: ${submission.source_path || '(unknown)'}`,
    '',
    `Name: ${submission.name}`,
    `Phone: ${submission.phone}`,
    `Email: ${submission.email}`,
    submission.preferred_time ? `Preferred time: ${submission.preferred_time}` : null,
    '',
    'Message:',
    submission.message,
  ].filter((line) => line !== null).join('\n');
}
```
