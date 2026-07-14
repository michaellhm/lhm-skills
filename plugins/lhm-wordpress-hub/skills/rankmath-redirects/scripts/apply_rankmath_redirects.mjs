import fs from 'node:fs/promises';

const envPath = process.env.WP_API_ENV || '/private/tmp/wp-api.env';
const payloadPath = process.env.REDIRECT_PAYLOAD || new URL('../rankmath-redirects-payload.json', import.meta.url);
const dryRun = process.argv.includes('--dry-run');
const verifyOnly = process.argv.includes('--verify-only');
const skipVerify = process.argv.includes('--skip-verify');

function parseEnv(raw) {
  const env = {};
  for (const line of raw.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    let value = match[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    env[match[1]] = value;
  }
  return env;
}

function value(env, names) {
  for (const name of names) {
    if (env[name]) return env[name];
  }
  return '';
}

function absoluteUrl(site, pathOrUrl) {
  return new URL(pathOrUrl, site.replace(/\/$/, '') + '/').toString();
}

function expectedLocation(site, target) {
  return target.startsWith('http://') || target.startsWith('https://') ? target : absoluteUrl(site, target);
}

async function postRedirect(endpoint, credentials, payload, item) {
  const response = await fetch(`${endpoint}/updateRedirection`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${Buffer.from(`${credentials.user}:${credentials.password}`).toString('base64')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      objectType: payload.objectType || 'post',
      objectID: payload.objectID || 29,
      hasRedirect: true,
      redirectionID: item.redirectionID || '',
      redirectionSources: item.source,
      redirectionUrl: item.target,
      redirectionType: String(item.code || 301)
    })
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(`${item.source}: ${response.status} ${response.statusText}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function deleteRedirect(endpoint, credentials, payload, item) {
  if (!item.redirectionID) {
    throw new Error(`${item.source || '(unknown source)'}: cleanup items require redirectionID.`);
  }

  const response = await fetch(`${endpoint}/updateRedirection`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${Buffer.from(`${credentials.user}:${credentials.password}`).toString('base64')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      objectType: payload.objectType || 'post',
      objectID: payload.objectID || 29,
      hasRedirect: false,
      redirectionID: String(item.redirectionID),
      redirectionSources: item.source || '/cleanup-placeholder',
      redirectionUrl: '',
      redirectionType: String(item.code || 301)
    })
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(`${item.redirectionID}: ${response.status} ${response.statusText}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function verifyRedirect(site, item) {
  const source = item.verifySource || item.source;
  const url = absoluteUrl(site, `${source}?codex_redirect_verify=${Date.now()}`);
  const response = await fetch(url, { redirect: 'manual' });
  const location = response.headers.get('location') || '';
  const expected = expectedLocation(site, item.target);

  const okStatus = response.status === (item.code || 301);
  const okLocation = location === expected || location.startsWith(`${expected}?`);

  return {
    source,
    target: item.target,
    status: response.status,
    location,
    ok: okStatus && okLocation
  };
}

const [envRaw, payloadRaw] = await Promise.all([
  fs.readFile(envPath, 'utf8'),
  fs.readFile(payloadPath, 'utf8')
]);

const env = parseEnv(envRaw);
const payload = JSON.parse(payloadRaw);
const site = value(env, ['WP_API_URL', 'WP_SITE_URL', 'WP_URL', 'WORDPRESS_URL', 'SITE_URL']) || payload.site;
const user = value(env, ['WP_API_USER', 'WP_USERNAME', 'WP_USER', 'WORDPRESS_USER', 'USERNAME']);
const password = value(env, ['WP_API_PASSWORD', 'WP_APP_PASSWORD', 'WORDPRESS_APP_PASSWORD', 'PASSWORD']);

if (!site || !user || !password) {
  throw new Error(`Missing required env values. Need site URL, user, and application password in ${envPath}.`);
}

const endpoint = `${site.replace(/\/$/, '')}/wp-json/rankmath/v1`;
const redirects = payload.redirects || [];
const cleanup = payload.cleanup || [];

console.log(`${dryRun ? 'Dry run' : verifyOnly ? 'Verifying' : 'Applying'} Rank Math redirects on ${site}`);
console.log(`Redirects: ${redirects.length}`);

if (!verifyOnly) {
  if (cleanup.length) {
    console.log(`Cleanup: ${cleanup.length}`);
    for (const item of cleanup) {
      console.log(`delete #${item.redirectionID} ${item.source || ''}`.trim());
      if (dryRun) continue;
      const result = await deleteRedirect(endpoint, { user, password }, payload, item);
      console.log(`  ${result.action || 'ok'} ${result.message || ''}`.trim());
    }
  }

  for (const item of redirects) {
    console.log(`${item.source} -> ${item.target}`);
    if (dryRun) continue;
    const result = await postRedirect(endpoint, { user, password }, payload, item);
    console.log(`  ${result.action || 'ok'} #${result.id || 'n/a'} ${result.message || ''}`.trim());
  }
}

if (!dryRun && !skipVerify) {
  console.log('Verifying public redirects...');
  const failures = [];
  for (const item of redirects) {
    const result = await verifyRedirect(site, item);
    console.log(`${result.ok ? 'OK' : 'FAIL'} ${result.status} ${result.source} -> ${result.location}`);
    if (!result.ok) failures.push(result);
  }

  if (failures.length) {
    throw new Error(`${failures.length} redirect verification checks failed.`);
  }
}

if (payload.skipped?.length) {
  console.log('Skipped:');
  for (const item of payload.skipped) {
    console.log(`- ${item.source}: ${item.reason}`);
  }
}

console.log('Done.');
