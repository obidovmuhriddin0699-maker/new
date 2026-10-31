# ADUZ 9-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 9 --cuesheet SOUND_ARCHITECTURE_9.md`).

## Qatlamlar

| Qatlam | Nomi | Vazifasi |
|---|---|---|
| L1 | Musiqa (score) | Pad, klavishlar, bas, baraban, melodiya. Kick'dan sidechain; 2,2–4,2 kHz diktor uchun bo'shatilgan. |
| L2 | Muhit (ambience) | Sahna 'xonasi': ofis shovqini, havo. Juda past, sezilmas — lekin sukunatni 'jonli' qiladi. |
| L3 | UI / foley | Bosish, tanlash, slider, popup, xato. Musiqa tonalligiga sozlangan. |
| L4 | O'tishlar | Whoosh, swell, riser, squeegee, whip. J-cut: tovush kesimdan oldin boshlanadi. |
| L5 | Zarbalar / urg'u | Boom, crash, glitch, uchqunlar. Kinetik so'zlar bilan bir kadrda. |
| L6 | Brend (sonic logo) | ADUZ ovozli logotipi: 5–1–3 motiv (qo'ng'iroq + elektro-pianino + sub). |
| L7 | Diktor joyi | Hozircha bo'sh. Diktor qo'shilsa: musiqa −6 dB ducking, SFX −3 dB. |

## Tovushlar kutubxonasi

