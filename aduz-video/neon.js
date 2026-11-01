// Neon theme for ADUZ episodes (23-qismdan boshlab) — the user's "telegram_reklama777" design system:
// ground-900 night background with a blurred red glow from the lower-left, ink text with soft glow, Russo One display
// (ALL CAPS) + Archivo sans (italic leads), neon-pink hero word, signal-yellow for one offer word, signal-cyan for the
// positive/CTA keyword (never yellow and cyan in the same block), chip cards with a thin edge.
// Load after lib.js: <script src="lib.js"></script><script src="neon.js"></script>. Overrides lib.js scene helpers.

const N = {
  ground: '#110e18', burg: '#260001', burgHi: '#460001', glowRed: '#c82224',
  ink: '#fcfcfc', muted: '#a0959f', pink: '#f84058', pinkSoft: '#f87888', wave: '#d87880',
  yellow: '#f8e800', cyan: '#08c0c8', chip: '#401820', chipEdge: '#5c2729', paper: '#f8f8f0', clip: '#b03028',
};
const HANDLE = '@telegram_reklama777';

// ---------- fonts (OFL, fonts/) ----------
{
  const LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
  const EXT = 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF';
  const faces = [];
  for (const [sub, range] of [['latin', LATIN], ['latin-ext', EXT]]) {
    faces.push(new FontFace('Russo One', `url(fonts/RussoOne-normal-${sub}.woff2)`, { unicodeRange: range }));
    faces.push(new FontFace('Archivo', `url(fonts/Archivo-normal-${sub}.woff2)`, { weight: '100 900', unicodeRange: range }));
    faces.push(new FontFace('Archivo', `url(fonts/Archivo-italic-${sub}.woff2)`, { weight: '100 900', style: 'italic', unicodeRange: range }));
  }
  // render.mjs awaits document.fonts.ready, which waits for these loads.
  for (const f of faces) { document.fonts.add(f); f.load(); }
}
F = 'Archivo, Inter, "DejaVu Sans", sans-serif';
FD = '"Russo One", Archivo, "DejaVu Sans", sans-serif';
Object.assign(C, { navy: N.ground, red: N.pink, redDim: N.clip, green: N.cyan, greenDeep: '#04363a', teal: '#067f86', gold: N.yellow, ink: N.ground, grey: '#6b6270' });
CONFETTI.forEach((c, i) => { c.c = [N.yellow, N.pink, N.ink, N.cyan][i % 4]; });

// ---------- helpers ----------
// Text with a neon glow (text-shadow emulation: tight + wide blur).
function glowText(s, x, y, size, color, weight = 900, align = 'center', base = 'middle', glow = color, amt = 1) {
  ctx.save();
  ctx.shadowOffsetX = ctx.shadowOffsetY = 0; ctx.shadowColor = glow; ctx.shadowBlur = 22 * amt; text(s, x, y, size, color, weight, align, base);
  ctx.shadowBlur = 6 * amt; text(s, x, y, size, color, weight, align, base);
  ctx.restore();
}
const it = w => `italic ${w}`;   // Archivo italic: text(s, x, y, size, col, it(500))
// Background: night ground, blurred red corner glow (k = intensity), optional second glow (x, y, rgb).
function neonGround(t, k = 1, second = null) {
  ctx.fillStyle = N.ground; ctx.fillRect(0, 0, W, H);
  const gx = -80 + Math.sin(t * .4) * 30, gy = H + 60, R = H * .62;
  const g = ctx.createRadialGradient(gx, gy, 0, gx, gy, R);
  g.addColorStop(0, `rgba(200,34,36,${.85 * k})`); g.addColorStop(.45, `rgba(70,0,1,${.55 * k})`); g.addColorStop(1, 'rgba(38,0,1,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  if (second) {
    const [x, y, rgb, a = .35, r = 900] = second;
    const s = ctx.createRadialGradient(x, y, 0, x, y, r);
    s.addColorStop(0, `rgba(${rgb},${a})`); s.addColorStop(1, `rgba(${rgb},0)`); ctx.fillStyle = s; ctx.fillRect(0, 0, W, H);
  }
}
// Chip card (design: chip fill, chip-edge 2px, radius 14).
function chipCard(x, y, w, h, r = 14, fill = N.chip, edge = N.chipEdge) {
  rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = edge; ctx.stroke();
}

