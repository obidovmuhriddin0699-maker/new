// "Motion reel" theme for ADUZ episodes (24-qismdan) — from the user's reference showreel video:
// HUD frame (corner brackets, tiny tracked mono labels, live timecode, section number, ruler with a playhead),
// ink-black / warm-paper grounds, a 4-colour palette (signal orange, acid lime, violet, off-white),
// heavy grotesk ALL-CAPS kinetic words (Archivo 900), serif italic accents (Instrument Serif), mono micro-labels
// (JetBrains Mono), rounded-square dot grids moving in waves, flat UI cards, diagonal stripes, halftone rings,
// letters falling into a logotype with an orbit ellipse and an orange underline.
// Load after lib.js: <script src="lib.js"></script><script src="reel.js"></script>. Overrides lib.js scene helpers.

const R = {
  ink: '#0e0d0f', ink2: '#17151a', warm: '#1c1311', paper: '#e9e7e2', card: '#f7f6f3', off: '#efece4',
  orange: '#f04a1e', lime: '#d6f03a', violet: '#6a5cf2', violetSoft: '#c9c2f7', grey: '#8b8790', line: '#3a373d',
};
const PAL = [R.orange, R.lime, R.violet, R.off];
const SERIF = '"Instrument Serif", Georgia, serif', MONO = '"JetBrains Mono", "DejaVu Sans Mono", monospace';

// ---------- fonts (OFL, fonts/) ----------
{
  const LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
  const EXT = 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF';
  const faces = [];
  for (const [sub, range] of [['latin', LATIN], ['latin-ext', EXT]]) {
    faces.push(new FontFace('Archivo', `url(fonts/Archivo-normal-${sub}.woff2)`, { weight: '100 900', unicodeRange: range }));
    faces.push(new FontFace('Archivo', `url(fonts/Archivo-italic-${sub}.woff2)`, { weight: '100 900', style: 'italic', unicodeRange: range }));
    faces.push(new FontFace('Instrument Serif', `url(fonts/InstrumentSerif-normal-${sub}.woff2)`, { unicodeRange: range }));
    faces.push(new FontFace('Instrument Serif', `url(fonts/InstrumentSerif-italic-${sub}.woff2)`, { style: 'italic', unicodeRange: range }));
    faces.push(new FontFace('JetBrains Mono', `url(fonts/JetBrainsMono-normal-${sub}.woff2)`, { weight: '100 800', unicodeRange: range }));
  }
  for (const f of faces) { document.fonts.add(f); f.load(); }   // render.mjs awaits document.fonts.ready
}
F = 'Archivo, Inter, "DejaVu Sans", sans-serif';
Object.assign(C, { navy: R.ink, red: R.orange, redDim: '#7a2410', green: R.lime, greenDeep: '#2a3108', teal: R.violet, gold: R.lime, ink: R.ink, grey: R.grey, paper: R.card });
CONFETTI.forEach((c, i) => { c.c = PAL[i % 4]; });

// ---------- type helpers ----------
function serif(s, x, y, size, color, align = 'center', base = 'middle', italic = true) {
  ctx.font = `${italic ? 'italic ' : ''}400 ${size}px ${SERIF}`; ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(s, x, y);
}
function mono(s, x, y, size, color, align = 'left', track = .25, weight = 500, base = 'middle') {
  ctx.save(); ctx.font = `${weight} ${size}px ${MONO}`; ctx.letterSpacing = `${(size * track).toFixed(1)}px`;
  ctx.fillStyle = color; ctx.textAlign = align; ctx.textBaseline = base;
  // letterSpacing adds trailing space after the last glyph; nudge right-/centre-aligned text back
  const nudge = align === 'right' ? size * track : align === 'center' ? size * track / 2 : 0;
  ctx.fillText(s, x + nudge, y); ctx.restore();
}
// Decoding text: random glyphs settle left→right into `str` between at and at+dur.
const SCR = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%/<>';
function scramble(t, at, str, x, y, size, color, o = {}) {
  const { dur = .7, align = 'center', track = .35, weight = 700, hold = 99, out = .25 } = o;
  const d = t - at; if (d < 0) return;
  const fade = 1 - clamp((d - hold) / out); if (fade <= 0) return;
  const k = Math.floor(d * 30);
  const s = [...str].map((ch, i) => { const done = d > dur * (i + 1) / str.length; if (done || ch === ' ') return ch;
    return SCR[Math.abs(Math.floor(Math.sin((i + 1) * 12.9898 + k * 78.233) * 43758.5453)) % SCR.length]; }).join('');
  withAlpha(fade * clamp(d / .1), () => mono(s, x, y, size, color, align, track, weight));
}
// Heavy grotesk word that slams in with a rotation settle and squash; o.hold → fades.
function heavy(t, at, s, x, y, size, color, o = {}) {
  const { rot = 0, hold = 99, out = .2, from = 1.6, track = -.03 } = o;
  const d = t - at; if (d < 0) return;
  const p = clamp(d / .32), q = clamp((d - hold) / out); if (q >= 1) return;
  const sc = lerp(from, 1, eBack(p)), r = rot * (1 - eOut(p)) + (o.endRot || 0);
  ctx.save(); ctx.globalAlpha *= clamp(p * 3) * (1 - q); ctx.translate(x, y); ctx.rotate(r); ctx.scale(sc, sc * (1 + .12 * Math.sin(Math.PI * p) * (1 - p)));
  ctx.font = `900 ${size}px ${F}`; ctx.letterSpacing = `${(size * track).toFixed(1)}px`;
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 0); ctx.restore();
}

