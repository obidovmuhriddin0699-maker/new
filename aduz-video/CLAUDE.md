# ADUZ promo roliklar — loyiha xotirasi

Bu fayl keyingi ishlar uchun "xotira": foydalanuvchi tasdiqlagan uslub, ovoz va dizayn qoidalari. Javoblar — o'zbekcha.

## Holat
- 28 qismning hammasi tayyor (1–28). 27–28 — Instagram Reels formatida.
- 1–26 ning Instagram versiyalari (`episodeN_ig.html` = asl qism + `reel.js` + `ig_config.js` + `igwrap.js`,
  `make_ig.py`, `ig_audio.py`, `build_ig.sh N`) → `instagram/`. Matnlar `ig_config.js`, post matnlari `instagram/captions.json`.
- Joylash: Windsor.ai Instagram ulanishi (akkaunt 17841419124058324 = telegram_reklama777, `create_video_post`),
  video/muqova — GitHub raw havolalari (repo ochiq). Reja `instagram/README.md`: har kuni 18:53 (Toshkent) 1 ta,
  2026-10-16 dan kuniga 3 ta (09:53, 13:53, 18:53); vazifa trig_01Bp5FitH93XqTyCeTKFUhAs (shu sessiyaga bog'langan).
- Haqiqiy bot ("Target reklama bot", foydalanuvchi skrinshotlari): rollar Mijoz / Kanal egasi; reklama yaratish →
  WebApp 3 qadam (hudud → kategoriya → kanal: narx, obunachi, ko'rish, ER, bo'sh navbat) → sana/vaqt/interval →
  hisob-kitob → to'lov (hamyon, Click, Payme, demo) → moderatsiya → rejalashtirish. Statistika: kampaniyalar,
  yuborilgan xabarlar, muvaffaqiyat darajasi, sarflangan. Botda ko'rinmagan: escrow, matching %, A/B, retargeting,
  referal, reyting, yuridik hujjatlar, konstruktor, optimizatsiya.
- **Botga mos IG versiyalar** (2, 3, 10, 11, 15, 18–23, 26, 27; foydalanuvchi: "Qolganlarni botga moslab joyla"):
  `ig_config.js` oxiridagi `BOT` bloki matnlarni almashtiradi va `bot` qo'shadi (`seq` ekranlar [nom, boshi, oxiri, opts],
  `focus` izohlar, `caps` 11–27 s subtitrlar, `title`/`cmp`/`badges` natija). `igwrap.js` 10.95–23.1 s da
  `IGBOT.scene`, 23.1–27 s da `IGBOT.result` (`igbot.js`, telefon ichida botning haqiqiy ekranlari) chizadi.
  Ovoz `bot_audio.py` (muammo cue'lari < 10.9 s + bot cue'lari + IG qatlami; 2–3 uchun asl wav + score_7 fon).
  Faqat botda bor funksiyalarni ko'rsatish; namunaviy raqamlarni "namuna" deb belgilash. Joylash 2026-10-30 dan.

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

