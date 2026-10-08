/* ==========================================================================
   clouds.js — every section emerges from between the clouds.

   Each [data-clouds] element receives a cloud veil (two billowing banks, a
   low band and a soft fog). When the section scrolls into view the banks
   drift apart, the fog clears and the content rises out of the mist.
   The hero veil parts once the page is ready (see animations.js → is-ready).
   Only transform and opacity are animated; veils are removed afterwards.
   ========================================================================== */
import { reducedMotion } from "./data.js";
import { onceInView } from "./inview.js";

const VEIL =
  '<span class="veil__fog"></span>' +
  '<span class="veil__cloud veil__cloud--l"></span>' +
  '<span class="veil__cloud veil__cloud--r"></span>' +
  '<span class="veil__cloud veil__cloud--b"></span>';

export function initClouds() {
  const sections = [...document.querySelectorAll("[data-clouds]")];
  if (!sections.length) return;
  if (reducedMotion) {
    sections.forEach((s) => s.classList.add("is-parted"));
    return;
  }

  sections.forEach((section) => {
    const veil = document.createElement("div");
    veil.className = "veil";
    veil.setAttribute("aria-hidden", "true");
    veil.innerHTML = VEIL;
    section.prepend(veil);
    section.classList.add("has-veil");
  });

  const part = (section) => {
    section.classList.add("is-parted");
    // free the layers once the clouds have drifted away
    setTimeout(() => section.querySelector(":scope > .veil")?.remove(), 4600);
  };

  // the hero opens when the page is ready (fonts + poster)
  const hero = sections.find((s) => s.dataset.clouds === "hero");
  if (hero) {
    const root = document.documentElement;
    const check = () => root.classList.contains("is-ready") && (part(hero), true);
    if (!check()) {
      const mo = new MutationObserver(() => { if (check()) mo.disconnect(); });
      mo.observe(root, { attributes: true, attributeFilter: ["class"] });
    }
  }

  // sections skipped by a fast fling or a menu jump are opened too (see inview.js)
  onceInView(sections.filter((s) => s !== hero), part, 0.82);

  initDrift();
}

/** The hero sinks into a slow cloud bank as you scroll — the next section rises out of it. */
function initDrift() {
  const band = document.querySelector(".hero__clouds");
  const hero = document.getElementById("home");
  if (!band || !hero) return;
  let ticking = false;
  const update = () => {
    ticking = false;
    const p = Math.min(1, Math.max(0, window.scrollY / hero.offsetHeight));
    band.style.transform = `translate3d(0, ${(-p * 22).toFixed(2)}%, 0)`;
    hero.style.setProperty("--sink", p.toFixed(3));
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
}
