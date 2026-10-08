/* ==========================================================================
   data.js — loads data/wedding.json and derives everything the UI shows.
   The single-file build embeds the JSON (#wedding-data) and media
   (window.__ASSETS), so the same code runs with or without a server.
   ========================================================================== */

const MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul",
  "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"];
const WEEKDAYS = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"];

export const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Resolve an asset path (inlined data: URI in the single-file build). */
export const asset = (path) => (window.__ASSETS && window.__ASSETS[path]) || path;

export async function loadData() {
  const embedded = document.getElementById("wedding-data");
  if (embedded) return JSON.parse(embedded.textContent);
  const res = await fetch("data/wedding.json", { cache: "no-cache" });
  if (!res.ok) throw new Error(`wedding.json: HTTP ${res.status}`);
  return res.json();
}

/** Offset (minutes) of an IANA time zone at a given instant, e.g. Asia/Tashkent → +300. */
function zoneOffset(timeZone, utcMs) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).formatToParts(new Date(utcMs));
  const v = Object.fromEntries(parts.map((p) => [p.type, +p.value]));
  const asUtc = Date.UTC(v.year, v.month - 1, v.day, v.hour, v.minute, v.second);
  return (asUtc - utcMs) / 60000;
}

/** Wall-clock date/time in a time zone → absolute Date. */
export function zonedDate(y, m, d, hh, mm, timeZone) {
  const guess = Date.UTC(y, m - 1, d, hh, mm);
  let offset = 0;
  try { offset = zoneOffset(timeZone, guess); } catch (_) { offset = 300; /* Tashkent fallback */ }
  return new Date(guess - offset * 60000);
}

const pad = (n) => String(n).padStart(2, "0");
const title = (s) => s.toLowerCase().replace(/(^|\s|-)(\p{L})/gu, (_, a, b) => a + b.toUpperCase());

/** Everything derived from the raw JSON, ready for binding. */
export function derive(data) {
  const [d, m, y] = data.date.split(".").map(Number);
  const [hh, mm] = data.time.split(":").map(Number);
  const at = zonedDate(y, m, d, hh, mm, data.timezone || "Asia/Tashkent");
  const weekday = WEEKDAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()];
  const groomTitle = title(data.groom);
  const brideTitle = title(data.bride);
  const venue = data.venue || {};
  const mapsUrl = venue.mapsUrl ||
    "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent([venue.name, venue.address, venue.city].filter(Boolean).join(", "));

  const fill = (tpl = "") => tpl
    .replace(/\{groom\}/g, groomTitle).replace(/\{bride\}/g, brideTitle)
    .replace(/\{date\}/g, data.date).replace(/\{venue\}/g, venue.name || "");

  return {
    at, mapsUrl, fill,
    bind: {
      groom: data.groom,
      bride: data.bride,
      groomTitle,
      brideTitle,
      initials: `${data.groom.charAt(0)}&${data.bride.charAt(0)}`,
      namesInline: `${groomTitle} & ${brideTitle}`,
      dateDots: data.date,
      dateLong: `${pad(d)}-${MONTHS[m - 1].toLowerCase()}, ${y}-yil`,
      day: pad(d),
      monthName: MONTHS[m - 1],
      year: String(y),
      weekdayTime: `${weekday} · ${data.time}`,
      time: data.time,
      venueName: venue.name || "",
      venueCity: venue.city || "",
      heroEyebrow: data.hero?.eyebrow || "To‘yga taklifnoma",
      introKicker: data.intro?.kicker || "Biz turmush quryapmiz",
      introText: data.intro?.text || "",
      finalMessage: data.final?.message || "Sizni intiqlik bilan kutamiz.",
      rsvpDeadline: data.rsvp?.deadline ? `Iltimos, ${data.rsvp.deadline} gacha javob bering` : "Iltimos, javob bering",
      musicCredit: data.musicTitle ? `Musiqa — ${data.musicTitle}` : ""
    },
    iso: `${y}-${pad(m)}-${pad(d)}T${pad(hh)}:${pad(mm)}:00`
  };
}

/**
 * Responsive <picture>: WebP srcset from assets/images/{id}-{w}.webp (works in every current browser).
 * In the single-file build only the largest WebP is embedded.
 */
export function picture(item, { sizes = "100vw", eager = false, alt } = {}) {
  const widths = item.widths || [480, 960];
  const max = Math.max(...widths);
  const [rw, rh] = (item.ratio || "4/5").split("/").map(Number);
  const h = Math.round((max * rh) / rw);
  const src = (w, ext) => asset(`assets/images/${item.id}-${w}.${ext}`);
  const text = (alt ?? item.alt ?? "").replace(/"/g, "&quot;");
  const loading = eager ? 'fetchpriority="high"' : 'loading="lazy"';
  if (window.__BUNDLE) {
    return `<img src="${src(max, "webp")}" alt="${text}" width="${max}" height="${h}" ${loading} decoding="async">`;
  }
  const set = (ext) => widths.map((w) => `${src(w, ext)} ${w}w`).join(", ");
  return `<picture>` +
    `<source type="image/webp" srcset="${set("webp")}" sizes="${sizes}">` +
    `<img src="${src(max, "webp")}" alt="${text}" width="${max}" height="${h}" ${loading} decoding="async">` +
    `</picture>`;
}

/** Largest image URL for an item (used by the lightbox). */
export function largest(item) {
  const max = Math.max(...(item.widths || [960]));
  return asset(`assets/images/${item.id}-${max}.webp`);
}