## Dizayn (23-qismdan): NEON mavzu — foydalanuvchi tanlovi "ADUZ qismlariga qo'llash"
- Manba: foydalanuvchining "telegram_reklama777" dizayn tizimi (artifact VaMAiJqBED4BgPhffYNP8A). Qism sahifasida
  `<script src="lib.js"></script><script src="neon.js"></script>` — `neon.js` fonlar, subtitr, logotip, hisoblagich,
  natija foni, yakuniy kadrni almashtiradi; `C` ranglarini neon palitraga o'tkazadi; `F`=Archivo, `FD`=Russo One
  (`fnt()`: og'irlik ≥ 900 → Russo One). Eski qismlar (`neon.js` siz) o'zgarmaydi — tekshirilgan.
- Ranglar `N.*`: ground #110e18, burg/burgHi, glowRed #c82224 (chap-past nur), ink #fcfcfc, muted #a0959f,
  pink #f84058 (qahramon so'z, muammo slablari), pinkSoft, yellow #f8e800 (bitta taklif so'zi / oltin slam),
  cyan #08c0c8 (ijobiy, yechim, CTA kalit so'zi; sariq bilan bir blokda emas), chip #401820 + chipEdge #5c2729.
- Shrift: Russo One — faqat KATTA HARF (slam, sarlavha, CTA); Archivo 800 — sarlavha qatori; Archivo italik
  (`it(500)`) — izoh/subtitr. Matnda emoji va heshteg yo'q, "Siz" murojaati, o'zbek lotin ʻ bilan.
- Yordamchilar: `glowText`, `neonGround`, `chipCard`, `neonBadge`, `commentCTA`, `postTimeline`, `HANDLE`.
  Pastki ~420 px — subtitrdan boshqa matnsiz (subtitr y≈1588).

## Dizayn (24-qismdan): "MOTION REEL" mavzu — foydalanuvchi referens videosi (showreel, 15 s)
- Foydalanuvchi: "keyingi qism grafik dizaynini shu video dizaynidan tayyorla va bu uslubni saqlab qo'y".
  Sahifada `<script src="lib.js"></script><script src="reel.js"></script>` (neon.js o'rniga). Ikkala mavzu saqlanadi;
  keyingi qismlar uchun foydalanuvchi boshqasini aytmaguncha — oxirgi so'ralgan uslub (reel). 26-qism: foydalanuvchi
  "24-qism dizaynida" deb so'radi — reel uslubi tasdiqlangan asosiy uslub.
- Ranglar `R.*`: ink #0e0d0f, warm #1c1311 (identity foni), paper #e9e7e2 (yechim/UI foni), card #f7f6f3,
  off #efece4, orange #f04a1e (asosiy aksent, muammo kesimi, tagchiziq), lime #d6f03a (ijobiy, "javob bor"),
  violet #6a5cf2 (ikkinchi aksent, keyframe kartasi, halftone). Ko'p rang — faqat panjara/konfetti/nishonlarda.
- Shrift: Archivo 900 — KATTA HARF kinetik so'zlar (`heavy()`, manfiy tracking); Instrument Serif italik — urg'u
  iboralar (`serif()`); JetBrains Mono — kengaytirilgan mayda yozuvlar, HUD, raqamlar (`mono()`, `scramble()`).
- Qurilmalar: `hud(t, SECTIONS, light, '24-QISM')` (har kadrda, overlay'da; qog'oz fonda light=true), `tickLine`,
  `dotGrid`, `stripes`, `halftone`, `card`/`toggle`/`donut`, `particleSphere`, `reelBadge`, identity `endCard`,
  o'tish `gridWave(t,a,b,A,B,'So'z.')`. Muammo slamlari — qiyshiq rangli slab-kartalar; 8.5 va 18.5 da
  butun kadrni egallovchi rangli kesim (to'q sariq / laym) + og'ir so'z + serif izoh.
- Subtitr: siyoh plashka, chapda to'q sariq chiziq, y≈1700 (HUD shkalasidan yuqorida).

## Aralash rejim (25-qismdan): uchala dizayn bitta qismda
- Sahifa: `lib.js` → `const TH_CLASSIC = snapTheme()` → `neon.js` → `TH_NEON` → `reel.js` → `FD = null; TH_REEL`.
  `useTheme(TH_*)` — lib yordamchilari, `C`, `F`/`FD`, konfetti ranglarini almashtiradi; har sahna/qism chizishdan
  oldin chaqiriladi, overlay oxirida subtitr uchun `useTheme(capTheme(t))`. Namuna: `episode25.html`.
- Foydalanuvchi "barcha dizayn va ovozlar" so'rasa — shu rejim + butun ovoz kutubxonasi (sfx/ + oldingi qismlarning
  fx./tr./imp. sintez ovozlari + xor + pizzicato).

## Instagram Reels rejimi (27-qismdan) — foydalanuvchi "Instagram uchun, rekka chiqish uchun" so'rasa
- Hook kadr 0 da: `boot({ fadeIn: 0, fadeOut: 0 })`, birinchi kadrda katta raqam/savol + zarba ovozi.
- Xavfsiz zona (`reel.js`: `IG`, `igSafe()`, `render.mjs --safe`): matn y 250…1460; y > 1060 da x ≤ 900.
  Subtitr — `window.captions = igCaptions` (markaz x 480, pastki cheti y 1410). Pastdagi elementlar markazi `IGX = 480`.
- Loop: oxirgi ~0.6 s da hook kadrini qayta qurish (`hookFrame(t - 32, t)`), audio — riser kadr 0 zarbasiga, render'da
  so'nish o'rniga 20 ms anti-klik. Yakunda izoh-kalit so'z CTA (`endCard(t, t0, ctaFn)`) + "saqlab qo'ying".
- Eksport: `-c:v libx264 -profile:v high -level 4.1 -pix_fmt yuv420p -crf 17 -r 30 -g 30 … -ar 48000 -c:a aac -b:a 256k`;
  muqova `ADUZ_N-qism_cover.jpg` (hook kadri, subtitrsiz), `INSTAGRAM_N.md` (post matni, 3–5 heshteg, alt matn, joylash).

## Vizual effektlar (foydalanuvchi: "juda yoqdi, yanada efekt qil")
- **FX v2** (`lib.js`, 20-qismdan): `rgbGlitch`, `punch`, `shine`, `inkSplat`, `flare`, `trail`, `pulseVignette`,
  `godRays`, `disintegrate`. Har qismda ko'p ishlatiladi: slamlarda glitch, voqealarda punch, tayyor kartalarda shine,
  zarbalarda flare, oltin slam ortida godRays, vakuumda pulseVignette.
- **Kinetik matn presetlari** (`kText`, 22-qismdan; foydalanuvchi referenslari — "Text Animation Presets" videolari):
  `bounce`, `charsDown`, `letterUp`, `colorBounce`, `flicker`, `typewriter`, `blurUp`, `scale`, `wordRight`.
  Sarlavhalar, oltin slam, natija sarlavhasi va reklama kartalari shu presetlar bilan jonlantiriladi.
- Ishlatilgan o'tishlar (takrorlamaslik uchun): circleWipe, clockWipe, zoomThrough, pixelDissolve, splitDoors, squeegee,
  implode, cardFlip, crtOff, sliceGlitch, lightsOn, tileFlip, eyelidOpen, shatter, slitOpen, splitOpen, sudya bolg'asi, radarSweep (23), gridWave (24), pocketZoom (25), stripeWipe (26, reel.js), barsWipe (27, reel.js), snapInto (28, episode28.html).

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
- FRONT to'plamiga mavjud ovozni qo'shmang (eski qismlar ovozi o'zgaradi) — vakuumda kerak bo'lsa alohida nom bilan
  nusxa qiling (masalan `fx.chain_snap_v`).
- Litsenziya eslatmasi: sfx/ namunalari boshqa muallifning SFX to'plami reklamasidan — e'lon qilishdan oldin ruxsat olish.
