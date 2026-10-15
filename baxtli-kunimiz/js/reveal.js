/* ==========================================================================
   reveal.js — content floats in as it reaches the screen (once).
   Script headings "write themselves" with a soft whoosh; the calendar day
   gives a quiet heartbeat. Sounds are throttled so scrolling stays calm.
   ========================================================================== */
import { reducedMotion } from "./data.js";
import { onceInView } from "./inview.js";
import { play } from "./sfx.js";

let lastSound = 0;
function soft(name, opts) {
  const now = performance.now();
  if (now - lastSound < 2200) return;
  lastSound = now;
  play(name, opts);
}

export function initReveals() {
  const items = [...document.querySelectorAll(".page .reveal, .gallery__item, .timeline__item, .calendar")]
    .filter((el) => !el.closest(".hero"));          // the hero waits for the envelope (revealHero)
  if (reducedMotion) { items.forEach((el) => el.classList.add("is-in")); return; }

  // stagger siblings that arrive together
  let batch = 0, batchTimer = 0;
  onceInView(items, (el) => {
    el.style.setProperty("--d", `${Math.min(batch, 5) * 0.09}s`);
    batch++;
    clearTimeout(batchTimer);
    batchTimer = setTimeout(() => { batch = 0; }, 120);
    el.classList.add("is-in");
    if (el.classList.contains("title")) soft("whoosh", { volume: 0.35 });
    if (el.classList.contains("calendar")) setTimeout(() => play("heartbeat", { volume: 0.55 }), 900);
  }, 0.9);
}

/** Hero content waits for the envelope; called when the intro finishes. */
export function revealHero() {
  document.querySelectorAll(".hero .reveal").forEach((el, i) => {
    el.style.setProperty("--d", `${0.15 + i * 0.16}s`);
    el.classList.add("is-in");
  });
}
