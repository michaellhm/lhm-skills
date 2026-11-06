/** Mechanical static-prototype QA. It never grants semantic or publication approval. */
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

export const QA_ROOT = '/var/lib/lhm-prototype-feedback/qa-runs';
export const PAGES = ['index.html', 'about-tara.html', 'how-i-can-help.html', 'online-counselling.html', 'fees-and-getting-started.html']
  .map(name => 'luminary-counselling/homepage/' + name);
export const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value);
}
export function runPaths(source, output, root = QA_ROOT) {
  source = path.resolve(source); output = path.resolve(output); root = path.resolve(root);
  const relative = path.relative(root, source).split(path.sep);
  if (relative.length !== 2 || !/^[a-z0-9][a-z0-9-]{0,159}$/.test(relative[0]) || relative[1] !== 'source'
      || output !== path.join(root, relative[0], 'output')) throw new Error('source/output must be the same registered QA run');
  return { source, output, run: path.dirname(source), manifest: path.join(path.dirname(source), 'source-manifest.json') };
}
async function regular(file, requireRoot, maximum = 32 * 1024 * 1024) {
  const info = await fs.lstat(file);
  if (!info.isFile() || info.isSymbolicLink() || info.size > maximum || (info.mode & 0o022) || requireRoot && info.uid !== 0)
    throw new Error('source requires a bounded protected regular file');
  return info;
}
async function protectedDirectory(directory, requireRoot) {
  const info = await fs.lstat(directory);
  if (!info.isDirectory() || info.isSymbolicLink() || info.mode & 0o022 || requireRoot && info.uid !== 0)
    throw new Error('source directory is not protected');
}
export async function loadManifest(paths, { requireRoot = true } = {}) {
  await protectedDirectory(paths.run, requireRoot);
  await protectedDirectory(paths.source, requireRoot);
  await regular(paths.manifest, requireRoot, 1024 * 1024);
  const raw = await fs.readFile(paths.manifest);
  const manifest = JSON.parse(raw);
  if (manifest.schema_version !== 1 || !Array.isArray(manifest.files) || !Array.isArray(manifest.pages)
      || manifest.files.length === 0 || manifest.files.length > 1000 || !/^[a-f0-9]{64}$/.test(manifest.package_sha256)
      || sha(Buffer.from(canonical(manifest.files))) !== manifest.package_sha256
      || canonical([...manifest.pages].sort()) !== canonical([...PAGES].sort())) throw new Error('source manifest or five-page scope mismatch');
  const files = new Map();
  let totalBytes = 0;
  const expected = [];
  for (const entry of manifest.files) {
    const size = entry.size_bytes ?? entry.bytes;
    if (typeof entry.path !== 'string' || entry.path.startsWith('/') || entry.path.includes('\\') || entry.path.split('/').some(piece => !piece || piece === '.' || piece === '..')
        || !/^[a-f0-9]{64}$/.test(entry.sha256) || !Number.isSafeInteger(size) || size < 0 || files.has(entry.path)) throw new Error('invalid source manifest entry');
    totalBytes += size;
    if (totalBytes > 50 * 1024 * 1024) throw new Error('source package exceeds bounded QA memory');
    const file = path.join(paths.source, entry.path);
    let parent = path.dirname(file);
    while (parent !== paths.source) { await protectedDirectory(parent, requireRoot); parent = path.dirname(parent); }
    const info = await regular(file, requireRoot);
    const bytes = await fs.readFile(file);
    if (info.size !== size || bytes.length !== size || sha(bytes) !== entry.sha256) throw new Error('source bytes differ from exact manifest');
    files.set(entry.path, { bytes, sha256: entry.sha256 }); expected.push(entry.path);
  }
  // Unlisted files, including injected scripts, cannot be served or escape the package hash.
  const actual = [];
  async function walk(directory, prefix = '') {
    for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
      const relative = prefix + entry.name;
      if (entry.isSymbolicLink()) throw new Error('source symlink rejected');
      if (entry.isDirectory()) await walk(path.join(directory, entry.name), relative + '/');
      else if (entry.isFile()) actual.push(relative);
      else throw new Error('unsupported source filesystem entry');
    }
  }
  await walk(paths.source);
  if (canonical(actual.sort()) !== canonical(expected.sort()) || PAGES.some(page => !files.has(page))) throw new Error('source package is incomplete or contains unlisted files');
  return { manifest, files, manifestSha256: sha(raw) };
}
export function packagePath(urlPath) {
  let decoded;
  try { decoded = decodeURIComponent(urlPath); } catch { return null; }
  if (decoded.includes('\\') || decoded.split('/').some(piece => piece === '..')) return null;
  decoded = decoded.replace(/^\/prototypes\//, '/').replace(/^\//, '');
  if (decoded.endsWith('/')) decoded += 'index.html';
  return decoded;
}
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
export async function staticServer(files) {
  const server = http.createServer((req, res) => {
    if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405); res.end(); return; }
    let target;
    try { target = packagePath(new URL(req.url, 'http://localhost').pathname); }
    catch { res.writeHead(400); res.end(); return; }
    const file = files.get(target);
    if (!file) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(target)] ?? 'application/octet-stream', 'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' });
    res.end(req.method === 'HEAD' ? undefined : file.bytes);
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return { server, origin: 'http://127.0.0.1:' + server.address().port };
}
export function checkDom(dom) {
  const errors = [];
  if (dom.h1.length !== 1 || !dom.h1[0].trim()) errors.push('exactly one non-empty H1 required');
  if (!dom.noindex) errors.push('noindex is missing');
  if (dom.scrollWidth > dom.viewportWidth + 1) errors.push('horizontal overflow');
  if (dom.missingImages.length) errors.push('missing images: ' + dom.missingImages.join(', '));
  if (!dom.reducedMotion) errors.push('reduced-motion preference was not applied');
  if (dom.motion.length) errors.push('active motion exceeds reduced-motion limit');
  return errors;
}
export async function bookingChoices(page) {
  const controls = page.locator('[data-booking-choice]');
  if (await controls.count() === 0) return { present: false, status: 'not_present', errors: [], branches: [] };
  const errors = [], branches = [], initialUrl = page.url();
  const initial = new URL(initialUrl);
  const panel = page.locator('#booking-placeholder');
  if (await controls.count() !== 2) errors.push('booking widget must expose exactly session and conversation choices');
  if (await panel.count() !== 1 || !await panel.isVisible()) errors.push('booking choice panel missing or hidden');
  else if (await panel.getAttribute('aria-live') !== 'polite' || await panel.getAttribute('tabindex') !== '-1')
    errors.push('booking choice panel must be a focusable polite live region');
  const message = page.locator('#booking-placeholder [data-choice-message]');
  if (await message.count() !== 1 || !await message.isVisible()) errors.push('booking choice message missing or hidden');
  if (errors.length) return { present: true, status: 'failed', errors, branches };
  const originalMessage = (await message.textContent() ?? '').trim();
  const network = [], popupClosures = [];
  let tracking = false, touched = false, restoredOrdinaryState = false;
  const onRequest = request => {
    if (!tracking) return;
    let parsed;
    try { parsed = new URL(request.url()); } catch { network.push('invalid request URL'); return; }
    if (!['GET', 'HEAD'].includes(request.method()) || ![initial.origin, 'null'].includes(parsed.origin)
        || parsed.protocol !== 'data:' && parsed.origin !== initial.origin)
      network.push(request.method() + ' ' + parsed.origin + parsed.pathname);
  };
  const onPopup = popup => {
    if (!tracking) return;
    errors.push('booking choice opened an unexpected window');
    popupClosures.push(popup.close().catch(() => {}));
  };
  page.on('request', onRequest); page.on('popup', onPopup);
  try {
    let previousMessage = originalMessage;
    for (const choice of ['session', 'conversation']) {
      const branchErrors = [];
      const link = page.locator('a[data-booking-choice="' + choice + '"]');
      if (await link.count() !== 1 || !await link.isVisible() || await link.getAttribute('href') !== '#booking-placeholder') {
        branches.push({ choice, status: 'failed', errors: ['local booking choice anchor missing or unsafe'] });
        errors.push(choice + ': local booking choice anchor missing or unsafe');
        continue;
      }
      tracking = true; touched = true;
      await link.click();
      try {
        await page.waitForFunction(before => {
          const panel = document.getElementById('booking-placeholder');
          const message = panel?.querySelector('[data-choice-message]');
          return document.activeElement === panel && message?.textContent.trim() && message.textContent.trim() !== before;
        }, previousMessage, { timeout: 2500 });
      } catch { branchErrors.push('choice did not update its message and focus the panel'); }
      const text = (await message.textContent() ?? '').trim();
      const focused = await page.evaluate(() => document.activeElement?.id === 'booking-placeholder');
      const current = new URL(page.url());
      const samePage = current.origin === initial.origin && current.pathname === initial.pathname && current.search === initial.search;
      const fragmentMatched = current.hash === '#booking-placeholder';
      if (!text || text === originalMessage || text === previousMessage) branchErrors.push('choice message is empty, unchanged or not distinct');
      if (!await panel.isVisible() || !await message.isVisible()) branchErrors.push('choice result is not visible');
      if (!focused) branchErrors.push('choice result did not receive focus');
      if (!samePage || !fragmentMatched) branchErrors.push('choice did not stay on the matching local panel fragment');
      branches.push({ choice, status: branchErrors.length ? 'failed' : 'passed', message: text,
        focused, fragmentMatched, stayedOnPage: samePage, errors: branchErrors });
      errors.push(...branchErrors.map(error => choice + ': ' + error));
      previousMessage = text;
      tracking = false;
    }
  } finally {
    tracking = false;
    page.off('request', onRequest); page.off('popup', onPopup);
    await Promise.all(popupClosures);
    // Reload the ordinary prototype state before the normal desktop/mobile screenshot.
    if (touched) {
      const restored = await page.goto(initialUrl, { waitUntil: 'networkidle', timeout: 25000 });
      restoredOrdinaryState = Boolean(restored && restored.status() === 200);
      if (!restoredOrdinaryState) errors.push('ordinary booking UI could not be restored');
    }
  }
  errors.push(...network.map(request => 'booking choice attempted a backend/network request: ' + request));
  return { present: true, status: errors.length ? 'failed' : 'passed', errors, branches,
    prototypeOnly: true, backendRequests: network, restoredOrdinaryState };
}

