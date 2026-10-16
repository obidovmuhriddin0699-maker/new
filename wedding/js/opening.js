/* ==========================================================================
   opening.js — the "Taklifnomani ochish" gate.
   Before opening: page locked at the top behind a lace envelope, everything
   after the opening is inert. On tapping the wax seal: music starts (inside
   the user gesture), the flap opens, the card rises and the view zooms into
   it; the hero arch draws itself and the names are written in. The page then
   unlocks; a #section deep link is honoured.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;
  var opened = false;
  var hidden = [];

  function setInert(on) {
    if (on) {
      hidden = L.$$("#main > section:not(#opening), .footer");
      hidden.forEach(function (el) {
        el.setAttribute("inert", "");
        el.setAttribute("aria-hidden", "true");
      });
    } else {
      hidden.forEach(function (el) {
        el.removeAttribute("inert");
        el.removeAttribute("aria-hidden");
      });
      hidden = [];
    }
  }

  /** A #section in the URL (other than the opening) to show once the curtain parts. */
  function targetFromHash() {
    var id = (window.location.hash || "").slice(1);
    var el = id && id !== "opening" ? document.getElementById(id) : null;
    return el && el.closest("#main") ? el : null;
  }

  function open(options) {
    if (opened) return;
    opened = true;
    options = options || {};
    var root = document.documentElement;
    var reduced = L.reducedMotion();

    // Must run synchronously inside the click so browsers allow playback.
    if (options.music !== false && L.audio) L.audio.start();
    else if (L.audio) L.audio.reveal();

    // The envelope opens (CSS) and the hero comes alive.
    root.classList.add("is-opened");
    document.dispatchEvent(new CustomEvent("invitation:open"));

    var target = options.target || targetFromHash();
    window.setTimeout(function () {
      root.classList.remove("is-locked");
      setInert(false);
      window.dispatchEvent(new Event("scroll"));
      if (target) {
        root.style.scrollBehavior = "auto";
        target.scrollIntoView({ block: "start" });
        root.style.scrollBehavior = "";
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
      } else {
        document.getElementById("opening-title").focus({ preventScroll: true });
      }
    }, reduced ? 0 : 2600); // after the envelope has opened and zoomed into the card
  }

  window.LITC.opening = {
    init: function () {
      var root = document.documentElement;
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      window.scrollTo(0, 0);
      root.classList.add("is-locked");
      setInert(true);
      // Browsers may still jump to a #fragment after load; keep the gate at the top.
      function pin() { if (!opened && window.scrollY !== 0) window.scrollTo(0, 0); }
      window.addEventListener("load", pin);
      window.addEventListener("scroll", pin, { passive: true });

      L.$("[data-open-invitation]").addEventListener("click", function () { open(); });

      // The skip link opens the invitation too (without music: it isn't a request for sound).
      L.$(".skip-link").addEventListener("click", function (e) {
        if (opened) return;
        e.preventDefault();
        open({ music: false, target: document.getElementById("taklif") });
      });
    },
    open: open,
    isOpen: function () { return opened; }
  };
})();
