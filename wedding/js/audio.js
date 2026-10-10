/* ==========================================================================
   audio.js — background music.
   • Never starts on its own: start() is only called from the guest's click.
   • preload="none": the file is not downloaded until the guest opens the invitation.
   • Missing / unsupported file → the toggle says so instead of pretending to play.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  var audio = null;
  var button = null;
  var label = null;
  var state = "idle";          // idle | playing | paused | unavailable
  var wantPlaying = false;     // the guest's intent (survives tab switches)
  var resumeOnVisible = false;
  var fadeFrame = 0;
  var targetVolume = 0.4;
  var revealed = false;        // the toggle appears only after the invitation is opened

  function setState(next, message) {
    state = next;
    if (!button) return;
    button.hidden = !revealed;
    button.classList.toggle("is-unavailable", next === "unavailable");
    button.setAttribute("aria-pressed", next === "playing" ? "true" : "false");
    if (next === "unavailable") {
      button.setAttribute("aria-disabled", "true");
      button.setAttribute("aria-label", message || "Musiqa mavjud emas");
      label.textContent = "Musiqa yo‘q";
      button.title = message || "Musiqa fayli topilmadi";
    } else {
      button.removeAttribute("aria-disabled");
      button.setAttribute("aria-label", next === "playing" ? "Musiqani o‘chirish" : "Musiqani yoqish");
      label.textContent = next === "playing" ? "Musiqa" : "Musiqa o‘chiq";
      button.removeAttribute("title");
    }
  }

  function fadeTo(volume, ms, done) {
    cancelAnimationFrame(fadeFrame);
    var from = audio.volume;
    var start = performance.now();
    (function step(now) {
      var t = Math.min(1, (now - start) / ms);
      try { audio.volume = from + (volume - from) * t; } catch (e) { /* iOS: volume is read-only */ }
      if (t < 1) fadeFrame = requestAnimationFrame(step);
      else if (done) done();
    })(start);
  }

  function markUnavailable(reason) {
    if (state === "unavailable") return;
    console.warn("[taklifnoma] Background music unavailable: " + reason);
    wantPlaying = false;
    setState("unavailable", "Musiqa mavjud emas");
  }

  function play() {
    if (!audio || state === "unavailable") return Promise.resolve(false);
    wantPlaying = true;
    try { audio.volume = 0; } catch (e) { /* iOS */ }
    var attempt;
    try { attempt = audio.play(); } catch (err) { attempt = Promise.reject(err); }
    return Promise.resolve(attempt).then(function () {
      setState("playing");
      fadeTo(targetVolume, 1800);
      return true;
    }).catch(function (err) {
      if (err && err.name === "NotAllowedError") {
        // The browser refused (no user gesture). Leave it off; the toggle still works.
        wantPlaying = false;
        setState("paused");
      } else if (err && err.name === "AbortError") {
        // Interrupted by a pause() — not an error.
      } else {
        markUnavailable(err && err.name ? err.name : "playback failed");
      }
      return false;
    });
  }

  function pause(fromUser) {
    if (!audio || state === "unavailable") return;
    if (fromUser) wantPlaying = false;
    setState("paused");
    fadeTo(0, 450, function () { audio.pause(); });
  }

  window.LITC.audio = {
    init: function () {
      var cfg = L.view.cfg;
      button = L.$("[data-music-toggle]");
      label = L.$("[data-music-label]");
      targetVolume = Math.max(0, Math.min(1, Number(cfg.musicVolume) || 0.4));

      if (!cfg.backgroundMusic) {
        button.remove();
        button = null;
        return;
      }

      audio = new Audio();
      audio.preload = "none";
      audio.loop = true;
      audio.setAttribute("playsinline", "");
      var type = /\.m4a$|\.mp4$|\.aac$/i.test(cfg.backgroundMusic) ? 'audio/mp4; codecs="mp4a.40.2"' : "";
      if (type && audio.canPlayType(type) === "") {
        markUnavailable("this browser cannot play " + type);
        return;
      }
      audio.src = encodeURI(cfg.backgroundMusic);
      audio.addEventListener("error", function () {
        var code = audio.error ? audio.error.code : 0;
        markUnavailable(code === 4 ? "file missing or unsupported (" + cfg.backgroundMusic + ")" : "media error " + code);
      });

      button.addEventListener("click", function () {
        if (state === "unavailable") return;
        if (state === "playing") pause(true);
        else play();
      });

      // Pause while the tab is hidden; resume only if the guest had it playing.
      document.addEventListener("visibilitychange", function () {
        if (document.hidden && state === "playing") {
          resumeOnVisible = true;
          audio.pause();
          setState("paused");
        } else if (!document.hidden && resumeOnVisible && wantPlaying) {
          resumeOnVisible = false;
          play();
        }
      });
    },

    /** Called synchronously inside the "Taklifnomani ochish" click handler. */
    start: function () {
      if (!button) return Promise.resolve(false);
      revealed = true;
      if (state === "unavailable") { setState("unavailable"); return Promise.resolve(false); }
      setState("paused");
      return play();
    },

    /** Show the toggle (paused) without playing — used when opened via the skip link. */
    reveal: function () {
      if (!button) return;
      revealed = true;
      setState(state === "unavailable" ? "unavailable" : state === "playing" ? "playing" : "paused");
    },

    state: function () { return state; }
  };
})();
