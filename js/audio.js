/* ==========================================================================
   audio.js — background music. Starts MUTED (browsers block sound without a
   gesture); the first tap/click/key on the page starts playback with a fade,
   the floating button toggles it afterwards. m4a with an mp3 fallback.
   ========================================================================== */
import { asset } from "./data.js";

export function initAudio(data) {
  const audio = document.getElementById("audio");
  const btn = document.getElementById("sound");
  if (!audio || !btn || !data.music) return;
  const label = btn.querySelector(".sound__label");
  const target = Math.min(1, Math.max(0, data.musicVolume ?? 0.35));
  let wanted = false;          // user intent (survives tab switches)
  let fade = 0;
  let broken = false;

  const canAac = audio.canPlayType('audio/mp4; codecs="mp4a.40.2"') !== "";
  audio.src = asset(canAac || !data.musicFallback ? data.music : data.musicFallback);
  audio.volume = 0;
  btn.disabled = false;

  function ui(playing) {
    btn.classList.toggle("is-playing", playing);
    btn.setAttribute("aria-pressed", String(playing));
    btn.setAttribute("aria-label", playing ? "Musiqani to‘xtatish" : "Musiqani yoqish");
    if (label) label.textContent = playing ? "Musiqa yoqilgan" : "Musiqa o‘chiq";
  }
  function ramp(to, ms, then) {
    cancelAnimationFrame(fade);
    const from = audio.volume, start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / ms);
      try { audio.volume = from + (to - from) * t; } catch (_) { /* iOS: volume is read-only */ }
      if (t < 1) fade = requestAnimationFrame(step); else if (then) then();
    };
    fade = requestAnimationFrame(step);
  }
  function play() {
    if (broken) return;
    wanted = true;
    const p = audio.play();
    const ok = () => { ui(true); ramp(target, 2200); };
    if (p && p.then) p.then(ok).catch(() => { wanted = false; ui(false); });
    else ok();
  }
  function pause() {
    wanted = false;
    ui(false);
    ramp(0, 450, () => audio.pause());
  }

  let triedFallback = !canAac;
  audio.addEventListener("error", () => {
    // m4a failed → try the mp3 copy once, otherwise disable the control
    if (data.musicFallback && !triedFallback) {
      triedFallback = true;
      audio.src = asset(data.musicFallback);
      if (wanted) play();
      return;
    }
    broken = true;
    ui(false);
    btn.disabled = true;
    btn.setAttribute("aria-label", "Musiqa mavjud emas");
  });

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    first.cancel();
    audio.paused || !btn.classList.contains("is-playing") ? play() : pause();
  });

  // first real interaction anywhere on the page starts the music once
  const first = (() => {
    const start = (e) => {
      if (e.target.closest && e.target.closest("#sound")) return;
      cancel();
      if (!wanted && audio.paused) play();
    };
    const cancel = () => {
      document.removeEventListener("click", start, true);
      document.removeEventListener("keydown", start, true);
    };
    document.addEventListener("click", start, true);
    document.addEventListener("keydown", start, true);
    return { cancel };
  })();

  document.addEventListener("visibilitychange", () => {
    if (document.hidden && !audio.paused) { cancelAnimationFrame(fade); audio.pause(); ui(false); }
    else if (!document.hidden && wanted) play();
  });
}
