/* ==========================================================================
   intro.js — the envelope. One tap on the wax seal:
     0.00 s  seal cracks            (seal-crack)
     0.45 s  flap swings open       (envelope-open)
     1.35 s  card slides out        (card-slide)
     2.45 s  card blooms to light   (shimmer) — music fades in
     3.25 s  the invitation appears
   That tap is also the gesture browsers require before playing sound.
   ========================================================================== */
import { reducedMotion } from "./data.js";
import { crackSeal } from "./seal.js";
import { play, unlockSfx } from "./sfx.js";

export function initIntro({ onOpen, onDone }) {
  const intro = document.getElementById("intro");
  const env = document.getElementById("envelope");
  const seal = document.getElementById("intro-seal");
  const root = document.documentElement;
  if (!intro || !env || !seal) { onDone?.(); return; }

  root.classList.add("intro-lock");
  const bloom = document.createElement("div");
  bloom.className = "intro__bloom";
  intro.appendChild(bloom);
  seal.focus({ preventScroll: true });

  let opened = false;
  const steps = reducedMotion
    ? [[0, () => crackSeal(seal)], [300, finish], [700, gone]]
    : [
        [0, () => { crackSeal(seal); play("seal-crack"); }],
        [450, () => { env.classList.add("is-open"); play("envelope-open", { volume: 0.9 }); }],
        [950, () => env.classList.add("is-flap-behind")],
        [1350, () => { env.classList.add("is-card-out"); play("card-slide", { volume: 0.9 }); }],
        [2450, () => { intro.classList.add("is-blooming"); play("shimmer", { volume: 0.85 }); }],
        [3250, finish],
        [4300, gone]
      ];

  function open() {
    if (opened) return;
    opened = true;
    unlockSfx();
    onOpen?.();                         // music starts inside the same gesture
    steps.forEach(([at, fn]) => setTimeout(fn, at));
  }
  function finish() {
    root.classList.remove("intro-lock");
    intro.classList.add("is-fading");
    window.scrollTo(0, 0);
    onDone?.();
  }
  function gone() {
    intro.classList.add("is-gone");
    intro.setAttribute("aria-hidden", "true");
    document.getElementById("main")?.focus?.({ preventScroll: true });
  }

  seal.addEventListener("click", open);
  // the whole envelope is a big tap target on phones
  env.addEventListener("click", (e) => { if (!e.target.closest("#intro-seal")) open(); });
  intro.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
}
