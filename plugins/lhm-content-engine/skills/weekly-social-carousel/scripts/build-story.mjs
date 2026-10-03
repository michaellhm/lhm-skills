#!/usr/bin/env node

import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';

const [inputArg, outputArg] = process.argv.slice(2);
if (!inputArg || !outputArg) {
  console.error('Usage: node build-story.mjs <story-input.json> <output-directory>');
  process.exit(2);
}

const inputPath = path.resolve(inputArg);
const outputDir = path.resolve(outputArg);
const data = JSON.parse(await readFile(inputPath, 'utf8'));

function fail(message) {
  console.error(`Invalid Story input: ${message}`);
  process.exit(2);
}

function text(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

if (typeof data.id !== 'string' || !data.id.trim()) fail('id is required');
if (typeof data.title !== 'string' || !data.title.trim()) fail('title is required');
if (!Array.isArray(data.frames) || data.frames.length < 2 || data.frames.length > 6) fail('frames must contain 2 to 6 entries');
if (data.frames.some((frame) => typeof frame !== 'string' || !frame.trim())) fail('every frame must be a non-empty string');
if (data.frames.some((frame) => /[—–]/.test(frame))) fail('frames cannot contain em dashes or en dashes');

try {
  await stat(path.join(outputDir, 'story.html'));
  fail('output directory already contains story.html; use a fresh package directory');
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}

await mkdir(outputDir, { recursive: true });
const frameCount = data.frames.length;
const frames = data.frames.map((frame, index) => {
  return `<article class="story-frame" data-frame="${index + 1}">
    <div class="topline"><span>LOCAL HEALTH MARKETING</span><span>${String(index + 1).padStart(2, '0')} / ${String(frameCount).padStart(2, '0')}</span></div>
    <div class="category">${text(data.category || 'Practice question')}</div>
    <h1>${text(frame)}</h1>
    <div class="footer"><span class="mark">+</span><span>@localhealthmarketing</span></div>
  </article>`;
}).join('\n');

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${text(data.title)}</title><style>
:root{--navy:#071625;--navy2:#122b49;--blue:#7fb3ff;--white:#f8fafc;--muted:#c6d5e8}*{box-sizing:border-box}html,body{margin:0;background:#d9dee6;font-family:"Avenir Next",Avenir,"Helvetica Neue",Arial,sans-serif}body{display:grid;gap:48px;justify-content:center;padding:48px}.story-frame{position:relative;width:1080px;height:1920px;overflow:hidden;padding:120px 94px 112px;color:var(--white);background:radial-gradient(circle at 90% 8%,rgba(255,255,255,.26),transparent 29%),linear-gradient(155deg,var(--blue) 0%,#4387d9 42%,var(--navy2) 76%,var(--navy) 100%);display:flex;flex-direction:column;isolation:isolate}.story-frame:before{content:"";position:absolute;z-index:-1;right:-310px;bottom:160px;width:760px;height:760px;border:3px solid rgba(255,255,255,.16);border-radius:50%;box-shadow:0 0 0 90px rgba(255,255,255,.045),0 0 0 185px rgba(255,255,255,.025)}.topline{display:flex;justify-content:space-between;font-size:19px;font-weight:850;letter-spacing:.12em}.category{align-self:flex-start;margin-top:230px;padding:14px 22px 12px;border-radius:999px;background:var(--white);color:var(--navy);font-size:20px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}h1{max-width:890px;margin:42px 0 0;font-size:86px;line-height:1.01;letter-spacing:-.048em;text-wrap:balance}.footer{margin-top:auto;padding-top:34px;border-top:1px solid rgba(255,255,255,.22);display:flex;align-items:center;gap:18px;font-size:20px;font-weight:800;letter-spacing:.08em}.mark{display:grid;width:46px;height:46px;place-items:center;border:2px solid var(--white);border-radius:50% 50% 50% 12px;color:var(--blue);background:var(--white);font-size:32px}@media print{body{padding:0;gap:0}.story-frame{page-break-after:always}}
</style></head><body>${frames}</body></html>`;

const manifest = {
  schema_version: '1.0',
  id: data.id,
  title: data.title,
  content_format: 'story',
  accent: 'soft-blue',
  frame_count: frameCount,
  generated_at: new Date().toISOString(),
  render_state: 'html_built',
  files: ['story.html', 'story-manifest.json']
};

await writeFile(path.join(outputDir, 'story.html'), html, 'utf8');
await writeFile(path.join(outputDir, 'story-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ status: 'built', output_directory: outputDir, manifest }, null, 2));
