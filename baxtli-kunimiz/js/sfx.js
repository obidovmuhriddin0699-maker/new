/* ==========================================================================
   sfx.js — the site's own synthesised sound effects (assets/sfx/*.mp3),
   played through Web Audio so they start instantly and can overlap.

   Buffers are fetched and decoded on load (the AudioContext may start
   suspended); the first tap — opening the envelope — resumes it.
   Turning the music off with the floating button silences effects too.
   ========================================================================== */
import { asset } from "./data.js";

export const SOUNDS = ["seal-crack", "envelope-open", "card-slide", "shimmer", "click", "pop", "whoosh", "success", "page", "heartbeat"];

let ctx = null;
let master = null;
let enabled = true;
let unlocked = false;
const buffers = {};

function decode(bytes) {
  // Safari < 14 only supports the callback form
  return new Promise((resolve, reject) => {
    const p = ctx.decodeAudioData(bytes, resolve, reject);
    if (p && p.then) p.then(resolve, reject);
  });
}

export function initSfx(volume = 0.8) {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  try { ctx = new AC(); } catch (_) { return; }
  master = ctx.createGain();
  master.gain.value = volume;
  master.connect(ctx.destination);
  SOUNDS.forEach((name) => {
    fetch(asset(`assets/sfx/${name}.mp3`))
      .then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); })
      .then(decode)
      .then((buf) => { buffers[name] = buf; })
      .catch((err) => console.warn(`[sfx] ${name}:`, err));
  });
}

/** Call inside a user gesture (tap / click / key) so browsers allow sound. */
export function unlockSfx() {
  unlocked = true;
  if (ctx && ctx.state === "suspended") ctx.resume();
}

export function setSfxEnabled(on) { enabled = on; }

/**
 * @param {string} name   one of SOUNDS
 * @param {{volume?: number, rate?: number, delay?: number}} opts
 */
export function play(name, { volume = 1, rate = 1, delay = 0 } = {}) {
  // sounds scheduled while the context is still resuming play as soon as it runs
  if (!enabled || !unlocked || !ctx || !buffers[name] || ctx.state === "closed") return;
  const src = ctx.createBufferSource();
  src.buffer = buffers[name];
  src.playbackRate.value = rate;
  const g = ctx.createGain();
  g.gain.value = volume;
  src.connect(g);
  g.connect(master);
  src.start(ctx.currentTime + delay);
  // lets a host page (or the video-reel recorder) follow what is heard
  window.dispatchEvent(new CustomEvent("sfx:play", { detail: { name, volume, rate, delay } }));
}
