/* ==========================================================================
   dust.js — the sparkle engine over the opening and the finale:
     • rising, twinkling gold dust
     • crystal glints (four-point stars) that flare and fade, like light on
       a chandelier
     • sparkler fountains from the bottom corners: data-fountains="burst" fires
       them for a few seconds when the doors open, "always" keeps them going
   Every particle is a pure function of time (no stored state), so motion is
   smooth at any frame rate and frame-exact in the video render. Drawing
   stops whenever the canvas is off screen; everything is off with reduced
   motion.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  function glowSprite() {
    var c = document.createElement("canvas");
    c.width = c.height = 64;
    var g = c.getContext("2d");
    var grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, "rgba(255, 248, 224, 1)");
    grad.addColorStop(0.18, "rgba(240, 212, 146, 0.9)");
    grad.addColorStop(0.45, "rgba(201, 158, 70, 0.28)");
    grad.addColorStop(1, "rgba(201, 158, 70, 0)");
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    return c;
  }

  function starSprite() {
    // A crystal glint: soft core plus two thin crossed rays.
    var c = document.createElement("canvas");
    c.width = c.height = 96;
    var g = c.getContext("2d");
    var core = g.createRadialGradient(48, 48, 0, 48, 48, 14);
    core.addColorStop(0, "rgba(255, 255, 255, 1)");
    core.addColorStop(1, "rgba(255, 240, 210, 0)");
    g.fillStyle = core;
    g.fillRect(0, 0, 96, 96);
    g.globalCompositeOperation = "lighter";
    [[96, 3], [3, 96]].forEach(function (d) {
      var ray = g.createRadialGradient(48, 48, 0, 48, 48, 48);
      ray.addColorStop(0, "rgba(255, 252, 240, 0.95)");
      ray.addColorStop(1, "rgba(255, 230, 180, 0)");
      g.fillStyle = ray;
      g.beginPath();
      g.ellipse(48, 48, d[0] / 2, d[1] / 2, 0, 0, Math.PI * 2);
      g.fill();
    });
    return c;
  }

  // Deterministic hash → [0, 1) for particle k of stream s.
  function hash(k, s) {
    var x = Math.sin(k * 127.1 + s * 311.7) * 43758.5453;
    return x - Math.floor(x);
  }

  function rand(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function Field(canvas, sprites, seed) {
    var ctx = canvas.getContext("2d");
    var mode = canvas.getAttribute("data-fountains") || "";
    var burstAt = null;
    var dust = [], stars = [];
    var w = 0, h = 0, dpr = 1;
    var visible = false;

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      var r = rand(seed);
      dust = [];
      for (var i = 0, n = Math.min(80, Math.round((w * h) / 9000)); i < n; i++) {
        dust.push({ x: r(), y: r(), speed: 6 + r() * 18, sway: 6 + r() * 22, swayF: 0.15 + r() * 0.35,
          size: 2 + r() * 7, tw: 0.6 + r() * 1.8, ph: r() * Math.PI * 2, alpha: 0.35 + r() * 0.6 });
      }
      stars = [];
      for (var j = 0, m = Math.min(26, Math.round((w * h) / 22000)); j < m; j++) {
        stars.push({ x: r(), y: r() * 0.85, size: 10 + r() * 22, period: 2.6 + r() * 4, ph: r() * 10 });
      }
    }

    function drawDust(t) {
      for (var i = 0; i < dust.length; i++) {
        var p = dust[i];
        var span = h + 40;
        var y = ((p.y * span - p.speed * t) % span + span) % span - 20;
        var x = p.x * w + Math.sin(t * p.swayF + p.ph) * p.sway;
        var s1 = Math.sin(t * p.tw + p.ph);
        var a = p.alpha * (0.45 + 0.55 * s1 * s1) * Math.min(1, y / (h * 0.25));
        if (a <= 0.01) continue;
        ctx.globalAlpha = a;
        var s = p.size * 2.2;
        ctx.drawImage(sprites.glow, x - s / 2, y - s / 2, s, s);
      }
    }

    function drawStars(t) {
      for (var i = 0; i < stars.length; i++) {
        var st = stars[i];
        // Each glint flares briefly once per period, then rests.
        var phase = ((t + st.ph) % st.period) / st.period;
        var flare = phase < 0.22 ? Math.sin((phase / 0.22) * Math.PI) : 0;
        if (flare <= 0.02) continue;
        ctx.globalAlpha = flare * 0.95;
        var s = st.size * (0.6 + 0.6 * flare);
        ctx.drawImage(sprites.star, st.x * w - s / 2, st.y * h - s / 2, s, s);
      }
    }

    /** Two sparkler jets. `intensity` 0..1 fades the emission in and out. */
    function drawFountains(t, intensity) {
      if (intensity <= 0) return;
      var rate = 150;              // sparks per second per jet
      var life = 1.5;              // seconds
      var g = h * 0.62;            // gravity, px/s²
      ctx.lineCap = "round";
      for (var jet = 0; jet < 2; jet++) {
        var x0 = w * (jet === 0 ? 0.1 : 0.9);
        var y0 = h * 1.01;
        var first = Math.floor((t - life) * rate);
        var last = Math.floor(t * rate);
        for (var k = first; k <= last; k++) {
          var born = k / rate;
          var age = t - born;
          if (age < 0 || age > life) continue;
          var r1 = hash(k, jet + seed), r2 = hash(k, jet + seed + 7), r3 = hash(k, jet + seed + 13);
          if (r3 > intensityAt(born)) continue; // emission follows the burst envelope
          var vy = -(h * (0.95 + 0.4 * r1));
          var vx = (r2 - 0.5) * w * 0.16 + (jet === 0 ? 1 : -1) * w * 0.02;
          var x = x0 + vx * age;
          var y = y0 + vy * age + 0.5 * g * age * age;
          var px = x0 + vx * (age - 0.035);
          var py = y0 + vy * (age - 0.035) + 0.5 * g * (age - 0.035) * (age - 0.035);
          var fade = 1 - age / life;
          ctx.globalAlpha = Math.max(0, fade) * (0.55 + 0.45 * r3);
          ctx.strokeStyle = r1 > 0.7 ? "rgba(255, 255, 255, 1)" : "rgba(255, 228, 170, 1)";
          ctx.lineWidth = 1.1 + 1.2 * fade;
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(x, y);
          ctx.stroke();
          if (r2 > 0.85) {
            var s = 6 + 10 * fade;
            ctx.drawImage(sprites.glow, x - s / 2, y - s / 2, s, s);
          }
        }
      }
    }

    function intensityAt(t) {
      if (mode === "always") return 1;
      if (mode !== "burst" || burstAt === null) return 0;
      var a = t - burstAt;
      if (a < 0 || a > 4.2) return 0;
      return a < 0.3 ? a / 0.3 : a > 2.8 ? Math.max(0, 1 - (a - 2.8) / 1.4) : 1;
    }

    function draw() {
      if (!visible) return;
      var t = Date.now() / 1000;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.globalCompositeOperation = "lighter";
      drawDust(t);
      drawStars(t);
      var on = mode === "always" ? 1 : intensityAt(t) || (burstAt !== null && t - burstAt < 6 ? 0.001 : 0);
      drawFountains(t, on);
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
      requestAnimationFrame(draw);
    }

    resize();
    window.addEventListener("resize", resize, { passive: true });
    if (mode === "burst") {
      document.addEventListener("invitation:open", function () { burstAt = Date.now() / 1000 + 0.35; });
    }
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
      var sprites = { glow: glowSprite(), star: starSprite() };
      L.$$("[data-dust]").forEach(function (canvas, i) { new Field(canvas, sprites, 1337 + i * 101); });
    }
  };
})();
