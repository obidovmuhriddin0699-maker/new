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

// ---------- scene building blocks ----------
const fmt = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
const bump = (t, at, len = .15) => prog(t, at, at + len / 2) * (1 - prog(t, at + len / 2, at + len));

// Eased cursor path through keyframes [[time, x, y], ...].
function pathAt(t, keys) {
  if (t <= keys[0][0]) return [keys[0][1], keys[0][2]];
  for (let i = 1; i < keys.length; i++) {
    const [t1, x1, y1] = keys[i], [t0, x0, y0] = keys[i - 1];
    if (t <= t1) { const p = eInOut(prog(t, t0, t1)); return [lerp(x0, x1, p), lerp(y0, y1, p)]; }
  }
  const k = keys[keys.length - 1]; return [k[1], k[2]];
}

// Muammo background: dark navy turning red as stress (0..1) grows, with a pulsing vignette.
function problemBg(t, stress) {
  const g = ctx.createRadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 1300);
  g.addColorStop(0, '#141a2e'); g.addColorStop(1, `rgba(${Math.round(lerp(11, 90, stress))},16,32,1)`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  const pulse = stress * (0.25 + 0.25 * Math.sin(t * 9));
  const v = ctx.createRadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1200);
  v.addColorStop(0, 'rgba(255,40,60,0)'); v.addColorStop(1, `rgba(255,40,60,${pulse})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}
function episodeTitle(t, label, title, size) {
  withAlpha(prog(t, 0, .5), () => {
    text(label, W / 2, 120, 34, C.red, 800, 'center');
    text(title, W / 2, 185, size, '#fff', 800, 'center');
  });
}
// Row of three stat tiles under the title: [[value, label, color], ...].
function counters(t, items) {
  withAlpha(prog(t, .6, 1.2), () => {
    items.forEach(([a, b, col], i) => {
      const x = 200 + i * 340;
      rr(x - 150, 228, 300, 100, 22); ctx.fillStyle = 'rgba(255,255,255,.07)'; ctx.fill();
      text(a, x, 278, 44, col, 800, 'center');
      text(b, x, 312, 26, '#94a3b8', 500, 'center');
    });
  });
}
// Red warning stickers: [[time, label, x, y, rotation], ...].
function errorBadges(t, list) {
  for (const [at, s, x, y, r] of list) {
    const p = prog(t, at, at + .4);
    if (p <= 0) continue;
    ctx.save(); ctx.translate(x + 170, y + 45); ctx.rotate(r + Math.sin(t * 8 + x) * .02);
    ctx.scale(eBack(p), eBack(p));
    ctx.font = `800 32px ${F}`; const bw = ctx.measureText(s).width + 130;
    ctx.shadowColor = 'rgba(255,40,60,.6)'; ctx.shadowBlur = 30;
    rr(-bw / 2, -48, bw, 96, 24); ctx.fillStyle = C.red; ctx.fill(); ctx.shadowBlur = 0;
    ctx.beginPath(); ctx.arc(-bw / 2 + 52, 0, 26, 0, 7); ctx.fillStyle = '#fff'; ctx.fill();
    cross(-bw / 2 + 52, 0, 10, C.red, 7);
    text(s, -bw / 2 + 94, 2, 32, '#fff', 800, 'left', 'middle');
    ctx.restore();
  }
}
// Yechim background with drifting light blobs, ADUZ logo and a subtitle under it.
function solutionBg(t, subtitle) {
  const g = ctx.createLinearGradient(0, 0, W, H);
  g.addColorStop(0, '#04261f'); g.addColorStop(1, '#0b5a46'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 3; i++) {
    const bx = 200 + i * 340 + Math.sin(t * .6 + i) * 60, by = 500 + i * 380;
    const b = ctx.createRadialGradient(bx, by, 0, bx, by, 420);
    b.addColorStop(0, 'rgba(34,227,154,.18)'); b.addColorStop(1, 'rgba(34,227,154,0)');
    ctx.fillStyle = b; ctx.fillRect(0, 0, W, H);
  }
  const lp = eBack(prog(t, 11.2, 11.9));
  withAlpha(prog(t, 11.2, 11.6), () => scaled(W / 2, 200, lp, () => logo(W / 2 - 205, 150, 1)));
  withAlpha(prog(t, 11.8, 12.3), () => text(subtitle, W / 2, 310, 34, '#a7f3d0', 600, 'center'));
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


// ---------- motion toolkit (4-qismdan boshlab) ----------
const eIn = p => p * p * p;
// Draws fn under a camera: zoom/rotation about (cx, cy) plus a screen offset.
function camera(zoom, rot, dx, dy, fn, cx = W / 2, cy = H / 2) {
  ctx.save(); ctx.translate(cx + dx, cy + dy); ctx.rotate(rot); ctx.scale(zoom, zoom); ctx.translate(-cx, -cy);
  fn(); ctx.restore();
}
// Decaying camera shake from impacts [[time, amplitude px], …] → [dx, dy, rot].
function shakeAt(t, impacts) {
  let x = 0, y = 0, r = 0;
  for (const [at, a] of impacts) {
    const d = t - at; if (d < 0 || d > 1.2) continue;
    const e = Math.exp(-d * 7) * a;
    x += Math.sin(d * 61) * e; y += Math.cos(d * 47) * e * .8; r += Math.sin(d * 38) * e * .0009;
  }
  return [x, y, r];
}
function shockwave(t, at, x, y, color, maxR = 900) {
  const p = prog(t, at, at + .7);
  if (p <= 0 || p >= 1) return;
  withAlpha(1 - p, () => {
    ctx.beginPath(); ctx.arc(x, y, maxR * eOut(p), 0, 7);
    ctx.lineWidth = 36 * (1 - p) + 2; ctx.strokeStyle = color; ctx.stroke();
  });
}
function flash(t, at, color = '#ffffff', len = .35, peak = .8) {
  const p = prog(t, at, at + len);
  if (p <= 0 || p >= 1) return;
  withAlpha(peak * (1 - eOut(p)), () => { ctx.fillStyle = color; ctx.fillRect(0, 0, W, H); });
}
// Burst of streaking sparks with gravity.
function sparks(t, at, x, y, seed, colors, n = 28, speed = 950) {
  const d = t - at; if (d < 0 || d > 1.3) return;
  const r = rnd(seed);
  ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const ang = r() * Math.PI * 2, v = speed * (.35 + r() * .65), life = .55 + r() * .6;
    if (d > life) continue;
    const k = 1 - d / life, px = x + Math.cos(ang) * v * d, py = y + Math.sin(ang) * v * d + 600 * d * d;
    const tx = px - Math.cos(ang) * v * .035, ty = py - (Math.sin(ang) * v + 1200 * d) * .035;
    withAlpha(k, () => {
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(tx, ty);
      ctx.lineWidth = 7 * k + 1; ctx.strokeStyle = colors[i % colors.length]; ctx.stroke();
    });
  }
}
// Kinetic "slam" word: drops in from 2.4x with overshoot and a scale motion trail, holds, then punches out.
function slam(t, at, s, x, y, size, color, o = {}) {
  const { hold = 1.2, rot = 0, slab = null, glow = 'rgba(0,0,0,.45)' } = o;
  const p = prog(t, at, at + .3), q = prog(t, at + hold, at + hold + .25);
  if (p <= 0 || q >= 1) return;
  const a = clamp(p * 4) * (1 - q), base = ctx.globalAlpha;
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.font = `900 ${size}px ${F}`; const w = ctx.measureText(s).width;
  const draw = alpha => {
    ctx.globalAlpha = base * alpha;
    if (slab) { rr(-w / 2 - size * .45, -size * .68, w + size * .9, size * 1.36, size * .24); ctx.fillStyle = slab; ctx.fill(); }
    text(s, 0, size * .04, size, color, 900, 'center', 'middle');
  };
  if (p < 1) for (let k = 3; k >= 1; k--) {
    const sk = lerp(2.4, 1, eBack(clamp(p - k * .09)));
    ctx.save(); ctx.scale(sk, sk); draw(a * .13 * (4 - k)); ctx.restore();
  }
  const sc = lerp(2.4, 1, eBack(p)) * (1 + .3 * eIn(q));
  ctx.scale(sc, sc); ctx.shadowColor = glow; ctx.shadowBlur = 40; draw(a);
  ctx.restore();
}
// Analog clock: minuteTurns = full turns of the minute hand; secTicks = second-hand position in ticks.
function bigClock(cx, cy, R, minuteTurns, secTicks, color, alpha) {
  withAlpha(alpha, () => {
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.lineWidth = 10; ctx.stroke();
    for (let i = 0; i < 60; i++) {
      const a = i / 60 * Math.PI * 2, l = i % 5 ? 22 : 54;
      ctx.beginPath(); ctx.moveTo(cx + Math.sin(a) * (R - 26), cy - Math.cos(a) * (R - 26));
      ctx.lineTo(cx + Math.sin(a) * (R - 26 - l), cy - Math.cos(a) * (R - 26 - l));
      ctx.lineWidth = i % 5 ? 4 : 10; ctx.stroke();
    }
    const hand = (a, l, w) => { ctx.beginPath(); ctx.moveTo(cx - Math.sin(a) * 40, cy + Math.cos(a) * 40); ctx.lineTo(cx + Math.sin(a) * l, cy - Math.cos(a) * l); ctx.lineWidth = w; ctx.stroke(); };
    hand(minuteTurns / 12 * Math.PI * 2, R * .5, 20);
    hand(minuteTurns * Math.PI * 2, R * .78, 12);
    ctx.strokeStyle = C.red; hand(secTicks / 60 * Math.PI * 2, R * .86, 5);
    ctx.beginPath(); ctx.arc(cx, cy, 20, 0, 7); ctx.fill();
  });
}
// Transition: a clock hand sweeps round, revealing drawB behind it.
function clockWipe(t, a, b, drawA, drawB, color) {
  const p = eInOut(prog(t, a, b)), ang = -Math.PI / 2 + p * Math.PI * 2, cx = W / 2, cy = H / 2;
  drawA(t);
  ctx.save(); ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, 2400, -Math.PI / 2, ang); ctx.closePath(); ctx.clip(); drawB(t); ctx.restore();
  if (p > 0 && p < 1) {
    ctx.save(); ctx.shadowColor = color; ctx.shadowBlur = 50;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(ang) * 2400, cy + Math.sin(ang) * 2400);
    ctx.lineWidth = 18; ctx.strokeStyle = color; ctx.lineCap = 'round'; ctx.stroke();
    ctx.beginPath(); ctx.arc(cx, cy, 34, 0, 7); ctx.fillStyle = color; ctx.fill(); ctx.restore();
  }
}
// Transition: push into drawA, white flash, land on drawB.
function zoomThrough(t, a, b, drawA, drawB) {
  const p = prog(t, a, b);
  if (p < .5) camera(1 + .7 * eIn(p * 2), 0, 0, 0, () => drawA(t));
  else camera(lerp(1.35, 1, eOut((p - .5) * 2)), 0, 0, 0, () => drawB(t));
  withAlpha(Math.pow(1 - Math.abs(p - .5) * 2, 2), () => { ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H); });
}
// Transition: the frame breaks into square cells that flip to drawB, rippling out from (ox, oy).
const PIXEL_CELLS = (() => {
  const r = rnd(17), cells = [], size = 90;
  for (let y = 0; y < H; y += size) for (let x = 0; x < W; x += size) cells.push({ x, y, size, j: r() * .25 });
  return cells;
})();
function pixelDissolve(t, a, b, drawA, drawB, color, ox = W / 2, oy = H / 2) {
  const p = prog(t, a, b), maxD = Math.hypot(W, H) * .62;
  drawA(t);
  const live = [];
  ctx.save(); ctx.beginPath();
  for (const c of PIXEL_CELLS) {
    const d = Math.hypot(c.x + c.size / 2 - ox, c.y + c.size / 2 - oy) / maxD;
    const q = clamp((p * 1.35 - d * .9 - c.j * .4) / .25);
    if (q <= 0) continue;
    const s = c.size * eOut(q), cx = c.x + c.size / 2, cy = c.y + c.size / 2;
    ctx.rect(cx - s / 2, cy - s / 2, s, s);
    if (q < 1) live.push([cx, cy, s, q]);
  }
  ctx.clip(); drawB(t); ctx.restore();
  for (const [cx, cy, s, q] of live) withAlpha(1 - q, () => { ctx.fillStyle = color; ctx.fillRect(cx - s / 2, cy - s / 2, s, s); });
}
// Film grain + vignette, frame-stable for rendering.
let GRAIN = null;
function filmLook(t, grain = .07, vignette = .38) {
  if (!GRAIN) {
    GRAIN = document.createElement('canvas'); GRAIN.width = GRAIN.height = 256;
    const g = GRAIN.getContext('2d'), img = g.createImageData(256, 256), r = rnd(3);
    for (let i = 0; i < img.data.length; i += 4) { const v = 70 + r() * 115; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    g.putImageData(img, 0, 0);
  }
  const f = Math.floor(t * 24), ox = (f * 7919) % 256, oy = (f * 104729) % 256;
  ctx.save(); ctx.globalAlpha = grain; ctx.globalCompositeOperation = 'overlay';
  ctx.translate(-ox, -oy); ctx.fillStyle = ctx.createPattern(GRAIN, 'repeat'); ctx.fillRect(0, 0, W + 256, H + 256);
  ctx.restore();
  const v = ctx.createRadialGradient(W / 2, H / 2, 600, W / 2, H / 2, 1250);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, `rgba(0,0,0,${vignette})`);
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
}

// Every episode: scene1 0-11 s (Muammo), scene2 11-22 s (Yechim), scene3 22-32 s (Natija).
// transitions: optional [{ a, b, fn(t, a, b, drawA, drawB) }, …] for the 1→2 and 2→3 cuts.
// overlay: optional fn(t) drawn over the scenes, under the captions (grain, vignette…).
const DEFAULT_TRANSITIONS = [
  { a: 10.7, b: 11.3, fn: (t, a, b, A, B) => circleWipe(t, a, b, A, B, '#22e39a') },
  { a: 21.9, b: 22.4, fn: (t, a, b, A, B) => circleWipe(t, a, b, A, B, '#ffc83d') },
];
function boot({ scene1, scene2, scene3, captions: caps, duration = 32, transitions = DEFAULT_TRANSITIONS, overlay = null }) {
  const [t1, t2] = transitions;
  function renderFrame(t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
    if (t < t1.a) scene1(t);
    else if (t < t1.b) t1.fn(t, t1.a, t1.b, scene1, scene2);
    else if (t < t2.a) scene2(t);
    else if (t < t2.b) t2.fn(t, t2.a, t2.b, scene2, scene3);
    else scene3(t);
    if (overlay) overlay(t);
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
