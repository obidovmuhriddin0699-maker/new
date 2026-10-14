# ADUZ promo roliklar — loyiha xotirasi

Bu fayl keyingi ishlar uchun "xotira": foydalanuvchi tasdiqlagan uslub, ovoz va dizayn qoidalari. Javoblar — o'zbekcha.

## Format va tuzilma
- Har qism: `episodeN.html` (canvas 1080×1920, 30 fps, 32 s) + `audio.py` dagi `render_N` / `CUES_N` / `SCORE_N`.
- Yig'ish: `python3 -I audio.py N build/episodeN.wav` → `node render.mjs episodeN.html` → ffmpeg mux
  (`loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false`, AAC 192k). Cho'qqi ≤ −1.0 dBFS bo'lishi shart.
- Cue-sheet: `python3 -I audio.py N --cuesheet SOUND_ARCHITECTURE_N.md`. README'ga jadval qatori va qism bo'limi.
- Tuzilma (7-qism uslubi): Muammo 0–9.5 s (slamlar 5.6/6.6/7.6, asosiy zarba 8.5) → **ovoz vakuumi** 9.5–10.15
  (gate; faqat FRONT tovushlar) → o'tish ~10.3–11.0 (har qismda yangi) → Yechim 11–21.75 (telefon UI, kursor bosishlari,
  18.5 oltin slam, 19.7 "muvaffaqiyat" oynasi) → whip-pan → Natija 22–27 ("Oldin ↔ ADUZ" kartasi + 3 oltin nishon,
  23.2 da kassa) → endCard 27 s.
- Har qismda: aniq namuna raqamlar va funksiya da'volarini README'da "namuna — tekshiring" deb belgilash.

## Vizual effektlar (foydalanuvchi: "juda yoqdi, yanada efekt qil")
- **FX v2** (`lib.js`, 20-qismdan): `rgbGlitch`, `punch`, `shine`, `inkSplat`, `flare`, `trail`, `pulseVignette`,
  `godRays`, `disintegrate`. Har qismda ko'p ishlatiladi: slamlarda glitch, voqealarda punch, tayyor kartalarda shine,
  zarbalarda flare, oltin slam ortida godRays, vakuumda pulseVignette.
- **Kinetik matn presetlari** (`kText`, 22-qismdan; foydalanuvchi referenslari — "Text Animation Presets" videolari):
  `bounce`, `charsDown`, `letterUp`, `colorBounce`, `flicker`, `typewriter`, `blurUp`, `scale`, `wordRight`.
  Sarlavhalar, oltin slam, natija sarlavhasi va reklama kartalari shu presetlar bilan jonlantiriladi.
- Ishlatilgan o'tishlar (takrorlamaslik uchun): circleWipe, clockWipe, zoomThrough, pixelDissolve, splitDoors, squeegee,
  implode, cardFlip, crtOff, sliceGlitch, lightsOn, tileFlip, eyelidOpen, shatter, slitOpen, splitOpen, sudya bolg'asi.

## Ovoz
- **SFX kutubxonasi** `sfx/` (39 ta, foydalanuvchi yuborgan SFX-to'plam videolaridan kesilgan): UI/o'tish/zarba
  ovozlarining hammasi shulardan (`sfx.<nom>`, `smp(name, semis)` bilan balandligini o'zgartirish mumkin).
  Matn animatsiyalari uchun: tick_hi, swoosh_text, type_burst, blip_up, bass_drop + sparkle_hit, shimmer, pop_short.
  Ko'rish: `sfx/PREVIEW.mp4` (dastlabki 26 ta).
- Sintez faqat musiqiy qismlarda: partitura (`score_7` + `KEY_SHIFT`), swell, ui.select qo'ng'iroqchalari, success,
  uchqunlar, kassa, sonic logo.
- **Musiqa uslubi** (foydalanuvchi referenslari: "Heavenly-meme", "Dexter-meme", "Romance-meme"):
  meme treklarining o'zi **ishlatilmaydi** (mualliflik huquqi, platformalar ovozni o'chiradi). Ularning kayfiyati
  original sintezda: `choir()` — "heavenly" xor "aaah" (vahiy/yechim ochilishi, oltin slam, logotip ostida),
  `quirky_pizz()` — Dexter kayfiyatidagi o'ynoqi-sirli pizzicato (muammo sahnasi). Referens tahlili: Dexter ≈108 BPM
  E-major, Romance ≈161 BPM D-minor (vokal), Heavenly — D-minor atrofida xor.
- Litsenziya eslatmasi: sfx/ namunalari boshqa muallifning SFX to'plami reklamasidan — e'lon qilishdan oldin ruxsat olish.
