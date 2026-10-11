# ADUZ · "Reklama degani shumi?!" — BOSQICH 2
## 1-hafta (1–7-kunlar): suratga olishga tayyor ssenariylar

> **Yangilangan ma’lumotlar (mijozdan):**
> - ADUZ boti: **@Targetreklammabot** (manzil mijoz tomonidan tasdiqlangan). Barcha funksiyalar ✅ **ishlamoqda**.
> - Videolardagi yagona haqiqiy shaxs — **ADUZ platformasi asoschisi** (taqdim etilgan foto). Rustam aka, Dilnoza va Shokir — to‘qima obrazlar.
> - Jasur obrazi bekor qilindi: ADUZ vakili rolini endi **asoschining o‘zi** o‘ynaydi. Ssenariyda u **"ASOSCHI"** deb belgilangan, qahramonlar unga "uka" yoki "siz" deb murojaat qiladi. Ekranda tanishtiruv yozuvi: *"Muxriddin Obidov — ADUZ asoschisi"* (yozuv montajda qo‘shiladi). 8-kundan boshlab qahramonlar unga "Muxriddin" yoki "Muxriddin uka" deb murojaat qiladi.
> - 1-haftada asoschi faqat 7-kun oxirida paydo bo‘ladi. 1–6-kunlarning "Yechim" qismida botning **haqiqiy ekran yozuvi** (2–4 soniya) va qisqa brend ovozi ishlatiladi.
> - Dilnoza obrazi uchun standart variant tanlandi: ro‘molsiz. Muqobil satr 0.2-bo‘limda.

---

# 0. UMUMIY ISHLAB CHIQARISH QOIDALARI (barcha 7 video uchun)

## 0.1. Kadr, matn va logotip joylashuvi (1080 × 1920, 9:16)

| Element | Joylashuv | Qoida |
|---|---|---|
| Instagram UI xavfli zonasi | Yuqori 220 px, pastki 420 px, o‘ng 140 px | Muhim matn va yuzlar bu zonaga tushmasin |
| Seriya belgisi | Chap yuqori (x 60, y 240) | *"Reklama degani shumi?! · N-qism"*, 34 px, oq, 80% shaffoflik |
| ADUZ logotipi | O‘ng yuqori (x 900, y 240), kengligi 120 px | **Faqat montajda qo‘shiladi**, butun video davomida bir joyda |
| Subtitrlar | Markazdan pastroq, y 1250–1450 | Montserrat/Inter ExtraBold 64–70 px, oq matn, 6 px qora kontur. Bir qatorda 32 belgidan oshmasin, ko‘pi bilan 2 qator |
| Ekran sarlavhasi (hook matni) | Yuqori uchdan bir qism, y 380–600 | 80–96 px, sariq aksent |
| "Muammo hisoblagichi" | O‘ng tomon, y 700 | Raqamli "tablo" uslubi, qizil raqamlar |
| "Shartli misol" belgisi | Raqam yonida | 30 px, kulrang plashka |

**Vaqtinchalik brend ranglari** (haqiqiy brendbuk kelguncha): asosiy rang to‘q ko‘k `#0F3D91`, aksent sariq `#FFC83D`, xato yoki muammo uchun qizil `#E5484D`, fon oq yoki juda och kulrang.

## 0.2. Qahramonlar uchun "character sheet" promptlari (inglizcha, har klipda so‘zma-so‘z qo‘shiladi)

**RUSTAM (Rustam aka):**
`Uzbek man, 42 years old, medium height, slightly heavy build, short black hair with grey temples, thick black mustache, clean-shaven chin, warm brown eyes, navy blue classic jacket over a white open-collar shirt (no tie), silver wristwatch on left wrist, dark grey trousers, black leather shoes. Expressive, friendly face.`

**DILNOZA:**
`Uzbek woman, 26 years old, slim, black hair tied in a low bun, thin black-framed glasses, oversized beige knit sweater, black trousers, white wireless headphones resting around her neck, always holding a smartphone. Smart, quick, slightly ironic expression.`
*(Ro‘molli muqobil: `... wearing a simple light-grey headscarf neatly tied, ...` — "black hair tied in a low bun" o‘rniga.)*

**SHOKIR:**
`Uzbek young man, 19 years old, slim, black baseball cap worn backwards, navy tracksuit with two white stripes, white sneakers, holding two smartphones at once. Overconfident, energetic grin.`

**ASOSCHI** (haqiqiy shaxs, 7-kundan boshlab):
`Use the provided reference photo for exact face identity. Central Asian (Uzbek) man, around 30 years old, short neat black hair combed to the side, straight dark eyebrows, rimless rectangular eyeglasses with thin dark temples, clean-shaven, calm and confident composed expression, crisp white collared shirt with the top button open, dark trousers. Holds a smartphone. Speaks calmly, never exaggerated.`

> **Asoschi kadrlari bo‘yicha tavsiya:** u haqiqiy odam, shuning uchun uning qismlarini **jonli suratga olish** eng yaxshi variant: ishonch yuqoriroq bo‘ladi va AI yuzni buzish xavfi yo‘qoladi. Qolgan to‘qima qahramonlar bilan bitta kadrda bo‘lsa, ikki yo‘l bor: (1) asoschini yashil fonda yoki shunga o‘xshash yorug‘likda suratga olib, AI sahnaga montaj qilish; (2) foto-reference bilan image-to-video. Har ikkala holatda asoschining roziligi bor, lekin AI yaratgan realistik videolarni Instagramda **"AI info" belgisi** bilan joylashni unutmang.

**Lokatsiyalar:**
- **Do‘kon:** `small furniture showroom in Fergana, Uzbekistan: grey and beige sofas with price tags, wooden cashier desk, warm fluorescent + daylight from a glass storefront, a red "SALE" style paper sign on the wall with no readable text.`
- **Dilnozaning xonasi:** `cozy small home office: wooden desk, laptop, ring light, cup of green tea in a traditional Uzbek piala (blue cotton pattern), wall covered with colorful sticky notes, potted plant.`

## 0.3. Asosiy negative prompt (har klipga)
`no readable text, no letters, no logos, no watermarks, no subtitles, no distorted hands, no extra fingers, no melting faces, no face changes between shots, no change of clothing, no cartoon style, no oversaturated colors, no Western suburban interiors, no snow, no fisheye distortion, no camera shake beyond handheld, no exaggerated mouth movements`

## 0.4. Texnik ish oqimi (AI video)
1. **Gemini Pro** — ssenariyni takomillashtirish, dialog variantlari, storyboard va har kadr uchun inglizcha promptni aniqlashtirish. Gemini versiyangizda video generatsiya bo‘lmasligi mumkin, shuning uchun video alohida generatorda (masalan, Veo, Kling, Runway yoki Sora kabi) yaratiladi.
2. **Klip uzunligi:** generatorlar odatda 5–10 soniyalik klip beradi. Har video uchun 4–7 ta klip yarating va montajda yig‘ing.
3. **Ovoz:** o‘zbekcha dialogni haqiqiy ovoz aktyori yoki sifatli TTS bilan alohida yozing. Lab harakatini moslash (lip-sync) alohida vosita bilan qilinadi. Lip-sync sifatsiz chiqsa, kadrni qahramonning orqasidan, telefon ekranidan yoki o‘rta plandan oling: bunda ovoz "kadr ortidan" eshitiladi.
4. **Matnlar:** barcha o‘zbekcha yozuvlar, chat oynalari, Telegram interfeysi, narxlar, logotip va hisoblagich **montajda** (CapCut, Premiere, DaVinci) qo‘shiladi. Generatorda ekranlar bo‘sh yoki xira bo‘lsin.
5. **Telegram ekranlari:** haqiqiy Telegram interfeysining nusxasi o‘rniga oddiy, brendsiz "chat maketi" ishlating (Figma yoki CapCut shablon): bu ham xavfsizroq, ham o‘qishga osonroq.
6. **Bir xillik:** har qahramon uchun 1 ta "reference" rasm yarating va barcha klipsda "image-to-video" / reference sifatida ishlating.

## 0.5. Gemini uchun universal prompt shabloni
```
Sen o‘zbek tilidagi Instagram Reels komediya ssenariynavisisan.
Quyidagi ssenariyni yaxshila:
1) Dialoglarni Farg‘ona vodiysidagi tabiiy so‘zlashuvga yaqinlashtir, lekin butun O‘zbekiston tushunsin.
2) Har replika 7 so‘zdan oshmasin.
3) Hookni yanada keskin qilib, 3 ta muqobil variant ber.
4) Punchline uchun 3 ta muqobil variant ber.
5) Har kadr uchun ingliz tilida video-generator promptini yoz (9:16, realistik, kino yorug‘ligi).
6) Soxta statistika, kafolat va raqobatchi nomlarini qo‘shma.
Ssenariy: [SSENARIYNI SHU YERGA QO‘YING]
```

---
# 1-KUN

**KUN:** 1
**VIDEO RAQAMI:** 01
**SARLAVHA:** "3 kun, 0 kanal"
**MAQSADLI AUDITORIYA:** biznes egasi
**VIDEO MAQSADI:** ko‘rish + izoh
**DAVOMIYLIGI:** 35 soniya
**FORMAT:** komediya
**SERIAL BILAN BOG‘LANISH:** Serialning birinchi qismi. Rustam aka va uning maqsadi (kuzgi divan kolleksiyasini sotish) tanishtiriladi. Oxirida u nihoyat 3 ta kanal topadi, keyingi qismda esa narx so‘raydi.

