/* ==========================================================================
   seal.js — burgundy wax seals (envelope + RSVP), drawn in SVG, and the
   crack animation: two halves fall apart, crumbs fly, a warm glow flashes.
   ========================================================================== */
let uid = 0;

function blobPath(seed) {
  // an irregular wax puddle: radius wobbles with a few low harmonics
  const pts = [];
  for (let i = 0; i < 72; i++) {
    const a = (i / 72) * Math.PI * 2;
    const r = 45 + 1.6 * Math.sin(a * 7 + seed) + 1.1 * Math.sin(a * 13 + seed * 2) + 0.8 * Math.cos(a * 4 - seed);
    pts.push(`${(50 + Math.cos(a) * r).toFixed(2)} ${(50 + Math.sin(a) * r).toFixed(2)}`);
  }
  return `M${pts.join(" L")} Z`;
}

function sealSVG(label, variant) {
  const id = `seal-g${++uid}`;
  const text = variant === "rsvp"
    ? `<text x="50" y="57" text-anchor="middle" font-family="Cormorant Garamond, Georgia, serif" font-weight="600" font-size="17" letter-spacing="2.5" fill="#f3cfc0" opacity=".9">${label}</text>`
    : `<text x="50" y="60" text-anchor="middle" font-family="Great Vibes, cursive" font-size="27" fill="#f3cfc0" opacity=".9">${label.replace("&", "&amp;")}</text>`;
  return `<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false">
    <defs>
      <radialGradient id="${id}" cx="38%" cy="32%" r="75%">
        <stop offset="0" stop-color="#b8404c"/><stop offset=".5" stop-color="#7d1f2c"/><stop offset="1" stop-color="#4a1018"/>
      </radialGradient>
      <radialGradient id="${id}i" cx="50%" cy="45%" r="55%">
        <stop offset="0" stop-color="#6e1a25"/><stop offset="1" stop-color="#8c2733"/>
      </radialGradient>
    </defs>
    <path d="${blobPath(uid * 1.7)}" fill="url(#${id})"/>
    <circle cx="50" cy="50" r="32" fill="url(#${id}i)"/>
    <circle cx="50" cy="50" r="32" fill="none" stroke="rgba(255,205,190,.35)" stroke-width="1.3"/>
    <circle cx="50" cy="50" r="28.5" fill="none" stroke="rgba(40,5,10,.35)" stroke-width="1"/>
    <path d="M28 30 Q50 18 72 30" fill="none" stroke="rgba(255,225,215,.28)" stroke-width="2" stroke-linecap="round"/>
    ${text}
  </svg>`;
}

/** Fill every <button data-seal="…"> with its seal artwork. */
export function initSeals() {
  document.querySelectorAll("[data-seal]").forEach((btn) => {
    const variant = btn.classList.contains("seal--rsvp") ? "rsvp" : "intro";
    const svg = sealSVG(btn.dataset.seal, variant);
    let crumbs = "";
    for (let i = 0; i < 9; i++) crumbs += '<i class="seal__crumb"></i>';
    btn.insertAdjacentHTML("afterbegin",
      `<span class="seal__glow"></span><span class="seal__half seal__half--l">${svg}</span><span class="seal__half seal__half--r">${svg}</span>${crumbs}`);
  });
}

/** Break the seal (purely visual; callers play the sound). */
export function crackSeal(btn) {
  btn.querySelectorAll(".seal__crumb").forEach((c, i) => {
    const a = (i / 9) * Math.PI * 2 + Math.random() * 0.6;
    const d = 30 + Math.random() * 46;
    c.style.setProperty("--dx", `${(Math.cos(a) * d).toFixed(1)}px`);
    c.style.setProperty("--dy", `${(Math.sin(a) * d + 26).toFixed(1)}px`);
    c.style.setProperty("--rot", `${Math.round(Math.random() * 360)}deg`);
    c.style.width = c.style.height = `${(3 + Math.random() * 4).toFixed(1)}px`;
  });
  btn.classList.add("is-cracked");
}
