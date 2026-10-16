/* ==========================================================================
   motion.js — drives the motion-design invitation.
   • Fills names, date and place from ../config.js.
   • Splits titles into letters / words for the staggered reveals.
   • Loads the films and photos, runs the sparkle canvas.
   • Clock: with ?render the page waits for window.__motion.step(t) — every CSS
     animation, film and spark is set to exactly time t (frame-exact video);
     otherwise it plays in real time.
   ========================================================================== */
(function () {
  "use strict";
  var cfg = window.WEDDING_CONFIG || {};
  var MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
  var WEEKDAYS = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"];
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var pad = function (n) { return String(n).padStart(2, "0"); };
  var RENDER = /[?&]render\b/.test(location.search);

  // ---------- Text from config ----------
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(cfg.eventDate || "") || [0, 2026, 1, 1];
  var y = +m[1], mo = +m[2], d = +m[3];
  var groom = cfg.groom || "", bride = cfg.bride || "";
  var text = {
    groomUpper: groom.toLocaleUpperCase("uz"),
    brideUpper: bride.toLocaleUpperCase("uz"),
    initialGroom: groom.charAt(0),
    initialBride: bride.charAt(0),
    namesInline: groom + " & " + bride,
    day: pad(d),
    monthUpper: MONTHS[mo - 1].toLocaleUpperCase("uz"),
    year: String(y),
    weekdayTime: WEEKDAYS[new Date(Date.UTC(y, mo - 1, d)).getUTCDay()] + " · soat " + (cfg.eventTime || ""),
    city: cfg.venueName ? cfg.venueName : (cfg.venueCity || ""),
    dateDots: pad(d) + " · " + pad(mo) + " · " + y
  };
  $$("[data-text]").forEach(function (el) {
    var v = text[el.getAttribute("data-text")];
    if (v != null) el.textContent = v;
  });

  // ---------- Letter / word splitting ----------
  $$(".letters").forEach(function (el) {
    var t = el.textContent;
    el.setAttribute("aria-label", t);
    // Letters are grouped per word so a line never breaks inside a word.
    var i = 0;
    el.innerHTML = t.split(" ").map(function (word) {
      return '<span class="wd">' + Array.prototype.map.call(word, function (ch) {
        return '<span class="l" style="--i:' + (i++) + '"><span>' + ch.replace("&", "&amp;") + "</span></span>";
      }).join("") + "</span>";
    }).join(" ");
  });
  $$(".words").forEach(function (el) {
    el.innerHTML = el.textContent.split(/\s+/).map(function (w, i) {
      return '<span class="w" style="--i:' + i + '">' + w + "</span>";
    }).join(" ");
  });

  // ---------- Media ----------
  var images = cfg.images || {};
  $$("img[data-image]").forEach(function (img) {
    var id = img.getAttribute("data-image");
    var widths = (images[id] && images[id].widths) || [720];
    img.src = "../assets/images/" + id + "-" + Math.max.apply(null, widths) + ".webp";
  });
  var probe = document.createElement("video");
  var useMp4 = !!probe.canPlayType('video/mp4; codecs="avc1.64001F"');
  var films = $$("video[data-film]").map(function (v) {
    var id = v.getAttribute("data-film");
    v.src = "../assets/video/" + id + (useMp4 ? ".mp4" : ".webm");
    v.poster = "../assets/video/" + id + ".webp";
    v.loop = true;
    v.muted = true;
    v.preload = "auto";
    // The film's on-screen window comes from its scene / chapter timing.
    var holder = v.closest(".chapter") || v.closest(".scene");
    var st = getComputedStyle(holder);
    return {
      el: v,
      start: parseFloat(v.getAttribute("data-start")) || 0,
      from: parseFloat(st.getPropertyValue("--at")) || 0,
      to: (parseFloat(st.getPropertyValue("--out")) || 99) + 1
    };
  });

  // ---------- Sparkles: dust, crystal glints, sparkler fountains ----------
  var canvas = document.getElementById("sparks");
  var ctx = canvas.getContext("2d");
  var DPR = RENDER ? 2.5 : Math.min(window.devicePixelRatio || 1, 2.5);
  var W = 432, H = 768;
  canvas.width = W * DPR;
  canvas.height = H * DPR;
  // Fountain windows (seconds): doors burst open, then the whole finale.
  var FOUNTAINS = [[5.45, 9.4], [41.6, 60]];

  function sprite(size, stops) {
    var c = document.createElement("canvas");
    c.width = c.height = size;
    var g = c.getContext("2d");
    var gr = g.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    stops.forEach(function (s) { gr.addColorStop(s[0], s[1]); });
    g.fillStyle = gr;
    g.fillRect(0, 0, size, size);
    return c;
  }
  var glow = sprite(64, [[0, "rgba(255,248,224,1)"], [0.18, "rgba(240,212,146,0.9)"], [0.45, "rgba(201,158,70,0.28)"], [1, "rgba(201,158,70,0)"]]);
  var star = (function () {
    var c = sprite(96, [[0, "rgba(255,255,255,1)"], [0.14, "rgba(255,240,210,0.5)"], [0.3, "rgba(255,240,210,0)"]]);
    var g = c.getContext("2d");
    g.globalCompositeOperation = "lighter";
    [[96, 3], [3, 96]].forEach(function (dd) {
      var r = g.createRadialGradient(48, 48, 0, 48, 48, 48);
      r.addColorStop(0, "rgba(255,252,240,0.95)");
      r.addColorStop(1, "rgba(255,230,180,0)");
      g.fillStyle = r;
      g.beginPath();
      g.ellipse(48, 48, dd[0] / 2, dd[1] / 2, 0, 0, Math.PI * 2);
      g.fill();
    });
    return c;
  })();
  function hash(k, s) { var x = Math.sin(k * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); }

  var dust = [], stars = [];
  for (var i = 0; i < 46; i++) {
    dust.push({ x: hash(i, 1), y: hash(i, 2), speed: 6 + hash(i, 3) * 18, sway: 6 + hash(i, 4) * 22,
      swayF: 0.15 + hash(i, 5) * 0.35, size: 2 + hash(i, 6) * 7, tw: 0.6 + hash(i, 7) * 1.8, ph: hash(i, 8) * 6.28, a: 0.35 + hash(i, 9) * 0.55 });
  }
  for (var j = 0; j < 22; j++) {
    stars.push({ x: hash(j, 11), y: hash(j, 12) * 0.9, size: 12 + hash(j, 13) * 24, period: 2.4 + hash(j, 14) * 3.6, ph: hash(j, 15) * 10 });
  }

  function fountainLevel(t) {
    for (var f = 0; f < FOUNTAINS.length; f++) {
      var a = t - FOUNTAINS[f][0], len = FOUNTAINS[f][1] - FOUNTAINS[f][0];
      if (a >= 0 && a <= len) return Math.min(1, a / 0.3, (len - a) / 1.2 + 0.0001);
    }
    return 0;
  }

  function drawSparks(t) {
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";
    // Dust: gentler in the bright story scene.
    var dustLevel = t > 18 && t < 30 ? 0.25 : 1;
    dust.forEach(function (p) {
      var span = H + 40;
      var yy = ((p.y * span - p.speed * t) % span + span) % span - 20;
      var xx = p.x * W + Math.sin(t * p.swayF + p.ph) * p.sway;
      var s1 = Math.sin(t * p.tw + p.ph);
      var a = dustLevel * p.a * (0.45 + 0.55 * s1 * s1) * Math.min(1, yy / (H * 0.25));
      if (a <= 0.01) return;
      ctx.globalAlpha = a;
      var s = p.size * 2.2;
      ctx.drawImage(glow, xx - s / 2, yy - s / 2, s, s);
    });
    // Crystal glints.
    stars.forEach(function (st) {
      var ph = ((t + st.ph) % st.period) / st.period;
      var flare = ph < 0.22 ? Math.sin((ph / 0.22) * Math.PI) : 0;
      if (flare <= 0.02 || (t > 18 && t < 30)) return;
      ctx.globalAlpha = flare * 0.95;
      var s = st.size * (0.6 + 0.6 * flare);
      ctx.drawImage(star, st.x * W - s / 2, st.y * H - s / 2, s, s);
    });
    // Sparkler fountains (each spark is a pure function of its birth time).
    var rate = 150, life = 1.5, g = H * 0.62;
    ctx.lineCap = "round";
    for (var jet = 0; jet < 2; jet++) {
      var x0 = W * (jet === 0 ? 0.1 : 0.9), y0 = H * 1.01;
      for (var k = Math.floor((t - life) * rate); k <= Math.floor(t * rate); k++) {
        var born = k / rate, age = t - born;
        if (age < 0 || age > life) continue;
        var r1 = hash(k, jet + 21), r2 = hash(k, jet + 28), r3 = hash(k, jet + 34);
        if (r3 > fountainLevel(born)) continue;
        var vy = -(H * (0.95 + 0.4 * r1));
        var vx = (r2 - 0.5) * W * 0.16 + (jet === 0 ? 1 : -1) * W * 0.02;
        var xx = x0 + vx * age, yy = y0 + vy * age + 0.5 * g * age * age;
        var pa = age - 0.035;
        var px = x0 + vx * pa, py = y0 + vy * pa + 0.5 * g * pa * pa;
        var fade = 1 - age / life;
        ctx.globalAlpha = Math.max(0, fade) * (0.55 + 0.45 * r3);
        ctx.strokeStyle = r1 > 0.7 ? "#FFFFFF" : "#FFE4AA";
        ctx.lineWidth = 1.1 + 1.2 * fade;
        ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(xx, yy); ctx.stroke();
        if (r2 > 0.85) { var s = 6 + 10 * fade; ctx.drawImage(glow, xx - s / 2, yy - s / 2, s, s); }
      }
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";
  }

  // ---------- Clock ----------
  function filmTime(f, t) {
    var dur = f.el.duration || 1;
    return Math.max(0, t - f.start) % dur;
  }

  var ready = Promise.all([
    document.fonts ? document.fonts.ready : Promise.resolve(),
    Promise.all($$("img[data-image]").map(function (img) {
      return img.complete ? 0 : new Promise(function (r) { img.onload = img.onerror = r; });
    })),
    Promise.all(films.map(function (f) {
      return f.el.readyState >= 2 ? 0 : new Promise(function (r) {
        f.el.addEventListener("loadeddata", r, { once: true });
        f.el.addEventListener("error", r, { once: true });
      });
    }))
  ]);

  if (RENDER) {
    window.__motion = {
      ready: ready,
      /** Put every animation, film and spark at exactly t seconds. */
      step: function (t) {
        document.getAnimations().forEach(function (a) { a.pause(); a.currentTime = t * 1000; });
        drawSparks(t);
        return Promise.all(films.map(function (f) {
          if (t < f.from - 0.2 || t > f.to) return 0;
          return new Promise(function (done) {
            var timer = setTimeout(done, 1500);
            f.el.addEventListener("seeked", function () { clearTimeout(timer); done(); }, { once: true });
            f.el.currentTime = filmTime(f, t);
          });
        }));
      }
    };
  } else {
    var t0 = null;
    ready.then(function () {
      document.getAnimations().forEach(function (a) { a.currentTime = 0; a.play(); });
      t0 = performance.now();
      (function frame() {
        var t = (performance.now() - t0) / 1000;
        drawSparks(t);
        films.forEach(function (f) {
          var on = t >= f.from - 0.2 && t <= f.to;
          if (on && f.el.paused) { f.el.currentTime = filmTime(f, t); f.el.play().catch(function () {}); }
          if (!on && !f.el.paused) f.el.pause();
        });
        requestAnimationFrame(frame);
      })();
    });
  }
})();
