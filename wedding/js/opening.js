/* ==========================================================================
   opening.js — the "Taklifnomani ochish" gate.
   Before opening: page locked at the top, everything after the opening is
   inert. On click: music starts (inside the user gesture), the camera flies
   through the clouds, then the page unlocks and glides to the invitation.
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

  function targetFromHash() {
    var id = (window.location.hash || "").slice(1);
    var el = id && id !== "opening" ? document.getElementById(id) : null;
    return el && el.closest("#main") ? el : document.getElementById("taklif");
  }

  function open(options) {
    if (opened) return;
    opened = true;
    var withMusic = !options || options.music !== false;
    var root = document.documentElement;
    var reduced = L.reducedMotion();

    // Must run synchronously inside the click so browsers allow playback.
    if (withMusic && L.audio) L.audio.start();
    else if (L.audio) L.audio.reveal();

    root.classList.add("is-opened");
    if (!reduced) root.classList.add("is-opening");

    var target = targetFromHash();
    // The cloud pass covers the screen at ~1 s: jump to the invitation underneath,
    // so the guest sees the clouds part onto it (no long scroll).
    window.setTimeout(function () {
      root.classList.remove("is-locked");
      setInert(false);
      root.style.scrollBehavior = "auto";
      target.scrollIntoView({ block: "start" });
      root.style.scrollBehavior = "";
      window.dispatchEvent(new Event("scroll"));
      if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    }, reduced ? 0 : 1000);
    window.setTimeout(function () { root.classList.remove("is-opening"); }, 2400);
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
        open({ music: false });
      });
    },
    open: open,
    isOpen: function () { return opened; }
  };
})();
