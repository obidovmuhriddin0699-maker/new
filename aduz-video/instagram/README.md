# Instagram Reels — telegram_reklama777

28 qismning Reels versiyasi (28-qism dizayni: hook kadr 0 da, xavfsiz zona, HUD, kesimlar, identity yakun + izoh-CTA, loop).
- `ADUZ_N-qism_reels.mp4` — 1080×1920, 30 fps, H.264 High, AAC 48 kHz, −14 LUFS. 28 — asl Reels qism; 27 — botga mos versiya.
- `ADUZ_N-qism_cover.jpg` — muqova (hook kadri). `captions.json` — post matnlari.
- Qayta yig'ish: `python3 make_ig.py N` → `./build_ig.sh N` (1–27; botga mos qismlar avtomatik `bot_audio.py` bilan).

## Joylash rejasi (foydalanuvchi tanlovi: 2026-10-16 dan kuniga 3 ta)
Windsor.ai Instagram ulanishi (`create_video_post`, akkaunt 17841419124058324 = telegram_reklama777) orqali,
video va muqova — GitHub raw havolalari (repo ochiq). 2026-10-16 dan kuniga 3 ta: 09:53, 13:53, 18:53 (Toshkent).

| Sana | Vaqt | Qism | Holat |
|---|---|---|---|
| 2026-10-15 | 18:53 | 1 | joylandi (media 17968006389192775) |
| 2026-10-16 | 12:17 | 4 | joylandi (media 18113383217168204) |
| 2026-10-16 | 13:53 | 5 | rejada |
| 2026-10-16 | 18:53 | 6 | rejada |
| 2026-10-17 | 09:53 | 7 | rejada |
| 2026-10-17 | 13:53 | 8 | rejada |
| 2026-10-17 | 18:53 | 9 | rejada |
| 2026-10-18 | 09:53 | 12 | rejada |
| 2026-10-18 | 13:53 | 13 | rejada |
| 2026-10-18 | 18:53 | 14 | rejada |
| 2026-10-19 | 09:53 | 16 | rejada |
| 2026-10-19 | 13:53 | 17 | rejada |
| 2026-10-19 | 18:53 | 24 | rejada |
| 2026-10-20 | 09:53 | 25 | rejada |
| 2026-10-20 | 13:53 | 28 | rejada |
| 2026-10-20 | 18:53 | 2 (botga mos) | rejada |
| 2026-10-21 | 09:53 | 3 (botga mos) | rejada |
| 2026-10-21 | 13:53 | 10 (botga mos) | rejada |
| 2026-10-21 | 18:53 | 11 (botga mos) | rejada |
| 2026-10-22 | 09:53 | 15 (botga mos) | rejada |
| 2026-10-22 | 13:53 | 18 (botga mos) | rejada |
| 2026-10-22 | 18:53 | 19 (botga mos) | rejada |
| 2026-10-23 | 09:53 | 20 (botga mos) | rejada |
| 2026-10-23 | 13:53 | 21 (botga mos) | rejada |
| 2026-10-23 | 18:53 | 22 (botga mos) | rejada |
| 2026-10-24 | 09:53 | 23 (botga mos) | rejada |
| 2026-10-24 | 13:53 | 26 (botga mos) | rejada |
| 2026-10-24 | 18:53 | 27 (botga mos) | rejada |

**Botga mos versiyalar** (2, 3, 10, 11, 15, 18, 19, 20, 21, 22, 23, 26, 27): muammo qismi (0–10.9 s) asl qism bilan bir xil,
yechim va natija esa Target reklama botining haqiqiy oqimini ko'rsatadi (`igbot.js`): asosiy menyu → reklama yaratish
(nom, matn, media) → WebApp 3 qadam (hudud → kategoriya → kanal kartochkasi: post narxi, obunachilar, ko'rishlar, ER,
bo'sh navbat) → preview va hisob-kitob → to'lov (hamyon / Click / Payme) → moderatsiya → rejalashtirildi; Kampaniyalar
va Kanal egasi (kanal biriktirish, daromadlar, pul yechish) ekranlari. Ovoz — `bot_audio.py`. Raqamlar (20 000 so'm,
2 400 obunachi, 20 post = 400 000 so'm) — namuna.
