#!/usr/bin/env node

import { access, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const [outputArg] = process.argv.slice(2);
if (!outputArg) {
  console.error('Usage: node render-story.mjs <output-directory>');
  process.exit(2);
}

const outputDir = path.resolve(outputArg);
const require = createRequire(import.meta.url);
const exists = async (target) => { try { await access(target); return true; } catch { return false; } };
const candidates = [process.env.PLAYWRIGHT_MODULE, 'playwright', path.join(os.homedir(), '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node', 'node_modules', 'playwright'), path.join(os.homedir(), '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node_modules', 'playwright')].filter(Boolean);
let playwright = null;
for (const candidate of candidates) { try { playwright = require(candidate); break; } catch {} }
if (!playwright?.chromium) { console.error('Playwright is unavailable.'); process.exit(3); }

const executableCandidates = [process.env.CHROME_EXECUTABLE, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/usr/bin/google-chrome', '/usr/bin/chromium'].filter(Boolean);
let executablePath = null;
for (const candidate of executableCandidates) { if (await exists(candidate)) { executablePath = candidate; break; } }

const htmlPath = path.join(outputDir, 'story.html');
const manifestPath = path.join(outputDir, 'story-manifest.json');
if (!(await exists(htmlPath)) || !(await exists(manifestPath))) { console.error('Render requires story.html and story-manifest.json.'); process.exit(2); }

const browser = await playwright.chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 2100 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href);
  await page.evaluate(() => document.fonts.ready);
  const frames = page.locator('.story-frame');
  const count = await frames.count();
  const frameFiles = [];
  for (let index = 0; index < count; index += 1) {
    const filename = `story-${String(index + 1).padStart(2, '0')}.png`;
    await frames.nth(index).screenshot({ path: path.join(outputDir, filename) });
    frameFiles.push(filename);
  }
  const cards = frameFiles.map((filename) => `<div><img src="${pathToFileURL(path.join(outputDir, filename)).href}"></div>`).join('');
  await page.setViewportSize({ width: 980, height: 900 });
  await page.setContent(`<!doctype html><html><head><style>*{box-sizing:border-box}body{margin:0;padding:28px;background:#e7ebf0}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}div{background:white;padding:6px;box-shadow:0 6px 18px #07162522}img{width:100%;display:block}</style></head><body><section class="grid">${cards}</section></body></html>`);
  await page.waitForFunction(() => [...document.images].every((image) => image.complete && image.naturalWidth));
  const height = await page.evaluate(() => Math.ceil(document.documentElement.scrollHeight));
  await page.setViewportSize({ width: 980, height });
  await page.screenshot({ path: path.join(outputDir, 'story-preview.png') });
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  manifest.render_state = 'png_verified';
  manifest.export_files = frameFiles;
  manifest.files = [...new Set([...(manifest.files ?? []), ...frameFiles, 'story-preview.png'])];
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ status: 'rendered', output_directory: outputDir, frame_count: count }, null, 2));
} finally {
  await browser.close();
}
