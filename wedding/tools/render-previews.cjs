/* Re-render the link-preview image (assets/icons/og-image.jpg, 1200×630) and the
   home-screen icon (assets/icons/apple-touch-icon.png) from the live page, so they
   always match config.js. Run after changing names or the date:
     node tools/render-previews.cjs                                            */
"use strict";
const path = require("path");
const { start, ROOT } = require("./static-server.cjs");

function loadPlaywright() {
  for (const c of ["playwright", "/opt/node-tools/node_modules/playwright"]) {
    try { return require(c); } catch (e) { /* next */ }
  }
  throw new Error("Playwright not found. Run `npm install` in the wedding/ folder.");
}

(async () => {
  const { chromium } = loadPlaywright();
  const server = await start();
  const base = `http://127.0.0.1:${server.address().port}`;
  const out = path.join(ROOT, "assets", "icons");
  const browser = await chromium.launch();

  const og = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  await og.goto(base + "/", { waitUntil: "networkidle" });
  await og.addStyleTag({ content: ".opening__actions,.opening__subtitle{display:none!important}.opening__photo{height:300px!important}" });
  await og.evaluate(() => document.getAnimations().forEach((a) => { try { a.finish(); } catch (e) { /* infinite */ } }));
  await og.waitForTimeout(500);
  await og.screenshot({ path: path.join(out, "og-image.jpg"), type: "jpeg", quality: 84 });

  const icon = await browser.newPage({ viewport: { width: 180, height: 180 } });
  await icon.goto(base + "/", { waitUntil: "networkidle" });
  const mono = await icon.evaluate(() => {
    const c = window.WEDDING_CONFIG;
    return [c.groom.charAt(0), c.bride.charAt(0)];
  });
  await icon.setContent(`<html><head><link rel="stylesheet" href="${base}/css/fonts.css"></head>
    <body style="margin:0;width:180px;height:180px;display:grid;place-items:center;background:linear-gradient(180deg,#EADCC6,#FBF7F1);font-family:'Instrument Serif';color:#2F2822;font-size:78px;letter-spacing:2px">
    ${mono[0]}<i style="color:#A88A5C;font-size:58px;margin:0 2px">&amp;</i>${mono[1]}</body></html>`);
  await icon.waitForTimeout(800);
  await icon.screenshot({ path: path.join(out, "apple-touch-icon.png") });

  await browser.close();
  server.close();
  console.log("Wrote assets/icons/og-image.jpg and assets/icons/apple-touch-icon.png");
})().catch((e) => { console.error(e); process.exit(1); });
