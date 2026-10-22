#!/usr/bin/env node
import { readFile } from 'node:fs/promises';

const PRODUCTION_ORIGIN = 'https://lhm-social.pages.dev';
const verifiedStates = new Set(['scheduled_verified', 'published_verified']);
const pendingStates = new Set(['verification_pending', 'outcome_unknown', 'creating', 'uploading']);

function fail(message, details = {}) {
  process.stderr.write(`${JSON.stringify({ run_result: 'blocked', error: message, ...details })}\n`);
  process.exit(1);
}

const inputPath = process.argv[2];
if (!inputPath) fail('Pass the approved scheduling input JSON path.');

let input;
try { input = JSON.parse(await readFile(inputPath, 'utf8')); }
catch { fail('The scheduling input JSON could not be read.'); }

const baseUrl = input.base_url ?? PRODUCTION_ORIGIN;
if (baseUrl !== PRODUCTION_ORIGIN) fail('Only the verified production LHM Social API is allowed.');
if (input.approved !== true) fail('Explicit approval for this immutable package, platform set and time is required.');
if (typeof input.package_id !== 'string' || !input.package_id) fail('A package_id is required.');
if (typeof input.revision !== 'string' || !input.revision) fail('The approved catalogue revision is required.');
if (!Array.isArray(input.platforms) || input.platforms.length < 1 || input.platforms.length > 2 || new Set(input.platforms).size !== input.platforms.length || input.platforms.some(value => !['facebook', 'instagram'].includes(value))) fail('Choose facebook, instagram, or both.');
if (typeof input.local_time !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(input.local_time)) fail('local_time must be a Melbourne wall-clock value in YYYY-MM-DDTHH:mm format.');

const username = process.env.LHM_SOCIAL_API_USERNAME;
const password = process.env.LHM_SOCIAL_API_PASSWORD;
if (!username || !password) fail('Secure LHM Social API credentials are unavailable.', { next_action: 'configure API credentials' });
const authorization = `Basic ${Buffer.from(`${username}:${password}`, 'utf8').toString('base64')}`;

class ApiError extends Error {
  constructor(message, status = null) { super(message); this.status = status; }
}

async function request(path, { method = 'GET', body } = {}) {
  const url = new URL(path, baseUrl);
  if (url.origin !== PRODUCTION_ORIGIN) throw new ApiError('Refusing a request outside the verified production origin.');
  let response;
  try {
    response = await fetch(url, {
      method,
      redirect: 'manual',
      cache: 'no-store',
      headers: {
        Authorization: authorization,
        Accept: 'application/json',
        ...(body ? { 'Content-Type': 'application/json', Origin: PRODUCTION_ORIGIN } : {})
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(30000)
    });
  } catch { throw new ApiError('The protected API could not be reached.'); }
  if (response.status >= 300 && response.status < 400) throw new ApiError('The protected API attempted to redirect. No credentials were forwarded.', response.status);
  let data;
  try { data = await response.json(); }
  catch { throw new ApiError(`The API returned a non-JSON response (${response.status}).`, response.status); }
  if (!response.ok) throw new ApiError(data.error || `The API request failed (${response.status}).`, response.status);
  return data;
}

async function requiredRequest(path, options) {
  try { return await request(path, options); }
  catch (error) { fail(error.message, error.status ? { http_status: error.status } : {}); }
}

const setup = await requiredRequest('/api/setup');
if (setup.enabled !== true) fail('Live API scheduling is disabled.');
const enabledPlatforms = new Set((setup.accounts ?? []).filter(account => account.enabled).map(account => account.platform));
if (input.platforms.some(platform => !enabledPlatforms.has(platform))) fail('An approved platform is not connected to the verified LHM account.');

const catalogue = await requiredRequest('/scheduling-catalogue.json');
const item = Array.isArray(catalogue) ? catalogue.find(candidate => candidate.id === input.package_id) : null;
if (!item) fail('The approved package is not present in the deployed scheduling catalogue.');
if (input.revision !== item.revision) fail('The approved package revision has changed.');

async function status() {
  const data = await requiredRequest(`/api/status?packageId=${encodeURIComponent(item.id)}`);
  return Array.isArray(data.attempts) ? data.attempts : [];
}

function platformsMatch(attempts) {
  const actual = [...new Set(attempts.map(attempt => attempt.platform))].sort();
  const expected = [...input.platforms].sort();
  return JSON.stringify(actual) === JSON.stringify(expected);
}

function result(attempts, runResult) {
  return {
    run_result: runResult,
    package_id: item.id,
    revision: item.revision,
    platforms: input.platforms,
    scheduled_for_melbourne: input.local_time,
    attempts: attempts.map(({ platform, state, ghl_post_id, upstream_status, error, schedule_date }) => ({ platform, state, ghl_post_id, upstream_status, error, schedule_date })),
    next_action: runResult === 'verification_pending' ? 'inspect GoHighLevel' : 'none'
  };
}

let attempts = await status();
if (attempts.length) {
  const complete = platformsMatch(attempts) && attempts.every(attempt => verifiedStates.has(attempt.state));
  process.stdout.write(`${JSON.stringify(result(attempts, complete ? 'already_exists' : 'verification_pending'))}\n`);
  process.exit(complete ? 0 : 2);
}

const intent = { packageId: item.id, revision: item.revision, platforms: input.platforms, localTime: input.local_time };
const approval = await requiredRequest('/api/approval', { method: 'POST', body: intent });
if (typeof approval.nonce !== 'string' || !approval.nonce) fail('The API did not return a valid approval nonce.');
try {
  await request('/api/schedule', { method: 'POST', body: { ...intent, nonce: approval.nonce, approved: true } });
} catch (error) {
  attempts = await status();
  if (attempts.length) {
    process.stdout.write(`${JSON.stringify(result(attempts, 'verification_pending'))}\n`);
    process.exit(2);
  }
  fail(error.message, error.status ? { http_status: error.status } : {});
}

attempts = await status();
for (const attempt of attempts.filter(value => value.state === 'verification_pending' && value.ghl_post_id)) {
  await requiredRequest('/api/verify', { method: 'POST', body: { attemptId: attempt.id } });
}
attempts = await status();

const complete = attempts.length > 0 && platformsMatch(attempts) && attempts.every(attempt => verifiedStates.has(attempt.state));
const incomplete = attempts.some(attempt => pendingStates.has(attempt.state) || attempt.state === 'failed');
const runResult = complete
  ? (attempts.every(attempt => attempt.state === 'published_verified') ? 'published' : 'scheduled')
  : 'verification_pending';
process.stdout.write(`${JSON.stringify(result(attempts, runResult))}\n`);
process.exit(complete ? 0 : incomplete ? 2 : 1);
