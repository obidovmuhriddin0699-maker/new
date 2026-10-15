/* ==========================================================================
   app.js — loads data/wedding.json and starts every part of the invitation.
   Each part starts in isolation: one failing feature never blanks the page.
   ========================================================================== */
import { loadData, dateParts, picture } from "./data.js";
import { initI18n, setLang, onLang, t, L } from "./i18n.js";
import { initSfx, play } from "./sfx.js";
import { initSeals } from "./seal.js";
import { initIntro } from "./intro.js";
import { initAudio } from "./audio.js";
import { initCalendar } from "./calendar.js";
import { initCountdown } from "./countdown.js";
import { initTimeline } from "./timeline.js";
import { initGallery } from "./gallery.js";
import { initRsvp } from "./rsvp.js";
import { initWishes } from "./wishes.js";
import { initSparkles } from "./sparkles.js";
import { initReveals, revealHero } from "./reveal.js";
import { setVideo, playWhenVisible } from "./media.js";

function run(name, fn) {
  try { return fn(); } catch (err) { console.error(`[${name}]`, err); return undefined; }
}

function setMeta(sel, attr, value) {
  const el = document.head.querySelector(sel);
  if (el && value) el.setAttribute(attr, value);
}

function applySeo(data) {
  const base = data.siteUrl || (location.protocol.startsWith("http") ? location.href.split(/[?#]/)[0] : "");
  const abs = (p) => (base ? new URL(p, base).href : p);
  const title = t("seo_title");
  const description = t("seo_description");
  document.title = title;
  setMeta('meta[name="description"]', "content", description);
  ["og:title", "twitter:title"].forEach((k) => setMeta(`meta[property="${k}"], meta[name="${k}"]`, "content", title));
  ["og:description", "twitter:description"].forEach((k) => setMeta(`meta[property="${k}"], meta[name="${k}"]`, "content", description));
  ["og:image", "twitter:image"].forEach((k) => setMeta(`meta[property="${k}"], meta[name="${k}"]`, "content", abs("assets/images/og-image.jpg")));
  if (base) setMeta('link[rel="canonical"]', "href", base);
  const ld = document.head.querySelector('script[type="application/ld+json"]');
  if (ld) {
    const { at } = dateParts(data);
    ld.textContent = JSON.stringify({
      "@context": "https://schema.org", "@type": "Event",
      name: t("calendar_event"), startDate: at.toISOString(),
      eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode", eventStatus: "https://schema.org/EventScheduled",
      location: { "@type": "Place", name: L(data.venue.name), address: L(data.venue.city) },
      image: [abs("assets/images/og-image.jpg")], description
    });
  }
}

function initVenue(data) {
  const v = data.venue;
  const q = encodeURIComponent(v.query || `${L(v.name)}, ${L(v.city)}`);
  const y = document.getElementById("map-yandex");
  const g = document.getElementById("map-google");
  if (y) y.href = v.yandexUrl || `https://yandex.uz/maps/?text=${q}`;
  if (g) g.href = v.googleUrl || `https://www.google.com/maps/dir/?api=1&destination=${q}`;
  [y, g].forEach((a) => a?.addEventListener("click", () => play("click")));
  const fig = document.querySelector('[data-photo="venue"]');
  const img = data.images?.[v.image];
  if (fig && img) {
    const draw = () => { fig.innerHTML = picture({ id: v.image, ...img }, { sizes: "320px", alt: L(img.alt) }); };
    draw();
    onLang(draw);
  }
}

function initSwatches(colors = []) {
  const ul = document.getElementById("swatches");
  if (ul) ul.innerHTML = colors.map((c) => `<li style="--c:${c}"></li>`).join("");
}

function initLangToggle() {
  document.querySelectorAll(".lang [data-lang]").forEach((btn) => btn.addEventListener("click", () => {
    if (btn.getAttribute("aria-pressed") === "true") return;
    play("page");
    setLang(btn.dataset.lang);
  }));
}

async function boot() {
  document.documentElement.classList.add("app-ok");
  let data;
  try {
    data = await loadData();
  } catch (err) {
    // the static Uzbek text stays readable; open the site through a server (see README)
    console.error("[data] Could not load data/wedding.json", err);
    document.documentElement.classList.replace("js", "no-js");
    return;
  }

  run("i18n", () => initI18n(data));
  run("sfx", () => initSfx(data.sfxVolume ?? 0.8));
  run("seals", initSeals);
  const music = run("audio", () => initAudio(data)) || { start() {} };
  const heroVideo = document.querySelector(".arch__video");
  const finaleVideo = document.querySelector(".medallion__video");
  run("videos", () => setVideo(finaleVideo, data.finale.video, data.finale.poster));
  run("intro", () => initIntro({
    onOpen: () => music.start(),
    onDone: () => { revealHero(); playWhenVisible([heroVideo, finaleVideo].filter(Boolean)); }
  }));
  run("lang", initLangToggle);
  run("seo", () => { applySeo(data); onLang(() => applySeo(data)); });
  const cal = run("calendar", () => initCalendar(data));
  run("countdown", () => initCountdown(cal ? cal.at : dateParts(data).at));
  run("timeline", () => initTimeline(data.program));
  run("venue", () => initVenue(data));
  run("gallery", () => initGallery(data.gallery));
  run("swatches", () => initSwatches(data.dressColors));
  run("rsvp", () => initRsvp(data.rsvp));
  run("wishes", () => initWishes(data.wishes, data.rsvp));
  run("sparkles", initSparkles);
  run("reveals", initReveals);
  document.querySelector(".scroll-hint")?.addEventListener("click", () => play("whoosh", { volume: 0.5 }));
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();
