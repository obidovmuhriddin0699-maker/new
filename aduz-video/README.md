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
| 8 | `ADUZ_8-qism.mp4` | Yagona Marketplace yechimi |
| 9 | `ADUZ_9-qism.mp4` | Aqlli kampaniya yaratish |
| 10 | `ADUZ_10-qism.mp4` | Matching algoritmi ishda |
| 11 | `ADUZ_11-qism.mp4` | Kafolatlangan xavfsizlik (Escrow) |
| 12 | `ADUZ_12-qism.mp4` | Shaffof statistika va jonli tahlil |
| 13 | `ADUZ_13-qism.mp4` | Ommaviy qamrov |
| 14 | `ADUZ_14-qism.mp4` | Vaqt mashinasi (Rejalashtirish) |
| 15 | `ADUZ_15-qism.mp4` | Ochiq haqiqat (Reyting tizimi) |
| 16 | `ADUZ_16-qism.mp4` | Bot va mutaxassis hamkorligi |
| 17 | `ADUZ_17-qism.mp4` | Topilgan daromadning erkinligi |

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

## 8-qism: "Yagona Marketplace yechimi"

**Yangi ko'rinish:** muammo sahnasida telefon yo'q — kamera katta "tartibsiz ish stoli" bo'ylab pastga suzadi
(Telegram, Direkt, Excel, daftar, stikerlar, 14 tabli brauzer, kontaktlar, chek — orasida qizil uzuq-uzuq iplar),
oxirida orqaga tortilib butun stolni bir kadrda ko'rsatadi. Yechimda ADUZ magnit bo'lib hamma bo'laklarni o'ziga tortadi,
logotip telefonga aylanadi. Natija — jonli "hub" xaritasi. Yangi o'tishlar: `implode` (spiral bo'lib markazga so'rilish)
va `cardFlip` (karta aylanishi).

