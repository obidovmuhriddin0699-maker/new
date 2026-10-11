/* ==========================================================================
   dust.js — slowly rising, twinkling gold dust over the opening and finale.
   Every particle's position is a pure function of time, so the animation is
   smooth at any frame rate (and frame-exact in the video render). Drawing
   stops whenever the canvas is off screen; off entirely with reduced motion.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  function sprite() {
    // One soft gold glow, drawn once and stamped for every particle.
    var c = document.createElement("canvas");
    c.width = c.height = 64;
    var g = c.getContext("2d");
    var grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, "rgba(255, 246, 214, 1)");
    grad.addColorStop(0.18, "rgba(240, 210, 140, 0.9)");
    grad.addColorStop(0.45, "rgba(201, 158, 70, 0.28)");
    grad.addColorStop(1, "rgba(201, 158, 70, 0)");
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    return c;
  }

  function rand(seed) {
    // Small deterministic PRNG (mulberry32).
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function Field(canvas, glow, seed) {
    var ctx = canvas.getContext("2d");
    var particles = [];
    var w = 0, h = 0, dpr = 1;
    var visible = false;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      var r = rand(seed);
      var count = Math.min(80, Math.round((w * h) / 9000));
      particles = [];
      for (var i = 0; i < count; i++) {
        particles.push({
          x: r(), y: r(),
          speed: 6 + r() * 18,            // px/s upward
          sway: 6 + r() * 22, swayF: 0.15 + r() * 0.35,
          size: 2 + r() * 7,              // glow diameter in px
          tw: 0.6 + r() * 1.8, ph: r() * Math.PI * 2,
          alpha: 0.35 + r() * 0.6
        });
      }
    }

    function draw() {
      if (!visible) return;
      var t = Date.now() / 1000;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        var span = h + 40;
        var y = ((p.y * span - p.speed * t) % span + span) % span - 20;
        var x = p.x * w + Math.sin(t * p.swayF + p.ph) * p.sway;
        var a = p.alpha * (0.45 + 0.55 * Math.sin(t * p.tw + p.ph) * Math.sin(t * p.tw + p.ph));
        // Fade near the top so specks dissolve rather than vanish.
        a *= Math.min(1, y / (h * 0.25));
        if (a <= 0.01) continue;
        ctx.globalAlpha = a;
        var s = p.size * 2.2;
        ctx.drawImage(glow, x - s / 2, y - s / 2, s, s);
      }
      requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener("resize", resize, { passive: true });
    var io = new IntersectionObserver(function (entries) {
      var was = visible;
      visible = entries[0].isIntersecting;
      if (visible && !was) requestAnimationFrame(draw);
    });
    io.observe(canvas);
  }

  window.LITC.dust = {
    init: function () {
      if (L.reducedMotion() || !("IntersectionObserver" in window)) return;
      var glow = sprite();
      L.$$("[data-dust]").forEach(function (canvas, i) { new Field(canvas, glow, 1337 + i * 101); });
    }
  };
})();
