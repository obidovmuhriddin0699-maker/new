/* ==========================================================================
   countdown.js — real-time countdown to the wedding (Asia/Tashkent).
   Ticks on the start of each real second; numbers only, no cards.
   ========================================================================== */
import { reducedMotion } from "./data.js";

const pad = (n) => String(n).padStart(2, "0");

export function initCountdown(target) {
  const section = document.getElementById("countdown");
  const done = document.getElementById("countdown-done");
  if (!section || !(target instanceof Date)) return;
  const units = {};
  section.querySelectorAll("[data-unit]").forEach((el) => { units[el.dataset.unit] = el; });
  let timer = 0;

  function render() {
    const diff = target.getTime() - Date.now();
    if (diff <= 0) {
      section.classList.add("is-done");
      if (done) done.hidden = false;
      return;
    }
    const s = Math.floor(diff / 1000);
    const values = {
      days: pad(Math.floor(s / 86400)),
      hours: pad(Math.floor((s % 86400) / 3600)),
      minutes: pad(Math.floor((s % 3600) / 60)),
      seconds: pad(s % 60)
    };
    for (const key in values) {
      const el = units[key];
      if (!el || el.textContent === values[key]) continue;
      el.textContent = values[key];
      if (!reducedMotion) { el.classList.remove("tick"); void el.offsetWidth; el.classList.add("tick"); }
    }
    timer = setTimeout(render, 1000 - (Date.now() % 1000) + 5);
  }
  render();
  return () => clearTimeout(timer);
}
