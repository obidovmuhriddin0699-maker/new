/* ==========================================================================
   navigation.js — floating menu button → fullscreen menu (fade + slide)
   Focus is trapped while open, Esc closes, focus returns to the toggle.
   ========================================================================== */
import { reducedMotion } from "./data.js";

export function initNavigation() {
  const toggle = document.getElementById("menu-toggle");
  const menu = document.getElementById("menu");
  if (!toggle || !menu) return;
  const label = toggle.querySelector(".menu-toggle__label");
  const root = document.documentElement;
  let open = false;
  let closeTimer = 0;

  const focusables = () => [toggle, ...menu.querySelectorAll("a[href]")];

  function setOpen(next, { returnFocus = true } = {}) {
    if (next === open) return;
    open = next;
    clearTimeout(closeTimer);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Menyuni yopish" : "Menyuni ochish");
    if (label) label.textContent = open ? "Yopish" : "Menyu";
    root.classList.toggle("menu-open", open);
    if (open) {
      menu.hidden = false;
      void menu.offsetWidth;                      // commit the closed state before animating
      menu.classList.add("is-open");
      document.body.style.overflow = "hidden";
      menu.querySelector("a")?.focus({ preventScroll: true });
    } else {
      menu.classList.remove("is-open");
      document.body.style.overflow = "";
      closeTimer = setTimeout(() => { menu.hidden = true; }, reducedMotion ? 0 : 900);
      if (returnFocus) toggle.focus({ preventScroll: true });
    }
  }

  toggle.addEventListener("click", () => setOpen(!open));

  menu.addEventListener("click", (e) => {
    const link = e.target.closest("a[href^='#']");
    if (!link) return;
    e.preventDefault();
    const target = document.querySelector(link.getAttribute("href"));
    setOpen(false, { returnFocus: false });
    // wait for the curtain to start lifting, then glide to the section
    setTimeout(() => {
      target?.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
      target?.setAttribute("tabindex", "-1");
      target?.focus({ preventScroll: true });
    }, reducedMotion ? 0 : 250);
  });

  document.addEventListener("keydown", (e) => {
    if (!open) return;
    if (e.key === "Escape") { e.preventDefault(); setOpen(false); return; }
    if (e.key === "Tab") {
      const els = focusables();
      const i = els.indexOf(document.activeElement);
      const next = e.shiftKey ? (i <= 0 ? els.length - 1 : i - 1) : (i === els.length - 1 ? 0 : i + 1);
      e.preventDefault();
      els[next].focus();
    }
  });

  // in-page anchors outside the menu (brand, scroll hint) also glide
  document.querySelectorAll(".brand, .scroll-hint").forEach((a) => {
    a.addEventListener("click", (e) => {
      const target = document.querySelector(a.getAttribute("href"));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
    });
  });
}
