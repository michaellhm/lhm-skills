#!/usr/bin/env node

import { access, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const [outputArg] = process.argv.slice(2);
if (!outputArg) {
  console.error('Usage: node render-carousel.mjs <output-directory>');
  process.exit(2);
}

const outputDir = path.resolve(outputArg);
const htmlPath = path.join(outputDir, 'carousel.html');
const manifestPath = path.join(outputDir, 'manifest.json');
const require = createRequire(import.meta.url);

async function exists(target) {
  try {
    await access(target);
    return true;
  } catch {
    return false;
  }
}

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_MODULE,
    'playwright',
    path.join(os.homedir(), '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node', 'node_modules', 'playwright'),
    path.join(os.homedir(), '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'node_modules', 'playwright')
  ].filter(Boolean);

  for (const candidate of candidates) {
    try {
      return require(candidate);
    } catch {
      // Try the next known installation.
    }
  }
  return null;
}

async function resolveBrowserExecutable() {
  const candidates = [
    process.env.CHROME_EXECUTABLE,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser'
  ].filter(Boolean);

  for (const candidate of candidates) {
    if (await exists(candidate)) return candidate;
  }
  return null;
}

if (!(await exists(htmlPath)) || !(await exists(manifestPath))) {
  console.error('Render requires carousel.html and manifest.json in the output directory.');
  process.exit(2);
}

const playwright = loadPlaywright();
if (!playwright?.chromium) {
  console.error('Playwright is unavailable. The HTML package remains valid, but PNG rendering needs review.');
  process.exit(3);
}

const executablePath = await resolveBrowserExecutable();
const launchOptions = { headless: true, ...(executablePath ? { executablePath } : {}) };
const browser = await playwright.chromium.launch(launchOptions);

try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href);
  await page.evaluate(() => document.fonts.ready);

  const overflows = await page.locator('.slide').evaluateAll((slides) => slides.map((slide, index) => {
    const slideBox = slide.getBoundingClientRect();
    const content = [...slide.querySelectorAll('.topline, .eyebrow, h1, h2, .body, .labels, .checklist, .callout, .footer')];
    const horizontal = content.some((element) => {
      const box = element.getBoundingClientRect();
      return box.left < slideBox.left - 1 || box.right > slideBox.right + 1;
    });
    const vertical = content.some((element) => {
      const box = element.getBoundingClientRect();
      return box.top < slideBox.top - 1 || box.bottom > slideBox.bottom + 1;
    });
    return { slide: index + 1, horizontal, vertical };
  }).filter((item) => item.horizontal || item.vertical));
  if (overflows.length) throw new Error(`Slide overflow detected: ${JSON.stringify(overflows)}`);

  const slides = page.locator('.slide');
  const count = await slides.count();
  const slideFiles = [];
  for (let index = 0; index < count; index += 1) {
    const filename = `slide-${String(index + 1).padStart(2, '0')}.png`;
    await slides.nth(index).screenshot({ path: path.join(outputDir, filename) });
    slideFiles.push(filename);
  }

  await page.setViewportSize({ width: 1080, height: 900 });
  const cards = slideFiles.map((filename) => `<div class="card"><img src="${pathToFileURL(path.join(outputDir, filename)).href}" alt="${filename}"></div>`).join('');
  await page.setContent(`<!doctype html><html><head><style>
    *{box-sizing:border-box}body{margin:0;padding:34px;background:#e7ebf0;font-family:Arial,sans-serif}
    .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:white;padding:8px;box-shadow:0 8px 24px rgba(7,22,37,.12)}
    img{width:100%;display:block}
  </style></head><body><div class="grid">${cards}</div></body></html>`);
  await page.waitForFunction(() => [...document.images].every((image) => image.complete && image.naturalWidth > 0));
  const contactSheetHeight = await page.evaluate(() => Math.ceil(document.documentElement.scrollHeight));
  await page.setViewportSize({ width: 1080, height: contactSheetHeight });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: path.join(outputDir, 'carousel-preview.png') });

  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  manifest.render_state = 'png_verified';
  manifest.files = [...new Set([...(manifest.files ?? []), ...slideFiles, 'carousel-preview.png'])];
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

  console.log(JSON.stringify({
    status: 'rendered',
    output_directory: outputDir,
    slide_count: count,
    preview: path.join(outputDir, 'carousel-preview.png')
  }, null, 2));
} finally {
  await browser.close();
}
