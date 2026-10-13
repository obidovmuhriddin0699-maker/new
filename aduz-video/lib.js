// Shared building blocks for the ADUZ episode videos.
// An episode page defines its scenes and captions, then calls boot({...}).
// Requires <canvas id="c" width="1080" height="1920"> before this script.

const W = 1080, H = 1920;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const F = 'Inter, "DejaVu Sans", sans-serif';

const C = {
  navy: '#0b1020', red: '#ff3b4e', redDim: '#7a1422',
  green: '#16c784', greenDeep: '#063b30', teal: '#0a5c4a',
  gold: '#ffc83d', ink: '#0f172a', grey: '#64748b', paper: '#ffffff',
};


// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const prog = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, p) => a + (b - a) * p;
const eOut = p => 1 - Math.pow(1 - p, 3);
const eInOut = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); };
function rnd(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

function rr(x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function text(s, x, y, size, color, weight = 600, align = 'left', base = 'alphabetic') {
  ctx.font = `${weight} ${size}px ${F}`; ctx.fillStyle = color;
  ctx.textAlign = align; ctx.textBaseline = base; ctx.fillText(s, x, y);
}
function wrap(s, maxW, size, weight = 500) {
  ctx.font = `${weight} ${size}px ${F}`;
  const words = s.split(' '), lines = []; let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (ctx.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; } else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
}
function check(x, y, s, color, lw, p = 1) {
  // tick drawn progressively (p 0..1)
  const pts = [[x - s * .5, y], [x - s * .15, y + s * .35], [x + s * .55, y - s * .4]];
  const l1 = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
  const l2 = Math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]);
  let d = (l1 + l2) * p;
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(...pts[0]);
  if (d <= l1) { const k = d / l1; ctx.lineTo(lerp(pts[0][0], pts[1][0], k), lerp(pts[0][1], pts[1][1], k)); }
  else { ctx.lineTo(...pts[1]); const k = (d - l1) / l2; ctx.lineTo(lerp(pts[1][0], pts[2][0], k), lerp(pts[1][1], pts[2][1], k)); }
  ctx.stroke();
}
function cross(x, y, s, color, lw) {
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - s, y - s); ctx.lineTo(x + s, y + s);
  ctx.moveTo(x + s, y - s); ctx.lineTo(x - s, y + s); ctx.stroke();
}
function withAlpha(a, fn) { ctx.save(); ctx.globalAlpha *= clamp(a); fn(); ctx.restore(); }
function scaled(cx, cy, s, fn) { ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.translate(-cx, -cy); fn(); ctx.restore(); }

// Phone frame
const PX = 150, PY = 360, PW = 780, PH = 1180, PR = 80, SI = 22;
const SX = PX + SI, SY = PY + SI, SW = PW - 2 * SI, SH = PH - 2 * SI;
function phone(screenFill, dx = 0, dy = 0, rot = 0, drawScreen) {
  ctx.save();
  ctx.translate(PX + PW / 2 + dx, PY + PH / 2 + dy); ctx.rotate(rot); ctx.translate(-PX - PW / 2, -PY - PH / 2);
  ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 30;
  rr(PX, PY, PW, PH, PR); ctx.fillStyle = '#11151c'; ctx.fill();
  ctx.shadowColor = 'transparent';
  rr(SX, SY, SW, SH, PR - SI); ctx.fillStyle = screenFill; ctx.fill();
  ctx.save(); rr(SX, SY, SW, SH, PR - SI); ctx.clip(); drawScreen(); ctx.restore();
  rr(PX + PW / 2 - 90, PY + 34, 180, 34, 17); ctx.fillStyle = '#11151c'; ctx.fill();
  ctx.restore();
}

// Captions (subtitles = diktor matni)
function captions(t, list) {
  for (const [a, b, s] of list) {
    if (t < a || t > b) continue;
    const al = Math.min(prog(t, a, a + .25), 1 - prog(t, b - .25, b));
    const lines = wrap(s, 880, 46, 700);
    const lh = 60, h = lines.length * lh + 44, y = 1745 - h / 2;
    withAlpha(al, () => {
      rr(80, y, 920, h, 28); ctx.fillStyle = 'rgba(5,8,15,.78)'; ctx.fill();
      lines.forEach((l, i) => text(l, W / 2, y + 22 + lh * i + lh / 2 + 2, 46, '#fff', 700, 'center', 'middle'));
    });
  }
}

