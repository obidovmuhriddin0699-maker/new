# ADUZ — promo roliklar seriyasi

Har bir qism — 32 soniyalik vertikal (9:16, 1080×1920, 30 fps) motion-grafika rolik,
musiqa va SFX bilan. Telegram, Instagram Reels va YouTube Shorts uchun.

| Qism | Rolik | Mavzu |
|---|---|---|
| 1 | `ADUZ_1-qism.mp4` | Reklama bozoridagi xaos |
| 2 | `ADUZ_2-qism.mp4` | Auditoriyani topish muammosi |
| 3 | `ADUZ_3-qism.mp4` | Soxta obunachilar va ishonchsizlik |

> Diktor ovozi hali yozilmagan: matn ekranda subtitr sifatida turibdi.
> Diktor yozib berilsa, quyidagi taymkodlar bo'yicha qo'yiladi.
>
> Roliklardagi kanal nomlari, narxlar va natija ko'rsatkichlari (×3, ×32 va h.k.)
> namuna uchun qo'yilgan. Efirga chiqarishdan oldin ularni haqiqiy ma'lumotlar bilan almashtiring.

## Fayllar

| Fayl | Nima |
|---|---|
| `episodeN.html` | Qism sahnalari. Brauzerda ochsangiz takrorlanib o'ynaydi |
| `lib.js` | Umumiy qismlar: telefon, logotip, subtitr, kursor, sarlavha va hisoblagichlar, xatolik belgilari, muammo/yechim/natija fonlari, yakuniy kadr, sahnalar tartibi |
| `render.mjs` | HTML → MP4 render (Playwright + ffmpeg) |
| `audio.py` | Musiqa va SFX sintezi (numpy). Musiqa foni umumiy, effektlar har qismga alohida |

Har bir qism bir xil tuzilmada: Muammo 0–11 s, Yechim 11–22 s, Natija 22–32 s.
Yangi qism qo'shish uchun `episodeN.html` faylida uchta sahna va subtitrlarni yozib,
`audio.py` ga `cues_N()` qo'shish kifoya.

Qayta yig'ish (masalan, 2-qism):

```bash
python3 audio.py 2 build/episode2.wav
node render.mjs episode2.html            # → build/episode2_silent.mp4
ffmpeg -y -i build/episode2_silent.mp4 -i build/episode2.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ADUZ_2-qism.mp4
```

Tekshirish uchun alohida kadrlar: `node render.mjs episode2.html --stills=3,8.5,15` → `build/episode2/`.

## 1-qism: "Reklama bozoridagi xaos"

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | Qorong'u fon. "1-QISM · Reklama bozoridagi xaos". Telegram chat: tadbirkor kanal adminiga yozadi ("Narxi qancha?", "Obunachilar haqiqiymi?", "Kafolat bormi?"). Hisoblagich: kun / xabar / **0 natija** | Past tarang dron, yurak urishi, xabar "pop"lari | Reklama uchun ishonchli kanal topish — haqiqiy bosh og'rig'i. |
| 0:05–0:11 | 1. Muammo | "Admin javob bermayapti...". Qizil belgilar: *Soxta obunachilar? · Narx noaniq · Kafolat yo'q · Javob yo'q*. Chigal qizil chiziqlar, telefon titraydi, fon qizarib boradi | Xatolik buzzerlari, kuchayib boruvchi riser | Narx noaniq, obunachilar shubhali, kafolat yo'q. |
| 0:11 | O'tish | Yashil doira ekranni "tozalaydi" | Whoosh | — |
| 0:11–0:16 | 2. Yechim | ADUZ logotipi. Ilova: qidiruvga "Farg'ona · Kiyim-kechak" yoziladi, filtrlar (Haqiqiy auditoriya / Ochiq narx / Kafolat), tasdiqlangan kanal kartalari: obunachi, ERR, moslik %, narx | Zamonaviy pad + arpedjio, klaviatura, swoosh | ADUZ — Farg'ona vodiysidagi Telegram kanallari bitta platformada. |
| 0:16–0:22 | 2. Yechim | Barmoq 1-kanalni tanlaydi → "Buyurtma berish" → "Buyurtma qabul qilindi!": to'lov ADUZ kafolatida, avtomatik hisob-kitob, real vaqt statistikasi | Click, tasdiq chime | Tekshirilgan auditoriya, ochiq narx va kafolatlangan to'lov. |
| 0:22–0:27 | 3. Natija | "Reklama ishladi": buyurtmalar grafigi o'sadi, **×3.0**, oltin nishonlar, konfetti | G'alaba musiqasi, kassa "cha-ching" | Natija: aniq auditoriya, o'sayotgan savdo va xotirjamlik. |
| 0:27–0:32 | Yakun | ADUZ logotipi + yaltirash. "Biznesingiz himoyachisi!", "Farg'ona vodiysi uchun Telegram reklama ekotizimi", CTA: **Hoziroq sinab ko'ring** | "Ting" | ADUZ — biznesingiz himoyachisi! |


