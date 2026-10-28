# Instagram Reels — telegram_reklama777

28 qismning Reels versiyasi (28-qism dizayni: hook kadr 0 da, xavfsiz zona, HUD, kesimlar, identity yakun + izoh-CTA, loop).
- `ADUZ_N-qism_reels.mp4` — 1080×1920, 30 fps, H.264 High, AAC 48 kHz, −14 LUFS. 28 — asl Reels qism; 27 — botga mos versiya.
- `ADUZ_N-qism_cover.jpg` — muqova (hook kadri). `captions.json` — post matnlari.
- Qayta yig'ish: `python3 make_ig.py N` → `./build_ig.sh N` (1–27; botga mos qismlar avtomatik `bot_audio.py` bilan).

## Joylash rejasi (foydalanuvchi tanlovi 2026-10-24: 2026-10-25 dan kuniga 3 ta, 19:00 / 20:00 / 21:00, Gemini diktor ovozi bilan)
Windsor.ai Instagram ulanishi (`create_video_post`, akkaunt 17841419124058324 = telegram_reklama777) orqali,
video va muqova — GitHub raw havolalari (repo ochiq). Ovozli video: `instagram/ovozli/ADUZ_N-qism_reels.mp4` (`GEMINI_API_KEY=... python3 -I voice_gemini.py all`, matn — `instagram/diktor.json`). 10-20 dagi 5- va 6-qism joylangan edi: Windsor 60 s ichida javob bermagan (timeout), lekin post chiqqan — timeout bo'lsa qayta joylanmaydi, "joylandi (timeout)" deb belgilanadi.

| Sana | Vaqt | Qism | Holat |
|---|---|---|---|
| 2026-10-15 | 18:53 | 1 | joylandi (media 17968006389192775) |
| 2026-10-16 | 12:17 | 4 | joylandi (media 18113383217168204) |
| 2026-10-20 | 12:55 | 5 | joylandi (media 17908650408563692) |
| 2026-10-20 | 18:57 | 6 | joylandi (media 17894864835615315) |
| 2026-10-25 | 19:00 | 7 | joylandi (timeout, 2026-10-25 14:03Z) |
| 2026-10-25 | 20:00 | 8 | joylandi (media 18629717860017695) |
| 2026-10-25 | 21:00 | 9 | joylandi (media 18120581044950476) |
| 2026-10-26 | 19:00 | 12 | joylandi (media 17920937433455799) |
| 2026-10-26 | 20:00 | 13 | joylandi (media 18094316087263382) |
| 2026-10-26 | 21:00 | 14 | joylandi (timeout, 2026-10-26 16:07Z) |
| 2026-10-27 | 19:00 | 16 | joylandi (media 18107874907973328) |
| 2026-10-27 | 20:00 | 17 | joylandi (media 18135385249791484) |
| 2026-10-27 | 21:00 | 24 | joylandi (media 18100153193548717) |
| 2026-10-28 | 19:00 | 15 (botga mos) | joylandi (media 18091565528702743) |
| 2026-10-28 | 20:00 | 25 | rejada (ovozli) |
| 2026-10-28 | 21:00 | 28 | rejada (ovozli) |
| 2026-10-29 | 19:00 | 20 (botga mos) | rejada (ovozli) |
| 2026-10-29 | 20:00 | 2 (botga mos) | rejada (ovozli) |
| 2026-10-29 | 21:00 | 3 (botga mos) | rejada (ovozli) |
| 2026-10-30 | 19:00 | 23 (botga mos) | rejada (ovozli) |
| 2026-10-30 | 20:00 | 10 (botga mos) | rejada (ovozli) |
| 2026-10-30 | 21:00 | 11 (botga mos) | rejada (ovozli) |
| 2026-10-31 | 19:00 | S1 (qisqa) | foydalanuvchi ovozi kutilmoqda |
| 2026-10-31 | 20:00 | 18 (botga mos) | rejada (ovozli) |
| 2026-10-31 | 21:00 | 19 (botga mos) | rejada (ovozli) |
| 2026-11-01 | 19:00 | S2 (qisqa) | foydalanuvchi ovozi kutilmoqda |
| 2026-11-01 | 20:00 | 21 (botga mos) | rejada (ovozli) |
| 2026-11-01 | 21:00 | 22 (botga mos) | rejada (ovozli) |
| 2026-11-02 | 19:00 | S3 (qisqa) | foydalanuvchi ovozi kutilmoqda |
| 2026-11-02 | 20:00 | 26 (botga mos) | rejada (ovozli) |
| 2026-11-02 | 21:00 | 27 (botga mos) | rejada (ovozli) |

**Botga mos versiyalar** (2, 3, 10, 11, 15, 18, 19, 20, 21, 22, 23, 26, 27): muammo qismi (0–10.9 s) asl qism bilan bir xil,
yechim va natija esa Target reklama botining haqiqiy oqimini ko'rsatadi (`igbot.js`): asosiy menyu → reklama yaratish
(nom, matn, media) → WebApp 3 qadam (hudud → kategoriya → kanal kartochkasi: post narxi, obunachilar, ko'rishlar, ER,
bo'sh navbat) → preview va hisob-kitob → to'lov (hamyon / Click / Payme) → moderatsiya → rejalashtirildi; Kampaniyalar
va Kanal egasi (kanal biriktirish, daromadlar, pul yechish) ekranlari. Ovoz — `bot_audio.py`. Raqamlar (20 000 so'm,
2 400 obunachi, 20 post = 400 000 so'm) — namuna.
