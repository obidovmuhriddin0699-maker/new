/* ==========================================================================
   countdown.js — days / hours / minutes / seconds until the wedding
   (Asia/Tashkent). Each changing digit drops in softly.
   ========================================================================== */
import { pad, reducedMotion } from "./data.js";
import { t, onLang } from "./i18n.js";

export function initCountdown(target) {
  const box = document.getElementById("countdown");
  const done = document.getElementById("countdown-done");
  if (!box) return;
  const nums = {};
  box.querySelectorAll("[data-unit]").forEach((el) => { nums[el.dataset.unit] = el; });

  const labels = () => {
    const u = t("units");
    box.querySelectorAll("[data-unit-label]").forEach((el) => { el.textContent = u[+el.dataset.unitLabel]; });
  };

  function render() {
    const diff = target.getTime() - Date.now();
    if (diff <= 0) {
      box.classList.add("is-done");
      document.querySelector(".countdown__title")?.setAttribute("hidden", "");
      if (done) done.hidden = false;
      return;
    }
    const s = Math.floor(diff / 1000);
    const v = {
      days: String(Math.floor(s / 86400)).padStart(2, "0"),
      hours: pad(Math.floor((s % 86400) / 3600)),
      minutes: pad(Math.floor((s % 3600) / 60)),
      seconds: pad(s % 60)
    };
    for (const k in v) {
      const el = nums[k];
      if (!el || el.textContent === v[k]) continue;
      el.textContent = v[k];
      if (!reducedMotion) { el.classList.remove("tick"); void el.offsetWidth; el.classList.add("tick"); }
    }
    setTimeout(render, 1000 - (Date.now() % 1000) + 5);
  }
  labels();
  onLang(labels);
  render();
}