## 2-qism: "Auditoriyani topish muammosi"

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "2-QISM · Auditoriyani topish muammosi". Tadbirkor katta kanalda ("Toshkent Memlar", 128 ming) Farg'onadagi ayollar ko'ylaklari reklamasini berdi. Ko'rishlar o'sadi, izohlar esa boshqa auditoriyadan: "Toshkentga yetkazib berasizmi?", "Erkaklar uchun yo'qmi?". Fonda nishon: tomoshabinlar (qizil nuqtalar) nishonga tegmaydi | Tarang dron, yurak urishi, nuqtalar "pop"lari | Katta kanalga reklama berdingiz: ko'rishlar ko'p, mijoz yo'q. |
| 0:05–0:11 | 1. Muammo | Post statistikasi: Toshkent 64%, erkaklar 81%, 14–18 yosh 58%; Farg'ona vodiysi atigi **7%**. Hisoblagich: 38 000 ko'rish → **2 mijoz**, 1,2 mln so'm sarflangan. Qizil belgilar: *Boshqa shahar · Boshqa yosh · Boshqa qiziqish · Pul havoga* | Buzzerlar, riser | Chunki o'quvchilar boshqa shahar, boshqa yosh, boshqa qiziqishda. |
| 0:11 | O'tish | Yashil doira | Whoosh | — |
| 0:11–0:16 | 2. Yechim | ADUZ "Kimga reklama beramiz?" ekrani. Barmoq tanlaydi: hudud (Farg'ona, Marg'ilon, Qo'qon), jins (Ayollar), yoshni 20–40 ga suradi, qiziqish (Moda, Kiyim-kechak). "Mos kanallar" soni 214 → **12** ga tushadi | Kliklar, slider, pad + arpedjio | ADUZ'da auditoriyani oldindan tanlaysiz: hudud, jins, yosh, qiziqish. |
| 0:16–0:22 | 2. Yechim | "Eng mos kanallar": Ayollar Klubi · Farg'ona — moslik **94%** (Farg'ona vodiysi 88%, ayollar 91%, 20–40 yosh 76%), 290 000 so'm. "Buyurtma berish" → "Reklama aniq manzilga yetadi!" | Gauge ovozi, click, chime | Algoritm faqat sizning mijozlaringiz o'qiydigan kanallarni topadi. |
| 0:22–0:27 | 3. Natija | "To'g'ri auditoriya": endi tomoshabinlar nishon markaziga tushadi (1-kadrga ishora). Oldin / ADUZ bilan: ko'rishlar 38 000 → 9 500, mijozlar 2 → **64**, 1 mijoz narxi 600 000 → 4 500 so'm. **×32 ko'p mijoz** | G'alaba musiqasi, cha-ching | Ko'rishlar kamroq — mijozlar esa 32 barobar ko'p. |
| 0:27–0:32 | Yakun | ADUZ logotipi, "Biznesingiz himoyachisi!", CTA "Hoziroq sinab ko'ring" | "Ting" | ADUZ — biznesingiz himoyachisi! |

## 3-qism: "Soxta obunachilar va ishonchsizlik"

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "3-QISM · Soxta obunachilar va ishonchsizlik". "Biznes Olami" kanali — 250 000 obunachi. Tadbirkor "Farg'ona Mebel" reklamasini beradi (1,5 mln so'm). Ko'rishlar sekinlashib 1 900 da to'xtaydi, 0 reaksiya. "Kutilgan: 50 000+ · Haqiqatda: 1 900". Fonda bot avatarlar suzib yuradi | Tarang dron, sekinlashuvchi "tik"lar, past "umidsizlik" tovushi | 250 ming obunachi — lekin reklamangizni deyarli hech kim ko'rmadi. |
| 0:05–0:11 | 1. Muammo | "Obunachilar" ro'yxatini qizil chiziq skanerlaydi: user_83746251, Deleted Account, bot_5521x... har biriga BOT / O'CHIRILGAN belgisi. O'sish grafigida **+80 000 bir kunda** sakrash. Qizil belgilar: *Bot obunachilar · Sun'iy ko'rishlar · ERR 0,7% · Ishonch yo'q*. Oxirida hisoblagich 250 000 → **3 100 haqiqiy obunachi** ga tushib ketadi | Skaner, "pop"lar, buzzerlar, pastga tushuvchi tovush | Obunachilar sotib olingan: botlar, o'chirilgan akkauntlar, soxta ko'rishlar. |
| 0:11 | O'tish | Yashil doira | Whoosh | — |
| 0:11–0:16 | 2. Yechim | ADUZ "Kanal tekshiruvi": @biznes_olami kiritiladi → "Tekshirish". 4 ta tekshiruv: faol obunachilar 1,2%, bot va o'chirilgan 78%, ko'rishlar sun'iy, +80 ming / 1 kun. Ishonch reytingi **12/100**, muhr: **KATALOGGA KIRITILMADI** | Klaviatura, skaner "tik"lari, muhr zarbasi | ADUZ har bir kanalni tekshiradi: botlar, soxta ko'rishlar, sun'iy o'sish. |
| 0:16–0:22 | 2. Yechim | "Tekshirilgan kanallar": "Har bir kanal har kuni avtomatik tekshiriladi". Kartalarda qalqon belgisi va "Haqiqiy 96%". "Buyurtma berish" → "Faqat haqiqiy ko'rishlar!" | Swoosh, click, chime | Katalogda faqat haqiqiy va faol auditoriyali kanallar qoladi. |
| 0:22–0:27 | 3. Natija | "Haqiqiy auditoriya": "Reklamani ko'rganlar" to'ridagi bot avatarlar birin-ketin haqiqiy odamlarga aylanadi (haqiqiy 96%). 14 200 haqiqiy ko'rish · ERR 31% · 47 mijoz. **Ishonch reytingi 96/100** | G'alaba musiqasi, cha-ching | Endi har bir ko'rish ortida — haqiqiy odam va haqiqiy mijoz. |
| 0:27–0:32 | Yakun | ADUZ logotipi, "Biznesingiz himoyachisi!", CTA "Hoziroq sinab ko'ring" | "Ting" | ADUZ — biznesingiz himoyachisi! |

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