### A. HOOK (0–3 s)
Rustam aka do‘kondagi divanda chalqancha yotibdi, telefonni yuziga qo‘ygan. Telefonni ko‘tarib, charchagan ovozda:
**RUSTAM:** "«Telegramda reklama berish oson» deyishdi..."
Ekranda: **"3-KUN. HALI HAM KANAL QIDIRYAPMAN."**

### B. VAZIYAT (3–10 s)
Flashback, kadr yorqinroq. 1-kun, Rustam aka g‘ayratli, qo‘llarini ishqalaydi:
**RUSTAM:** "Bir soatda topaman! Telegram-ku bu!"
U qidiruvga "Farg‘ona mebel reklama" deb yozadi. Ekranda natijalar maketi chiqadi: oxirgi posti 2021-yilda bo‘lgan kanal, "admin bilan bog‘lanish" tugmasi yo‘q kanal.

### C. ASOSIY VOQEA (10–20 s)
Tez montaj: Rustam aka adminlarga birma-bir yozadi. Javoblar ekranda chat pufakchalari bo‘lib chiqadi:
- "Narx lichkada." → **RUSTAM:** "Men lichkadaman-ku!"
- "Admin hozir band, keyinroq yozing."
- 3 daqiqa 40 soniyalik ovozli xabar. Rustam aka uni eshitib ulgurmay uxlab qoladi.
Hisoblagich: **"Yozilgan adminlar: 12 · Javob: 2"**

### D. YECHIM (20–30 s)
Kadr muzlaydi, ADUZ uslubidagi grafika chiqadi. Botning **haqiqiy ekran yozuvi** (3 s): reklama beruvchi bo‘limida kanallar ro‘yxati ochiladi.
**OVOZ (diktor, xotirjam):** "Kanal qidirish uch kun emas, bir necha daqiqa olishi mumkin. ADUZ'da Telegram kanallari bir joyda jamlangan."
Ekranda: **"Kanallar — bir joyda. ADUZ"**

### E. YAKUNIY BURILISH (30–33 s)
Do‘kon eshigi ochiladi, haqiqiy xaridor kiradi:
**XARIDOR:** "Aka, divan bormi?"
**RUSTAM** (telefondan ko‘zini uzmay): "Hozir emas, uka, mijoz qidiryapman!"
Xaridor hayron bo‘lib chiqib ketadi. Rustam aka 2 soniyadan keyin tushunadi va kameraga qaraydi. "Ding" ovozi.

### F. CTA (33–35 s)
Ekranda: **"Siz reklama uchun kanalni qanday topasiz? Izohda yozing 👇"**
Pastda: *"Ertaga: 3 ta kanal topildi... endi narx so‘raymiz."*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Tepadan (top-down), o‘rta plan | Divanda yotibdi, telefonni yuzidan oladi | "«Telegramda reklama berish oson» deyishdi..." | 3-KUN. HALI HAM KANAL QIDIRYAPMAN. | Soat chiqillashi, uzun xo‘rsinish | Jump-cut yo‘q, kadr bir butun | Oq "flash" + rewind ovozi |
| 2 | 3–6 | Ko‘z darajasi, o‘rta plan | Qo‘llarini ishqalab, ishonch bilan telefonni oladi | "Bir soatda topaman! Telegram-ku bu!" | 1-KUN, 09:00 | Ko‘tarinki qisqa musiqa | Ranglar to‘yinganroq (flashback) | Tez zoom-in telefonga |
| 3 | 6–10 | Telefon ekrani (insert) | Barmoq qidiruv yozadi, natijalar aylanadi | — | Qidiruv maketi, "oxirgi post: 2021" | Klaviatura ovozi | Ekran maketi montajda | Swipe up |
| 4 | 10–16 | Yelka ortidan (OTS) + yaqin plan, navbatma-navbat | Yozadi, javob o‘qiydi, peshonasiga uradi | "Men lichkadaman-ku!" | Chat pufakchalari | Telegram'ga o‘xshash "ding" (o‘ziga xos, brendsiz) | Har 1,5 soniyada kesish | Match cut |
| 5 | 16–20 | Yon tomondan, o‘rta plan | Ovozli xabar eshitib uxlab qoladi | — | ▶ 3:40 · Yozilgan: 12 · Javob: 2 | Monoton "bla-bla" ovozi, xurrak | Speed ramp (tezlashtirish) | Freeze frame |
| 6 | 20–30 | Grafika + bot ekran yozuvi | — | Diktor matni | Kanallar — bir joyda. ADUZ | Yengil texno-tovush, "whoosh" | Ekran yozuvi telefon maketi ichida | Zoom-out |
| 7 | 30–33 | Do‘kon eshigidan keng plan | Xaridor kiradi va chiqib ketadi | "Aka, divan bormi?" / "Hozir emas, uka, mijoz qidiryapman!" | — | Eshik qo‘ng‘irog‘i | Pauza 1 s | Kameraga qarash |
| 8 | 33–35 | Rustam akaning yaqin plani | Kameraga ma’noli qaraydi | — | CTA + "Ertaga..." | "Ding" + musiqa tugaydi | Matn animatsiyasi | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> 0.5-bo‘limdagi shablonga quyidagini qo‘shing: *"Bu serialning 1-qismi. Rustam aka xarakterini birinchi 5 soniyada esda qolarli qilib ko‘rsatish kerak. Punchline — u mijoz qidirib, haqiqiy mijozni qaytarib yuboradi. Shu kulgini kuchaytiradigan 3 variant ber."*

**Video promptlar (inglizcha):**

*Klip 1 (0–3 s):*
`Vertical 9:16, realistic cinematic. Top-down medium shot of [RUSTAM character sheet] lying exhausted on a grey sofa inside [furniture showroom], smartphone resting on his face. He slowly lifts the phone off his face and stares at the ceiling with a tired, comic expression. Soft warm interior light, late afternoon. Static camera.`

*Klip 2 (3–6 s):*
`Vertical 9:16, realistic. Eye-level medium shot of [RUSTAM] standing in the same showroom in the morning, energetic, rubbing his hands together and confidently picking up his smartphone. Bright morning daylight from the storefront, slightly warmer color grade. Slow push-in.`

*Klip 4 (10–16 s):*
`Vertical 9:16, realistic. Over-the-shoulder shot of [RUSTAM] typing fast on his smartphone at the wooden cashier desk, then close-up of his face reacting with disbelief and lightly slapping his own forehead. Phone screen blurred (content added in post). Handheld, subtle movement.`

*Klip 5 (16–20 s):*
`Vertical 9:16, realistic. Side medium shot of [RUSTAM] sitting on the sofa holding the phone to his ear, eyelids getting heavy, he slowly falls asleep sitting up, head tilting. Comic timing, warm light. Static camera.`

*Klip 7 (30–33 s):*
`Vertical 9:16, realistic. Wide shot from the showroom entrance: a young Uzbek customer in a casual jacket walks in and asks something; [RUSTAM] waves him off without looking up from his phone; customer shrugs and leaves. [RUSTAM] freezes, slowly realizes, looks directly at the camera. Natural daylight.`

**Kamera va yorug‘lik:** issiq, iliq do‘kon yorug‘ligi (3200–4000K), flashback 5600K va yorqinroq. Kamera asosan statik, chat qismlari qo‘lda olingan (handheld).

**O‘zbekcha dialog va subtitrlar:**
```
00:00 «Telegramda reklama berish oson» deyishdi...
00:03 Bir soatda topaman! Telegram-ku bu!
00:10 «Narx lichkada.»
00:11 Men lichkadaman-ku!
00:20 Kanal qidirish uch kun emas,
00:23 bir necha daqiqa olishi mumkin.
00:26 ADUZ'da Telegram kanallari bir joyda jamlangan.
00:30 Aka, divan bormi?
00:31 Hozir emas, uka, mijoz qidiryapman!
```

**Bir xillik uchun:** Rustam akaning kurtkasi, soati va mo‘ylovi barcha kliplarda bir xil bo‘lsin. Reference rasmni har klipga bering. Divanlar rangi (kulrang/bej) va kassa stoli o‘zgarmasin.

**Oldini olish kerak bo‘lgan xatolar:** 0.3-bo‘limdagi negative prompt + `no readable text on phone screen, no second customer, no modern glass office`.

**Montajda qo‘shiladiganlar:** barcha chat pufakchalari, qidiruv natijalari maketi, hisoblagich, ADUZ logotipi, seriya belgisi, botning ekran yozuvi (telefon ramkasi ichida).

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > Rustam aka divan sotish uchun reklama bermoqchi edi... 3 kun o‘tdi, kanal hali ham yo‘q 😅
  > Telegramda reklama uchun kanal qidirish sizga ham tanishmi?
  > 👇 Izohda yozing: siz kanalni qanday topasiz?
  >
  > «Reklama degani shumi?!» — 1-qism. Davomi ertaga.
  > Kanallarni bir joyda ko‘rish: @Targetreklammabot
- **Hashtaglar:** #telegramreklama #biznesuz #fargona #reklama #aduz
- **Cover sarlavhasi:** "3 KUN — 0 KANAL"
- **Izoh uchun savol:** "Siz reklama uchun kanalni qanday topasiz: tanish orqali, qidiruv orqali yoki boshqa yo‘l bilan?"
- **Story matni:** "Rustam aka 3 kundan beri kanal qidiryapti 😅 Sizda ham shunaqa bo‘lganmi? [So‘rovnoma: Ha, doim / Ba’zan / Yo‘q]"
- **Auditoriya segmenti:** A — mahalliy biznes egalari.

