/* ==========================================================================
   audio.js — background music + the floating play/pause button.
   Music starts when the envelope is opened (a user gesture); the button
   pauses/resumes it and also silences the sound effects.
   ========================================================================== */
import { asset } from "./data.js";
import { t, onLang } from "./i18n.js";
import { setSfxEnabled } from "./sfx.js";

export function initAudio(data) {
  const audio = document.getElementById("audio");
  const btn = document.getElementById("sound");
  if (!audio || !btn || !data.music) return { start() {} };
  const target = Math.min(1, Math.max(0, data.musicVolume ?? 0.4));
  let fade = 0;
  let wanted = false;
  let triedFallback = false;

  const canAac = audio.canPlayType('audio/mp4; codecs="mp4a.40.2"') !== "";
  triedFallback = !canAac || !data.musicFallback;
  audio.src = asset(canAac || !data.musicFallback ? data.music : data.musicFallback);
  audio.volume = 0;

  function ui() {
    const on = wanted && !audio.paused;
    btn.classList.toggle("is-playing", on);
    btn.setAttribute("aria-pressed", String(on));
    btn.setAttribute("aria-label", on ? t("sound_on") : t("sound_off"));
  }
  function ramp(to, ms, then) {
    cancelAnimationFrame(fade);
    const from = audio.volume, t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / ms);
      try { audio.volume = from + (to - from) * k; } catch (_) { /* iOS: volume is read-only */ }
      if (k < 1) fade = requestAnimationFrame(step); else if (then) then();
    };
    fade = requestAnimationFrame(step);
  }
  function start() {
    wanted = true;
    setSfxEnabled(true);
    btn.disabled = false;
    const p = audio.play();
    const ok = () => { ui(); ramp(target, 2600); };
    if (p && p.then) p.then(ok).catch(() => { wanted = false; ui(); });
    else ok();
  }
  function stop() {
    wanted = false;
    setSfxEnabled(false);
    ui();
    ramp(0, 450, () => audio.pause());
  }

  audio.addEventListener("error", () => {
    if (!triedFallback) {            // m4a failed → mp3 once
      triedFallback = true;
      audio.src = asset(data.musicFallback);
      if (wanted) start();
      return;
    }
    console.warn("[audio] music could not be loaded");
    wanted = false;
    ui();
  });
  audio.addEventListener("play", ui);
  audio.addEventListener("pause", ui);
  btn.addEventListener("click", () => (wanted && !audio.paused ? stop() : start()));
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) audio.pause();
    else if (wanted) audio.play().catch(() => {});
  });
  onLang(ui);
  ui();
  return { start, stop };
}
