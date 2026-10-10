/* ==========================================================================
   nav.js — full-screen section menu (focus trap, Esc, returns focus).
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  window.LITC.nav = {
    init: function () {
      var menu = L.$("[data-menu]");
      var openBtn = L.$("[data-menu-open]");
      var closeBtn = L.$("[data-menu-close]");
      var release = null;

      function open() {
        menu.hidden = false;
        // Next frame so the opacity transition runs.
        requestAnimationFrame(function () { menu.classList.add("is-open"); });
        openBtn.setAttribute("aria-expanded", "true");
        L.lockScroll(true);
        release = L.trapFocus(menu);
        closeBtn.focus();
      }

      function close(returnFocus) {
        if (menu.hidden) return;
        menu.classList.remove("is-open");
        openBtn.setAttribute("aria-expanded", "false");
        L.lockScroll(false);
        if (release) release();
        window.setTimeout(function () { menu.hidden = true; }, L.reducedMotion() ? 0 : 450);
        if (returnFocus !== false) openBtn.focus();
      }

      openBtn.addEventListener("click", open);
      closeBtn.addEventListener("click", function () { close(); });
      menu.addEventListener("click", function (e) {
        var link = e.target.closest("a[href^='#']");
        if (!link) return;
        var target = document.querySelector(link.getAttribute("href"));
        close(false);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: L.reducedMotion() ? "auto" : "smooth", block: "start" });
          if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
          target.focus({ preventScroll: true });
        }
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !menu.hidden) close();
      });
    }
  };
})();
