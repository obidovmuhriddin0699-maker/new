# ADUZ — 1-qism: "Reklama bozoridagi xaos"

`ADUZ_1-qism.mp4` — 32 soniyalik vertikal (9:16, 1080×1920, 30 fps) motion-grafika rolik,
musiqa va SFX bilan. Telegram, Instagram Reels va YouTube Shorts uchun.

> Diktor ovozi hali yozilmagan: matn ekranda subtitr sifatida turibdi.
> Diktor yozib berilsa, quyidagi taymkodlar bo'yicha qo'yiladi.

## Fayllar

| Fayl | Nima |
|---|---|
| `ADUZ_1-qism.mp4` | Tayyor rolik |
| `episode1.html` | Animatsiya manbasi. Brauzerda ochsangiz takrorlanib o'ynaydi |
| `render.mjs` | HTML → MP4 render (Playwright + ffmpeg) |
| `audio.py` | Musiqa va SFX sintezi (numpy) |

Qayta yig'ish:

```bash
python3 audio.py build/audio.wav
node render.mjs build/video_silent.mp4
ffmpeg -y -i build/video_silent.mp4 -i build/audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ADUZ_1-qism.mp4
```

## Ssenariy (taymkodlar bilan)

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | Qorong'u fon. "1-QISM · Reklama bozoridagi xaos". Telegram chat: tadbirkor kanal adminiga yozadi ("Narxi qancha?", "Obunachilar haqiqiymi?", "Kafolat bormi?"). Hisoblagich: kun / xabar / **0 natija** | Past tarang dron, yurak urishi, xabar "pop"lari | Reklama uchun ishonchli kanal topish — haqiqiy bosh og'rig'i. |
| 0:05–0:11 | 1. Muammo | "Admin javob bermayapti...". Qizil belgilar: *Soxta obunachilar? · Narx noaniq · Kafolat yo'q · Javob yo'q*. Chigal qizil chiziqlar, telefon titraydi, fon qizarib boradi | Xatolik buzzerlari, kuchayib boruvchi riser | Narx noaniq, obunachilar shubhali, kafolat yo'q. |
| 0:11 | O'tish | Yashil doira ekranni "tozalaydi" | Whoosh | — |
| 0:11–0:16 | 2. Yechim | ADUZ logotipi. Ilova: qidiruvga "Farg'ona · Kiyim-kechak" yoziladi, filtrlar (Haqiqiy auditoriya / Ochiq narx / Kafolat), tasdiqlangan kanal kartalari: obunachi, ERR, moslik %, narx | Zamonaviy pad + arpedjio, klaviatura, swoosh | ADUZ — Farg'ona vodiysidagi Telegram kanallari bitta platformada. |
| 0:16–0:22 | 2. Yechim | Barmoq 1-kanalni tanlaydi → "Buyurtma berish" → "Buyurtma qabul qilindi!": to'lov ADUZ kafolatida, avtomatik hisob-kitob, real vaqt statistikasi | Click, tasdiq chime | Tekshirilgan auditoriya, ochiq narx va kafolatlangan to'lov. |
| 0:22–0:27 | 3. Natija | "Reklama ishladi": buyurtmalar grafigi o'sadi, **×3.0**, oltin nishonlar, konfetti | G'alaba musiqasi, kassa "cha-ching" | Natija: aniq auditoriya, o'sayotgan savdo va xotirjamlik. |
| 0:27–0:32 | Yakun | ADUZ logotipi + yaltirash. "Biznesingiz himoyachisi!", "Farg'ona vodiysi uchun Telegram reklama ekotizimi", CTA: **Hoziroq sinab ko'ring** | "Ting" | ADUZ — biznesingiz himoyachisi! |

Rolikdagi kanal nomlari, narxlar va "×3" ko'rsatkichi namuna uchun qo'yilgan.
Efirga chiqarishdan oldin ularni haqiqiy ma'lumotlar bilan almashtiring.

## Manba ssenariylar tahlili (PDF + XLSX, 28 qism)

**Kuchli tomonlari**
- Har qism bitta aniq og'riqqa bag'ishlangan (Muammo → Yechim → Natija): qisqa rolik uchun to'g'ri tuzilma.
- 28 ta mavzu mantiqiy yoy hosil qiladi: bozor muammolari (1–5) → ADUZ bilan tanishuv (6–9) →
  xususiyatlar (10–27) → yakun va CTA (28).
- XLSX'da kamera rejasi (o'rta/yaqin → keng) va SFX aniq ko'rsatilgan.

**Tuzatish kerak bo'lgan joylar**
1. **Shablon takrori.** Vizual, motion va audio ustunlari 28 qismda so'zma-so'z bir xil. 3-kadr
   (Natija) hamma qismda aynan bir xil. Har qism uchun o'ziga xos sahna kerak: 1-qismda chat xaosi
   va "0 natija", 11-qismda muzlatilgan to'lov, 14-qismda tungi soat va hokazo.
2. **Diktor matni yo'q, faqat sarlavha bor.** Masalan: "(Asabiylashgan ohangda) Kanal qidirishdagi
   tartibsizlik" — bu o'qiladigan gap emas, mavzu nomi. Shu rolik uchun to'liq jumlalar yozildi (yuqoridagi jadval).
3. **Matn xatolari.** PDF 1-qism, 2-kadr: "ADUZ orqali ADUZ orqali tizimlashtirish" (takror).
   XLSX'da "ADUZ ning Reklama bozoridagi xaos xususiyati bilan tanishing": muammo nomi
   xususiyat deb atalgan (3–5-qismlarda ham shunday).
4. **Shior bir xil emas.** PDF'da "ADUZ — biznesingiz himoyachisi!", XLSX'da "ADUZ — ishonchli va
   barqaror reklama ekotizimi!". Bittasini tanlash kerak. Bu rolikda birinchisi shior,
   ikkinchisi taglavha qilib olindi.
5. **Texnik parametrlar yo'q.** Davomiylik, format (9:16 / 16:9), kadr vaqtlari, CTA va
   qahramon (kim u, qanday biznes) ko'rsatilmagan. "Obyektlar diqqat markazida" kabi
   iboralar rejissyorga hech narsa bermaydi.
6. **Qahramon ko'rsatilmagan.** "Qahramon muammodan nolimoqda" deyilgan, lekin qahramon
   tavsiflanmagan. Tavsiya: bitta doimiy qahramon (masalan, Farg'onalik kiyim do'koni egasi)
   barcha qismlardan o'tsa, serial yaxlit bo'ladi.
