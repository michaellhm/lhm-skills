# functions/admin/submissions.js — Reference Implementation

Protected admin page to view accepted D1 form submissions and rejected spam attempts.

```js
// functions/admin/submissions.js

export async function onRequest(context) {
  const { request, env } = context;

  const expectedUser = env.ADMIN_USERNAME;
  const expectedPass = env.ADMIN_PASSWORD;
  if (!expectedUser || !expectedPass) {
    return new Response('Admin access not configured.', {
      status: 403,
      headers: { 'content-type': 'text/plain', 'cache-control': 'no-store' },
    });
  }

  const authHeader = request.headers.get('Authorization') || '';
  const [scheme, encoded] = authHeader.split(' ');
  if (scheme !== 'Basic' || !encoded) {
    return unauthorised();
  }

  let decoded = '';
  try {
    decoded = atob(encoded);
  } catch {
    return unauthorised();
  }

  const colonIdx = decoded.indexOf(':');
  const user = decoded.slice(0, colonIdx);
  const pass = decoded.slice(colonIdx + 1);

  if (user !== expectedUser || pass !== expectedPass) {
    return unauthorised();
  }

  let rows = [];
  let rejectedRows = [];
  try {
    const submissions = await env.DB.prepare(
      'SELECT * FROM contact_submissions ORDER BY submitted_at DESC LIMIT 100'
    ).all();
    rows = submissions.results || [];

    const rejected = await env.DB.prepare(
      'SELECT * FROM contact_spam_rejections ORDER BY rejected_at DESC LIMIT 100'
    ).all();
    rejectedRows = rejected.results || [];
  } catch (err) {
    return new Response(`Database error: ${escHtml(String(err))}`, {
      status: 500,
      headers: { 'content-type': 'text/html', 'cache-control': 'no-store' },
    });
  }

  return new Response(renderPage(rows, rejectedRows), {
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store',
      'x-robots-tag': 'noindex, nofollow',
    },
  });
}

function unauthorised() {
  return new Response('Unauthorised', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Admin"',
      'content-type': 'text/plain',
      'cache-control': 'no-store',
    },
  });
}

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderTable(rows, cols, emptyText) {
  const thead = `<tr>${cols.map((col) => `<th>${escHtml(col)}</th>`).join('')}</tr>`;
  const tbody = rows.map((row) =>
    `<tr>${cols.map((col) => `<td>${escHtml(row[col])}</td>`).join('')}</tr>`
  ).join('');

  return `<table>
    <thead>${thead}</thead>
    <tbody>${tbody || `<tr><td colspan="${cols.length}">${escHtml(emptyText)}</td></tr>`}</tbody>
  </table>`;
}

function renderPage(rows, rejectedRows) {
  const submissionCols = [
    'submitted_at',
    'name',
    'phone',
    'email',
    'preferred_time',
    'source_path',
    'form_name',
    'email_status',
    'crm_status',
    'message',
  ];
  const rejectedCols = [
    'rejected_at',
    'reason',
    'detail',
    'source_path',
    'name',
    'phone',
    'email',
    'message_preview',
    'ip_address',
  ];

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex, nofollow">
  <title>Form Submissions</title>
  <style>
    body { font-family: sans-serif; font-size: 13px; padding: 1rem; }
    table { border-collapse: collapse; margin-bottom: 2rem; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; vertical-align: top; }
    th { background: #f0f0f0; white-space: nowrap; }
    td { max-width: 320px; word-break: break-word; }
    tr:nth-child(even) { background: #fafafa; }
  </style>
</head>
<body>
  <h1>Form Submissions</h1>
  <p>Latest accepted submissions: ${rows.length}</p>
  ${renderTable(rows, submissionCols, 'No submissions yet.')}

  <h2>Rejected Attempts</h2>
  <p>Latest rejected attempts: ${rejectedRows.length}</p>
  ${renderTable(rejectedRows, rejectedCols, 'No rejected attempts yet.')}
</body>
</html>`;
}
```
