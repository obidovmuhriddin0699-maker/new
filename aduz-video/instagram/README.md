# Instagram Reels — telegram_reklama777

28 qismning Reels versiyasi (28-qism dizayni: hook kadr 0 da, xavfsiz zona, HUD, kesimlar, identity yakun + izoh-CTA, loop).
- `ADUZ_N-qism_reels.mp4` — 1080×1920, 30 fps, H.264 High, AAC 48 kHz, −14 LUFS. 28 — asl Reels qism; 27 — botga mos versiya.
- `ADUZ_N-qism_cover.jpg` — muqova (hook kadri). `captions.json` — post matnlari.
- Qayta yig'ish: `python3 make_ig.py N` → `./build_ig.sh N` (1–27; botga mos qismlar avtomatik `bot_audio.py` bilan).

## Joylash rejasi (foydalanuvchi tanlovi: har kuni 1 ta, avval bot bilan mos qismlar)
Windsor.ai Instagram ulanishi (`create_video_post`, akkaunt 17841419124058324 = telegram_reklama777) orqali,
video va muqova — GitHub raw havolalari (repo ochiq). Har kuni 18:53 (Toshkent).

| Sana | Qism | Holat |
|---|---|---|
| 2026-10-15 | 1 | joylandi (media 17968006389192775) |
| 2026-10-16 | 4 | rejada |
| 2026-10-17 | 5 | rejada |
| 2026-10-18 | 6 | rejada |
| 2026-10-19 | 7 | rejada |
| 2026-10-20 | 8 | rejada |
| 2026-10-21 | 9 | rejada |
| 2026-10-22 | 12 | rejada |
| 2026-10-23 | 13 | rejada |
| 2026-10-24 | 14 | rejada |
| 2026-10-25 | 16 | rejada |
| 2026-10-26 | 17 | rejada |
| 2026-10-27 | 24 | rejada |
| 2026-10-28 | 25 | rejada |
| 2026-10-29 | 28 | rejada |
| 2026-10-30 | 2 (botga mos) | rejada |
| 2026-10-31 | 3 (botga mos) | rejada |
| 2026-11-01 | 10 (botga mos) | rejada |
| 2026-11-02 | 11 (botga mos) | rejada |
| 2026-11-03 | 15 (botga mos) | rejada |
| 2026-11-04 | 18 (botga mos) | rejada |
| 2026-11-05 | 19 (botga mos) | rejada |
| 2026-11-06 | 20 (botga mos) | rejada |
| 2026-11-07 | 21 (botga mos) | rejada |
| 2026-11-08 | 22 (botga mos) | rejada |
| 2026-11-09 | 23 (botga mos) | rejada |
| 2026-11-10 | 26 (botga mos) | rejada |
| 2026-11-11 | 27 (botga mos) | rejada |

**Botga mos versiyalar** (2, 3, 10, 11, 15, 18, 19, 20, 21, 22, 23, 26, 27): muammo qismi (0–10.9 s) asl qism bilan bir xil,
yechim va natija esa Target reklama botining haqiqiy oqimini ko'rsatadi (`igbot.js`): asosiy menyu → reklama yaratish
(nom, matn, media) → WebApp 3 qadam (hudud → kategoriya → kanal kartochkasi: post narxi, obunachilar, ko'rishlar, ER,
bo'sh navbat) → preview va hisob-kitob → to'lov (hamyon / Click / Payme) → moderatsiya → rejalashtirildi; Kampaniyalar
va Kanal egasi (kanal biriktirish, daromadlar, pul yechish) ekranlari. Ovoz — `bot_audio.py`. Raqamlar (20 000 so'm,
2 400 obunachi, 20 post = 400 000 so'm) — namuna.
