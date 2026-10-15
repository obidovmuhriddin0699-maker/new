// "Botga mos" solution + result scenes for the Instagram versions (igwrap.js calls IGBOT when cfg.bot is set).
// The solution (10.95–18.45 s) shows the REAL Target reklama bot flow from the user's screenshots: main menu →
// create ad (chat steps) → WebApp 3 steps (hudud → kategoriya → kanal card: narx, obunachi, ko'rish, ER, bo'sh navbat)
// → preview & hisob-kitob → to'lov (hamyon / Click / Payme) → moderatsiya → rejalashtirildi; plus Kampaniyalar and
// Kanal egasi screens. The result (23.1–27 s) is a before/after card with only bot-backed claims.
window.IGBOT = (function () {
  const PXg = 150, PYg = 262, PWg = 660, PHg = 990, BZ = 18;
  const sx = PXg + BZ, sy = PYg + BZ, sw = PWg - 2 * BZ, sh = PHg - 2 * BZ;
  const TG = { bg: '#c9dbb0', out: '#e1f7cb', inBtn: 'rgba(62,92,52,.62)', key: '#ffffff', head: '#ffffff', blue: '#3a9ad9', grey: '#7d8b8f' };
  const WA = { bg: '#0b0b10', card: '#15151b', edge: '#26262e', chip: '#1e1838', chipEdge: '#3b2f6e', violet: '#a78bfa', cyan: '#22d3ee', pink: '#e879f9', gold: '#f5c451', green: '#34d399', grey: '#9ca3af' };
  let taps = [];

  function T(s, x, y, size, col, w = 600, align = 'left', base = 'alphabetic') { text(s, x, y, size, col, w, align, base); }
  function wrapW(s, maxW, size, w) { return wrap(s, maxW, size, w); }
  // ---------- Telegram chat chrome ----------
  function chatBg() {
    ctx.fillStyle = TG.bg; ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = 'rgba(255,255,255,.18)'; for (let i = 0; i < 40; i++) { ctx.beginPath(); ctx.arc(sx + (i * 97) % sw, sy + 120 + (i * 151) % (sh - 120), 6 + (i % 3) * 3, 0, 7); ctx.fill(); }
    ctx.fillStyle = TG.head; ctx.fillRect(sx, sy, sw, 104);
    T('‹', sx + 26, sy + 66, 46, '#333', 400);
    ctx.beginPath(); ctx.arc(sx + 100, sy + 52, 30, 0, 7); ctx.fillStyle = TG.blue; ctx.fill(); T('TA', sx + 100, sy + 53, 24, '#fff', 800, 'center', 'middle');
    T('Target reklama bot', sx + 146, sy + 48, 27, '#111', 800); T('bot', sx + 146, sy + 80, 20, TG.grey, 500);
  }
  function bubble(y, s, side = 'l', size = 23, w = 0) {
    size = Math.round(size * 1.24);
    const maxW = sw - 140, lines = s.split('\n').flatMap(l => l ? wrapW(l, maxW - 36, size, 500) : ['']), lh = size * 1.32;
    ctx.font = fnt(500, size); const bw = w || Math.min(maxW, Math.max(...lines.map(l => ctx.measureText(l).width)) + 36), bh = lines.length * lh + 26;
    const bx = side === 'l' ? sx + 18 : sx + sw - 18 - bw;
    rr(bx, y, bw, bh, 18); ctx.fillStyle = side === 'l' ? '#ffffff' : TG.out; ctx.fill();
    lines.forEach((l, i) => T(l, bx + 18, y + 13 + lh * (i + .78), size, '#111', /^[✅❗📌📍📁🗓⏰🔁💳📢]/.test(l) ? 600 : 500));
    return bh;
  }
  function inlineBtn(x, y, w, h, s, hi = 0) { rr(x, y, w, h, 14); ctx.fillStyle = hi ? 'rgba(52,140,72,.9)' : TG.inBtn; ctx.fill(); T(s, x + w / 2, y + h / 2 + 1, 22, '#fff', 700, 'center', 'middle'); }
  function keyboard(labels, hiIdx, hiK) {
    const kh = 300, ky = sy + sh - kh; ctx.fillStyle = '#eef0f2'; ctx.fillRect(sx, ky, sw, kh);
    labels.forEach((l, i) => { const c = i % 2, r = Math.floor(i / 2), w = (sw - 42) / 2, x = sx + 14 + c * (w + 14), y = ky + 16 + r * 92;
      scaled(x + w / 2, y + 40, 1 - .05 * (i === hiIdx ? hiK : 0), () => { rr(x, y, w, 80, 18); ctx.fillStyle = i === hiIdx && hiK > 0 ? '#dfe8d6' : TG.key; ctx.fill(); T(l, x + w / 2, y + 41, 21, '#222', 700, 'center', 'middle'); }); });
    return ky;
  }
  const MENU = ['Reklama yaratish', 'Mening reklamalarim', 'Kampaniyalar', 'Statistika', 'Profil', 'Yordam'];
  function scrMenu(t, a, b, o) {
    chatBg(); const hit = MENU.indexOf(o.tap || 'Reklama yaratish'), at = a + (b - a) * .55;
    bubble(sy + 130, 'Asosiy menyu:', 'l');
    const ky = keyboard(MENU, hit, bump(t, at, .25) * 4);
    const c = hit % 2, r = Math.floor(hit / 2), w = (sw - 42) / 2; taps.push([at, sx + 14 + c * (w + 14) + w / 2, ky + 16 + r * 92 + 40]);
    if (t > at) { const k = eOut(prog(t, at, at + .25)); withAlpha(k, () => bubble(sy + 210, MENU[hit], 'r')); }
  }
  function scrCreate(t, a, b, o) {
    chatBg(); const steps = o.steps || [['1️⃣ Reklama nomini kiriting (faqat siz uchun):', o.name || 'Yozgi aksiya'], ['2️⃣ Reklama matnini kiriting (foydalanuvchilar koʻradigan matn):', o.text || 'Yangi kolleksiya — 30% chegirma! Manzil: Fargʻona sh.'], ['3️⃣ Rasm, video yoki hujjat yuboring (ixtiyoriy).', o.media ? '[media]' : null]];
    let y = sy + 124; const n = steps.length, dt = (b - a) / (n + .3);
    steps.forEach(([q, ans], i) => { const qa = a + i * dt, aa = qa + dt * .5; if (t < qa) return;
      withAlpha(eOut(prog(t, qa, qa + .2)), () => { y += bubble(y, q, 'l', 21) + 10; });
      if (ans && t > aa) withAlpha(eOut(prog(t, aa, aa + .2)), () => {
        if (ans === '[media]') { const bx = sx + sw - 18 - 300; rr(bx, y, 300, 190, 18); const g = ctx.createLinearGradient(bx, y, bx + 300, y + 190); g.addColorStop(0, '#f472b6'); g.addColorStop(1, '#f59e0b'); ctx.fillStyle = g; ctx.fill(); T('−30%', bx + 150, y + 100, 64, '#fff', 900, 'center', 'middle'); y += 200; }
        else { const typed = ans.slice(0, Math.floor(ans.length * clamp((t - aa) / .45))); y += bubble(y, typed || ' ', 'r', 21) + 10; }
      });
    });
    if (y > sy + sh - 20) { /* overflow guard */ }
  }
  const REGIONS = ['Fargʻona', 'Andijon', 'Namangan', 'Toshkent shahri', 'Toshkent viloyati', 'Samarqand'];
  const CATS = ['Yangiliklar va OAV', 'IT va Texnologiyalar', 'Biznes va Moliya', 'Taʼlim va Fan', 'Sport', 'Avto va Transport'];
  function waTop(step, title, sub, chips = []) {
    ctx.fillStyle = WA.bg; ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = '#f4f4f5'; ctx.fillRect(sx, sy, sw, 84); T('←', sx + 26, sy + 54, 30, '#222', 700); T('Target reklama…', sx + 80, sy + 54, 26, '#222', 700);
    const cy = sy + 112; ctx.font = fnt(800, 18); const cw = ctx.measureText(step).width + 40;
    rr(sx + 24, cy, cw, 40, 20); ctx.fillStyle = WA.chip; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = WA.chipEdge; ctx.stroke(); T(step, sx + 24 + cw / 2, cy + 21, 18, step.startsWith('3') ? WA.green : step.startsWith('2') ? WA.cyan : WA.violet, 800, 'center', 'middle');
    let x = sx + 24; chips.forEach(([s, col]) => { ctx.font = fnt(700, 18); const w = ctx.measureText(s).width + 36; rr(x, cy + 52, w, 38, 19); ctx.fillStyle = '#16142a'; ctx.fill(); ctx.strokeStyle = col; ctx.stroke(); T(s, x + w / 2, cy + 72, 18, col, 700, 'center', 'middle'); x += w + 10; });
    const ty = cy + (chips.length ? 140 : 90); T(title, sx + 24, ty, 36, '#fff', 800); T(sub, sx + 24, ty + 38, 18, WA.grey, 500);
    return ty + 66;
  }
  function scrRegion(t, a, b, o) {
    const y0 = waTop('1-QADAM / 3', 'Hududni tanlang', 'Reklama uchun viloyat yoki shaharni tanlang'), hit = o.region || 0, at = a + (b - a) * .6;
    REGIONS.forEach((r, i) => { const y = y0 + i * 96, p = eOut(prog(t, a + i * .05, a + .25 + i * .05)); if (p <= 0) return;
      withAlpha(p, () => scaled(sx + sw / 2, y + 40, 1 - .03 * bump(t, at, .25) * (i === hit), () => {
        rr(sx + 24, y, sw - 48, 82, 22); ctx.fillStyle = i === hit && t > at ? '#1c1730' : WA.card; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = i === hit && t > at ? WA.violet : WA.edge; ctx.stroke();
        rr(sx + 40, y + 14, 54, 54, 14); ctx.fillStyle = '#221b3a'; ctx.fill(); glyphPin(sx + 67, y + 41);
        T(r, sx + 112, y + 50, 26, '#fff', 700); T('›', sx + sw - 60, y + 52, 30, WA.grey, 400); })); });
    taps.push([at, sx + sw / 2, y0 + hit * 96 + 41]);
  }
  function glyphPin(x, y) { ctx.save(); ctx.translate(x, y); ctx.strokeStyle = WA.violet; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(0, -5, 10, Math.PI * .85, Math.PI * 2.15); ctx.lineTo(0, 14); ctx.closePath(); ctx.stroke(); ctx.beginPath(); ctx.arc(0, -5, 3.5, 0, 7); ctx.stroke(); ctx.restore(); }
  function scrCategory(t, a, b, o) {
    const y0 = waTop('2-QADAM / 3', 'Kategoriyani tanlang', 'Kanallar mavzusi va yoʻnalishi', [[REGIONS[o.region || 0], WA.violet]]), hit = o.cat ?? 2, at = a + (b - a) * .6;
    CATS.forEach((c, i) => { const col = i % 2, row = Math.floor(i / 2), w = (sw - 64) / 2, x = sx + 24 + col * (w + 16), y = y0 + row * 190, p = eBack(prog(t, a + i * .05, a + .3 + i * .05)); if (p <= 0) return;
      scaled(x + w / 2, y + 85, p * (1 - .04 * bump(t, at, .25) * (i === hit)), () => {
        rr(x, y, w, 170, 24); ctx.fillStyle = i === hit && t > at ? '#18172a' : WA.card; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = i === hit && t > at ? WA.cyan : WA.edge; ctx.stroke();
        rr(x + 18, y + 18, 60, 60, 16); ctx.fillStyle = '#23232b'; ctx.fill(); ctx.fillStyle = [WA.grey, WA.cyan, WA.gold, WA.violet, WA.green, WA.pink][i]; ctx.fillRect(x + 36, y + 36, 24, 24);
        const ls = wrapW(c, w - 36, 22, 800); ls.forEach((l, k) => T(l, x + 18, y + 108 + k * 26, 22, '#fff', 800)); T('Tanlash ›', x + 18, y + 156, 17, WA.grey, 500); }); });
    taps.push([at, sx + 24 + (hit % 2) * ((sw - 64) / 2 + 16) + (sw - 64) / 4, y0 + Math.floor(hit / 2) * 190 + 85]);
  }
  function spark(x, y, w, col, ph) { ctx.beginPath(); for (let i = 0; i <= 20; i++) { const xx = x + w * i / 20, yy = y - 14 - 10 * Math.sin(i / 3 + ph); i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.lineWidth = 3; ctx.strokeStyle = col; ctx.stroke(); }
  function scrChannel(t, a, b, o) {
    const ch = o.ch || {}, cats = [[REGIONS[o.region || 0], WA.violet], [CATS[o.cat ?? 2], WA.cyan]];
    const y0 = waTop('3-QADAM / 3', 'Mos kanallarni tanlang', 'Faqat tanlangan hudud va kategoriyadagi faol kanallar', cats);
    const chk = o.check ?? a + (b - a) * .45, ok = o.confirm ?? a + (b - a) * .8, x = sx + 24, y = y0 - 10, w = sw - 48, on = t > chk;
    const p = eOut(prog(t, a, a + .3)); if (p <= 0) return;
    withAlpha(p, () => {
      rr(x, y, w, 520, 30); ctx.fillStyle = WA.card; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = on ? WA.violet : WA.edge; ctx.stroke();
      rr(x + 22, y + 24, 92, 92, 22); ctx.fillStyle = '#f3efe9'; ctx.fill(); T((ch.name || 'Kanal')[0], x + 68, y + 72, 44, '#333', 900, 'center', 'middle');
      T(ch.name || 'Vodiy Bozor', x + 134, y + 62, 28, '#fff', 800); T(ch.user || '@vodiy_bozor', x + 134, y + 100, 19, WA.pink, 600);
      ctx.beginPath(); ctx.arc(x + w - 46, y + 52, 22, 0, 7); if (on) { ctx.fillStyle = WA.violet; ctx.fill(); check(x + w - 46, y + 53, 20, '#fff', 4); } else { ctx.lineWidth = 3; ctx.strokeStyle = '#555'; ctx.stroke(); }
      rr(x + 22, y + 136, w - 44, 104, 18); ctx.fillStyle = 'rgba(245,196,81,.07)'; ctx.fill(); ctx.strokeStyle = 'rgba(245,196,81,.55)'; ctx.stroke();
      T('POST NARXI:', x + 44, y + 170, 17, '#d4a43a', 800); T(ch.price || '20 000 soʻm', x + 44, y + 218, 38, WA.gold, 900);
      [['OBUNACHILAR', ch.subs || '2 400', '#60a5fa'], ['KOʻRISHLAR', ch.views || '1 818', WA.pink], ['FAOLLIK (ER)', ch.er || '24.0%', '#fb923c'], ['BOʻSH NAVBAT', 'Hozir boʻsh', WA.green]].forEach(([l, v, c], i) => {
        const cx = x + 24 + (i % 2) * (w / 2 - 10), cy = y + 270 + Math.floor(i / 2) * 125, hi = (o.focusStat || []).includes(i) && t > a + (b - a) * .25;
        if (hi) { rr(cx - 10, cy - 14, w / 2 - 24, 128, 16); ctx.fillStyle = 'rgba(167,139,250,.14)'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = WA.violet; ctx.stroke(); }
        T(l, cx + 4, cy + 14, 16, WA.grey, 800); T(v, cx + 4, cy + 56, 30, i === 3 ? WA.green : '#fff', 800); if (i < 3) spark(cx + 4, cy + 104, w / 2 - 60, c, i + t);
      });
    });
    taps.push([chk, x + w - 46, y + 52]);
    if (t > chk) { const q = eBack(prog(t, chk + .1, chk + .4)); if (q > 0) scaled(sx + sw / 2, sy + sh - 70, q * (1 - .04 * bump(t, ok, .25)), () => {
      const g = ctx.createLinearGradient(sx + 24, 0, sx + sw - 24, 0); g.addColorStop(0, '#7c3aed'); g.addColorStop(1, '#c026d3'); rr(sx + 24, sy + sh - 110, sw - 48, 80, 24); ctx.fillStyle = g; ctx.fill();
      T(`Tasdiqlash (${o.nch || 1} ta kanal)`, sx + sw / 2, sy + sh - 68, 26, '#fff', 800, 'center', 'middle'); }); taps.push([ok, sx + sw / 2, sy + sh - 70]); }
  }
  function scrPreview(t, a, b, o) {
    chatBg(); const p = eOut(prog(t, a, a + .3)), d = o.prev || {};
    const lines = ['👀 Preview va hisob-kitob', '', `📌 Nomi: ${o.name || 'Yozgi aksiya'}`, `📍 Hudud: ${REGIONS[o.region || 0]}`, `📁 Kategoriya: ${CATS[o.cat ?? 2]}`, `🗓 Muddat: ${d.days || '4 kun (17.10 – 20.10)'}`, `⏰ Vaqt: ${d.hours || '09:00 – 21:00'}`, `🔁 Interval: ${d.every || 'har 3 soatda'}`, '', `📢 ${(o.ch || {}).name || 'Vodiy Bozor'}: ${(o.ch || {}).price || '20 000 soʻm'}/post`, `   ${d.posts || 20} post × ${(o.ch || {}).price || '20 000 soʻm'}`, `💳 Jami: ${d.total || '400 000 soʻm'}`, '', 'Tasdiqlaysizmi?'];
    withAlpha(p, () => { const h = bubble(sy + 124, lines.join('\n'), 'l', 21, sw - 60);
      inlineBtn(sx + 18, sy + 134 + h, (sw - 46) / 2, 62, '✅ Tasdiqlash', t > (o.ok ?? b - .3)); inlineBtn(sx + 28 + (sw - 46) / 2, sy + 134 + h, (sw - 46) / 2, 62, '❌ Bekor qilish');
      taps.push([o.ok ?? b - .3, sx + 18 + (sw - 46) / 4, sy + 165 + h]);
      (o.focusLines || []).forEach(k => { if (t < a + (b - a) * .3) return; const ly = sy + 124 + 13 + 26 * 1.32 * (k + .78); rr(sx + 22, ly - 31, sw - 70, 42, 8); ctx.lineWidth = 3; ctx.strokeStyle = '#7c3aed'; ctx.stroke(); });
    });
  }
  function scrPay(t, a, b, o) {
    chatBg(); const tot = (o.prev || {}).total || '400 000 soʻm', click = o.click ?? a + (b - a) * .3, s1 = click + .25, s2 = o.sched ?? click + (b - click) * .6;
    let y = sy + 124; y += bubble(y, `💳 Toʻlov summasi: ${tot}\n\nQaysi usulda toʻlaysiz?`, 'l', 22) + 12;
    if (t < s1) { ['💰 Hamyondan', '💳 Click orqali toʻlash', '💳 Payme orqali toʻlash'].forEach((s, i) => inlineBtn(sx + 18, y + i * 74, sw - 120, 62, s, i === 1 && t > click)); taps.push([click, sx + 18 + (sw - 120) / 2, y + 74 + 31]); }
    else { withAlpha(eOut(prog(t, s1, s1 + .2)), () => { y += bubble(y, '✅ Toʻlov muvaffaqiyatli amalga oshirildi!\n\n📨 Reklamangiz moderatsiyaga yuborildi. Administrator koʻrib chiqqandan soʻng avtomatik rejalashtiriladi.', 'l', 21) + 12; });
      if (t > s2) withAlpha(eOut(prog(t, s2, s2 + .2)), () => { bubble(y, `✅ "${o.name || 'Yozgi aksiya'}" reklamangiz tasdiqlandi va rejalashtirildi.`, 'l', 21); }); }
  }
  function scrCampaigns(t, a, b, o) {
    chatBg(); const at = a + .2; withAlpha(eOut(prog(t, a, a + .3)), () => bubble(sy + 124, 'Kampaniyalar', 'r'));
    if (t > at + .2) withAlpha(eOut(prog(t, at + .2, at + .45)), () => bubble(sy + 210, '🗓 Kampaniyalaringiz:\n\n' + (o.camps || ['Yozgi aksiya — SCHEDULED']).map(s => '• ' + s).join('\n'), 'l', 23));
  }
  function scrOwner(t, a, b, o) {
    chatBg(); const t1 = a + (b - a) * .3, t2 = a + (b - a) * .72; let y = sy + 124;
    y += bubble(y, '👤 Profilingiz\n\nMijoz — reklama joylash uchun hamyon\nKanal egasi — kanal daromadlari va pul yechish', 'l', 21) + 12;
    if (t < t1 + .3) { inlineBtn(sx + 18, y, sw - 120, 62, '📢 Mijoz profili'); inlineBtn(sx + 18, y + 74, sw - 120, 62, '📡 Kanal egasi profili', t > t1); taps.push([t1, sx + 18 + (sw - 120) / 2, y + 74 + 31]); }
    else { withAlpha(eOut(prog(t, t1 + .3, t1 + .5)), () => { y += bubble(y, '📡 Kanal egasi: daromadlar, kanal biriktirish va pul yechish', 'l', 21) + 12;
      ['➕ Kanal biriktirish', '💰 Daromadlar', '💳 Pul yechish'].forEach((s, i) => inlineBtn(sx + 18, y + i * 74, sw - 120, 62, s, i === 0 && t > t2)); taps.push([t2, sx + 18 + (sw - 120) / 2, y + 31]); }); }
  }
  const SCR = { menu: scrMenu, create: scrCreate, region: scrRegion, category: scrCategory, channel: scrChannel, preview: scrPreview, pay: scrPay, campaigns: scrCampaigns, owner: scrOwner };

  function phoneFrame(draw) {
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 24; rr(PXg, PYg, PWg, PHg, 64); ctx.fillStyle = '#101114'; ctx.fill(); ctx.restore();
    ctx.save(); rr(sx, sy, sw, sh, 48); ctx.clip(); draw(); ctx.restore();
  }
  function scene(t, cfg) {
    const B = cfg.bot; taps = [];
    ctx.fillStyle = R.paper; ctx.fillRect(0, 0, W, H); dotGrid(t, .06, .4, 1, 480, 800);
    const ent = eBack(prog(t, 10.95, 11.4));
    scaled(480, 757, lerp(.85, 1, ent), () => withAlpha(prog(t, 10.95, 11.15), () => phoneFrame(() => {
      const sq = B.seq; let cur = sq[0];
      for (const s of sq) if (t >= s[1]) cur = s;
      const [name, a, b, o] = cur, k = eInOut(prog(t, a, a + .25)), prev = sq[sq.indexOf(cur) - 1];
      if (prev && k < 1) { ctx.save(); ctx.translate(-sw * k, 0); SCR[prev[0]](t, prev[1], prev[2], { ...B, ...(prev[3] || {}) }); ctx.restore(); ctx.save(); ctx.translate(sw * (1 - k), 0); }
      else ctx.save();
      SCR[name](t, a, b, { ...B, ...(o || {}) }); ctx.restore();
    })));
    // cursor through this frame's taps
    const tp = taps.filter(([at]) => Math.abs(t - at) < .6).sort((x, y) => x[0] - y[0]);
    if (tp.length) { const [at, x, y] = tp[0], k = clamp(1 - Math.abs(t - at) / .6); withAlpha(Math.min(1, k * 3), () => cursor(x + (1 - eOut(clamp((t - at + .6) / .6))) * 120 * (t < at), y + (1 - eOut(clamp((t - at + .6) / .6))) * 160 * (t < at), bump(t, at, .22))); ripple(x, y, prog(t, at, at + .6), '#7c3aed'); }
    // focus callouts
    (B.focus || []).forEach(([a, b, l1, l2]) => { const p = eBack(prog(t, a, a + .3)), q = prog(t, b - .2, b); if (p <= 0 || q >= 1) return;
      withAlpha(1 - q, () => scaled(480, 346, p, () => { ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 24; rr(110, 290, 740, 112, 22); ctx.fillStyle = R.ink; ctx.fill(); ctx.restore();
        ctx.fillStyle = R.lime; ctx.fillRect(110, 310, 8, 72); mono(l1, 140, 327, 18, R.lime, 'left', .25, 800); serif(l2, 140, 373, 40, R.off, 'left'); })); });
  }
  function result(t, cfg) {
    const B = cfg.bot; ctx.fillStyle = R.ink; ctx.fillRect(0, 0, W, H);
    const g = ctx.createRadialGradient(480, 800, 50, 480, 800, 1300); g.addColorStop(0, 'rgba(106,92,242,.32)'); g.addColorStop(1, 'rgba(106,92,242,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    scramble(t, 23.0, 'NATIJA', 480, 300, 26, R.lime, { dur: .4 });
    ctx.save(); ctx.font = `900 66px Archivo, Inter, sans-serif`; ctx.letterSpacing = '-2px'; const tw = ctx.measureText(B.title).width; ctx.restore();
    heavy(t, 23.05, B.title, 480, 375, Math.min(66, 66 * 800 / Math.max(1, tw)), R.off, { rot: .06 });
    const cp = eOut(prog(t, 23.1, 23.6)), x = 70, y = lerp(560, 520, cp), w = 840, h = 430;
    withAlpha(cp, () => {
      card(x, y, w, h, R.card, 30);
      mono('OLDIN', x + 50, y + 62, 20, R.grey, 'left', .3, 800);
      rr(x + 430, y + 34, 220, 54, 27); ctx.fillStyle = R.orange; ctx.fill(); mono('BOT BILAN', x + 540, y + 62, 18, R.ink, 'center', .25, 800);
      ctx.fillStyle = '#e4e1da'; ctx.fillRect(x + 400, y + 105, 2, h - 130);
      B.cmp.forEach(([a, b], i) => {
        const ry = y + 165 + i * 100, st = eInOut(prog(t, 23.6 + i * .35, 23.9 + i * .35)), ok = eBack(prog(t, 23.8 + i * .35, 24.1 + i * .35));
        const la = wrap(a, 330, 25, 600); la.forEach((l, k) => text(l, x + 45, ry - (la.length - 1) * 15 + k * 30, 25, st > 0 ? '#a8a4ac' : R.ink, 600));
        if (st > 0) { ctx.fillStyle = R.orange; ctx.fillRect(x + 40, ry - 11, 340 * st, 4); }
        if (ok > 0) scaled(x + 445, ry - 10, ok, () => { ctx.beginPath(); ctx.arc(x + 445, ry - 10, 20, 0, 7); ctx.fillStyle = R.ink; ctx.fill(); check(x + 445, ry - 9, 18, R.lime, 5);
          const lb = wrap(b, 330, 25, 800); lb.forEach((l, k) => text(l, x + 478, ry - (lb.length - 1) * 15 + k * 30, 25, R.ink, 800)); });
      });
    });
    B.badges.forEach((l, i) => { const p = eBack(prog(t, 25.2 + i * .25, 25.65 + i * .25)); if (p > 0) reelBadge(200 + i * 280, 1100, l, [R.orange, R.lime, R.violet][i], (bx, by) => { ctx.fillStyle = i === 2 ? R.off : R.ink; ctx.beginPath(); ctx.arc(bx, by, 26, 0, 7); ctx.fill(); check(bx, by + 1, 26, i === 2 ? R.violet : [R.orange, R.lime][i], 6); }, p); });
    confetti(t, 25.0);
  }
  return { scene, result };
})();
