# Luxury Wedding Invitation Platform — Theme 10: Cloud Palace

Open `index.html` in a browser, or serve it locally with `python3 -m http.server`.

## Structure

```
index.html            Cloud Palace theme (markup + CSS + runtime, self-contained)
data/wedding.json     Wedding data (overrides inline data when served over HTTP)
assets/video/         Optimised clips (H.264, no audio, faststart)
assets/images/        Posters and stills (JPG + WebP + AVIF), og-cover.jpg
assets/audio/         Put "Asadov Silencio.m4a" here
assets/icons/         favicon, PWA icons
manifest.json, sw.js  PWA
```

## Data

All content comes from a single `weddingData` object (inline `#wedding-data` → `data/wedding.json`
→ `CONFIG.apiBase/invitations/{slug}`). No theme text is hard-coded.
RSVP posts JSON to `rsvp.endpoint` when it is set; otherwise answers are stored in localStorage.

## Runtime modules (inside index.html)

DataLoader · Theme engine (bindings + SEO) · SkyEngine (WebGL clouds) · CloudSprites/CloudBanks ·
Particles · AudioEngine · Countdown (Asia/Tashkent) · Film · Story · Gallery + Lightbox · Map · RSVP · Motion (reveal/parallax).
