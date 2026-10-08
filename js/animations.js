/* ==========================================================================
   animations.js — hero entrance, scroll reveals (IntersectionObserver)
   and the subtle desktop cursor.
   ========================================================================== */
import { reducedMotion } from "./data.js";
import { onceInView } from "./inview.js";

/** Hero: wait for fonts + poster so the reveal never starts on a blank frame. */
export function initHero() {
  const root = document.documentElement;
  const poster = document.querySelector(".hero__poster");
  const video = document.querySelector(".hero__video");
  const ready = () => root.classList.add("is-ready");

  const posterReady = poster && !poster.complete
    ? new Promise((r) => { poster.addEventListener("load", r, { once: true }); poster.addEventListener("error", r, { once: true }); })
    : Promise.resolve();
  const fontsReady = document.fonts ? document.fonts.ready : Promise.resolve();
  Promise.race([Promise.all([posterReady, fontsReady]), new Promise((r) => setTimeout(r, 1800))]).then(ready);

  if (video) {
    video.addEventListener("playing", () => video.classList.add("is-playing"), { once: true });
  }
}

/** Reveal anything with .reveal / .event / .tile / .program__item / .photo[data-cine] / .film */
export function initReveals(scope = document) {
  const selector = ".reveal, .event, .tile, .program__item, .photo[data-cine], .film";
  const items = [...scope.querySelectorAll(selector)].filter((el) => !el.classList.contains("is-in"));
  if (reducedMotion) {
    items.forEach((el) => el.classList.add("is-in"));
    return;
  }
  // A fully clipped element (mask reveals) never reports as intersecting,
  // so those are triggered by their parent instead.
  const groups = new Map();
  items.forEach((el) => {
    const watch = el.dataset.reveal === "mask" && el.parentElement ? el.parentElement : el;
    if (!groups.has(watch)) groups.set(watch, []);
    groups.get(watch).push(el);
  });
  onceInView([...groups.keys()], (watch) => groups.get(watch).forEach((el) => el.classList.add("is-in")));
}

/** Desktop-only cursor: small ring, grows on interactive elements, "View" over photos. */
export function initCursor() {
  const cursor = document.querySelector(".cursor");
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!cursor || !fine || reducedMotion) return;
  document.documentElement.classList.add("has-cursor");
  cursor.classList.add("is-hidden");

  let x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y, raf = 0;
  const loop = () => {
    cx += (x - cx) * 0.22;
    cy += (y - cy) * 0.22;
    cursor.style.transform = `translate3d(${cx.toFixed(1)}px, ${cy.toFixed(1)}px, 0)`;
    raf = Math.abs(x - cx) + Math.abs(y - cy) > 0.1 ? requestAnimationFrame(loop) : 0;
  };
  window.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse") return;
    x = e.clientX; y = e.clientY;
    cursor.classList.remove("is-hidden");
    if (!raf) raf = requestAnimationFrame(loop);
  }, { passive: true });
  document.addEventListener("pointerleave", () => cursor.classList.add("is-hidden"));
  document.addEventListener("pointerover", (e) => {
    const t = e.target;
    cursor.classList.toggle("is-view", !!t.closest(".tile__btn"));
    cursor.classList.toggle("is-hover", !!t.closest("a, button, input, textarea, label, select"));
  });
}
