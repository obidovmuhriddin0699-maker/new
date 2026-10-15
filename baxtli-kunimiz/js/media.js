/* ==========================================================================
   media.js — muted background videos play only while visible
   (battery-friendly); the poster stays if autoplay is not allowed.
   ========================================================================== */
import { asset, reducedMotion } from "./data.js";

/** Fill a <video> with mp4 + webm sources (only what the single-file build embedded). */
export function setVideo(video, base, poster) {
  if (!video || !base) return;
  if (poster) video.poster = asset(poster);
  const sources = [[`${base}.mp4`, "video/mp4"], [`${base}.webm`, "video/webm"]].filter(([p]) => !window.__ASSETS || window.__ASSETS[p]);
  video.innerHTML = sources.map(([p, type]) => `<source src="${asset(p)}" type="${type}">`).join("");
  video.load();
}

export function playWhenVisible(videos) {
  const saveData = navigator.connection && navigator.connection.saveData;
  const onScreen = new Set();
  const play = (v) => {
    if (reducedMotion || saveData) return;
    const p = v.play();
    if (p && p.catch) p.catch(() => { /* Low Power Mode: poster stays */ });
  };
  videos.forEach((v) => v.addEventListener("playing", () => v.classList.add("is-playing"), { once: true }));
  if (!("IntersectionObserver" in window)) { videos.forEach(play); return; }
  const io = new IntersectionObserver((entries) => entries.forEach(({ target, isIntersecting }) => {
    if (isIntersecting) { onScreen.add(target); play(target); } else { onScreen.delete(target); target.pause(); }
  }), { rootMargin: "120px 0px" });
  videos.forEach((v) => io.observe(v));
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) videos.forEach((v) => v.pause()); else onScreen.forEach(play);
  });
}
