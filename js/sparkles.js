/* ==========================================================================
   sparkles.js — a few warm lights rising and rose petals drifting down.
   One small <canvas> per [data-sparkles] element; it only animates while on
   screen and the tab is visible. Disabled for "reduce motion".
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
  const petalsOn = canvas.dataset.sparkles.includes("petals");
  let w = 0, h = 0, dpr = 1, lights = [], petals = [], raf = 0, visible = false, last = 0;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const area = (w * h) / (390 * 844);
    lights = Array.from({ length: Math.round(14 + 10 * Math.min(area, 2.5)) }, () => light(true));
    petals = petalsOn ? Array.from({ length: Math.round(5 + 4 * Math.min(area, 2.5)) }, () => petal(true)) : [];
  }

  const light = (anywhere) => ({
    x: rand(0, w), y: anywhere ? rand(0, h) : h + 20,
    r: rand(1.2, 3.6), vy: rand(6, 18), sway: rand(0.4, 1.2), phase: rand(0, 6.28),
    a: rand(0.25, 0.75), tw: rand(0.6, 1.6)
  });
  const petal = (anywhere) => ({
    x: rand(0, w), y: anywhere ? rand(-h, h) : rand(-60, -20),
    s: rand(6, 11), vy: rand(14, 30), vx: rand(-8, 8), rot: rand(0, 6.28), vr: rand(-0.8, 0.8),
    phase: rand(0, 6.28), hue: rand(342, 358)
  });

  function draw(t) {
    raf = visible ? requestAnimationFrame(draw) : 0;
    const dt = Math.min(0.05, (t - (last || t)) / 1000); last = t;
    ctx.clearRect(0, 0, w, h);
    const time = t / 1000;

    ctx.globalCompositeOperation = "lighter";
    for (const p of lights) {
      p.y -= p.vy * dt;
      const x = p.x + Math.sin(time * p.sway + p.phase) * 12;
      if (p.y < -20) Object.assign(p, light(false));
      const a = p.a * (0.55 + 0.45 * Math.sin(time * p.tw + p.phase));
      const g = ctx.createRadialGradient(x, p.y, 0, x, p.y, p.r * 6);
      g.addColorStop(0, `rgba(255, 236, 205, ${a})`);
      g.addColorStop(0.35, `rgba(244, 205, 160, ${a * 0.35})`);
      g.addColorStop(1, "rgba(244, 205, 160, 0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(x, p.y, p.r * 6, 0, 6.283); ctx.fill();
    }

    ctx.globalCompositeOperation = "source-over";
    for (const p of petals) {
      p.y += p.vy * dt; p.x += (p.vx + Math.sin(time + p.phase) * 14) * dt; p.rot += p.vr * dt;
      if (p.y > h + 30) Object.assign(p, petal(false));
      const flip = Math.cos(time * 1.3 + p.phase);              // petal turning in the air
      ctx.save();
      ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.scale(1, 0.35 + 0.65 * Math.abs(flip));
      const g = ctx.createLinearGradient(0, -p.s, 0, p.s);
      g.addColorStop(0, `hsla(${p.hue}, 70%, 88%, 0.95)`);
      g.addColorStop(1, `hsla(${p.hue}, 55%, 70%, 0.9)`);
      ctx.fillStyle = g;
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
