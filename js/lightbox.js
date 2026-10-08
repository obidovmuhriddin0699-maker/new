/* ==========================================================================
   lightbox.js — fullscreen photo viewer.
   Next / previous / close, keyboard (← → Esc), swipe, pinch-zoom,
   double-tap zoom, drag-to-pan while zoomed, swipe down to close.
   ========================================================================== */
import { largest, reducedMotion } from "./data.js";

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

export function createLightbox(items) {
  const box = document.getElementById("lightbox");
  const stage = document.getElementById("lightbox-stage");
  const img = document.getElementById("lightbox-img");
  const count = document.getElementById("lightbox-count");
  const caption = document.getElementById("lightbox-caption");
  if (!box || !img || !items.length) return { open() {} };

  let index = 0, lastTrigger = null, closeTimer = 0;
  // zoom / pan state
  let scale = 1, tx = 0, ty = 0;
  const pointers = new Map();
  let gesture = null;
  let lastTap = 0;

  const apply = (animate) => {
    img.style.transition = animate && !reducedMotion ? "transform 0.35s cubic-bezier(.16,1,.3,1)" : "none";
    img.style.transform = `translate3d(${tx}px, ${ty}px, 0) scale(${scale})`;
  };
  const resetZoom = (animate) => { scale = 1; tx = 0; ty = 0; apply(animate); };
  const bounds = () => {
    const r = img.getBoundingClientRect(), s = stage.getBoundingClientRect();
    const w = (r.width / scale) * scale, h = (r.height / scale) * scale;
    const mx = Math.max(0, (w - s.width) / 2), my = Math.max(0, (h - s.height) / 2);
    tx = clamp(tx, -mx, mx); ty = clamp(ty, -my, my);
  };

  function show(i, dir = 0) {
    index = (i + items.length) % items.length;
    const item = items[index];
    resetZoom(false);
    const swap = () => {
      img.src = largest(item);
      img.alt = item.alt || "";
      img.classList.remove("is-swapping");
    };
    if (dir && !reducedMotion) { img.classList.add("is-swapping"); setTimeout(swap, 180); }
    else swap();
    count.textContent = `${index + 1} / ${items.length}`;
    caption.textContent = item.alt || "";
    // warm the neighbours
    [index + 1, index - 1].forEach((n) => { const p = new Image(); p.src = largest(items[(n + items.length) % items.length]); });
  }

  function open(i, trigger) {
    clearTimeout(closeTimer);
    lastTrigger = trigger || document.activeElement;
    box.hidden = false;
    void box.offsetWidth;
    box.classList.add("is-open");
    document.body.style.overflow = "hidden";
    show(i);
    box.querySelector("[data-lb='close']").focus({ preventScroll: true });
  }

  function close() {
    box.classList.remove("is-open");
    document.body.style.overflow = "";
    closeTimer = setTimeout(() => { box.hidden = true; img.removeAttribute("src"); }, reducedMotion ? 0 : 500);
    lastTrigger?.focus({ preventScroll: true });
  }

  box.addEventListener("click", (e) => {
    const action = e.target.closest("[data-lb]")?.dataset.lb;
    if (action === "close") close();
    else if (action === "next") show(index + 1, 1);
    else if (action === "prev") show(index - 1, -1);
  });

  document.addEventListener("keydown", (e) => {
    if (box.hidden) return;
    if (e.key === "Escape") { e.preventDefault(); close(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1, 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1, -1); }
    else if (e.key === "Tab") {
      const els = [...box.querySelectorAll("button")];
      const i = els.indexOf(document.activeElement);
      e.preventDefault();
      els[(i + (e.shiftKey ? -1 : 1) + els.length) % els.length].focus();
    }
  });

  /* ---- pointer gestures on the stage ---- */
  stage.addEventListener("pointerdown", (e) => {
    stage.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      gesture = { type: "pinch", d0: Math.hypot(a.x - b.x, a.y - b.y), s0: scale, tx0: tx, ty0: ty, cx: (a.x + b.x) / 2, cy: (a.y + b.y) / 2 };
    } else {
      gesture = { type: scale > 1 ? "pan" : "swipe", x0: e.clientX, y0: e.clientY, tx0: tx, ty0: ty, t0: performance.now() };
    }
  });

  stage.addEventListener("pointermove", (e) => {
    if (!pointers.has(e.pointerId) || !gesture) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (gesture.type === "pinch" && pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      scale = clamp((gesture.s0 * d) / gesture.d0, 1, 4);
      const cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
      tx = gesture.tx0 + (cx - gesture.cx); ty = gesture.ty0 + (cy - gesture.cy);
      apply(false);
    } else if (gesture.type === "pan") {
      tx = gesture.tx0 + (e.clientX - gesture.x0); ty = gesture.ty0 + (e.clientY - gesture.y0);
      bounds(); apply(false);
    } else if (gesture.type === "swipe") {
      const dx = e.clientX - gesture.x0, dy = e.clientY - gesture.y0;
      tx = dx; ty = Math.max(0, dy) * 0.6;
      img.style.opacity = String(1 - Math.min(0.6, Math.abs(dx) / 600 + ty / 500));
      apply(false);
    }
  });

  const end = (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (!gesture) return;
    if (gesture.type === "pinch") {
      if (pointers.size < 2) { if (scale <= 1.02) resetZoom(true); else { bounds(); apply(true); } gesture = null; }
      return;
    }
    if (gesture.type === "swipe") {
      const dx = e.clientX - gesture.x0, dy = e.clientY - gesture.y0;
      img.style.opacity = "";
      const moved = Math.hypot(dx, dy);
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) show(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
      else if (dy > 110) close();
      else {
        resetZoom(true);
        // tap / double-tap
        if (moved < 8 && e.target === img) {
          const now = performance.now();
          if (now - lastTap < 300) { zoomAt(e.clientX, e.clientY); lastTap = 0; } else lastTap = now;
        }
      }
    }
    gesture = null;
  };
  stage.addEventListener("pointerup", end);
  stage.addEventListener("pointercancel", end);

  function zoomAt(x, y) {
    if (scale > 1) { resetZoom(true); return; }
    const r = img.getBoundingClientRect();
    scale = 2.5;
    tx = (r.left + r.width / 2 - x) * (scale - 1);
    ty = (r.top + r.height / 2 - y) * (scale - 1);
    bounds(); apply(true);
  }
  img.addEventListener("dblclick", (e) => { if (e.pointerType !== "touch") zoomAt(e.clientX, e.clientY); });

  // desktop: ctrl/trackpad pinch zoom
  stage.addEventListener("wheel", (e) => {
    if (!e.ctrlKey) return;
    e.preventDefault();
    scale = clamp(scale * (1 - e.deltaY * 0.01), 1, 4);
    if (scale === 1) { tx = 0; ty = 0; }
    bounds(); apply(false);
  }, { passive: false });

  return { open, close };
}
