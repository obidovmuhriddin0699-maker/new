// Instagram Reels packaging layer for episodes 1–26 ("28-qism kabi"): loaded AFTER an episode's own script (and
// reel.js), by the generated episodeN_ig.html pages (make_ig.py). It wraps the episode's renderFrame:
//   0–1.6 s   hook card on frame 0 (loop target) — no fade-in
//   1.6–27 s  the original episode, scaled into the Reels safe area (×0.72, centre x 480) over a blurred backdrop
//   overlays  orange cut 8.45–9.45, lime cut 18.45–19.65, violet card 19.7–21.75, result card 22–23.1
//             (each switchable per episode in ig_config.js), HUD frame, IG captions
//   27–31.4 s reel identity end card + comment CTA; 31.4–32 s loop bridge back to the hook frame
(function () {
  const ep = window.IG_EP, cfg = window.IGCFG[ep], base = window.renderFrame;
  const ARCH = 'Archivo, Inter, "DejaVu Sans", sans-serif';
  const SC = .72, FX = 480, FY = 200, FW = W * SC, FH = H * SC;
  const caps = (window.IG_CAPTIONS || []).filter(c => c[0] < 27);
  const sm = document.createElement('canvas'); sm.width = 54; sm.height = 96;
  const noop = () => {};
  window.captions = igCaptions;
  FD = null;

  // heavy word auto-fitted to a max width
  function fitHeavy(t, at, s, x, y, size, maxW, color, o = {}) {
    ctx.save(); ctx.font = `900 ${size}px ${ARCH}`; ctx.letterSpacing = `${(-size * .03).toFixed(1)}px`; const w = ctx.measureText(s).width; ctx.restore();
    heavy(t, at, s, x, y, Math.min(size, size * maxW / Math.max(1, w)), color, o);
  }
  function fitSerif(s, x, y, size, maxW, color) {
    ctx.font = `italic 400 ${size}px ${SERIF}`; const w = ctx.measureText(s).width;
    serif(s, x, y, Math.min(size, size * maxW / Math.max(1, w)), color);
  }
  const bg = ep % 2 ? R.orange : R.violet, fg = ep % 2 ? R.ink : R.off, accent = ep % 2 ? R.ink : R.lime;
  function hookFrame(u, t) {
    const [label, b1, b2, sub] = cfg.hook;
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    dotGrid(u + 40, .1, .42, 1, FX, 820);
    mono(label, FX, 470, 26, fg, 'center', .4, 800);
    if (b2) { fitHeavy(u, -.3, b1, FX, 690, 240, 820, fg, { rot: -.15, endRot: -.03 }); fitHeavy(u, -.2, b2, FX, 900, 240, 820, fg, { rot: .12, endRot: .02 }); }
    else fitHeavy(u, -.3, b1, FX, 790, 320, 820, fg, { rot: -.15, endRot: -.03 });
    fitSerif(sub, FX, 1090, 70, 800, accent);
    mono(`${ep}-QISM  /  ADUZ`, FX, 1250, 20, fg, 'center', .35, 800);
  }
  function orangeCut(t) {
    if (!cfg.cut1 || t < 8.45 || t > 9.45) return;
    const k = eOut(prog(t, 8.45, 8.62)), a = 1 - prog(t, 9.3, 9.45), rw = lerp(500, W + 40, k), rh = lerp(260, H + 40, k);
    withAlpha(a, () => {
      rr(W / 2 - rw / 2, H / 2 - rh / 2, rw, rh, lerp(130, 0, k)); ctx.fillStyle = R.orange; ctx.fill();
      fitHeavy(t, 8.5, cfg.cut1[0], FX, 820, 230, 840, R.ink, { rot: -.12, endRot: -.04 });
      withAlpha(prog(t, 8.7, 8.9), () => fitSerif(cfg.cut1[1], FX, 1020, 66, 800, R.ink));
    });
  }
  function limeCut(t) {
    if (!cfg.cut2 || t < 18.45 || t > 19.65) return;
    const k = eOut(prog(t, 18.45, 18.62)), a = 1 - prog(t, 19.45, 19.65), rw = lerp(420, W + 40, k), rh = lerp(240, H + 40, k);
    withAlpha(a, () => {
      rr(W / 2 - rw / 2, H / 2 - rh / 2, rw, rh, lerp(120, 0, k)); ctx.fillStyle = R.lime; ctx.fill();
      dotGrid(t, .12, .5, 1, FX, 820);
      fitHeavy(t, 18.5, cfg.cut2[0], FX, 700, 230, 840, R.ink, { rot: .14, endRot: -.03 });
      fitHeavy(t, 18.6, cfg.cut2[1], FX, 910, 230, 840, R.ink, { rot: -.14, endRot: .02 });
      withAlpha(prog(t, 18.8, 19.05), () => fitSerif(cfg.cut2[2], FX, 1070, 62, 800, R.ink));
    });
  }
  function violetCard(t) {
    if (!cfg.card || t < 19.7 || t > 21.9) return;
    const [l1, l2, rows, pill] = cfg.card, mp = eOut(prog(t, 19.7, 20.15)), out = prog(t, 21.6, 21.9);
    withAlpha(1 - out, () => {
      withAlpha(.45 * mp, () => { ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H); });
      const y0 = lerp(H, 380, mp);
      card(70, y0, 840, 700, R.violet, 34);
      withAlpha(prog(t, 20.0, 20.3), () => { fitSerif(l1, 490, y0 + 110, 92, 760, R.off); fitSerif(l2, 490, y0 + 210, 92, 760, R.off); });
      rows.forEach((l, i) => {
        const at = 20.4 + i * .3, k = eBack(prog(t, at, at + .3)), ry = y0 + 330 + i * 72;
        mono(l, 120, ry, 20, R.off, 'left', .25, 800); ctx.fillStyle = 'rgba(239,236,228,.2)'; ctx.fillRect(120, ry + 28, 700, 2);
        if (k > 0) scaled(800, ry, k, () => { ctx.beginPath(); ctx.arc(800, ry, 24, 0, 7); ctx.fillStyle = R.lime; ctx.fill(); check(800, ry + 1, 22, R.ink, 5); });
      });
      const dn = eBack(prog(t, 21.3, 21.55)); if (dn > 0) scaled(490, y0 + 640, dn, () => {
        ctx.font = `800 15px ${MONO}`; const w = Math.max(300, ctx.measureText(pill).width * 1.35 + 60);
        rr(490 - w / 2, y0 + 612, w, 56, 28); ctx.fillStyle = R.lime; ctx.fill(); mono(pill, 490, y0 + 641, 15, R.ink, 'center', .15, 800); });
    });
  }
  function resultCard(t) {
    if (!cfg.res || t < 22.0 || t > 23.15) return;
    const a = 1 - prog(t, 22.85, 23.15), st = ep % 3;
    withAlpha(a, () => {
      if (st === 0) stripes(t);
      else if (st === 1) halftone(t, FX, 900);
      else { ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H); dotGrid(t, 1, .55, 1.4, FX, 800); withAlpha(.55, () => { ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H); }); }
      fitHeavy(t, 22.1, cfg.res[0], FX, 790, 380, 820, R.off, { rot: -.25, endRot: -.05 });
      ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 20; mono(cfg.res[1], FX, 1060, 32, R.off, 'center', .35, 800); ctx.restore();
    });
  }
  function cta(tt, t0) {
    const p = eBack(prog(tt, t0 + 1.5, t0 + 1.9)); if (p <= 0) return;
    scaled(W / 2, 1250, p, () => {
      mono('IZOHGA YOZING', W / 2, 1195, 22, R.off, 'center', .4, 800);
      rr(W / 2 - 170, 1225, 340, 100, 50); ctx.fillStyle = R.lime; ctx.fill();
      ctx.save(); ctx.font = `900 64px ${ARCH}`; ctx.letterSpacing = '-2px'; ctx.fillStyle = R.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('ADUZ', W / 2, 1278); ctx.restore();
    });
    withAlpha(prog(tt, t0 + 1.9, t0 + 2.2), () => serif('ulanish havolasini yuboramiz · saqlab qoʻying', W / 2, 1385, 40, R.off));
  }
  const SECTIONS = [[0, '00', 'HOOK'], [1.6, '01', 'MUAMMO'], [9.5, '02', 'VAKUUM'], [10.4, '03', 'OTISH'], [11, '04', 'YECHIM'], [22, '05', 'NATIJA'], [27, '06', 'ADUZ']];

  window.renderFrame = function (t) {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
    const F0 = F, FD0 = FD, hud0 = window.hud;
    if (t < 1.6) {
      F = ARCH; FD = null; ctx.clearRect(0, 0, W, H); hookFrame(t, t);
      const cut = prog(t, 1.45, 1.6); if (cut > 0) withAlpha(cut, () => { ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H); });
    } else {
      window.hud = noop;
      base(t);
      window.hud = hud0;
      F = ARCH; FD = null;
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
      const buf = fxSnapshot();
      const g = sm.getContext('2d'); g.drawImage(buf, 0, 0, sm.width, sm.height);
      ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H);
      ctx.imageSmoothingEnabled = true; withAlpha(.55, () => ctx.drawImage(sm, -60, -60, W + 120, H + 120));
      ctx.fillStyle = 'rgba(14,13,15,.45)'; ctx.fillRect(0, 0, W, H);
      const fx = FX - FW / 2;
      ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.6)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 20; rr(fx, FY, FW, FH, 30); ctx.fillStyle = R.ink; ctx.fill(); ctx.restore();
      ctx.save(); rr(fx, FY, FW, FH, 30); ctx.clip(); ctx.drawImage(buf, fx, FY, FW, FH); ctx.restore();
      ctx.save(); rr(fx, FY, FW, FH, 30); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(239,236,228,.22)'; ctx.stroke(); ctx.restore();
      orangeCut(t); limeCut(t); violetCard(t); resultCard(t);
      if (t >= 27) endCard(t, 27.0, cta);
      if (t > 31.4) {
        const k = eOut(prog(t, 31.4, 31.62)), rw = lerp(300, W + 40, k), rh = lerp(180, H + 40, k);
        ctx.save(); rr(W / 2 - rw / 2, H / 2 - rh / 2, rw, rh, lerp(100, 0, k)); ctx.clip(); hookFrame(t - 32, t); ctx.restore();
      }
    }
    rgbGlitch(t, 1.55, .2, .8, 2); rgbGlitch(t, 8.5, .3, .9, 9); rgbGlitch(t, 18.5, .3, .6, 13); rgbGlitch(t, 31.4, .2, .6, 30);
    if (cfg.cut1) flare(t, 8.5, FX, 820, '#ffd0c0');
    if (cfg.cut2) flare(t, 18.5, FX, 800, '#fbffd8');
    const light = cfg.cut2 && t > 18.5 && t < 19.5;
    hud(t, SECTIONS, light, `${ep}-QISM`);
    if (t >= 1.6 && t < 27) igCaptions(t, caps.map(([a, b, x]) => [Math.max(a, 1.6), b, x]).filter(c => c[0] < c[1]));
    filmLook(t, .04, .25);
    igSafe();
    F = F0; FD = FD0;
  };
})();
