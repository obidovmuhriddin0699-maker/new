# ADUZ — promo roliklar seriyasi

Har bir qism — 32 soniyalik vertikal (9:16, 1080×1920, 30 fps) motion-grafika rolik,
musiqa va SFX bilan. Telegram, Instagram Reels va YouTube Shorts uchun.

| Qism | Rolik | Mavzu |
|---|---|---|
| 1 | `ADUZ_1-qism.mp4` | Reklama bozoridagi xaos |
| 2 | `ADUZ_2-qism.mp4` | Auditoriyani topish muammosi |
| 3 | `ADUZ_3-qism.mp4` | Soxta obunachilar va ishonchsizlik |
| 4 | `ADUZ_4-qism.mp4` | Vaqtni o'g'irlaydigan jarayonlar |
| 5 | `ADUZ_5-qism.mp4` | Hisobotlarning yo'qligi |
| 6 | `ADUZ_6-qism.mp4` | ADUZ kashfiyoti |
| 7 | `ADUZ_7-qism.mp4` | Platforma interfeysi bilan tanishuv |

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
| `audio.py` | Musiqa va SFX sintezi. 1–3-qism: oddiy fon (numpy). 4-qismdan: v2 dvigatel (numpy + scipy) — 120 BPM aranjirovka (baraban, sub-bas, supersaw akkordlar, FM qo'ng'iroqchalar), reverb, sidechain, soft-clip |

Har bir qism bir xil tuzilmada: Muammo 0–11 s, Yechim 11–22 s, Natija 22–32 s.
Yangi qism qo'shish uchun `episodeN.html` faylida uchta sahna va subtitrlarni yozib,
`audio.py` ga `cues_N()` qo'shish kifoya.

Qayta yig'ish (masalan, 2-qism):

```bash
python3 audio.py 2 build/episode2.wav
node render.mjs episode2.html            # → build/episode2_silent.mp4
ffmpeg -y -i build/episode2_silent.mp4 -i build/episode2.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ADUZ_2-qism.mp4
```

4-qismdan boshlab ovoz −14 LUFS ga normallashtiriladi (`pip install scipy` kerak; 5-qism uchun raqamlarni almashtiring):

