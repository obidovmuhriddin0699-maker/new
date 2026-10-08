/* ==========================================================================
   gallery.js — editorial masonry built from wedding.json, wired to the lightbox.
   ========================================================================== */
import { picture } from "./data.js";
import { createLightbox } from "./lightbox.js";

export function initGallery(items) {
  const grid = document.getElementById("gallery-grid");
  if (!grid || !items?.length) return;

  grid.innerHTML = items.map((item, i) => `
    <li class="tile" style="--ratio:${item.ratio}">
      <button class="tile__btn" type="button" data-index="${i}" aria-label="Suratni ochish, ${i + 1} / ${items.length}: ${item.alt}">
        <figure class="photo" data-cine>${picture(item, { sizes: "(min-width: 1024px) 31vw, (min-width: 768px) 46vw, 92vw" })}</figure>
      </button>
      <p class="tile__caption" aria-hidden="true">${String(i + 1).padStart(2, "0")}</p>
    </li>`).join("");

  const lightbox = createLightbox(items);
  grid.addEventListener("click", (e) => {
    const btn = e.target.closest(".tile__btn");
    if (btn) lightbox.open(+btn.dataset.index, btn);
  });
}
