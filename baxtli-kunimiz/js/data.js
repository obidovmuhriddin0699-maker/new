/* ==========================================================================
   data.js — loads data/wedding.json (or the copy embedded by the single-file
   build), time-zone maths and responsive images.
   ========================================================================== */
export const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
export const pad = (n) => String(n).padStart(2, "0");

/** Asset path → data: URI in the single-file build. */
export const asset = (path) => (window.__ASSETS && window.__ASSETS[path]) || path;

export async function loadData() {
  const embedded = document.getElementById("wedding-data");
  if (embedded) return JSON.parse(embedded.textContent);
  const res = await fetch("data/wedding.json", { cache: "no-cache" });
  if (!res.ok) throw new Error(`wedding.json: HTTP ${res.status}`);
  return res.json();
}

function zoneOffset(timeZone, utcMs) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).formatToParts(new Date(utcMs));
  const v = {};
  parts.forEach((p) => { v[p.type] = +p.value; });
  return (Date.UTC(v.year, v.month - 1, v.day, v.hour, v.minute, v.second) - utcMs) / 60000;
}

/** Wall-clock time in an IANA zone → absolute Date (Asia/Tashkent = UTC+5). */
export function zonedDate(y, m, d, hh, mm, timeZone) {
  const guess = Date.UTC(y, m - 1, d, hh, mm);
  let offset = 300;
  try { offset = zoneOffset(timeZone, guess); } catch (_) { /* old browser: Tashkent */ }
  return new Date(guess - offset * 60000);
}

/** Parsed wedding date parts. */
export function dateParts(data) {
  const [d, m, y] = data.date.split(".").map(Number);
  const [hh, mm] = data.time.split(":").map(Number);
  return { d, m, y, hh, mm, at: zonedDate(y, m, d, hh, mm, data.timezone || "Asia/Tashkent") };
}

/** <picture> with a WebP srcset (every current browser). */
export function picture(item, { sizes = "100vw", alt = "", eager = false } = {}) {
  const widths = item.widths || [480, 960];
  const max = Math.max(...widths);
  const [rw, rh] = (item.ratio || "4/5").split("/").map(Number);
  const src = (w) => asset(`assets/images/${item.id}-${w}.webp`);
  const text = String(alt).replace(/"/g, "&quot;");
  const loading = eager ? 'fetchpriority="high"' : 'loading="lazy"';
  const img = `<img src="${src(max)}" alt="${text}" width="${max}" height="${Math.round((max * rh) / rw)}" ${loading} decoding="async">`;
  if (window.__BUNDLE) return img;
  return `<picture><source type="image/webp" srcset="${widths.map((w) => `${src(w)} ${w}w`).join(", ")}" sizes="${sizes}">${img}</picture>`;
}

export function largest(item) {
  return asset(`assets/images/${item.id}-${Math.max(...(item.widths || [960]))}.webp`);
}
