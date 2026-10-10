/* ==========================================================================
   motion.js — scroll reveals (IntersectionObserver), layered parallax,
   story-line progress and the top bar's scroll behaviour.
   One passive scroll listener + requestAnimationFrame; transforms only.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  function initReveals() {
    var items = L.$$(".reveal");
    if (!("IntersectionObserver" in window) || L.reducedMotion()) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });

    // Stagger siblings that enter together (e.g. a heading and its lead).
    items.forEach(function (el) {
      if (!el.style.getPropertyValue("--delay")) {
        var siblings = el.parentElement ? L.$$(":scope > .reveal", el.parentElement) : [];
        var index = siblings.indexOf(el);
        if (index > 0) el.style.setProperty("--delay", Math.min(index, 5) * 0.09 + "s");
      }
      io.observe(el);
    });
  }

  function initScrollEffects() {
    var opening = L.$("[data-opening]");
    var layers = L.$$(".opening [data-depth]");
    var stage = L.$("[data-opening-stage]");
    var finalePhoto = L.$(".finale__photo");
    var finale = L.$(".finale");
    var timeline = L.$(".timeline");
    var progress = L.$("[data-story-progress]");
    var topbar = L.$("[data-topbar]");
    var reduced = L.reducedMotion();
    var lastY = window.scrollY;
    var ticking = false;
    var pointer = { x: 0, y: 0 };

    function update() {
      ticking = false;
      var y = window.scrollY;
      var vh = window.innerHeight;

      if (!reduced) {
        // Opening: each layer moves at its own depth → natural parallax.
        var openH = opening.offsetHeight;
        if (y < openH * 1.2) {
          layers.forEach(function (el) {
            var depth = parseFloat(el.getAttribute("data-depth")) || 0;
            el.style.setProperty("--py", (y * depth + pointer.y * depth * 18).toFixed(1) + "px");
            el.style.setProperty("--px", (pointer.x * depth * -26).toFixed(1) + "px");
          });
          // Names and photo drift together (never overlapping) and fade into the sky.
          stage.style.setProperty("--py", (y * 0.3).toFixed(1) + "px");
          stage.style.opacity = Math.max(0, 1 - y / (openH * 0.85)).toFixed(3);
        }
        // Final scene photograph drifts slower than the page.
        if (finalePhoto && finale) {
          var r = finale.getBoundingClientRect();
          if (r.top < vh && r.bottom > 0) {
            // Clamped so the photo never drifts past its 8% bleed.
            var t = Math.max(-1, Math.min(1, (r.top + r.height / 2 - vh / 2) / vh));
            var bleed = finalePhoto.offsetHeight * 0.06;
            finalePhoto.style.setProperty("--py", (t * -bleed).toFixed(1) + "px");
          }
        }
      }

      // Story line fills as the reader moves through the chapters.
      if (timeline && progress) {
        var tr = timeline.getBoundingClientRect();
        var p = (vh * 0.6 - tr.top) / tr.height;
        progress.style.setProperty("--progress", Math.max(0, Math.min(1, p)).toFixed(3));
      }

      // Top bar: glassy once past the opening, tucked away while scrolling down.
      if (topbar) {
        var past = y > vh * 0.6;
        topbar.classList.toggle("is-solid", past);
        var delta = y - lastY;
        // Hide only on a genuine downward scroll — not on jumps (opening, menu links).
        if (past && delta > 4 && delta < vh * 0.5 && !document.documentElement.classList.contains("is-scroll-locked")) {
          topbar.classList.add("is-hidden");
        } else if (delta < -4 || !past || delta >= vh * 0.5) {
          topbar.classList.remove("is-hidden");
        }
      }
      lastY = y;
    }

    function request() {
      if (!ticking) { ticking = true; window.requestAnimationFrame(update); }
    }

    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request, { passive: true });

    // Gentle pointer parallax on devices with a fine pointer (desktop).
    if (!reduced && window.matchMedia && window.matchMedia("(pointer: fine)").matches) {
      opening.addEventListener("pointermove", function (e) {
        pointer.x = e.clientX / window.innerWidth - 0.5;
        pointer.y = e.clientY / window.innerHeight - 0.5;
        request();
      }, { passive: true });
    }
    update();
  }

  /** Pause cloud drift in scenes that are off screen (saves battery on phones). */
  function initCloudPausing() {
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { e.target.classList.toggle("is-offscreen", !e.isIntersecting); });
    }, { rootMargin: "100px 0px" });
    L.$$(".opening, .countdown, .finale").forEach(function (el) { io.observe(el); });
  }

  window.LITC.motion = {
    init: function () {
      initReveals();
      initScrollEffects();
      initCloudPausing();
    }
  };
})();
