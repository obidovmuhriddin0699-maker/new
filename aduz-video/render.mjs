// Renders episode1.html to MP4 (1080x1920, 30 fps).
// Usage: node render.mjs [out.mp4] [--stills]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : path.join(dir, 'build/video_silent.mp4');
const stills = process.argv.includes('--stills');
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
await page.goto('file://' + path.join(dir, 'episode1.html') + '?render');
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.DURATION);
const grab = t => page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93).split(',')[1]; }, t);

fs.mkdirSync(path.dirname(out), { recursive: true });
if (stills) {
  for (const t of [3, 8.5, 12.8, 15.2, 17.2, 20.5, 25.5, 30]) fs.writeFileSync(path.join(dir, `build/still_${t}.jpg`), Buffer.from(await grab(t), 'base64'));
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
