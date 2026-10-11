/* ==========================================================================
   video.js — the silent background films.
   • A film's file is fetched only when it comes near the screen (data-video →
     src), plays while visible and pauses when it leaves.
   • Posters stay instead of motion with prefers-reduced-motion, Save-Data, or
     when the browser refuses autoplay (e.g. iOS Low Power Mode).
   • A missing or broken file simply leaves the poster — never a black box.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  function allowMotion() {
    var saveData = navigator.connection && navigator.connection.saveData;
    return !L.reducedMotion() && !saveData;
  }

  /** H.264 MP4 everywhere it decodes (Safari/iOS need it); VP9 WebM otherwise. */
  var mp4 = null;
  function source(video) {
    if (mp4 === null) mp4 = !!video.canPlayType('video/mp4; codecs="avc1.64001F"');
    var webm = video.getAttribute("data-video-webm");
    return !mp4 && webm && video.canPlayType('video/webm; codecs="vp9"') ? webm : video.getAttribute("data-video");
  }

  function load(video) {
    if (video.src || !video.getAttribute("data-video")) return;
    video.src = source(video);
    video.preload = "auto";
  }

  function play(video) {
    if (video.getAttribute("data-video-failed")) return;
    load(video);
    var p;
    try { p = video.play(); } catch (e) { p = null; }
    if (p && p.catch) {
      p.catch(function (err) {
        // Autoplay refused (low-power mode) — the poster remains, which is fine.
        if (err && err.name !== "AbortError") console.info("[taklifnoma] Film stays on its poster:", err.name);
      });
    }
  }

  window.LITC.video = {
    init: function () {
      var videos = L.$$("video[data-video]");
      if (!videos.length) return;

      videos.forEach(function (v) {
        v.muted = true; // required for autoplay on every mobile browser
        v.addEventListener("error", function () {
          v.setAttribute("data-video-failed", "");
          console.warn("[taklifnoma] Film could not be played, showing its poster: " + v.currentSrc);
        });
      });

      if (!allowMotion()) return; // posters only

      if (!("IntersectionObserver" in window)) {
        videos.forEach(play);
        return;
      }
      // Start fetching a little before the film scrolls into view.
      // Watch each film's frame, not the film: the film may be clipped mid-reveal.
      var frameOf = function (v) { return v.closest(".chapter__media, .scene__media") || v; };
      var filmIn = function (el) { return el.tagName === "VIDEO" ? el : el.querySelector("video[data-video]"); };
      var near = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { load(filmIn(e.target)); near.unobserve(e.target); }
        });
      }, { rootMargin: "600px 0px" });
      var visible = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) play(filmIn(e.target));
          else filmIn(e.target).pause();
        });
      }, { threshold: 0.05 });
      videos.forEach(function (v) { near.observe(frameOf(v)); visible.observe(frameOf(v)); });

      document.addEventListener("visibilitychange", function () {
        videos.forEach(function (v) {
          if (document.hidden) v.pause();
          else if (v.getBoundingClientRect().bottom > 0 && v.getBoundingClientRect().top < window.innerHeight) play(v);
        });
      });
    }
  };
})();
