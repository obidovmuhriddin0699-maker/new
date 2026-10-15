/* ==========================================================================
   timeline.js — "Kechaning tartibi". A rose glides down the golden line as
   the guest scrolls; every hour it passes lights up.
   ========================================================================== */
import { L, onLang } from "./i18n.js";
import { reducedMotion } from "./data.js";

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

export function initTimeline(program = []) {
  const list = document.getElementById("program-list");
  const wrap = list?.closest(".timeline");
  const rose = wrap?.querySelector(".timeline__rose");
  if (!list || !wrap) return;

  const render = () => {
    const passed = [...list.children].map((li) => li.classList.contains("is-in"));
    list.innerHTML = program.map((p, i) => `
      <li class="timeline__item${passed[i] ? " is-in" : ""}">
        <span class="timeline__time">${p.time}</span>
        <span class="timeline__dot" aria-hidden="true"></span>
        <span class="timeline__title">${L(p)}</span>
      </li>`).join("");
  };
  render();
  onLang(render);

  let ticking = false;
  function update() {
    ticking = false;
    const r = wrap.getBoundingClientRect();
    const vh = window.innerHeight;
    // 0 when the timeline top reaches 70% of the screen, 1 when its bottom does
    const p = clamp((vh * 0.7 - r.top) / Math.max(1, r.height), 0, 1);
    const travel = Math.max(0, r.height - (rose?.offsetHeight || 34) - 4);
    wrap.style.setProperty("--tl", p.toFixed(4));
    wrap.style.setProperty("--rose-y", `${(p * travel).toFixed(1)}px`);
    const roseCenter = r.top + p * travel + 17;
    [...list.children].forEach((li) => {
      const lr = li.getBoundingClientRect();
      li.classList.toggle("is-past", roseCenter >= lr.top + lr.height / 2 - 4);
    });
  }
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  if (reducedMotion) {
    wrap.style.setProperty("--tl", "1");
    [...list.children].forEach((li) => li.classList.add("is-past"));
    return;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();
}
