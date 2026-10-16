/* ==========================================================================
   Render the invitation as a vertical video: dist/taklifnoma-video.mp4
   (1080×1920, 30 fps, H.264 + AAC, with the invitation's music track).

     node tools/render-video.cjs            # needs Playwright + ffmpeg

   The page runs on a virtual clock: every CSS animation/transition and every
   page timer advances exactly 1/30 s per captured frame, so motion is smooth
   no matter how slowly frames are captured. The camera follows a scripted
   walk-through of the real site (tap → cloud pass → each section → finale).

   VIDEO_NOW sets the "current time" the countdown is shown from (venue time),
   because a video is frozen in time. Re-render after confirming the date.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { start, ROOT } = require("./static-server.cjs");

const FPS = 30;
const DT = 1000 / FPS;
const VIEW = { width: 432, height: 768, scale: 2.5 }; // → 1080×1920
const VIDEO_NOW = process.env.VIDEO_NOW || "2026-09-06T10:00";
const OUT = path.join(ROOT, "dist", "taklifnoma-video.mp4");
const FRAMES = path.join(ROOT, "dist", ".frames");
const MUSIC = path.join(ROOT, "assets", "audio", "taklifnoma-musiqa.m4a");

function loadPlaywright() {
  for (const c of ["playwright", "/opt/node-tools/node_modules/playwright"]) {
    try { return require(c); } catch (e) { /* next */ }
  }
  throw new Error("Playwright not found. Run `npm install` in the wedding/ folder.");
}

