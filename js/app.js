/* ==========================================================================
   app.js — entry point. Loads data/wedding.json, fills the page and starts
   every module. Each module is started in isolation, so a failure in one
   (e.g. an old browser missing an API) never blanks the whole invitation.
   ========================================================================== */
import { loadData, derive, picture, asset } from "./data.js";
import { initNavigation } from "./navigation.js";
import { initScroll, initMediaVisibility } from "./scroll.js";
import { initHero, initReveals, initCursor } from "./animations.js";
import { initCountdown } from "./countdown.js";
import { initGallery } from "./gallery.js";
import { initAudio } from "./audio.js";
import { initRsvp } from "./rsvp.js";
import { initClouds } from "./clouds.js";
import { initSparkles } from "./sparkles.js";

const esc = (s = "") => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function run(name, fn) {
  try { return fn(); } catch (err) { console.error(`[${name}]`, err); }
}

/* ---------- content ---------- */
function bindText(bind) {
  document.querySelectorAll("[data-bind]").forEach((el) => {
    const v = bind[el.dataset.bind];
    if (v !== undefined) el.textContent = v;
  });
}

function setMeta(selector, attr, value) {
  const el = document.head.querySelector(selector);
  if (el && value) el.setAttribute(attr, value);
}

function applySeo(data, d) {
  const seo = data.seo || {};
  const base = data.siteUrl || (location.protocol.startsWith("http") ? location.href.split(/[?#]/)[0] : "");
  const abs = (p) => (base ? new URL(p, base).href : p);
  const title = d.fill(seo.title || "{groom} & {bride} — to‘yga taklifnoma");
  const description = d.fill(seo.description || "");
  const image = abs(seo.image || "assets/images/og-image.jpg");

  document.title = title;
  setMeta('meta[name="description"]', "content", description);
  setMeta('meta[property="og:title"]', "content", title);
  setMeta('meta[property="og:description"]', "content", description);
  setMeta('meta[property="og:image"]', "content", image);
  setMeta('meta[name="twitter:title"]', "content", title);
  setMeta('meta[name="twitter:description"]', "content", description);
  setMeta('meta[name="twitter:image"]', "content", image);
  if (base) {
    setMeta('link[rel="canonical"]', "href", base);
    let og = document.head.querySelector('meta[property="og:url"]');
    if (!og) { og = document.createElement("meta"); og.setAttribute("property", "og:url"); document.head.appendChild(og); }
    og.setAttribute("content", base);
  }

  const ld = document.head.querySelector('script[type="application/ld+json"]');
  if (ld) {
    const venue = data.venue || {};
    ld.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Event",
      name: `${d.bind.namesInline} — to‘y`,
      startDate: d.at.toISOString(),
      eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
      eventStatus: "https://schema.org/EventScheduled",
      location: { "@type": "Place", name: venue.name, address: [venue.address, venue.city, "O‘zbekiston"].filter(Boolean).join(", ") },
      image: [image],
      description
    });
  }
}

function renderStory(story, byId) {
  const list = document.getElementById("story-list");
  if (!list || !story?.length) return;
  list.innerHTML = story.map((s) => {
    const img = byId[s.image];
    return `
      <li class="event">
        <p class="event__year">${esc(s.year)}</p>
        <h3 class="meta event__title">${esc(s.title)}</h3>
        <p class="event__text">${esc(s.text)}</p>
        ${img ? `<figure class="photo event__photo" data-cine>${picture(img, { sizes: "(min-width: 768px) 460px, 92vw" })}</figure>` : ""}
      </li>`;
  }).join("");
}

function renderProgram(program) {
  const list = document.getElementById("program-list");
  if (!list || !program?.length) return;
  list.innerHTML = program.map((p) => `
    <li class="program__item">
      <p class="program__time">${esc(p.time)}</p>
      <div class="program__body">
        <h3 class="meta program__title">${esc(p.title)}</h3>
        <p class="program__text">${esc(p.text)}</p>
      </div>
    </li>`).join("");
}

function renderPhotos(data, byId) {
  const slots = {
    venue: { id: data.venue?.image, sizes: "(min-width: 1024px) 45vw, 92vw" },
    final: { id: data.films?.final?.image, sizes: "100vw" }
  };
  document.querySelectorAll("[data-photo]").forEach((fig) => {
    const slot = slots[fig.dataset.photo];
    const item = slot && byId[slot.id];
    if (!item) return;
    fig.setAttribute("data-cine", "");
    fig.innerHTML = picture(item, { sizes: slot.sizes, alt: fig.getAttribute("aria-hidden") ? "" : item.alt });
  });
}

/** Film panels: an mp4 (H.264) source plus a WebM fallback, poster first. */
function renderFilms(films = {}) {
  const videos = [];
  document.querySelectorAll("[data-film]").forEach((fig) => {
    const film = films[fig.dataset.film];
    const video = fig.querySelector("video");
    if (!film?.video || !video) { fig.hidden = true; return; }
    if (film.poster) video.poster = asset(film.poster);
    const sources = [[`${film.video}.mp4`, "video/mp4"], [`${film.video}.webm`, "video/webm"]]
      .filter(([src]) => !window.__ASSETS || window.__ASSETS[src]);
    video.innerHTML = sources.map(([src, type]) => `<source src="${asset(src)}" type="${type}">`).join("");
    const cap = fig.querySelector("figcaption");
    if (cap) cap.textContent = film.caption || "";
    videos.push(video);
  });
  return videos;
}

function heroVideo() {
  return document.querySelector(".hero__video");
}

/* ---------- boot ---------- */
async function boot() {
  const hero = run("hero-video", heroVideo);
  run("clouds", initClouds);
  run("hero", initHero);
  run("sparkles", initSparkles);
  run("navigation", initNavigation);

  let data;
  try {
    data = await loadData();
  } catch (err) {
    // The static HTML already holds the default copy, so the page stays usable.
    console.error("[data] Could not load data/wedding.json — open the site through a local server (see README).", err);
    run("scroll", initScroll);
    run("reveals", () => initReveals());
    run("cursor", initCursor);
    if (hero) run("media", () => initMediaVisibility([hero]));
    return;
  }

  const d = derive(data);
  const byId = Object.fromEntries([
    ...Object.entries(data.images || {}).map(([id, img]) => [id, { id, ...img }]),
    ...(data.gallery || []).map((g) => [g.id, g])
  ]);

  run("bind", () => bindText(d.bind));
  run("seo", () => applySeo(data, d));
  run("map", () => { const a = document.getElementById("map-link"); if (a) a.href = d.mapsUrl; });
  run("story", () => renderStory(data.story, byId));
  run("program", () => renderProgram(data.program));
  run("photos", () => renderPhotos(data, byId));
  const films = run("films", () => renderFilms(data.films)) || [];
  run("gallery", () => initGallery(data.gallery));

  run("scroll", initScroll);
  run("reveals", () => initReveals());
  run("cursor", initCursor);
  run("countdown", () => initCountdown(d.at));
  run("media", () => initMediaVisibility([hero, ...films].filter(Boolean)));
  run("audio", () => initAudio(data));
  run("rsvp", () => initRsvp(data.rsvp, d.bind.namesInline));

  if ("serviceWorker" in navigator && location.protocol.startsWith("http") && !window.__BUNDLE) {
    navigator.serviceWorker.register("sw.js").catch((err) => console.warn("[sw]", err));
  }
}

boot();