**Ovoz:** [`SOUND_ARCHITECTURE_8.md`](SOUND_ARCHITECTURE_8.md) — 12 ta yangi tovush (oyna, qog'oz, stiker, tab, magnit, yutilish,
snap, savatcha, to'lov, impuls, implode, flip) va cue-sheet. Stereo kenglik hikoyaga ergashadi: muammoda har bir bo'lak ekrandagi
joyidan eshitiladi, plucklar beat'ga bo'ysunmaydi (3:4) — keng va tarqoq; magnitda kenglik 1,7 → 0,35 ga qisqarib, tovush markazga
"yig'iladi"; natijada yana keng ochiladi. Sonic logo G tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "8-QISM · Yagona marketplace". Ish stoli: adminlar chati, Direkt, `kanallar_final_2.xlsx` (#REF! bilan), daftar ("JAMI: ???"), stikerlar ("Adminga qayta yoz!", "Narx?"), 14 tabli brauzer, kontaktlar, "KIMGA?" muhrli chek. Lupa "?" bilan qidiradi | Kanallar ro'yxati — Excel'da, adminlar — chatda, narxlar — daftarda... |
| 0:05–0:10.5 | 1. Muammo | *QAYSI EXCEL? · QAYSI CHAT? · CHEK QAYERDA?*. 8.3 s: kamera orqaga tortiladi — butun tartibsizlik. **TARQOQ — 8 ta joyda, bitta reklama uchun** | Har bir kanal alohida joyda. Bitta reklama uchun — sakkizta ilova. |
| 0:10.5–0:11 | O'tish | Implosion: stol spiral bo'lib markazga so'riladi, yashil halqa | — |
| 0:11–0:16 | 2. Yechim | ADUZ magniti: 8 bo'lak chetlardan uchib kelib "yutiladi". Logo telefonga aylanadi → Marketplace: qidiruv, kategoriyalar (Moda tanlanadi), kanal kartalari. "+" bosilganda kanal savatchaga uchadi (1…5) | ADUZ hammasini bitta marketplace'ga jamlaydi: qidiring, tanlang, savatchaga qo'shing. |
| 0:16–0:22 | 2. Yechim | Savatcha: 5 kanal, jami 1 640 000 so'm → **Bitta to'lov** → To'landi. 18.5 s: **BITTA JOY — barcha kanallar · bitta to'lov**. "Buyurtma qabul qilindi!" | Besh kanal — bitta buyurtma, bitta to'lov, bitta chek. |
| 0:21.75–0:22.15 | O'tish | Karta aylanishi | — |
| 0:22–0:27 | 3. Natija | "Hammasi bir joyda": markazda ADUZ, atrofida 6 kategoriya (Yangiliklar, Moda, Biznes, Ta'lim, Sport, Oziq-ovqat), iplar bo'ylab impulslar oqadi. Oltin pillar: **1 ilova · 1 to'lov · 1 hisobot** | Barcha kanallar, to'lovlar va hisobotlar — bir joyda. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Narxlar yig'indisi: 320 000 + 280 000 + 410 000 + 250 000 + 380 000 = 1 640 000 so'm. Kanal nomlari namuna.

## 9-qism: "Aqlli kampaniya yaratish" (2-variant)

7-qism uslubida: telefon, sodda yorug' UI, kursor, squeegee va whip-pan o'tishlari, "ovoz vakuumi", taqqoslash kartasi.
Birinchi variant (boshqaruv pulti + AI paneli) git tarixida saqlangan: `8afea94`.

**G'oya:** bitta maqsad tanlaysiz — ADUZ qolgan 20 ta sozlamani o'zi to'ldiradi. Muammo va yechimda **aynan bir xil 20 ta sozlama**
ko'rsatiladi: avval qizil "Majburiy *" va "Tanlang ›" bilan, keyin ADUZ ularni domino kabi birin-ketin yashil qiymatlar bilan to'ldiradi.

**Ovoz:** [`SOUND_ARCHITECTURE_9.md`](SOUND_ARCHITECTURE_9.md). Musiqa — 7-qism aranjirovkasi 3 yarim ton yuqorida (G-minor → F-major),
seriya "qardosh" eshitilishi uchun. Imzo tovushi — avtomatik to'ldirish "domino"si: 20 ta nota F-pentatonik bo'yicha 4 oktavaga ko'tariladi.
Qoralama g'ijimlanganda ovoz vakuumi: faqat qog'oz chirsillashi va to'pning tushishi. Stereo 7-qismdan biroz torroq (telefon karnayi uchun).

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "9-QISM · Aqlli kampaniya". Telefonda "Kampaniya sozlamalari": 20 maydon, "To'ldirildi: 3 / 20", ko'pi qizil "*". "Narx strategiyasi" bosiladi — jargonli ro'yxat (Lowest cost, Cost cap, Bid cap...). Orqada tishli g'ildiraklar aylanadi | Kampaniya sozlamalari: yigirmata maydon, ko'pi majburiy... |
| 0:05–0:10.5 | 1. Muammo | "12 ta majburiy maydon to'ldirilmagan". *MAJBURIY \* · QAYSI STRATEGIYA? · YANA XATO!*. "Saqlash" → "Saqlanmadi". 8.5 s: **20 TA SOZLAMA — bitta reklama uchun**. 9.55 s: qoralama g'ijimlanib qog'oz to'pga aylanadi va tushib ketadi (ovoz vakuumi) | Strategiya, chastota, istisno auditoriya... va yana xato. ...qoralama savatga. |
| 0:10.5–0:11 | O'tish | Squeegee | — |
| 0:11–0:16 | 2. Yechim | "Maqsadingiz nima?" — 3 ta katta karta: Do'konga mijoz · Kanalga obunachi · Aksiya / chegirma. "Do'konga mijoz" tanlanadi → "ADUZ avtomatik to'ldirmoqda...": o'sha 20 ta sozlama domino kabi to'ladi (0 → 20 / 20), ro'yxat o'zi pastga suriladi | ADUZ'da faqat maqsadni tanlaysiz — qolgan sozlamalarni ADUZ o'zi to'ldiradi. |
| 0:16–0:22 | 2. Yechim | "Tavsiya etilgan reja": 500 000 so'm · 6 ta kanal · 19:00–21:00 · ≈ 9 000 ko'rish → "Ishga tushirish" → Ishga tushdi! 18.5 s: **1 TANLOV — 20 ta sozlama avtomatik** | Bir tanlov, bir bosish — va kampaniya ishga tushdi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Aqlli — demak oson": Oldin (20 ta sozlama, 12 ta majburiy maydon, "Saqlanmadi" xatosi, 1 soat) chizib o'chiriladi ↔ ADUZ (1 ta tanlov, 0 ta majburiy, avtomatik tekshiruv, 1 daqiqa). Nishonlar: Aqlli · Avtomatik · Moslashuvchan | Murakkab sozlamalar yo'q — aqlli tavsiyalar bor. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Sozlama nomlari, tavsiya qiymatlari va vaqtlar namuna — ADUZ'dagi haqiqiy avto-sozlash bilan solishtiring.

## 10-qism: "Matching algoritmi ishda"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: piksel-dissolve ("ma'lumot" mavzusi) va whip-pan.

**G'oya:** muammo — kanal **omad g'ildiragi**da tanlanadi; yechim — o'sha kanallarni Matching skaneri baholaydi, ro'yxat moslik
bo'yicha qayta tartiblanadi va eng mos kanal **radar (o'rgimchak to'ri) diagramma**sida ochiladi: sizning auditoriyangiz (uzuq chiziq)
va kanal auditoriyasi (yashil) 5 o'q bo'yicha ustma-ust.

**Ovoz:** [`SOUND_ARCHITECTURE_10.md`](SOUND_ARCHITECTURE_10.md). G'ildirak fizikasi (chiziqli sekinlashish) JS va Python'da bir xil
formula bilan hisoblanadi — 68 ta qoziq "chiq"i aynan qoziq ko'rsatkichdan o'tgan kadrga tushadi (boshida ~30/s "trrr", oxirida sekin).
G'ildirak 9.5 s da to'xtaydi — musiqa kesiladi, sukunatda yakuniy "tak" va yurak urishi: "Moslik: 12%". Skaner baholaganda har bir kanal
o'z notasida eshitiladi: yuqori moslik — baland nota, past moslik — past nota (C-pentatonik). Radar sonar "ping"i bilan ochiladi.
Musiqa — 7-qism aranjirovkasi 2 yarim ton pastda (D-minor → C-major). Sonic logo C tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "10-QISM · Matching algoritmi". Kanallar katalogi: 8 kanal, faqat obunachi soni, har birida "moslik: ?". Kursor ikkilanib kanaldan kanalga o'tadi → "Tasodifiy tanlash" | Yuzlab kanal — qaysi biri sizning mijozingizga mos? Hech kim bilmaydi. |
| 0:05–0:10.5 | 1. Muammo | Katta omad g'ildiragi aylanadi (12 kanal). *TAXMIN? · OMAD? · TAVAKKAL!*. 8.5 s: **50 / 50 — omadga ishonib reklama**. 9.5 s: g'ildirak "Toshkent Memlar"da to'xtaydi, sukunatda: **Moslik: 12%** | Shuning uchun tanlov taxminga, omadga qoladi... natija: 12% moslik. |
| 0:10.5–0:11 | O'tish | Piksel-dissolve | — |
| 0:11–0:16 | 2. Yechim | "Matching": auditoriyangiz (Farg'ona · Ayollar 20–40 · Moda). Skaner nuri ro'yxatni kezadi, har kanalda moslik halqasi to'ladi (12, 94, 23, 91, 31, 88, 18, 76). Ro'yxat moslik bo'yicha qayta tartiblanadi, top-3 ga oltin/kumush/bronza medal | ADUZ'ning Matching algoritmi har bir kanalni auditoriyangiz bilan solishtiradi. |
| 0:16–0:22 | 2. Yechim | "Ayollar Klubi — Nega mos?": radar diagramma (Hudud 96, Yosh 92, Jins 97, Qiziqish 94, Faollik 91) → "Tanlash". 18.5 s: **94% MOSLIK — taxmin emas, hisob**. "Eng mos kanallar tanlandi!" | Eng mos kanallar tepada — har biri uchun aniq moslik foizi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Aniq tanlov — aniq natija": Taxmin bilan (g'ildirak, 12%, 6 mijoz, pul havoga) chizib o'chiriladi ↔ ADUZ Matching (Matching Score, 94%, 41 mijoz, har so'm hisobda). Nishonlar: Aniq · Hisob-kitob · Tez | Taxmin emas — hisob. Natija ham shunga yarasha. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Kanal nomlari, moslik foizlari va mijozlar soni namuna (radar o'qlari o'rtachasi = 94%). Matching mezonlarini mahsulotdagi haqiqiy algoritm bilan solishtiring.

## 11-qism: "Kafolatlangan xavfsizlik (Escrow)"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: oltin doira ("seyf eshigi") va whip-pan.

**G'oya:** muammo — admin bilan chatda "avval to'lov, keyin post": 500 000 so'm o'tkaziladi, post chiqmaydi, xabarlar o'qilmaydi va
sukunat ichida admin **bloklaydi** ("Deleted Account", xabarlar yonida qizil "!"). Yechim — pul **seyfga** tushadi: disk-qulf aylanadi,
seyf qulflanadi, ustini **muz qoplaydi** ("MUZLATILDI"), vaqt tez o'tadi (18:52 → 19:00 → ertasi), bot postni tekshiradi, muz eriydi va
tanga adminga o'tadi. Pastda qoida: "Post chiqmasa — pul avtomatik qaytadi".

**Ovoz:** [`SOUND_ARCHITECTURE_11.md`](SOUND_ARCHITECTURE_11.md). Yangi tovushlar: pul o'tkazmasi, tanga, "blokladi" (og'ir eshik),
yetib bormagan xabar "!", seyf qulflanishi (thunk + uch zinali latch + metall jarang), muz kristallanishi (zichlashib boruvchi shisha
uchqunlar), muz erishi (tomchilar). Musiqa — 7-qism aranjirovkasi 5 yarim ton yuqorida (A-minor → G-major). Sonic logo G tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "11-QISM · Kafolatlangan xavfsizlik". Chat: "Reklama 500 000. Avval to'lov, keyin post." → karta raqami → bank o'tkazmasi "−500 000 so'm · Bajarildi" (tanga uchib ketadi) → "Ko'rdim. Bugun 19:00 da chiqadi" | Admin: «Avval to'lov, keyin post». Pulni o'tkazdingiz... |
| 0:05–0:10.5 | 1. Muammo | "Ertasi kuni": "Post chiqmadi-ku?", "Javob bering!", "???" — o'qilmagan. *OLDINDAN TO'LOV · POST YO'Q · JAVOB YO'Q*. 8.5 s: **500 000 → 0 — pul ham, reklama ham yo'q**. 9.55 s: "Deleted Account", "Bu foydalanuvchi sizni blokladi" (ovoz vakuumi) | Post chiqmadi. Admin javob bermaydi... va sizni bloklaydi. |
| 0:10.5–0:11 | O'tish | Oltin doira | — |
| 0:11–0:16 | 2. Yechim | "Buyurtma: Vodiy Live · 500 000 so'm · To'lov ADUZ kafolatida" → "Kafolat bilan to'lash". "Kafolat hisobi": Siz → seyf → Admin. Tanga seyfga uchadi, seyf qulflanadi, muz qoplaydi: **MUZLATILDI**. Vaqt tez o'tadi, "Post chiqdi — ADUZ bot tekshirdi" | ADUZ'da pul to'g'ridan-to'g'ri adminga emas — kafolat hisobida muzlatiladi. |
| 0:16–0:22 | 2. Yechim | "24 soat turdi" → muz eriydi → tanga adminga o'tadi → "Pul adminga o'tdi". "Post chiqmasa — pul avtomatik qaytadi". 18.5 s: **PUL HIMOYADA — post chiqmaguncha admin olmaydi** | Post chiqib, tekshiruvdan o'tgach pul adminga o'tadi. Chiqmasa — qaytadi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Pulingiz himoyada": Oldin (oldindan to'lov, post yo'q — pul ketdi, admin bloklaydi, qo'rquv) ↔ ADUZ (kafolatli to'lov, post yo'q — pul qaytadi, ADUZ nazorat qiladi, xotirjamlik). Nishonlar: Kafolat · Muzlatish · Qaytarish | Pulingiz har doim himoyada. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Escrow shartlari (24 soat, avtomatik qaytarish, bot tekshiruvi) ssenariy asosidagi namuna — ADUZ'ning haqiqiy to'lov qoidalari bilan solishtiring.

## 12-qism: "Shaffof statistika va jonli tahlil"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **chiroq yonishi** (yangi `lightsOn`: qorong'ilik →
ikki marta miltillab lyuminessent lampa yonadi) va whip-pan.

**G'oya:** muammo — "qorong'ida o'q uzish". Qorong'i xonada faqat fonar nuri yuradi; reklama posti ostida "Statistika mavjud emas".
Dartlar birin-ketin qorong'ilikka otiladi — qayerga tekkani ko'rinmaydi. 8.5 s da chaqmoq xonani bir lahzaga yoritadi: dartlar
nishonning hamma joyiga sochilib ketgan — **QORONG'IDA**. Vakuumda yana bitta dart uchadi — faqat eshitiladi ("tegdimi, yo'qmi —
noma'lum"). Yechim — chiroq yonadi: "Jonli tahlil" ekrani, hozir ko'rayotganlar hisoblagichi, haftalik **issiqlik xaritasi** (kun × soat,
qaynoq kataklar 20:00 atrofida), shaharlar bo'yicha ulush, tavsiya "postni 20:00 ga ko'chiring ≈ +38% ko'rish" → "Qo'llash" → ko'rishlar
o'sadi. Natija — yoritilgan nishon, to'rtta dart markazga.

**Ovoz:** [`SOUND_ARCHITECTURE_12.md`](SOUND_ARCHITECTURE_12.md). Yangi tovushlar: dart uchishi, dart tegishi (yog'och "tuk" + dum
titrashi), chaqmoq, elektr shiti "klak", lyuminessent lampa miltillashi (tasvirdagi miltillash kadrlari bilan sinxron), issiqlik
xaritasi "blip"lari (Bb-pentatonik zinapoya), shahar ustunlari, tavsiya "ding". Musiqa — 7-qism aranjirovkasi 4 yarim ton pastda
(C-minor → Bb-major). Sonic logo Bb tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "12-QISM · Jonli tahlil". Qorong'i xona, fonar nuri, "Farg'ona Style — reklama posti · Statistika mavjud emas". Dartlar qorong'ilikka otiladi; hisoblagich: N ta reklama · ? natija · 0 ma'lumot | Reklama berdingiz — lekin kim, qachon, qayerda ko'rdi? Qorong'i. |
| 0:05–0:10.5 | 1. Muammo | *NATIJA? · KIM KO'RDI? · QACHON?*. 8.5 s: chaqmoq — **QORONG'IDA — natijani ko'rmay reklama**. Keyin to'liq qorong'ilik (ovoz vakuumi) | Har bir reklama — qorong'ida otilgan o'q... tegdimi, yo'qmi — noma'lum. |
| 0:10.4–0:11 | O'tish | Chiroq yonishi (ikki miltillash) | — |
| 0:11–0:16 | 2. Yechim | "Jonli tahlil · 1 2xx hozir". Issiqlik xaritasi to'ladi, qaynoq kataklar belgilanadi. "Shaharlar": Farg'ona 31% · Marg'ilon 27% · Qo'qon 18% · Andijon 14% · Namangan 10%. Tavsiya: "postni 20:00 ga ko'chiring ≈ +38% ko'rish" | ADUZ'da hammasi jonli: issiqlik xaritasi qachon va qayerda ko'rishayotganini ko'rsatadi. |
| 0:16–0:22 | 2. Yechim | "Qo'llash" → "Vaqt: 19:00 → 20:00 ✓", ko'rishlar o'sadi (+N). 18.5 s: **CHIROQ YONDI — har bir ko'rish jonli**. "Hammasi ko'z oldingizda!" | Tavsiyani bir bosishda qo'llaysiz — ko'rishlar darhol oshadi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Har bir reklama — nishonga": yoritilgan nishon, 4 dart markazda. Oldin (qorong'ida otish; qachon? — noma'lum; qayerda? — noma'lum) ↔ ADUZ (jonli tahlil; eng faol: 20:00; eng faol: Farg'ona). Nishonlar: Jonli · Issiqlik xaritasi · Tavsiyalar | Endi har bir reklama — nishonga. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Raqamlar (shaharlar ulushi, ko'rayotganlar soni, "+38% ko'rish", eng faol soat 20:00) — namuna. Tavsiya va "bir bosishda qo'llash"
funksiyasi ssenariy asosida — ADUZ'ning haqiqiy statistika imkoniyatlari bilan solishtiring.

## 13-qism: "Ommaviy qamrov"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **plitkalar ag'darilishi** (yangi `tileFlip`:
kadr 6×10 plitkaga bo'linadi va ular diagonal to'lqin bo'lib ag'dariladi — muammodagi "50 ta chat devori" g'oyasining davomi) va whip-pan.

**G'oya:** muammo — 50 ta kanal = 50 ta alohida chat. Har biriga bir xil marosim: chatni ochish → "Nusxa olish" → "Joylash" →
"Yuborish"; ba'zi adminlar "Narx boshqacha, qayta yozing" deydi (qizil "!"). Soat 09:00 dan 13:40 gacha yuguradi, batareya tugaydi.
8.5 s: **14 / 50 — yarim kun, hali 36 ta qoldi**. Ovoz vakuumida telefon o'chadi ("1%"). Yechim — "Ommaviy joylash": ikki filtr
(Kiyim-kechak · Farg'ona vodiysi) → 54 kanal kaskad bilan belgilanadi → "Qamrov ≈ 186 000 obunachi" → **bitta tugma** → postlar
54 kanalga to'lqin bo'lib ketadi, telefondan qog'oz samolyotchalar uchadi. Natija — qamrov hisoblagichi o'sish grafigi bilan, kassa ovozi.

**Ovoz:** [`SOUND_ARCHITECTURE_13.md`](SOUND_ARCHITECTURE_13.md). Yangi tovushlar: plitka ag'darilishi (qog'oz "shirt", 15 ta
diagonal bilan sinxron), telefon o'chishi, "batareya 1%" ogohlantirishi, post yuborish "fiyt", kassa (tugma + quti + "ding" + tanga).
Muammoda bir xil uch bosish qayta-qayta takrorlanadi va soat tiqillashi tobora balandlashadi. Musiqa — 7-qism aranjirovkasi
2 yarim ton yuqorida (F#-minor → E-major). Sonic logo E tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "13-QISM · Ommaviy qamrov". "Kanallar · 50 ta chat" devori; 3 marta to'liq marosim: Nusxa olish → Joylash → Yuborish (2-sida admin: «Narx boshqacha»). Hisoblagich: N/50 kanal · soat · xato | 50 ta kanal — 50 ta chat. Har biriga nusxa, joylash, yuborish... |
| 0:05–0:10.5 | 1. Muammo | Tezlashgan montaj: plitkalar birin-ketin (ba'zilari qizil). *50 TA CHAT · 50 MARTA NUSXA · YANA 36 TA...*. 8.5 s: **14 / 50 — yarim kun, hali 36 ta qoldi**. 9.55 s: telefon o'chadi, "1%" | Yarim kun o'tdi — hali 14 tasi ham tayyor emas... telefon ham charchadi. |
| 0:10.35–0:11 | O'tish | Plitkalar ag'darilishi | — |
| 0:11–0:16 | 2. Yechim | "Ommaviy joylash": filtrlar → 54 kanal belgilanadi → "Qamrov ≈ 186 000 obunachi" → "54 kanalga yuborish" | ADUZ'da kanallarni tanlaysiz — 54 tasi bir zumda belgilanadi. |
| 0:16–0:22 | 2. Yechim | "Yuborilmoqda... N / 54" → "54 / 54 yuborildi". 18.5 s: **BITTA TUGMA — butun vodiyga bir bosishda**. "54 kanalga yuborildi!" | Bitta tugma — reklama hammasiga birdan yuboriladi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Bir bosishda — butun vodiy": Qamrov 0 → 186 000 (o'sish grafigi, kassa). Oldin (50 marta nusxa-joylash; yarim kun; 14/50 kanal) ↔ ADUZ (bitta tugma; 2 daqiqa; 54/54 kanal). Nishonlar: Ommaviy · Tejamkor · Qamrov | Bir bosishda — butun vodiy qamrovi. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Raqamlar (54 kanal, 186 000 obunachi, "2 daqiqa", "har bir kanal — alohida tasdiq", "bitta hisobot") — namuna; ssenariyda faqat
"50+ kanal" deyilgan. ADUZ'ning haqiqiy ommaviy joylash imkoniyatlari bilan solishtiring.

## 14-qism: "Vaqt mashinasi (Rejalashtirish)"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **uyg'onish** (yangi `eyelidOpen`: ko'z qovoqlari
ochiladi, bir pirpiraydi, keyin to'liq ochiladi; muammo sahnasida ham xuddi shu `lids()` qovoqlari kadr ustida og'irlashib yumiladi) va whip-pan.

**G'oya:** muammo — "tungi soatlardagi noqulayliklar". Qulflangan ekranda uchta tungi budilnik: 23:00, 01:00, 06:30 (har biri boshqa
kanal posti). 23:00 da budilnik chalinadi — "Kechiktirish"; ko'z qovoqlari og'irlashadi (POV), soat 23:07, admin: "Vaqt o'tdi — post
bekor qilindi". 01:00 da yana, 06:30 da yana. 8.5 s: **UYQUSIZ TUN — har bir post alohida budilnik**. Ovoz vakuumida ko'zlar yumiladi.
Yechim — uyg'onish, "Rejalashtirish": kun (Seshanba) → soat barabani 19:00 → 23:00 → navbatga 23:00, 01:00, 06:30 → "Rejalashtirish".
Keyin "vaqt mashinasi": telefon orqasida katta soat aylanadi, sarlavha osmoni kechqurundan tunga va tongga o'tadi (oy → quyosh),
"Siz: uxlayapsiz zzz", har post o'z vaqtida "Chiqdi ✓". Natija — soat millari 23:00 dan 07:00 gacha aylanadi, uchta yashil belgi.

**Ovoz:** [`SOUND_ARCHITECTURE_14.md`](SOUND_ARCHITECTURE_14.md). Yangi tovushlar: budilnik (tonallikdagi marimba-arpedjio),
vibratsiya, uyquli nafas, ko'z yumilishi "shirt", ertalabki qushlar (uyg'onishda va lapse oxirida — tong). Muammoda devor soati
tiqillaydi; yechimdagi lapse paytida tiqillash tezlashadi. Musiqa — 7-qism aranjirovkasi 3 yarim ton pastda (C#-minor → B-major).
Sonic logo B tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "14-QISM · Vaqt mashinasi". Tungi qulflangan ekran 22:58, uchta budilnik. 23:00: "Postni joylang!" → "Kechiktirish", qovoqlar og'irlashadi | Tungi post — tungi budilnik. 23:00... yana besh daqiqa... |
| 0:05–0:10.2 | 1. Muammo | 23:07, admin: "Vaqt o'tdi — post bekor qilindi" (23:00 kartasi "Kechikdi"). *TUNGI 23:00 · 01:00 — YANA · 06:30 — YANA* (budilniklar). 8.5 s: **UYQUSIZ TUN**. Ko'zlar yumiladi (ovoz vakuumi) | Kechikdingiz — post bekor. 01:00 da yana, 06:30 da yana... uyqu ham, reklama ham yo'q. |
| 0:10.2–0:11 | O'tish | Uyg'onish: qovoqlar ochiladi, pirpirash | — |
| 0:11–0:16 | 2. Yechim | "Rejalashtirish": post "Yangi kolleksiya — 30% chegirma", kun Seshanba, soat barabani → 23:00, navbat: 23:00 · 01:00 · 06:30 → "3 ta post rejada" | ADUZ'da kun va soatni tanlaysiz — postlar navbatga turadi. |
| 0:16–0:22 | 2. Yechim | Vaqt mashinasi: soat 22:59 → 07:00, oy → quyosh, "Siz: uxlayapsiz", har post "Chiqdi ✓". 18.5 s: **AVTOMATIK — siz uxlaysiz, post o'z vaqtida**. "Hammasi o'z vaqtida chiqdi!" | Siz uxlaysiz — taymer har birini o'z vaqtida joylaydi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Siz uxladingiz — reklama ishladi": soat 23:00 → 07:00, uchta ✓ (kassa). Oldin (tunda budilnik; 23:07 — kechikdi; uyqusiz tun) ↔ ADUZ (avtomatik taymer; aniq 23:00; tinch uyqu). Nishonlar: Taymer · Kalendar · Tinch uyqu | Vaqtingiz — sizniki, reklama — o'z vaqtida. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Kanal nomlari, vaqtlar va post matni ("30% chegirma") — namuna. Rejalashtirish interfeysi (kun, soat barabani, navbat) ssenariy
asosida — ADUZ'ning haqiqiy rejalashtirish imkoniyatlari bilan solishtiring.

## 15-qism: "Ochiq haqiqat (Reyting tizimi)"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **shisha sinishi** (yangi `cracks()` + `shatter`:
vakuumda kadr shishadek yoriladi va to'xtab turadi, keyin yoriqlar bo'ylab parchalanib tushadi — ortidan yechim ochiladi) va whip-pan.

**G'oya:** muammo — "soxta skrinshotlar va isbotlar". Admin chatda "isbot" yuboradi: statistika skrinshoti "50 000 ko'rish" va
"340 ta buyurtma!" + besh yulduzli sharh. Kadrga **lupa** kiradi: uning ichida asl holat ko'rinadi — "4 200", "3 ta buyurtma",
sharh muallifi "@user8812 · bot · 0 obunachi", qizil "TAHRIRLANGAN" belgilari. *SOXTA SKRIN · KO'PAYTIRILGAN · BOT SHARH*.
8.5 s: **SOXTA ISBOT — skrinshot isbot emas**; vakuumda ishonch "sinadi". Yechim — "Kanal profili": reyting 4.6 (1 248 ta baho),
yulduzlar taqsimoti, qoida "Baho — faqat buyurtma bergan mijozdan", uchta sharh (5, 4 va halol 3 yulduz) — har biriga
"Tasdiqlangan buyurtma #…" muhri; "Buyurtma berish". Natija — beshta oltin yulduz (4.6), kassa.

**Ovoz:** [`SOUND_ARCHITECTURE_15.md`](SOUND_ARCHITECTURE_15.md). Yangi tovushlar: skrinshot (kamera zatvori), lupa foshi
(shisha shimmer + pastga tushuvchi "vuuu"), shisha yorilishi va g'ichirlashi (vakuum ichida), shisha sinishi (70 ta parcha jarangi),
"Tasdiqlangan" muhri. Musiqa — 7-qism aranjirovkasi 1 yarim ton yuqorida (F-minor → Eb-major). Sonic logo Eb tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "15-QISM · Ochiq haqiqat". Chat "Super Kanal UZ · admin": "Mana isbot:" → skrinshot "50 000 ko'rish" → skrinshot "340 ta buyurtma!" ★★★★★ «Zo'r kanal!!!» → "Narxi 800 000. Bugun band qiling!" | Admin «isbot» yuboradi: 50 000 ko'rish, 340 ta buyurtma... |
| 0:05–0:10.3 | 1. Muammo | Lupa: 50 000 → 4 200, 340 → 3, @aziza_shop → bot. *SOXTA SKRIN · KO'PAYTIRILGAN · BOT SHARH*. 8.5 s: **SOXTA ISBOT**. 9.5 s: kadr yoriladi (ovoz vakuumi) | Lekin skrinshotni tahrirlash — bir daqiqalik ish... ishonch sinadi. |
| 0:10.3–0:11 | O'tish | Shisha parchalanadi | — |
| 0:11–0:16 | 2. Yechim | "Kanal profili · Vodiy Live": 4.6 ★, 1 248 ta baho, taqsimot; "Baho — faqat buyurtma bergan mijozdan"; sharhlar + "Tasdiqlangan buyurtma" | ADUZ'da reyting ochiq: baho faqat haqiqiy buyurtmadan keyin. |
| 0:16–0:22 | 2. Yechim | "Buyurtma berish" → "Ishonch bilan buyurtma ✓". 18.5 s: **OCHIQ HAQIQAT — har bir baho haqiqiy buyurtmadan**. "Ishonch bilan tanlang!" | Sharhlarni haqiqiy mijozlar yozadi — tahrirlab bo'lmaydi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Haqiqat — ko'z oldingizda": 5 yulduz (4.6 · 1 248 ta haqiqiy baho), kassa. Oldin (soxta skrinshot; bot sharhlar; ko'r-ko'rona ishonch) ↔ ADUZ (ADUZ statistikasi; tasdiqlangan sharh; ochiq reyting). Nishonlar: Reyting · Tasdiqlangan · Shaffof | Ishonch — skrinshotda emas, ochiq reytingda. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Raqamlar (4.6, 1 248 ta baho, taqsimot foizlari, obunachilar, buyurtma raqamlari) va sharh matnlari — namuna. "Baho faqat
buyurtmadan keyin" va "sharhlar tahrirlanmaydi" qoidalari ssenariy asosida — ADUZ'ning haqiqiy reyting qoidalari bilan solishtiring.

## 16-qism: "Bot va mutaxassis hamkorligi"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **bitta chiziq** (chigal simlar tortilib bitta
yashil chiziqqa aylanadi, yangi `slitOpen` esa kadrni shu chiziqdan ochadi) va whip-pan.

**G'oya:** muammo — "murakkab texnik integratsiya". Telefonda kod muharriri: "Kanalni ulash · 1/12 qadam", `POST /api/v2/…`,
`Bearer` token, webhook, SSL; konsolda xatolar (401, SSL, timeout, 403). Telefon atrofida rang-barang **simlar** chiqib, tobora
chigallashadi, xatolarda uchqun sachraydi. *API TOKEN? · WEBHOOK? · 401 XATO*. 8.5 s: **CHIGAL — kanal ulash dasturchi ishi**.
Vakuumda qisqa tutashuv: chiroqlar o'chadi, ekran qorayadi. Yechim — Telegram'da "Vodiy Live › Administratorlar › + Admin qo'shish"
→ "@aduz_bot" → uchta huquq (xabar joylash, tahrirlash, statistika) → "Saqlash". ADUZ'da: botdan kanalga **bitta kabel** ulanadi →
"Kanal ulandi", ro'yxat (avto-joylash, jonli statistika, kafolatli to'lov) va **mutaxassis** Dilshod: "Salom! Kanalingiz ulandi.
Birinchi reklamani birga sozlaymiz." Natija — kanal va bot avatarlari yashil kabel bilan ulanadi, ma'lumot impulslari oqadi.

**Ovoz:** [`SOUND_ARCHITECTURE_16.md`](SOUND_ARCHITECTURE_16.md). Yangi tovushlar: elektr uchquni, qisqa tutashuv (portlash +
pasayuvchi g'uvullash), kuygan sim vishillashi, simlar tortilishi "tang", vilka rozetkaga (klak + uchqun + yoqilish toni).
Kod yozish va "@aduz_bot" — klaviatura. Musiqa — 7-qism aranjirovkasi 1 yarim ton pastda (Eb-minor → Db-major). Sonic logo Db tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "16-QISM · Oson ulanish". Kod: POST /api/v2/channels/connect, token, webhook; konsol: 401, SSL, timeout. Simlar chiqadi | Kanalni ulash: API token, webhook, kod... 12 ta qadam. |
| 0:05–0:10.3 | 1. Muammo | 403 xato, simlar telefon ustidan kesib o'tadi. *API TOKEN? · WEBHOOK? · 401 XATO*. 8.5 s: **CHIGAL**. 9.5 s: qisqa tutashuv (ovoz vakuumi) | Xato ustiga xato — dasturchisiz iloji yo'q... va hammasi kuyib ketdi. |
| 0:10.3–0:11 | O'tish | Simlar bitta yashil chiziqqa → kadr chiziqdan ochiladi | — |
| 0:11–0:16 | 2. Yechim | Telegram: Administratorlar → + Admin qo'shish → @aduz_bot → 3 ta huquq → Saqlash. ADUZ: vilka ulanadi → "Kanal ulandi" | ADUZ'da botni kanalga admin qilasiz — tamom, ulandi. |
| 0:16–0:22 | 2. Yechim | Ro'yxat ✓✓✓; mutaxassis Dilshod xabari. 18.5 s: **BOT + MUTAXASSIS — kod yozmasdan, bitta qadamda**. "Kanal ulandi!" | Texnik ishni bot bajaradi, savollarga mutaxassis javob beradi. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Ulanish — bitta qadam": VL ↔ bot yashil kabel, ✓ (kassa). Oldin (API, webhook, kod; dasturchi kerak; kunlab sozlash) ↔ ADUZ (botni admin qilish; mutaxassis yordami; bir necha daqiqa). Nishonlar: Oson ulanish · Aqlli bot · Mutaxassis | Kod yo'q, chigal yo'q — bitta qadam. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Bot nomi (@aduz_bot), huquqlar ro'yxati, mutaxassis ismi va "bir necha daqiqa" — namuna. Ulanish jarayoni ssenariy asosida ("botni
admin qilish orqali oson ulanish") — ADUZ'ning haqiqiy bot nomi, kerakli huquqlar va qo'llab-quvvatlash xizmati bilan solishtiring.

## 17-qism: "Topilgan daromadning erkinligi"

7-qism uslubida (telefon, sodda UI, ovoz vakuumi, taqqoslash kartasi). O'tishlar: **zanjir uzilishi** (vakuumda ikki zanjir kadrni
X shaklida o'raydi va markazga qulf osiladi; 10.3 s da zanjirlar uzilib sochiladi, qulf pastga tushadi) → oltin doira (`circleWipe`) va whip-pan.

**G'oya:** muammo — "pullarni yechib olishdagi bahonalar". Admin hamyonida 2 450 000 so'm, lekin "Yechib bo'lmaydi" (qulf belgisi).
Har "Pulni yechish" bosilishida yangi bahona kartasi yopishadi: faqat oyning 1-sanasida · minimal summa 3 000 000 · komissiya 15% ·
ko'rib chiqish 14 kun · operator: «Ertaga albatta...» · texnik ishlar. Kutish hisoblagichi 0 → 14 kun. *BAHONA · YANA BAHONA ·
14 KUN KUTING*. 8.5 s: **QULFDA — o'z pulingiz o'zingizga berilmaydi**. Yechim — ADUZ "Daromad": balans va oxirgi tushumlar →
"Kartaga yechish" → Uzcard •••• 4417 → "Hammasi" → "Muddat: darhol · istalgan vaqtda" → "Tasdiqlash". Telefon kichrayadi, pastda
bank kartasi paydo bo'ladi va 16 ta tanga unga oqib tushadi (balans 2 450 000 → 0, karta 0 → 2 450 000), SMS: "+2 450 000 so'm
kelib tushdi". Natija — tanga yomg'iri kartaga, kassa.

**Ovoz:** [`SOUND_ARCHITECTURE_17.md`](SOUND_ARCHITECTURE_17.md). Yangi tovushlar: zanjir shaldirashi, qulf (og'ir klak), zanjir
uzilishi (chars + jarang + halqalar sochilishi), SMS signali. Bahona kartalari — stiker "shap" + rad signali; tangalar — har biri
alohida. Musiqa — 7-qism aranjirovkasi 4 yarim ton yuqorida (G#-minor → F#-major). Sonic logo F# tonikada.

| Vaqt | Kadr | Ekranda | Diktor |
|---|---|---|---|
| 0:00–0:05 | 1. Muammo | "17-QISM · Daromad erkinligi". "Daromadim · Balans 2 450 000 so'm" → "Pulni yechish" → bahonalar: 1-sana, minimal summa, komissiya 15% | Daromad bor — lekin yechib bo'lmaydi. Har safar yangi bahona. |
| 0:05–0:10.3 | 1. Muammo | "14 kun", «Ertaga albatta...», "Texnik ishlar". *BAHONA · YANA BAHONA · 14 KUN KUTING*. 8.5 s: **QULFDA**. 9.5 s: zanjir + qulf (ovoz vakuumi) | Minimal summa, komissiya, «14 kun kuting»... pulingiz — qulf ostida. |
| 0:10.3–0:11 | O'tish | Zanjir uziladi → oltin doira | — |
| 0:11–0:16 | 2. Yechim | "Daromad" → "Kartaga yechish" → Uzcard → "Hammasi" → "Tasdiqlash" → tangalar kartaga | ADUZ'da daromadni istalgan vaqtda kartaga yechasiz. |
| 0:16–0:22 | 2. Yechim | SMS "+2 450 000 so'm kelib tushdi". 18.5 s: **PUL — SIZNIKI — istalgan vaqtda, kartaga**. "Pul kartangizda!" | Bir necha bosish — pul kartangizda. Bahonasiz. |
| 0:21.75–0:22.15 | O'tish | Whip-pan | — |
| 0:22–0:27 | 3. Natija | "Topgan pulingiz — sizniki": tanga yomg'iri, karta 2 450 000 so'm (kassa). Oldin (14 kun kutish; bahona va «ertaga»; pul qulf ostida) ↔ ADUZ (bir necha daqiqa; istalgan vaqtda; pul kartangizda). Nishonlar: Tezkor · Kartaga · 24/7 | Topgan pulingiz — sizniki. Istalgan payt. |
| 0:27–0:32 | Yakun | ADUZ logotipi + sonic logo, shior, CTA | ADUZ — biznesingiz himoyachisi! |

Summalar, karta raqamlari, "darhol", "bir necha daqiqa" va "24/7" — namuna. Yechib olish shartlari (muddat, komissiya, minimal summa,
qo'llab-quvvatlanadigan kartalar) — ADUZ'ning haqiqiy to'lov qoidalari bilan solishtiring.

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
