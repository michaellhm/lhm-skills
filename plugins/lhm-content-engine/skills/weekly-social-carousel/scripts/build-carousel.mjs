#!/usr/bin/env node

import { copyFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const [inputArg, outputArg] = process.argv.slice(2);
if (!inputArg || !outputArg) {
  console.error('Usage: node build-carousel.mjs <input.json> <output-directory>');
  process.exit(2);
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const inputPath = path.resolve(inputArg);
const outputDir = path.resolve(outputArg);
const cssPath = path.resolve(scriptDir, '..', 'assets', 'carousel.css');
const publicFiles = ['carousel.html', 'caption.md', 'manifest.json'];

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const words = (value = '') => String(value).trim().split(/\s+/).filter(Boolean).length;
const headlineText = (slide) => slide.headline ?? (slide.headline_segments ?? []).map((part) => part.text).join('');

function fail(message) {
  console.error(`Invalid carousel input: ${message}`);
  process.exit(2);
}

function requireString(value, field) {
  if (typeof value !== 'string' || !value.trim()) fail(`${field} must be a non-empty string`);
}

function checkPublicText(value, field) {
  if (typeof value === 'string' && /[—–]/.test(value)) fail(`${field} contains an em dash or en dash`);
}

function validate(data) {
  const lanes = new Set(['client-question', 'quick-win-sop', 'rotating-opportunity', 'practice-question', 'practical-shortcut', 'search-ads-update', 'ai-experiment']);
  const coverStyles = new Set(['typography', 'image']);
  const slideTypes = new Set(['cover', 'statement', 'labels', 'checklist', 'callout']);

  if (data.schema_version !== '1.0') fail('schema_version must be 1.0');
  requireString(data.slug, 'slug');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(data.slug)) fail('slug must be lowercase kebab-case');
  requireString(data.title, 'title');
  if (!lanes.has(data.lane)) fail('lane is not supported');
  if (!coverStyles.has(data.cover_style)) fail('cover_style must be typography or image');
  if (!Array.isArray(data.slides) || data.slides.length < 5 || data.slides.length > 7) fail('slides must contain 5 to 7 entries');
  if (data.slides[0]?.type !== 'cover') fail('the first slide must use type cover');
  if (data.slides.slice(1).some((slide) => slide.type === 'cover')) fail('only the first slide can use type cover');

  data.slides.forEach((slide, index) => {
    const prefix = `slides[${index}]`;
    if (!slideTypes.has(slide.type)) fail(`${prefix}.type is not supported`);
    requireString(slide.kicker, `${prefix}.kicker`);
    const headline = headlineText(slide);
    requireString(headline, `${prefix}.headline`);
    const limit = index === 0 ? 22 : 16;
    if (words(headline) > limit) fail(`${prefix} headline exceeds ${limit} words`);
    if (slide.body && words(slide.body) > 40) fail(`${prefix}.body exceeds 40 words`);
    if (slide.callout && words(slide.callout) > 22) fail(`${prefix}.callout exceeds 22 words`);
    if (slide.type === 'labels' && (!Array.isArray(slide.items) || slide.items.length < 3 || slide.items.length > 4)) fail(`${prefix}.items must contain 3 or 4 labels`);
    if (slide.type === 'checklist' && (!Array.isArray(slide.items) || slide.items.length < 4 || slide.items.length > 6)) fail(`${prefix}.items must contain 4 to 6 checklist items`);

    checkPublicText(slide.kicker, `${prefix}.kicker`);
    checkPublicText(headline, `${prefix}.headline`);
    checkPublicText(slide.body, `${prefix}.body`);
    checkPublicText(slide.callout, `${prefix}.callout`);
    (slide.items ?? []).forEach((item, itemIndex) => checkPublicText(item, `${prefix}.items[${itemIndex}]`));
  });

  requireString(data.caption, 'caption');
  checkPublicText(data.caption, 'caption');
  if (data.first_comment !== undefined && data.first_comment !== null && data.first_comment !== '') {
    requireString(data.first_comment, 'first_comment');
    checkPublicText(data.first_comment, 'first_comment');
  }
  checkPublicText(data.public_source_note, 'public_source_note');
  if (data.cover_style === 'image') requireString(data.cover_image, 'cover_image');
}

function headlineClass(text) {
  const count = words(text);
  if (count > 14) return 'headline--long';
  if (count > 10) return 'headline--medium';
  return '';
}

function renderHeadline(slide) {
  if (!Array.isArray(slide.headline_segments)) return escapeHtml(slide.headline);
  return slide.headline_segments.map((segment) => {
    const tone = segment.tone === 'accent' ? 'accent' : segment.tone === 'blue' ? 'blue' : '';
    const text = escapeHtml(segment.text);
    return tone ? `<span class="${tone}">${text}</span>` : text;
  }).join('');
}

function renderBody(slide) {
  if (slide.type === 'labels') {
    return `<div class="labels">${slide.items.map((item) => `<div class="label">${escapeHtml(item)}</div>`).join('')}</div>${slide.body ? `<p class="body">${escapeHtml(slide.body)}</p>` : ''}`;
  }
  if (slide.type === 'checklist') {
    return `<div class="checklist">${slide.items.map((item) => `<div class="check-item"><span class="dot"></span>${escapeHtml(item)}</div>`).join('')}</div>`;
  }
  return `${slide.body ? `<p class="body">${escapeHtml(slide.body)}</p>` : ''}${slide.callout ? `<div class="callout">${escapeHtml(slide.callout)}</div>` : ''}`;
}

function renderSlide(slide, index, count, brand, coverImageName) {
  const headline = headlineText(slide);
  const isCover = index === 0;
  const coverClass = isCover && coverImageName ? ' cover--image' : '';
  const coverStyle = coverImageName ? ` style="--cover-image: url('${encodeURI(coverImageName)}')"` : '';
  const tag = isCover ? 'h1' : 'h2';
  const endLabel = isCover ? 'Swipe →' : (index === count - 1 ? 'Save this post' : String(index + 1).padStart(2, '0'));

  return `<article class="slide${coverClass}" data-slide="${index + 1}"${coverStyle}>
    <div class="topline"><div class="series">${escapeHtml(slide.kicker)}</div><div class="number">${String(index + 1).padStart(2, '0')} / ${String(count).padStart(2, '0')}</div></div>
    ${slide.eyebrow ? `<div class="eyebrow">${escapeHtml(slide.eyebrow)}</div>` : ''}
    <${tag} class="${headlineClass(headline)}">${renderHeadline(slide)}</${tag}>
    ${renderBody(slide)}
    <div class="footer"><div class="brand"><div class="brand-mark"><span>+</span></div>${escapeHtml(brand.name)}</div><div>${escapeHtml(endLabel)}</div></div>
  </article>`;
}

async function pathExists(target) {
  try {
    await stat(target);
    return true;
  } catch {
    return false;
  }
}

const data = JSON.parse(await readFile(inputPath, 'utf8'));
validate(data);

await mkdir(outputDir, { recursive: true });
for (const filename of publicFiles) {
  if (await pathExists(path.join(outputDir, filename))) {
    fail(`output directory already contains ${filename}; use a fresh package directory`);
  }
}

let coverImageName = null;
if (data.cover_style === 'image') {
  const source = path.resolve(data.cover_image);
  if (!(await pathExists(source))) fail('cover_image does not exist');
  const extension = path.extname(source).toLowerCase();
  if (!['.png', '.jpg', '.jpeg', '.webp'].includes(extension)) fail('cover_image must be PNG, JPEG, or WebP');
  coverImageName = `cover-image${extension}`;
  await copyFile(source, path.join(outputDir, coverImageName));
}

const css = await readFile(cssPath, 'utf8');
const brand = {
  name: data.brand?.name || 'Local Health Marketing',
  website: data.brand?.website || 'localhealthmarketing.com'
};
const slides = data.slides.map((slide, index) => renderSlide(slide, index, data.slides.length, brand, coverImageName)).join('\n');
const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="generator" content="LHM weekly-social-carousel">
  <title>${escapeHtml(data.title)} | ${escapeHtml(brand.name)}</title>
  <style>${css}</style>
</head>
<body class="lane-${escapeHtml(data.lane)}">
${slides}
</body>
</html>
`;

const caption = `${data.caption.trim()}${data.public_source_note ? `\n\n## Source note\n\n${data.public_source_note.trim()}` : ''}\n`;
const receipt = {
  schema_version: '1.0',
  slug: data.slug,
  private_sources: Array.isArray(data.private_sources) ? data.private_sources : [],
  warning: 'Private source receipt. Exclude from public deployment and social uploads.'
};
const manifest = {
  schema_version: '1.0',
  slug: data.slug,
  title: data.title,
  lane: data.lane,
  content_format: 'feed-post',
  accent: ['practice-question', 'client-question'].includes(data.lane)
    ? 'soft-blue'
    : ['rotating-opportunity', 'search-ads-update', 'ai-experiment'].includes(data.lane)
      ? 'seafoam'
      : 'orange',
  cover_style: data.cover_style,
  slide_count: data.slides.length,
  generated_at: new Date().toISOString(),
  render_state: 'html_built',
  files: ['carousel.html', 'caption.md', ...(data.first_comment?.trim() ? ['first-comment.md'] : []), 'manifest.json', 'source-receipt.private.json', ...(coverImageName ? [coverImageName] : [])]
};

await writeFile(path.join(outputDir, 'carousel.html'), html, 'utf8');
await writeFile(path.join(outputDir, 'caption.md'), caption, 'utf8');
if (data.first_comment?.trim()) await writeFile(path.join(outputDir, 'first-comment.md'), `${data.first_comment.trim()}\n`, 'utf8');
await writeFile(path.join(outputDir, 'source-receipt.private.json'), `${JSON.stringify(receipt, null, 2)}\n`, 'utf8');
await writeFile(path.join(outputDir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

console.log(JSON.stringify({ status: 'built', output_directory: outputDir, manifest }, null, 2));
