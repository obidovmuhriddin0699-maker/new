# ADUZ 8-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 8 --cuesheet SOUND_ARCHITECTURE_8.md`).

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

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:10.5 | Muammo · B-minor, 'tarqoq' | Pad + filtrlangan bas. Plucklar har xil vaqtda, stereo maydonning turli nuqtalarida (poliritm 3:4, sidechain'siz — beat'ga bo'ysunmaydi) — tovush ham tarqoq. 5.5 s dan kick, 8.5 s dan riser. |
| 0:10.5–0:12.3 | Magnit · o'tish | Implosion: hamma tovush markazga so'riladi; magnit g'uvullashi; bo'laklar chetdan markazga 'yutiladi'. Stereo kenglik 1,7 → 0,35 ga qisqaradi — tovush tom ma'noda markazga yig'iladi. |
| 0:12.3–0:21.75 | Yechim · D-major, 'yig'ilgan' | Hamma narsa to'rga tushadi: to'g'ri 4/4 kick, clap, 8-lik hat, Rhodes D–Bm–G–A, sub. Plucklar markazda, beat'ga qulflangan. |
| 0:22–0:27 | Natija · G-major, to'liq | G–D–Em–C: supersaw, Rhodes + qo'ng'iroqcha melodiyasi, to'liq baraban. |
| 0:27–0:32 | Yakun · brend | Baraban o'chadi, ADUZ sonic logo (G tonikada: D–G–B), G akkord bilan so'nadi. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Ish stoli xonasi |
| 0:00.50 | L3 | `fx.window` | -14 dB | L60 | 25% | Stolda yangi bo'lak (window) — ekrandagi joyidan eshitiladi |
| 0:00.90 | L3 | `fx.window` | -14 dB | R70 | 25% | Stolda yangi bo'lak (window) — ekrandagi joyidan eshitiladi |
| 0:01.30 | L3 | `fx.window` | -14 dB | R40 | 25% | Stolda yangi bo'lak (window) — ekrandagi joyidan eshitiladi |
| 0:02.00 | L3 | `fx.paper` | -16 dB | L60 | 25% | Stolda yangi bo'lak (paper) — ekrandagi joyidan eshitiladi |
| 0:02.40 | L3 | `fx.sticky` | -14 dB | R30 | 25% | Stolda yangi bo'lak (sticky) — ekrandagi joyidan eshitiladi |
| 0:02.60 | L3 | `fx.sticky` | -14 dB | R80 | 25% | Stolda yangi bo'lak (sticky) — ekrandagi joyidan eshitiladi |
| 0:03.00 | L3 | `fx.tab` | -14 dB | R30 | 25% | Stolda yangi bo'lak (tab) — ekrandagi joyidan eshitiladi |
| 0:03.05 | L3 | `fx.tab` | -23 dB | R30 | 10% | Brauzer tabi #2 |
| 0:03.12 | L3 | `fx.tab` | -23 dB | R33 | 10% | Brauzer tabi #3 |
| 0:03.19 | L3 | `fx.tab` | -23 dB | R36 | 10% | Brauzer tabi #4 |
| 0:03.26 | L3 | `fx.tab` | -23 dB | R39 | 10% | Brauzer tabi #5 |
| 0:03.33 | L3 | `fx.tab` | -23 dB | R42 | 10% | Brauzer tabi #6 |
| 0:03.40 | L3 | `fx.tab` | -23 dB | R45 | 10% | Brauzer tabi #7 |
| 0:03.70 | L3 | `fx.window` | -14 dB | L50 | 25% | Stolda yangi bo'lak (window) — ekrandagi joyidan eshitiladi |
| 0:04.40 | L3 | `fx.paper` | -16 dB | R50 | 25% | Stolda yangi bo'lak (paper) — ekrandagi joyidan eshitiladi |
| 0:04.80 | L3 | `fx.sticky` | -14 dB | L20 | 25% | Stolda yangi bo'lak (sticky) — ekrandagi joyidan eshitiladi |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: QAYSI EXCEL? |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: QAYSI CHAT? |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: CHEK QAYERDA? |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: kamera uzoqlashishi oldidan |
| 0:08.25 | L4 | `tr.whoosh` | -12 dB | C | 30% | Kamera orqaga tortiladi — butun stol |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | TARQOQ — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -11 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser |
| 0:10.45 | L4 | `tr.implode` | -6 dB | C | 35% | Implosion o'tishi (J-cut) |
| 0:11.00 | L5 | `imp.boom` | -5 dB | C | 40% | Yechim: magnit yoqiladi |
| 0:11.00 | L4 | `fx.magnet` | -8 dB | C | 30% | Magnit maydoni kuchayadi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit |
| 0:11.25 | L5 | `fx.absorb` | -12 dB | R80 | 25% | Bo'lak #1 yutildi — chetdan markazga |
| 0:11.36 | L5 | `fx.absorb` | -12 dB | L70 | 25% | Bo'lak #2 yutildi — chetdan markazga |
| 0:11.47 | L5 | `fx.absorb` | -12 dB | R60 | 25% | Bo'lak #3 yutildi — chetdan markazga |
| 0:11.58 | L5 | `fx.absorb` | -12 dB | L50 | 25% | Bo'lak #4 yutildi — chetdan markazga |
| 0:11.69 | L5 | `fx.absorb` | -12 dB | R40 | 25% | Bo'lak #5 yutildi — chetdan markazga |
| 0:11.80 | L5 | `fx.absorb` | -12 dB | L30 | 25% | Bo'lak #6 yutildi — chetdan markazga |
| 0:11.91 | L5 | `fx.absorb` | -12 dB | R20 | 25% | Bo'lak #7 yutildi — chetdan markazga |
| 0:12.02 | L5 | `fx.absorb` | -12 dB | L10 | 25% | Bo'lak #8 yutildi — chetdan markazga |
| 0:12.25 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: telefon paydo bo'lishi |
| 0:12.30 | L3 | `fx.snap` | -9 dB | C | 20% | Logo telefonga aylanadi |
| 0:12.50 | L3 | `ui.select` | -18 dB | C | 30% | ADUZ logotipi |
| 0:12.80 | L4 | `tr.slide` | -16 dB | R60 | 10% | Kategoriyalar kirib keladi |
| 0:13.60 | L3 | `ui.select` | -12 dB | L20 | 20% | Tanlandi: Moda |
| 0:13.80 | L3 | `fx.snap` | -18 dB | L30 | 15% | Kanal kartasi #1 joyiga tushdi |
| 0:13.90 | L3 | `fx.snap` | -18 dB | R30 | 15% | Kanal kartasi #2 joyiga tushdi |
| 0:14.00 | L3 | `fx.snap` | -18 dB | L30 | 15% | Kanal kartasi #3 joyiga tushdi |
| 0:14.10 | L3 | `fx.snap` | -18 dB | R30 | 15% | Kanal kartasi #4 joyiga tushdi |
| 0:14.20 | L3 | `fx.snap` | -18 dB | L30 | 15% | Kanal kartasi #5 joyiga tushdi |
| 0:14.30 | L3 | `fx.snap` | -18 dB | R30 | 15% | Kanal kartasi #6 joyiga tushdi |
| 0:14.60 | L3 | `ui.tap` | -10 dB | L20 | 0% | '+' bosildi #1 |
| 0:15.00 | L3 | `ui.tap` | -10 dB | R30 | 0% | '+' bosildi #2 |
| 0:15.05 | L3 | `ui.cart` | -14 dB | R60 | 20% | Savatchaga tushdi — 1 |
| 0:15.40 | L3 | `ui.tap` | -10 dB | L20 | 0% | '+' bosildi #3 |
| 0:15.45 | L3 | `ui.cart` | -14 dB | R60 | 20% | Savatchaga tushdi — 2 |
| 0:15.80 | L3 | `ui.tap` | -10 dB | R30 | 0% | '+' bosildi #4 |
| 0:15.85 | L3 | `ui.cart` | -14 dB | R60 | 20% | Savatchaga tushdi — 3 |
| 0:16.20 | L3 | `ui.tap` | -10 dB | L20 | 0% | '+' bosildi #5 |
| 0:16.25 | L3 | `ui.cart` | -14 dB | R60 | 20% | Savatchaga tushdi — 4 |
| 0:16.60 | L4 | `tr.slide` | -15 dB | C | 15% | Savatcha ochiladi |
| 0:16.65 | L3 | `ui.cart` | -14 dB | R60 | 20% | Savatchaga tushdi — 5 |
| 0:17.60 | L3 | `ui.pay` | -10 dB | C | 35% | Bitta to'lov |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: BITTA JOY oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | BITTA JOY — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Buyurtma qabul qilindi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: aylanish oldidan |
| 0:21.75 | L4 | `tr.flip` | -8 dB | C | 20% | Karta aylanishi o'tishi |
| 0:22.00 | L5 | `imp.boom` | -6 dB | C | 45% | Natija boshlanishi |
| 0:22.30 | L3 | `fx.snap` | -10 dB | C | 30% | ADUZ hub markazi |
| 0:22.60 | L3 | `ui.select` | -18 dB | C | 30% | Kategoriya: Yangiliklar |
| 0:22.75 | L3 | `ui.select` | -18 dB | R70 | 30% | Kategoriya: Moda |
| 0:22.90 | L3 | `ui.select` | -18 dB | R70 | 30% | Kategoriya: Biznes |
| 0:23.05 | L3 | `ui.select` | -18 dB | C | 30% | Kategoriya: Taʼlim |
| 0:23.20 | L3 | `ui.select` | -18 dB | L70 | 30% | Kategoriya: Sport |
| 0:23.35 | L3 | `ui.select` | -18 dB | L70 | 30% | Kategoriya: Oziq-ovqat |
| 0:23.40 | L3 | `fx.pulse` | -26 dB | R60 | 30% | Hub bo'ylab impuls |
| 0:23.80 | L3 | `fx.pulse` | -26 dB | L60 | 30% | Hub bo'ylab impuls |
| 0:24.10 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: pillar oldidan |
| 0:24.20 | L3 | `fx.pulse` | -26 dB | R60 | 30% | Hub bo'ylab impuls |
| 0:24.60 | L3 | `fx.pulse` | -26 dB | L60 | 30% | Hub bo'ylab impuls |
| 0:24.60 | L3 | `ui.cart` | -16 dB | L50 | 30% | Pill: 1 ilova |
| 0:24.80 | L3 | `ui.cart` | -16 dB | C | 30% | Pill: 1 to‘lov |
| 0:25.00 | L3 | `fx.pulse` | -26 dB | R60 | 30% | Hub bo'ylab impuls |
| 0:25.00 | L3 | `ui.cart` | -16 dB | R50 | 30% | Pill: 1 hisobot |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -8 dB | C | 50% | Uchqunlar |
| 0:25.40 | L3 | `fx.pulse` | -26 dB | L60 | 30% | Hub bo'ylab impuls |
| 0:25.80 | L3 | `fx.pulse` | -26 dB | R60 | 30% | Hub bo'ylab impuls |
| 0:26.20 | L3 | `fx.pulse` | -26 dB | L60 | 30% | Hub bo'ylab impuls |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (G tonallikda) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
