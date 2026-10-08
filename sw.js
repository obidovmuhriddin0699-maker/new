/* ==========================================================================
   sw.js — offline shell. Network-first for pages, code and wedding.json (edits always
   show up), cache-first for images and fonts.
   Video and audio are never cached here: browsers request them with Range
   headers, which a simple cache cannot answer correctly.
   Bump VERSION after changing files to refresh every guest's cache.
   ========================================================================== */
const VERSION = "sevgi-bulutlari-v2";
const SHELL = [
  "./",
  "index.html",
  "manifest.json",
  "css/fonts.css",
  "css/base.css",
  "css/components.css",
  "css/clouds.css",
  "css/animations.css",
  "css/responsive.css",
  "js/app.bundle.js",
  "data/wedding.json",
  "assets/fonts/InstrumentSerif-normal-latin.woff2",
  "assets/fonts/InstrumentSerif-italic-latin.woff2",
  "assets/fonts/Manrope-normal-latin.woff2",
  "assets/fonts/GreatVibes-latin.woff2",
  "assets/clouds/cloud-left.webp",
  "assets/clouds/cloud-right.webp",
  "assets/clouds/cloud-band.webp",
  "assets/icons/favicon.svg",
  "assets/icons/icon-192.png",
  "assets/video/beach-poster.webp"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  if (req.headers.has("range") || /\.(mp4|webm|m4a|mp3)$/i.test(url.pathname)) return;

  // images and fonts never change → cache first
  if (/\.(webp|png|jpg|svg|woff2)$/i.test(url.pathname)) {
    e.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        if (res.ok && res.type === "basic") { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
        return res;
      }))
    );
    return;
  }

  // pages, code and wedding.json → always the newest from the network, cache only offline
  e.respondWith(
    fetch(req).then((res) => {
      if (res.ok && res.type === "basic") { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true }))
  );
});