```bash
python3 audio.py 4 build/episode4.wav
node render.mjs episode4.html
ffmpeg -y -i build/episode4_silent.mp4 -i build/episode4.wav -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 44100 -c:a aac -b:a 192k -shortest -movflags +faststart ADUZ_4-qism.mp4
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

## 4-qism: "Vaqtni o'g'irlaydigan jarayonlar"

Bu qismdan boshlab motion va ovoz kuchaytirildi (`lib.js` dagi "motion toolkit" va `audio.py` dagi v2 dvigatel):
kamera harakati (asta yaqinlashish, zarbada silkinish), kinetik tipografiya (overshoot va motion-trail bilan "slam"),
zarba to'lqinlari, uchqunlar, yorug'lik chaqnashi, soat-wipe va zoom-through o'tishlari, film donadorligi va vinyetka.
Musiqa 120 BPM: har bir kesim va zarba beat'ga tushadi.

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "4-QISM · Vaqtni o'g'irlaydigan jarayonlar". Orqada katta soat: daqiqa mili tezlashib boradi, sekund mili har "tik"da sakraydi. Telegram chatlar ro'yxati: 6 ta kanal admini, yangi xabar kelgan chat tepaga ko'tariladi, o'qilmaganlar soni o'sadi. Hisoblagich: Dushanba → Seshanba → Chorshanba (aylanuvchi raqam), xabarlar 0 → 62, natija 0 | Soat taqillashi (ritm), qorong'i A-minor pad, filtrlangan bas pulsi, xabar "ding"lari | Har bir admin bilan alohida yozishish, kutish, qayta yozish... |
| 0:05–0:10.5 | 1. Muammo | Savdolashish chati: "800 000" → "600 000 bo'ladimi?" → "700 000. Oxirgi narx." → "Ertaga javob beraman...". Qizil kinetik so'zlar: *SAVDOLASHISH · KUTISH · QAYTA YOZISH*. 0:08.5 da **3 KUN** zarbasi: ekran qorayadi, zarba to'lqini, uchqunlar, qizil chaqnash | Tik-tak tezlashadi, kick qo'shiladi, glitch-zarbalar; 8.5 s da katta "boom" va crash, keyin baraban o'chib riser ko'tariladi | Narx ustida savdolashish — va bitta reklama uchun 3 kun ketadi. |
| 0:10.5–0:11 | O'tish | Soat mili aylanib ekranni yashil sahnaga "o'tkazadi", oq chaqnash | Whoosh + 11.0 s da boom | — |
| 0:11–0:16 | 2. Yechim | ADUZ "Kampaniya": sekundomer 00:00 dan boshlanadi. "Hammasini tanlash" → 6 ta checkbox kaskad bo'lib belgilanadi. "Narxlar belgilangan — savdolashish yo'q" banneri. "6 ta kanalga yuborish" bosiladi → qog'oz samolyot ekran bo'ylab uchadi | Kick + clap + hat, sub-bas, sidechain'li supersaw akkordlar (Cmaj7–Am7–Fmaj7–G), pentatonik qo'ng'iroqchalar, samolyot whoosh'i (chapdan o'ngga) | ADUZ'da narxlar oldindan belgilangan: kanallarni tanlang va yuboring. |
| 0:16–0:22 | 2. Yechim | Kanallar birin-ketin "Yuborildi" → "Tasdiqlandi". Sekundomer **00:47** da to'xtaydi. 0:18.5 da **47 SONIYA** zarbasi (oltin). "Kampaniya ishga tushdi!" oynasi | Tasdiq qo'ng'iroqchalari zinapoya bo'lib ko'tariladi, boom + crash, muvaffaqiyat akkordi | Barcha kanallar bir necha soniyada tasdiqlaydi — yozishmasiz, savdolashmasiz. |
| 0:21.75–0:22.25 | O'tish | Zoom-through: kamera ichkariga "sho'ng'iydi", oq chaqnash | Riser → whoosh → boom | — |
| 0:22–0:27 | 3. Natija | "Vaqtingiz qaytdi": orqada tinch soat. Oldin: 3 kun (uzun qizil chiziq) / ADUZ bilan: 47 soniya (kichik yashil nuqta). **5 500 barobar tezroq**. "Tejalgan vaqt — muhim ishlarga:" Mijozlar · Mahsulot · Oila nishonlari | To'liq baraban, C–G–Am–F progressiya, qo'ng'iroqcha melodiyasi, 25.0 s da boom + uchqunli "sparkle" | 3 kun o'rniga 47 soniya. Tejalgan vaqt — biznesingiz uchun. |
| 0:27–0:32 | Yakun | ADUZ logotipi, "Biznesingiz himoyachisi!", CTA "Hoziroq sinab ko'ring" | Baraban o'chadi, pad + melodiya, "ting", yakuniy C akkord | ADUZ — biznesingiz himoyachisi! |

"5 500 barobar" = 3 kun (259 200 s) / 47 s. Kanal nomlari, narxlar va vaqtlar namuna uchun qo'yilgan.

## 5-qism: "Hisobotlarning yo'qligi"

Ovoz rejissurasi (`audio.py` → `render_5`, `MixerPro`): har bir qism o'z tonalligida —
muammo A-minor (sirli, half-time), yechim C-major (iliq groove, 9-li akkordlar), natija F ga "ko'tariladi"
va plagal kadensiya (F → C) bilan tugaydi. UI tovushlari ham shu tonallikka sozlangan, shuning uchun musiqa bilan
"urishmaydi". Asboblar: Rhodes uslubidagi FM elektro-pianino, sub-bas, swing'li 16-lik hi-hat'lar, yumshoq kick va snare,
qo'ng'iroqchalar. Ishlov: ping-pong delay (nuqtali 8-lik), reverb, kick'dan sidechain, katta zarbalar oldidan teskari
"swell", musiqa o'rta chastotasida (2,2–4,2 kHz) diktor uchun joy, 300 Hz dan yuqorida stereo kengaytirish (pastki
chastotalar mono), bus-kompressor (2:1), iliqlik va "havo" EQ, yumshoq saturatsiya, −14 LUFS.

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "5-QISM · Hisobotlarning yo'qligi". Orqada "qora tuynuk": pul kupyuralari spiral bo'ylab so'rilib yo'qoladi. "Eslatmalar": 5 ta kanal xarajati, har birida qizil "natija: ?". "Jami: 1 970 000 so'm · Natija: ???" | Sirli A-minor pad, Rhodes akkordlari (delay bilan), half-time "yurak" kick, kupyuralar shitirlashi, aylanuvchi shamol | Besh kanalga reklama berdingiz — 2 million so'm sarflandi. |
| 0:05–0:10.5 | 1. Muammo | Admin bilan chat: statistika so'raladi → xira, piksellangan skrinshot "Mana" → "Aniq raqam yo'q. Taxminan ko'p bo'ldi". Qizil so'zlar: *HISOBOT YO'Q · TAXMIN · PUL QAYERDA?*. 8.5 s: **NOMA'LUM** zarbasi | Shaker kiradi, glitch-zarbalar, teskari swell → boom + snare + crash, riser | Hisobot yo'q, raqamlar taxminiy. Qaysi kanal ishladi — noma'lum. |
| 0:10.5–0:11 | O'tish | Piksel-dissolve: kadr kvadratlarga bo'linib yashil sahnaga aylanadi | C-pentatonik "raqamli uchqunlar" (32-liklarda), swell → boom | — |
| 0:11–0:16 | 2. Yechim | ADUZ "Statistika · JONLI": ko'rishlar 48 200, kliklar 3 140, mijozlar 126, 1 mijoz narxi 15 600 so'm. Soatlik grafik jonli chiziladi. "Kanallar samaradorligi" ro'yxati qayta tartiblanadi | Iliq groove: kick, snare, swing hi-hat, C–Am–F–G (9-li) Rhodes, sub-bas, delay'li qo'ng'iroqcha arpedjio; raqamlar sanalayotgandagi "tik"lar | ADUZ'da har bir kanal natijasi real vaqtda: ko'rish, klik, mijoz. |
| 0:16–0:22 | 2. Yechim | "Eng samarali" — Farg'ona 24 (42 mijoz). "Samarasiz" — Qo'qon TV (6). Barmoq uni o'chiradi, tangalar pulni eng samarali kanalga "ko'chiradi". 18.5 s: **HAR BIR SO'M — KO'RINADI**. "Hisobot tayyor!" | Toj akkordi, past "flag" tovushi, toggle "klik-tuk", tanga jiringlashi, swell → boom + akkord, chime | Samarasiz kanalni bir bosishda to'xtatib, pulni ishlayotganiga o'tkazasiz. |
| 0:21.75–0:22.25 | O'tish | Zoom-through, oq chaqnash | Riser → whoosh → boom | — |
| 0:22–0:27 | 3. Natija | "Har bir so'm hisobda": donut-diagramma 126 mijozni kanallar bo'yicha ko'rsatadi. 1 mijoz narxi 15 600 so'm (oldin: ?), tejalgan byudjet 400 000 so'm. **Har bir so'm ishlaydi** | F ga ko'tarilish, Rhodes + qo'ng'iroqcha melodiyasi, donut "sweep", tanga va uchqunlar | Endi har bir so'm qayerga ketgani va nima olib kelgani aniq. |
| 0:27–0:32 | Yakun | ADUZ logotipi, shior, CTA | Baraban o'chadi, F → C plagal kadensiya, "ting" | ADUZ — biznesingiz himoyachisi! |

Raqamlar bir-biriga mos: 5 ta kanal xarajati jami 1 970 000 so'm, mijozlar 42+9+38+31+6 = 126, 1 970 000 / 126 ≈ 15 600 so'm.
Kanal nomlari va raqamlar namuna uchun.

## 6-qism: "ADUZ kashfiyoti"

4-qism uslubida (motion toolkit + v2 ovoz dvigateli, `render_6`). Yangi o'tish: `splitDoors` — eski sahna o'rtadan
ikki eshikdek ochilib, ichidan yorug'lik bilan ADUZ chiqadi. Mux'da `loudnorm` dan keyin `alimiter` (−1,5 dBFS) qo'yilgan.

| Vaqt | Kadr | Ekranda | Audio / SFX | Diktor |
|---|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "6-QISM · ADUZ kashfiyoti". Orqada labirint devorlari paydo bo'lib boradi. Telefonda uzun "Ro'yxatdan o'tish" formasi: Ism, Familiya, Pasport, STIR, bank hisobi, MFO, yuridik manzil, shartnoma PDF... "Qadam 1/12". Pasport maydoni: "Noto'g'ri format!" (qizil, titraydi) | D-minor pad, filtrlangan bas pulsi; ritmni klaviatura taqillashi beradi; xato signali | Yangi platforma? Uzun ro'yxatdan o'tish, hujjatlar, shartnomalar... |
| 0:05–0:10.5 | 1. Muammo | "Sessiya muddati tugadi — qaytadan boshlang": forma tozalanib, qadam 4/12 → **1/12** ga qaytadi. Qizil so'zlar: *YANA BIR ILOVA? · MURAKKAB · PULIM XAVFSIZMI?*. 8.5 s: **12 QADAM — faqat ro'yxatdan o'tish uchun** | Ogohlantirish ohangi, teskari "rewind", kick + hat, glitch-zarbalar, boom + crash, riser | Murakkab bo'lsa-chi? Pulim xavfsizmi? — va siz yana eski usulda qolasiz. |
| 0:10.5–0:11 | O'tish | Kadr ikki eshikdek ochiladi, o'rtadan yorug'lik, yashil chegaralar | Og'ir "sirpanish" whoosh'i chap-o'ngga tarqaladi + yorug' "aah" xor; 11.0 s da boom | — |
| 0:11–0:16 | 2. Yechim | Telegram'da ADUZ bot: START → "/start" → "Xush kelibsiz!" kartasi → "Telegram orqali kirish" → **Kirildi**. Sekundomer 00:10 da to'xtaydi | G-major groove (G–Em–C–D), START va login kliklari, bot kartasi qo'ng'iroqchalari | ADUZ Telegramning ichida: bir bosishda kirasiz, ortiqcha hujjatlarsiz. |
| 0:16–0:22 | 2. Yechim | "Salom! Hammasi bitta joyda": 6 ta imkoniyat kartasi (Kanallar bozori, Aniq auditoriya, Tekshirilgan, Avto kampaniya, Jonli statistika, Kafolatli to'lov) kaskad bo'lib chiqadi va navbat bilan yoritiladi. 18.5 s: **1 BOSISH — va siz ichkaridasiz**. "Xush kelibsiz!" oynasi | Kartalar pentatonik kaskadi, tur "ping"lari, boom + crash + qo'ng'iroqcha akkordi, chime | Bitta joyda: kanallar bozori, tekshiruv, kampaniya, statistika va kafolatli to'lov. |
| 0:21.75–0:22.25 | O'tish | Zoom-through, oq chaqnash | Riser → whoosh → boom | — |
| 0:22–0:27 | 3. Natija | "Birinchi kundayoq": yo'l xaritasi — Ro'yxatdan o'tish (10 soniya) → Kanallarni tanlash (1 daqiqa) → Kampaniya (3 daqiqa) → **Birinchi mijoz (1-kun)**. Oltin nishonlar: Oson · Tez · Xavfsiz | C–G–Am–F, ko'tariluvchi "yo'l" tovushi, har bosqichda qo'ng'iroqcha, boom + uchqunlar | Ro'yxatdan o'tishdan birinchi mijozgacha — bir kun ichida. |
| 0:27–0:32 | Yakun | ADUZ logotipi, shior, CTA | Baraban o'chadi, "ting" | ADUZ — biznesingiz himoyachisi! |

Vaqtlar (10 soniya, 1 daqiqa, 1-kun) va "ortiqcha hujjatlarsiz" da'vosi namuna — haqiqiy jarayonga moslab tekshiring.

## 7-qism: "Platforma interfeysi bilan tanishuv"

**Ovoz arxitekturasi:** [`SOUND_ARCHITECTURE_7.md`](SOUND_ARCHITECTURE_7.md) — 7 qatlam (musiqa, muhit, UI/foley, o'tishlar,
zarbalar, brend, diktor joyi), 27 ta nomlangan tovushdan iborat kutubxona, musiqa bo'limlari va taymkodli cue-sheet.
Hujjat koddan avtomatik yaratiladi: `python3 audio.py 7 --cuesheet SOUND_ARCHITECTURE_7.md`. Qism ovozi shu cue-sheet'dan
yig'iladi (`CUES_7`, `score_7`, `render_7`), shuning uchun hujjat va ovoz doim bir xil.

**Montaj:** har bir o'tishda J-cut (tovush kesimdan oldin boshlanadi); 9.5 s da "ovoz vakuumi" — ilova yopilganda musiqa,
reverb va dumlar keskin kesiladi, faqat xona shovqini va yurak urishi qoladi; riser ataylab yarmida uziladi;
o'tishlar xilma-xil — squeegee-wipe (tartibsizlikni "artib tashlaydi") va whip-pan. Yechim musiqasi ataylab siyrak
(4 qatlam) — "sodda" xabarini aranjirovka ham aytadi. Yakunda **ADUZ sonic logo** (5–1–3 motiv) logotip bilan bir kadrda.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "7-QISM · Platforma interfeysi". Zich reklama kabineti: 6 ta tab, 9 ta mayda ikonka, 12 qatorli jadval (CPM, CTR, CPC...). Popup'lar ustma-ust: "Bid strategiyasi", "Optimallashtirish maqsadi", piksel kodi, "To'lov usuli tasdiqlanmagan", "Qo'llanma.pdf — 128 sahifa". Atrofda jargon bo'laklari aylanadi; adashgan kursor "?" bilan kezadi | Reklama kabinetini ochdingiz: o'nlab menyu, notanish atamalar... |
| 0:05–0:10.5 | 1. Muammo | Qizil so'zlar: *CPM? CTR? · QAYERDAN BOSHLASH? · QO'LLANMA: 128 SAHIFA*. 8.5 s: **CHALKASH — va siz ilovani yopasiz**. 9.6 s: ilova nuqtaga "so'rilib" yopiladi, kadr qorayadi (ovoz vakuumi) | CPM, CTR, piksel, strategiya... Qayerdan boshlash kerak? ...va ilova yopiladi. |
| 0:10.5–0:11 | O'tish | Yashil squeegee chizig'i yuqoridan pastga tartibsizlikni artib, yangi sahnani ochadi | — |
| 0:11–0:16 | 2. Yechim | ADUZ "Bugun nima qilamiz?": 3 ta katta tugma. "Reklama berish" → 1/3 "Nimani reklama qilamiz?" (Do'kon / Xizmat / Tadbir, "Har ekranda bitta savol" maslahati) → 2/3 "Byudjetingiz qancha?" katta slider 100 000 → 500 000 so'm, ≈ ko'rishlar | ADUZ boshqacha: har ekranda bitta savol, katta va tushunarli tugmalar. |
| 0:16–0:22 | 2. Yechim | 3/3 "Hammasi tayyor!" — post ko'rinishi, "Ishga tushirish" → progress → **Ishga tushdi!** 18.5 s: **3 QADAM — qo'llanmasiz**. "Kampaniya ishga tushdi!" oynasi | Uch qadam — va reklamangiz ishga tushdi. Qo'llanma shart emas. |
| 0:21.75–0:22.15 | O'tish | Whip-pan: kadr chapga "uchib" ketadi, natija o'ngdan keladi | — |
| 0:22–0:27 | 3. Natija | "Sodda — demak tez": Oldin (47 sozlama, 12 atama, 128 sahifa, 3 kun) qizil chiziq bilan o'chiriladi ↔ ADUZ (3 qadam, 0 atama, qo'llanma shart emas, 2 daqiqa). Nishonlar: Sodda · Tushunarli · O'zbekcha | Murakkablik yo'q — faqat natija. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Raqamlar (47 sozlama, 128 sahifa, 2 daqiqa) va boshqa platformaning ko'rinishi umumlashtirilgan namuna — biror real mahsulot nomi ishlatilmagan.

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