export async function inspectPage(page, { origin, pagePath, viewport, output, files }) {
  const url = origin + '/prototypes/' + pagePath;
  const resourceErrors = [];
  page.on('response', resource => {
    if (resource.url().startsWith(origin + '/') && resource.status() >= 400) resourceErrors.push(resource.status() + ': ' + resource.url());
  });
  const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 25000 });
  if (!response || response.status() !== 200) throw new Error('local package page did not return HTTP 200');
  const dom = await page.evaluate(() => {
    const duration = value => value.split(',').some(piece => parseFloat(piece) * (piece.trim().endsWith('ms') ? 0.001 : 1) > 0.1);
    const motion = [...document.querySelectorAll('*')].filter(node => {
      return [undefined, '::before', '::after'].some(pseudo => {
        const style = getComputedStyle(node, pseudo);
        return duration(style.animationDuration) || duration(style.transitionDuration);
      });
    }).map(node => node.tagName.toLowerCase() + (node.id ? '#' + node.id : '')).slice(0, 20);
    return { h1: [...document.querySelectorAll('h1')].map(node => node.textContent),
      noindex: [...document.querySelectorAll('meta[name="robots" i]')].some(node => /\bnoindex\b/i.test(node.content)),
      scrollWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth), viewportWidth: innerWidth,
      missingImages: [...document.images].filter(image => !image.complete || image.naturalWidth === 0).map(image => image.getAttribute('src')),
      reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches, motion,
      ids: [...document.querySelectorAll('[id]')].map(node => node.id),
      links: [...document.querySelectorAll('a[href]')].map(node => node.href) };
  });
  const errors = [...checkDom(dom), ...resourceErrors.map(error => 'missing package resource: ' + error)];
  let menu = { required: viewport.width === 390, opened: false, escapeClosed: false };
  if (menu.required) {
    const toggle = page.locator('button[aria-controls="primary-nav"][aria-expanded]');
    if (await toggle.count() !== 1 || !await toggle.isVisible()) errors.push('mobile menu toggle missing or hidden');
    else {
      await toggle.click();
      menu.opened = await toggle.getAttribute('aria-expanded') === 'true' && await page.locator('#primary-nav').isVisible();
      await page.keyboard.press('Escape');
      menu.escapeClosed = await toggle.getAttribute('aria-expanded') === 'false' && !await page.locator('#primary-nav').isVisible();
      if (!menu.opened || !menu.escapeClosed) errors.push('mobile menu open/Escape-close failed');
    }
  }
  const booking = await bookingChoices(page);
  errors.push(...booking.errors);
  // Inspect links without navigating away, booking, clicking external links or submitting forms.
  const links = dom.links.map(href => {
    try {
      const parsed = new URL(href);
      if (![origin, 'https://lhmstaging.net'].includes(parsed.origin)) return null;
      const target = packagePath(parsed.pathname);
      if (!target || !files.has(target)) return { href, error: 'missing local link target' };
      return { href, target, fragment: parsed.hash ? decodeURIComponent(parsed.hash.slice(1)) : null };
    } catch { return { href, error: 'invalid local URL or fragment' }; }
  }).filter(Boolean);
  for (const link of links) if (link.error) errors.push(link.error + ': ' + link.href);
  const screenshot = path.join(output, pagePath.replaceAll('/', '--').replace(/\.html$/, '') + '-' + viewport.width + '.png');
  await page.screenshot({ path: screenshot, fullPage: true, animations: 'disabled' });
  const screenshotBytes = await fs.readFile(screenshot);
  return { page: pagePath, viewport, url, status: errors.length ? 'failed' : 'passed', errors, menu, booking,
    checks: { h1: dom.h1, noindex: dom.noindex, horizontalOverflow: dom.scrollWidth > dom.viewportWidth + 1,
      missingImages: dom.missingImages, reducedMotion: dom.reducedMotion, motion: dom.motion },
    screenshot: { path: screenshot, sha256: sha(screenshotBytes), size_bytes: screenshotBytes.length }, ids: dom.ids, links };
}
export function fragments(results) {
  const byPage = new Map(results.map(result => [result.page, new Set(result.ids)]));
  for (const result of results) for (const link of result.links) {
    if (link.fragment && (!byPage.has(link.target) || !byPage.get(link.target).has(link.fragment))) {
      result.errors.push('missing fragment: ' + link.href); result.status = 'failed';
    }
  }
}
export async function run(source, output, { playwright, root = QA_ROOT, requireRoot = true } = {}) {
  const paths = runPaths(source, output, root);
  const sourcePackage = await loadManifest(paths, { requireRoot });
  const outStat = await fs.lstat(paths.output);
  if (!outStat.isDirectory() || outStat.isSymbolicLink() || outStat.uid !== process.getuid() || outStat.mode & 0o077
      || (await fs.readdir(paths.output)).length) throw new Error('output must be an empty private directory owned by this QA worker');
  if (!playwright) playwright = createRequire(import.meta.url)('/opt/lhm-prototype-feedback-qa/node_modules/playwright');
  const { server, origin } = await staticServer(sourcePackage.files);
  let browser;
  const results = [], blocked = new Set();
  try {
    browser = await playwright.chromium.launch({ headless: true, chromiumSandbox: true,
      args: ['--disable-background-networking', '--disable-component-update', '--disable-default-apps', '--disable-sync', '--no-first-run'] });
    for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
      const context = await browser.newContext({ viewport, reducedMotion: 'reduce', serviceWorkers: 'block' });
      await context.route('**/*', route => {
        const url = route.request().url();
        if (url.startsWith(origin + '/') || url.startsWith('data:')) return route.continue();
        blocked.add(url.split('?')[0]); return route.abort('blockedbyclient');
      });
      if (context.routeWebSocket) await context.routeWebSocket('**/*', socket => socket.close());
      try {
        for (const pagePath of PAGES) {
          const page = await context.newPage();
          try { results.push(await inspectPage(page, { origin, pagePath, viewport, output: paths.output, files: sourcePackage.files })); }
          catch (error) { results.push({ page: pagePath, viewport, status: 'failed', errors: [String(error.message)], ids: [], links: [] }); }
          finally { await page.close(); }
        }
      } finally { await context.close(); }
    }
    fragments(results);
    // Re-read the source after the browser pass to reject package mutation during QA.
    const after = await loadManifest(paths, { requireRoot });
    if (after.manifestSha256 !== sourcePackage.manifestSha256) throw new Error('source manifest changed during QA');
    const receipt = { schema_version: 1, status: results.every(result => result.status === 'passed') ? 'mechanical_passed' : 'mechanical_failed',
      source_package_sha256: sourcePackage.manifest.package_sha256, source_manifest_sha256: sourcePackage.manifestSha256,
      pages: results.map(({ ids, links, ...result }) => result), blocked_external_requests: [...blocked].sort(),
      semantic_qa_approved: false, scope: 'isolated headless-browser mechanics and screenshots only; independent visual review still required' };
    await fs.writeFile(path.join(paths.output, 'mechanical-qa.json'), JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
    return receipt;
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 4) { console.error('Usage: visual_qa.mjs <registered-source> <registered-output>'); process.exitCode = 2; }
  else try {
    const receipt = await run(process.argv[2], process.argv[3]);
    console.log(JSON.stringify({ status: receipt.status, semantic_qa_approved: false,
      receipt: path.join(path.resolve(process.argv[3]), 'mechanical-qa.json') }));
    if (receipt.status !== 'mechanical_passed') process.exitCode = 1;
  } catch (error) { console.error(JSON.stringify({ status: 'mechanical_failed', reason: error.message })); process.exitCode = 1; }
}