// Injected before any page script: virtual timers/clock and silent media.
function pageClock() {
  let vt = 0;
  let seq = 1;
  const setRealTimeout = window.setTimeout.bind(window);
  const clearRealTimeout = window.clearTimeout.bind(window);
  const timers = [];
  const base = Date.now();
  window.setTimeout = (fn, ms, ...args) => {
    const t = { id: seq++, at: vt + (Number(ms) || 0), fn: typeof fn === "function" ? fn : () => {}, args };
    timers.push(t);
    return t.id;
  };
  window.clearTimeout = (id) => {
    const i = timers.findIndex((t) => t.id === id);
    if (i >= 0) timers.splice(i, 1);
  };
  Date.now = () => base + vt;
  window.__clock = {
    advance(ms) {
      vt += ms;
      for (;;) {
        timers.sort((a, b) => a.at - b.at || a.id - b.id);
        if (!timers.length || timers[0].at > vt) break;
        const t = timers.shift();
        try { t.fn(...t.args); } catch (e) { console.error(e); }
      }
      // Step every animation and transition by the same amount.
      document.getAnimations().forEach((a) => {
        a.pause();
        a.currentTime = (a.__vt == null ? 0 : a.__vt) + ms;
        a.__vt = a.currentTime;
      });
      // Films: seek each visible one forward by exactly one frame (looping).
      const seeks = [];
      document.querySelectorAll("video[data-video]").forEach((v) => {
        if (!v.src || !v.duration) return;
        const r = v.getBoundingClientRect();
        v.__vt = (v.__vt || 0) + ms / 1000;
        if (r.bottom < 0 || r.top > innerHeight) return;
        seeks.push(new Promise((done) => {
          const t = setRealTimeout(done, 1500);
          v.addEventListener("seeked", () => { clearRealTimeout(t); done(); }, { once: true });
          v.currentTime = v.__vt % v.duration;
        }));
      });
      return Promise.all(seeks);
    },
    reset() {
      document.getAnimations().forEach((a) => { a.pause(); a.currentTime = 0; a.__vt = 0; });
    }
  };
  // The soundtrack is added by ffmpeg; in the page the music player just "plays".
  // Films never play on their own here — the clock seeks them frame by frame.
  const canPlay = HTMLMediaElement.prototype.canPlayType;
  HTMLMediaElement.prototype.canPlayType = function (t) { return /audio\//.test(t) ? "probably" : canPlay.call(this, t); };
  HTMLMediaElement.prototype.play = function () { return Promise.resolve(); };
  HTMLMediaElement.prototype.pause = function () {};
}

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

(async () => {
  const { chromium } = loadPlaywright();
  fs.rmSync(FRAMES, { recursive: true, force: true });
  fs.mkdirSync(FRAMES, { recursive: true });

  const server = await start();
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: VIEW.width, height: VIEW.height },
    deviceScaleFactor: VIEW.scale,
    isMobile: true,
    hasTouch: true
  });
  await context.addInitScript(pageClock);
  const page = await context.newPage();
  page.on("pageerror", (e) => console.error("page error:", e.message));

  await page.goto(`${base}/?now=${encodeURIComponent(VIDEO_NOW)}`, { waitUntil: "load" });
  await page.addStyleTag({
    content: `
      .preview-badge { display: none !important; }
      .tap { position: fixed; z-index: 99; width: 64px; height: 64px; margin: -32px 0 0 -32px; border-radius: 50%;
             background: rgb(255 255 255 / 0.35); border: 2px solid rgb(255 255 255 / 0.9);
             box-shadow: 0 0 0 1px rgb(47 40 34 / 0.15); pointer-events: none;
             animation: tap 0.8s cubic-bezier(.22,1,.36,1) forwards; }
      @keyframes tap { from { transform: scale(0.35); opacity: 1; } to { transform: scale(1.7); opacity: 0; } }`
  });
  // Load every photo and film up front so nothing pops in mid-shot.
  await page.evaluate(async () => {
    document.querySelectorAll("img[loading=lazy]").forEach((i) => { i.loading = "eager"; });
    const films = [...document.querySelectorAll("video[data-video]")];
    films.forEach((v) => {
      if (!v.src) v.src = v.canPlayType('video/mp4; codecs="avc1.64001F"') ? v.getAttribute("data-video") : v.getAttribute("data-video-webm");
      v.preload = "auto";
    });
    await Promise.all(films.map((v) => (v.readyState >= 2 ? 0 : new Promise((r) => { v.addEventListener("loadeddata", r, { once: true }); v.addEventListener("error", r, { once: true }); }))));
    await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
    await document.fonts.ready;
  });
  await page.evaluate(() => window.__clock.reset());

  let frame = 0;
  let videoTime = 0;
  let musicAt = null;

  async function shoot(n = 1) {
    for (let i = 0; i < n; i++) {
      await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
      await page.evaluate((dt) => window.__clock.advance(dt), DT);
      await page.evaluate(() => new Promise((r) => requestAnimationFrame(r)));
      await page.screenshot({ path: path.join(FRAMES, `f${String(frame).padStart(5, "0")}.jpg`), type: "jpeg", quality: 90 });
      frame++;
      videoTime += DT / 1000;
      if (frame % 150 === 0) console.log(`  ${frame} frames (${videoTime.toFixed(1)} s)`);
    }
  }
  const hold = (s) => shoot(Math.round(s * FPS));

  async function scrollTo(target, seconds) {
    const from = await page.evaluate(() => window.scrollY);
    const to = await page.evaluate((y) => Math.max(0, Math.min(y, document.documentElement.scrollHeight - innerHeight)), target);
    const n = Math.max(1, Math.round(seconds * FPS));
    for (let i = 1; i <= n; i++) {
      const y = from + (to - from) * ease(i / n);
      await page.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), y);
      await shoot();
    }
  }
  async function visit(selector, holdSeconds, offset = 64, scrollSeconds = 0) {
    const top = await page.evaluate(({ s, o }) => {
      const el = document.querySelector(s);
      return el.getBoundingClientRect().top + window.scrollY - o;
    }, { s: selector, o: offset });
    const dist = Math.abs(top - (await page.evaluate(() => window.scrollY)));
    await scrollTo(top, scrollSeconds || Math.min(2.6, Math.max(1.3, dist / 650)));
    await hold(holdSeconds);
  }

  console.log("Rendering frames…");
  // Timed to the 27-second track, like the reference video (music from the first frame).
  // 1 · The lace envelope; the wax seal pulses.
  await hold(2.4);
  // 2 · Tap on the seal: flap opens, card rises, zoom into the hero; names are written in.
  const btn = await page.locator("[data-open-invitation]").boundingBox();
  await page.evaluate(({ x, y }) => {
    const t = document.createElement("div");
    t.className = "tap"; t.style.left = x + "px"; t.style.top = y + "px";
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 900);
  }, { x: btn.x + btn.width / 2, y: btn.y + btn.height / 2 });
  await hold(0.3);
  await page.evaluate(() => document.querySelector("[data-open-invitation]").click());
  musicAt = 0;
  await hold(6.0);
  // 3 · "Sizni kutamiz" card.
  await visit(".invitation__card", 2.2, 70, 1.3);
  // 4 · Calendar with the sealed day and the countdown.
  await visit(".calendar-card", 3.1, 64, 2.4);
  // 5 · Venue card with the map buttons.
  await visit(".location-card", 2.7, 64, 2.4);
  // 6 · Finale.
  await visit("#yakun", 2.5, 0, 2.0);

  await browser.close();
  server.close();

  const duration = frame / FPS;
  const music = musicAt.toFixed(2);
  const fadeOut = Math.max(0, duration - 3).toFixed(2);
  console.log(`Encoding ${frame} frames (${duration.toFixed(1)} s), music from ${music} s…`);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-framerate", String(FPS), "-i", path.join(FRAMES, "f%05d.jpg"),
    "-i", MUSIC,
    "-filter_complex",
    // Video: soft fade from and to warm white. Audio: enters on the tap, gentle fade in/out.
    `[0:v]fade=t=in:st=0:d=0.8:color=0xFBF7F1,fade=t=out:st=${(duration - 1.2).toFixed(2)}:d=1.2:color=0xFBF7F1,format=yuv420p[v];` +
    `[1:a]afade=t=in:st=0:d=0.5,adelay=${Math.round(musicAt * 1000)}|${Math.round(musicAt * 1000)},` +
    `afade=t=out:st=${fadeOut}:d=3,atrim=0:${duration.toFixed(2)},volume=0.9[a]`,
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-profile:v", "high", "-r", String(FPS),
    "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", "-t", duration.toFixed(2),
    OUT
  ]);
  fs.rmSync(FRAMES, { recursive: true, force: true });
  console.log(`Wrote ${path.relative(ROOT, OUT)} (${(fs.statSync(OUT).size / 1048576).toFixed(1)} MB)`);
})().catch((e) => { console.error(e); process.exit(1); });