// ---------- shared UI ----------
function logo(x, y, s, light = false) {
  rr(x, y, 96 * s, 96 * s, 26 * s);
  const g = ctx.createLinearGradient(x, y, x + 96 * s, y + 96 * s);
  g.addColorStop(0, '#22e39a'); g.addColorStop(1, '#0ea371'); ctx.fillStyle = g; ctx.fill();
  // stylised shield + check
  ctx.save(); ctx.translate(x + 48 * s, y + 48 * s); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -30); ctx.lineTo(26, -20); ctx.lineTo(24, 8); ctx.quadraticCurveTo(18, 26, 0, 34);
  ctx.quadraticCurveTo(-18, 26, -24, 8); ctx.lineTo(-26, -20); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill();
  check(1, 2, 26, '#0ea371', 7);
  ctx.restore();
  text('ADUZ', x + 116 * s, y + 66 * s, 64 * s, light ? C.ink : '#fff', 900);
}
function cursor(x, y, press) {
  ctx.beginPath(); ctx.arc(x, y, 34 - 8 * press, 0, 7);
  ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.fill();
  ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(15,23,42,.35)'; ctx.stroke();
}
function ripple(x, y, p, color) {
  if (p <= 0 || p >= 1) return;
  ctx.beginPath(); ctx.arc(x, y, 30 + 140 * eOut(p), 0, 7);
  ctx.strokeStyle = color; ctx.globalAlpha = 1 - p; ctx.lineWidth = 6; ctx.stroke(); ctx.globalAlpha = 1;
}const CONFETTI = (() => { const r = rnd(42); return Array.from({ length: 90 }, () => ({ x: r() * W, vx: (r() - .5) * 240, vy: 300 + r() * 500, rot: r() * 6, vr: (r() - .5) * 10, c: ['#ffc83d', '#16c784', '#ffffff', '#22e39a'][Math.floor(r() * 4)], s: 12 + r() * 14, d: r() * .8 })); })();
function shield(x, y, s, fill) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(0, -30); ctx.lineTo(26, -20); ctx.lineTo(24, 8); ctx.quadraticCurveTo(18, 26, 0, 34);
  ctx.quadraticCurveTo(-18, 26, -24, 8); ctx.lineTo(-26, -20); ctx.closePath(); ctx.fillStyle = fill; ctx.fill(); ctx.restore();
}
// Natija background: green → gold gradient with slowly rotating light rays.
function resultBg(t) {
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, '#0b5a46'); g.addColorStop(.55, '#0ea371'); g.addColorStop(1, '#f2c14e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // god rays
  ctx.save(); ctx.translate(W / 2, 760); ctx.rotate(t * .15);
  for (let i = 0; i < 12; i++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-90, -1400); ctx.lineTo(90, -1400); ctx.closePath(); ctx.fillStyle = 'rgba(255,255,255,.045)'; ctx.fill(); }
  ctx.restore();
}
// Gold medal with shield + tick; label may contain '\n'. p = pop-in progress (eBack'd).
function goldBadge(bx, by, s, p) {
  scaled(bx, by, p, () => {
    ctx.save(); ctx.shadowColor = 'rgba(255,200,61,.8)'; ctx.shadowBlur = 40;
    ctx.beginPath(); ctx.arc(bx, by, 95, 0, 7);
    const gg = ctx.createLinearGradient(bx - 95, by - 95, bx + 95, by + 95);
    gg.addColorStop(0, '#ffe08a'); gg.addColorStop(1, '#f5a524'); ctx.fillStyle = gg; ctx.fill(); ctx.restore();
    ctx.beginPath(); ctx.arc(bx, by, 78, 0, 7); ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.stroke();
    shield(bx, by, 1.5, '#fff'); check(bx + 1, by + 3, 38, '#f5a524', 9);
    s.split('\n').forEach((l, k) => text(l, bx, by + 150 + k * 40, 32, '#fff', 800, 'center'));
  });
}
function confetti(t, start) {
  if (t <= start) return;
  for (const c of CONFETTI) {
    const tt = t - start - c.d; if (tt < 0) continue;
    const x = c.x + c.vx * tt, y = -40 + c.vy * tt;
    if (y > H + 40) continue;
    ctx.save(); ctx.translate(x, y); ctx.rotate(c.rot + c.vr * tt); ctx.fillStyle = c.c;
    ctx.fillRect(-c.s / 2, -c.s / 4, c.s, c.s / 2); ctx.restore();
  }
}
// Closing card: logo with shine, slogan, CTA. Starts at t0 and needs ~1.8 s to settle.
function endCard(t, t0) {
  const ep = prog(t, t0, t0 + .6);
  if (ep <= 0) return;
  const s = eBack(ep);
  withAlpha(ep, () => scaled(W / 2, 780, s * 1.7, () => logo(W / 2 - 205, 732, 1)));
  // shine sweep
  const sh = prog(t, t0 + .8, t0 + 1.6);
  if (sh > 0 && sh < 1) {
    ctx.save(); ctx.beginPath(); ctx.rect(W / 2 - 360, 680, 720, 200); ctx.clip();
    const sx = lerp(W / 2 - 500, W / 2 + 500, sh);
    const lg = ctx.createLinearGradient(sx - 80, 0, sx + 80, 0);
    lg.addColorStop(0, 'rgba(255,255,255,0)'); lg.addColorStop(.5, 'rgba(255,255,255,.55)'); lg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = lg; ctx.fillRect(W / 2 - 360, 680, 720, 200); ctx.restore();
  }
  withAlpha(prog(t, t0 + .6, t0 + 1.1), () => {
    text('Biznesingiz himoyachisi!', W / 2, 1010, 62, '#fff', 900, 'center');
    text('Fargʻona vodiysi uchun', W / 2, 1085, 36, '#e7fff5', 600, 'center');
    text('Telegram reklama ekotizimi', W / 2, 1132, 36, '#e7fff5', 600, 'center');
  });
  const cta = eBack(prog(t, t0 + 1.3, t0 + 1.8));
  if (cta > 0) scaled(W / 2, 1290, cta * (1 + .03 * Math.sin(t * 6)), () => {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.25)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
    rr(W / 2 - 300, 1240, 600, 104, 52); ctx.fillStyle = '#fff'; ctx.fill(); ctx.restore();
    text('Hoziroq sinab koʻring', W / 2, 1293, 40, '#0b5a46', 900, 'center', 'middle');
  });
}

