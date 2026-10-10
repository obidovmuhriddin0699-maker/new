/* ==========================================================================
   End-to-end checks for the invitation (Playwright, Chromium).

     npm test                 # from the wedding/ folder
     node tests/e2e.cjs       # same thing

   Starts its own static server, so nothing else needs to be running.
   Note: the open-source Chromium used by Playwright has no AAC decoder, so the
   playback test swaps the .m4a response for a generated WAV tone. Real
   Chrome, Safari, Firefox and mobile browsers play the .m4a itself.
   ========================================================================== */
"use strict";

const fs = require("fs");
const path = require("path");

function loadPlaywright() {
  const candidates = ["playwright", "/opt/node-tools/node_modules/playwright"];
  for (const c of candidates) {
    try { return require(c); } catch (e) { /* try next */ }
  }
  throw new Error("Playwright not found. Run `npm install` in the wedding/ folder.");
}
const { chromium } = loadPlaywright();

const { start: serve, ROOT } = require("../tools/static-server.cjs");

/** A one-second 440 Hz mono WAV, used as a stand-in for the AAC file in Chromium. */
function wavTone() {
  const rate = 8000, n = rate;
  const buf = Buffer.alloc(44 + n * 2);
  buf.write("RIFF", 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write("WAVE", 8);
  buf.write("fmt ", 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22);
  buf.writeUInt32LE(rate, 24); buf.writeUInt32LE(rate * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34);
  buf.write("data", 36); buf.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) buf.writeInt16LE(Math.round(Math.sin(2 * Math.PI * 440 * i / rate) * 8000), 44 + i * 2);
  return buf;
}

// Pretend the browser can decode AAC (so the real code path runs with the WAV stand-in).
const AAC_CAPABLE = () => {
  const orig = HTMLMediaElement.prototype.canPlayType;
  HTMLMediaElement.prototype.canPlayType = function (t) { return /mp4/.test(t) ? "probably" : orig.call(this, t); };
};

const results = [];
let base = "";
let browser;

async function test(name, fn) {
  const started = Date.now();
  try {
    await fn();
    results.push({ name, ok: true });
    console.log(`  ✓ ${name} (${Date.now() - started} ms)`);
  } catch (err) {
    results.push({ name, ok: false, err });
    console.log(`  ✗ ${name}\n      ${String(err && err.stack || err).split("\n").slice(0, 4).join("\n      ")}`);
  }
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }

const EXPECTED_WARNINGS = [/event date .* is in the past/, /Background music unavailable/, /RSVP not sent/];

async function newPage(opts = {}) {
  const context = await browser.newContext({
    viewport: opts.viewport || { width: 390, height: 844 },
    reducedMotion: opts.reducedMotion || "no-preference",
    timezoneId: opts.timezoneId,
    hasTouch: !!opts.hasTouch,
    isMobile: !!opts.isMobile,
    acceptDownloads: true
  });
  if (opts.init) for (const fn of [].concat(opts.init)) await context.addInitScript(fn);
  const page = await context.newPage();
  page.problems = [];
  page.on("console", (m) => {
    if (m.type() === "error" || (m.type() === "warning" && !EXPECTED_WARNINGS.some((r) => r.test(m.text())))) {
      if (!(opts.allowConsole || []).some((r) => r.test(m.text()))) page.problems.push(`${m.type()}: ${m.text()}`);
    }
  });
  page.on("pageerror", (e) => page.problems.push(`pageerror: ${e.message}`));
  page.on("requestfailed", (r) => {
    if (!/rsvp\.test/.test(r.url()) && !/m4a/.test(r.url())) page.problems.push(`requestfailed: ${r.url()}`);
  });
  page.on("response", (r) => {
    if (r.status() >= 400 && r.url().startsWith(base) && !(opts.allow404 || []).some((x) => r.url().includes(x))) {
      page.problems.push(`HTTP ${r.status()}: ${r.url()}`);
    }
  });
  return page;
}

async function openInvitation(page, query = "") {
  await page.goto(base + "/" + query, { waitUntil: "load" });
  await page.waitForSelector("[data-open-invitation]", { state: "visible" });
  // force: the opening's 14 s camera push keeps the button "moving", which Playwright
  // would otherwise wait out; visibility was asserted just above.
  await page.click("[data-open-invitation]", { force: true });
  await page.waitForFunction(() => !document.documentElement.classList.contains("is-locked"));
}