| Nomi | Qatlam | Tavsif |
|---|---|---|
| `amb.office` | L2 | Ofis fon shovqini: past 'xona tovushi', ventilyatsiya, 50 Hz g'uvullash |
| `amb.air` | L2 | Yorug', ochiq havo — yechim sahnasi muhiti |
| `ui.popup` | L3 | Yumshoq 'pop' — popup paydo bo'lishi (balandligi sozlanadi) |
| `ui.dropdown` | L3 | Ochiluvchi ro'yxat 'shitirlashi' (5 ta tez tik) |
| `ui.error` | L3 | Xato: pastga tushuvchi ikki nota + glitch |
| `ui.tap` | L3 | Barmoq bosishi |
| `ui.select` | L3 | Tanlash: klik + tonallikdagi qo'ng'iroqcha |
| `ui.slider` | L3 | Slider qadami: ko'tariluvchi mayda tik |
| `ui.next` | L3 | 'Keyingi': ikki nota yuqoriga |
| `ui.launch` | L3 | Ishga tushirish: ko'tariluvchi ton + shovqin |
| `ui.success` | L3 | Muvaffaqiyat: D-major arpedjio akkordi |
| `fx.fragment` | L3 | Suzuvchi jargon bo'lagi: bit-crush 'blip' |
| `fx.strike` | L3 | Matn ustidan chizish: tushuvchi 'chirt' |
| `fx.collapse` | L5 | Ilova yopilishi: pastga 'so'rilish' + zarba |
| `fx.heartbeat` | L5 | Yurak urishi — ovoz vakuumi ichida |
| `tr.whoosh` | L4 | Yumshoq whoosh: telefon/ekran kirishi |
| `tr.slide` | L4 | Ekranlar orasida sirpanish |
| `tr.swell` | L4 | Teskari swell (J-cut): keyingi kadrga 'nafas' |
| `tr.riser` | L4 | Riser — keskin kesiladi (montaj usuli) |
| `tr.squeegee` | L4 | Squeegee o'tishi: yuqori chastotali 'shirr' + rezina g'ichirlashi |
| `tr.whip` | L4 | Whip-pan: chapdan o'ngga tez o'tuvchi whoosh |
| `imp.glitch` | L5 | Qizil kinetik so'z zarbasi |
| `imp.boom` | L5 | Katta zarba: sub + thump |
| `imp.clap` | L5 | Zarba ustidagi clap qatlami |
| `imp.crash` | L5 | Crash tarelka (yumshatilgan) |
| `imp.sparkle` | L5 | Uchqunlar: D-pentatonik qo'ng'iroqchalar to'dasi |
| `brand.logo` | L6 | ADUZ sonic logo (5–1–3 motiv) |
| `fx.window` | L3 | Oyna ochilishi: yumshoq 'bloop' (balandligi sozlanadi) |
| `fx.paper` | L3 | Qog'oz shitirlashi (daftar, chek) |
| `fx.sticky` | L3 | Stiker 'shap' etib yopishishi |
| `fx.tab` | L3 | Brauzer tabi ochilishi |
| `fx.magnet` | L4 | Magnit maydoni: ko'tariluvchi tremolo g'uvullash |
| `fx.absorb` | L5 | Bo'lak magnitga 'yutilishi': pastga tushuvchi ton + thump |
| `fx.snap` | L3 | Karta joyiga 'chiq' etib tushishi |
| `ui.cart` | L3 | Savatchaga qo'shish: pop + qo'ng'iroqcha |
| `ui.pay` | L3 | To'lov: klik + muvaffaqiyat akkordi |
| `fx.pulse` | L3 | Hub impulsi: ma'lumot oqimi |
| `tr.implode` | L4 | Implosion: hamma narsa markazga so'riladi |
| `tr.flip` | L4 | Karta aylanishi: ikki marta 'fvip' |
| `fx.knob` | L3 | Murvat aylantirish: zinali 'chiq-chiq' (ratchet) |
| `fx.detent` | L3 | Bitta murvat qadami — pult elementi paydo bo'lishi |
| `fx.switch` | L3 | Tumbler: metall 'chiq' + past thunk |
| `fx.slider` | L3 | Slayder ishqalanishi |
| `fx.lcd` | L3 | LCD yonishi: qisqa beep + elektr g'uvullash |
| `fx.alarm` | L5 | Ogohlantirish signali (C-minor tonallikda) |
| `fx.relay` | L1 | Rele chiqillashi — muammo sahnasining 'hi-hat'i |
| `tr.crt_off` | L4 | Eski televizor o'chishi: chiyillash + thoomp + chirsillash |
| `tr.boot` | L4 | ADUZ yonishi: Eb-major arpedjio |
| `fx.token` | L3 | AI so'zni ajratdi: shisha shimmer (balandligi sozlanadi) |
| `fx.think` | L3 | AI 'o'ylayapti': mayda qo'ng'iroqcha uchqunlari |
| `fx.type` | L3 | Yumshoq klaviatura bosishi |
| `tr.glitch` | L4 | Digital glitch o'tishi: bit-stutter |
| `fx.nope` | L3 | 'Oldin' qatori: past ikki nota (rad) |
| `fx.crumple` | L5 | Qoralama g'ijimlanadi: qog'oz chirsillashi |
| `fx.thud` | L5 | Qog'oz to'p yerga tushadi |
| `fx.fill` | L3 | Avtomatik to'ldirish 'domino'si: har sozlama o'z notasida |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · G-minor, tashvishli minimal | 7-qism aranjirovkasi 3 yarim ton yuqorida: qorong'i pad, offbeat bo'g'iq Rhodes, filtrlangan bas pulsi, yumshoq hat, 5.5 s dan kick. 9.5 s da hammasi keskin to'xtaydi. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: musiqa va dumlar −30 dB. Faqat qoralama g'ijimlanishi va qog'oz to'pning tushishi eshitiladi. Keyin J-cut swell F-major'da. |
| 0:11–0:21.75 | Yechim · F-major, siyrak | Half-time kick + snap, iliq Rhodes, sub, qo'ng'iroqcha. Ustida 20 notali 'domino' — avtomatik to'ldirish F-pentatonik bo'yicha 4 oktavaga ko'tariladi. |
| 0:22–0:27 | Natija · F-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (F tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.40 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #1 |
| 0:00.85 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #2 |
| 0:01.00 | L4 | `tr.slide` | -22 dB | C | 10% | Ro'yxat pastga suriladi |
| 0:01.30 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #3 |
| 0:01.75 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #4 |
| 0:02.00 | L3 | `ui.tap` | -10 dB | R20 | 0% | Narx strategiyasi bosildi |
| 0:02.05 | L3 | `ui.dropdown` | -14 dB | R20 | 10% | Jargonli ro'yxat ochiladi |
| 0:02.20 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #5 |
| 0:02.65 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #6 |
| 0:03.00 | L3 | `ui.tap` | -14 dB | R20 | 0% | Yopildi — tanlanmadi |
| 0:03.10 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #7 |
| 0:03.20 | L4 | `tr.slide` | -22 dB | C | 10% | Yana pastga |
| 0:03.55 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #8 |
| 0:04.00 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #9 |
| 0:04.45 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #10 |
| 0:04.90 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #11 |
| 0:05.00 | L3 | `ui.error` | -12 dB | C | 20% | 12 ta majburiy maydon to'ldirilmagan |
| 0:05.35 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #12 |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: MAJBURIY * |
| 0:05.80 | L4 | `tr.slide` | -22 dB | C | 10% | Yana pastga |
| 0:05.80 | L3 | `fx.detent` | -22 dB | R70 | 20% | Tishli g'ildirak #13 |
| 0:06.25 | L3 | `fx.detent` | -22 dB | L70 | 20% | Tishli g'ildirak #14 |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: QAYSI STRATEGIYA? |
| 0:07.60 | L3 | `ui.tap` | -10 dB | R40 | 0% | Saqlash bosildi |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: YANA XATO! |
| 0:07.80 | L3 | `ui.error` | -12 dB | C | 25% | Saqlanmadi |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | 20 TA SOZLAMA — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.55 | L5 | `fx.crumple` | -12 dB | C | 0% | OVOZ VAKUUMI: qoralama g'ijimlanadi |
| 0:09.95 | L5 | `fx.thud` | -8 dB | R15 | 0% | Qog'oz to'p tushadi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi kesimdan oldin |
| 0:10.55 | L4 | `tr.squeegee` | -7 dB | C | 25% | Squeegee o'tishi |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.60 | L3 | `ui.select` | -18 dB | L30 | 25% | Maqsad kartasi #1 |
| 0:11.75 | L3 | `ui.select` | -18 dB | C | 25% | Maqsad kartasi #2 |
| 0:11.90 | L3 | `ui.select` | -18 dB | R30 | 25% | Maqsad kartasi #3 |
| 0:13.00 | L3 | `ui.select` | -12 dB | R20 | 20% | Tanlandi: Do'konga mijoz |
| 0:13.20 | L4 | `tr.slide` | -17 dB | R50 | 10% | Aqlli sozlash ekrani |
| 0:13.55 | L3 | `fx.fill` | -15 dB | L50 | 25% | Avto-to'ldirish 1/20 — domino |
| 0:13.66 | L3 | `fx.fill` | -15 dB | L45 | 25% | Avto-to'ldirish 2/20 — domino |
| 0:13.76 | L3 | `fx.fill` | -15 dB | L40 | 25% | Avto-to'ldirish 3/20 — domino |
| 0:13.87 | L3 | `fx.fill` | -15 dB | L35 | 25% | Avto-to'ldirish 4/20 — domino |
| 0:13.97 | L3 | `fx.fill` | -15 dB | L30 | 25% | Avto-to'ldirish 5/20 — domino |
| 0:14.08 | L3 | `fx.fill` | -15 dB | L25 | 25% | Avto-to'ldirish 6/20 — domino |
| 0:14.18 | L3 | `fx.fill` | -15 dB | L20 | 25% | Avto-to'ldirish 7/20 — domino |
| 0:14.29 | L3 | `fx.fill` | -15 dB | L15 | 25% | Avto-to'ldirish 8/20 — domino |
| 0:14.39 | L3 | `fx.fill` | -15 dB | L10 | 25% | Avto-to'ldirish 9/20 — domino |
| 0:14.50 | L3 | `fx.fill` | -15 dB | C | 25% | Avto-to'ldirish 10/20 — domino |
| 0:14.60 | L3 | `fx.fill` | -15 dB | C | 25% | Avto-to'ldirish 11/20 — domino |
| 0:14.71 | L3 | `fx.fill` | -15 dB | R5 | 25% | Avto-to'ldirish 12/20 — domino |
| 0:14.81 | L3 | `fx.fill` | -15 dB | R10 | 25% | Avto-to'ldirish 13/20 — domino |
| 0:14.92 | L3 | `fx.fill` | -15 dB | R15 | 25% | Avto-to'ldirish 14/20 — domino |
| 0:15.02 | L3 | `fx.fill` | -15 dB | R20 | 25% | Avto-to'ldirish 15/20 — domino |
| 0:15.12 | L3 | `fx.fill` | -15 dB | R25 | 25% | Avto-to'ldirish 16/20 — domino |
| 0:15.23 | L3 | `fx.fill` | -15 dB | R30 | 25% | Avto-to'ldirish 17/20 — domino |
| 0:15.34 | L3 | `fx.fill` | -15 dB | R35 | 25% | Avto-to'ldirish 18/20 — domino |
| 0:15.44 | L3 | `fx.fill` | -15 dB | R40 | 25% | Avto-to'ldirish 19/20 — domino |
| 0:15.54 | L3 | `fx.fill` | -15 dB | R45 | 25% | Avto-to'ldirish 20/20 — domino |
| 0:15.80 | L3 | `ui.next` | -13 dB | C | 30% | 20/20 — hammasi to'ldirildi |
| 0:15.95 | L4 | `tr.slide` | -16 dB | C | 15% | Tavsiya etilgan reja |
| 0:16.80 | L3 | `ui.tap` | -9 dB | R10 | 0% | Ishga tushirish bosildi |
| 0:16.85 | L3 | `ui.launch` | -12 dB | C | 30% | Ishga tushmoqda... |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: 1 TANLOV oldidan |
| 0:18.20 | L3 | `ui.success` | -10 dB | C | 40% | Ishga tushdi! |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | 1 TANLOV — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Kampaniya ishga tushdi oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.80 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.00 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #1 |
| 0:23.15 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:23.35 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #2 |
| 0:23.50 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:23.70 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #3 |
| 0:23.85 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #4 chizildi |
| 0:24.05 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #4 |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -7 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `ui.select` | -17 dB | L40 | 30% | Nishon #1 |
| 0:25.45 | L3 | `ui.select` | -17 dB | C | 30% | Nishon #2 |
| 0:25.70 | L3 | `ui.select` | -17 dB | R40 | 30% | Nishon #3 |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (F tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
