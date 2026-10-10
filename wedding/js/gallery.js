/* ==========================================================================
   gallery.js — full-screen lightbox for the photo grid.
   Keyboard: ←/→ navigate, Esc closes, Tab stays inside. Touch: swipe
   left/right (pinch-zoom is left to the browser). Focus returns to the
   thumbnail that opened it. Neighbouring photos are preloaded.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  window.LITC.gallery = {
    init: function () {
      var grid = L.$('[data-slot="gallery"]');
      var box = L.$("[data-lightbox]");
      if (!grid || !grid.getAttribute("data-ids")) return;

      var ids = JSON.parse(grid.getAttribute("data-ids"));
      var images = L.view.cfg.images;
      var img = L.$("[data-lightbox-img]", box);
      var caption = L.$("[data-lightbox-caption]", box);
      var count = L.$("[data-lightbox-count]", box);
      var index = 0;
      var opener = null;
      var release = null;
      var loadToken = 0;

      function preload(i) {
        var pic = new Image();
        pic.decoding = "async";
        pic.src = L.largest(ids[(i + ids.length) % ids.length]);
      }

      function show(i, direction) {
        index = (i + ids.length) % ids.length;
        var id = ids[index];
        var token = ++loadToken;
        var reduced = L.reducedMotion();

        function swap() {
          if (token !== loadToken) return;
          img.classList.remove("is-ready", "is-leaving-left", "is-leaving-right");
          var next = new Image();
          next.onload = next.onerror = function () {
            if (token !== loadToken) return;
            img.src = next.src;
            img.alt = images[id].alt || "";
            requestAnimationFrame(function () { img.classList.add("is-ready"); });
          };
          next.src = L.largest(id);
        }

        caption.textContent = images[id].alt || "";
        count.textContent = (index + 1) + " / " + ids.length;
        if (direction && img.classList.contains("is-ready") && !reduced) {
          img.classList.add(direction > 0 ? "is-leaving-left" : "is-leaving-right");
          window.setTimeout(swap, 220);
        } else {
          swap();
        }
        preload(index + 1);
        preload(index - 1);
      }

      function open(i, trigger) {
        opener = trigger || null;
        box.hidden = false;
        L.lockScroll(true);
        release = L.trapFocus(box);
        show(i, 0);
        requestAnimationFrame(function () { box.classList.add("is-open"); });
        L.$("[data-lightbox-close].lightbox__btn", box).focus();
      }

      function close() {
        if (box.hidden) return;
        box.classList.remove("is-open");
        L.lockScroll(false);
        if (release) release();
        loadToken++;
        window.setTimeout(function () {
          box.hidden = true;
          img.classList.remove("is-ready");
          img.removeAttribute("src");
        }, L.reducedMotion() ? 0 : 450);
        if (opener) opener.focus({ preventScroll: true });
      }

      grid.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-gallery-index]");
        if (btn) open(Number(btn.getAttribute("data-gallery-index")), btn);
      });
      L.$$("[data-lightbox-close]", box).forEach(function (el) { el.addEventListener("click", close); });
      L.$("[data-lightbox-prev]", box).addEventListener("click", function () { show(index - 1, -1); });
      L.$("[data-lightbox-next]", box).addEventListener("click", function () { show(index + 1, 1); });

      document.addEventListener("keydown", function (e) {
        if (box.hidden) return;
        if (e.key === "Escape") { e.preventDefault(); close(); }
        else if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1, 1); }
        else if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1, -1); }
      });

      // Swipe: a mostly-horizontal single-finger drag of 50px or more.
      var startX = 0, startY = 0, tracking = false;
      box.addEventListener("touchstart", function (e) {
        if (e.touches.length !== 1) { tracking = false; return; }
        tracking = true;
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      }, { passive: true });
      box.addEventListener("touchend", function (e) {
        if (!tracking) return;
        tracking = false;
        var t = e.changedTouches[0];
        var dx = t.clientX - startX, dy = t.clientY - startY;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) show(index + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
        else if (dy > 90 && Math.abs(dy) > Math.abs(dx) * 1.4) close(); // swipe down to close
      }, { passive: true });
    }
  };
})();