/** Jump all running CSS animations to their end state (final resting layout). */
const settle = (page) => page.evaluate(() => document.getAnimations().forEach((a) => { if (a.effect && a.effect.getComputedTiming().iterations !== Infinity) a.finish(); }));

/** Scroll the whole page slowly so lazy images and reveals trigger. */
async function scrollThrough(page) {
  await page.evaluate(async () => {
    const step = window.innerHeight * 0.6;
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      window.scrollTo({ top: y, behavior: "instant" });
      await new Promise((r) => setTimeout(r, 120));
    }
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "instant" });
    await new Promise((r) => setTimeout(r, 400));
  });
}

/** Override values in config.js for one page (e.g. an RSVP endpoint). */
async function withConfig(page, patch) {
  await page.route("**/config.js", async (route) => {
    const res = await route.fetch();
    const body = (await res.text()) + `\n;(${function (p) {
      const merge = (t, s) => { for (const k in s) { if (s[k] && typeof s[k] === "object" && !Array.isArray(s[k])) merge(t[k] = t[k] || {}, s[k]); else t[k] = s[k]; } };
      merge(window.WEDDING_CONFIG, p);
    }})(${JSON.stringify(patch)});`;
    route.fulfill({ response: res, body, headers: { ...res.headers(), "content-type": "text/javascript" } });
  });
}

