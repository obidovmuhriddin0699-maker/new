/* ==========================================================================
   sparkles.js — gold dust and blush petals drifting down.
   <canvas data-sparkles="dust petals">; animates only while on screen.
   ========================================================================== */
import { reducedMotion } from "./data.js";

const rand = (a, b) => a + Math.random() * (b - a);

export function initSparkles() {
  if (reducedMotion) return;
  document.querySelectorAll("canvas[data-sparkles]").forEach(scene);
}

function scene(canvas) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const mode = canvas.dataset.sparkles;
  let w = 0, h = 0, dust = [], petals = [], raf = 0, visible = false, last = 0;

  const mkDust = (any) => ({
    x: rand(0, w), y: any ? rand(0, h) : -10, r: rand(0.6, 2.2), vy: rand(8, 24), sway: rand(0.3, 1), ph: rand(0, 6.3),
    a: rand(0.35, 0.95), tw: rand(1, 2.6)
  });
  const mkPetal = (any) => ({
    x: rand(0, w), y: any ? rand(-h, h) : rand(-60, -20), s: rand(5, 9), vy: rand(14, 28), vx: rand(-6, 6),
    rot: rand(0, 6.3), vr: rand(-0.9, 0.9), ph: rand(0, 6.3), hue: rand(345, 360), l: rand(82, 90)
  });

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const area = Math.min(2.5, (w * h) / (390 * 844));
    dust = mode.includes("dust") ? Array.from({ length: Math.round(26 + 22 * area) }, () => mkDust(true)) : [];
    petals = mode.includes("petals") ? Array.from({ length: Math.round(5 + 4 * area) }, () => mkPetal(true)) : [];
  }

  function draw(now) {
    raf = visible ? requestAnimationFrame(draw) : 0;
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    const time = now / 1000;
    ctx.clearRect(0, 0, w, h);
    for (const p of dust) {
      p.y += p.vy * dt;
      if (p.y > h + 10) Object.assign(p, mkDust(false));
      const x = p.x + Math.sin(time * p.sway + p.ph) * 10;
      const a = p.a * (0.55 + 0.45 * Math.sin(time * p.tw + p.ph));
      ctx.fillStyle = `rgba(214, 178, 108, ${a})`;
      ctx.beginPath(); ctx.arc(x, p.y, p.r, 0, 6.283); ctx.fill();
      if (p.r > 1.6) {                                   // a few catch the light
        ctx.fillStyle = `rgba(255, 240, 205, ${a * 0.35})`;
        ctx.beginPath(); ctx.arc(x, p.y, p.r * 3, 0, 6.283); ctx.fill();
      }
    }
    for (const p of petals) {
      p.y += p.vy * dt; p.x += (p.vx + Math.sin(time + p.ph) * 12) * dt; p.rot += p.vr * dt;
      if (p.y > h + 30) Object.assign(p, mkPetal(false));
      const flip = Math.cos(time * 1.4 + p.ph);
      ctx.save();
      ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.scale(1, 0.35 + 0.65 * Math.abs(flip));
      ctx.fillStyle = `hsla(${p.hue}, 60%, ${p.l}%, 0.9)`;
      ctx.beginPath();
      ctx.moveTo(0, -p.s);
      ctx.bezierCurveTo(p.s * 0.9, -p.s * 0.6, p.s * 0.7, p.s * 0.8, 0, p.s);
      ctx.bezierCurveTo(-p.s * 0.7, p.s * 0.8, -p.s * 0.9, -p.s * 0.6, 0, -p.s);
      ctx.fill();
      ctx.restore();
    }
  }
  const start = () => { if (!raf && visible && !document.hidden) { last = 0; raf = requestAnimationFrame(draw); } };
  const stop = () => { cancelAnimationFrame(raf); raf = 0; };
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; visible ? start() : stop(); }).observe(canvas);
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
  let rt = 0;
  window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(resize, 200); }, { passive: true });
  resize();
}
