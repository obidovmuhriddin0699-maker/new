/* Cloud Palace — service worker
   HTML & data: network-first (always fresh invitation data).
   Static assets: stale-while-revalidate. Video/audio: passthrough (range requests). */
const VERSION = 'cloud-palace-v1';
const PRECACHE = [
  './',
  'index.html',
  'manifest.json',
  'assets/icons/favicon.svg',
  'assets/icons/icon-192.png',
  'assets/images/poster-hands-ring.jpg',
  'assets/images/couple-ring.jpg'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (/\.(mp4|webm|m4a|mp3|ogg)$/i.test(url.pathname) || req.headers.has('range')) return;

  const isDoc = req.mode === 'navigate' || /\.(html|json)$/i.test(url.pathname);
  if (isDoc) {
    e.respondWith(
      fetch(req)
        .then((res) => { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); return res; })
        .catch(() => caches.match(req).then((r) => r || caches.match('index.html')))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((cached) => {
      const net = fetch(req).then((res) => {
        if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
        return res;
      }).catch(() => cached);
      return cached || net;
    })
  );
});
