/* ==========================================================================
   scroll.js — one requestAnimationFrame loop for everything scroll-driven:
   the 1px progress line, the story timeline fill and the 06 → OCTOBER → 2026
   date sequence. Listeners are passive; layout is read once per frame.
   ========================================================================== */
import { reducedMotion } from "./data.js";

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

export function initScroll() {
  const root = document.documentElement;
  const progress = document.querySelector(".progress");
  const timeline = document.querySelector(".timeline");
  const date = document.getElementById("date");
  const dateLines = date ? [date.querySelector(".date__meta"), ...date.querySelectorAll(".date__line")] : [];
  const thresholds = [0.02, 0.08, 0.32, 0.56];       // meta, day, month, year

  if (reducedMotion) dateLines.forEach((el) => el?.classList.add("is-on"));

  let ticking = false;
  function update() {
    ticking = false;
    const y = window.scrollY;
    const vh = window.innerHeight;
    const max = root.scrollHeight - vh;
    progress?.style.setProperty("--progress", max > 0 ? (y / max).toFixed(4) : 0);

    if (timeline) {
      const r = timeline.getBoundingClientRect();
      timeline.style.setProperty("--story-progress", clamp((vh * 0.6 - r.top) / r.height, 0, 1).toFixed(4));
    }

    if (date && !reducedMotion) {
      const r = date.getBoundingClientRect();
      const p = clamp(-r.top / Math.max(1, r.height - vh), 0, 1);
      dateLines.forEach((el, i) => el?.classList.toggle("is-on", p >= thresholds[i] && r.top < vh * 0.5));
    }
  }
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();
}

/** Play muted background videos only while they are on screen. */
export function initMediaVisibility(videos) {
  if (!("IntersectionObserver" in window)) return;
  const saveData = navigator.connection && navigator.connection.saveData;
  const onScreen = new Set();
  const play = (v) => {
    if (reducedMotion || saveData) return;
    const p = v.play();
    if (p && p.catch) p.catch(() => { /* Low Power Mode: poster stays */ });
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (isIntersecting) { onScreen.add(target); play(target); }
      else { onScreen.delete(target); target.pause(); }
    });
  }, { rootMargin: "150px 0px" });
  videos.forEach((v) => io.observe(v));
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) videos.forEach((v) => v.pause());
    else onScreen.forEach(play);
  });
}
