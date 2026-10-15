/* ==========================================================================
   gallery.js — "Xotiralarimiz": a framed two-column grid that opens in the
   fullscreen viewer (swipe, pinch-zoom, keyboard).
   ========================================================================== */
import { picture } from "./data.js";
import { L, t, onLang } from "./i18n.js";
import { createLightbox } from "./lightbox.js";

export function initGallery(items = []) {
  const grid = document.getElementById("gallery-grid");
  if (!grid || !items.length) return;

  grid.innerHTML = items.map((item, i) => `
    <li class="gallery__item" style="--tilt:${i % 2 ? 2 : -2}deg">
      <button class="gallery__btn" type="button" data-index="${i}">
        ${picture(item, { sizes: "(min-width: 480px) 220px, 46vw", alt: L(item.alt) })}
      </button>
    </li>`).join("");

  const labels = () => {
    grid.querySelectorAll(".gallery__btn").forEach((btn, i) => {
      btn.setAttribute("aria-label", `${t("lb_open")} ${i + 1} / ${items.length}: ${L(items[i].alt)}`);
      const img = btn.querySelector("img");
      if (img) img.alt = L(items[i].alt);
    });
  };
  labels();
  onLang(labels);

  // the viewer reads captions in the current language
  const lightbox = createLightbox(items.map((it) => ({ ...it, get alt() { return L(it.alt); } })));
  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".gallery__btn");
    if (btn) lightbox.open(+btn.dataset.index, btn);
  });
}