// ---------- compositor ----------
function circleWipe(t, a, b, drawA, drawB, color) {
  const p = eInOut(prog(t, a, b));
  drawA(t);
  ctx.save(); ctx.beginPath(); ctx.arc(W / 2, H / 2, p * 1200, 0, 7); ctx.clip(); drawB(t); ctx.restore();
  if (color && p > 0 && p < 1) { ctx.beginPath(); ctx.arc(W / 2, H / 2, p * 1200, 0, 7); ctx.lineWidth = 24; ctx.strokeStyle = color; ctx.stroke(); }
}

// Every episode: scene1 0-11 s (Muammo), scene2 11-22 s (Yechim), scene3 22-32 s (Natija).
function boot({ scene1, scene2, scene3, captions: caps, duration = 32 }) {
  function renderFrame(t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
    if (t < 10.7) scene1(t);
    else if (t < 11.3) circleWipe(t, 10.7, 11.3, scene1, scene2, '#22e39a');
    else if (t < 21.9) scene2(t);
    else if (t < 22.4) circleWipe(t, 21.9, 22.4, scene2, scene3, '#ffc83d');
    else scene3(t);
    captions(t, caps);
    // fade from/to black
    const fb = Math.max(1 - prog(t, 0, .4), prog(t, duration - .5, duration));
    if (fb > 0) { ctx.fillStyle = `rgba(0,0,0,${fb})`; ctx.fillRect(0, 0, W, H); }
  }
  window.renderFrame = renderFrame;
  window.DURATION = duration;
  // Browser preview: loop playback unless driven by the renderer.
  if (!location.search.includes('render')) {
    const t0 = performance.now();
    (function loop() { renderFrame(((performance.now() - t0) / 1000) % duration); requestAnimationFrame(loop); })();
  }
}