// ---------- HUD frame ----------
// sections: [[startTime, '01', 'MUAMMO'], …]; light = draw in ink (on paper grounds).
function hud(t, sections, light = false, episode = '') {
  const col = light ? 'rgba(14,13,15,.75)' : 'rgba(239,236,228,.78)', m = 44, top = 70, bot = H - 70;
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 2;
  const br = (x, y, sx, sy) => { ctx.beginPath(); ctx.moveTo(x + 26 * sx, y); ctx.lineTo(x, y); ctx.lineTo(x, y + 26 * sy); ctx.stroke(); };
  br(m, top, 1, 1); br(W - m, top, -1, 1); br(m, bot, 1, -1); br(W - m, bot, -1, -1);
  mono(`ADUZ  /  ${episode}`, m + 40, top + 4, 17, col, 'left', .28, 700);
  const fr = Math.floor(t * 30), ss = Math.floor(t);
  mono(`TC 00:00:${String(ss).padStart(2, '0')}:${String(fr % 30).padStart(2, '0')}`, W - m - 40, top + 4, 17, col, 'right', .22, 700);
  let cur = sections[0]; for (const s of sections) if (t >= s[0]) cur = s;
  mono(`${cur[1]}  /  ${cur[2]}`, m + 40, bot - 4, 17, col, 'left', .28, 700);
  mono('1080 X 1920  /  30 FPS', W - m - 40, bot - 4, 17, col, 'right', .22, 700);
  // ruler with playhead
  const y = bot - 40, x0 = m + 40, x1 = W - m - 40;
  ctx.globalAlpha = .55; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
  for (let i = 0; i <= 32; i++) { const x = lerp(x0, x1, i / 32); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y - (i % 4 ? 6 : 14)); ctx.stroke(); }
  ctx.globalAlpha = 1; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(lerp(x0, x1, clamp(t / (window.DURATION || 32))), y); ctx.strokeStyle = col; ctx.stroke();
  ctx.restore();
}
// Orange line with tick ruler (the reel's "ignition" device). p = draw-on progress.
function tickLine(cx, y, w, p, col = R.orange, tick = 'rgba(239,236,228,.7)') {
  if (p <= 0) return;
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(cx - w / 2 * p, y); ctx.lineTo(cx + w / 2 * p, y); ctx.stroke();
  ctx.strokeStyle = tick; ctx.lineWidth = 2;
  for (let i = -18; i <= 18; i++) { const x = cx + i * w * .022; if (Math.abs(i) / 18 > p) continue; const l = i % 3 ? 8 : 20;
    ctx.beginPath(); ctx.moveTo(x, y - 12); ctx.lineTo(x, y - 12 - l); ctx.stroke(); ctx.beginPath(); ctx.moveTo(x, y + 12); ctx.lineTo(x, y + 12 + l * .5); ctx.stroke(); }
  ctx.restore();
}