---

# 2-KUN

**KUN:** 2
**VIDEO RAQAMI:** 02
**SARLAVHA:** "Bir post — uch narx"
**MAQSADLI AUDITORIYA:** biznes egasi
**VIDEO MAQSADI:** ulashish
**DAVOMIYLIGI:** 35 soniya
**FORMAT:** komediya
**SERIAL BILAN BOG‘LANISH:** 1-qismda Rustam aka 3 ta kanal topgan edi, endi narx so‘raydi. Uchinchi admin — Dilnoza. Uning yuzi oxirida birinchi marta ko‘rinadi va bu 3-qismga ko‘prik bo‘ladi.

### A. HOOK (0–3 s)
Ekran uchga bo‘lingan, uchta chat. Rustam aka markazda:
**RUSTAM:** "Bir xil post. Uch xil admin. Uch xil narx!"
Ekranda: **"QAYSI BIRI TO‘G‘RI?!"**

### B. VAZIYAT (3–10 s)
Uchta admin javobi chat ko‘rinishida (ovoz kadr ortidan), har birining yonida **"Shartli misol"** belgisi:
- **1-ADMIN** (tez gapiradi): "300 ming. Bir soat tepada, keyin lentada."
- **2-ADMIN:** "150 ming. 24 soat turadi, lekin faqat bitta rasm."
- **3-ADMIN** (ayol ovozi, yuzi ko‘rinmaydi): "Avval postni yuboring, keyin narxini aytaman."

### C. ASOSIY VOQEA (10–20 s)
Rustam aka kassa stolidan eski cho‘tni (yog‘och hisob-kitob asbobi) oladi va hisoblay boshlaydi:
**RUSTAM:** "Bir soat tepada... yigirma to‘rt soat... bitta rasm... Bu matematikami yo fizika?!"
Keyin bozorcha savdolashadi:
**RUSTAM** (ovozli xabar yozib): "Ukam, 300 mingga ikkita qilib bering, bozor-ku!"
**1-ADMIN** (javob): "Aka, bu bozor emas, kanal."

### D. YECHIM (20–30 s)
Grafika: uchta narx yonma-yon jadvalga tushadi, ustunlar: **narx · turish muddati · format · o‘rtacha ko‘rishlar**.
**OVOZ (diktor):** "Narxni solishtirish uchun bir xil ma’lumot kerak: narx, muddat, format va ko‘rishlar. ADUZ'da kanallar ma’lumotini yonma-yon ko‘rib solishtirish mumkin."
Botning ekran yozuvi (3 s): kanal kartochkasida narx va ma’lumotlar.

### E. YAKUNIY BURILISH (30–33 s)
**RUSTAM** (cho‘tni stolga qo‘yib): "Bu reklama-ku, yo lotereya?!"
Keskin kesish: boshqa xona, stol ustidagi telefon. Chiroyli qo‘l uni oladi, kamera ko‘tariladi va birinchi marta Dilnozaning yuzi ko‘rinadi. U ekranga qarab xo‘rsinadi:
**DILNOZA:** "Postni yubormadi-yu..."

### F. CTA (33–35 s)
Ekranda: **"Narx so‘rab charchagan do‘stingizga yuboring 📩"**
Pastda: *"Ertaga: uchinchi admin kim edi?"*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Ko‘z darajasi, o‘rta plan, markazda | Telefonni kameraga ko‘rsatadi | "Bir xil post. Uch xil admin. Uch xil narx!" | QAYSI BIRI TO‘G‘RI?! | "Dun-dun-dun" ovozi | Uchga bo‘lingan ekran grafika bilan | Har chat ketma-ket yonadi |
| 2 | 3–10 | Telefon insert + Rustamning reaksiyasi | Har javobdan keyin qoshini ko‘taradi | Uch admin replikasi | 300 000 / 150 000 / "?" + Shartli misol | Har javobda "ding" | Har 2,3 s kesish | Whip-pan |
| 3 | 10–15 | Yaqin plan, qo‘llar va cho‘t | Cho‘t donalarini suradi | "Bu matematikami yo fizika?!" | — | Cho‘t donalari tiqillashi | Slow-mo 0,5 s | Cut |
| 4 | 15–20 | O‘rta plan | Telefonni og‘ziga yaqin tutib ovozli xabar yozadi | "Ukam, 300 mingga ikkita qilib bering, bozor-ku!" / "Aka, bu bozor emas, kanal." | Javob pufakchasi | Bozor shovqini (komik effekt, 1 s) | — | Grafikaga zoom |
| 5 | 20–30 | Grafika + bot ekran yozuvi | — | Diktor | Narx · Muddat · Format · Ko‘rishlar | Yengil texno-musiqa | Jadval animatsiyasi | Match cut |
| 6 | 30–31 | Yaqin plan | Cho‘tni qo‘yadi | "Bu reklama-ku, yo lotereya?!" | — | Musiqa to‘xtaydi | — | Keskin kesish |
| 7 | 31–33 | Stol ustidan, kamera qo‘l bilan ko‘tariladi | Dilnoza telefonni olib xo‘rsinadi | "Postni yubormadi-yu..." | — | Tinch, sokin muhit | Yangi ranglar (sovuqroq) | Yuziga push-in |
| 8 | 33–35 | Dilnozaning yaqin plani | Kameraga yon qaraydi | — | CTA | Sirli qisqa tovush | — | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"Bu 2-qism. Asosiy kulgi — Rustam aka reklama narxini bozordagidek savdolashadi. Uchta admin ovozi uchun uch xil xarakter (shoshqaloq, rasmiy, sirli) va uchta qisqa replika variantini yoz. Dilnozaning birinchi chiqishi uchun 2 ta sirli yakun varianti ber."*

**Video promptlar:**

*Klip 1:*
`Vertical 9:16, realistic. Eye-level medium shot of [RUSTAM] in [furniture showroom], holding his smartphone toward the camera with an outraged comic expression, as if presenting evidence. Warm interior light. Static camera, center framing with empty space at top for graphics.`

*Klip 3:*
`Vertical 9:16, realistic close-up of [RUSTAM]'s hands sliding beads on an old wooden abacus on a wooden cashier desk, then tilt up to his confused face counting under his breath. Warm light, shallow depth of field.`

*Klip 4:*
`Vertical 9:16, realistic medium shot of [RUSTAM] holding a smartphone near his mouth recording a voice message, bargaining gestures with his free hand like at a bazaar, confident grin. Warm light.`

*Klip 6–7:*
`Vertical 9:16, realistic. Part 1: close-up of [RUSTAM] putting the abacus down with a dramatic sigh. Part 2: different room [Dilnoza's home office], a smartphone lying on a wooden desk next to a piala of green tea; a woman's hand picks it up, camera tilts up to reveal [DILNOZA] looking at the screen and sighing. Cooler, soft daylight from a window.`

