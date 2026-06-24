# functions/admin/submissions.js — Reference Implementation

Protected admin page to view the latest D1 form submissions.

```js
// functions/admin/submissions.js

export async function onRequest(context) {
  const { request, env } = context;

  // Require credentials to be configured
  const expectedUser = env.ADMIN_USERNAME;
  const expectedPass = env.ADMIN_PASSWORD;
  if (!expectedUser || !expectedPass) {
    return new Response('Admin access not configured.', {
      status: 403,
      headers: { 'content-type': 'text/plain' },
    });
  }

  // HTTP Basic Auth
  const authHeader = request.headers.get('Authorization') || '';
  const [scheme, encoded] = authHeader.split(' ');
  if (scheme !== 'Basic' || !encoded) {
    return unauthorised();
  }

  const decoded = atob(encoded);
  const colonIdx = decoded.indexOf(':');
  const user = decoded.slice(0, colonIdx);
  const pass = decoded.slice(colonIdx + 1);

  if (user !== expectedUser || pass !== expectedPass) {
    return unauthorised();
  }

  // Query D1
  let rows = [];
  try {
    const result = await env.DB.prepare(
      'SELECT * FROM contact_submissions ORDER BY submitted_at DESC LIMIT 100'
    ).all();
    rows = result.results || [];
  } catch (err) {
    return new Response(`Database error: ${escHtml(String(err))}`, {
      status: 500,
      headers: { 'content-type': 'text/html', 'cache-control': 'no-store' },
    });
  }

  const html = renderTable(rows);
  return new Response(html, {
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

function renderTable(rows) {
  const cols = [
    'submitted_at', 'name', 'phone', 'email',
    'preferred_time', 'source_path', 'form_name',
    'email_status', 'crm_status', 'message'
  ];

  const thead = `<tr>${cols.map(c => `<th>${escHtml(c)}</th>`).join('')}</tr>`;
  const tbody = rows.map(row =>
    `<tr>${cols.map(c => `<td>${escHtml(row[c])}</td>`).join('')}</tr>`
  ).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex, nofollow">
  <title>Submissions</title>
  <style>
    body { font-family: sans-serif; font-size: 13px; padding: 1rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; vertical-align: top; }
    th { background: #f0f0f0; white-space: nowrap; }
    td { max-width: 300px; word-break: break-word; }
    tr:nth-child(even) { background: #fafafa; }
  </style>
</head>
<body>
  <h1>Form Submissions (latest 100)</h1>
  <p>Total shown: ${rows.length}</p>
  <table>
    <thead>${thead}</thead>
    <tbody>${tbody || '<tr><td colspan="10">No submissions yet.</td></tr>'}</tbody>
  </table>
</body>
</html>`;
}
```