// ---------- lib.js overrides ----------
function problemBg(t, stress) {
  neonGround(t, .55 + .45 * stress);
  const pulse = stress * (.18 + .18 * Math.sin(t * 9));
  const v = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1200);
  v.addColorStop(0, 'rgba(248,64,88,0)'); v.addColorStop(1, `rgba(248,64,88,${pulse})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
function episodeTitle(t, label, title, size) {
  withAlpha(prog(t, 0, .5), () => {
    glowText(label, W / 2, 110, 30, N.pink, 900);
    glowText(title.toUpperCase(), W / 2, 175, size, N.ink, 900, 'center', 'middle', 'rgba(252,252,252,.6)', .7);
  });
}
function counters(t, items) {
  withAlpha(prog(t, .6, 1.2), () => {
    items.forEach(([a, b, col], i) => {
      const x = 200 + i * 340;
      chipCard(x - 150, 228, 300, 100);
      glowText(a, x, 268, 40, col === '#fff' ? N.ink : col, 900, 'center', 'middle', col === '#fff' ? 'rgba(252,252,252,.5)' : col, .7);
      text(b, x, 312, 24, N.muted, it(500), 'center');
    });
  });
}
function solutionBg(t, subtitle) {
  neonGround(t, .45, [W + 60 + Math.sin(t * .5) * 40, 420, '8,192,200', .32, 1000]);
  const lp = eBack(prog(t, 11.2, 11.9));
  withAlpha(prog(t, 11.2, 11.6), () => scaled(W / 2, 200, lp, () => logo(W / 2 - 205, 150, 1)));
  withAlpha(prog(t, 11.8, 12.3), () => text(subtitle, W / 2, 310, 34, N.muted, it(500), 'center'));
}
function logo(x, y, s, light = false) {
  ctx.save(); ctx.shadowColor = 'rgba(8,192,200,.8)'; ctx.shadowBlur = 30 * s;
  rr(x, y, 96 * s, 96 * s, 26 * s);
  const g = ctx.createLinearGradient(x, y, x + 96 * s, y + 96 * s);
  g.addColorStop(0, '#3ff0f5'); g.addColorStop(1, '#067f86'); ctx.fillStyle = g; ctx.fill(); ctx.restore();
  ctx.save(); ctx.translate(x + 48 * s, y + 48 * s); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -30); ctx.lineTo(26, -20); ctx.lineTo(24, 8); ctx.quadraticCurveTo(18, 26, 0, 34);
  ctx.quadraticCurveTo(-18, 26, -24, 8); ctx.lineTo(-26, -20); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill();
  check(1, 2, 26, '#067f86', 7);
  ctx.restore();
  if (light) text('ADUZ', x + 116 * s, y + 70 * s, 64 * s, N.ground, 900);
  else glowText('ADUZ', x + 116 * s, y + 70 * s, 64 * s, N.ink, 900, 'left', 'alphabetic', 'rgba(252,252,252,.55)', s);
}
function resultBg(t) {
  // "premium" look: burgundy core over the night ground, red corner glow, slow signal-yellow rays
  ctx.fillStyle = N.ground; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, 760, 0, W / 2, 760, 1250);
  g.addColorStop(0, N.burgHi); g.addColorStop(.55, N.burg); g.addColorStop(1, N.ground);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const r = ctx.createRadialGradient(-80, H + 60, 0, -80, H + 60, H * .62);
  r.addColorStop(0, 'rgba(200,34,36,.6)'); r.addColorStop(1, 'rgba(200,34,36,0)'); ctx.fillStyle = r; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(W / 2, 760); ctx.rotate(t * .15);
  for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-90, -1400); ctx.lineTo(90, -1400); ctx.closePath(); ctx.fillStyle = 'rgba(248,232,0,.035)'; ctx.fill(); }
  ctx.restore();
}
// Captions: Archivo italic ink with glow, no box, kept above the bottom safe zone (design: bottom ~420 px free).
function captions(t, list) {
  for (const [a, b, s] of list) {
    if (t < a || t > b) continue;
    const al = Math.min(prog(t, a, a + .25), 1 - prog(t, b - .25, b));
    const lines = wrap(s, 900, 40, it(600));
    const lh = 52, y = 1588 - (lines.length - 1) * lh / 2;
    withAlpha(al, () => {
      const bg = ctx.createLinearGradient(0, y - 70, 0, y + lines.length * lh + 30);
      bg.addColorStop(0, 'rgba(17,14,24,0)'); bg.addColorStop(.35, 'rgba(17,14,24,.72)'); bg.addColorStop(.75, 'rgba(17,14,24,.72)'); bg.addColorStop(1, 'rgba(17,14,24,0)');
      ctx.fillStyle = bg; ctx.fillRect(0, y - 70, W, lines.length * lh + 100);
      lines.forEach((l, i) => glowText(l, W / 2, y + lh * i, 40, N.ink, it(600), 'center', 'middle', 'rgba(252,252,252,.45)', .6));
    });
  }
}
// Neon medal: yellow ring, glyph drawn by `drawGlyph(x, y)`, chip-style label.
function neonBadge(bx, by, label, drawGlyph, p) {
  scaled(bx, by, p, () => {
    ctx.save(); ctx.shadowColor = 'rgba(248,232,0,.9)'; ctx.shadowBlur = 36;
    ctx.beginPath(); ctx.arc(bx, by, 88, 0, 7); ctx.fillStyle = N.chip; ctx.fill();
    ctx.lineWidth = 8; ctx.strokeStyle = N.yellow; ctx.stroke(); ctx.restore();
    ctx.beginPath(); ctx.arc(bx, by, 72, 0, 7); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(248,232,0,.45)'; ctx.stroke();
    drawGlyph(bx, by);
    glowText(label.toUpperCase(), bx, by + 140, 26, N.ink, 900, 'center', 'middle', 'rgba(252,252,252,.5)', .6);
  });
}
// Comment CTA (design: "IZOHGA" + “KEYWORD” in cyan + small-italic line). y = baseline of the first line.
function commentCTA(t, t0, word, y = 1260) {
  const p = eBack(prog(t, t0, t0 + .45)); if (p <= 0) return;
  scaled(W / 2, y + 20, p, () => {
    ctx.font = fnt(900, 64); const a = 'IZOHGA ', b = `“${word}”`, wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = W / 2 - (wa + wb) / 2;
    glowText(a, x0, y, 64, N.ink, 900, 'left', 'middle', 'rgba(252,252,252,.6)', .7);
    glowText(b, x0 + wa, y, 64, N.cyan, 900, 'left', 'middle', N.cyan, 1 + .25 * Math.sin(t * 6));
  });
  withAlpha(prog(t, t0 + .3, t0 + .6), () => text('deb yozing — sizga yuboramiz', W / 2, y + 78, 36, N.ink, it(500), 'center', 'middle'));
}
// Closing card: glowing logo, ALL-CAPS slogan with a neon-pink hero word, comment CTA, handle.
function endCard(t, t0) {
  const ep = prog(t, t0, t0 + .6);
  if (ep <= 0) return;
  withAlpha(ep * .85, () => neonGround(t, .9));
  const s = eBack(ep);
  withAlpha(ep, () => scaled(W / 2, 700, s * 1.6, () => logo(W / 2 - 205, 652, 1)));
  shine(W / 2 - 340, 600, 680, 200, prog(t, t0 + .8, t0 + 1.6), 30);
  kText(t, t0 + .5, 'BIZNESINGIZ', W / 2, 930, 84, N.ink, 'letterUp', { glow: 'rgba(252,252,252,.55)', stagger: .03 });
  kText(t, t0 + .7, 'HIMOYACHISI!', W / 2, 1035, 96, N.pink, 'bounce', { glow: N.pink, stagger: .035 });
  withAlpha(prog(t, t0 + 1.0, t0 + 1.4), () => text('Fargʻona vodiysi · Telegram reklama ekotizimi', W / 2, 1125, 32, N.muted, it(500), 'center'));
  commentCTA(t, t0 + 1.3, 'ADUZ', 1260);
  withAlpha(prog(t, t0 + 1.7, t0 + 2.1), () => text(HANDLE, W / 2, 1450, 28, N.muted, 900, 'center'));
}

// ---------- design-system demo pieces ----------
// PostTimeline: ad-post chips scrolling right→left under a fixed ink playhead (downward triangle).
// items: [{ label, sub }], offset: scroll in px, live: index drawn as the "live" chip (neon-pink thumb).
function postTimeline(y, items, offset, live = -1, cw = 300, gap = 24) {
  const step = cw + gap;
  items.forEach((it2, i) => {
    const x = W / 2 - cw / 2 + i * step - offset; if (x > W + 20 || x + cw < -20) return;
    const on = i === live;
    ctx.save(); if (on) { ctx.shadowColor = 'rgba(248,64,88,.8)'; ctx.shadowBlur = 30; }
    chipCard(x, y, cw, 150, 14, N.chip, on ? N.pink : N.chipEdge); ctx.restore();
    rr(x + 16, y + 16, 80, 118, 10); ctx.fillStyle = on ? N.pink : '#5c2729'; ctx.fill();
    text(it2.label, x + 112, y + 62, 28, on ? N.ink : '#d9cfd6', 800);
    rr(x + 112, y + 84, 160, 10, 5); ctx.fillStyle = on ? N.pinkSoft : '#6b3a40'; ctx.fill();
    rr(x + 112, y + 106, 110, 10, 5); ctx.fillStyle = on ? N.pinkSoft : '#6b3a40'; ctx.fill();
    if (it2.sub) text(it2.sub, x + cw - 16, y + 134, 20, on ? N.pinkSoft : N.muted, it(500), 'right');
  });
  // playhead
  ctx.fillStyle = N.ink; ctx.fillRect(W / 2 - 2, y - 40, 4, 230);
  ctx.beginPath(); ctx.moveTo(W / 2 - 16, y - 54); ctx.lineTo(W / 2 + 16, y - 54); ctx.lineTo(W / 2, y - 32); ctx.closePath(); ctx.fill();
}
