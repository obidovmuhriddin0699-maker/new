// "Qisqa" Reels (2026-10-27, OSISH_REJASI.md 4-band): 18 s, one idea, the real bot screen — the format of the
// best-performing post (10-23, bot screen: 31 % skip vs 80 %+ for the 32 s series). Loaded after lib.js, reel.js and
// igbot.js; the page sets window.SHORT = { hook: [label, line1, line2, sub], bot: {seq, focus}, caps, cta: [l1, l2] }.
//   0–2.2 s    hook card (frame 0 — no fade, loop target)
//   2.2–14.2 s real bot flow in the phone (IGBOT.scene, its 11.0–23 s timeline shifted to start at 2.2 s)
//   14.2–18 s  CTA card: comment keyword + bot handle + follow
(function () {
  const S = window.SHORT, DUR = 18, OFF = 10.95 - 2.2, ARCH = 'Archivo, Inter, "DejaVu Sans", sans-serif';
  FD = null;

  function fitHeavy(t, at, s, x, y, size, maxW, color, o = {}) {
    ctx.save(); ctx.font = `900 ${size}px ${ARCH}`; ctx.letterSpacing = `${(-size * .03).toFixed(1)}px`; const w = ctx.measureText(s).width; ctx.restore();
    heavy(t, at, s, x, y, Math.min(size, size * maxW / Math.max(1, w)), color, o);
  }
  function hook(t) {
    const [label, l1, l2, sub] = S.hook;
    ctx.fillStyle = R.orange; ctx.fillRect(0, 0, W, H);
    dotGrid(t + 40, .1, .42, 1, 480, 820);
    mono(label, 480, 470, 28, R.ink, 'center', .4, 800);
    fitHeavy(t, -.3, l1, 480, 690, 220, 820, R.ink, { rot: -.15, endRot: -.03 });
    fitHeavy(t, -.2, l2, 480, 900, 220, 820, R.ink, { rot: .12, endRot: .02 });
    serif(sub, 480, 1090, 64, R.ink);
  }
  function cta(t) {
    const a = 14.2, p = eOut(prog(t, a, a + .35));
    ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H);
    dotGrid(t, .08, .4, 1, 480, 800);
    withAlpha(p, () => {
      mono('IZOHGA YOZING', 480, 470, 28, R.lime, 'center', .4, 800);
      fitHeavy(t, a + .1, S.cta[0], 480, 680, 260, 800, R.off, { rot: -.1, endRot: -.02 });
      serif(S.cta[1], 480, 860, 60, R.lime);
      rr(130, 980, 700, 110, 55); ctx.fillStyle = R.orange; ctx.fill();
      mono('@TARGETREKLAMMABOT', 480, 1036, 34, R.ink, 'center', .12, 800);
      const q = eBack(prog(t, a + .9, a + 1.3));
      if (q > 0) scaled(480, 1200, q, () => { rr(230, 1155, 500, 90, 45); ctx.fillStyle = R.lime; ctx.fill(); mono('OBUNA BOʻLING', 480, 1201, 30, R.ink, 'center', .2, 800); });
    });
  }
  function renderFrame(t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H);
    if (t < 2.2) hook(t);
    else if (t < 14.2) IGBOT.scene(t + OFF, S);
    else cta(t);
    // 0.25 s whip between sections
    [2.2, 14.2].forEach(at => { const k = 1 - Math.abs(t - at) / .12; if (k > 0) { ctx.fillStyle = `rgba(14,13,15,${Math.min(1, k)})`; ctx.fillRect(0, 0, W, H); } });
    if (t > DUR - .25) { withAlpha(prog(t, DUR - .25, DUR), () => hook(0)); }
    igCaptions(t, S.caps);
  }
  window.renderFrame = renderFrame;
  window.DURATION = DUR;
  if (!location.search.includes('render')) {
    const t0 = performance.now();
    (function loop() { renderFrame(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop); })();
  }
})();
