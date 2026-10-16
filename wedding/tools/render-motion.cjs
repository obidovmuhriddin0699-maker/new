/* ==========================================================================
   Render the motion-design invitation (motion/index.html) to
   dist/taklifnoma-motion.mp4 — 1080×1920, 30 fps, H.264 + AAC with
   "Asadov Silencio.m4a".

     node tools/render-motion.cjs              # full film
     node tools/render-motion.cjs --preview    # a few stills into dist/.motion-preview/

   Each frame is placed at an exact time with window.__motion.step(t), so the
   result is smooth no matter how long a frame takes to capture.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { start, ROOT } = require("./static-server.cjs");

const FPS = 30;
const DURATION = 48;
const OUT = path.join(ROOT, "dist", "taklifnoma-motion.mp4");
const FRAMES = path.join(ROOT, "dist", ".motion-frames");
const MUSIC = path.join(ROOT, "assets", "audio", "Asadov Silencio.m4a");
const PREVIEW = process.argv.includes("--preview");

function loadPlaywright() {
  for (const c of ["playwright", "/opt/node-tools/node_modules/playwright"]) {
    try { return require(c); } catch (e) { /* next */ }
  }
  throw new Error("Playwright not found. Run `npm install` in the wedding/ folder.");
}

(async () => {
  const { chromium } = loadPlaywright();
  const server = await start();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 2.5 });
  page.on("pageerror", (e) => console.error("page error:", e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/motion/index.html?render`, { waitUntil: "load" });
  await page.evaluate(() => window.__motion.ready);

  const shot = async (t, file) => {
    await page.evaluate((t) => window.__motion.step(t), t);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await page.screenshot({ path: file, type: "jpeg", quality: 90 });
  };

  if (PREVIEW) {
    const dir = path.join(ROOT, "dist", ".motion-preview");
    fs.mkdirSync(dir, { recursive: true });
    const times = (process.env.TIMES || "1.5,3.5,5.9,8.5,10.5,14.8,16.5,19.5,23,26,29,32,34,37.5,39.5,43,46").split(",").map(Number);
    for (const t of times) await shot(t, path.join(dir, `t${t.toFixed(1).padStart(5, "0")}.jpg`));
    console.log(`Wrote ${times.length} preview stills to ${path.relative(ROOT, dir)}`);
  } else {
    fs.rmSync(FRAMES, { recursive: true, force: true });
    fs.mkdirSync(FRAMES, { recursive: true });
    const total = DURATION * FPS;
    for (let f = 0; f < total; f++) {
      await shot(f / FPS, path.join(FRAMES, `f${String(f).padStart(5, "0")}.jpg`));
      if ((f + 1) % 150 === 0) console.log(`  ${f + 1}/${total} frames`);
    }
    console.log("Encoding…");
    execFileSync("ffmpeg", [
      "-y", "-loglevel", "error",
      "-framerate", String(FPS), "-i", path.join(FRAMES, "f%05d.jpg"),
      "-i", MUSIC,
      "-filter_complex",
      `[0:v]format=yuv420p[v];[1:a]afade=t=in:st=0:d=2,afade=t=out:st=${DURATION - 3}:d=3,atrim=0:${DURATION}[a]`,
      "-map", "[v]", "-map", "[a]",
      "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-profile:v", "high", "-r", String(FPS),
      "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", String(DURATION),
      OUT
    ]);
    fs.rmSync(FRAMES, { recursive: true, force: true });
    console.log(`Wrote ${path.relative(ROOT, OUT)} (${(fs.statSync(OUT).size / 1048576).toFixed(1)} MB)`);
  }
  await browser.close();
  server.close();
})().catch((e) => { console.error(e); process.exit(1); });