**Kamera va yorug‘lik:** Rustam aka sahnalari issiq. Dilnoza sahnasi sovuqroq, deraza yorug‘ligi (5000–5600K), halqa chiroq fonda o‘chiq turadi.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 Bir xil post. Uch xil admin. Uch xil narx!
00:03 300 ming. Bir soat tepada, keyin lentada.
00:05 150 ming. 24 soat turadi, lekin faqat bitta rasm.
00:07 Avval postni yuboring, keyin narxini aytaman.
00:10 Bu matematikami yo fizika?!
00:15 Ukam, 300 mingga ikkita qilib bering, bozor-ku!
00:18 Aka, bu bozor emas, kanal.
00:20 Narxni solishtirish uchun bir xil ma’lumot kerak.
00:25 ADUZ'da kanallar ma’lumotini yonma-yon solishtirish mumkin.
00:30 Bu reklama-ku, yo lotereya?!
00:32 Postni yubormadi-yu...
```

**Bir xillik uchun:** Dilnoza uchun reference rasm aynan shu klipda yaratiladi va keyingi barcha videolarda ishlatiladi (ko‘zoynak, bej sviter, quloqchin, sochi tugunda).

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `no visible faces of the three admins, no readable numbers on abacus, no market crowd`.

**Montajda qo‘shiladiganlar:** uchga bo‘lingan ekran, narxlar va "Shartli misol" belgilari, solishtirish jadvali, bot ekran yozuvi, logotip.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > Bitta post uchun uchta narx 🤯 Rustam aka hatto cho‘tni ham chiqardi.
  > Narxni to‘g‘ri solishtirish uchun faqat summaga emas, muddat, format va ko‘rishlarga ham qarang.
  > 📩 Narx so‘rab charchagan do‘stingizga yuboring.
  >
  > *Videodagi narxlar — shartli misol.*
  > Kanallarni solishtirish: @Targetreklammabot
- **Hashtaglar:** #telegramreklama #reklamanarxi #biznesuz #aduz
- **Cover sarlavhasi:** "BIR POST — UCH NARX"
- **Izoh uchun savol:** "Siz narxni solishtirganda nimaga ko‘proq qaraysiz?"
- **Story matni:** "Uchinchi admin kim edi? 👀 Ertaga bilasiz. [Savol stikeri: «Sizningcha, u kim?»]"
- **Auditoriya segmenti:** A — biznes egalari, C — SMM mutaxassislar.

---

# 3-KUN

**KUN:** 3
**VIDEO RAQAMI:** 03
**SARLAVHA:** "30 ming obunachi, 0 buyurtma"
**MAQSADLI AUDITORIYA:** kanal egasi
**VIDEO MAQSADI:** izoh
**DAVOMIYLIGI:** 38 soniya
**FORMAT:** mini-hikoya
**SERIAL BILAN BOG‘LANISH:** 2-qism oxirida ko‘ringan Dilnoza endi bosh qahramon. Uning kuni ko‘rsatiladi. Kechasi kelgan xabar — Rustam akadan, bu 4-qismdagi tushunmovchilikka olib boradi.

### A. HOOK (0–3 s)
Stol ustida jim yotgan telefonning yaqin plani. Soat chiqillaydi. Dilnoza kadrga kiradi:
**DILNOZA:** "30 ming obunachi. Bugun ham birorta reklama yo‘q."
Ekranda: **"KANAL EGASINING BIR KUNI"**

### B. VAZIYAT (3–10 s)
Timelapse, burchakda soat ko‘rinadi:
- 09:00 — yangilik posti joylaydi, ko‘rishlar ortib boradi.
- 12:00 — telefonni yangilaydi. Jimlik.
- 15:00 — gulga qarab:
**DILNOZA:** "Sen ham kutyapsanmi?"

### C. ASOSIY VOQEA (10–22 s)
Bildirishnoma keladi, Dilnoza sakrab o‘rnidan turadi. Lekin xabarlar umidni oqlamaydi:
1. *"Kanalingizga 10 000 obunachi! Arzon!"* → **DILNOZA:** "Kerak emas!" (o‘chiradi)
2. *"Balansingiz kam qoldi"* → indamay ko‘zini yumadi.
3. *"Opa, bepul reklama qilib berasizmi? Keyin tanishlarga aytaman"* →
**DILNOZA** (kameraga): "Tanishlarga aytsangiz, ular ham bepul so‘raydi-da."
Eslaydi: **DILNOZA:** "Kecha bir aka narx so‘radi-yu, yo‘qolib qoldi..."

### D. YECHIM (22–31 s)
Grafika. Botning ekran yozuvi (3 s): kanal egasi bo‘limi, kanal qo‘shish sahifasi.
**OVOZ (diktor):** "Kanal egasining savoli: reklama beruvchilar meni qanday topadi? ADUZ'da kanalingizni qo‘shasiz va reklama beruvchilar uni ko‘ra oladi."
Ekranda: **"Kanalingiz — reklama beruvchilar ko‘radigan joyda. ADUZ"**

### E. YAKUNIY BURILISH (31–36 s)
Tun, 23:47. Dilnoza choy ichib turibdi. "Ding". Ekranda: *"Assalomu alaykum, reklama necha pul? — Rustam Mebel"*
**DILNOZA** (ko‘zini qisib): "Bir minut... yana kimdir «narx?» deb yozdi."
Keyin tanib qoladi:
**DILNOZA:** "Yana o‘sha aka!"

### F. CTA (36–38 s)
Ekranda: **"Kanal egasi bo‘lsangiz, reklama buyurtmasini qanday topasiz? Tajribangizni yozing 👇"**
Pastda: *"Ertaga: ular nihoyat kelishadi... yoki yo‘q?"*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Telefonning makro plani, keyin rack focus Dilnozaga | Jim telefon, Dilnoza kadrga kiradi | "30 ming obunachi. Bugun ham birorta reklama yo‘q." | KANAL EGASINING BIR KUNI | Soat chiqillashi | Fokus o‘tishi | Timelapse |
| 2 | 3–10 | Bir nuqtadan statik keng plan | Timelapse: post, yangilash, gul bilan gaplashish | "Sen ham kutyapsanmi?" | 09:00 / 12:00 / 15:00 | Musiqa tezlashadi | Timelapse + soat grafikasi | Ding ovozi bilan kesish |
| 3 | 10–14 | O‘rta plan | Sakrab turadi, xabarni ko‘radi, o‘chiradi | "Kerak emas!" | Spam xabari maketi | Ding, keyin "puf" | Tez kesish | Cut |
| 4 | 14–17 | Yaqin plan | Ko‘zini yumadi | — | Balans xabari | Jim, chuqur nafas | — | Cut |
| 5 | 17–22 | Kameraga qarab, o‘rta plan | Kameraga hazil bilan gapiradi | "Tanishlarga aytsangiz, ular ham bepul so‘raydi-da." / "Kecha bir aka..." | Xabar maketi | Komik "bum" | Pauza 0,5 s | Grafikaga |
| 6 | 22–31 | Grafika + bot ekran yozuvi | — | Diktor | Kanalingiz — reklama beruvchilar ko‘radigan joyda | Yengil texno | Telefon maketi | Qorong‘ilashtirish |
| 7 | 31–36 | Tungi, past kalitli yorug‘lik, yaqin plan | Choy ichadi, ding, o‘qiydi, taniydi | "Bir minut... yana kimdir «narx?» deb yozdi." / "Yana o‘sha aka!" | 23:47 + xabar maketi | Ding | Yuziga zoom | Muzlatish |
| 8 | 36–38 | Kadr muzlagan | — | — | CTA | Musiqa yakuni | — | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"Bu 3-qism, kanal egasi Dilnoza haqida. Kanal egalari bu videoni ko‘rib «aynan men» deyishi kerak. Ular oladigan befoyda xabarlar uchun yana 5 ta kulgili, lekin haqoratsiz variant ber. Kanal egalarini masxara qilma."*

**Video promptlar:**

*Klip 1:*
`Vertical 9:16, realistic. Macro shot of a silent smartphone lying face-up on a wooden desk (screen blank), next to a piala of green tea; rack focus to [DILNOZA] entering the frame and sitting down with a disappointed expression in [Dilnoza's home office]. Soft daylight.`

*Klip 2:*
`Vertical 9:16, realistic timelapse-style sequence, static wide shot of [DILNOZA] at her desk: typing on laptop, refreshing phone repeatedly, then turning and talking to a potted plant. Light changes from morning to afternoon. Locked camera.`

*Klip 3–5:*
`Vertical 9:16, realistic. [DILNOZA] jumps up excited at a notification, reads the phone, her face falls, she deletes it with an annoyed swipe; then a close-up of her closing her eyes patiently; then she looks into the camera with dry ironic humor and speaks. Soft daylight, handheld subtle.`

*Klip 7:*
`Vertical 9:16, realistic night scene. Low-key light from a desk lamp and phone screen glow on [DILNOZA]'s face, she sips tea, phone lights up, she squints, then her eyes widen in recognition. Slow push-in. Cinematic.`

**Kamera va yorug‘lik:** kunduzi deraza yorug‘ligi, tungi sahna issiq stol chirog‘i (2700K) va telefondan tushgan ko‘kish yorug‘lik.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 30 ming obunachi. Bugun ham birorta reklama yo‘q.
00:08 Sen ham kutyapsanmi?
00:11 Kerak emas!
00:17 Tanishlarga aytsangiz, ular ham bepul so‘raydi-da.
00:20 Kecha bir aka narx so‘radi-yu, yo‘qolib qoldi...
00:22 Reklama beruvchilar meni qanday topadi?
00:26 ADUZ'da kanalingizni qo‘shasiz va reklama beruvchilar uni ko‘radi.
00:32 Bir minut... yana kimdir «narx?» deb yozdi.
00:35 Yana o‘sha aka!
```

**Bir xillik uchun:** 2-kunda yaratilgan Dilnoza reference rasmi. Stol, piala va devordagi stikerlar 2-kundagidek joylashsin.

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `no readable notification text, no other people in room, no pets`.

**Montajda qo‘shiladiganlar:** "30 ming obunachi" yozuvi + "Shartli misol", soat grafikasi, xabar maketlari, bot ekran yozuvi.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > Kanal bor, auditoriya bor... reklama buyurtmasi yo‘q 📵
  > Kanal egalari, bu holat sizga tanishmi?
  > 👇 Reklama beruvchilarni qanday topasiz? Tajribangizni yozing.
  >
  > Kanalingizni qo‘shish: @Targetreklammabot
- **Hashtaglar:** #telegramkanal #kanalegasi #telegramreklama #aduz
- **Cover sarlavhasi:** "30 MING OBUNACHI, 0 BUYURTMA"
- **Izoh uchun savol:** "Kanal egalari: reklama beruvchi sizni qanday topadi?"
- **Story matni:** "Kanal egalari, sizga eng ko‘p qanday «befoyda» xabar keladi? 😅 [Savol stikeri]"
- **Auditoriya segmenti:** B — kanal egalari va adminlar.

---
# 4-KUN

**KUN:** 4
**VIDEO RAQAMI:** 04
**SARLAVHA:** "Qaysi ertaga?!"
**MAQSADLI AUDITORIYA:** ikkalasi
**VIDEO MAQSADI:** izoh + saqlash
**DAVOMIYLIGI:** 38 soniya
**FORMAT:** komediya (ekran ikkiga bo‘lingan, yozishma)
**SERIAL BILAN BOG‘LANISH:** 3-qism oxirida Rustam aka Dilnozaga yozgan edi. Endi ular birinchi marta muloqot qiladi va kelishuv shartlarida adashib ketadi. Oxirida kelishiladi, lekin 5-qismda bu hammasi Rustam akaga qanchaga tushgani ko‘rsatiladi.

### A. HOOK (0–3 s)
Ertalab soat 09:00. Rustam aka do‘konda telefonga tikilib turibdi:
**RUSTAM:** "«Ertaga chiqaramiz» dedi. Bugun ertami, yo yo‘q?!"
Ekranda: **"QAYSI ERTAGA?!"**

### B. VAZIYAT (3–10 s)
Ekran ikkiga bo‘linadi: yuqorida Rustam aka, pastda Dilnoza. Kechagi yozishma maketi:
*Rustam:* "Ertaga chiqaring." / *Dilnoza:* "Xo‘p, ertaga."
Har birining tepasida "fikr bulutchasi":
- Rustam aka: **"ertalab 08:00 ☀️"**
- Dilnoza: **"kechqurun 20:00 🌙 (eng ko‘p ko‘rish vaqti)"**

### C. ASOSIY VOQEA (10–22 s)
Telefon qo‘ng‘irog‘i, ikkalasi ekranda:
**RUSTAM:** "Qani reklama?"
**DILNOZA:** "Kechqurun chiqadi."
**RUSTAM:** "Kechqurun do‘kon yopiq-ku!"
**DILNOZA:** "Post matni qani, aka?"
**RUSTAM:** "Beshta rasm, ikkita ovozli xabar yubordim-ku. Matnni o‘zingiz yozib qo‘ying."
**DILNOZA:** "Ovozli xabardan post yozib bo‘lmaydi-da..."
**RUSTAM:** "Post qancha turadi?"
**DILNOZA:** "Bir soat tepada, keyin lentaga tushadi."
**RUSTAM:** "Lentaga?! Qanaqa lenta? Atlasmi?"

### D. YECHIM (22–31 s)
Grafika, saqlab qo‘yishga arziydigan ro‘yxat:
**"Kelishuvda 5 narsa aniq bo‘lsin:**
**1. Sana · 2. Soat · 3. Format (matn/rasm/video) · 4. Tepada turish muddati · 5. To‘lov"**
**OVOZ (diktor):** "Bu shartlar oldindan aniq bo‘lsa, tushunmovchilik bo‘lmaydi. ADUZ'da buyurtma berishda bu shartlar oldindan belgilanadi."
Botning ekran yozuvi (3 s): buyurtma yaratish sahifasi.

### E. YAKUNIY BURILISH (31–36 s)
Ikkalasi telefonda, charchagan:
**DILNOZA:** "Bo‘ldi. Ertaga, soat 20:00."
**RUSTAM:** "Qaysi ertaga?"
**DILNOZA:** "...Aka!!!"
Kadr muzlaydi, ikkalasi telefonga qarab qolgan.

### F. CTA (36–38 s)
Ekranda: **"Sizda ham shunday tushunmovchilik bo‘lganmi? Izohda yozing 👇"**
Pastda: *"Ertaga: bu yozishma Rustam akaga qanchaga tushdi?"*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Ko‘z darajasi, yaqin plan | Telefonga tikiladi | "«Ertaga chiqaramiz» dedi..." | QAYSI ERTAGA?! | Xo‘roz qichqirig‘i (ertalab) | — | Ekran ikkiga ajraladi |
| 2 | 3–10 | Ikkiga bo‘lingan ekran, ikkalasi o‘rta planda | Ikkalasi telefonga qarab tabassum qiladi | — | Chat maketi + fikr bulutchalari | Ding-ding | Bulutchalar "pop" animatsiyasi | Qo‘ng‘iroq ovozi |
| 3 | 10–16 | Ikkiga bo‘lingan ekran, ikkalasi telefonda | Rustam aka do‘konda yuradi, Dilnoza stolda | Qo‘ng‘iroq dialogi, 1-qism | — | Telefon jiringlashi | Har replikada gapirayotgan tomon yorqinroq | Cut |
| 4 | 16–22 | Navbatma-navbat yaqin planlar | Rustam aka "Atlasmi?" deb hayron | Dialog, 2-qism | "LENTA?!" yozuvi | Komik "boing" | Tezroq kesish | Grafikaga |
| 5 | 22–31 | Grafika + bot ekran yozuvi | — | Diktor | 5 ta shart ro‘yxati | Har bandda "tik" | Bandlar ketma-ket chiqadi | Ikkiga bo‘lingan ekranga qaytish |
| 6 | 31–36 | Ikkiga bo‘lingan ekran | Ikkalasi charchagan | "Ertaga, soat 20:00." / "Qaysi ertaga?" / "...Aka!!!" | — | Pauza, keyin "bum" | 1 s pauza | Freeze |
| 7 | 36–38 | Muzlagan kadr | — | — | CTA | Yakun | — | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"4-qism. Kulgi manbai — «ertaga», «lenta», «post qancha turadi» kabi so‘zlarni ikki tomon har xil tushunishi. Shu kabi yana 3 ta so‘z o‘yini ber (masalan «top», «pin», «format»). Dialog tez va jonli bo‘lsin, har replika 6 so‘zdan oshmasin."*

**Video promptlar:**

*Klip 1:*
`Vertical 9:16, realistic. Early morning in [furniture showroom], [RUSTAM] standing near the storefront staring intensely at his smartphone, puzzled and impatient. Cool morning daylight. Static close-up.`

*Klip 3 (Rustam qismi, alohida yaratiladi):*
`Vertical 9:16, realistic medium shot of [RUSTAM] walking between sofas while talking on the phone, gesturing with his free hand, getting frustrated. Warm light. Framed in the upper half of the frame (for split screen).`

*Klip 3 (Dilnoza qismi, alohida yaratiladi):*
`Vertical 9:16, realistic medium shot of [DILNOZA] at her desk talking on the phone with patient, slightly exasperated expression, adjusting her glasses. Soft daylight. Framed for the lower half (for split screen).`

*Klip 6:*
Ikkala qahramon uchun alohida: `... both look exhausted, then [DILNOZA] covers her face with her hand in disbelief / [RUSTAM] looks innocently confused.`

**Kamera va yorug‘lik:** Ikki sahna rang bo‘yicha farqlansin: Rustam aka issiq, Dilnoza sovuqroq. Shunda bo‘lingan ekranda ular darhol ajralib turadi.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 «Ertaga chiqaramiz» dedi. Bugun ertami, yo yo‘q?!
00:10 Qani reklama?
00:11 Kechqurun chiqadi.
00:12 Kechqurun do‘kon yopiq-ku!
00:13 Post matni qani, aka?
00:14 Beshta rasm, ikkita ovozli xabar yubordim-ku.
00:16 Ovozli xabardan post yozib bo‘lmaydi-da...
00:18 Bir soat tepada, keyin lentaga tushadi.
00:20 Lentaga?! Qanaqa lenta? Atlasmi?
00:22 Kelishuvda 5 narsa aniq bo‘lsin.
00:27 ADUZ'da buyurtma shartlari oldindan belgilanadi.
00:31 Bo‘ldi. Ertaga, soat 20:00.
00:33 Qaysi ertaga?
00:34 ...Aka!!!
```

**Bir xillik uchun:** har qahramon o‘z lokatsiyasida, kiyimi oldingi qismlardagidek.

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `characters must not appear in the same room, no phone screen content`.

**Montajda qo‘shiladiganlar:** ikkiga bo‘lingan ekran kompozitsiyasi, chat maketi, fikr bulutchalari, 5 ta shart ro‘yxati, bot ekran yozuvi.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > «Ertaga» — eng xavfli so‘z 😅 Rustam aka ertalabni kutdi, Dilnoza kechqurunni.
  > 📌 Saqlab qo‘ying: reklama kelishuvida 5 narsa aniq bo‘lsin — sana, soat, format, tepada turish muddati va to‘lov.
  > 👇 Sizda ham shunday tushunmovchilik bo‘lganmi?
  >
  > Shartlari aniq buyurtma: @Targetreklammabot
- **Hashtaglar:** #telegramreklama #kanalegasi #biznesuz #aduz #reklamamaslahat
- **Cover sarlavhasi:** "QAYSI ERTAGA?!"
- **Izoh uchun savol:** "Reklama kelishuvida siz eng ko‘p nimada adashgansiz?"
- **Story matni:** "Rustam aka yoki Dilnoza — kim haq? [So‘rovnoma: Rustam aka / Dilnoza / Ikkalasi ham 😅]"
- **Auditoriya segmenti:** A + B.

---

# 5-KUN

**KUN:** 5
**VIDEO RAQAMI:** 05
**SARLAVHA:** "Bugun divan emas, chat sotdim"
**MAQSADLI AUDITORIYA:** biznes egasi
**VIDEO MAQSADI:** ulashish
**DAVOMIYLIGI:** 36 soniya
**FORMAT:** mini-hikoya (montaj)
**SERIAL BILAN BOG‘LANISH:** 4-qismdagi kelishuv Rustam akaning butun kunini olib qo‘ygan ekan. Oxirida Shokir kirib keladi va 6-qism uchun "200 ming obunachi" g‘oyasini olib keladi.

### A. HOOK (0–3 s)
Kechqurun, do‘kon yopilmoqda. Rustam aka jalyuzini tushirayotib kameraga:
**RUSTAM:** "Bugun divan sotmadim. Bugun... yozishdim."
Ekranda: **"REKLAMA UCHUN BIR KUN"**

### B. VAZIYAT (3–12 s)
Kun bo‘yicha tez montaj, burchakda soat:
- **09:00** — do‘konni ochadi, darhol telefon.
- **11:00** — xaridor kiradi. Rustam aka barmog‘ini ko‘taradi: "Bir minut..." Xaridor kutib qoladi.
- **13:00** — oldidagi osh soviyapti, u yozyapti.
- **15:00** — **RUSTAM:** "Qaysi rasmni yuboruvdim? To‘rtinchisimi, beshinchisimi?"

### C. ASOSIY VOQEA (12–22 s)
Hisoblagich tez ortadi:
**"Xabarlar: 47 · Ovozli: 9 · Qo‘ng‘iroqlar: 6 · Chek yuborildi: 2 marta · Sotilgan divan: 0"**
11:00 dagi xaridor oxiri chiqib ketadi. Telefondan xotinining ovozi:
**XOTINI (kadr ortidan):** "Dadasi, kechki ovqat soviydi!"
**RUSTAM:** "Hozir, admin yozyapti!"
**RUSTAM** (Dilnozaga ovozli xabar): "Chekni yubordim, ko‘rdingizmi? ...Yana yuboraymi?"

### D. YECHIM (22–30 s)
Grafika: o‘nlab chat pufakchalari bitta tartibli kartochkaga yig‘iladi.
**OVOZ (diktor):** "Reklama joylash — bitta ish. Qo‘lda qilinsa, o‘nlab kichik ishlarga bo‘linib ketadi. ADUZ'da kanal tanlash, buyurtma berish va kuzatish bir joyda."
Botning ekran yozuvi (3 s).

### E. YAKUNIY BURILISH (30–34 s)
Eshik shiddat bilan ochiladi, Shokir kirib keladi, qo‘lida ikkita telefon:
**SHOKIR:** "Toga! Muammo hal! 200 ming obunachisi bor kanal topdim!"
Rustam akaning ko‘zlari porlaydi (yaltirash effekti).

### F. CTA (34–36 s)
Ekranda: **"Hamma ishni telefonda qiladigan band do‘stingizga yuboring 📩"**
Pastda: *"Ertaga: 200 ming obunachi... lekin..."*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Ko‘chadan, do‘kon oldida, o‘rta plan | Jalyuzini tushiradi, kameraga qaraydi | "Bugun divan sotmadim. Bugun... yozishdim." | REKLAMA UCHUN BIR KUN | Jalyuzi ovozi, kechki ko‘cha | — | Rewind |
| 2 | 3–6 | Ichkaridan, keng plan | Ochadi, telefonga sho‘ng‘iydi | — | 09:00 | Tez musiqa | Soat grafikasi | Jump cut |
| 3 | 6–8 | O‘rta plan | Xaridorga barmoq ko‘rsatadi | "Bir minut..." | 11:00 | — | — | Jump cut |
| 4 | 8–10 | Tepadan, stol | Osh soviyapti, qo‘llar yozmoqda | — | 13:00 | Bug‘ ovozi pasayadi | — | Jump cut |
| 5 | 10–12 | Yaqin plan | Galereyani varaqlaydi | "Qaysi rasmni yuboruvdim?" | 15:00 | — | — | Hisoblagichga |
| 6 | 12–22 | Har xil burchaklardan tez montaj | Yozadi, gapiradi, xaridor ketadi | Xotini va Rustam aka dialogi | Hisoblagich | Hisoblagich "tik-tik", ding | Speed ramp | Grafikaga |
| 7 | 22–30 | Grafika + bot ekran yozuvi | — | Diktor | — | Texno | Pufakchalar bitta kartochkaga yig‘iladi | Eshik ovozi |
| 8 | 30–34 | Eshikdan, keng plan → Rustam akaga yaqin plan | Shokir kirib keladi | "Toga! Muammo hal!..." | — | Eshik "bang", yaltirash | Ko‘zdagi porlash effekti | Muzlatish |
| 9 | 34–36 | Muzlagan kadr | — | — | CTA | — | — | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"5-qism. Bu montaj video: kun bo‘yi telefonda o‘tirgan biznes egasi. Har vaqt bo‘lagi uchun 1 ta qisqa vizual gag ber (har biri 2 soniyagacha). Shokirning birinchi chiqishi uchun 3 ta energiyali replika varianti yoz."*

**Video promptlar:**

*Klip 1:*
`Vertical 9:16, realistic. Evening street in front of a small furniture shop in Fergana, [RUSTAM] pulling down a metal shutter, then turning to the camera with a tired, ironic face. Warm street lights, dusk sky.`

*Klip 3:*
`Vertical 9:16, realistic. Inside [furniture showroom], a middle-aged Uzbek customer waiting politely while [RUSTAM] raises one finger without looking up from his phone. Natural daylight. Static.`

*Klip 4:*
`Vertical 9:16, realistic top-down shot of a plate of Uzbek plov on a wooden cashier desk with steam slowly fading, [RUSTAM]'s hands typing on a smartphone beside it.`

*Klip 8:*
`Vertical 9:16, realistic. [SHOKIR] bursts through the showroom door excitedly holding two smartphones high; cut to close-up of [RUSTAM] whose eyes widen with hope. Comic energy, warm light.`

**Kamera va yorug‘lik:** kun davomida yorug‘lik o‘zgaradi: ertalab sovuq, tushda yorqin, kechqurun issiq. Bu "kun o‘tib ketdi" hissini beradi.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 Bugun divan sotmadim. Bugun... yozishdim.
00:06 Bir minut...
00:10 Qaysi rasmni yuboruvdim? To‘rtinchisimi, beshinchisimi?
00:16 Dadasi, kechki ovqat soviydi!
00:17 Hozir, admin yozyapti!
00:19 Chekni yubordim, ko‘rdingizmi? ...Yana yuboraymi?
00:22 Qo‘lda qilinsa, reklama o‘nlab kichik ishlarga bo‘linib ketadi.
00:26 ADUZ'da kanal tanlash, buyurtma va kuzatish — bir joyda.
00:30 Toga! Muammo hal! 200 ming obunachisi bor kanal topdim!
```

**Bir xillik uchun:** Shokir uchun reference rasm shu yerda yaratiladi (teskari kiyilgan kepka, ikkita telefon, ko‘k sport kostyum).

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `customer must not look angry or aggressive, no food waste emphasis`.

**Montajda qo‘shiladiganlar:** soat grafikasi, hisoblagich, chat pufakchalarining yig‘ilish animatsiyasi, bot ekran yozuvi. Xotinining ovozi faqat audio bo‘ladi, kadrda ko‘rinmaydi.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > 47 ta xabar, 6 ta qo‘ng‘iroq, 0 ta sotilgan divan 🛋️
  > Reklama joylash ba’zan sotishdan ham ko‘p vaqt oladi.
  > 📩 Hamma ishni telefonda qiladigan band do‘stingizga yuboring.
  >
  > Reklama buyurtmasi bir joyda: @Targetreklammabot
- **Hashtaglar:** #tadbirkor #biznesuz #telegramreklama #aduz
- **Cover sarlavhasi:** "DIVAN EMAS, CHAT SOTDIM"
- **Izoh uchun savol:** "Bitta reklamani kelishish uchun sizga qancha vaqt ketadi?"
- **Story matni:** "Shokir 200 ming obunachisi bor kanal topdi 😏 Sizningcha, yaxshi tanlovmi? [So‘rovnoma: Ha / Tekshirish kerak]"
- **Auditoriya segmenti:** A — biznes egalari.

---

# 6-KUN

**KUN:** 6
**VIDEO RAQAMI:** 06
**SARLAVHA:** "200 ming obunachi... va 900 ta ko‘rish"
**MAQSADLI AUDITORIYA:** biznes egasi
**VIDEO MAQSADI:** saqlash + izoh
**DAVOMIYLIGI:** 38 soniya
**FORMAT:** komediya + foydali maslahat
**SERIAL BILAN BOG‘LANISH:** 5-qism oxiridagi Shokirning "kashfiyoti" tekshiriladi. Natijada Rustam aka ikki kanalga pul to‘lab qo‘yadi, 7-qismda esa natijani o‘lchay olmaydi.

### A. HOOK (0–3 s)
Shokir telefonni Rustam akaning yuziga tutadi:
**SHOKIR:** "200 ming obunachi, toga! 200 ming!"
**RUSTAM:** "Voy-bo‘!"
Ekranda: **"200 000 OBUNACHI 🔥"** (*shartli misol*)

### B. VAZIYAT (3–10 s)
Ikkalasi quvonadi. Shokir o‘zini ekspertdek tutadi:
**SHOKIR:** "Obunachisi ko‘p bo‘lsa, bo‘ldi-da! Hamma ko‘radi!"
Rustam akaning xayoli: do‘kon oldida uzun navbat, hamma qo‘lida divan (fantaziya kadri, oltin rangli filtr).

### C. ASOSIY VOQEA (10–20 s)
Rustam aka kanalni o‘zi varaqlaydi. Postlar ostidagi "ko‘z" belgisiga yaqin plan: **900 · 1,1 ming · 850**.
**RUSTAM:** "Shokir... bu ko‘zcha nima?"
**SHOKIR:** "Bu... dizayn, toga."
Rustam aka Dilnozaning kanalini ochadi: **30 ming obunachi, postlarda 6–8 ming ko‘rish** (*shartli misol*).
**RUSTAM:** "O‘ttiz mingda yetti ming ko‘radi. Ikki yuz mingda to‘qqiz yuz?!"

### D. YECHIM (20–30 s)
Grafika, saqlab qo‘yishga arziydigan maslahat:
**"Kanal tanlashda obunachiga emas, quyidagilarga qarang:**
**✔ oxirgi 10 ta postdagi o‘rtacha ko‘rishlar**
**✔ auditoriya sizning hududingiz va mavzuingizga mosmi"**
**OVOZ (diktor):** "Obunachi soni hali hammasi emas. Ko‘rishlar va auditoriya mosligi muhimroq. ADUZ'da kanal ma’lumotlarini yonma-yon solishtirishingiz mumkin."
Botning ekran yozuvi (3 s): kanal kartochkasi.
*(Hech qanday haqiqiy kanal ko‘rsatilmaydi va "soxta" deb atalmaydi — faqat ko‘rishlar kamligi aytiladi.)*

### E. YAKUNIY BURILISH (30–35 s)
**RUSTAM:** "Yaxshiyamki, hali pul to‘lamadik."
**SHOKIR** (telefonga qarab, sekin): "Toga... men allaqachon to‘lab qo‘ydim."
Pauza. Rustam aka kameraga qaraydi:
**RUSTAM:** "Bu reklama-ku, yo lotereya?!"

### F. CTA (35–38 s)
Ekranda: **"Siz nimaga qaraysiz: obunachigami yoki ko‘rishgami? Izohda yozing 👇"**
Pastda: *"Ertaga: reklama chiqdi... natija qani?"*

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | Yaqin plan, telefon kameraga tomon | Shokir telefonni tutadi | "200 ming obunachi, toga!" / "Voy-bo‘!" | 200 000 OBUNACHI 🔥 + Shartli misol | Fanfara | Tez zoom | Cut |
| 2 | 3–6 | Ikki kishilik o‘rta plan | High-five qilishadi | "Obunachisi ko‘p bo‘lsa, bo‘ldi-da!" | — | Ko‘tarinki musiqa | — | Xayol "to‘lqini" |
| 3 | 6–10 | Keng plan, fantaziya | Do‘kon oldida navbat | — | — | Olomon shovqini | Oltin filtr, sekinlashtirish | To‘lqin bilan qaytish |
| 4 | 10–14 | Telefon insert, makro | Barmoq postlarni varaqlaydi | "Shokir... bu ko‘zcha nima?" / "Bu... dizayn, toga." | 👁 900 · 1,1K · 850 | Musiqa to‘satdan to‘xtaydi | Ko‘zcha belgisiga zoom | Cut |
| 5 | 14–20 | Rustam akaning yaqin plani + taqqoslash grafikasi | Ikki kanalni solishtiradi | "O‘ttiz mingda yetti ming..." | 200K → 900 / 30K → 7K (shartli) | "Hmm" ovozi | Ekran ikkiga bo‘linib taqqoslaydi | Grafikaga |
| 6 | 20–30 | Grafika + bot ekran yozuvi | — | Diktor | Maslahat ro‘yxati | Har bandda "tik" | — | O‘rta planga qaytish |
| 7 | 30–35 | Ikki kishilik plan → Rustam akaning yaqin plani | Shokir aybdor qiyofada | "Men allaqachon to‘lab qo‘ydim." / "Bu reklama-ku, yo lotereya?!" | — | Sverchok ovozi (jimlik), keyin "bum" | 1 s pauza | Muzlatish |
| 8 | 35–38 | Muzlagan kadr | — | — | CTA | — | — | Qoraga |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"6-qism. Ta’limiy fikr: obunachi soni emas, ko‘rishlar va auditoriya mosligi muhim. Buni kulgili, lekin haqiqiy kanallarni ayblamasdan ko‘rsat. «Soxta», «nakrutka» so‘zlarini ishlatma. Shokir uchun yana 3 ta «noto‘g‘ri ekspert» replikasi ber."*

**Video promptlar:**

*Klip 1–2:*
`Vertical 9:16, realistic. [SHOKIR] excitedly holds a smartphone right up to [RUSTAM]'s face in [furniture showroom]; [RUSTAM] gasps with joy; they high-five. Warm light, handheld energy.`

*Klip 3 (fantaziya):*
`Vertical 9:16, dreamy golden-filtered shot: a long happy queue of Uzbek customers outside a small furniture shop, people carrying sofa cushions, slow motion, soft glow. Comic daydream feel.`

*Klip 5:*
`Vertical 9:16, realistic close-up of [RUSTAM] scrolling his phone, his excited smile slowly turning into suspicion, one eyebrow raising. Warm light, slow push-in.`

*Klip 7:*
`Vertical 9:16, realistic two-shot: [SHOKIR] looks down guiltily at his phone and speaks quietly; [RUSTAM] slowly turns his head toward him, then looks directly at the camera with comic despair.`

**Kamera va yorug‘lik:** quvonch qismi issiq va yorqin, "ko‘zcha" qismidan boshlab biroz sovuqroq rang. Bu kayfiyat o‘zgarganini sezdiradi.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 200 ming obunachi, toga! 200 ming!
00:02 Voy-bo‘!
00:03 Obunachisi ko‘p bo‘lsa, bo‘ldi-da! Hamma ko‘radi!
00:10 Shokir... bu ko‘zcha nima?
00:12 Bu... dizayn, toga.
00:15 O‘ttiz mingda yetti ming ko‘radi. Ikki yuz mingda to‘qqiz yuz?!
00:20 Obunachi soni hali hammasi emas.
00:23 Ko‘rishlar va auditoriya mosligi muhimroq.
00:30 Yaxshiyamki, hali pul to‘lamadik.
00:32 Toga... men allaqachon to‘lab qo‘ydim.
00:34 Bu reklama-ku, yo lotereya?!
```

**Bir xillik uchun:** Shokir va Rustam akaning reference rasmlari. Do‘kon interyeri 1–5-qismlardagidek.

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `no real Telegram channel names or avatars, no readable view counts (added in post)`.

**Montajda qo‘shiladiganlar:** barcha raqamlar va "Shartli misol" belgilari, "ko‘zcha" belgisi, taqqoslash grafikasi, maslahat ro‘yxati, bot ekran yozuvi.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > 200 ming obunachi — zo‘r eshitiladi. Lekin postni nechta odam ko‘ryapti? 👀
  > 📌 Saqlab qo‘ying: kanal tanlashda oxirgi postlardagi o‘rtacha ko‘rishlarga va auditoriya mosligiga qarang.
  > 👇 Siz nimaga qaraysiz?
  >
  > *Videodagi raqamlar — shartli misol.*
  > Kanallarni solishtirish: @Targetreklammabot
- **Hashtaglar:** #telegramreklama #reklamamaslahat #biznesuz #aduz #marketinguz
- **Cover sarlavhasi:** "200 MING OBUNACHI, 900 KO‘RISH"
- **Izoh uchun savol:** "Reklama berishdan oldin kanalning ko‘rishlarini tekshirasizmi?"
- **Story matni:** "Obunachi yoki ko‘rish — nimaga qaraysiz? [So‘rovnoma: Obunachi / Ko‘rish] + ertaga javobini ulashamiz"
- **Auditoriya segmenti:** A — biznes egalari, C — SMM mutaxassislar.

---

# 7-KUN

**KUN:** 7
**VIDEO RAQAMI:** 07
**SARLAVHA:** "Mijoz qaysi kanaldan keldi?"
**MAQSADLI AUDITORIYA:** biznes egasi
**VIDEO MAQSADI:** ko‘rish + keyingi qismni kutish
**DAVOMIYLIGI:** 40 soniya
**FORMAT:** mini-hikoya + cliffhanger
**SERIAL BILAN BOG‘LANISH:** 1-hafta finali. Ikki kanalda reklama chiqdi (Dilnozaniki va 200 minglik), lekin Rustam aka qaysi biri ishlaganini bilmaydi. Oxirida ADUZ asoschisi birinchi marta paydo bo‘ladi va 2-hafta boshlanadi.

### A. HOOK (0–3 s)
Rustam aka ikki telefonda ikkita reklama postiga qarab turibdi:
**RUSTAM:** "Reklama chiqdi. Pul ketdi. Endi... mijoz qaysi kanaldan keldi?"
Ekranda: **"1-HAFTA FINALI"**

### B. VAZIYAT (3–12 s)
Do‘konga mijozlar kira boshlaydi (bu yaxshi!). Rustam aka qo‘lida bloknot, detektivdek har biridan so‘raydi:
**RUSTAM:** "Bizni qayerdan topdingiz?"
- **1-MIJOZ:** "Instagramdan." → Rustam aka: "Bizda Instagram yo‘q-ku?!"
- **2-MIJOZ:** "Qo‘shnim aytdi."
- **3-MIJOZ:** "Shunchaki o‘tib ketayotgan edim."

### C. ASOSIY VOQEA (12–22 s)
Shokir oq doskaga strelkalar chizadi, chalkashib ketadi:
**SHOKIR:** "Demak, qo‘shni kanalni ko‘rgan, keyin Instagramga kirgan..."
**RUSTAM:** "Qaysi biri ishladi? Keyingi safar qayerga pul beraman?"
Hisoblagich: **"Sarflangan: ✔ · Kelgan mijozlar: 3 · Qaysi kanaldan: ???"**

### D. YECHIM (22–31 s)
Grafika, foydali maslahat:
**"Har bir kanal uchun alohida promo-kod yoki havola bering.**
**Masalan: «FARGONA10» — faqat 1-kanalda, «DIVAN10» — faqat 2-kanalda."**
**OVOZ (diktor):** "Shunda qaysi kanal ishlaganini aniq bilasiz. ADUZ'da esa buyurtmalar va reklama natijalari bir joyda kuzatiladi."
Botning ekran yozuvi (3 s): buyurtmalar va natijalar bo‘limi.

### E. YAKUNIY BURILISH (31–37 s)
Rustam aka divanga cho‘kadi, shiftga qarab:
**RUSTAM:** "Kimdir buning osonroq yo‘lini o‘ylab topsa edi..."
Divan ortidan xotirjam ovoz eshitiladi:
**ASOSCHI:** "Shoshmang, osonroq yo‘li bor."
Asoschi divan ortidan turib, qo‘lida telefon bilan tabassum qiladi. Rustam aka sakrab turadi:
**RUSTAM:** "Siz kimsiz?!"
Ekranda: **"Muxriddin Obidov — ADUZ asoschisi"**

### F. CTA (37–40 s)
Qora ekran: **"DAVOMI BOR..."**
**"Keyingi qismni o‘tkazib yubormaslik uchun sahifani kuzating 🔔"**

### G. KADRMA-KADR PLAN

| # | Vaqt | Kamera rakursi | Harakat | Dialog | Ekrandagi matn | Ovoz / SFX | Montaj | O‘tish |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–3 | O‘rta plan, ikki qo‘lda ikki telefon | Ikkala ekranga navbat bilan qaraydi | "Reklama chiqdi. Pul ketdi..." | 1-HAFTA FINALI | Seriya musiqasi | — | Eshik qo‘ng‘irog‘i |
| 2 | 3–12 | Kassa stoli ortidan, har mijozga kesish | Bloknot bilan so‘roq qiladi | 3 ta mijoz dialogi | Har javob yonida "?" | Detektiv musiqa, ruchka ovozi | Har mijoz 2,5 s | Cut |
| 3 | 12–17 | Doska oldida o‘rta plan | Shokir strelkalar chizadi | "Demak, qo‘shni kanalni ko‘rgan..." | — | Marker ovozi | Doskaga zoom | Cut |
| 4 | 17–22 | Rustam akaning yaqin plani | Boshini changallaydi | "Qaysi biri ishladi?..." | Hisoblagich | "Tik-tik" | — | Grafikaga |
| 5 | 22–31 | Grafika + bot ekran yozuvi | — | Diktor | Promo-kod misoli | Texno | Kodlar animatsiyasi | Do‘konga qaytish |
| 6 | 31–34 | Tepadan, keng plan | Divanga cho‘kadi | "Kimdir buning osonroq yo‘lini..." | — | Musiqa pasayadi | Jim 1 s | Cut |
| 7 | 34–37 | Ko‘z darajasi, divan orqasi ko‘rinadi | Asoschi divan ortidan turadi, Rustam aka sakraydi | "Shoshmang, osonroq yo‘li bor." / "Siz kimsiz?!" | Muxriddin Obidov — ADUZ asoschisi | "Whoosh", ko‘tarinki akkord | Asoschining yuziga sekin push-in | Muzlatish |
| 8 | 37–40 | Qora ekran | — | — | DAVOMI BOR... + CTA | Seriya musiqasi yakuni | — | — |

### H. AI VIDEO PRODUCTION

**Gemini Pro vazifasi:**
> *"7-qism — 1-hafta finali. Ikkita vazifa: (1) «Bizni qayerdan topdingiz?» savoliga 5 ta kulgili, lekin real mijoz javobi ber. (2) ADUZ asoschisining birinchi chiqishi uchun 3 ta variant ber: u xotirjam, ishonchli va kutilmagan bo‘lsin, lekin masxaraboz emas. U haqiqiy odam — uni kulgili qilib ko‘rsatma, kulgi Rustam akaning reaksiyasidan chiqsin."*

**Video promptlar:**

*Klip 1:*
`Vertical 9:16, realistic medium shot of [RUSTAM] in [furniture showroom] holding two smartphones, one in each hand, looking back and forth between them with confusion. Warm light. Static.`

*Klip 2:*
`Vertical 9:16, realistic. [RUSTAM] behind the wooden cashier desk with a small notepad and pen, questioning a series of different Uzbek customers (a young woman, an elderly man in a doppi skullcap, a young man) like a comic detective. Each customer shrugs or answers casually. Warm daylight.`

*Klip 3:*
`Vertical 9:16, realistic. [SHOKIR] drawing chaotic arrows on a small whiteboard in the showroom, getting confused and scratching his head under his backwards cap. Whiteboard drawings blurred, no readable text.`

*Klip 6:*
`Vertical 9:16, realistic top-down wide shot: [RUSTAM] collapses onto a grey sofa and stares at the ceiling, sighing. Warm, quiet evening light.`

*Klip 7 (ASOSCHI):*
**1-variant — tavsiya etiladi (gibrid):** asoschini haqiqiy hayotda divan ortida (yoki yashil fonda) suratga oling: u sekin qaddini rostlaydi, telefonini ushlagan, kameraga xotirjam tabassum qiladi. Rustam akaning reaksiyasi alohida AI klip bo‘ladi:
`Vertical 9:16, realistic. [RUSTAM] sitting on a grey sofa jumps up startled and turns around toward the back of the sofa, comic shocked face, pointing. Warm evening light.`
**2-variant (to‘liq AI, foto-reference bilan):**
`Vertical 9:16, realistic. Using the provided reference photo for exact face identity: [ASOSCHI character sheet] slowly rises from behind a grey sofa in [furniture showroom], holding a smartphone, calm confident half-smile, looking at the camera. Warm evening light, slow push-in, shallow depth of field.`

**Kamera va yorug‘lik:** finalda yorug‘lik iliq va biroz dramatik (kechki). Asoschi chiqqan paytda orqa fonda yumshoq kontur yorug‘lik bo‘lsin — "yechim keldi" effekti.

**O‘zbekcha dialog va subtitrlar:**
```
00:00 Reklama chiqdi. Pul ketdi.
00:01 Endi... mijoz qaysi kanaldan keldi?
00:03 Bizni qayerdan topdingiz?
00:05 Instagramdan.
00:06 Bizda Instagram yo‘q-ku?!
00:08 Qo‘shnim aytdi.
00:10 Shunchaki o‘tib ketayotgan edim.
00:12 Demak, qo‘shni kanalni ko‘rgan, keyin Instagramga kirgan...
00:17 Qaysi biri ishladi? Keyingi safar qayerga pul beraman?
00:22 Har kanal uchun alohida promo-kod yoki havola bering.
00:27 ADUZ'da buyurtmalar va natijalar bir joyda kuzatiladi.
00:31 Kimdir buning osonroq yo‘lini o‘ylab topsa edi...
00:34 Shoshmang, osonroq yo‘li bor.
00:36 Siz kimsiz?!
```

**Bir xillik uchun:** asoschi har doim oq ko‘ylakda va o‘sha ko‘zoynakda. Bu uning serialdagi "imzo" obrazi. Rustam aka va Shokir oldingi qismlardagidek.

**Oldini olish kerak bo‘lgan xatolar:** negative prompt + `do not alter the founder's facial features, no different glasses, no beard, no hoodie on the founder, no comic exaggeration of the founder`.

**Montajda qo‘shiladiganlar:** hisoblagich, promo-kod grafikasi, bot ekran yozuvi, asoschining ism-familiyasi yozuvi, "DAVOMI BOR" ekrani. Instagramda **"AI info"** belgisini yoqing.

### I. INSTAGRAM PUBLISHING PACKAGE
- **Caption:**
  > Reklama chiqdi, mijozlar keldi... lekin qaysi kanaldan? 🕵️‍♂️
  > 📌 Maslahat: har kanal uchun alohida promo-kod yoki havola bering — shunda qaysi biri ishlaganini bilasiz.
  > Divan ortidagi odam kim? 👀 Davomi keyingi qismda.
  > 🔔 Sahifani kuzating.
  >
  > ADUZ: @Targetreklammabot
- **Hashtaglar:** #telegramreklama #biznesuz #reklamamaslahat #aduz
- **Cover sarlavhasi:** "MIJOZ QAYERDAN KELDI?"
- **Izoh uchun savol:** "Siz reklama natijasini qanday aniqlaysiz?"
- **Story matni:** "Divan ortidan kim chiqdi? 👀 Ertaga tanishasiz. [Hisoblagich stikeri: «2-hafta boshlanishi»]"
- **Auditoriya segmenti:** A — biznes egalari, C — SMM mutaxassislar.

---

# 1-HAFTA UCHUN TEZKOR ISHLAB CHIQARISH RO‘YXATI

| Kun | Qahramonlar | Lokatsiya | AI klip soni | Montaj elementlari | Asoschi |
|---|---|---|---|---|---|
| 1 | Rustam, xaridor | Do‘kon | 5–6 | Chat, hisoblagich, bot yozuvi | — |
| 2 | Rustam, Dilnoza (oxirida) | Do‘kon, Dilnozaning xonasi | 5 | Uchga bo‘lingan ekran, jadval | — |
| 3 | Dilnoza | Dilnozaning xonasi | 5 | Soat, xabarlar | — |
| 4 | Rustam, Dilnoza | Ikkalasi (bo‘lingan ekran) | 6 | Chat, 5 ta shart | — |
| 5 | Rustam, xaridor, Shokir | Do‘kon, ko‘cha | 6–7 | Soat, hisoblagich | — |
| 6 | Rustam, Shokir | Do‘kon | 5–6 | Raqamlar, taqqoslash | — |
| 7 | Rustam, Shokir, mijozlar, **Asoschi** | Do‘kon | 6–7 | Promo-kod, ism yozuvi | ✅ jonli yoki gibrid |

**Asoschi bilan suratga olish kuni:** 7-kun kadrini 2-hafta kadrlari bilan bir kunda oling (bir xil kiyim va yorug‘lik — bir xillik avtomatik saqlanadi).

**Bot ekran yozuvlari:** 1–7-kunlar uchun 6 ta qisqa (3 soniyalik) ekran yozuvi kerak: kanallar ro‘yxati, kanal kartochkasi, kanal qo‘shish, buyurtma yaratish, buyurtmalar/natijalar. Hammasini bir sessiyada, 1080×1920 da yozib oling.
