/* ==========================================================================
   main.js — boot sequence. Each feature starts in isolation, so one failure
   (e.g. a typo in config.js) never blanks the whole invitation.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  function safely(name, fn) {
    try { fn(); } catch (err) { console.error("[taklifnoma] " + name + " failed:", err); }
  }

  function boot() {
    try {
      L.init();
    } catch (err) {
      // Without config nothing can render; show the static page without the gate.
      console.error("[taklifnoma]", err);
      document.documentElement.classList.remove("js");
      return;
    }
    var v = L.view;

    safely("render", L.render);
    safely("audio", L.audio.init);
    safely("opening", L.opening.init);
    safely("motion", L.motion.init);
    safely("nav", L.nav.init);
    safely("countdown", L.countdown.init);
    safely("gallery", L.gallery.init);
    safely("rsvp", L.rsvp.init);

    if (v.preview) {
      var badge = L.$("[data-preview-badge]");
      badge.textContent = "Sinov rejimi · vaqt: " + v.preview.label;
      badge.hidden = false;
    }
    if (!isNaN(v.startMs) && Date.now() > v.endMs) {
      console.warn("[taklifnoma] The configured event date (" + v.cfg.eventDate + " " + v.cfg.eventTime +
        ") is in the past. Confirm or update eventDate in config.js before sharing the invitation.");
    }
    document.documentElement.classList.add("is-ready");
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
