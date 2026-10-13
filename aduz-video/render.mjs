// Renders an episode page (episodeN.html) to MP4 (1080x1920, 30 fps).
// Usage: node render.mjs <episodeN.html> [out.mp4] [--stills[=t1,t2,…]]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const dir = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const html = args[0] || 'episode1.html';
const name = path.basename(html, '.html');
const out = args[1] || path.join(dir, `build/${name}_silent.mp4`);
// --stills or --stills=3,8.5,… writes JPEG stills to build/<episode>/ instead of a video.
const stillsArg = process.argv.find(a => a.startsWith('--stills'));
const stills = stillsArg && (stillsArg.includes('=') ? stillsArg.split('=')[1].split(',').map(Number) : [3, 8.5, 12.8, 15.2, 17.2, 20.5, 25.5, 30]);
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
await page.goto('file://' + path.resolve(dir, html) + '?render');
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.DURATION);
const grab = t => page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93).split(',')[1]; }, t);

fs.mkdirSync(path.dirname(out), { recursive: true });
if (stills) {
  const sdir = path.join(dir, 'build', name);
  fs.mkdirSync(sdir, { recursive: true });
  for (const t of stills) fs.writeFileSync(path.join(sdir, `still_${t}.jpg`), Buffer.from(await grab(t), 'base64'));
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(duration * FPS);
  for (let i = 0; i < total; i++) {
    const buf = Buffer.from(await grab(i / FPS), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await browser.close();