function contrast(hex1, hex2) {
  const lum = (hex) => {
    const c = hex.replace("#", "").match(/../g).map((x) => parseInt(x, 16) / 255)
      .map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const [a, b] = [lum(hex1), lum(hex2)].sort((x, y) => y - x);
  return (a + 0.05) / (b + 0.05);
}

(async () => {
  const server = await serve();
  base = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch();
  console.log(`Testing ${base}\n`);

  // ---------------------------------------------------------------- layout
  console.log("Responsive layout");
  const viewports = [[360, 740], [375, 667], [390, 844], [430, 932], [768, 1024], [1024, 768], [1440, 900]];
  for (const [w, h] of viewports) {
    await test(`${w}×${h}: no horizontal overflow, no clipped elements, every image loads`, async () => {
      const page = await newPage({ viewport: { width: w, height: h } });
      await page.goto(base + "/?now=2026-09-01T10:00", { waitUntil: "load" });
      await settle(page);
      const before = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      assert(before <= 0, `opening overflows horizontally by ${before}px`);
      // The opening fits on one screen: the button is fully visible without scrolling.
      const btn = await page.locator("[data-open-invitation]").boundingBox();
      assert(btn && btn.y + btn.height <= h, `open button below the fold (${btn && btn.y + btn.height} > ${h})`);
      await page.click("[data-open-invitation]", { force: true });
      await page.waitForFunction(() => !document.documentElement.classList.contains("is-locked"));
      await scrollThrough(page);
      const report = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const overflow = document.documentElement.scrollWidth - window.innerWidth;
        const clipped = [];
        document.querySelectorAll("main *:not(.cloud-layer):not(.cloud-track):not(.sky *), footer *").forEach((el) => {
          if (el.closest(".sky, .finale__photo, .opening__photo, .visually-hidden, [hidden], .field--trap")) return;
          const cs = getComputedStyle(el);
          if (cs.display === "none" || cs.visibility === "hidden") return;
          const r = el.getBoundingClientRect();
          if (r.width && (r.left < -1 || r.right > vw + 1)) clipped.push(`${el.tagName.toLowerCase()}.${el.className} [${Math.round(r.left)}, ${Math.round(r.right)}]`);
        });
        const imgs = [...document.querySelectorAll("img")].filter((i) => i.getAttribute("src"));
        const broken = imgs.filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.getAttribute("src"));
        const noDims = imgs.filter((i) => !i.getAttribute("width") || !i.getAttribute("height")).map((i) => i.getAttribute("src"));
        return { overflow, clipped: clipped.slice(0, 5), broken, noDims, count: imgs.length };
      });
      assert(report.overflow <= 0, `page overflows horizontally by ${report.overflow}px`);
      assert(!report.clipped.length, `elements outside the viewport: ${report.clipped.join("; ")}`);
      assert(!report.broken.length, `images failed to load: ${report.broken.join(", ")}`);
      assert(!report.noDims.length, `images without width/height (layout shift): ${report.noDims.join(", ")}`);
      assert(report.count >= 12, `expected the story, gallery and scene photos, found ${report.count}`);
      assert(!page.problems.length, page.problems.join("\n"));
      await page.screenshot({ path: path.join(__dirname, "screenshots", `${w}.png`) }).catch(() => {});
      await page.context().close();
    });
  }

  await test("text never overlaps the opening title at 360px (photo, names, subtitle, button in order)", async () => {
    const page = await newPage({ viewport: { width: 360, height: 640 } });
    await page.goto(base + "/", { waitUntil: "load" });
    await settle(page);
    const boxes = await page.evaluate(() => [".opening__photo", ".opening__eyebrow", ".opening__title", ".opening__date", ".opening__subtitle", ".opening__button"]
      .map((s) => { const r = document.querySelector(s).getBoundingClientRect(); return { s, top: r.top, bottom: r.bottom }; }));
    for (let i = 1; i < boxes.length; i++) {
      assert(boxes[i].top >= boxes[i - 1].bottom - 1, `${boxes[i].s} overlaps ${boxes[i - 1].s}`);
    }
    assert(boxes[boxes.length - 1].bottom <= 640, "button below the fold on a 360×640 screen");
    await page.context().close();
  });

  // ---------------------------------------------------------------- opening + audio
  console.log("\nOpening and music");
  await test("page is locked and the rest is inert until the guest opens the invitation", async () => {
    const page = await newPage();
    await page.goto(base + "/", { waitUntil: "load" });
    const locked = await page.evaluate(() => ({
      locked: document.documentElement.classList.contains("is-locked"),
      inert: [...document.querySelectorAll("#main > section:not(#opening)")].every((s) => s.hasAttribute("inert")),
      topbarHidden: getComputedStyle(document.querySelector(".topbar")).visibility === "hidden",
      musicHidden: document.querySelector("[data-music-toggle]").hidden
    }));
    assert(locked.locked && locked.inert && locked.topbarHidden && locked.musicHidden, JSON.stringify(locked));
    // First Tab stop is the skip link, the next is the open button (nothing invisible in between).
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement.hasAttribute("data-open-invitation"));
    assert(focused, "second Tab stop should be the open button");
    await page.keyboard.press("Enter");
    await page.waitForFunction(() => !document.documentElement.classList.contains("is-locked"));
    await page.waitForTimeout(1500);
    const after = await page.evaluate(() => ({
      inert: document.querySelector("#taklif").hasAttribute("inert"),
      focus: document.activeElement.id,
      y: window.scrollY,
      music: !document.querySelector("[data-music-toggle]").hidden
    }));
    assert(!after.inert && after.focus === "taklif" && after.y > 200 && after.music, JSON.stringify(after));
    assert(!page.problems.length, page.problems.join("\n"));
    await page.context().close();
  });

  await test("music never plays before the click, downloads nothing early, then plays and toggles", async () => {
    const page = await newPage({
      init: [AAC_CAPABLE, () => {
        window.__plays = 0;
        const p = HTMLMediaElement.prototype.play;
        HTMLMediaElement.prototype.play = function () { window.__plays++; return p.call(this); };
      }]
    });
    const audioRequests = [];
    await page.route("**/*.m4a", (route) => {
      audioRequests.push(route.request().url());
      route.fulfill({ status: 200, contentType: "audio/wav", body: wavTone() });
    });
    await page.goto(base + "/", { waitUntil: "load" });
    await page.waitForTimeout(1500);
    assert(await page.evaluate(() => window.__plays) === 0, "play() was called before any interaction");
    assert(audioRequests.length === 0, "audio was downloaded before the guest opened the invitation");
    await page.click("[data-open-invitation]", { force: true });
    await page.waitForFunction(() => document.querySelector("[data-music-toggle]").getAttribute("aria-pressed") === "true", null, { timeout: 5000 });
    assert(decodeURIComponent(audioRequests[0] || "").endsWith("assets/audio/Asadov Silencio.m4a"), `wrong audio file: ${audioRequests[0]}`);
    const label = await page.getAttribute("[data-music-toggle]", "aria-label");
    assert(label === "Musiqani o‘chirish", `toggle label: ${label}`);
    await page.click("[data-music-toggle]");
    await page.waitForFunction(() => document.querySelector("[data-music-toggle]").getAttribute("aria-pressed") === "false");
    await page.click("[data-music-toggle]");
    await page.waitForFunction(() => document.querySelector("[data-music-toggle]").getAttribute("aria-pressed") === "true");
    assert(!page.problems.length, page.problems.join("\n"));
    await page.context().close();
  });

  await test("missing audio file is reported on the toggle instead of pretending to play", async () => {
    const page = await newPage({ init: AAC_CAPABLE, allow404: [".m4a"], allowConsole: [/404/] });
    await page.route("**/*.m4a", (route) => route.fulfill({ status: 404, body: "" }));
    await openInvitation(page);
    await page.waitForFunction(() => document.querySelector("[data-music-toggle]").classList.contains("is-unavailable"), null, { timeout: 5000 });
    const state = await page.evaluate(() => ({
      pressed: document.querySelector("[data-music-toggle]").getAttribute("aria-pressed"),
      text: document.querySelector("[data-music-label]").textContent
    }));
    assert(state.pressed === "false" && state.text === "Musiqa yo‘q", JSON.stringify(state));
    assert(!page.problems.length, page.problems.join("\n"));
    await page.context().close();
  });

  await test("browsers without AAC support get the same honest 'Musiqa yo‘q' state", async () => {
    const page = await newPage();
    await openInvitation(page);
    const text = await page.textContent("[data-music-label]");
    assert(text === "Musiqa yo‘q", `label was "${text}"`);
    await page.context().close();
  });

  // ---------------------------------------------------------------- countdown
  console.log("\nCountdown");
  await test("counts down from the configured date in Asia/Tashkent and ticks every second", async () => {
    const page = await newPage();
    await page.goto(base + "/?now=2026-10-05T15:59:50", { waitUntil: "load" });
    const read = () => page.evaluate(() => ["days", "hours", "minutes", "seconds"].map((u) => document.querySelector(`[data-unit="${u}"]`).textContent));
    const first = await read();
    assert(first[0] === "1" && first[1] === "00" && first[2] === "00" && ["10", "09"].includes(first[3]), `got ${first}`);
    await page.waitForTimeout(2100);
    const second = await read();
    assert(Number(second[3]) <= Number(first[3]) - 2, `did not tick: ${first[3]} → ${second[3]}`);
    const live = await page.textContent("[data-countdown-live]");
    assert(/1 kun, 0 soat va 0 daqiqa/.test(live), `live summary: ${live}`);
    await page.context().close();
  });

  await test("result is independent of the visitor's own time zone (New York, Tokyo)", async () => {
    for (const tz of ["America/New_York", "Asia/Tokyo"]) {
      const page = await newPage({ timezoneId: tz });
      await page.goto(base + "/?now=2026-10-06T14:30", { waitUntil: "load" });
      const vals = await page.evaluate(() => ["days", "hours", "minutes"].map((u) => document.querySelector(`[data-unit="${u}"]`).textContent));
      assert(vals.join(":") === "0:01:30" || vals.join(":") === "0:01:29", `${tz}: ${vals.join(":")}`);
      await page.context().close();
    }
  });

  await test("shows a 'today' message during the event and a thank-you after it", async () => {
    const page = await newPage();
    await page.goto(base + "/?now=2026-10-06T17:00", { waitUntil: "load" });
    const during = await page.evaluate(() => ({ timer: document.querySelector("[data-countdown]").hidden, msg: document.querySelector("[data-countdown-message]").textContent }));
    assert(during.timer && /Baxtli kunimiz keldi/.test(during.msg), JSON.stringify(during));
    await page.goto(base + "/", { waitUntil: "load" }); // real "now" (10 Oct 2026+) is after the configured date
    const after = await page.evaluate(() => ({ timer: document.querySelector("[data-countdown]").hidden, title: document.querySelector("[data-countdown-title]").textContent }));
    assert(after.timer && after.title === "Bu kun ortda qoldi", JSON.stringify(after));
    const badge = await page.isHidden("[data-preview-badge]");
    assert(badge, "preview badge should only appear with ?now=");
    await page.context().close();
  });

  await test("calendar file starts 16:00 Tashkent (11:00 UTC)", async () => {
    const page = await newPage();
    await openInvitation(page, "?now=2026-09-01T10:00");
    const [download] = await Promise.all([page.waitForEvent("download"), page.click("[data-add-calendar]")]);
    const text = fs.readFileSync(await download.path(), "utf8");
    assert(/DTSTART:20261006T110000Z/.test(text), "DTSTART missing or wrong");
    assert(/LOCATION:Versal to‘yxonasi\\, Farg‘ona shahri/.test(text), "LOCATION missing");
    await page.context().close();
  });

  // ---------------------------------------------------------------- gallery
  console.log("\nGallery");
  await test("lightbox: open, arrows, wrap-around, Esc, focus returns", async () => {
    const page = await newPage({ viewport: { width: 1440, height: 900 } });
    await openInvitation(page);
    const thumb = page.locator("[data-gallery-index='0']");
    await thumb.scrollIntoViewIfNeeded();
    await thumb.click();
    await page.waitForSelector("[data-lightbox].is-open");
    await page.waitForFunction(() => document.querySelector("[data-lightbox-img]").naturalWidth > 0);
    const count = () => page.textContent("[data-lightbox-count]");
    assert(await count() === "1 / 7", await count());
    assert(await page.evaluate(() => document.activeElement.closest("[data-lightbox]") !== null), "focus not moved into the lightbox");
    await page.keyboard.press("ArrowRight");
    assert(await count() === "2 / 7", await count());
    await page.keyboard.press("ArrowLeft");
    await page.keyboard.press("ArrowLeft");
    assert(await count() === "7 / 7", await count());
    await page.click("[data-lightbox-next]");
    assert(await count() === "1 / 7", await count());
    await page.waitForFunction(() => document.querySelector("[data-lightbox-img]").classList.contains("is-ready"));
    const alt = await page.getAttribute("[data-lightbox-img]", "alt");
    assert(alt && alt.length > 5, "lightbox image needs alt text");
    // Tab stays inside the dialog.
    for (let i = 0; i < 5; i++) await page.keyboard.press("Tab");
    assert(await page.evaluate(() => !!document.activeElement.closest("[data-lightbox]")), "focus escaped the lightbox");
    await page.keyboard.press("Escape");
    await page.waitForSelector("[data-lightbox]", { state: "hidden" });
    assert(await page.evaluate(() => document.activeElement.getAttribute("data-gallery-index") === "0"), "focus did not return to the thumbnail");
    assert(!page.problems.length, page.problems.join("\n"));
    await page.context().close();
  });

  await test("lightbox: touch swipe left/right on a phone", async () => {
    const page = await newPage({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
    await openInvitation(page);
    const thumb = page.locator("[data-gallery-index='2']");
    await thumb.scrollIntoViewIfNeeded();
    await thumb.tap();
    await page.waitForSelector("[data-lightbox].is-open");
    const swipe = (dx) => page.evaluate((dx) => {
      const box = document.querySelector("[data-lightbox]");
      const mk = (x) => new Touch({ identifier: 1, target: box, clientX: x, clientY: 400 });
      box.dispatchEvent(new TouchEvent("touchstart", { touches: [mk(200)], changedTouches: [mk(200)], bubbles: true }));
      box.dispatchEvent(new TouchEvent("touchend", { touches: [], changedTouches: [mk(200 + dx)], bubbles: true }));
    }, dx);
    await swipe(-120);
    assert(await page.textContent("[data-lightbox-count]") === "4 / 7", "swipe left should go forward");
    await swipe(140);
    assert(await page.textContent("[data-lightbox-count]") === "3 / 7", "swipe right should go back");
    await page.tap("[data-lightbox-close].lightbox__btn");
    await page.waitForSelector("[data-lightbox]", { state: "hidden" });
    await page.context().close();
  });

  // ---------------------------------------------------------------- location + menu
  console.log("\nLocation and navigation");
  await test("“Xaritada ochish” opens a map search for the venue in a new tab", async () => {
    const page = await newPage();
    await openInvitation(page);
    const link = page.locator("[data-map-link]");
    const href = await link.getAttribute("href");
    assert(/^https:\/\/www\.google\.com\/maps\/search\/\?api=1&query=/.test(href), href);
    assert(decodeURIComponent(href).includes("Versal to‘yxonasi, Farg‘ona shahri"), href);
    assert(await link.getAttribute("target") === "_blank" && /noopener/.test(await link.getAttribute("rel")), "target/rel");
    assert(/Xaritada ochish/.test(await link.textContent()), "link text");
    await page.context().close();
  });

  await test("deep link (#galereya) opens on that section after the gate", async () => {
    const page = await newPage();
    await page.goto(base + "/#galereya", { waitUntil: "load" });
    assert(await page.evaluate(() => window.scrollY) === 0, "should stay on the opening until the guest opens it");
    await page.click("[data-open-invitation]", { force: true });
    await page.waitForFunction(() => !document.documentElement.classList.contains("is-locked"));
    await page.waitForTimeout(300);
    const top = await page.evaluate(() => document.querySelector("#galereya").getBoundingClientRect().top);
    assert(Math.abs(top) < 120, `gallery not in view (top=${top})`);
    const items = await page.evaluate(() => document.querySelectorAll("#hikoya ol > li").length);
    assert(items === 4, `story list should have 4 items, has ${items}`);
    await page.context().close();
  });

  await test("menu opens, traps focus, closes with Esc and navigates", async () => {
    const page = await newPage();
    await openInvitation(page);
    await page.waitForTimeout(1200);
    await page.click("[data-menu-open]");
    await page.waitForSelector("[data-menu].is-open");
    assert(await page.getAttribute("[data-menu-open]", "aria-expanded") === "true", "aria-expanded");
    await page.keyboard.press("Escape");
    await page.waitForSelector("[data-menu]", { state: "hidden" });
    assert(await page.evaluate(() => document.activeElement.hasAttribute("data-menu-open")), "focus should return to the menu button");
    await page.click("[data-menu-open]");
    await page.click("[data-menu] a[href='#javob']");
    await page.waitForTimeout(1500);
    const top = await page.evaluate(() => document.querySelector("#javob").getBoundingClientRect().top);
    assert(Math.abs(top) < 120, `RSVP section not in view (top=${top})`);
    await page.context().close();
  });

  // ---------------------------------------------------------------- RSVP
  console.log("\nRSVP");
  await test("validation: accessible inline errors and focus on the first problem", async () => {
    const page = await newPage();
    await openInvitation(page, "?now=2026-09-01T10:00");
    await page.locator("#javob").scrollIntoViewIfNeeded();
    await page.click("[data-rsvp-submit]");
    const state = await page.evaluate(() => ({
      nameErr: document.querySelector('[data-error-for="name"]').textContent,
      attErr: document.querySelector('[data-error-for="attendance"]').textContent,
      invalid: document.querySelector("#rsvp-name").getAttribute("aria-invalid"),
      focus: document.activeElement.id,
      described: document.querySelector("#rsvp-name").getAttribute("aria-describedby")
    }));
    assert(state.nameErr && state.attErr && state.invalid === "true" && state.focus === "rsvp-name" && state.described === "rsvp-name-error", JSON.stringify(state));
    // Guest count appears only for "yes".
    assert(await page.isHidden("[data-guests-field]"), "guest count should be hidden at first");
    await page.check('input[name="attendance"][value="yes"]');
    assert(await page.isVisible("[data-guests-field]"), "guest count should show for 'yes'");
    await page.check('input[name="attendance"][value="no"]');
    assert(await page.isHidden("[data-guests-field]"), "guest count should hide for 'no'");
    await page.context().close();
  });

  await test("without an endpoint it says replies are not collected — never 'saved'", async () => {
    const page = await newPage();
    let posted = 0;
    page.on("request", (r) => { if (r.method() === "POST") posted++; });
    await openInvitation(page, "?now=2026-09-01T10:00");
    await page.fill("#rsvp-name", "Aziza Karimova");
    await page.check('input[name="attendance"][value="yes"]');
    await page.click("[data-rsvp-submit]");
    const status = await page.textContent("[data-rsvp-status]");
    assert(/yuborilmadi/.test(status) && /sozlanmagan/.test(status), status);
    assert(await page.isHidden("[data-rsvp-done]"), "success panel must not appear");
    assert(posted === 0, "nothing should be posted");
    await page.context().close();
  });

  await test("with an endpoint: loading state, exactly one request on double submit, success, remembered", async () => {
    const page = await newPage();
    await withConfig(page, { rsvp: { rsvpEndpoint: "https://rsvp.test/submit" } });
    const bodies = [];
    await page.route("https://rsvp.test/**", async (route) => {
      bodies.push(JSON.parse(route.request().postData()));
      await new Promise((r) => setTimeout(r, 900));
      route.fulfill({ status: 200, contentType: "application/json", headers: { "Access-Control-Allow-Origin": "*" }, body: '{"ok":true}' });
    });
    await openInvitation(page, "?now=2026-09-01T10:00");
    await page.fill("#rsvp-name", "  Aziza   Karimova ");
    await page.check('input[name="attendance"][value="yes"]');
    await page.selectOption("#rsvp-guests", "3");
    await page.fill("#rsvp-message", "Baxtli bo‘linglar!");
    await page.evaluate(() => {
      const f = document.querySelector("[data-rsvp-form]");
      f.requestSubmit(); f.requestSubmit(); f.requestSubmit();
    });
    const loading = await page.evaluate(() => {
      const b = document.querySelector("[data-rsvp-submit]");
      return { disabled: b.disabled, busy: b.getAttribute("aria-busy"), text: b.textContent.trim() };
    });
    assert(loading.disabled && loading.busy === "true" && /Yuborilmoqda/.test(loading.text), JSON.stringify(loading));
    await page.waitForSelector("[data-rsvp-done]", { state: "visible" });
    assert(bodies.length === 1, `expected 1 request, got ${bodies.length}`);
    const b = bodies[0];
    assert(b.name === "Aziza Karimova" && b.attendance === "yes" && b.guests === 3 && b.message === "Baxtli bo‘linglar!" && b.submissionId, JSON.stringify(b));
    assert(/Rahmat, Aziza Karimova/.test(await page.textContent("[data-rsvp-done-title]")), "success title");
    await page.reload({ waitUntil: "load" });
    assert(/avval yuborilgan/.test(await page.textContent("[data-rsvp-done-text]")), "reply should be remembered on this device");
    await page.context().close();
  });

  await test("server error or timeout keeps the form and explains, then a retry succeeds", async () => {
    const page = await newPage({ allowConsole: [/RSVP failed/, /500/] });
    await withConfig(page, { rsvp: { rsvpEndpoint: "https://rsvp.test/submit" } });
    let calls = 0;
    await page.route("https://rsvp.test/**", (route) => {
      calls++;
      if (calls === 1) return route.fulfill({ status: 500, headers: { "Access-Control-Allow-Origin": "*" }, body: "boom" });
      if (calls === 2) return route.fulfill({ status: 200, contentType: "application/json", headers: { "Access-Control-Allow-Origin": "*" }, body: '{"ok":false,"error":"sheet locked"}' });
      return route.fulfill({ status: 200, headers: { "Access-Control-Allow-Origin": "*" }, body: "" });
    });
    await openInvitation(page, "?now=2026-09-01T10:00");
    await page.fill("#rsvp-name", "Bobur");
    await page.check('input[name="attendance"][value="no"]');
    await page.click("[data-rsvp-submit]");
    await page.waitForFunction(() => document.querySelector("[data-rsvp-status]").classList.contains("is-error"));
    assert(/vaqtinchalik nosozlik/.test(await page.textContent("[data-rsvp-status]")), "500 message");
    await page.click("[data-rsvp-submit]");
    await page.waitForFunction(() => /qabul qilib bo‘lmadi/.test(document.querySelector("[data-rsvp-status]").textContent));
    assert(await page.isVisible("[data-rsvp-form]"), "form should stay visible after an error");
    await page.click("[data-rsvp-submit]");
    await page.waitForSelector("[data-rsvp-done]", { state: "visible" });
    assert(/Javobingiz uchun rahmat/.test(await page.textContent("[data-rsvp-done-title]")), "decline thank-you");
    await page.context().close();
  });

  await test("replies close after the deadline / once the event has started", async () => {
    const page = await newPage();
    await openInvitation(page); // real now is after 6 Oct 2026
    assert(await page.isVisible("[data-rsvp-closed]") && await page.isHidden("[data-rsvp-form]"), "form should be closed");
    await page.context().close();
  });

  // ---------------------------------------------------------------- a11y + misc
  console.log("\nAccessibility and robustness");
  await test("reduced motion: content visible immediately, no drifting clouds", async () => {
    const page = await newPage({ reducedMotion: "reduce" });
    await openInvitation(page);
    const s = await page.evaluate(() => ({
      reveal: getComputedStyle(document.querySelector("#hikoya .reveal")).opacity,
      drift: getComputedStyle(document.querySelector(".cloud-track")).animationName,
      y: window.scrollY
    }));
    assert(s.reveal === "1" && s.drift === "none" && s.y > 200, JSON.stringify(s));
    await page.context().close();
  });

  await test("structure: one h1, landmarks, labelled form controls, alt text everywhere", async () => {
    const page = await newPage();
    await openInvitation(page, "?now=2026-09-01T10:00");
    const r = await page.evaluate(() => {
      const unlabeled = [...document.querySelectorAll("input:not([type=hidden]):not([tabindex='-1']), select, textarea")]
        .filter((el) => !(el.labels && el.labels.length) && !el.getAttribute("aria-label"));
      const imgsNoAlt = [...document.querySelectorAll("img[src]")].filter((i) => !i.hasAttribute("alt"));
      const buttonsNoName = [...document.querySelectorAll("button")].filter((b) => !b.hidden && !(b.textContent.trim() || b.getAttribute("aria-label")));
      return {
        h1: document.querySelectorAll("h1").length,
        main: !!document.querySelector("main"), nav: !!document.querySelector("nav"), footer: !!document.querySelector("footer"),
        unlabeled: unlabeled.map((e) => e.name), imgsNoAlt: imgsNoAlt.length, buttonsNoName: buttonsNoName.length,
        lang: document.documentElement.lang
      };
    });
    assert(r.h1 === 1 && r.main && r.nav && r.footer && !r.unlabeled.length && !r.imgsNoAlt && !r.buttonsNoName && r.lang === "uz", JSON.stringify(r));
    await page.context().close();
  });

  await test("colour contrast of text tokens meets WCAG AA", async () => {
    const pairs = [
      ["#2F2822", "#FBF7F1", 4.5, "ink on ivory"],
      ["#665748", "#FBF7F1", 4.5, "taupe on ivory"],
      ["#665748", "#F4ECE0", 4.5, "taupe on cream"],
      ["#665748", "#EADCC6", 4.5, "taupe on champagne"],
      ["#7E6440", "#FBF7F1", 4.5, "gold-deep on ivory"],
      ["#7E6440", "#F4ECE0", 4.5, "gold-deep on cream"],
      ["#7E6440", "#EADCC6", 3.0, "gold-deep large text on champagne"],
      ["#FBF7F1", "#2F2822", 4.5, "button text"],
      ["#9A4334", "#FFFEFB", 4.5, "error text"]
    ];
    const fails = pairs.filter(([a, b, min]) => contrast(a, b) < min).map(([a, b, min, n]) => `${n}: ${contrast(a, b).toFixed(2)} < ${min}`);
    assert(!fails.length, fails.join("; "));
  });

  await test("works when opened straight from disk (file://)", async () => {
    // Chrome refuses web fonts over file:// (CORS), so the page falls back to system
    // serif/sans fonts there. Everything else must work.
    const page = await newPage({ allowConsole: [/Failed to load resource/, /Access to font at .* blocked by CORS/, /preload for .*woff2/] });
    page.removeAllListeners("requestfailed");
    await page.goto("file://" + path.join(ROOT, "index.html"), { waitUntil: "load" });
    await page.click("[data-open-invitation]", { force: true });
    await page.waitForFunction(() => !document.documentElement.classList.contains("is-locked"));
    const ok = await page.evaluate(() => document.querySelector("#tafsilotlar .section-title").textContent.includes("Umida"));
    assert(ok, "content did not render from file://");
    assert(!page.problems.filter((p) => !/requestfailed/.test(p)).length, page.problems.join("\n"));
    await page.context().close();
  });

  await browser.close();
  server.close();

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} passed`);
  process.exit(failed.length ? 1 : 0);
})().catch((err) => { console.error(err); process.exit(1); });