// ---------- graphic devices ----------
// Grid of rounded squares in the palette; each tile turns/squashes with a travelling wave. a = alpha, cover: 0..1 tile size.
const GRID_COLS = 9, GRID_GAP = W / GRID_COLS;
const GRID_C = (() => { const r = rnd(911); return Array.from({ length: 200 }, () => r() < .45 ? R.off : PAL[Math.floor(r() * 3)]); })();
function dotGrid(t, a = 1, size = .55, wave = 1, cx = W / 2, cy = H / 2, round = .28) {
  if (a <= 0) return;
  withAlpha(a, () => {
    let k = 0;
    for (let j = -1; j * GRID_GAP < H + GRID_GAP; j++) for (let i = 0; i < GRID_COLS; i++, k++) {
      const x = (i + .5) * GRID_GAP, y = (j + .5) * GRID_GAP + ((t * 40) % GRID_GAP), dd = Math.hypot(x - cx, y - cy);
      const ph = Math.sin(dd / 140 - t * 4) * wave, s = GRID_GAP * size * (1 + .12 * ph);
      ctx.save(); ctx.translate(x, y); ctx.rotate(ph * .6);
      rr(-s / 2, -s / 2, s, s, s * round); ctx.fillStyle = GRID_C[k % GRID_C.length]; ctx.fill(); ctx.restore();
    }
  });
}
// Diagonal stripes (offset scrolls with t).
function stripes(t, c1 = R.orange, c2 = R.ink, w = 90, speed = 160) {
  ctx.fillStyle = c2; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.fillStyle = c1; const off = (t * speed) % (w * 2);
  for (let x = -H - w * 2 + off; x < W + H; x += w * 2) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + w, 0); ctx.lineTo(x + w + H, H); ctx.lineTo(x + H, H); ctx.closePath(); ctx.fill(); }
  ctx.restore();
}
// Halftone rings pulsing outwards from (cx, cy) on a violet ground.
function halftone(t, cx = W / 2, cy = H / 2, bg = R.violet, dot = 'rgba(239,236,228,.85)', a = 1) {
  if (a <= 0) return;
  withAlpha(a, () => {
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H); ctx.fillStyle = dot;
    const g = 30;
    for (let y = g / 2; y < H; y += g) for (let x = g / 2; x < W; x += g) {
      const d = Math.hypot(x - cx, y - cy), r = 11 * (.5 + .5 * Math.sin(d / 55 - t * 5)) ** 1.5;
      if (r < .6) continue; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
    }
  });
}
// Flat UI card with a soft drop shadow.
function card(x, y, w, h, fill = R.card, r = 30) {
  ctx.save(); ctx.shadowColor = 'rgba(14,13,15,.18)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 18;
  rr(x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
function toggle(x, y, on, k = 1) { // pill toggle, on 0..1
  rr(x, y, 130, 64, 32); ctx.fillStyle = on > .5 ? R.ink : R.off; ctx.fill();
  ctx.beginPath(); ctx.arc(x + lerp(32, 98, eInOut(on)), y + 32, 24, 0, 7); ctx.fillStyle = on > .5 ? R.lime : R.ink; ctx.fill();
}
function donut(cx, cy, r, p, col = R.orange, track = '#2b2830', lw = 16) {
  ctx.lineWidth = lw; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.strokeStyle = track; ctx.stroke();
  if (p > 0) { ctx.beginPath(); ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * p); ctx.strokeStyle = col; ctx.stroke(); }
}
// Particles that gather from a scattered cloud into a ring/sphere (p 0→1), violet ground glow.
const PARTS = (() => { const r = rnd(913); return Array.from({ length: 900 }, () => ({ a: r() * 6.283, b: Math.acos(2 * r() - 1), sx: r() * W, sy: r() * H, d: r() * .3 })); })();
function particleSphere(t, p, cx, cy, rad, col = 'rgba(239,236,228,.9)') {
  const rot = t * .6;
  ctx.fillStyle = col;
  for (const q of PARTS) {
    const k = eInOut(clamp((p - q.d) / .7));
    const x3 = Math.sin(q.b) * Math.cos(q.a + rot), z = Math.sin(q.b) * Math.sin(q.a + rot), y3 = Math.cos(q.b);
    const x = lerp(q.sx, cx + x3 * rad, k), y = lerp(q.sy, cy + y3 * rad, k), s = lerp(1.5, 1.2 + (z + 1) * 1.6, k);
    ctx.globalAlpha = lerp(.35, .35 + .6 * (z + 1) / 2, k); ctx.fillRect(x, y, s, s);
  }
  ctx.globalAlpha = 1;
}

// ---------- lib.js overrides ----------
function problemBg(t, stress) {
  ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, H * .55, 100, W / 2, H * .55, 1300);
  g.addColorStop(0, `rgba(240,74,30,${.05 + .16 * stress})`); g.addColorStop(1, 'rgba(240,74,30,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function episodeTitle(t, label, title, size) {
  scramble(t, .1, label, W / 2, 150, 26, R.orange);
  heavy(t, .3, title.toUpperCase(), W / 2, 215, size, R.off);
}
function counters(t, items) {
  withAlpha(prog(t, .6, 1.2), () => items.forEach(([a, b, col], i) => {
    const x = 200 + i * 340;
    ctx.save(); ctx.strokeStyle = R.line; ctx.lineWidth = 2; rr(x - 150, 290, 300, 104, 18); ctx.stroke(); ctx.restore();
    text(a, x, 334, 46, col === '#fff' ? R.off : col, 900, 'center', 'middle');
    mono(b.toUpperCase(), x, 372, 15, R.grey, 'center', .3, 700);
  }));
}
function solutionBg(t, subtitle) {
  ctx.fillStyle = R.paper; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W * .3, H * .3, 100, W * .3, H * .3, 1400); g.addColorStop(0, 'rgba(255,255,255,.7)'); g.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const lp = eBack(prog(t, 11.2, 11.9));
  withAlpha(prog(t, 11.2, 11.6), () => scaled(W / 2, 205, lp, () => logo(W / 2 - 205, 155, 1, true)));
  withAlpha(prog(t, 11.8, 12.3), () => serif(subtitle, W / 2, 300, 44, R.ink));
}
function logo(x, y, s, light = false) {
  rr(x, y, 96 * s, 96 * s, 26 * s); ctx.fillStyle = R.orange; ctx.fill();
  ctx.save(); ctx.translate(x + 48 * s, y + 48 * s); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -30); ctx.lineTo(26, -20); ctx.lineTo(24, 8); ctx.quadraticCurveTo(18, 26, 0, 34);
  ctx.quadraticCurveTo(-18, 26, -24, 8); ctx.lineTo(-26, -20); ctx.closePath(); ctx.fillStyle = R.off; ctx.fill();
  check(1, 2, 26, R.orange, 7);
  ctx.restore();
  ctx.save(); ctx.letterSpacing = `${(-2 * s).toFixed(1)}px`; text('ADUZ', x + 116 * s, y + 70 * s, 66 * s, light ? R.ink : R.off, 900); ctx.restore();
}
function resultBg(t) {
  ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, 800, 50, W / 2, 800, 1300); g.addColorStop(0, 'rgba(106,92,242,.32)'); g.addColorStop(1, 'rgba(106,92,242,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// Captions: off-white Archivo on an ink pill, above the HUD ruler.
function captions(t, list) {
  for (const [a, b, s] of list) {
    if (t < a || t > b) continue;
    const al = Math.min(prog(t, a, a + .25), 1 - prog(t, b - .25, b));
    const lines = wrap(s, 860, 42, 700), lh = 56, h = lines.length * lh + 36, y = 1700 - h / 2;
    withAlpha(al, () => {
      rr(90, y, 900, h, 18); ctx.fillStyle = 'rgba(14,13,15,.86)'; ctx.fill();
      ctx.fillStyle = R.orange; ctx.fillRect(90, y + 18, 6, h - 36);
      lines.forEach((l, i) => text(l, W / 2, y + 18 + lh * i + lh / 2 + 2, 42, R.off, 700, 'center', 'middle'));
    });
  }
}
// Coloured medal: palette disc, glyph, mono label.
function reelBadge(bx, by, label, col, drawGlyph, p) {
  scaled(bx, by, p, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
    ctx.beginPath(); ctx.arc(bx, by, 90, 0, 7); ctx.fillStyle = col; ctx.fill(); ctx.restore();
    drawGlyph(bx, by);
    mono(label.toUpperCase(), bx, by + 140, 20, R.off, 'center', .3, 700);
  });
}
// Identity end card: letters fall into "ADUZ" along an arc, orbit ellipse with two satellites, orange underline,
// mono strap line + serif italic tagline, CTA pill.
function endCard(t, t0) {
  const ep = prog(t, t0, t0 + .5);
  if (ep <= 0) return;
  withAlpha(ep, () => {
    ctx.fillStyle = R.warm; ctx.fillRect(0, 0, W, H);
    const g = ctx.createRadialGradient(W / 2, 820, 50, W / 2, 820, 1100); g.addColorStop(0, 'rgba(240,74,30,.22)'); g.addColorStop(1, 'rgba(240,74,30,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  });
  // logo mark
  const lm = eBack(prog(t, t0 + .1, t0 + .5));
  if (lm > 0) scaled(W / 2, 560, lm * 1.25, () => {
    rr(W / 2 - 48, 512, 96, 96, 26); ctx.fillStyle = R.orange; ctx.fill(); shield(W / 2, 560, 1, R.off); check(W / 2 + 1, 562, 26, R.orange, 7);
  });
  // letters
  const word = 'ADUZ', size = 230; ctx.font = `900 ${size}px ${F}`;
  const ws = [...word].map(c => ctx.measureText(c).width), tot = ws.reduce((a, b) => a + b, 0) - 3 * 8;
  let x = W / 2 - tot / 2;
  [...word].forEach((c, i) => {
    const p = prog(t, t0 + .15 + i * .1, t0 + .6 + i * .1), e = eBack(p);
    if (p > 0) { const cx = x + ws[i] / 2, fy = lerp(-200 - i * 80, 830, eOut(p)), r = (1 - eOut(p)) * (i % 2 ? .8 : -.9);
      ctx.save(); ctx.translate(lerp(cx + (i - 1.5) * 160, cx, eOut(p)), fy); ctx.rotate(r); ctx.scale(1, lerp(1.3, 1, e));
      ctx.font = `900 ${size}px ${F}`; ctx.fillStyle = R.off; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(c, 0, 0); ctx.restore(); }
    x += ws[i] - 8;
  });
  // orbit
  const op = prog(t, t0 + .7, t0 + 1.2);
  if (op > 0) withAlpha(op, () => {
    ctx.save(); ctx.translate(W / 2, 830); ctx.rotate(-.12);
    ctx.beginPath(); ctx.ellipse(0, 0, 470, 170, 0, 0, 7); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(239,236,228,.35)'; ctx.stroke();
    [[t * 1.4, R.orange], [t * 1.4 + Math.PI, R.lime]].forEach(([a, c]) => { ctx.beginPath(); ctx.arc(Math.cos(a) * 470, Math.sin(a) * 170, 11, 0, 7); ctx.fillStyle = c; ctx.fill(); });
    ctx.restore();
  });
  const ul = eInOut(prog(t, t0 + .8, t0 + 1.3));
  if (ul > 0) { ctx.fillStyle = R.orange; ctx.fillRect(W / 2 - 380, 975, 760 * ul, 7); }
  scramble(t, t0 + 1.0, 'BIZNESINGIZ HIMOYACHISI', W / 2, 1035, 26, R.off, { dur: .8, track: .32 });
  withAlpha(prog(t, t0 + 1.3, t0 + 1.7), () => serif('Telegram reklama ekotizimi', W / 2, 1110, 58, R.off));
  const cta = eBack(prog(t, t0 + 1.6, t0 + 2.0));
  if (cta > 0) scaled(W / 2, 1290, cta * (1 + .03 * Math.sin(t * 6)), () => {
    rr(W / 2 - 300, 1240, 600, 100, 50); ctx.fillStyle = R.orange; ctx.fill();
    text('Hoziroq sinab koʻring', W / 2, 1292, 40, R.ink, 900, 'center', 'middle');
  });
}

// Transition (24-qism): palette tiles pop in on a radial wave over A, a serif word flashes on the full grid,
// then the tiles pop out on the same wave revealing B. word: shown mid-way.
function gridWave(t, a, b, drawA, drawB, word = '') {
  const p = prog(t, a, b), cx = W / 2, cy = H / 2, maxD = Math.hypot(W / 2, H / 2);
  (p < .5 ? drawA : drawB)(t);
  let k = 0;
  for (let j = -1; j * GRID_GAP < H + GRID_GAP; j++) for (let i = 0; i < GRID_COLS; i++, k++) {
    const x = (i + .5) * GRID_GAP, y = (j + .5) * GRID_GAP, d = Math.hypot(x - cx, y - cy) / maxD;
    const inn = clamp((p * 2.2 - d * .9) / .35), outp = clamp(((p - .55) * 2.4 - d * .9) / .35);
    const s = GRID_GAP * 1.04 * eBack(inn) * (1 - eIn(outp)); if (s <= .5) continue;
    ctx.save(); ctx.translate(x, y); ctx.rotate((1 - inn) * 1.2 + outp * 1.2);
    rr(-s / 2, -s / 2, s, s, s * .28 * (1 - .8 * inn * (1 - outp))); ctx.fillStyle = GRID_C[k % GRID_C.length]; ctx.fill(); ctx.restore();
  }
  if (word) { const wp = Math.sin(Math.PI * clamp((p - .32) / .4)); if (wp > 0) withAlpha(wp, () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 30; serif(word, W / 2 - 6, H / 2, 210, R.violet); serif(word, W / 2 + 6, H / 2, 210, R.orange); serif(word, W / 2, H / 2, 210, R.off); ctx.restore(); }); }
}
